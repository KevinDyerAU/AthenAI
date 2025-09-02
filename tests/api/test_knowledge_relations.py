import os
import types
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

    # mock neo4j client
    class MockClient:
        def __init__(self):
            self.calls = []
        def run_query(self, cypher, params=None):
            self.calls.append((cypher, params))
            if "RETURN r" in cypher and "MERGE (s)-[r:RELATED" in cypher:
                return [[{"type": params["pred"], "version": 1, "state": "active", **(params.get("attrs") or {})}]]
            if "RETURN r" in cypher and "MATCH (s:Entity" in cypher:
                return [[{"type": params["pred"], "version": 2, "state": "inactive"}]]
            if "RETURN r ORDER BY" in cypher:
                return [[{"type": "KNOWS", "version": 3, "state": "active", "lastUpdated": 1}],
                        [{"type": "OWNS", "version": 1, "state": "inactive", "lastUpdated": 0}]]
            return []

    from api import resources as _
    from api.resources import knowledge as knowledge_mod
    monkeypatch.setattr(knowledge_mod, "get_client", lambda: MockClient())
    monkeypatch.setattr(knowledge_mod, "audit_event", lambda *args, **kwargs: None)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}


def test_relation_update(app, client):
    payload = {
        "subject_id": "s1",
        "predicate": "KNOWS",
        "object_id": "o1",
        "attributes": {"confidence": 0.9}
    }
    resp = client.post("/api/knowledge/relations/update", json=payload, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["relation"]["type"] == "KNOWS"
    assert data["relation"]["state"] == "active"


def test_relation_delete(app, client):
    payload = {
        "subject_id": "s1",
        "predicate": "KNOWS",
        "object_id": "o1",
        "reason": "cleanup"
    }
    resp = client.post("/api/knowledge/relations/delete", json=payload, headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["relation"]["state"] == "inactive"


def test_provenance_get(app, client):
    resp = client.get("/api/knowledge/provenance?entityId=s1&direction=both&limit=10", headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 2
