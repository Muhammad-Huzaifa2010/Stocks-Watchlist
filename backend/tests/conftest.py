import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "unit-test-secret-key-32-chars-min"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["CORS_ORIGINS"] = (
    "http://localhost:5173,http://127.0.0.1:5173"
)
os.environ["LOGIN_RATE_LIMIT"] = "1000"
os.environ["SIGNUP_RATE_LIMIT"] = "1000"
os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "60"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.rate_limit import limiter


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")

engine_kwargs = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(TEST_DATABASE_URL, **engine_kwargs)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Signs a user up and logs them in through the real API.

    Usage in a test: headers = auth_headers("alice", "alice@gmail.com")
    Returns {"Authorization": "Bearer <token>"} for that user.
    """

    def _auth_headers(username, email, password="password123"):
        signup = client.post(
            "/users",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )
        assert signup.status_code == 201, signup.text

        login = client.post(
            "/login",
            data={"username": email, "password": password},
        )
        assert login.status_code == 200, login.text

        return {
            "Authorization": f"Bearer {login.json()['access_token']}"
        }

    return _auth_headers
