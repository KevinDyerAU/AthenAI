"""
Enhanced AI Agent OS - Agent Lifecycle Management System
Implements autonomous agent lifecycle management with dynamic creation,
deployment, monitoring, and retirement capabilities.

Author: Manus AI
Version: 1.0
Date: August 2025
License: MIT
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import docker
import subprocess
import tempfile
import os
from pathlib import Path

import aiohttp
from neo4j import GraphDatabase
from openai import OpenAI
import pika

from autonomous_agent_base import (
    AgentState, AgentCapability, AgentPersonality, AgentMetrics,
    AutonomousAgentBase
)


class LifecyclePhase(Enum):
    """Agent lifecycle phases"""
    CONCEPTION = "conception"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    OPERATION = "operation"
    RETIREMENT = "retirement"


class AgentNeed(Enum):
    """Types of agent needs that trigger creation"""
    CAPABILITY_GAP = "capability_gap"
    PERFORMANCE_BOTTLENECK = "performance_bottleneck"
    WORKLOAD_INCREASE = "workload_increase"
    SPECIALIZATION_REQUIRED = "specialization_required"
    REDUNDANCY_NEEDED = "redundancy_needed"
    INNOVATION_OPPORTUNITY = "innovation_opportunity"


@dataclass
class AgentCreationRequest:
    """Request for creating a new agent"""
    request_id: str
    need_type: AgentNeed
    required_capabilities: Set[AgentCapability]
    performance_requirements: Dict[str, Any]
    integration_requirements: List[str]
    priority: int = 5  # 1-10 scale
    deadline: Optional[datetime] = None
    justification: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentDesignSpec:
    """Comprehensive agent design specification"""
    spec_id: str
    request_id: str
    personality: AgentPersonality
    technical_requirements: Dict[str, Any]
    integration_patterns: List[Dict[str, Any]]
    performance_targets: Dict[str, float]
    testing_criteria: List[Dict[str, Any]]
    deployment_config: Dict[str, Any]
    estimated_development_time: int  # hours
    resource_requirements: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentImplementation:
    """Agent implementation artifacts"""
    implementation_id: str
    spec_id: str
    python_code: str
    n8n_workflows: List[Dict[str, Any]]
    configuration_files: Dict[str, str]
    docker_config: Dict[str, Any]
    test_suite: Dict[str, Any]
    documentation: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AgentLifecycleManager:
    """
    Manages the complete lifecycle of autonomous agents from conception to retirement.
    
    Provides capabilities for:
    - Autonomous need assessment and agent creation
    - Intelligent agent design generation
    - Automated code generation and testing
    - Dynamic deployment and scaling
    - Continuous monitoring and optimization
    - Graceful retirement and resource cleanup
    """
    
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        rabbitmq_url: str,
        openai_api_key: str,
        docker_client: docker.DockerClient,
        n8n_base_url: str = "http://localhost:5678",
        api_base_url: str = "http://localhost:8000"
    ):
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        self.rabbitmq_connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.docker_client = docker_client
        self.n8n_base_url = n8n_base_url
        self.api_base_url = api_base_url
        
        # Internal state
        self._running = False
        self._active_requests: Dict[str, AgentCreationRequest] = {}
        self._active_implementations: Dict[str, AgentImplementation] = {}
        self._deployed_agents: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_concurrent_developments = 3
        self.max_agents_per_capability = 5
        self.performance_monitoring_interval = 300  # 5 minutes
        self.need_assessment_interval = 900  # 15 minutes
        
        # Initialize logging
        self.logger = logging.getLogger("agent_lifecycle_manager")
        self.logger.setLevel(logging.INFO)
        
        # Initialize substrate schema
        self._initialize_substrate_schema()
    
    async def start(self) -> None:
        """Start the lifecycle management system"""
        try:
            self.logger.info("Starting Agent Lifecycle Manager")
            self._running = True
            
            # Start background tasks
            asyncio.create_task(self._need_assessment_loop())
            asyncio.create_task(self._development_management_loop())
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._retirement_assessment_loop())
            
            self.logger.info("Agent Lifecycle Manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start Agent Lifecycle Manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the lifecycle management system"""
        try:
            self.logger.info("Stopping Agent Lifecycle Manager")
            self._running = False
            
            # Gracefully stop all managed agents
            for agent_id in list(self._deployed_agents.keys()):
                await self._graceful_agent_shutdown(agent_id)
            
            # Close connections
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
            
            if self.neo4j_driver:
                self.neo4j_driver.close()
            
            self.logger.info("Agent Lifecycle Manager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping Agent Lifecycle Manager: {e}")
    
    async def _need_assessment_loop(self) -> None:
        """Continuously assess system needs for new agents"""
        while self._running:
            try:
                # Analyze current system state
                system_analysis = await self._analyze_system_state()
                
                # Identify needs for new agents
                identified_needs = await self._identify_agent_needs(system_analysis)
                
                # Create requests for high-priority needs
                for need in identified_needs:
                    if need["priority"] >= 7:  # High priority threshold
                        await self._create_agent_request(need)
                
                # Wait before next assessment
                await asyncio.sleep(self.need_assessment_interval)
                
            except Exception as e:
                self.logger.error(f"Error in need assessment loop: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_system_state(self) -> Dict[str, Any]:
        """Analyze current system state and performance"""
        with self.neo4j_driver.session() as session:
            # Get agent statistics
            agent_stats = session.run("""
                MATCH (a:Agent)
                RETURN 
                    count(a) as total_agents,
                    collect(a.capabilities) as all_capabilities,
                    collect(a.state) as agent_states,
                    collect(a.health_score) as health_scores,
                    collect(a.tasks_completed) as task_counts,
                    collect(a.average_response_time) as response_times
            """).single()
            
            # Get task queue statistics
            task_stats = session.run("""
                MATCH (t:Task)
                WHERE t.status IN ['pending', 'in_progress']
                RETURN 
                    count(t) as pending_tasks,
                    collect(t.required_capabilities) as required_caps,
                    collect(t.priority) as task_priorities,
                    collect(t.created_at) as creation_times
            """).single()
            
            # Get performance metrics
            performance_stats = session.run("""
                MATCH (m:PerformanceMetric)
                WHERE m.timestamp > datetime() - duration('PT1H')
                RETURN 
                    avg(m.system_load) as avg_system_load,
                    avg(m.response_time) as avg_response_time,
                    avg(m.throughput) as avg_throughput,
                    count(m) as metric_count
            """).single()
        
        return {
            "agents": dict(agent_stats) if agent_stats else {},
            "tasks": dict(task_stats) if task_stats else {},
            "performance": dict(performance_stats) if performance_stats else {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _identify_agent_needs(
        self,
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify needs for new agents based on system analysis"""
        needs = []
        
        # Check for capability gaps
        capability_gaps = await self._identify_capability_gaps(system_analysis)
        needs.extend(capability_gaps)
        
        # Check for performance bottlenecks
        performance_bottlenecks = await self._identify_performance_bottlenecks(system_analysis)
        needs.extend(performance_bottlenecks)
        
        # Check for workload increases
        workload_increases = await self._identify_workload_increases(system_analysis)
        needs.extend(workload_increases)
        
        # Check for specialization opportunities
        specialization_needs = await self._identify_specialization_needs(system_analysis)
        needs.extend(specialization_needs)
        
        return needs
    
    async def _identify_capability_gaps(
        self,
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify capability gaps in the current agent ecosystem"""
        gaps = []
        
        # Get all required capabilities from pending tasks
        task_data = system_analysis.get("tasks", {})
        required_caps = task_data.get("required_caps", [])
        
        # Get all available capabilities from active agents
        agent_data = system_analysis.get("agents", {})
        available_caps = agent_data.get("all_capabilities", [])
        
        # Flatten and analyze capabilities
        all_required = set()
        for cap_list in required_caps:
            if isinstance(cap_list, list):
                all_required.update(cap_list)
        
        all_available = set()
        for cap_list in available_caps:
            if isinstance(cap_list, list):
                all_available.update(cap_list)
        
        # Identify missing capabilities
        missing_caps = all_required - all_available
        
        for cap in missing_caps:
            gaps.append({
                "type": AgentNeed.CAPABILITY_GAP,
                "capability": cap,
                "priority": 8,
                "justification": f"No agents available with {cap} capability",
                "required_capabilities": {AgentCapability(cap)} if cap in [c.value for c in AgentCapability] else set()
            })
        
        return gaps
    
    async def _identify_performance_bottlenecks(
        self,
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks requiring additional agents"""
        bottlenecks = []
        
        performance_data = system_analysis.get("performance", {})
        avg_response_time = performance_data.get("avg_response_time", 0)
        avg_system_load = performance_data.get("avg_system_load", 0)
        
        # Check if response times are too high
        if avg_response_time > 5.0:  # 5 seconds threshold
            bottlenecks.append({
                "type": AgentNeed.PERFORMANCE_BOTTLENECK,
                "metric": "response_time",
                "current_value": avg_response_time,
                "threshold": 5.0,
                "priority": 7,
                "justification": f"Average response time ({avg_response_time:.2f}s) exceeds threshold",
                "required_capabilities": {AgentCapability.EXECUTION}
            })
        
        # Check if system load is too high
        if avg_system_load > 0.8:  # 80% threshold
            bottlenecks.append({
                "type": AgentNeed.PERFORMANCE_BOTTLENECK,
                "metric": "system_load",
                "current_value": avg_system_load,
                "threshold": 0.8,
                "priority": 8,
                "justification": f"System load ({avg_system_load:.2f}) exceeds threshold",
                "required_capabilities": {AgentCapability.EXECUTION}
            })
        
        return bottlenecks
    
    async def _create_agent_request(self, need: Dict[str, Any]) -> str:
        """Create an agent creation request based on identified need"""
        request_id = str(uuid.uuid4())
        
        creation_request = AgentCreationRequest(
            request_id=request_id,
            need_type=need["type"],
            required_capabilities=need.get("required_capabilities", set()),
            performance_requirements=need.get("performance_requirements", {}),
            integration_requirements=need.get("integration_requirements", []),
            priority=need.get("priority", 5),
            justification=need.get("justification", "")
        )
        
        # Store request
        self._active_requests[request_id] = creation_request
        
        # Store in substrate
        await self._store_creation_request(creation_request)
        
        # Trigger design phase
        asyncio.create_task(self._process_creation_request(request_id))
        
        self.logger.info(f"Created agent creation request {request_id} for {need['type']}")
        return request_id
    
    async def _process_creation_request(self, request_id: str) -> None:
        """Process an agent creation request through all lifecycle phases"""
        try:
            request = self._active_requests.get(request_id)
            if not request:
                self.logger.error(f"Request {request_id} not found")
                return
            
            # Design phase
            self.logger.info(f"Starting design phase for request {request_id}")
            design_spec = await self._generate_agent_design(request)
            
            if not design_spec:
                self.logger.error(f"Failed to generate design for request {request_id}")
                return
            
            # Development phase
            self.logger.info(f"Starting development phase for spec {design_spec.spec_id}")
            implementation = await self._develop_agent(design_spec)
            
            if not implementation:
                self.logger.error(f"Failed to develop agent for spec {design_spec.spec_id}")
                return
            
            # Testing phase
            self.logger.info(f"Starting testing phase for implementation {implementation.implementation_id}")
            test_results = await self._test_agent(implementation)
            
            if not test_results.get("passed", False):
                self.logger.error(f"Agent testing failed for implementation {implementation.implementation_id}")
                return
            
            # Deployment phase
            self.logger.info(f"Starting deployment phase for implementation {implementation.implementation_id}")
            deployment_result = await self._deploy_agent(implementation)
            
            if deployment_result.get("success", False):
                agent_id = deployment_result["agent_id"]
                self._deployed_agents[agent_id] = {
                    "request_id": request_id,
                    "spec_id": design_spec.spec_id,
                    "implementation_id": implementation.implementation_id,
                    "deployed_at": datetime.now(timezone.utc),
                    "container_id": deployment_result.get("container_id"),
                    "status": "active"
                }
                
                self.logger.info(f"Successfully deployed agent {agent_id}")
                
                # Clean up request
                del self._active_requests[request_id]
            else:
                self.logger.error(f"Failed to deploy agent for implementation {implementation.implementation_id}")
        
        except Exception as e:
            self.logger.error(f"Error processing creation request {request_id}: {e}")
    
    async def _generate_agent_design(
        self,
        request: AgentCreationRequest
    ) -> Optional[AgentDesignSpec]:
        """Generate comprehensive agent design specification"""
        try:
            # Analyze requirements
            requirements_analysis = await self._analyze_requirements(request)
            
            # Generate personality
            personality = await self._generate_agent_personality(
                request.required_capabilities,
                requirements_analysis
            )
            
            # Generate technical requirements
            technical_requirements = await self._generate_technical_requirements(
                request, requirements_analysis
            )
            
            # Generate integration patterns
            integration_patterns = await self._generate_integration_patterns(
                request.integration_requirements
            )
            
            # Generate performance targets
            performance_targets = await self._generate_performance_targets(
                request.performance_requirements
            )
            
            # Generate testing criteria
            testing_criteria = await self._generate_testing_criteria(
                personality, technical_requirements
            )
            
            # Generate deployment configuration
            deployment_config = await self._generate_deployment_config(
                technical_requirements, integration_patterns
            )
            
            # Estimate development time
            estimated_time = await self._estimate_development_time(
                technical_requirements, integration_patterns
            )
            
            # Calculate resource requirements
            resource_requirements = await self._calculate_resource_requirements(
                technical_requirements, performance_targets
            )
            
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
                resource_requirements=resource_requirements
            )
            
            # Store design spec
            await self._store_design_spec(spec)
            
            return spec
            
        except Exception as e:
            self.logger.error(f"Error generating agent design: {e}")
            return None
    
    async def _generate_agent_personality(
        self,
        required_capabilities: Set[AgentCapability],
        requirements_analysis: Dict[str, Any]
    ) -> AgentPersonality:
        """Generate agent personality based on requirements"""
        
        # Use OpenAI to generate personality traits
        prompt = f"""
        Generate a comprehensive agent personality for an AI agent with the following capabilities:
        {[cap.value for cap in required_capabilities]}
        
        Requirements analysis: {json.dumps(requirements_analysis, indent=2)}
        
        Please provide:
        1. A suitable name for the agent
        2. A clear role description
        3. Personality traits that align with the capabilities
        4. Decision-making style
        5. Communication style
        6. Risk tolerance (0.0-1.0)
        7. Learning rate (0.0-1.0)
        8. Collaboration preference (0.0-1.0)
        9. Autonomy level (0.0-1.0)
        
        Return as JSON format.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        personality_data = json.loads(response.choices[0].message.content)
        
        return AgentPersonality(
            name=personality_data.get("name", "Generated Agent"),
            role=personality_data.get("role", "Specialized Agent"),
            capabilities=required_capabilities,
            personality_traits=personality_data.get("personality_traits", {}),
            decision_making_style=personality_data.get("decision_making_style", "analytical"),
            communication_style=personality_data.get("communication_style", "professional"),
            risk_tolerance=personality_data.get("risk_tolerance", 0.5),
            learning_rate=personality_data.get("learning_rate", 0.1),
            collaboration_preference=personality_data.get("collaboration_preference", 0.7),
            autonomy_level=personality_data.get("autonomy_level", 0.8)
        )
    
    async def _develop_agent(
        self,
        design_spec: AgentDesignSpec
    ) -> Optional[AgentImplementation]:
        """Develop agent implementation from design specification"""
        try:
            # Generate Python code
            python_code = await self._generate_python_code(design_spec)
            
            # Generate n8n workflows
            n8n_workflows = await self._generate_n8n_workflows(design_spec)
            
            # Generate configuration files
            config_files = await self._generate_configuration_files(design_spec)
            
            # Generate Docker configuration
            docker_config = await self._generate_docker_config(design_spec)
            
            # Generate test suite
            test_suite = await self._generate_test_suite(design_spec)
            
            # Generate documentation
            documentation = await self._generate_documentation(design_spec)
            
            implementation = AgentImplementation(
                implementation_id=str(uuid.uuid4()),
                spec_id=design_spec.spec_id,
                python_code=python_code,
                n8n_workflows=n8n_workflows,
                configuration_files=config_files,
                docker_config=docker_config,
                test_suite=test_suite,
                documentation=documentation
            )
            
            # Store implementation
            await self._store_implementation(implementation)
            self._active_implementations[implementation.implementation_id] = implementation
            
            return implementation
            
        except Exception as e:
            self.logger.error(f"Error developing agent: {e}")
            return None
    
    async def _generate_python_code(self, design_spec: AgentDesignSpec) -> str:
        """Generate Python code for the agent"""
        prompt = f"""
        Generate complete Python code for an autonomous agent with the following specification:
        
        Personality: {design_spec.personality.__dict__}
        Technical Requirements: {json.dumps(design_spec.technical_requirements, indent=2)}
        Integration Patterns: {json.dumps(design_spec.integration_patterns, indent=2)}
        Performance Targets: {json.dumps(design_spec.performance_targets, indent=2)}
        
        The agent should inherit from AutonomousAgentBase and implement all required methods.
        Include proper error handling, logging, and performance monitoring.
        
        Return only the Python code without any markdown formatting.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    async def _test_agent(
        self,
        implementation: AgentImplementation
    ) -> Dict[str, Any]:
        """Test agent implementation"""
        try:
            # Create temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write implementation files
                code_file = Path(temp_dir) / "agent.py"
                code_file.write_text(implementation.python_code)
                
                # Write test files
                test_file = Path(temp_dir) / "test_agent.py"
                test_file.write_text(implementation.test_suite.get("unit_tests", ""))
                
                # Run tests
                test_result = subprocess.run(
                    ["python", "-m", "pytest", str(test_file), "-v"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                # Analyze results
                passed = test_result.returncode == 0
                
                return {
                    "passed": passed,
                    "output": test_result.stdout,
                    "errors": test_result.stderr,
                    "return_code": test_result.returncode
                }
        
        except Exception as e:
            self.logger.error(f"Error testing agent: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _deploy_agent(
        self,
        implementation: AgentImplementation
    ) -> Dict[str, Any]:
        """Deploy agent to production environment"""
        try:
            # Create deployment directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write all implementation files
                code_file = Path(temp_dir) / "agent.py"
                code_file.write_text(implementation.python_code)
                
                # Write configuration files
                for filename, content in implementation.configuration_files.items():
                    config_file = Path(temp_dir) / filename
                    config_file.write_text(content)
                
                # Write Dockerfile
                dockerfile = Path(temp_dir) / "Dockerfile"
                dockerfile.write_text(implementation.docker_config.get("dockerfile", ""))
                
                # Build Docker image
                agent_id = str(uuid.uuid4())
                image_tag = f"agent_{agent_id}:latest"
                
                image, build_logs = self.docker_client.images.build(
                    path=temp_dir,
                    tag=image_tag,
                    rm=True
                )
                
                # Run container
                container = self.docker_client.containers.run(
                    image_tag,
                    detach=True,
                    name=f"agent_{agent_id}",
                    environment=implementation.docker_config.get("environment", {}),
                    ports=implementation.docker_config.get("ports", {}),
                    volumes=implementation.docker_config.get("volumes", {}),
                    restart_policy={"Name": "unless-stopped"}
                )
                
                # Register agent in substrate
                await self._register_deployed_agent(agent_id, implementation, container.id)
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "container_id": container.id,
                    "image_tag": image_tag
                }
        
        except Exception as e:
            self.logger.error(f"Error deploying agent: {e}")
            return {"success": False, "error": str(e)}
    
    # Additional methods for monitoring, retirement, etc. would continue here...
    # This provides the core lifecycle management functionality

