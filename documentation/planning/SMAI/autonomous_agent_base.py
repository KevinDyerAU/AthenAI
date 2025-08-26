"""
Enhanced AI Agent OS - Autonomous Agent Base Classes
Implements core self-managing agent capabilities with lifecycle management,
knowledge drift detection, and autonomous decision-making.

Author: Manus AI
Version: 1.0
Date: August 2025
License: MIT
"""

from __future__ import annotations
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Callable
import threading
import time
from contextlib import asynccontextmanager

import aiohttp
import pika
from neo4j import GraphDatabase
from openai import OpenAI


class AgentState(Enum):
    """Agent lifecycle states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RETIRING = "retiring"
    RETIRED = "retired"


class AgentCapability(Enum):
    """Agent capability types"""
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
    """Agent personality configuration"""
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
    """Agent performance and health metrics"""
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
    """Knowledge drift detection alert"""
    alert_id: str
    agent_id: str
    drift_type: str
    severity: str
    description: str
    affected_knowledge: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False


class AutonomousAgentBase(ABC):
    """
    Base class for autonomous agents with self-managing capabilities.
    
    Provides core functionality for:
    - Autonomous lifecycle management
    - Knowledge drift detection and prevention
    - Self-healing and adaptation
    - Performance monitoring and optimization
    - Inter-agent communication and coordination
    """
    
    def __init__(
        self,
        agent_id: str,
        personality: AgentPersonality,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        rabbitmq_url: str,
        openai_api_key: str,
        n8n_base_url: str = "http://localhost:5678",
        api_base_url: str = "http://localhost:8000"
    ):
        self.agent_id = agent_id
        self.personality = personality
        self.state = AgentState.INITIALIZING
        self.metrics = AgentMetrics(agent_id=agent_id)
        
        # Infrastructure connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        self.rabbitmq_connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_url)
        )
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.n8n_base_url = n8n_base_url
        self.api_base_url = api_base_url
        
        # Internal state
        self._running = False
        self._monitoring_thread = None
        self._knowledge_drift_detector = None
        self._self_healing_enabled = True
        self._learning_enabled = True
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize logging
        self.logger = logging.getLogger(f"agent.{self.agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize agent in consciousness substrate
        self._initialize_in_substrate()
        
    async def start(self) -> None:
        """Start the autonomous agent"""
        try:
            self.logger.info(f"Starting autonomous agent {self.agent_id}")
            self.state = AgentState.ACTIVE
            self._running = True
            
            # Start monitoring thread
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitoring_thread.start()
            
            # Initialize knowledge drift detection
            self._knowledge_drift_detector = KnowledgeDriftDetector(
                agent_id=self.agent_id,
                neo4j_driver=self.neo4j_driver,
                openai_client=self.openai_client
            )
            
            # Register with message queue
            self._setup_message_queue()
            
            # Perform agent-specific initialization
            await self._agent_specific_initialization()
            
            self.logger.info(f"Agent {self.agent_id} started successfully")
            await self._emit_event("agent_started", {"agent_id": self.agent_id})
            
        except Exception as e:
            self.logger.error(f"Failed to start agent {self.agent_id}: {e}")
            self.state = AgentState.FAILED
            raise
    
    async def stop(self) -> None:
        """Stop the autonomous agent gracefully"""
        try:
            self.logger.info(f"Stopping autonomous agent {self.agent_id}")
            self.state = AgentState.RETIRING
            self._running = False
            
            # Perform agent-specific cleanup
            await self._agent_specific_cleanup()
            
            # Close connections
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
            
            if self.neo4j_driver:
                self.neo4j_driver.close()
            
            self.state = AgentState.RETIRED
            self.logger.info(f"Agent {self.agent_id} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping agent {self.agent_id}: {e}")
            self.state = AgentState.FAILED
    
    @abstractmethod
    async def _agent_specific_initialization(self) -> None:
        """Agent-specific initialization logic"""
        pass
    
    @abstractmethod
    async def _agent_specific_cleanup(self) -> None:
        """Agent-specific cleanup logic"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        pass
    
    def _initialize_in_substrate(self) -> None:
        """Initialize agent record in consciousness substrate"""
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (a:Agent {id: $agent_id})
                SET a.name = $name,
                    a.role = $role,
                    a.capabilities = $capabilities,
                    a.state = $state,
                    a.created_at = datetime(),
                    a.last_updated = datetime(),
                    a.personality = $personality
                """,
                agent_id=self.agent_id,
                name=self.personality.name,
                role=self.personality.role,
                capabilities=[cap.value for cap in self.personality.capabilities],
                state=self.state.value,
                personality=json.dumps(self.personality.personality_traits)
            )
    
    def _setup_message_queue(self) -> None:
        """Setup RabbitMQ message handling"""
        # Declare agent-specific queue
        queue_name = f"agent_{self.agent_id}"
        self.rabbitmq_channel.queue_declare(queue=queue_name, durable=True)
        
        # Setup message consumer
        self.rabbitmq_channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._handle_message,
            auto_ack=False
        )
        
        # Start consuming in separate thread
        consumer_thread = threading.Thread(
            target=self.rabbitmq_channel.start_consuming,
            daemon=True
        )
        consumer_thread.start()
    
    def _handle_message(self, ch, method, properties, body) -> None:
        """Handle incoming messages"""
        try:
            message = json.loads(body.decode('utf-8'))
            asyncio.create_task(self._process_message(message))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming message"""
        message_type = message.get("type")
        
        if message_type == "task":
            await self._handle_task_message(message)
        elif message_type == "coordination":
            await self._handle_coordination_message(message)
        elif message_type == "health_check":
            await self._handle_health_check_message(message)
        elif message_type == "knowledge_update":
            await self._handle_knowledge_update_message(message)
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
    
    async def _handle_task_message(self, message: Dict[str, Any]) -> None:
        """Handle task assignment message"""
        try:
            self.state = AgentState.BUSY
            task_start_time = time.time()
            
            # Process the task
            result = await self.process_task(message.get("task", {}))
            
            # Update metrics
            task_duration = time.time() - task_start_time
            self.metrics.tasks_completed += 1
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.tasks_completed - 1) + task_duration) /
                self.metrics.tasks_completed
            )
            self.metrics.last_activity = datetime.now(timezone.utc)
            
            # Send result
            await self._send_task_result(message.get("task_id"), result)
            
            self.state = AgentState.ACTIVE
            
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            self.metrics.tasks_failed += 1
            self.state = AgentState.DEGRADED
            await self._trigger_self_healing()
    
    async def _handle_coordination_message(self, message: Dict[str, Any]) -> None:
        """Handle inter-agent coordination message"""
        coordination_type = message.get("coordination_type")
        
        if coordination_type == "collaboration_request":
            await self._handle_collaboration_request(message)
        elif coordination_type == "resource_sharing":
            await self._handle_resource_sharing(message)
        elif coordination_type == "knowledge_sharing":
            await self._handle_knowledge_sharing(message)
    
    async def _handle_health_check_message(self, message: Dict[str, Any]) -> None:
        """Handle health check request"""
        health_status = {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "average_response_time": self.metrics.average_response_time,
                "health_score": self.metrics.health_score,
                "last_activity": self.metrics.last_activity.isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send health status response
        await self._send_message(
            "health_response",
            health_status,
            routing_key=message.get("reply_to", "health_monitor")
        )
    
    async def _handle_knowledge_update_message(self, message: Dict[str, Any]) -> None:
        """Handle knowledge update notification"""
        if self._knowledge_drift_detector:
            await self._knowledge_drift_detector.check_for_drift(
                message.get("knowledge_id"),
                message.get("update_type")
            )
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop for autonomous operations"""
        while self._running:
            try:
                # Update health metrics
                self._update_health_metrics()
                
                # Check for knowledge drift
                if self._knowledge_drift_detector:
                    asyncio.create_task(self._knowledge_drift_detector.periodic_check())
                
                # Perform self-optimization
                if self._learning_enabled:
                    asyncio.create_task(self._perform_self_optimization())
                
                # Update consciousness substrate
                self._update_substrate_status()
                
                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _update_health_metrics(self) -> None:
        """Update agent health metrics"""
        # Calculate health score based on various factors
        success_rate = (
            self.metrics.tasks_completed / 
            max(1, self.metrics.tasks_completed + self.metrics.tasks_failed)
        )
        
        # Factor in response time (lower is better)
        response_time_score = max(0, 1 - (self.metrics.average_response_time / 10.0))
        
        # Factor in recent activity
        time_since_activity = (
            datetime.now(timezone.utc) - self.metrics.last_activity
        ).total_seconds()
        activity_score = max(0, 1 - (time_since_activity / 3600))  # 1 hour decay
        
        # Calculate overall health score
        self.metrics.health_score = (
            success_rate * 0.4 +
            response_time_score * 0.3 +
            activity_score * 0.3
        )
        
        # Update state based on health score
        if self.metrics.health_score < 0.3:
            self.state = AgentState.FAILED
        elif self.metrics.health_score < 0.6:
            self.state = AgentState.DEGRADED
        elif self.state in [AgentState.DEGRADED, AgentState.FAILED]:
            self.state = AgentState.ACTIVE
    
    async def _trigger_self_healing(self) -> None:
        """Trigger self-healing mechanisms"""
        if not self._self_healing_enabled:
            return
        
        self.logger.info(f"Triggering self-healing for agent {self.agent_id}")
        
        try:
            # Analyze the issue
            issue_analysis = await self._analyze_performance_issues()
            
            # Apply healing strategies
            for strategy in issue_analysis.get("healing_strategies", []):
                await self._apply_healing_strategy(strategy)
            
            # Notify monitoring system
            await self._emit_event("self_healing_triggered", {
                "agent_id": self.agent_id,
                "issue_analysis": issue_analysis
            })
            
        except Exception as e:
            self.logger.error(f"Error in self-healing: {e}")
    
    async def _analyze_performance_issues(self) -> Dict[str, Any]:
        """Analyze current performance issues"""
        issues = []
        healing_strategies = []
        
        # Check task failure rate
        if self.metrics.tasks_failed > 0:
            failure_rate = self.metrics.tasks_failed / (
                self.metrics.tasks_completed + self.metrics.tasks_failed
            )
            if failure_rate > 0.2:
                issues.append("high_failure_rate")
                healing_strategies.append("reduce_task_complexity")
        
        # Check response time
        if self.metrics.average_response_time > 5.0:
            issues.append("slow_response_time")
            healing_strategies.append("optimize_processing")
        
        # Check recent activity
        time_since_activity = (
            datetime.now(timezone.utc) - self.metrics.last_activity
        ).total_seconds()
        if time_since_activity > 1800:  # 30 minutes
            issues.append("low_activity")
            healing_strategies.append("request_more_tasks")
        
        return {
            "issues": issues,
            "healing_strategies": healing_strategies,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _apply_healing_strategy(self, strategy: str) -> None:
        """Apply a specific healing strategy"""
        if strategy == "reduce_task_complexity":
            # Request simpler tasks temporarily
            await self._request_simpler_tasks()
        elif strategy == "optimize_processing":
            # Optimize internal processing
            await self._optimize_processing()
        elif strategy == "request_more_tasks":
            # Request additional tasks
            await self._request_more_tasks()
    
    async def _perform_self_optimization(self) -> None:
        """Perform self-optimization based on performance data"""
        # Analyze performance patterns
        performance_analysis = await self._analyze_performance_patterns()
        
        # Apply optimizations
        for optimization in performance_analysis.get("optimizations", []):
            await self._apply_optimization(optimization)
    
    async def _send_message(
        self,
        message_type: str,
        content: Dict[str, Any],
        routing_key: str = "broadcast"
    ) -> None:
        """Send message via RabbitMQ"""
        message = {
            "type": message_type,
            "sender": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content
        }
        
        self.rabbitmq_channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent
        )
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to registered handlers"""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                self.logger.error(f"Error in event handler: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def _update_substrate_status(self) -> None:
        """Update agent status in consciousness substrate"""
        with self.neo4j_driver.session() as session:
            session.run("""
                MATCH (a:Agent {id: $agent_id})
                SET a.state = $state,
                    a.last_updated = datetime(),
                    a.health_score = $health_score,
                    a.tasks_completed = $tasks_completed,
                    a.tasks_failed = $tasks_failed,
                    a.average_response_time = $avg_response_time
                """,
                agent_id=self.agent_id,
                state=self.state.value,
                health_score=self.metrics.health_score,
                tasks_completed=self.metrics.tasks_completed,
                tasks_failed=self.metrics.tasks_failed,
                avg_response_time=self.metrics.average_response_time
            )


class KnowledgeDriftDetector:
    """Detects and prevents knowledge drift in the consciousness substrate"""
    
    def __init__(
        self,
        agent_id: str,
        neo4j_driver,
        openai_client: OpenAI,
        drift_threshold: float = 0.7
    ):
        self.agent_id = agent_id
        self.neo4j_driver = neo4j_driver
        self.openai_client = openai_client
        self.drift_threshold = drift_threshold
        self.logger = logging.getLogger(f"drift_detector.{agent_id}")
    
    async def check_for_drift(
        self,
        knowledge_id: str,
        update_type: str
    ) -> Optional[KnowledgeDriftAlert]:
        """Check for knowledge drift in a specific knowledge entity"""
        try:
            # Get knowledge entity and its history
            knowledge_data = self._get_knowledge_entity(knowledge_id)
            if not knowledge_data:
                return None
            
            # Analyze for drift patterns
            drift_analysis = await self._analyze_drift_patterns(
                knowledge_data, update_type
            )
            
            if drift_analysis["drift_detected"]:
                alert = KnowledgeDriftAlert(
                    alert_id=str(uuid.uuid4()),
                    agent_id=self.agent_id,
                    drift_type=drift_analysis["drift_type"],
                    severity=drift_analysis["severity"],
                    description=drift_analysis["description"],
                    affected_knowledge=[knowledge_id]
                )
                
                # Store alert in substrate
                self._store_drift_alert(alert)
                
                # Trigger remediation if severe
                if alert.severity in ["high", "critical"]:
                    await self._trigger_drift_remediation(alert)
                
                return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking for drift: {e}")
            return None
    
    async def periodic_check(self) -> List[KnowledgeDriftAlert]:
        """Perform periodic drift check across knowledge base"""
        alerts = []
        
        try:
            # Get recent knowledge updates
            recent_updates = self._get_recent_knowledge_updates()
            
            for update in recent_updates:
                alert = await self.check_for_drift(
                    update["knowledge_id"],
                    update["update_type"]
                )
                if alert:
                    alerts.append(alert)
            
            # Perform system-wide consistency check
            consistency_alerts = await self._check_system_consistency()
            alerts.extend(consistency_alerts)
            
        except Exception as e:
            self.logger.error(f"Error in periodic drift check: {e}")
        
        return alerts
    
    def _get_knowledge_entity(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Get knowledge entity from consciousness substrate"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (k:KnowledgeEntity {id: $knowledge_id})
                OPTIONAL MATCH (k)-[:HAS_VERSION]->(v:KnowledgeVersion)
                RETURN k, collect(v) as versions
                ORDER BY v.created_at DESC
                """,
                knowledge_id=knowledge_id
            )
            
            record = result.single()
            if record:
                return {
                    "entity": dict(record["k"]),
                    "versions": [dict(v) for v in record["versions"]]
                }
            return None
    
    async def _analyze_drift_patterns(
        self,
        knowledge_data: Dict[str, Any],
        update_type: str
    ) -> Dict[str, Any]:
        """Analyze knowledge data for drift patterns"""
        entity = knowledge_data["entity"]
        versions = knowledge_data["versions"]
        
        # Check for rapid changes
        if len(versions) > 5:  # More than 5 versions
            recent_versions = versions[:5]
            time_span = (
                datetime.fromisoformat(recent_versions[0]["created_at"]) -
                datetime.fromisoformat(recent_versions[-1]["created_at"])
            ).total_seconds()
            
            if time_span < 3600:  # Less than 1 hour
                return {
                    "drift_detected": True,
                    "drift_type": "rapid_changes",
                    "severity": "medium",
                    "description": "Rapid successive changes detected"
                }
        
        # Check for semantic drift using embeddings
        if len(versions) >= 2:
            semantic_drift = await self._check_semantic_drift(versions[:2])
            if semantic_drift["drift_detected"]:
                return semantic_drift
        
        # Check for conflict patterns
        conflict_analysis = self._check_conflict_patterns(entity, versions)
        if conflict_analysis["drift_detected"]:
            return conflict_analysis
        
        return {"drift_detected": False}
    
    async def _check_semantic_drift(
        self,
        versions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check for semantic drift between knowledge versions"""
        try:
            # Get embeddings for the two most recent versions
            current_content = versions[0].get("content", "")
            previous_content = versions[1].get("content", "")
            
            current_embedding = await self._get_embedding(current_content)
            previous_embedding = await self._get_embedding(previous_content)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(current_embedding, previous_embedding)
            
            if similarity < self.drift_threshold:
                severity = "high" if similarity < 0.5 else "medium"
                return {
                    "drift_detected": True,
                    "drift_type": "semantic_drift",
                    "severity": severity,
                    "description": f"Semantic similarity dropped to {similarity:.2f}",
                    "similarity_score": similarity
                }
            
        except Exception as e:
            self.logger.error(f"Error checking semantic drift: {e}")
        
        return {"drift_detected": False}
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
        
        return dot_product / (magnitude_a * magnitude_b)


# Additional implementation continues...
# This is the foundation for the autonomous agent system

