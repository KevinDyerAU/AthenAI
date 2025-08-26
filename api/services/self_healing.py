from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import math
import statistics
import time
import uuid

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
        # Knowledge-based rules
        rules: List[Tuple[Callable[[Dict[str, Anomaly]], bool], Dict[str, Any]]] = [
            # Elevated error rate under CPU or MEM pressure
            (lambda m: ("error_rate" in m) and ("cpu_load" in m or "memory_usage" in m), {
                "issue_type": "degradation",
                "root_cause": "elevated error rate under resource pressure",
                "recommend": ["scale_service", "restart_unhealthy", "throttle_traffic"],
                "confidence": 0.8,
                "impact_key": "services",
            }),
            # Backpressure: latency + queue depth together
            (lambda m: (m.get("latency_p95") and abs(m["latency_p95"].zscore) > 2) and (m.get("queue_depth") and abs(m["queue_depth"].zscore) > 2), {
                "issue_type": "backpressure",
                "root_cause": "queue growth causing latency",
                "recommend": ["increase_workers", "rebalance_load", "purge_stuck"],
                "confidence": 0.75,
                "impact_key": "queues",
            }),
            # CPU hotspot
            (lambda m: m.get("cpu_load") and m["cpu_load"].zscore > 3, {
                "issue_type": "resource_hotspot",
                "root_cause": "sustained high CPU",
                "recommend": ["scale_service", "restart_unhealthy"],
                "confidence": 0.7,
                "impact_key": "services",
            }),
            # Memory pressure
            (lambda m: m.get("memory_usage") and m["memory_usage"].zscore > 3, {
                "issue_type": "memory_pressure",
                "root_cause": "sustained high memory",
                "recommend": ["restart_unhealthy", "recycle_container"],
                "confidence": 0.7,
                "impact_key": "services",
            }),
            # Error spikes without resource pressure -> config or dependency
            (lambda m: ("error_rate" in m) and not ("cpu_load" in m or "memory_usage" in m), {
                "issue_type": "configuration_or_dependency",
                "root_cause": "elevated errors without resource pressure; check recent deploys and dependencies",
                "recommend": ["rollback_config", "restart_unhealthy"],
                "confidence": 0.6,
                "impact_key": "services",
            }),
        ]

        m = {a.metric: a for a in anomalies}
        for predicate, outcome in rules:
            try:
                if predicate(m):
                    return Diagnosis(
                        issue_type=outcome["issue_type"],
                        root_cause=outcome["root_cause"],
                        confidence=outcome["confidence"],
                        impacted_components=context.get(outcome["impact_key"], []),
                        recommended_strategies=outcome["recommend"],
                    )
            except Exception:
                continue

        return Diagnosis(issue_type="unknown", root_cause="insufficient data", confidence=0.5, impacted_components=context.get("services", []), recommended_strategies=[])


