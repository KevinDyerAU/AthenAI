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
def mock_security_env(monkeypatch):
    # Force audit log path so compliance ok checks don't fail
    monkeypatch.setenv("AUDIT_LOG_PATH", "/tmp/audit.log")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    # Stub Neo4j client for compliance and incidents services
    class MockClient:
        def run_query(self, cypher, params=None):
            return []
    monkeypatch.setattr("api.services.compliance.get_client", lambda: MockClient())
    monkeypatch.setattr("api.services.incidents.get_client", lambda: MockClient())
    # default: admin identity for most tests
    monkeypatch.setattr("api.security.middleware.get_jwt_identity", lambda: {"roles": ["admin"]})


def test_compliance_assess(app, client):
    r = client.get("/api/security/compliance/assess", headers=auth_headers(app))
    assert r.status_code == 200
    data = r.get_json()
    assert "ok" in data and "checks" in data


def test_incidents_list_and_create(app, client):
    # List initially empty
    r1 = client.get("/api/security/incidents?limit=5", headers=auth_headers(app))
    assert r1.status_code == 200
    body = r1.get_json()
    assert "items" in body

    # Create incident
    payload = {"kind": "unauthorized_access", "severity": "high", "message": "test incident", "context": {"ip": "1.2.3.4"}}
    r2 = client.post("/api/security/incidents", json=payload, headers=auth_headers(app))
    assert r2.status_code == 201
    item = r2.get_json()
    assert item["kind"] == "unauthorized_access"
    assert item["severity"] == "high"


def test_rbac_denials_for_viewer_and_developer_on_write(app, client, monkeypatch):
    # viewer: can read, cannot write
    monkeypatch.setattr("api.security.middleware.get_jwt_identity", lambda: {"roles": ["viewer"]})
    r_read = client.get("/api/security/incidents", headers=auth_headers(app))
    assert r_read.status_code == 200
    r_write = client.post("/api/security/incidents", json={"kind": "k", "severity": "low", "message": "m"}, headers=auth_headers(app))
    assert r_write.status_code == 403

    # developer: can read, cannot write to security
    monkeypatch.setattr("api.security.middleware.get_jwt_identity", lambda: {"roles": ["developer"]})
    r_read2 = client.get("/api/security/incidents", headers=auth_headers(app))
    assert r_read2.status_code == 200
    r_write2 = client.post("/api/security/incidents", json={"kind": "k", "severity": "low", "message": "m"}, headers=auth_headers(app))
    assert r_write2.status_code == 403


def test_sandbox_policy_and_evaluate(app, client, monkeypatch):
    # Baseline policy
    r = client.get("/api/security/sandbox/policy", headers=auth_headers(app))
    assert r.status_code == 200
    pol = r.get_json()
    assert set(["cpu_quota", "memory_mb", "network", "filesystem", "dynamic"]).issubset(pol.keys())

    # Evaluate tightened policy
    r2 = client.post("/api/security/sandbox/evaluate", json={"risk_score": 0.9}, headers=auth_headers(app))
    assert r2.status_code == 200
    pol2 = r2.get_json()
    assert pol2["cpu_quota"] <= pol["cpu_quota"]
    assert pol2["network"] in ("limited", "isolated")
