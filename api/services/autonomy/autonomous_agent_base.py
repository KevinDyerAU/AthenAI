from __future__ import annotations
import os
import json
import time
import uuid
import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

# Optional OpenAI import (graceful if missing)
try:
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None

from ...utils import neo4j_client
from ...utils.rabbitmq import publish_exchange


class AgentState(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RETIRING = "retiring"
    RETIRED = "retired"


class AgentCapability(Enum):
    RESEARCH = "research"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    DEVELOPMENT = "development"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    EXECUTION = "execution"
    QUALITY_ASSURANCE = "quality_assurance"
    MONITORING = "monitoring"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"


@dataclass
class AgentPersonality:
    name: str
    role: str
    capabilities: Set[AgentCapability]
    personality_traits: Dict[str, Any]
    decision_making_style: str
    communication_style: str
    risk_tolerance: float = 0.5
    learning_rate: float = 0.1
    collaboration_preference: float = 0.7
    autonomy_level: float = 0.8


@dataclass
class AgentMetrics:
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_response_time: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    knowledge_contributions: int = 0
    collaboration_score: float = 0.0
    autonomy_score: float = 0.0
    health_score: float = 1.0
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeDriftAlert:
    alert_id: str
    agent_id: str
    drift_type: str
    severity: str
    description: str
    affected_knowledge: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False


class AutonomousAgentBase:
    """
    Foundational autonomous agent base class providing:
    - Lifecycle management and event emission
    - Health monitoring and metrics
    - Knowledge drift detection integration
    - Self-healing strategy hooks
    - Optional AI-assisted decision making
    Integrates with existing NeoV3 infrastructure: Neo4j and RabbitMQ.
    """

    def __init__(
        self,
        agent_id: str,
        personality: AgentPersonality,
        monitor_interval_sec: Optional[int] = None,
    ) -> None:
        self.agent_id = agent_id
        self.personality = personality
        self.state = AgentState.INITIALIZING
        self.metrics = AgentMetrics(agent_id=agent_id)

        # Config
        self.monitor_interval_sec = monitor_interval_sec or int(os.getenv("AUTONOMY_DEFAULT_MONITOR_INTERVAL", "30"))
        self.drift_scan_interval = int(os.getenv("DRIFT_SCAN_INTERVAL", "300"))
        self.safety_mode = os.getenv("AUTONOMY_SAFETY_MODE", "conservative")
        self.healing_policy = os.getenv("HEALING_POLICY", "restart_then_roll_back")

        # Optional OpenAI
        self._openai_enabled = False
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and openai is not None:
            try:
                openai.api_key = api_key
                self._openai_enabled = True
            except Exception:
                self._openai_enabled = False

        # Runtime
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._event_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

        # Logging
        self.logger = logging.getLogger(f"autonomy.agent.{self.agent_id}")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

        # Initialize in substrate
        self._initialize_in_substrate()
        self._emit_lifecycle("initialized", reason="construct")

    # -------------------------- Public API --------------------------
    def start(self) -> None:
        """Start the autonomous agent's monitoring and set ACTIVE state."""
        if self._running:
            return
        self._running = True
        self.state = AgentState.ACTIVE
        self._emit_lifecycle("started", reason="start")
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self) -> None:
        """Stop gracefully."""
        self.state = AgentState.RETIRING
        self._running = False
        self._emit_lifecycle("stopping", reason="stop")
        # Join monitor thread
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=self.monitor_interval_sec + 5)
        self.state = AgentState.RETIRED
        self._emit_lifecycle("stopped", reason="stop_complete")

    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        handlers = self._event_handlers.setdefault(event_type, [])
        handlers.append(handler)

    # To be implemented by subclasses
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - abstract-like
        raise NotImplementedError

    # -------------------------- Internals --------------------------
    def _initialize_in_substrate(self) -> None:
        """Upsert agent record in Neo4j."""
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (a:Agent {agent_id: $agent_id})\n"
                    "ON CREATE SET a.name=$name, a.role=$role, a.capabilities=$capabilities, a.state=$state, a.created_at=datetime(), a.updated_at=datetime(), a.personality=$personality\n"
                    "ON MATCH SET a.state=$state, a.updated_at=datetime()",
                    {
                        "agent_id": self.agent_id,
                        "name": self.personality.name,
                        "role": self.personality.role,
                        "capabilities": [c.value for c in self.personality.capabilities],
                        "state": self.state.value,
                        "personality": json.dumps(self.personality.personality_traits),
                    },
                )
            ])
        finally:
            client.close()

    def _update_substrate_status(self) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "SET a.state=$state, a.updated_at=datetime(), a.health_score=$health_score, a.tasks_completed=$tasks_completed, a.tasks_failed=$tasks_failed, a.average_response_time=$avg_response_time",
                    {
                        "agent_id": self.agent_id,
                        "state": self.state.value,
                        "health_score": self.metrics.health_score,
                        "tasks_completed": self.metrics.tasks_completed,
                        "tasks_failed": self.metrics.tasks_failed,
                        "avg_response_time": self.metrics.average_response_time,
                    },
                )
            ])
        finally:
            client.close()

    def _emit_event_local(self, event_type: str, data: Dict[str, Any]) -> None:
        for h in self._event_handlers.get(event_type, []):
            try:
                h(data)
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Event handler error: {e}")

    def _emit_lifecycle(self, state: str, reason: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        event_id = str(uuid.uuid4())
        payload = {
            "agent_id": self.agent_id,
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": state,
            "reason": reason,
            "metadata": metadata or {},
        }
        publish_exchange("agents.lifecycle", f"lifecycle.{state}", payload)
        self._persist_lifecycle_event(event_id, state, reason, metadata)
        self._emit_event_local("agent_lifecycle", payload)

    def _persist_lifecycle_event(self, event_id: str, state: str, reason: Optional[str], metadata: Optional[Dict[str, Any]]) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (e:LifecycleEvent {event_id: $event_id})\n"
                    "ON CREATE SET e.agent_id=$agent_id, e.timestamp=$timestamp, e.state=$state, e.reason=$reason, e.metadata=$metadata\n"
                    "MERGE (a)-[:HAS_EVENT]->(e)",
                    {
                        "agent_id": self.agent_id,
                        "event_id": event_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "state": state,
                        "reason": reason,
                        "metadata": metadata or {},
                    },
                )
            ])
        finally:
            client.close()

    def _publish_metrics(self) -> None:
        metric_id = str(uuid.uuid4())
        payload = {
            "agent_id": self.agent_id,
            "metric_id": metric_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": self.metrics.resource_utilization.get("cpu"),
            "mem": self.metrics.resource_utilization.get("mem"),
            "latency_ms": self.metrics.average_response_time * 1000.0 if self.metrics.average_response_time else None,
            "success_rate": self._success_rate(),
            "throughput": None,
            "metadata": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "health_score": self.metrics.health_score,
            },
        }
        publish_exchange("agents.health", "health.metrics", payload)
        # persist minimal metric node
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (m:AgentMetrics {metric_id: $metric_id})\n"
                    "ON CREATE SET m.agent_id=$agent_id, m.timestamp=$timestamp, m.cpu=$cpu, m.mem=$mem, m.latency_ms=$latency_ms, m.success_rate=$success_rate, m.throughput=$throughput, m.metadata=$metadata\n"
                    "MERGE (a)-[:HAS_METRIC]->(m)",
                    payload | {"agent_id": self.agent_id},
                )
            ])
        finally:
            client.close()

    def _emit_drift_alert(self, alert: KnowledgeDriftAlert) -> None:
        payload = {
            "agent_id": self.agent_id,
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "signal": alert.drift_type,
            "severity": alert.severity,
            "details": {"description": alert.description, "affected": alert.affected_knowledge},
        }
        publish_exchange("agents.drift", f"drift.{alert.drift_type}", payload)
        # Persist
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (d:KnowledgeDriftAlert {alert_id: $alert_id})\n"
                    "ON CREATE SET d.agent_id=$agent_id, d.timestamp=$timestamp, d.signal=$signal, d.severity=$severity, d.details=$details\n"
                    "MERGE (a)-[:RAISED_DRIFT]->(d)",
                    {
                        "agent_id": self.agent_id,
                        "alert_id": alert.alert_id,
                        "timestamp": alert.timestamp.isoformat(),
                        "signal": alert.drift_type,
                        "severity": alert.severity,
                        "details": {"description": alert.description, "affected": alert.affected_knowledge},
                    },
                )
            ])
        finally:
            client.close()

    # -------------------------- Monitoring & Health --------------------------
    def _monitoring_loop(self) -> None:
        last_drift_check = 0.0
        while self._running:
            try:
                self._update_health_metrics()
                self._update_substrate_status()
                self._publish_metrics()

                now = time.time()
                if now - last_drift_check >= self.drift_scan_interval:
                    alert = self._check_for_drift_systemwide()
                    if alert:
                        self._emit_drift_alert(alert)
                    last_drift_check = now

                time.sleep(self.monitor_interval_sec)
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(min(self.monitor_interval_sec * 2, 120))

    def _success_rate(self) -> float:
        total = self.metrics.tasks_completed + self.metrics.tasks_failed
        return self.metrics.tasks_completed / total if total > 0 else 1.0

    def _update_health_metrics(self) -> None:
        # Simple health score: success rate (40%) + inverse latency (30%) + recency (30%)
        success = self._success_rate()
        response_time_score = max(0.0, 1.0 - (self.metrics.average_response_time / 10.0)) if self.metrics.average_response_time else 1.0
        elapsed = (datetime.now(timezone.utc) - self.metrics.last_activity).total_seconds()
        activity_score = max(0.0, 1.0 - (elapsed / 3600.0))  # decay over 1h
        self.metrics.health_score = success * 0.4 + response_time_score * 0.3 + activity_score * 0.3

        if self.metrics.health_score < 0.3:
            self.state = AgentState.FAILED
            self._maybe_self_heal(trigger="health_below_0_3")
        elif self.metrics.health_score < 0.6:
            self.state = AgentState.DEGRADED
            self._maybe_self_heal(trigger="health_below_0_6")
        elif self.state in (AgentState.DEGRADED, AgentState.FAILED):
            self.state = AgentState.ACTIVE

    # -------------------------- Drift Detection (basic) --------------------------
    def _check_for_drift_systemwide(self) -> Optional[KnowledgeDriftAlert]:
        """Basic heuristic drift detector using recent KnowledgeEntity version churn.
        This is a placeholder; specialized agents can override with deeper checks.
        """
        try:
            client = neo4j_client.get_client()
            try:
                records = client.run_query(
                    """
                    MATCH (k:KnowledgeEntity)-[:HAS_VERSION]->(v:KnowledgeVersion)
                    WHERE v.created_at >= datetime() - duration({hours:1})
                    WITH k, count(v) AS versions
                    WHERE versions > 10
                    RETURN k.id AS id, versions
                    LIMIT 5
                    """
                )
                impacted = [r["id"] for r in records]
            finally:
                client.close()
            if impacted:
                return KnowledgeDriftAlert(
                    alert_id=str(uuid.uuid4()),
                    agent_id=self.agent_id,
                    drift_type="rapid_changes",
                    severity="medium",
                    description="High version churn in last hour",
                    affected_knowledge=impacted,
                )
            return None
        except Exception as e:  # pragma: no cover
            self.logger.warning(f"Drift check failed: {e}")
            return None

    # -------------------------- Self-Healing --------------------------
    def _maybe_self_heal(self, trigger: str) -> None:
        try:
            decision = self._decide_healing_action(trigger)
            if decision:
                self._apply_healing_strategy(decision)
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Self-heal failed: {e}")

    def _decide_healing_action(self, trigger: str) -> Optional[str]:
        """Minimal policy-based decision with optional AI-assisted reasoning."""
        # Safety-mode guardrails
        if self.safety_mode == "conservative" and trigger == "health_below_0_6":
            return None  # wait for stronger signal

        # Optional AI reasoning
        if self._openai_enabled:
            try:
                prompt = (
                    f"Agent {self.agent_id} trigger={trigger}, health={self.metrics.health_score:.2f}, "
                    f"success_rate={self._success_rate():.2f}, avg_latency={self.metrics.average_response_time:.2f}s. "
                    f"Given policy {self.healing_policy}, suggest one of: restart, optimize, scale_down, scale_up, none."
                )
                # Use Chat Completions if available; fallback to simple policy
                resp = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=16,
                )
                text = resp["choices"][0]["message"]["content"].lower()
                for opt in ("restart", "optimize", "scale_down", "scale_up", "none"):
                    if opt in text:
                        return None if opt == "none" else opt
            except Exception:
                pass

        # Simple defaults
        if trigger == "health_below_0_3":
            return "restart"
        if trigger == "health_below_0_6":
            return "optimize"
        return None

    def _apply_healing_strategy(self, strategy: str) -> None:
        self.logger.info(f"Applying healing strategy: {strategy}")
        if strategy == "restart":
            # lifecycle bounce events
            self._emit_lifecycle("restarting", reason="self_heal")
            # No real process control here; subclasses can override to restart workers
            self._emit_lifecycle("restarted", reason="self_heal")
        elif strategy == "optimize":
            # Placeholder for internal optimization hooks
            pass
        elif strategy == "scale_down":
            pass
        elif strategy == "scale_up":
            pass

