import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from api.services.autonomy.agent_lifecycle_manager import (
    AgentLifecycleManager,
    AgentNeed,
    AgentCreationRequest,
)
from api.services.autonomy.autonomous_agent_base import AgentCapability, AgentPersonality


class DummyNeo4jClient:
    def __init__(self, agents=None, tasks=None, perf=None):
        self.queries: List = []
        self._agents = agents if agents is not None else [{
            "total_agents": 1,
            "all_capabilities": [["analysis"]],
            "agent_states": ["active"],
            "health_scores": [0.9],
            "task_counts": [10],
            "response_times": [0.1],
        }]
        self._tasks = tasks if tasks is not None else [{
            "pending_tasks": 10,
            "required_caps": [["analysis", "execution"]],
            "task_priorities": [5],
            "creation_times": [datetime.now(timezone.utc).isoformat()],
        }]
        self._perf = perf if perf is not None else [{
            "avg_system_load": 0.5,
            "avg_response_time": 0.2,
            "avg_throughput": 100,
            "metric_count": 10,
        }]

    def run_queries_atomic(self, queries):
        self.queries.extend(queries)

    def run_query(self, query: str, params: Dict[str, Any] | None = None):
        if "MATCH (a:Agent)" in query:
            return self._agents
        if "MATCH (t:Task)" in query:
            return self._tasks
        if "MATCH (m:PerformanceMetric)" in query:
            return self._perf
        return []

    def close(self):
        pass


def test_need_assessment_identifies_capability_gap_and_creates_request(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    published: List[Dict[str, Any]] = []

    def fake_publish(exchange: str, routing_key: str, message: Dict[str, Any]):
        published.append({"e": exchange, "r": routing_key, "m": message})

    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        fake_publish,
    )

    mgr = AgentLifecycleManager()
    analysis = mgr._analyze_system_state()
    needs = mgr._identify_agent_needs(analysis)

    # We expect a capability gap for 'execution'
    assert any(n.get("type") == AgentNeed.CAPABILITY_GAP for n in needs)
    # Create request for the first high-priority need
    need = [n for n in needs if n.get("priority", 0) >= 7][0]
    req_id = mgr._create_agent_request(need)
    assert req_id in mgr._active_requests
    assert any(p["r"] == "lifecycle.request.created" for p in published)


def test_design_generation_and_development(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda *args, **kwargs: None,
    )

    mgr = AgentLifecycleManager()
    need = {
        "type": AgentNeed.CAPABILITY_GAP,
        "required_capabilities": {AgentCapability.EXECUTION},
        "priority": 8,
        "justification": "missing execution",
    }
    req_id = mgr._create_agent_request(need)
    req = mgr._active_requests[req_id]

    spec = mgr._generate_agent_design(req)
    assert spec is not None and spec.spec_id

    impl = mgr._develop_agent(spec)
    assert impl is not None and impl.implementation_id and "class GeneratedAgent" in impl.python_code


