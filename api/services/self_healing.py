from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import statistics
import time

try:
    import docker  # type: ignore
    _docker_available = True
except Exception:  # pragma: no cover
    docker = None
    _docker_available = False

from ..utils.audit import audit_event
from ..utils.rabbitmq import publish_exchange
from ..utils.neo4j_client import get_client


@dataclass
class Anomaly:
    metric: str
    value: float
    baseline: float
    zscore: float
    severity: str
    hint: str


@dataclass
class Diagnosis:
    issue_type: str
    root_cause: str
    confidence: float
    impacted_components: List[str] = field(default_factory=list)
    recommended_strategies: List[str] = field(default_factory=list)


@dataclass
class HealingStrategy:
    name: str
    description: str
    safety_level: str  # low|medium|high
    cost: float  # relative cost (0-1)
    actions: List[Dict[str, Any]]


class AnomalyDetector:
    def __init__(self):
        # baselines per metric: mean, stdev
        self._baselines: Dict[str, Tuple[float, float]] = {}

    def update_baseline(self, metric: str, values: List[float]) -> None:
        if not values:
            return
        mu = statistics.fmean(values)
        sd = statistics.pstdev(values) if len(values) > 1 else 0.0
        self._baselines[metric] = (mu, sd)

    def detect(self, metrics: Dict[str, float]) -> List[Anomaly]:
        findings: List[Anomaly] = []
        for k, v in metrics.items():
            mu, sd = self._baselines.get(k, (v, max(1e-6, abs(v)*0.05)))
            z = 0.0 if sd == 0 else (v - mu) / (sd or 1e-6)
            sev = "low"
            if abs(z) > 3:
                sev = "high"
            elif abs(z) > 2:
                sev = "medium"
            hint = "above" if v > mu else "below"
            if abs(z) >= 2:
                findings.append(Anomaly(metric=k, value=v, baseline=mu, zscore=z, severity=sev, hint=hint))
        return findings


class DiagnosisEngine:
    def diagnose(self, anomalies: List[Anomaly], context: Dict[str, Any]) -> Diagnosis:
        # Simple heuristics across common signals
        issue_type = "unknown"
        root = "insufficient data"
        impacted: List[str] = []
        rec: List[str] = []
        conf = 0.5

        m = {a.metric: a for a in anomalies}
        cpu = m.get("cpu_load")
        mem = m.get("memory_usage")
        err = m.get("error_rate")
        lat = m.get("latency_p95")
        qlen = m.get("queue_depth")

        if err and (cpu or mem):
            issue_type = "degradation"
            root = "elevated error rate under resource pressure"
            impacted = context.get("services", [])
            rec = ["scale_service", "restart_unhealthy", "throttle_traffic"]
            conf = 0.75
        elif lat and qlen and lat.zscore > 2 and qlen.zscore > 2:
            issue_type = "backpressure"
            root = "queue growth causing latency"
            impacted = context.get("queues", [])
            rec = ["increase_workers", "rebalance_load", "purge_stuck"]
            conf = 0.7
        elif cpu and cpu.zscore > 3:
            issue_type = "resource_hotspot"
            root = "sustained high CPU"
            impacted = context.get("services", [])
            rec = ["scale_service", "restart_unhealthy"]
            conf = 0.65
        elif mem and mem.zscore > 3:
            issue_type = "memory_pressure"
            root = "sustained high memory"
            impacted = context.get("services", [])
            rec = ["restart_unhealthy", "recycle_container"]
            conf = 0.65

        return Diagnosis(issue_type=issue_type, root_cause=root, confidence=conf, impacted_components=impacted, recommended_strategies=rec)


class StrategyLibrary:
    def list(self) -> List[HealingStrategy]:
        return [
            HealingStrategy(
                name="restart_unhealthy",
                description="Restart unhealthy containers/services",
                safety_level="high",
                cost=0.2,
                actions=[{"type": "docker.restart", "target": "service"}],
            ),
            HealingStrategy(
                name="scale_service",
                description="Increase service replicas to handle load",
                safety_level="medium",
                cost=0.4,
                actions=[{"type": "scale", "target": "service", "delta": +1}],
            ),
            HealingStrategy(
                name="rebalance_load",
                description="Rebalance work across nodes",
                safety_level="high",
                cost=0.3,
                actions=[{"type": "rebalance"}],
            ),
            HealingStrategy(
                name="throttle_traffic",
                description="Apply rate limits to reduce pressure",
                safety_level="low",
                cost=0.1,
                actions=[{"type": "rate_limit", "amount": 0.8}],
            ),
            HealingStrategy(
                name="purge_stuck",
                description="Remove stuck items from queues",
                safety_level="medium",
                cost=0.2,
                actions=[{"type": "queue.purge"}],
            ),
            HealingStrategy(
                name="recycle_container",
                description="Stop and start a container to clear state",
                safety_level="medium",
                cost=0.3,
                actions=[{"type": "docker.recycle"}],
            ),
        ]

    def get(self, name: str) -> Optional[HealingStrategy]:
        for s in self.list():
            if s.name == name:
                return s
        return None


