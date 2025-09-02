import pytest
from flask_jwt_extended import create_access_token
from api.app import create_app
from api.extensions import db


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
    })
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_mq_and_db(monkeypatch):
    # Stub RabbitMQ publish
    monkeypatch.setattr("api.utils.rabbitmq.publish_exchange_profiled", lambda *a, **k: True)
    # Stub Neo4j client
    class MockClient:
        def run_query(self, cypher, params=None):
            return []
    monkeypatch.setattr("api.services.validation.get_client", lambda: MockClient())


def test_run_validation_and_get_last_report(app, client):
    cfg = {
        "unit_selectors": ["api.*"],
        "integration_scenarios": ["mq", "neo4j"],
        "include_performance": True,
        "include_behavior": True,
        "load_profile": {"rps": 50, "duration_s": 10}
    }
    r = client.post("/api/validation/run", json=cfg, headers=auth_headers(app))
    assert r.status_code == 200
    data = r.get_json()
    assert "id" in data and "gate" in data and "reports" in data

    r2 = client.get("/api/validation/report/last", headers=auth_headers(app))
    assert r2.status_code == 200
    last = r2.get_json()
    assert last.get("id") == data.get("id")


def test_quality_gates_get_and_set(app, client):
    g1 = client.get("/api/validation/gates", headers=auth_headers(app))
    assert g1.status_code == 200
    body = g1.get_json()
    assert "gates" in body

    g2 = client.post(
        "/api/validation/gates",
        json={"min_pass_rate": 0.95, "max_error_rate": 0.02, "max_p95_latency_ms": 200.0},
        headers=auth_headers(app),
    )
    assert g2.status_code == 200
    gates = g2.get_json()["gates"]
    assert gates["min_pass_rate"] == 0.95
    assert gates["max_error_rate"] == 0.02
    assert gates["max_p95_latency_ms"] == 200.0
