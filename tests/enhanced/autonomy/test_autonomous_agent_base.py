import os
import types
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

import builtins

# Import the class under test
from api.services.autonomy.autonomous_agent_base import (
    AutonomousAgentBase,
    AgentPersonality,
    AgentCapability,
    AgentState,
    KnowledgeDriftAlert,
)


class DummyNeo4jClient:
    def __init__(self):
        self.queries: List = []
        self.closed = False

    def run_queries_atomic(self, queries):
        self.queries.extend(queries)

    def run_query(self, query: str, params: Dict[str, Any] | None = None):
        # default: no drift
        return []

    def close(self):
        self.closed = True


class DummyAgent(AutonomousAgentBase):
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # simulate some work and metrics update
        self.metrics.tasks_completed += 1
        self.metrics.average_response_time = 0.25
        self.metrics.last_activity = datetime.now(timezone.utc)
        return {"ok": True}


def make_personality():
    return AgentPersonality(
        name="Tester",
        role="test",
        capabilities={AgentCapability.RESEARCH, AgentCapability.ANALYSIS},
        personality_traits={"precision": 1.0},
        decision_making_style="analytical",
        communication_style="concise",
    )


def test_initialization_persists_and_emits(monkeypatch):
    fake_client = DummyNeo4jClient()
    published: List[Dict[str, Any]] = []

    # Mocks
    monkeypatch.setenv("AUTONOMY_DEFAULT_MONITOR_INTERVAL", "1")
    monkeypatch.setenv("DRIFT_SCAN_INTERVAL", "10")

    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.neo4j_client.get_client",
        lambda: fake_client,
    )

    def fake_publish(exchange: str, routing_key: str, message: Dict[str, Any]):
        published.append({"exchange": exchange, "routing_key": routing_key, "message": message})

    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.publish_exchange",
        fake_publish,
    )

    agent = DummyAgent(agent_id="a1", personality=make_personality())

    # verify persisted MERGE query has run
    assert len(fake_client.queries) >= 1
    # verify lifecycle event published
    assert any(p["exchange"] == "agents.lifecycle" for p in published)


def test_health_score_transitions_and_self_heal(monkeypatch):
    fake_client = DummyNeo4jClient()
    published: List[Dict[str, Any]] = []

    monkeypatch.setenv("AUTONOMY_DEFAULT_MONITOR_INTERVAL", "1")

    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.neo4j_client.get_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.publish_exchange",
        lambda e, r, m: published.append({"e": e, "r": r, "m": m}),
    )

    agent = DummyAgent(agent_id="a2", personality=make_personality())

    # Degrade health
    agent.metrics.tasks_completed = 1
    agent.metrics.tasks_failed = 4  # 20% success
    agent.metrics.average_response_time = 8.0
    agent.metrics.last_activity = datetime.now(timezone.utc) - timedelta(hours=2)

    agent._update_health_metrics()
    assert agent.state in (AgentState.DEGRADED, AgentState.FAILED)
    assert 0.0 <= agent.metrics.health_score <= 1.0

    # Improve metrics => should recover to ACTIVE
    agent.metrics.tasks_completed = 10
    agent.metrics.tasks_failed = 0
    agent.metrics.average_response_time = 0.1
    agent.metrics.last_activity = datetime.now(timezone.utc)

    agent._update_health_metrics()
    assert agent.state == AgentState.ACTIVE


def test_self_healing_policy_decisions(monkeypatch):
    fake_client = DummyNeo4jClient()
    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.neo4j_client.get_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.publish_exchange",
        lambda *args, **kwargs: None,
    )

    agent = DummyAgent(agent_id="a3", personality=make_personality())

    # Conservative: ignore mild trigger
    monkeypatch.setenv("AUTONOMY_SAFETY_MODE", "conservative")
    agent.safety_mode = "conservative"
    assert agent._decide_healing_action("health_below_0_6") is None

    # Severe trigger => restart
    assert agent._decide_healing_action("health_below_0_3") == "restart"

    # Balanced or unspecified => optimize on 0.6
    agent.safety_mode = "balanced"
    assert agent._decide_healing_action("health_below_0_6") == "optimize"


def test_drift_heuristic_emits_alert(monkeypatch):
    fake_client = DummyNeo4jClient()

    # Make run_query return churn to trigger alert
    def churn_query(query: str, params=None):
        return [{"id": "k1", "versions": 12}]

    fake_client.run_query = churn_query  # type: ignore

    emitted: List[Dict[str, Any]] = []

    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.neo4j_client.get_client",
        lambda: fake_client,
    )

    def capture_publish(exchange: str, routing_key: str, message: Dict[str, Any]):
        emitted.append({"exchange": exchange, "routing_key": routing_key, "message": message})

    monkeypatch.setattr(
        "api.services.autonomy.autonomous_agent_base.publish_exchange",
        capture_publish,
    )

    agent = DummyAgent(agent_id="a4", personality=make_personality())

    alert = agent._check_for_drift_systemwide()
    assert isinstance(alert, KnowledgeDriftAlert)
    agent._emit_drift_alert(alert)
    assert any(e["exchange"] == "agents.drift" for e in emitted)
