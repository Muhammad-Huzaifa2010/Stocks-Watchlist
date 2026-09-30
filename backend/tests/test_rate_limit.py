from app.config import settings
from app.rate_limit import client_key, limiter
from starlette.requests import Request

def test_login_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.setattr(settings, "login_rate_limit", 5)
    limiter.reset()

    payload = {"username": "nobody@example.com", "password": "password123"}
    for _ in range(5):
        response = client.post("/login", data=payload)
        assert response.status_code == 401

    response = client.post("/login", data=payload)
    assert response.status_code == 429
    assert response.json() == {
        "detail": "Too many requests. Please try again later."
    }


def test_signup_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.setattr(settings, "signup_rate_limit", 3)
    limiter.reset()

    for index in range(3):
        response = client.post(
            "/users",
            json={
                "username": f"user{index}",
                "email": f"user{index}@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 201, response.text

    response = client.post(
        "/users",
        json={
            "username": "user3",
            "email": "user3@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 429
    assert response.json() == {
        "detail": "Too many requests. Please try again later."
    }
def test_client_key_uses_scope_and_client_ip():
    request_a = Request({
        "type": "http",
        "client": ("192.0.2.10", 12345),
    })
    request_b = Request({
        "type": "http",
        "client": ("192.0.2.20", 12345),
    })

    assert client_key(request_a, "login") == "login:192.0.2.10"
    assert client_key(request_b, "login") == "login:192.0.2.20"
    assert client_key(request_a, "signup") == "signup:192.0.2.10"