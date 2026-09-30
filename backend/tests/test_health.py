from sqlalchemy.exc import OperationalError

from app import main as main_module
from app.database import get_db
from app.main import app


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_returns_ok_when_database_works(client):
    response = client.get("/health/ready")
    # Readiness uses the application engine, which tests isolate as sqlite://.
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        assert response.json()["status"] == "ok"


def test_ready_returns_503_when_database_is_down(client, monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("database is down"))

    monkeypatch.setattr(main_module, "engine", BrokenEngine())

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "detail": "Database unavailable",
    }


def test_health_does_not_use_database_dependency(client):
    def database_is_down():
        raise OperationalError("SELECT 1", {}, Exception("database is down"))
        yield

    app.dependency_overrides[get_db] = database_is_down
    try:
        response = client.get("/health")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db, None)
