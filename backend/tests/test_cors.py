# Phase 1 — M1: the React app runs on another origin (port 5173), so the
# browser only lets it read a response that carries an
# Access-Control-Allow-Origin header. Without it, React can't see the status
# or the message and shows "Unable to connect to the server".

import pytest
from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


FRONTEND = "http://localhost:5173"


def database_is_down():
    raise OperationalError("SELECT 1", {}, Exception("database is down"))
    yield  # makes this a generator dependency, like get_db


class BrokenSession:
    """A session whose queries fail, as if PostgreSQL went away mid-request."""

    def query(self, *args, **kwargs):
        raise OperationalError("SELECT users", {}, Exception("connection lost"))


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_preflight_from_frontend_is_allowed(client, origin):
    response = client.options(
        "/stocks",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()


def test_successful_request_from_frontend_has_cors_header(client, auth_headers):
    headers = {**auth_headers("sam", "sam@gmail.com"), "Origin": FRONTEND}

    response = client.get("/stocks", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_client_error_responses_have_cors_header(client, auth_headers):
    headers = {**auth_headers("sam", "sam@gmail.com"), "Origin": FRONTEND}

    responses = {
        401: client.get("/stocks", headers={"Origin": FRONTEND}),
        404: client.get("/stocks/999", headers=headers),
        409: client.post(
            "/users",
            json={"username": "sam", "email": "other@gmail.com", "password": "password123"},
            headers={"Origin": FRONTEND},
        ),
        422: client.post("/stocks", json={"symbol": "AAPL"}, headers=headers),
    }

    for status, response in responses.items():
        assert response.status_code == status, response.text
        assert response.headers.get("access-control-allow-origin") == FRONTEND, status


def test_database_error_returns_json_500_with_cors_header(client):
    app.dependency_overrides[get_db] = database_is_down

    response = client.post(
        "/users",
        json={"username": "sam", "email": "sam@gmail.com", "password": "password123"},
        headers={"Origin": FRONTEND},
    )

    assert response.status_code == 500
    # A generic message only: no SQL, no stack trace.
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_database_error_inside_a_route_returns_json_500_with_cors_header(client):
    app.dependency_overrides[get_db] = lambda: BrokenSession()

    response = client.post(
        "/login",
        data={"username": "sam@gmail.com", "password": "password123"},
        headers={"Origin": FRONTEND},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_request_without_origin_still_works(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_unknown_origin_gets_no_cors_header(client):
    response = client.get("/", headers={"Origin": "https://evil.example"})

    # The server still answers, but without the header the browser
    # won't let that other website read the response.
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_preflight_from_unknown_origin_is_refused(client):
    response = client.options(
        "/stocks",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers