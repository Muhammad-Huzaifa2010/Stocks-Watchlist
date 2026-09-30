# Phase 1 — signup and login responses.
# H1: a duplicate username or email gets 409 Conflict, never a 500.
# L4: create endpoints return 201, and login declares its response model.

from app.models import User
from app.routes import users as users_routes
from app.security import hash_password


def signup(client, username, email, password="password123"):
    return client.post(
        "/users",
        json={"username": username, "email": email, "password": password}
    )


def login(client, email, password="password123"):
    return client.post(
        "/login",
        data={"username": email, "password": password}
    )


def test_signup_with_unique_username_returns_201(client):
    response = signup(client, "sam", "sam@gmail.com")

    assert response.status_code == 201
    assert response.json()["username"] == "sam"
    assert response.json()["email"] == "sam@gmail.com"


def test_signup_response_does_not_expose_password(client):
    data = signup(client, "sam", "sam@gmail.com").json()

    assert set(data) == {"id", "username", "email"}


def test_duplicate_username_returns_409(client):
    signup(client, "sam", "sam@gmail.com")

    response = signup(client, "sam", "another@gmail.com")

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_duplicate_email_returns_409(client):
    signup(client, "sam", "sam@gmail.com")

    response = signup(client, "someone_else", "sam@gmail.com")

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_database_still_works_after_duplicate_signup(client):
    signup(client, "sam", "sam@gmail.com")
    assert signup(client, "sam", "another@gmail.com").status_code == 409

    # Signup, login and stock requests keep working afterwards.
    assert signup(client, "alex", "alex@gmail.com").status_code == 201

    response = login(client, "alex@gmail.com")
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    created = client.post(
        "/stocks",
        json={"symbol": "AAPL", "company_name": "Apple Inc.", "market": "NASDAQ"},
        headers=headers
    )
    assert created.status_code == 201


def test_simultaneous_duplicate_signup_returns_409_and_rolls_back(client, db, monkeypatch):
    """Two people sign up with the same username at the same moment.

    Both requests pass the "already exists" checks, then the database's
    unique rule rejects the second insert with an IntegrityError. This test
    recreates that by letting another user sign up while the password is
    being hashed (between the checks and the insert).
    """

    def someone_else_signs_up_first(password):
        db.add(User(username="sam", email="first@gmail.com", hashed_password="x"))
        db.commit()
        return hash_password(password)

    monkeypatch.setattr(users_routes, "hash_password", someone_else_signs_up_first)

    response = signup(client, "sam", "second@gmail.com")

    assert response.status_code == 409
    assert response.json() == {"detail": "Username or email already exists"}

    monkeypatch.undo()

    # The failed insert was rolled back, so the same session still works.
    assert signup(client, "alex", "alex@gmail.com").status_code == 201
    assert db.query(User).filter(User.username == "sam").count() == 1


def test_login_returns_only_the_token(client):
    signup(client, "sam", "sam@gmail.com")

    response = login(client, "sam@gmail.com")

    assert response.status_code == 200

    data = response.json()

    # Exactly the two fields the frontend uses — no password, no hash, no user data.
    assert set(data) == {"access_token", "token_type"}
    assert data["token_type"] == "bearer"
    assert data["access_token"].count(".") == 2


def test_login_declares_token_response_model(client):
    schema = client.get("/openapi.json").json()

    login_response = schema["paths"]["/login"]["post"]["responses"]["200"]
    token_schema = schema["components"]["schemas"]["TokenResponse"]

    assert login_response["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/TokenResponse"
    }
    assert set(token_schema["properties"]) == {"access_token", "token_type"}


def test_create_endpoints_document_201(client):
    paths = client.get("/openapi.json").json()["paths"]

    assert "201" in paths["/users"]["post"]["responses"]
    assert "201" in paths["/stocks"]["post"]["responses"]