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

    # Mock Neo4j client used by conversations resource
    class MockClient:
        def run_query(self, cypher, params=None):
            # messages pagination listing
            if "RETURN collect(m) AS messages" in cypher and "HAS_MESSAGE" in cypher:
                # emulate 3 messages
                data = [
                    {"id": "m3", "role": "assistant", "content": "third", "created_at": 3000, "agent": "bot"},
                    {"id": "m2", "role": "user", "content": "second", "created_at": 2000, "agent": None},
                    {"id": "m1", "role": "system", "content": "first", "created_at": 1000, "agent": None},
                ]
                # ignore offset/limit for mock simplicity; return all
                return [[data]]
            # permissions list
            if "RETURN collect({user_id: u.id, role: coalesce(r.role,'member')}) AS items" in cypher:
                return [[[{"user_id": "u1", "role": "admin"}, {"user_id": "u2", "role": "member"}]]]
            # set permission
            if "SET r.role = $role" in cypher and "RETURN u.id AS user_id, r.role AS role" in cypher:
                return [[params["target"], params["role"]]]
            # revoke permission
            if "DELETE r RETURN count(r) AS removed" in cypher and "MEMBER_OF" in cypher:
                return [[1]]
            return []

    from api.resources import conversations as conv_mod
    monkeypatch.setattr(conv_mod, "get_client", lambda: MockClient())
    # mock socketio emissions to no-op
    monkeypatch.setattr(conv_mod, "socketio", type("S", (), {"emit": staticmethod(lambda *a, **k: None)})())

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity={"id": "test-user"})
    return {"Authorization": f"Bearer {token}"}


def test_messages_pagination(app, client):
    cid = "c1"
    resp = client.get(f"/conversations/{cid}/messages?limit=2&offset=0", headers=auth_headers(app))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 3
    assert len(data["items"]) == 3  # mock returns all
    assert data["items"][0]["id"] == "m3"


def test_permissions_list_set_revoke(app, client):
    cid = "c1"
    # list
    resp = client.get(f"/conversations/{cid}/permissions", headers=auth_headers(app))
    assert resp.status_code == 200
    items = resp.get_json()["items"]
    assert {i["user_id"] for i in items} == {"u1", "u2"}

    # set role
    resp2 = client.post(
        f"/conversations/{cid}/permissions",
        json={"user_id": "u3", "role": "viewer"},
        headers=auth_headers(app),
    )
    assert resp2.status_code == 200
    body = resp2.get_json()
    assert body["user_id"] == "u3"
    assert body["role"] == "viewer"

    # revoke
    resp3 = client.delete(
        f"/conversations/{cid}/permissions/u3",
        headers=auth_headers(app),
    )
    assert resp3.status_code == 200
    assert resp3.get_json()["removed"] == 1
