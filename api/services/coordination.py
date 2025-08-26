from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time
import uuid

from ..utils.rabbitmq import publish_exchange_profiled
from ..utils.audit import audit_event
from ..utils.neo4j_client import get_client


@dataclass
class AgentInfo:
    id: str
    role: str  # strategic|tactical|operational
    capabilities: List[str]
    workload: float = 0.0  # 0..1
    perf_score: float = 0.5  # 0..1 historical quality metric
    last_heartbeat: float = field(default_factory=lambda: time.time())


@dataclass
class Task:
    id: str
    type: str
    requirements: List[str]
    priority: int = 0


class CoordinationService:
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}

    # --- Hierarchy and registration ---
    def register_agent(self, agent_id: str, role: str, capabilities: List[str], perf_score: float = 0.5) -> Dict[str, Any]:
        info = AgentInfo(id=agent_id, role=role, capabilities=capabilities, perf_score=perf_score)
        self._agents[agent_id] = info
        evt = {"agent": info.__dict__}
        publish_exchange_profiled("coordination", "agent.register", evt, profile="low")
        audit_event("coord.agent.register", evt, agent_id)
        return {"status": "registered", "agent": info.__dict__}

    def heartbeat(self, agent_id: str, workload: Optional[float] = None) -> Dict[str, Any]:
        info = self._agents.get(agent_id)
        if not info:
            return {"status": "unknown_agent"}, 404
        info.last_heartbeat = time.time()
        if workload is not None:
            info.workload = max(0.0, min(1.0, workload))
        publish_exchange_profiled("coordination", "agent.heartbeat", {"id": agent_id, "workload": info.workload}, profile="low")
        return {"status": "ok", "workload": info.workload}

    def list_agents(self) -> List[Dict[str, Any]]:
        return [a.__dict__ for a in self._agents.values()]

    # --- Task allocation and load balancing ---
    def allocate_task(self, task: Task, sla: Optional[Dict[str, Any]] = None, predict: Optional[Any] = None) -> Dict[str, Any]:
        # Candidate agents with capability match
        candidates = [a for a in self._agents.values() if all(req in a.capabilities for req in task.requirements)]
        if not candidates:
            return {"allocated": False, "reason": "no_capable_agent"}
        # Score: higher perf_score, lower workload, role preference by task priority (strategic for high)
        def score(a: AgentInfo) -> float:
            role_bonus = 0.0
            if task.priority >= 2 and a.role == "strategic":
                role_bonus = 0.1
            elif task.priority == 1 and a.role == "tactical":
                role_bonus = 0.05
            elif task.priority == 0 and a.role == "operational":
                role_bonus = 0.05
            predicted = 0.0
            if predict:
                try:
                    predicted = float(predict(a))
                except Exception:
                    predicted = 0.0
            sla_weight = float((sla or {}).get("weight", 1.0))
            # Higher score is better: prefer high perf, low current/predicted workload; honor SLA weight
            return sla_weight * (a.perf_score + role_bonus) - 0.5 * a.workload - 0.3 * predicted
        chosen = max(candidates, key=score)
        # Record assignment
        client = get_client()
        assignment_id = str(uuid.uuid4())
        client.run_query(
            """
            CREATE (ta:TaskAssignment {id: $id, at: timestamp(), taskId: $task_id, taskType: $type, priority: $prio, agentId: $agent})
            """,
            {"id": assignment_id, "task_id": task.id, "type": task.type, "prio": task.priority, "agent": chosen.id},
        )
        evt = {"task": task.__dict__, "agent": chosen.__dict__}
        publish_exchange_profiled("coordination", "task.allocated", evt, profile="medium")
        audit_event("coord.task.allocate", evt, None)
        # Update agent workload optimistically
        chosen.workload = min(1.0, chosen.workload + 0.1)
        return {"allocated": True, "agent_id": chosen.id, "assignment_id": assignment_id}

    def rebalance(self, apply: bool = False) -> Dict[str, Any]:
        # Simple suggestion: identify overloaded agents and underloaded agents
        overloaded = [a.id for a in self._agents.values() if a.workload > 0.8]
        underloaded = [a.id for a in self._agents.values() if a.workload < 0.3]
        plan = {"migrate_from": overloaded, "migrate_to": underloaded}
        publish_exchange_profiled("coordination", "rebalance.plan", plan, profile="low")
        if apply and overloaded and underloaded:
            # naive pairwise migration commands
            for src, dst in zip(overloaded, underloaded):
                cmd = {"from": src, "to": dst, "at": int(time.time()*1000)}
                publish_exchange_profiled("coordination", "rebalance.migrate", cmd, profile="high")
        return plan

    # --- Conflict resolution and consensus ---
    def resolve_conflict(self, parties: List[str], resource: str, priority: Dict[str, int]) -> Dict[str, Any]:
        # Negotiation: prefer higher priority; tie-break by lower workload
        agents = [self._agents[p] for p in parties if p in self._agents]
        if not agents:
            return {"resolved": False, "reason": "no_parties"}
        chosen = max(agents, key=lambda a: (priority.get(a.id, 0), -a.workload))
        decision_id = str(uuid.uuid4())
        get_client().run_query(
            """
            CREATE (d:CoordDecision {id: $id, at: timestamp(), kind: 'conflict', resource: $res, winner: $win, parties: $parties})
            """,
            {"id": decision_id, "res": resource, "win": chosen.id, "parties": parties},
        )
        evt = {"resource": resource, "winner": chosen.id, "parties": parties}
        publish_exchange_profiled("coordination", "conflict.resolved", evt, profile="high")
        return {"resolved": True, "winner": chosen.id, "decision_id": decision_id}

    def consensus(self, participants: List[str], proposal: Dict[str, Any], weights: Optional[Dict[str, float]] = None, timeout_ms: int = 1000) -> Dict[str, Any]:
        # Simple weighted majority: each participant votes based on workload/perf heuristic if no weights provided
        votes = []
        for pid in participants:
            a = self._agents.get(pid)
            if not a:
                continue
            w = (weights or {}).get(pid, max(0.1, a.perf_score * (1.0 - a.workload)))
            votes.append((pid, w))
        total = sum(w for _, w in votes) or 1.0
        passed = total >= 0.5  # trivial pass condition for demo
        decision_id = str(uuid.uuid4())
        get_client().run_query(
            """
            CREATE (d:CoordDecision {id: $id, at: timestamp(), kind: 'consensus', proposal: $proposal, participants: $parts, weightSum: $sum, passed: $passed})
            """,
            {"id": decision_id, "proposal": proposal, "parts": participants, "sum": total, "passed": bool(passed)},
        )
        evt = {"proposal": proposal, "participants": participants, "passed": bool(passed)}
        publish_exchange_profiled("coordination", "consensus.decision", evt, profile="high")
        return {"decision_id": decision_id, "passed": bool(passed)}

    # --- Message routing ---
    def route_message(self, kind: str, payload: Dict[str, Any], targets: Optional[List[str]] = None, broadcast: bool = False) -> Dict[str, Any]:
        if broadcast:
            publish_exchange_profiled("coordination", f"msg.broadcast.{kind}", payload, profile="medium")
            return {"delivered": "broadcast"}
        if targets:
            for t in targets:
                publish_exchange_profiled("coordination", f"msg.{kind}.{t}", payload, profile="medium")
            return {"delivered": targets}
        return {"delivered": []}

    # --- Knowledge sharing ---
    def share_knowledge(self, author: str, topic: str, content: Dict[str, Any], tags: Optional[List[str]] = None) -> Dict[str, Any]:
        kid = str(uuid.uuid4())
        get_client().run_query(
            """
            CREATE (k:CoordKnowledge {id: $id, at: timestamp(), author: $author, topic: $topic, content: $content, tags: $tags})
            """,
            {"id": kid, "author": author, "topic": topic, "content": content, "tags": tags or []},
        )
        evt = {"id": kid, "author": author, "topic": topic}
        publish_exchange_profiled("coordination", "knowledge.shared", evt, profile="low")
        audit_event("coord.knowledge.share", evt, author)
        return {"id": kid}
