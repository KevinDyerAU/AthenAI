import os
import pytest
from flask_jwt_extended import create_access_token
from api.app import create_app
from api.extensions import db


@pytest.fixture()
def app(monkeypatch):
    os.environ["FLASK_ENV"] = "development"
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        DB_AUTO_CREATE=True,
        JWT_SECRET_KEY="test-jwt",
    )

    # Avoid real RabbitMQ
    from api.resources import self_healing as sh_mod
    monkeypatch.setattr(sh_mod, "publish_exchange", lambda *args, **kwargs: None)

    # Capture socketio emits
    from api import extensions as ext
    emitted = []
    def fake_emit(event, payload=None, *args, **kwargs):
        emitted.append({"event": event, "payload": payload})
    monkeypatch.setattr(ext.socketio, "emit", fake_emit)

    with app.app_context():
        db.create_all()
        app.extensions["_emitted_socketio"] = emitted
        yield app
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity={"id": "test-user"})
    return {"Authorization": f"Bearer {token}"}


def test_analyze_emits_and_returns_structure(app, client, monkeypatch):
    # Force detector to return one anomaly and a diagnosis
    from api.resources import self_healing as sh_mod
    anomaly = {
        "metric": "error_rate", "value": 0.2, "baseline": 0.01, "zscore": 3.5, "severity": "high", "hint": "above"
    }
    diagnosis = {
        "issue_type": "degradation", "root_cause": "elevated error rate", "confidence": 0.8,
        "impacted_components": ["api"], "recommended_strategies": ["restart_unhealthy"]
    }
    monkeypatch.setattr(sh_mod.svc.detector, "detect", lambda metrics: [type("A", (), anomaly)])
    monkeypatch.setattr(sh_mod.svc.diagnoser, "diagnose", lambda anomalies, ctx: type("D", (), diagnosis))

    resp = client.post("/api/self_healing/analyze", json={"metrics": {"error_rate": 0.2}}, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["anomalies"][0]["metric"] == "error_rate"
    assert data["diagnosis"]["issue_type"] == "degradation"
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "self_healing:analyze" for e in emitted)


def test_heal_dry_run_strategy_selection_and_emit(app, client, monkeypatch):
    from api.resources import self_healing as sh_mod
    # Mock best strategy and execution to return plan
    monkeypatch.setattr(sh_mod.svc.selector, "best", lambda c: "restart_unhealthy")
    monkeypatch.setattr(sh_mod.svc.executor, "execute", lambda name, context, dry_run: {"applied": False, "plan": {"strategy": name}, "dry_run": True})

    issue = {"diagnosis": {
        "issue_type": "degradation", "root_cause": "elevated error rate", "confidence": 0.8,
        "impacted_components": ["api"], "recommended_strategies": ["restart_unhealthy"]
    }}
    resp = client.post("/api/self_healing/heal", json={"issue": issue, "dry_run": True}, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["outcome"]["dry_run"] is True
    assert data["strategy"] == "restart_unhealthy"
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "self_healing:heal" for e in emitted)


def test_strategies_and_learning_endpoints(app, client):
    r1 = client.get("/api/self_healing/strategies", headers=auth_headers(app))
    assert r1.status_code == 200
    assert "strategies" in r1.get_json()

    r2 = client.get("/api/self_healing/learning", headers=auth_headers(app))
    assert r2.status_code == 200
    assert "selector" in r2.get_json()
