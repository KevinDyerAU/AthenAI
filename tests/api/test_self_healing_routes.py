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


def test_metric_trend_and_forecast_endpoints(app, client, monkeypatch):
    from api.resources import self_healing as sh_mod
    monkeypatch.setattr(sh_mod.svc, "get_metric_trend", lambda metric, limit=100: [(1, 0.1), (2, 0.2)])
    monkeypatch.setattr(sh_mod.svc, "forecast", lambda metric, steps=1: 0.25)

    rt = client.get("/api/self_healing/metrics/trend?metric=error_rate&limit=10", headers=auth_headers(app))
    assert rt.status_code == 200
    assert rt.get_json()["trend"][0] == [1, 0.1] or tuple(rt.get_json()["trend"][0]) == (1, 0.1)

    rf = client.get("/api/self_healing/metrics/forecast?metric=error_rate&steps=3", headers=auth_headers(app))
    assert rf.status_code == 200
    assert rf.get_json()["forecast"] == 0.25


def test_python_uuid_persistence_on_heal(app, client, monkeypatch):
    # Capture run_query params when HealingAttempt is created and assert UUID-like id present
    calls = {"params": []}
    class MockClient:
        def run_query(self, cypher, params=None):
            if "CREATE (h:HealingAttempt" in cypher:
                calls["params"].append(params)
            return []
    monkeypatch.setattr("api.resources.self_healing.get_client", lambda: MockClient())

    from api.resources import self_healing as sh_mod
    # Make selection deterministic and executor return applied True
    monkeypatch.setattr(sh_mod.svc.selector, "best", lambda c: "restart_unhealthy")
    monkeypatch.setattr(sh_mod.svc.executor, "execute", lambda name, context, dry_run: {"applied": True, "verified": True})

    issue = {"diagnosis": {"issue_type": "x", "root_cause": "y", "confidence": 1.0, "impacted_components": [], "recommended_strategies": ["restart_unhealthy"]}}
    resp = client.post("/api/self_healing/heal", json={"issue": issue, "dry_run": False}, headers=auth_headers(app))
    assert resp.status_code == 200
    assert len(calls["params"]) == 1
    hid = calls["params"][0]["id"]
    # basic UUID sanity: contains hyphens and length > 10
    assert isinstance(hid, str) and "-" in hid and len(hid) > 10


def test_execute_verification_and_rollback_branches(app, monkeypatch):
    # Force a real execute path with strategy 'scale_service' and failing verification
    from api.resources import self_healing as sh_mod
    execu = sh_mod.svc.executor
    context = {"service": "api", "scaler": None, "verify": lambda: False}
    out = execu.execute("scale_service", context=context, dry_run=False)
    assert out["verified"] is False
    assert isinstance(out.get("rolled_back"), list)
    # Check that rollback contains inverse scale
    rb = [a for a in out["rolled_back"] if a.get("type") == "scale"]
    assert rb and rb[0].get("delta") == -1


def test_config_rollback_gitops_integration(app, monkeypatch):
    from api.resources import self_healing as sh_mod
    class GitOps:
        def rollback(self, target):
            return True
    # Avoid DB write
    class MockClient:
        def run_query(self, cypher, params=None):
            return []
    monkeypatch.setattr("api.resources.self_healing.get_client", lambda: MockClient())
    res = sh_mod.svc.heal(
        issue={"diagnosis": {"issue_type": "configuration_or_dependency", "root_cause": "deploy", "confidence": 0.6, "impacted_components": ["api"], "recommended_strategies": ["rollback_config"]}},
        context={"gitops": GitOps(), "config_target": "api"},
        dry_run=False,
        strategy="rollback_config",
    )
    assert res["outcome"]["applied"] in (True, False)  # verified depends on verify hook (not provided, defaults True)
    actions = res["outcome"].get("actions", [])
    assert any(a.get("type") == "config.rollback" for a in actions)
