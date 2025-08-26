import json
import types
import pytest

from api.app import create_app


class DummyNeo4jClient:
    def __init__(self):
        self.queries = []
        self._agents = [{
            "total_agents": 0,
            "all_capabilities": [[]],
            "agent_states": [],
            "health_scores": [],
            "task_counts": [],
            "response_times": [],
        }]
        self._tasks = [{
            "pending_tasks": 0,
            "required_caps": [[]],
            "task_priorities": [],
            "creation_times": [],
        }]
        self._perf = [{
            "avg_system_load": 0.05,
            "avg_response_time": 0.1,
            "avg_throughput": 10,
            "metric_count": 1,
        }]

    def run_queries_atomic(self, queries):
        self.queries.extend(queries)

    def run_query(self, query: str, params=None):
        if "MATCH (a:Agent)" in query:
            return self._agents
        if "MATCH (t:Task)" in query:
            return self._tasks
        if "MATCH (m:PerformanceMetric)" in query:
            return self._perf
        return []

    def close(self):
        pass


@pytest.fixture()
def app(monkeypatch):
    # Mock Neo4j client and publish
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: DummyNeo4jClient(),
    )
    published = []
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda e, r, m: published.append({"e": e, "r": r, "m": m}),
    )

    app = create_app()
    # attach published list for assertions via app context
    app.extensions["_published_events"] = published
    yield app


def test_manual_lifecycle_request_route_returns_202_and_queues(app):
    client = app.test_client()
    payload = {
        "need_type": "capability_gap",
        "required_capabilities": ["execution"],
        "priority": 8,
        "justification": "route test",
    }
    res = client.post("/api/autonomy/lifecycle/requests", json=payload)
    assert res.status_code == 202
    data = res.get_json()
    assert data.get("request_id")

    published = app.extensions["_published_events"]
    assert any(p["r"] == "lifecycle.request.created" for p in published)


def test_manager_start_stop_status(app):
    client = app.test_client()

    # Start
    r = client.post("/api/autonomy/lifecycle/manager/start")
    assert r.status_code == 200

    # Status should reflect running
    s = client.get("/api/autonomy/lifecycle/manager/status")
    assert s.status_code == 200
    status = s.get_json()
    assert status.get("running") is True

    # Stop
    r2 = client.post("/api/autonomy/lifecycle/manager/stop")
    assert r2.status_code == 200
    s2 = client.get("/api/autonomy/lifecycle/manager/status")
    assert s2.get_json().get("running") is False


def test_retirement_assessment_helper(monkeypatch):
    # Build manager directly to access helper
    from api.services.autonomy.agent_lifecycle_manager import AgentLifecycleManager

    # Mock persistence and publishing
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: DummyNeo4jClient(),
    )
    retired = []
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda e, r, m: retired.append({"r": r, "m": m}),
    )

    mgr = AgentLifecycleManager()
    # Seed two agents so retirement can happen when load is low
    mgr._deployed_agents["a1"] = {"deployed_at": "2021-01-01T00:00:00Z"}
    mgr._deployed_agents["a2"] = {"deployed_at": "2022-01-01T00:00:00Z"}

    analysis = {
        "performance": {"avg_system_load": 0.05},
    }
    retired_id = mgr._retirement_assessment(analysis)
    assert retired_id in ("a1", "a2")
    # Ensure retired event published
    assert any(x["r"] == "lifecycle.agent.retired" for x in retired)
