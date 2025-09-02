import pytest
from flask_jwt_extended import create_access_token
from api.app import create_app
from api.extensions import db


@pytest.fixture(autouse=True)
def mock_mq_and_db(monkeypatch):
    import api.utils.rabbitmq
    monkeypatch.setattr(api.utils.rabbitmq, "ensure_coordination_bindings", lambda: True)
    monkeypatch.setattr(api.utils.rabbitmq, "publish_exchange", lambda *a, **k: None)
    monkeypatch.setattr(api.utils.rabbitmq, "publish_exchange_profiled", lambda *a, **k: None)
    # Stub Neo4j client
    class MockClient:
        def run_query(self, cypher, params=None):
            return []
    monkeypatch.setattr("api.services.coordination.get_client", lambda: MockClient())
    monkeypatch.setattr("api.utils.audit.audit_event", lambda *a, **k: None)


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


def test_agent_register_and_list(app, client):
    r = client.post(
        "/api/coordination/agents",
        json={"agent_id": "a1", "role": "strategic", "capabilities": ["plan", "allocate"], "perf_score": 0.9},
        headers=auth_headers(app),
    )
    assert r.status_code == 200
    lst = client.get("/api/coordination/agents", headers=auth_headers(app))
    assert lst.status_code == 200
    agents = lst.get_json()["agents"]
    assert any(a["id"] == "a1" for a in agents)


def test_heartbeat_and_rebalance(app, client):
    # Register two agents first
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "a1", "role": "operational", "capabilities": ["execute"], "perf_score": 0.6},
        headers=auth_headers(app),
    )
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "a2", "role": "operational", "capabilities": ["execute"], "perf_score": 0.7},
        headers=auth_headers(app),
    )
    hb = client.post(
        "/api/coordination/agents/heartbeat",
        json={"agent_id": "a1", "workload": 0.9},
        headers=auth_headers(app),
    )
    assert hb.status_code == 200
    plan = client.post("/api/coordination/rebalance", headers=auth_headers(app))
    assert plan.status_code == 200
    body = plan.get_json()
    assert "migrate_from" in body and "migrate_to" in body


def test_task_allocation(app, client):
    # Register agents with differing workload and perf
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "s1", "role": "strategic", "capabilities": ["plan", "analyze"], "perf_score": 0.8},
        headers=auth_headers(app),
    )
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "t1", "role": "tactical", "capabilities": ["analyze"], "perf_score": 0.6},
        headers=auth_headers(app),
    )
    # Allocate strategic-priority task (priority 2) requiring analyze
    resp = client.post(
        "/api/coordination/tasks/allocate",
        json={"id": "task-1", "type": "analysis", "requirements": ["analyze"], "priority": 2},
        headers=auth_headers(app),
    )
    assert resp.status_code in (200, 409)
    if resp.status_code == 200:
        data = resp.get_json()
        assert data["allocated"] is True
        assert data["agent_id"] in ("s1", "t1")


def test_conflict_resolution_and_consensus(app, client):
    # Register minimal agents
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "x1", "role": "operational", "capabilities": ["exec"], "perf_score": 0.5},
        headers=auth_headers(app),
    )
    client.post(
        "/api/coordination/agents",
        json={"agent_id": "x2", "role": "operational", "capabilities": ["exec"], "perf_score": 0.7},
        headers=auth_headers(app),
    )
    r1 = client.post(
        "/api/coordination/conflict/resolve",
        json={"parties": ["x1", "x2"], "resource": "GPU0", "priority": {"x1": 1, "x2": 2}},
        headers=auth_headers(app),
    )
    assert r1.status_code == 200
    assert r1.get_json().get("resolved") is True

    r2 = client.post(
        "/api/coordination/consensus",
        json={"participants": ["x1", "x2"], "proposal": {"scale": 2}},
        headers=auth_headers(app),
    )
    assert r2.status_code == 200
    assert "decision_id" in r2.get_json()


def test_message_routing_and_knowledge_share(app, client):
    r = client.post(
        "/api/coordination/route",
        json={"kind": "notice", "payload": {"msg": "hello"}, "broadcast": True},
        headers=auth_headers(app),
    )
    assert r.status_code == 200
    ks = client.post(
        "/api/coordination/knowledge/share",
        json={"topic": "best-practices", "content": {"k": "v"}, "tags": ["ops"]},
        headers=auth_headers(app),
    )
    assert ks.status_code == 200
    assert "id" in ks.get_json()