def test_deploy_without_docker(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setenv("LIFECYCLE_ENABLE_DOCKER", "false")

    mgr = AgentLifecycleManager()

    # Build minimal design/impl
    req = AgentCreationRequest(
        request_id="r1",
        need_type=AgentNeed.CAPABILITY_GAP,
        required_capabilities={AgentCapability.EXECUTION},
        performance_requirements={},
        integration_requirements=[],
        priority=8,
        justification="",
    )

    spec = mgr._generate_agent_design(req)
    impl = mgr._develop_agent(spec)
    result = mgr._deploy_agent(impl)

    assert result.get("success") is True
    assert result.get("agent_id")


def test_failure_paths_publish_events(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    published: List[Dict[str, Any]] = []
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda e, r, m: published.append({"e": e, "r": r, "m": m}),
    )

    mgr = AgentLifecycleManager()
    need = {
        "type": AgentNeed.CAPABILITY_GAP,
        "required_capabilities": {AgentCapability.EXECUTION},
        "priority": 8,
        "justification": "missing execution",
    }
    req_id = mgr._create_agent_request(need)

    # 1) Design failure
    monkeypatch.setattr(mgr, "_generate_agent_design", lambda req: None)
    mgr._process_creation_request(req_id)
    assert any(p["r"] == "lifecycle.request.design_failed" and p["m"]["request_id"] == req_id for p in published)

    # Reset request
    req_id = mgr._create_agent_request(need)

    # 2) Development failure
    def fake_design(req):
        r = AgentCreationRequest(
            request_id=req.request_id,
            need_type=req.need_type,
            required_capabilities=req.required_capabilities,
            performance_requirements={},
            integration_requirements=[],
            priority=8,
            justification="",
        )
        return mgr._generate_agent_design(r)

    # real design, fake dev
    monkeypatch.setattr(mgr, "_generate_agent_design", lambda req: mgr._generate_agent_design(req))
    monkeypatch.setattr(mgr, "_develop_agent", lambda spec: None)
    mgr._process_creation_request(req_id)
    assert any(p["r"] == "lifecycle.request.development_failed" and p["m"]["request_id"] == req_id for p in published)

    # 3) Test failure
    req_id = mgr._create_agent_request(need)
    monkeypatch.setattr(mgr, "_generate_agent_design", lambda req: mgr._generate_agent_design(req))
    monkeypatch.setattr(mgr, "_develop_agent", lambda spec: mgr._develop_agent(spec))
    monkeypatch.setattr(mgr, "_test_agent", lambda impl: {"passed": False, "reason": "unit_failed"})
    mgr._process_creation_request(req_id)
    assert any(p["r"] == "lifecycle.request.testing_failed" and p["m"]["request_id"] == req_id for p in published)

    # 4) Deploy failure
    req_id = mgr._create_agent_request(need)
    monkeypatch.setattr(mgr, "_test_agent", lambda impl: {"passed": True})
    monkeypatch.setattr(mgr, "_deploy_agent", lambda impl: {"success": False, "error": "boom"})
    mgr._process_creation_request(req_id)
    assert any(p["r"] == "lifecycle.request.deployment_failed" and p["m"]["request_id"] == req_id for p in published)


def test_retirement_updates_substrate_and_events(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    published: List[Dict[str, Any]] = []
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda e, r, m: published.append({"e": e, "r": r, "m": m}),
    )

    mgr = AgentLifecycleManager()
    # Seed deployed agent
    agent_id = "agent-123"
    mgr._deployed_agents[agent_id] = {
        "request_id": "req-1",
        "spec_id": "spec-1",
        "implementation_id": "impl-1",
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "container_id": None,
        "status": "active",
    }
    ok = mgr.retire_agent(agent_id)
    assert ok is True
    assert agent_id not in mgr._deployed_agents
    assert any(p["r"] == "lifecycle.agent.retiring" for p in published)
    assert any(p["r"] == "lifecycle.agent.retired" for p in published)


def test_end_to_end_simulated_deployment(monkeypatch):
    # Docker disabled -> simulated deployment path
    fake_client = DummyNeo4jClient()
    monkeypatch.setenv("LIFECYCLE_ENABLE_DOCKER", "false")
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.neo4j_client.get_client",
        lambda: fake_client,
    )
    published: List[Dict[str, Any]] = []
    monkeypatch.setattr(
        "api.services.autonomy.agent_lifecycle_manager.publish_exchange",
        lambda e, r, m: published.append({"e": e, "r": r, "m": m}),
    )

    mgr = AgentLifecycleManager()
    need = {
        "type": AgentNeed.CAPABILITY_GAP,
        "required_capabilities": {AgentCapability.EXECUTION},
        "priority": 8,
        "justification": "missing execution",
    }
    req_id = mgr._create_agent_request(need)
    # Run synchronously for test determinism
    mgr._process_creation_request(req_id)

    # Expect deployed event and DeployedAgent registration
    deployed_events = [p for p in published if p["r"] == "lifecycle.agent.deployed"]
    assert deployed_events, "expected deployed event"
    # Verify Neo4j recorded creation request, design, implementation, and deployed agent
    # Check queries were recorded (simple sanity: at least 3 upserts)
    assert len(fake_client.queries) >= 3
