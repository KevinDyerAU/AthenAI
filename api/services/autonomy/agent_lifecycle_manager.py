from __future__ import annotations
import json
import logging
import uuid
import os
import threading
import time
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Optional dependencies
try:
    import docker  # type: ignore
except Exception:  # pragma: no cover
    docker = None

try:
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None

from ...utils import neo4j_client
from ...utils.rabbitmq import publish_exchange
from .autonomous_agent_base import (
    AgentCapability,
    AgentPersonality,
)


class LifecyclePhase(Enum):
    CONCEPTION = "conception"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    OPERATION = "operation"
    RETIREMENT = "retirement"


class AgentNeed(Enum):
    CAPABILITY_GAP = "capability_gap"
    PERFORMANCE_BOTTLENECK = "performance_bottleneck"
    WORKLOAD_INCREASE = "workload_increase"
    SPECIALIZATION_REQUIRED = "specialization_required"
    REDUNDANCY_NEEDED = "redundancy_needed"
    INNOVATION_OPPORTUNITY = "innovation_opportunity"


@dataclass
class AgentCreationRequest:
    request_id: str
    need_type: AgentNeed
    required_capabilities: Set[AgentCapability]
    performance_requirements: Dict[str, Any]
    integration_requirements: List[str]
    priority: int = 5
    deadline: Optional[datetime] = None
    justification: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentDesignSpec:
    spec_id: str
    request_id: str
    personality: AgentPersonality
    technical_requirements: Dict[str, Any]
    integration_patterns: List[Dict[str, Any]]
    performance_targets: Dict[str, float]
    testing_criteria: List[Dict[str, Any]]
    deployment_config: Dict[str, Any]
    estimated_development_time: int
    resource_requirements: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentImplementation:
    implementation_id: str
    spec_id: str
    python_code: str
    configuration_files: Dict[str, str]
    docker_config: Dict[str, Any]
    test_suite: Dict[str, Any]
    documentation: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AgentLifecycleManager:
    """
    Central coordinator for agent lifecycle operations: need assessment, design,
    implementation, deployment, monitoring, and retirement.
    Integrates with NeoV3 utils (Neo4j + RabbitMQ). Docker/OpenAI are optional.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("autonomy.lifecycle")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

        # Internal state
        self._running = False
        self._threads: List[threading.Thread] = []
        self._active_requests: Dict[str, AgentCreationRequest] = {}
        self._active_implementations: Dict[str, AgentImplementation] = {}
        self._deployed_agents: Dict[str, Dict[str, Any]] = {}

        # Config
        self.need_assessment_interval = int(os.getenv("LIFECYCLE_NEED_ASSESSMENT_INTERVAL", "900"))
        self.performance_monitoring_interval = int(os.getenv("LIFECYCLE_PERF_MONITOR_INTERVAL", "300"))
        self.max_concurrent_developments = int(os.getenv("LIFECYCLE_MAX_CONCURRENT_DEVS", "3"))
        self.max_agents_per_capability = int(os.getenv("LIFECYCLE_MAX_PER_CAPABILITY", "5"))

        # Optional services
        self._openai_enabled = False
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and openai is not None:
            try:
                openai.api_key = api_key
                self._openai_enabled = True
            except Exception:
                self._openai_enabled = False

        self._docker_enabled = docker is not None and os.getenv("LIFECYCLE_ENABLE_DOCKER", "true").lower() == "true"
        self._docker_client = None
        if self._docker_enabled:
            try:
                self._docker_client = docker.from_env()
            except Exception:  # pragma: no cover
                self._docker_client = None
                self._docker_enabled = False

    # ------------------------------ Public API ------------------------------
    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self.logger.info("Starting AgentLifecycleManager")
        self._threads = [
            threading.Thread(target=self._need_assessment_loop, daemon=True),
            threading.Thread(target=self._performance_monitoring_loop, daemon=True),
        ]
        for t in self._threads:
            t.start()
        publish_exchange("agents.lifecycle", "lifecycle.manager.started", {"timestamp": datetime.now(timezone.utc).isoformat()})

    def stop(self) -> None:
        self.logger.info("Stopping AgentLifecycleManager")
        self._running = False
        for t in self._threads:
            if t.is_alive():
                t.join(timeout=5)
        # Attempt graceful retirement of tracked agents
        try:
            for agent_id in list(self._deployed_agents.keys()):
                self.retire_agent(agent_id)
        except Exception:  # pragma: no cover
            pass
        publish_exchange("agents.lifecycle", "lifecycle.manager.stopped", {"timestamp": datetime.now(timezone.utc).isoformat()})

    # --------------------------- Background Loops ---------------------------
    def _need_assessment_loop(self) -> None:
        while self._running:
            try:
                analysis = self._analyze_system_state()
                needs = self._identify_agent_needs(analysis)
                for need in needs:
                    if need.get("priority", 0) >= 7:
                        self._create_agent_request(need)
                time.sleep(self.need_assessment_interval)
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Need assessment loop error: {e}")
                time.sleep(60)

    def _performance_monitoring_loop(self) -> None:
        while self._running:
            try:
                # Assess performance and consider retirement decisions
                analysis = self._analyze_system_state()
                try:
                    self._retirement_assessment(analysis)
                except Exception as re:  # pragma: no cover
                    self.logger.warning(f"Retirement assessment error: {re}")
                time.sleep(self.performance_monitoring_interval)
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Performance monitoring loop error: {e}")
                time.sleep(60)

    # -------------------------- Need Assessment ----------------------------
    def _analyze_system_state(self) -> Dict[str, Any]:
        client = neo4j_client.get_client()
        try:
            agents = client.run_query(
                """
                MATCH (a:Agent)
                RETURN 
                    count(a) as total_agents,
                    collect(a.capabilities) as all_capabilities,
                    collect(a.state) as agent_states,
                    collect(a.health_score) as health_scores,
                    collect(a.tasks_completed) as task_counts,
                    collect(a.average_response_time) as response_times
                """
            )
            tasks = client.run_query(
                """
                MATCH (t:Task)
                WHERE t.status IN ['pending','in_progress']
                RETURN count(t) as pending_tasks,
                       collect(t.required_capabilities) as required_caps,
                       collect(t.priority) as task_priorities,
                       collect(t.created_at) as creation_times
                """
            )
            perf = client.run_query(
                """
                MATCH (m:PerformanceMetric)
                WHERE m.timestamp > datetime() - duration('PT1H')
                RETURN avg(m.system_load) as avg_system_load,
                       avg(m.response_time) as avg_response_time,
                       avg(m.throughput) as avg_throughput,
                       count(m) as metric_count
                """
            )
            return {
                "agents": dict(agents[0]) if agents else {},
                "tasks": dict(tasks[0]) if tasks else {},
                "performance": dict(perf[0]) if perf else {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        finally:
            client.close()

    def _identify_agent_needs(self, system_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        needs: List[Dict[str, Any]] = []
        needs += self._identify_capability_gaps(system_analysis)
        needs += self._identify_performance_bottlenecks(system_analysis)
        needs += self._identify_workload_increases(system_analysis)
        needs += self._identify_specialization_needs(system_analysis)
        return needs

    def _identify_capability_gaps(self, system_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps: List[Dict[str, Any]] = []
        required_caps = system_analysis.get("tasks", {}).get("required_caps", [])
        available_caps = system_analysis.get("agents", {}).get("all_capabilities", [])

        def flatten(seq):
            s: Set[str] = set()
            for caps in seq:
                if isinstance(caps, list):
                    for c in caps:
                        if isinstance(c, str):
                            s.add(c)
            return s

        all_required = flatten(required_caps)
        all_available = flatten(available_caps)
        missing = all_required - all_available
        for cap in missing:
            req_caps: Set[AgentCapability] = set()
            try:
                req_caps = {AgentCapability(cap)}
            except Exception:
                req_caps = set()
            gaps.append({
                "type": AgentNeed.CAPABILITY_GAP,
                "capability": cap,
                "priority": 8,
                "justification": f"No agents available with {cap}",
                "required_capabilities": req_caps,
            })
        return gaps

    def _identify_performance_bottlenecks(self, system_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        perf = system_analysis.get("performance", {})
        avg_response = perf.get("avg_response_time") or 0
        avg_load = perf.get("avg_system_load") or 0
        if avg_response and float(avg_response) > 5.0:
            out.append({
                "type": AgentNeed.PERFORMANCE_BOTTLENECK,
                "metric": "response_time",
                "current_value": float(avg_response),
                "threshold": 5.0,
                "priority": 7,
                "justification": "Average response exceeds threshold",
                "required_capabilities": {AgentCapability.EXECUTION},
            })
        if avg_load and float(avg_load) > 0.8:
            out.append({
                "type": AgentNeed.PERFORMANCE_BOTTLENECK,
                "metric": "system_load",
                "current_value": float(avg_load),
                "threshold": 0.8,
                "priority": 8,
                "justification": "System load exceeds threshold",
                "required_capabilities": {AgentCapability.EXECUTION},
            })
        return out

    def _identify_workload_increases(self, system_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        pending = system_analysis.get("tasks", {}).get("pending_tasks") or 0
        if int(pending) > 100:
            out.append({
                "type": AgentNeed.WORKLOAD_INCREASE,
                "priority": 7,
                "justification": f"Pending tasks high ({pending})",
                "required_capabilities": {AgentCapability.EXECUTION},
            })
        return out

    def _identify_specialization_needs(self, system_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Placeholder for deeper domain logic (e.g., repeated failure types)
        return []

    # --------------------------- Request Processing -------------------------
    def _create_agent_request(self, need: Dict[str, Any]) -> str:
        request_id = str(uuid.uuid4())
        creation_request = AgentCreationRequest(
            request_id=request_id,
            need_type=need["type"],
            required_capabilities=need.get("required_capabilities", set()),
            performance_requirements=need.get("performance_requirements", {}),
            integration_requirements=need.get("integration_requirements", []),
            priority=need.get("priority", 5),
            justification=need.get("justification", ""),
        )
        self._active_requests[request_id] = creation_request
        self._store_creation_request(creation_request)
        publish_exchange("agents.lifecycle", "lifecycle.request.created", {
            "request_id": request_id,
            "need_type": creation_request.need_type.value,
            "priority": creation_request.priority,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        # Process in a worker thread
        threading.Thread(target=self._process_creation_request, args=(request_id,), daemon=True).start()
        return request_id

    def _store_creation_request(self, req: AgentCreationRequest) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (r:AgentCreationRequest {request_id: $request_id})\n"
                    "SET r.need_type=$need_type, r.priority=$priority, r.justification=$justification, r.created_at=$created_at",
                    {
                        "request_id": req.request_id,
                        "need_type": req.need_type.value,
                        "priority": req.priority,
                        "justification": req.justification,
                        "created_at": req.created_at.isoformat(),
                    },
                )
            ])
        finally:
            client.close()

    def _process_creation_request(self, request_id: str) -> None:
        try:
            req = self._active_requests.get(request_id)
            if not req:
                return
            # DESIGN
            spec = self._generate_agent_design(req)
            if not spec:
                publish_exchange("agents.lifecycle", "lifecycle.request.design_failed", {"request_id": request_id, "ts": datetime.now(timezone.utc).isoformat()})
                return
            # DEVELOPMENT
            impl = self._develop_agent(spec)
            if not impl:
                publish_exchange("agents.lifecycle", "lifecycle.request.development_failed", {"request_id": request_id, "spec_id": spec.spec_id, "ts": datetime.now(timezone.utc).isoformat()})
                return
            # TESTING
            tests_ok = self._test_agent(impl)
            if not tests_ok.get("passed"):
                publish_exchange("agents.lifecycle", "lifecycle.request.testing_failed", {"request_id": request_id, "implementation_id": impl.implementation_id, "ts": datetime.now(timezone.utc).isoformat(), "result": tests_ok})
                return
            # DEPLOYMENT
            result = self._deploy_agent(impl)
            if result.get("success"):
                agent_id = result["agent_id"]
                self._deployed_agents[agent_id] = {
                    "request_id": request_id,
                    "spec_id": spec.spec_id,
                    "implementation_id": impl.implementation_id,
                    "deployed_at": datetime.now(timezone.utc).isoformat(),
                    "container_id": result.get("container_id"),
                    "status": "active",
                }
                publish_exchange("agents.lifecycle", "lifecycle.agent.deployed", {
                    "agent_id": agent_id,
                    "request_id": request_id,
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
                # Cleanup request
                self._active_requests.pop(request_id, None)
            else:
                publish_exchange("agents.lifecycle", "lifecycle.request.deployment_failed", {"request_id": request_id, "implementation_id": impl.implementation_id, "ts": datetime.now(timezone.utc).isoformat(), "error": result.get("error")})
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Process creation request error: {e}")

    

    # --------------------------- Design Generation -------------------------
    def _generate_agent_design(self, request: AgentCreationRequest) -> Optional[AgentDesignSpec]:
        try:
            requirements_analysis = self._analyze_requirements(request)
            personality = self._generate_agent_personality(request.required_capabilities, requirements_analysis)
            technical_requirements = self._generate_technical_requirements(request, requirements_analysis)
            integration_patterns = self._generate_integration_patterns(request.integration_requirements)
            performance_targets = self._generate_performance_targets(request.performance_requirements)
            testing_criteria = self._generate_testing_criteria(personality, technical_requirements)
            deployment_config = self._generate_deployment_config(technical_requirements, integration_patterns)
            estimated_time = 4  # hours, placeholder
            resource_requirements = {"cpu": 0.25, "mem": "256Mi"}
            spec = AgentDesignSpec(
                spec_id=str(uuid.uuid4()),
                request_id=request.request_id,
                personality=personality,
                technical_requirements=technical_requirements,
                integration_patterns=integration_patterns,
                performance_targets=performance_targets,
                testing_criteria=testing_criteria,
                deployment_config=deployment_config,
                estimated_development_time=estimated_time,
                resource_requirements=resource_requirements,
            )
            self._store_design_spec(spec)
            return spec
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Design generation error: {e}")
            return None

    def _analyze_requirements(self, request: AgentCreationRequest) -> Dict[str, Any]:
        return {
            "need_type": request.need_type.value,
            "priority": request.priority,
            "caps": [c.value for c in request.required_capabilities],
        }

    def _generate_agent_personality(self, required_capabilities: Set[AgentCapability], requirements_analysis: Dict[str, Any]) -> AgentPersonality:
        # Optional OpenAI-driven traits; fallback to defaults
        name = f"Auto-{requirements_analysis['need_type'][:3]}-{uuid.uuid4().hex[:6]}"
        traits: Dict[str, Any] = {"reliability": 0.9, "adaptability": 0.8}
        if self._openai_enabled:
            try:
                prompt = (
                    "Generate a brief JSON object with keys: name, role, personality_traits, "
                    "decision_making_style, communication_style given capabilities "
                    f"{[c.value for c in required_capabilities]} and analysis {json.dumps(requirements_analysis)}"
                )
                resp = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=200,
                )
                data = json.loads(resp["choices"][0]["message"]["content"])  # type: ignore[index]
                name = data.get("name", name)
                role = data.get("role", "generated-agent")
                traits = data.get("personality_traits", traits)
                decision = data.get("decision_making_style", "analytical")
                comms = data.get("communication_style", "concise")
                return AgentPersonality(
                    name=name,
                    role=role,
                    capabilities=required_capabilities,
                    personality_traits=traits,
                    decision_making_style=decision,
                    communication_style=comms,
                )
            except Exception:
                pass
        return AgentPersonality(
            name=name,
            role="autonomous-agent",
            capabilities=required_capabilities,
            personality_traits=traits,
            decision_making_style="analytical",
            communication_style="concise",
        )

    def _generate_technical_requirements(self, request: AgentCreationRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dependencies": ["neo4j", "rabbitmq"],
            "requires_openai": self._openai_enabled,
            "observability": {"health": True, "metrics": True},
        }

    def _generate_integration_patterns(self, integration_requirements: List[str]) -> List[Dict[str, Any]]:
        return [{"type": "rabbitmq_topic", "exchange": "agents.lifecycle"}]

    def _generate_performance_targets(self, perf_requirements: Dict[str, Any]) -> Dict[str, float]:
        return {"p95_latency_s": float(perf_requirements.get("p95_latency_s", 1.0))}

    def _generate_testing_criteria(self, personality: AgentPersonality, tech_reqs: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"name": "unit_basics", "must_pass": True}]

    def _generate_deployment_config(self, tech_reqs: Dict[str, Any], integration_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "environment": {"AUTONOMY_DEFAULT_MONITOR_INTERVAL": "30"},
            "ports": {},
            "volumes": {},
            "dockerfile": """FROM python:3.11-slim\nWORKDIR /app\nCOPY . /app\nRUN pip install --no-cache-dir neo4j pika\nCMD [\"python\", \"agent.py\"]\n""",
        }

    def _store_design_spec(self, spec: AgentDesignSpec) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (s:AgentDesignSpec {spec_id: $spec_id})\n"
                    "SET s.request_id=$request_id, s.created_at=$created_at, s.personality=$personality, s.tech=$tech, s.deployment=$deployment",
                    {
                        "spec_id": spec.spec_id,
                        "request_id": spec.request_id,
                        "created_at": spec.created_at.isoformat(),
                        "personality": {
                            "name": spec.personality.name,
                            "role": spec.personality.role,
                            "capabilities": [c.value for c in spec.personality.capabilities],
                        },
                        "tech": spec.technical_requirements,
                        "deployment": spec.deployment_config,
                    },
                )
            ])
        finally:
            client.close()

    # -------------------------- Development & Tests -------------------------
    def _develop_agent(self, design_spec: AgentDesignSpec) -> Optional[AgentImplementation]:
        try:
            python_code = self._generate_python_code(design_spec)
            config_files = {"README.txt": "Generated agent"}
            docker_config = design_spec.deployment_config
            test_suite = {"unit_tests": ""}
            documentation = "Auto-generated agent based on design spec"
            impl = AgentImplementation(
                implementation_id=str(uuid.uuid4()),
                spec_id=design_spec.spec_id,
                python_code=python_code,
                configuration_files=config_files,
                docker_config=docker_config,
                test_suite=test_suite,
                documentation=documentation,
            )
            self._store_implementation(impl)
            self._active_implementations[impl.implementation_id] = impl
            return impl
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Develop agent error: {e}")
            return None

    def _generate_python_code(self, design_spec: AgentDesignSpec) -> str:
        # Template: subclass base class and implement process_task
        return f"""
from datetime import datetime, timezone
from typing import Dict, Any
from api.services.autonomy.autonomous_agent_base import AutonomousAgentBase

class GeneratedAgent(AutonomousAgentBase):
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics.tasks_completed += 1
        self.metrics.last_activity = datetime.now(timezone.utc)
        self.metrics.average_response_time = 0.2
        return {{"ok": True, "task": task}}
"""

    def _store_implementation(self, impl: AgentImplementation) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (i:AgentImplementation {implementation_id: $id})\n"
                    "SET i.spec_id=$spec_id, i.created_at=$created_at",
                    {
                        "id": impl.implementation_id,
                        "spec_id": impl.spec_id,
                        "created_at": impl.created_at.isoformat(),
                    },
                )
            ])
        finally:
            client.close()

    def _test_agent(self, implementation: AgentImplementation) -> Dict[str, Any]:
        # Placeholder: returns passed=True; extend with subprocess pytest if needed
        return {"passed": True}

    # ------------------------------- Deployment ----------------------------
    def _deploy_agent(self, implementation: AgentImplementation) -> Dict[str, Any]:
        try:
            if not self._docker_enabled or not self._docker_client:
                # Simulated deployment when Docker not available
                agent_id = str(uuid.uuid4())
                self._register_deployed_agent(agent_id, implementation, container_id=None)
                return {"success": True, "agent_id": agent_id, "container_id": None, "image_tag": None}

            with tempfile.TemporaryDirectory() as temp_dir:
                td = Path(temp_dir)
                (td / "agent.py").write_text(implementation.python_code)
                for name, content in implementation.configuration_files.items():
                    (td / name).write_text(content)
                (td / "Dockerfile").write_text(implementation.docker_config.get("dockerfile", ""))

                agent_id = str(uuid.uuid4())
                image_tag = f"agent_{agent_id}:latest"
                image, _ = self._docker_client.images.build(path=str(td), tag=image_tag, rm=True)
                container = self._docker_client.containers.run(
                    image_tag,
                    detach=True,
                    name=f"agent_{agent_id}",
                    environment=implementation.docker_config.get("environment", {}),
                    ports=implementation.docker_config.get("ports", {}),
                    volumes=implementation.docker_config.get("volumes", {}),
                    restart_policy={"Name": "unless-stopped"},
                )
                self._register_deployed_agent(agent_id, implementation, container_id=container.id)
                return {"success": True, "agent_id": agent_id, "container_id": container.id, "image_tag": image_tag}
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Deploy agent error: {e}")
            return {"success": False, "error": str(e)}

    def _register_deployed_agent(self, agent_id: str, implementation: AgentImplementation, container_id: Optional[str]) -> None:
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (a:DeployedAgent {agent_id: $agent_id})\n"
                    "SET a.implementation_id=$impl_id, a.deployed_at=$deployed_at, a.container_id=$container_id, a.status='active'",
                    {
                        "agent_id": agent_id,
                        "impl_id": implementation.implementation_id,
                        "deployed_at": datetime.now(timezone.utc).isoformat(),
                        "container_id": container_id,
                    },
                )
            ])
        finally:
            client.close()

    # ------------------------------- Retirement ----------------------------
    def retire_agent(self, agent_id: str) -> bool:
        """Gracefully retire an agent: update substrate, publish events, and remove from manager state."""
        # Update substrate
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:DeployedAgent {agent_id: $agent_id})\n"
                    "SET a.status='retired', a.retired_at=$ts",
                    {"agent_id": agent_id, "ts": datetime.now(timezone.utc).isoformat()},
                )
            ])
        finally:
            client.close()

        publish_exchange("agents.lifecycle", "lifecycle.agent.retiring", {"agent_id": agent_id, "ts": datetime.now(timezone.utc).isoformat()})
        publish_exchange("agents.lifecycle", "lifecycle.agent.retired", {"agent_id": agent_id, "ts": datetime.now(timezone.utc).isoformat()})
        # Remove from active map
        self._deployed_agents.pop(agent_id, None)
        return True

    def _retirement_assessment(self, system_analysis: Dict[str, Any]) -> Optional[str]:
        """If load is very low and multiple agents are active, retire the oldest one.
        Returns retired agent_id or None."""
        perf = system_analysis.get("performance", {})
        avg_load = perf.get("avg_system_load") or 0
        if float(avg_load) < 0.1 and len(self._deployed_agents) > 1:
            # Choose oldest by deployed_at
            def deployed_at_ts(meta):
                try:
                    return datetime.fromisoformat(meta.get("deployed_at").replace("Z", "+00:00"))
                except Exception:
                    return datetime.now(timezone.utc)

            oldest = sorted(self._deployed_agents.items(), key=lambda kv: deployed_at_ts(kv[1]))[0]
            agent_id = oldest[0]
            self.retire_agent(agent_id)
            return agent_id
        return None

