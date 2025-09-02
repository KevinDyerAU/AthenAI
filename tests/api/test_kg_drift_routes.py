import os
import pytest
from flask_jwt_extended import create_access_token
from api.app import create_app
from api.extensions import db


@pytest.fixture()
def app(monkeypatch):
    os.environ["FLASK_ENV"] = "development"
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        DB_AUTO_CREATE=True,
        JWT_SECRET_KEY="test-jwt",
    )

    # Avoid real RabbitMQ
    from api.resources import kg_drift as kg_drift_mod
    monkeypatch.setattr(kg_drift_mod, "publish_exchange", lambda *args, **kwargs: None)

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
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}


def test_detect_no_embed_environment(app, client, monkeypatch):
    # Force semantic drift detector to see embeddings disabled
    from api.services import knowledge_drift as kd
    monkeypatch.setattr(kd, "vector_search_enabled", lambda: False)
    # Also make conflicts empty
    monkeypatch.setattr(kd, "monitor_consistency", lambda limit=200: {"contradictions": []})

    resp = client.post("/api/kg_drift/detect", json={"sample_limit": 5}, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["semantic"] == []
    assert data["conflicts"] == []


def test_conflict_detection_with_synthetic_contradictions(app, client, monkeypatch):
    from api.services import knowledge_drift as kd
    fake = {
        "contradictions": [
            {"sid": "E:1", "pred": "located_in", "objs": ["A", "B"]},
            {"sid": "E:2", "pred": "status", "objs": ["active", "inactive", "paused"]},
        ]
    }
    monkeypatch.setattr(kd, "monitor_consistency", lambda limit=200: fake)
    # Disable semantic
    monkeypatch.setattr(kd, "vector_search_enabled", lambda: False)

    resp = client.post("/api/kg_drift/detect", json={"conflict_limit": 10}, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["conflicts"]) == 2
    kinds = {c["kind"] for c in data["conflicts"]}
    assert "contradiction" in kinds
    # Assert socketio emitted drift signals
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "kg_drift:drift" for e in emitted)


def test_remediation_winner_selection_and_dry_run(app, client, monkeypatch):
    from api.services import knowledge_drift as kd

    # Score options so that 'W' wins over 'L1', 'L2'
    monkeypatch.setattr(kd, "_score_options", lambda sid, pred, strategy: [("W", 0.9), ("L1", 0.5), ("L2", 0.1)])

    # Dry run should not attempt to write; we can track by wrapping get_client to raise if used (after plan)
    class Dummy:
        def run_query(self, *args, **kwargs):
            raise AssertionError("run_query should not be called in dry-run")
    monkeypatch.setattr(kd, "get_client", lambda: Dummy())

    resp = client.post(
        "/api/kg_drift/remediate",
        json={"subject_id": "E:1", "predicate": "located_in", "strategy": "confidence", "dry_run": True},
        headers=auth_headers(app),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("dry_run") is True
    assert data["plan"]["winner"] == "W"
    # UI plan emitted
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "kg_drift:remediate.plan" for e in emitted)


def test_remediation_escalation_creates_request_and_no_edge_changes(app, client, monkeypatch):
    from api.services import knowledge_drift as kd

    # Winner plan
    monkeypatch.setattr(kd, "_score_options", lambda sid, pred, strategy: [("W", 0.9), ("L1", 0.5)])

    # Mock client to capture MERGE of ResolutionRequest and ensure edge update query isn't called
    class MockClient:
        def __init__(self):
            self.queries = []
        def run_query(self, cypher, params=None):
            self.queries.append(cypher)
            if "MERGE (rr:ResolutionRequest" in cypher:
                return []
            if "SET r.state" in cypher:
                raise AssertionError("Edge update should not be executed on escalate")
            return []
    mc = MockClient()
    monkeypatch.setattr(kd, "get_client", lambda: mc)

    resp = client.post(
        "/api/kg_drift/remediate",
        json={"subject_id": "E:1", "predicate": "located_in", "escalate": True},
        headers=auth_headers(app),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("escalated") is True
    assert any("ResolutionRequest" in q for q in mc.queries)
    # Escalation UI event
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "kg_drift:resolution.escalated" for e in emitted)


def test_quality_snapshot_records_and_emits(app, client, monkeypatch):
    # Force stable metrics
    from api.services import knowledge_drift as kd
    monkeypatch.setattr(kd, "assess_quality", lambda: {"entities": 1, "relations": 1, "orphans": 0, "contradictions": [], "avg_confidence": 1.0, "last_update_ms": 0, "age_ms": 0, "quality_score": 1.0})
    # Mock record to no-op
    monkeypatch.setattr(kd, "record_quality_snapshot", lambda *args, **kwargs: None)
    r = client.post("/api/kg_drift/quality/snapshot", headers=auth_headers(app))
    assert r.status_code == 200
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "kg_drift:quality.snapshot" for e in emitted)


def test_resolution_requests_list_and_approve_reject(app, client, monkeypatch):
    # Mock list requests
    class MockClient:
        def __init__(self):
            self.queries = []
        def run_query(self, cypher, params=None):
            self.queries.append({"q": cypher, "p": params})
            if cypher.startswith("MATCH (rr:ResolutionRequest) WHERE"):
                return [[{"id": "RR1", "status": "pending", "createdAt": 1}] ]
            return []
    mc = MockClient()
    monkeypatch.setattr("api.resources.kg_drift.get_client", lambda: mc)

    # GET list
    res = client.get("/api/kg_drift/resolution/requests", headers=auth_headers(app))
    assert res.status_code == 200
    assert res.get_json()["requests"][0]["id"] == "RR1"

    # Approve path: mock remediate_conflict
    monkeypatch.setattr("api.resources.kg_drift.remediate_conflict", lambda *args, **kwargs: {"applied": True})
    res2 = client.post(
        "/api/kg_drift/resolution/approve",
        json={"request_id": "RR1", "subject_id": "E:1", "predicate": "status", "strategy": "confidence"},
        headers=auth_headers(app),
    )
    assert res2.status_code == 200
    emitted = app.extensions["_emitted_socketio"]
    assert any(e["event"] == "kg_drift:resolution.approved" for e in emitted)

    # Reject path
    res3 = client.post(
        "/api/kg_drift/resolution/reject",
        json={"request_id": "RR1", "reason": "not valid"},
        headers=auth_headers(app),
    )
    assert res3.status_code == 200
    assert any(e["event"] == "kg_drift:resolution.rejected" for e in emitted)
