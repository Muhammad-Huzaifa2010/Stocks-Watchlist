def signup(client, **overrides):
    payload = {
        "username": "sam",
        "email": "sam@example.com",
        "password": "password123",
        **overrides,
    }
    return client.post("/users", json=payload)


def test_non_gmail_email_is_accepted(client):
    response = signup(client, email="sam@example.com")
    assert response.status_code == 201
    assert response.json()["email"] == "sam@example.com"


def test_username_is_normalized_to_lowercase(client):
    response = signup(client, username="Sam.User", email="sam.user@example.com")
    assert response.status_code == 201
    assert response.json()["username"] == "sam.user"


def test_username_too_short_returns_422(client):
    response = signup(client, username="ab")
    assert response.status_code == 422


def test_username_invalid_characters_returns_422(client):
    response = signup(client, username="sam user")
    assert response.status_code == 422


def test_password_too_short_returns_422(client):
    response = signup(client, password="short")
    assert response.status_code == 422


def test_password_over_72_bytes_returns_422(client):
    response = signup(client, password="p" * 73)
    assert response.status_code == 422


def test_duplicate_username_is_case_insensitive(client):
    assert signup(client, username="Sam", email="one@example.com").status_code == 201
    response = signup(client, username="sam", email="two@example.com")
    assert response.status_code == 409


def test_symbol_is_normalized_to_uppercase(client, auth_headers):
    headers = auth_headers("trader", "trader@example.com")
    response = client.post(
        "/stocks",
        json={"symbol": "aapl", "company_name": "Apple Inc.", "market": "NASDAQ"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["symbol"] == "AAPL"


def test_invalid_symbol_returns_422(client, auth_headers):
    headers = auth_headers("trader", "trader@example.com")
    response = client.post(
        "/stocks",
        json={"symbol": "AA PL", "company_name": "Apple Inc.", "market": "NASDAQ"},
        headers=headers,
    )
    assert response.status_code == 422


def test_blank_optional_fields_become_null(client, auth_headers):
    headers = auth_headers("trader", "trader@example.com")
    response = client.post(
        "/stocks",
        json={
            "symbol": "MSFT",
            "company_name": "Microsoft",
            "market": "NASDAQ",
            "sector": "   ",
            "notes": "",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["sector"] is None
    assert response.json()["notes"] is None


def test_duplicate_symbol_for_same_user_returns_409(client, auth_headers):
    headers = auth_headers("trader", "trader@example.com")
    payload = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "market": "NASDAQ",
    }
    assert client.post("/stocks", json=payload, headers=headers).status_code == 201
    response = client.post("/stocks", json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Stock already exists in your watchlist"


def test_two_users_can_track_the_same_symbol(client, auth_headers):
    user_a = auth_headers("usera", "usera@example.com")
    user_b = auth_headers("userb", "userb@example.com")
    payload = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "market": "NASDAQ",
    }
    assert client.post("/stocks", json=payload, headers=user_a).status_code == 201
    assert client.post("/stocks", json=payload, headers=user_b).status_code == 201


def test_unknown_email_login_returns_generic_401(client):
    response = client.post(
        "/login",
        data={"username": "missing@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
