import os
import pytest
from flask_jwt_extended import create_access_token
from api.app import create_app
from api.extensions import db
from api.models import Agent, AgentRun


@pytest.fixture()
def app(monkeypatch):
    os.environ["FLASK_ENV"] = "development"
    os.environ["INTEGRATION_SECRET"] = "secret123"
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        DB_AUTO_CREATE=True,
        JWT_SECRET_KEY="test-jwt",
    )
    # monkeypatch external integrations
    from api.resources import agents as agents_mod
    monkeypatch.setattr(agents_mod, "trigger_webhook", lambda *args, **kwargs: None)
    from api.resources import integrations as integ_mod
    monkeypatch.setattr(integ_mod, "socketio", type("S", (), {"emit": staticmethod(lambda *a, **k: None)})())

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


def test_agent_run_flow(app, client):
    # Create agent
    with app.app_context():
        a = Agent(name="test-agent", type="utility")
        db.session.add(a)
        db.session.commit()
        agent_id = a.id

    # Execute agent -> creates AgentRun and returns execution_id
    resp = client.post(f"/agents/{agent_id}/execute", headers=auth_headers(app))
    assert resp.status_code == 202
    data = resp.get_json()
    execution_id = data["execution_id"]
    assert execution_id

    # Webhook callback from n8n updates run to completed
    payload = {
        "execution_id": execution_id,
        "status": "completed",
        "result": {"ok": True},
        "metrics": {"latency_ms": 10},
    }
    resp2 = client.post(
        "/integrations/n8n/runs",
        json=payload,
        headers={"X-Integration-Token": os.environ["INTEGRATION_SECRET"]},
    )
    assert resp2.status_code == 200

    # Verify runs list and metrics
    runs = client.get(f"/agents/{agent_id}/runs", headers=auth_headers(app)).get_json()
    assert runs["total"] == 1
    assert runs["items"][0]["status"] == "completed"
    assert runs["items"][0]["duration_ms"] is not None

    metrics = client.get(f"/agents/{agent_id}/metrics", headers=auth_headers(app)).get_json()
    assert metrics["total_runs"] == 1
    assert metrics["completed"] == 1
    assert metrics["failed"] == 0
