// Autonomous Agent Schema Extensions (idempotent)
// Nodes: Agent, AgentImplementation, AgentMetrics, KnowledgeDriftAlert, LifecycleEvent
// Relationships support lifecycle, metrics, and drift monitoring

// ========= Constraints =========
CREATE CONSTRAINT agent_id IF NOT EXISTS
FOR (n:Agent) REQUIRE n.agent_id IS UNIQUE;

CREATE CONSTRAINT agent_impl_id IF NOT EXISTS
FOR (n:AgentImplementation) REQUIRE n.impl_id IS UNIQUE;

CREATE CONSTRAINT agent_metrics_id IF NOT EXISTS
FOR (n:AgentMetrics) REQUIRE n.metric_id IS UNIQUE;

CREATE CONSTRAINT drift_alert_id IF NOT EXISTS
FOR (n:KnowledgeDriftAlert) REQUIRE n.alert_id IS UNIQUE;

CREATE CONSTRAINT lifecycle_event_id IF NOT EXISTS
FOR (n:LifecycleEvent) REQUIRE n.event_id IS UNIQUE;

// ========= Indexes =========
CREATE INDEX agent_state IF NOT EXISTS FOR (n:Agent) ON (n.state);
CREATE INDEX agent_health IF NOT EXISTS FOR (n:Agent) ON (n.health_score);
CREATE INDEX agent_updated_at IF NOT EXISTS FOR (n:Agent) ON (n.updated_at);

CREATE INDEX metrics_agent IF NOT EXISTS FOR (n:AgentMetrics) ON (n.agent_id);
CREATE INDEX metrics_timestamp IF NOT EXISTS FOR (n:AgentMetrics) ON (n.timestamp);

CREATE INDEX drift_timestamp IF NOT EXISTS FOR (n:KnowledgeDriftAlert) ON (n.timestamp);
CREATE INDEX drift_severity IF NOT EXISTS FOR (n:KnowledgeDriftAlert) ON (n.severity);

CREATE INDEX lifecycle_timestamp IF NOT EXISTS FOR (n:LifecycleEvent) ON (n.timestamp);
CREATE INDEX lifecycle_state IF NOT EXISTS FOR (n:LifecycleEvent) ON (n.state);

// ========= Type Hints =========
// :Agent { agent_id, name, type, version, state, health_score, created_at, updated_at, metadata }
// :AgentImplementation { impl_id, agent_id, language, entrypoint, config_path, version, created_at }
// :AgentMetrics { metric_id, agent_id, timestamp, cpu, mem, latency_ms, success_rate, throughput, metadata }
// :KnowledgeDriftAlert { alert_id, agent_id, timestamp, signal, severity, details }
// :LifecycleEvent { event_id, agent_id, timestamp, state, reason, metadata }

// ========= Relationship Hints =========
// (Agent)-[:USES_IMPLEMENTATION]->(AgentImplementation)
// (Agent)-[:HAS_METRIC]->(AgentMetrics)
// (Agent)-[:HAS_EVENT]->(LifecycleEvent)
// (Agent)-[:RAISED_DRIFT]->(KnowledgeDriftAlert)

// ========= Upsert Templates =========
// Agent upsert
// :param agent_id, :param name, :param type, :param version, :param state, :param health_score, :param metadata
MERGE (a:Agent {agent_id: $agent_id})
ON CREATE SET a.name=$name, a.type=$type, a.version=$version, a.state=coalesce($state,'inactive'), a.health_score=coalesce($health_score,1.0), a.created_at=datetime(), a.updated_at=datetime(), a.metadata=coalesce($metadata,{})
ON MATCH SET a.name=$name, a.type=$type, a.version=$version, a.state=coalesce($state,a.state), a.health_score=coalesce($health_score,a.health_score), a.updated_at=datetime(), a.metadata=coalesce($metadata,a.metadata);

// Attach implementation
// :param impl_id, :param language, :param entrypoint, :param config_path, :param version
MATCH (a:Agent {agent_id: $agent_id})
MERGE (i:AgentImplementation {impl_id: $impl_id})
ON CREATE SET i.agent_id=$agent_id, i.language=$language, i.entrypoint=$entrypoint, i.config_path=$config_path, i.version=$version, i.created_at=datetime()
MERGE (a)-[:USES_IMPLEMENTATION]->(i);

// Add metrics
// :param metric_id, :param timestamp, :param cpu, :param mem, :param latency_ms, :param success_rate, :param throughput, :param metadata
MATCH (a:Agent {agent_id: $agent_id})
MERGE (m:AgentMetrics {metric_id: $metric_id})
ON CREATE SET m.agent_id=$agent_id, m.timestamp=$timestamp, m.cpu=$cpu, m.mem=$mem, m.latency_ms=$latency_ms, m.success_rate=$success_rate, m.throughput=$throughput, m.metadata=coalesce($metadata,{})
MERGE (a)-[:HAS_METRIC]->(m);

// Add lifecycle event
// :param event_id, :param timestamp, :param state, :param reason, :param metadata
MATCH (a:Agent {agent_id: $agent_id})
MERGE (e:LifecycleEvent {event_id: $event_id})
ON CREATE SET e.agent_id=$agent_id, e.timestamp=$timestamp, e.state=$state, e.reason=$reason, e.metadata=coalesce($metadata,{})
MERGE (a)-[:HAS_EVENT]->(e);

// Add drift alert
// :param alert_id, :param timestamp, :param signal, :param severity, :param details
MATCH (a:Agent {agent_id: $agent_id})
MERGE (d:KnowledgeDriftAlert {alert_id: $alert_id})
ON CREATE SET d.agent_id=$agent_id, d.timestamp=$timestamp, d.signal=$signal, d.severity=$severity, d.details=$details
MERGE (a)-[:RAISED_DRIFT]->(d);