class StrategySelector:
    def __init__(self):
        # Track effectiveness per strategy name
        self._scores: Dict[str, Dict[str, float]] = {}  # {name: {success: x, attempts: y}}

    def record_outcome(self, name: str, success: bool) -> None:
        rec = self._scores.setdefault(name, {"success": 0.0, "attempts": 0.0})
        rec["attempts"] += 1
        if success:
            rec["success"] += 1

    def best(self, candidates: List[str]) -> Optional[str]:
        if not candidates:
            return None
        # Pick highest success rate (fallback to lowest cost by name length for determinism)
        def score(name: str) -> float:
            rec = self._scores.get(name, None)
            if not rec or rec["attempts"] == 0:
                return 0.5
            return rec["success"] / max(1.0, rec["attempts"])
        return max(candidates, key=score)


class RecoveryExecutor:
    def __init__(self):
        self.lib = StrategyLibrary()

    def execute(self, strategy_name: str, context: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        strat = self.lib.get(strategy_name)
        if not strat:
            return {"applied": False, "reason": "unknown_strategy"}
        plan = {"strategy": strat.name, "actions": strat.actions, "dry_run": dry_run}
        if dry_run:
            return {"applied": False, "plan": plan, "dry_run": True}
        # Execute actions (stubbed)
        applied_actions: List[Dict[str, Any]] = []
        for act in strat.actions:
            typ = act.get("type")
            if typ.startswith("docker.") and _docker_available:
                # Example: restart or recycle service/container ids from context
                try:
                    client = docker.from_env()
                    for c_id in context.get("containers", []):
                        c = client.containers.get(c_id)
                        if typ == "docker.restart":
                            c.restart()
                        elif typ == "docker.recycle":
                            c.stop(); c.start()
                    applied_actions.append({"type": typ, "targets": context.get("containers", [])})
                except Exception as e:  # pragma: no cover
                    applied_actions.append({"type": typ, "error": str(e)})
            else:
                # Simulate success
                applied_actions.append({"type": typ, "status": "ok"})
        return {"applied": True, "strategy": strat.name, "actions": applied_actions}


class LearningEngine:
    def __init__(self, selector: StrategySelector):
        self.selector = selector

    def update(self, strategy: str, outcome: Dict[str, Any]) -> None:
        self.selector.record_outcome(strategy, success=bool(outcome.get("applied")))


class SelfHealingService:
    def __init__(self):
        self.detector = AnomalyDetector()
        self.diagnoser = DiagnosisEngine()
        self.selector = StrategySelector()
        self.executor = RecoveryExecutor()
        self.learner = LearningEngine(self.selector)

    def analyze(self, metrics: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        anomalies = self.detector.detect(metrics)
        diag = self.diagnoser.diagnose(anomalies, context)
        event = {
            "anomalies": [a.__dict__ for a in anomalies],
            "diagnosis": diag.__dict__,
        }
        publish_exchange("ops.selfhealing", "analyze", event)
        audit_event("self_healing.analyze", event, context.get("user"))
        return event

    def heal(self, issue: Dict[str, Any], context: Dict[str, Any], dry_run: bool = True, strategy: Optional[str] = None) -> Dict[str, Any]:
        # Choose strategy
        diag = Diagnosis(**issue["diagnosis"]) if "diagnosis" in issue else self.diagnoser.diagnose([], context)
        candidates = strategy and [strategy] or diag.recommended_strategies
        chosen = self.selector.best(candidates) or (candidates[0] if candidates else None)
        if not chosen:
            return {"applied": False, "reason": "no_strategy"}
        # Execute
        outcome = self.executor.execute(chosen, context=context, dry_run=dry_run)
        # Persist attempt
        client = get_client()
        client.run_query(
            """
            CREATE (h:HealingAttempt {
                id: apoc.create.uuid(),
                at: timestamp(),
                strategy: $strategy,
                dryRun: $dry_run,
                applied: $applied,
                issueType: $issue_type,
                rootCause: $root_cause
            })
            """,
            {
                "strategy": chosen,
                "dry_run": dry_run,
                "applied": bool(outcome.get("applied")),
                "issue_type": diag.issue_type,
                "root_cause": diag.root_cause,
            },
        )
        # Learn
        self.learner.update(chosen, outcome)
        payload = {"strategy": chosen, "outcome": outcome, "issue": diag.__dict__}
        publish_exchange("ops.selfhealing", "heal", payload)
        audit_event("self_healing.heal", payload, context.get("user"))
        return payload

    def strategies(self) -> List[Dict[str, Any]]:
        return [s.__dict__ for s in self.executor.lib.list()]

    def learning_stats(self) -> Dict[str, Any]:
        return {"selector": self.selector._scores}
