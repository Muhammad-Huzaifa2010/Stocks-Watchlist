# Phase 11: every stock belongs to one user, and the backend enforces it.
# Users are created through the real signup and login endpoints (see the
# auth_headers fixture in conftest.py).

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.config import settings


STOCK = {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "market": "NASDAQ",
    "sector": "Technology",
    "notes": "User A's stock",
}

CHANGED_STOCK = {
    "symbol": "AAPL",
    "company_name": "Changed by someone",
    "market": "NASDAQ",
    "sector": "Technology",
    "notes": "changed",
}


def create_stock_as(client, headers, stock=STOCK):
    response = client.post("/stocks", json=stock, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def user_id_from(headers):
    """Reads the user id that the backend stored in the token ("sub")."""
    token = headers["Authorization"].removeprefix("Bearer ")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return int(payload["sub"])


def test_user_can_manage_own_stock(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")

    stock = create_stock_as(client, user_a)
    url = f"/stocks/{stock['id']}"

    listed = client.get("/stocks", headers=user_a)
    assert [s["id"] for s in listed.json()] == [stock["id"]]

    single = client.get(url, headers=user_a)
    assert single.status_code == 200
    assert single.json()["symbol"] == "AAPL"

    updated = client.put(url, json=CHANGED_STOCK, headers=user_a)
    assert updated.status_code == 200
    assert updated.json()["company_name"] == "Changed by someone"

    deleted = client.delete(url, headers=user_a)
    assert deleted.status_code == 200
    assert client.get("/stocks", headers=user_a).json() == []


def test_users_only_see_their_own_stocks(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")
    user_b = auth_headers("userb", "userb@gmail.com")

    stock_a = create_stock_as(client, user_a)
    stock_b = create_stock_as(
        client,
        user_b,
        {"symbol": "LUCK", "company_name": "Lucky Cement", "market": "PSX"},
    )

    list_a = client.get("/stocks", headers=user_a).json()
    list_b = client.get("/stocks", headers=user_b).json()

    assert [s["id"] for s in list_a] == [stock_a["id"]]
    assert [s["id"] for s in list_b] == [stock_b["id"]]


def test_user_b_cannot_read_update_or_delete_user_a_stock(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")
    user_b = auth_headers("userb", "userb@gmail.com")

    stock_a = create_stock_as(client, user_a)
    url = f"/stocks/{stock_a['id']}"

    attempts = [
        client.get(url, headers=user_b),
        client.put(url, json=CHANGED_STOCK, headers=user_b),
        client.delete(url, headers=user_b),
    ]

    # The same 404 as a stock that does not exist, so user B cannot even
    # find out that the id is in use.
    for response in attempts:
        assert response.status_code == 404
        assert response.json()["detail"] == "Stock not found"

    # User A's stock is still there and unchanged.
    still_there = client.get(url, headers=user_a)
    assert still_there.status_code == 200
    assert still_there.json() == stock_a


def test_user_id_in_request_body_is_ignored(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")
    user_b = auth_headers("userb", "userb@gmail.com")

    # User A tries to create a stock "for" user B.
    stock = create_stock_as(client, user_a, {**STOCK, "user_id": user_id_from(user_b)})

    assert "user_id" not in stock
    assert [s["id"] for s in client.get("/stocks", headers=user_a).json()] == [stock["id"]]
    assert client.get("/stocks", headers=user_b).json() == []


@pytest.mark.parametrize(
    "method, url",
    [
        ("GET", "/stocks"),
        ("POST", "/stocks"),
        ("GET", "/stocks/1"),
        ("PUT", "/stocks/1"),
        ("DELETE", "/stocks/1"),
    ],
)
def test_stock_endpoints_require_login(client, method, url):
    body = STOCK if method in ("POST", "PUT") else None

    response = client.request(method, url, json=body)

    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/stocks",
        headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_token_signed_with_wrong_secret_is_rejected(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")

    forged = jwt.encode(
        {
            "sub": str(user_id_from(user_a)),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "not-the-real-secret",
        algorithm=settings.algorithm,
    )

    response = client.get("/stocks", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_expired_token_is_rejected(client, auth_headers):
    user_a = auth_headers("usera", "usera@gmail.com")

    expired = jwt.encode(
        {
            "sub": str(user_id_from(user_a)),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get("/stocks", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401