class StrategyLibrary:
    def list(self) -> List[HealingStrategy]:
        return [
            HealingStrategy(
                name="restart_unhealthy",
                description="Restart unhealthy containers/services",
                safety_level="high",
                cost=0.2,
                actions=[{"type": "docker.restart", "target": "service"}],
                # Rollback may be a no-op for restart
            ),
            HealingStrategy(
                name="rollback_config",
                description="Rollback to last known good configuration",
                safety_level="medium",
                cost=0.5,
                actions=[{"type": "config.rollback"}],
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

    def _verify(self, context: Dict[str, Any]) -> bool:
        verifier: Optional[Callable[[], bool]] = context.get("verify")  # optional callable provided by caller
        if callable(verifier):
            try:
                return bool(verifier())
            except Exception:
                return False
        # default accept when no verifier is provided
        return True

    def _rollback(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Best-effort rollback stubs
        rolled: List[Dict[str, Any]] = []
        for act in reversed(actions):
            typ = act.get("type", "")
            if typ == "scale":
                # Invert scale delta
                delta = act.get("delta", 0)
                rolled.append({"type": "scale", "delta": -delta, "status": "ok"})
            elif typ in ("config.rollback", "rebalance", "rate_limit", "queue.purge"):
                # No-op or idempotent; mark as rolled
                rolled.append({"type": typ, "status": "noop"})
            elif typ.startswith("docker."):
                rolled.append({"type": typ, "status": "noop"})
        return rolled

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
                # Non-docker actions: try integration hooks or simulate
                if typ == "config.rollback":
                    gitops = context.get("gitops")  # expects .rollback(target?)
                    target = context.get("config_target")
                    try:
                        if gitops and hasattr(gitops, "rollback"):
                            res = gitops.rollback(target)
                            applied_actions.append({"type": typ, "target": target, "status": bool(res) and "ok" or "failed"})
                        else:
                            applied_actions.append({"type": typ, "target": target, "status": "simulated"})
                    except Exception as e:
                        applied_actions.append({"type": typ, "target": target, "error": str(e)})
                elif typ == "scale":
                    scaler = context.get("scaler")  # expects .scale(service, delta)
                    svc_name = context.get("service")
                    delta = act.get("delta", 0)
                    try:
                        if scaler and hasattr(scaler, "scale") and svc_name:
                            scaler.scale(svc_name, delta)
                            applied_actions.append({"type": typ, "service": svc_name, "delta": delta, "status": "ok"})
                        else:
                            applied_actions.append({"type": typ, "service": svc_name, "delta": delta, "status": "simulated"})
                    except Exception as e:
                        applied_actions.append({"type": typ, "service": svc_name, "delta": delta, "error": str(e)})
                elif typ == "rebalance":
                    applied_actions.append({"type": typ, "status": "simulated"})
                elif typ == "rate_limit":
                    applied_actions.append({"type": typ, "amount": act.get("amount"), "status": "simulated"})
                elif typ == "queue.purge":
                    q = context.get("queue")
                    applied_actions.append({"type": typ, "queue": q, "status": "simulated"})
                else:
                    # Fallback
                    applied_actions.append({"type": typ, "status": "ok"})
        verified = self._verify(context)
        rolled_back: List[Dict[str, Any]] = []
        if not verified:
            rolled_back = self._rollback(applied_actions, context)
        return {"applied": verified, "strategy": strat.name, "actions": applied_actions, "rolled_back": rolled_back, "verified": verified}


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
        # EWMA/Holt-Winters parameters
        self._ewma_alpha = 0.3
        self._hw_alpha = 0.2
        self._hw_beta = 0.1
        self._hw_gamma = 0.1
        # Internal seasonal states per metric for simple HW (additive, period configurable)
        self._season_len = 10
        self._hw_state: Dict[str, Dict[str, float]] = {}  # {metric: {level, trend}}

    def analyze(self, metrics: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        # Update predictive baselines (EWMA + simple HW level/trend)
        self._update_predictive_baselines(metrics)
        anomalies = self.detector.detect(metrics)
        diag = self.diagnoser.diagnose(anomalies, context)
        event = {
            "anomalies": [a.__dict__ for a in anomalies],
            "diagnosis": diag.__dict__,
        }
        # Persist time-series snapshot and anomalies
        try:
            self.record_metrics_snapshot(metrics)
            for a in anomalies:
                self.record_anomaly(a)
        except Exception:
            pass
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
        healing_id = str(uuid.uuid4())
        client.run_query(
            """
            CREATE (h:HealingAttempt {
                id: $id,
                at: timestamp(),
                strategy: $strategy,
                dryRun: $dry_run,
                applied: $applied,
                verified: $verified,
                issueType: $issue_type,
                rootCause: $root_cause
            })
            """,
            {
                "id": healing_id,
                "strategy": chosen,
                "dry_run": dry_run,
                "applied": bool(outcome.get("applied")),
                "verified": bool(outcome.get("verified", outcome.get("applied", False))),
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

    # --- Predictive baselines and time-series storage ---
    def _update_predictive_baselines(self, metrics: Dict[str, float]) -> None:
        # EWMA update affects detector baselines stdev lightly (keep sd as prior)
        for k, v in metrics.items():
            mu, sd = self.detector._baselines.get(k, (v, max(1e-6, abs(v) * 0.05)))
            ewma = self._ewma_alpha * v + (1 - self._ewma_alpha) * mu
            self.detector._baselines[k] = (ewma, sd)
            # Simple Holt-Winters additive (level/trend only)
            st = self._hw_state.get(k, {"level": v, "trend": 0.0})
            level = self._hw_alpha * v + (1 - self._hw_alpha) * (st["level"] + st["trend"]) 
            trend = self._hw_beta * (level - st["level"]) + (1 - self._hw_beta) * st["trend"]
            self._hw_state[k] = {"level": level, "trend": trend}

    def forecast(self, metric: str, steps: int = 1) -> float:
        st = self._hw_state.get(metric)
        if not st:
            mu, _ = self.detector._baselines.get(metric, (0.0, 0.0))
            return mu
        return st["level"] + steps * st["trend"]

    def record_metrics_snapshot(self, metrics: Dict[str, float]) -> None:
        client = get_client()
        client.run_query(
            """
            CREATE (m:MetricSnapshot {id: $id, at: timestamp(), metrics: $metrics})
            """,
            {"id": str(uuid.uuid4()), "metrics": metrics},
        )

    def record_anomaly(self, anomaly: Anomaly) -> None:
        client = get_client()
        client.run_query(
            """
            CREATE (a:AnomalyEvent {id: $id, at: timestamp(), metric: $metric, value: $value, baseline: $baseline, zscore: $z, severity: $sev, hint: $hint})
            """,
            {
                "id": str(uuid.uuid4()),
                "metric": anomaly.metric,
                "value": anomaly.value,
                "baseline": anomaly.baseline,
                "z": anomaly.zscore,
                "sev": anomaly.severity,
                "hint": anomaly.hint,
            },
        )

    def get_metric_trend(self, metric: str, limit: int = 100) -> List[Tuple[int, float]]:
        client = get_client()
        rows = client.run_query(
            """
            MATCH (m:MetricSnapshot)
            WITH m ORDER BY m.at DESC LIMIT $limit
            RETURN m.at AS at, m.metrics[$metric] AS value
            ORDER BY at ASC
            """,
            {"limit": int(limit), "metric": metric},
        )
        return [(r[0], r[1]) for r in rows if r and len(r) >= 2]
