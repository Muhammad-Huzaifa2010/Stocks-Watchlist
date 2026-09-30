# Phase 1 — L1: any token that can't be trusted gets 401, never a 500.
#
# Most tokens below are signed with the real SECRET_KEY on purpose. That way
# they get past the signature check, and the claim checks ("sub", "exp")
# are what the tests exercise.

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.config import settings


def make_token(claims):
    return jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)


def minutes_from_now(minutes):
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def create_user(client, username="sam", email="sam@gmail.com"):
    response = client.post(
        "/users",
        json={"username": username, "email": email, "password": "password123"}
    )
    return response.json()["id"]


def get_stocks(client, token):
    return client.get("/stocks", headers={"Authorization": f"Bearer {token}"})


def assert_rejected(response):
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_token_from_login_works(client, auth_headers):
    headers = auth_headers("sam", "sam@gmail.com")

    response = client.get("/stocks", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_valid_token_with_sub_and_exp_works(client):
    user_id = create_user(client)

    token = make_token({"sub": str(user_id), "exp": minutes_from_now(5)})

    assert get_stocks(client, token).status_code == 200


def test_missing_token_returns_401(client):
    response = client.get("/stocks")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    ["not-a-real-token", "a.b.c", "abc.def", "...", "eyJhbGciOiJIUzI1NiJ9.e30."],
)
def test_invalid_token_returns_401(client, token):
    assert_rejected(get_stocks(client, token))


@pytest.mark.parametrize(
    "sub",
    [
        "abc",                    # letters
        "1.5",                    # not a whole number
        "-1",                     # negative
        "0",                      # ids start at 1
        "",                       # empty
        " 1",                     # extra spaces
        "٣",                      # a non-ASCII digit
        "99999999999999999999",   # bigger than the database's INTEGER column
        1,                        # a number instead of a string
        None,
        ["1"],
    ],
)
def test_malformed_sub_returns_401(client, sub):
    create_user(client)

    token = make_token({"sub": sub, "exp": minutes_from_now(5)})

    assert_rejected(get_stocks(client, token))


def test_missing_sub_returns_401(client):
    create_user(client)

    token = make_token({"exp": minutes_from_now(5)})

    assert_rejected(get_stocks(client, token))


def test_missing_exp_returns_401(client):
    user_id = create_user(client)

    # Before Phase 1 this token was accepted and never expired.
    token = make_token({"sub": str(user_id)})

    assert_rejected(get_stocks(client, token))


@pytest.mark.parametrize("exp", [None, "soon", [1]])
def test_malformed_exp_returns_401(client, exp):
    user_id = create_user(client)

    token = make_token({"sub": str(user_id), "exp": exp})

    assert_rejected(get_stocks(client, token))


def test_expired_token_returns_401(client):
    user_id = create_user(client)

    token = make_token({"sub": str(user_id), "exp": minutes_from_now(-1)})

    assert_rejected(get_stocks(client, token))


def test_token_for_unknown_user_returns_401(client):
    token = make_token({"sub": "999", "exp": minutes_from_now(5)})

    assert_rejected(get_stocks(client, token))


def test_unsigned_token_returns_401(client):
    """A token with "alg": "none" and no signature must never be accepted."""
    user_id = create_user(client)

    def encode(part):
        return base64.urlsafe_b64encode(json.dumps(part).encode()).rstrip(b"=").decode()

    exp = int(minutes_from_now(5).timestamp())
    token = encode({"alg": "none", "typ": "JWT"}) + "." + encode({"sub": str(user_id), "exp": exp}) + "."

    assert_rejected(get_stocks(client, token))