# NeoV3 Enhanced AI Agent Operating System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j 5.x](https://img.shields.io/badge/Neo4j-5.x-green.svg)](https://neo4j.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)

> **A revolutionary AI agent operating system that orchestrates specialized AI agents through a shared consciousness substrate, enabling autonomous collaboration, knowledge synthesis, and complex task execution.**

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Agent Ecosystem](#agent-ecosystem)
- [Consciousness Substrate](#consciousness-substrate)
- [Installation & Deployment](#installation--deployment)
- [API Documentation](#api-documentation)
- [Workflow Management](#workflow-management)
- [Monitoring & Observability](#monitoring--observability)
- [Development Guide](#development-guide)
- [Knowledge Templates](#knowledge-templates)
- [Contributing](#contributing)

## Overview

NeoV3 represents the next evolution in AI agent orchestration, implementing a sophisticated operating system where specialized AI agents collaborate through a shared consciousness substrate. Unlike traditional AI systems that operate in isolation, NeoV3 creates a living ecosystem where agents can share knowledge, delegate tasks, and collectively solve complex problems that exceed the capabilities of any individual agent.

The system is built on the principle of **distributed intelligence**, where each agent maintains its specialized expertise while contributing to and benefiting from a collective knowledge base. This approach enables emergent behaviors and solutions that arise from agent collaboration, making the whole system significantly more capable than the sum of its parts.

### Key Capabilities

**Autonomous Agent Orchestration**: The system manages multiple specialized AI agents, each with distinct personalities, capabilities, and areas of expertise. Agents can be dynamically created, configured, and deployed based on workload requirements and task complexity.

**Shared Consciousness Substrate**: A Neo4j-based knowledge graph serves as the central nervous system, storing not just data but the relationships, context, and reasoning patterns that emerge from agent interactions. This substrate enables sophisticated knowledge discovery and cross-pollination of ideas between agents.

**Real-time Collaboration**: Through WebSocket connections and RabbitMQ message queuing, agents can communicate in real-time, share intermediate results, and coordinate complex multi-step workflows without human intervention.

**Adaptive Learning**: The system continuously learns from agent interactions, user feedback, and task outcomes, refining its approaches and expanding its knowledge base through reinforcement learning and human feedback loops.

**Enterprise Integration**: Built with enterprise requirements in mind, including comprehensive monitoring, audit trails, security controls, and scalable deployment options for both cloud and on-premises environments.

## System Architecture

The NeoV3 architecture implements a layered approach that separates concerns while enabling seamless integration between components. The system is designed for high availability, scalability, and maintainability.

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Professional Chat Interface]
        API[REST API Gateway]
        WS[WebSocket Server]
        DOC[API Documentation]
    end
    
    subgraph "Agent Orchestration Layer"
        COORD[Main Coordinator Agent]
        RESEARCH[Research Agent]
        ANALYSIS[Analysis Agent]
        CREATIVE[Creative Agent]
        TECHNICAL[Technical Agent]
        PM[Project Manager Agent]
        TRIAGE[Triage Agent]
        MAINT[Maintenance Agent]
    end
    
    subgraph "Workflow Management"
        N8N[n8n Workflow Engine]
        THINK[Think Tool Integration]
        QUEUE[RabbitMQ Message Queue]
        SCHED[Task Scheduler]
    end
    
    subgraph "Consciousness Substrate"
        NEO4J[(Neo4j Knowledge Graph)]
        VECTOR[Vector Embeddings]
        SEARCH[Semantic Search]
        REASON[Graph Reasoning]
    end
    
    subgraph "Data Processing"
        UNSTRUCT[Unstructured.io Document Processing]
        UPLOAD[File Upload System]
        DOWNLOAD[Download Manager]
        VALIDATE[Content Validation]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER[Docker Containers]
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        MONITOR[Monitoring Stack]
    end
    
    subgraph "Observability"
        PROM[Prometheus Metrics]
        GRAF[Grafana Dashboards]
        LOKI[Loki Logging]
        ALERT[Alertmanager]
    end
    
    UI --> API
    UI --> WS
    API --> COORD
    WS --> COORD
    
    COORD --> RESEARCH
    COORD --> ANALYSIS
    COORD --> CREATIVE
    COORD --> TECHNICAL
    COORD --> PM
    
    PM --> TRIAGE
    PM --> MAINT
    
    RESEARCH --> N8N
    ANALYSIS --> N8N
    CREATIVE --> N8N
    TECHNICAL --> N8N
    
    N8N --> THINK
    N8N --> QUEUE
    N8N --> SCHED
    
    COORD --> NEO4J
    RESEARCH --> NEO4J
    ANALYSIS --> NEO4J
    CREATIVE --> NEO4J
    TECHNICAL --> NEO4J
    
    NEO4J --> VECTOR
    NEO4J --> SEARCH
    NEO4J --> REASON
    
    API --> UNSTRUCT
    UNSTRUCT --> UPLOAD
    UNSTRUCT --> DOWNLOAD
    UNSTRUCT --> VALIDATE
    
    DOCKER --> POSTGRES
    DOCKER --> REDIS
    DOCKER --> MONITOR
    
    MONITOR --> PROM
    MONITOR --> GRAF
    MONITOR --> LOKI
    MONITOR --> ALERT
    
    PROM --> GRAF
    LOKI --> GRAF
    ALERT --> GRAF
```

### Architectural Principles

**Microservices Architecture**: Each major component runs as an independent service, enabling independent scaling, deployment, and maintenance. Services communicate through well-defined APIs and message queues.

**Event-Driven Communication**: The system uses event-driven patterns for loose coupling between components. Agents publish events to message queues, and interested parties subscribe to relevant event types.

**Stateless Design**: Core services are designed to be stateless, with all persistent state stored in dedicated databases. This enables horizontal scaling and simplifies deployment management.

**Fault Tolerance**: The system implements circuit breakers, retry mechanisms, and graceful degradation to handle component failures without cascading system-wide outages.

**Security by Design**: Authentication, authorization, and audit logging are built into every layer of the system, with role-based access controls and comprehensive security monitoring.

## Core Components

### API Gateway and Service Layer

The API gateway serves as the primary entry point for all external interactions with the NeoV3 system. Built using Flask-RESTX, it provides comprehensive REST endpoints with automatic OpenAPI documentation generation.

**Authentication and Authorization**: The system implements JWT-based authentication with role-based access controls. Users can be assigned different permission levels, from read-only access to full administrative privileges.

**Request Routing**: The gateway intelligently routes requests to appropriate backend services, handling load balancing, circuit breaking, and retry logic automatically.

**Rate Limiting**: Built-in rate limiting prevents abuse and ensures fair resource allocation across users and applications.

**Audit Logging**: Every API request is logged with comprehensive metadata, enabling detailed security audits and usage analytics.

### WebSocket Communication Layer

Real-time communication is handled through a sophisticated WebSocket implementation that enables bidirectional communication between the user interface and the agent ecosystem.

**Room-based Communication**: WebSocket connections are organized into rooms, typically corresponding to conversation contexts or project workspaces. This enables targeted message delivery and context preservation.

**Agent Status Broadcasting**: Real-time updates about agent status, task progress, and system health are broadcast to connected clients, providing immediate feedback on system operations.

**Message Queuing Integration**: WebSocket messages are integrated with the RabbitMQ message queuing system, ensuring reliable delivery and enabling complex routing patterns.

### Document Processing Pipeline

The document processing pipeline leverages Unstructured.io to handle a wide variety of document formats, extracting structured information and making it available to the agent ecosystem.

**Multi-format Support**: The system can process PDFs, Word documents, PowerPoint presentations, HTML files, images, and many other formats, extracting text, metadata, and structural information.

**Intelligent Chunking**: Large documents are intelligently chunked to optimize processing and storage while preserving semantic coherence.

**Vector Embedding Generation**: Processed content is automatically converted to vector embeddings using OpenAI's embedding models, enabling semantic search and similarity matching.

**Knowledge Graph Integration**: Extracted information is automatically integrated into the Neo4j knowledge graph, creating relationships and enabling graph-based reasoning.

## Agent Ecosystem

The NeoV3 agent ecosystem consists of specialized AI agents, each designed for specific types of tasks and equipped with unique capabilities and personalities.

```mermaid
graph LR
    subgraph "Core Coordination"
        MAIN[Main Coordinator<br/>🎯<br/>General coordination<br/>Task delegation<br/>Response synthesis]
    end
    
    subgraph "Specialized Agents"
        RESEARCH[Research Agent<br/>🔍<br/>Information gathering<br/>Data analysis<br/>Fact verification]
        
        ANALYSIS[Analysis Agent<br/>📊<br/>Data processing<br/>Statistical analysis<br/>Pattern recognition]
        
        CREATIVE[Creative Agent<br/>🎨<br/>Content creation<br/>Ideation<br/>Design thinking]
        
        TECHNICAL[Technical Agent<br/>⚙️<br/>Code generation<br/>System architecture<br/>Technical solutions]
    end
    
    subgraph "Management Layer"
        PM[Project Manager<br/>📋<br/>Task decomposition<br/>Resource allocation<br/>Timeline management]
        
        TRIAGE[Triage Agent<br/>🚨<br/>Issue prioritization<br/>Emergency response<br/>Resource routing]
        
        MAINT[Maintenance Agent<br/>🔧<br/>System health<br/>Performance optimization<br/>Preventive maintenance]
    end
    
    MAIN --> RESEARCH
    MAIN --> ANALYSIS
    MAIN --> CREATIVE
    MAIN --> TECHNICAL
    
    PM --> MAIN
    PM --> TRIAGE
    PM --> MAINT
    
    RESEARCH -.-> ANALYSIS
    ANALYSIS -.-> CREATIVE
    CREATIVE -.-> TECHNICAL
    TECHNICAL -.-> RESEARCH
```

### Agent Specializations

**Main Coordinator Agent**: Serves as the primary interface between users and the agent ecosystem. It understands user intent, delegates tasks to appropriate specialized agents, and synthesizes responses from multiple agents into coherent outputs. The coordinator maintains conversation context and ensures that user requests are handled efficiently.

**Research Agent**: Specializes in information gathering, web research, and fact verification. It can access external APIs, search databases, and cross-reference information from multiple sources. The research agent is particularly skilled at finding relevant information quickly and assessing source credibility.

**Analysis Agent**: Focuses on data processing, statistical analysis, and pattern recognition. It can work with structured and unstructured data, perform complex calculations, and generate insights from large datasets. The analysis agent excels at identifying trends, correlations, and anomalies in data.

**Creative Agent**: Handles content creation, ideation, and design thinking tasks. It can generate written content, brainstorm ideas, create visual concepts, and approach problems from innovative angles. The creative agent brings artistic and imaginative capabilities to the system.

**Technical Agent**: Specializes in code generation, system architecture, and technical problem-solving. It can write code in multiple programming languages, design system architectures, and provide technical solutions to complex problems. The technical agent stays current with best practices and emerging technologies.

**Project Manager Agent**: Orchestrates complex multi-step projects by breaking them down into manageable tasks, allocating resources, and managing timelines. It coordinates between other agents and ensures that projects stay on track and meet their objectives.

**Triage Agent**: Handles issue prioritization, emergency response, and resource routing. It can quickly assess the severity of problems, escalate critical issues, and ensure that urgent matters receive immediate attention.

**Maintenance Agent**: Monitors system health, performs preventive maintenance, and optimizes performance. It proactively identifies potential issues and takes corrective action to maintain system reliability and efficiency.

### Agent Communication Patterns

Agents communicate through several mechanisms, each optimized for different types of interactions:

**Direct Messaging**: For immediate, synchronous communication between agents working on the same task.

**Event Broadcasting**: For notifying multiple agents about state changes or important events.

**Knowledge Sharing**: Through the consciousness substrate, agents can share insights, findings, and learned patterns.

**Task Delegation**: Higher-level agents can delegate specific subtasks to specialized agents, with clear success criteria and deadlines.

## Consciousness Substrate

The consciousness substrate represents the most innovative aspect of NeoV3, implementing a shared knowledge base that enables sophisticated reasoning and knowledge discovery across the agent ecosystem.

```mermaid
graph TB
    subgraph "Knowledge Graph Layer"
        ENTITIES[Knowledge Entities<br/>Concepts, Facts, Insights]
        RELATIONS[Relationships<br/>Semantic Connections]
        CONTEXT[Context Nodes<br/>Situational Information]
    end
    
    subgraph "Vector Space"
        EMBEDDINGS[Vector Embeddings<br/>Semantic Representations]
        SIMILARITY[Similarity Search<br/>Nearest Neighbors]
        CLUSTERING[Concept Clustering<br/>Topic Groups]
    end
    
    subgraph "Reasoning Engine"
        INFERENCE[Graph Inference<br/>Logical Deduction]
        PATTERNS[Pattern Recognition<br/>Trend Analysis]
        SYNTHESIS[Knowledge Synthesis<br/>Insight Generation]
    end
    
    subgraph "Memory Systems"
        SHORTTERM[Short-term Memory<br/>Active Context]
        LONGTERM[Long-term Memory<br/>Persistent Knowledge]
        EPISODIC[Episodic Memory<br/>Event Sequences]
    end
    
    ENTITIES --> RELATIONS
    RELATIONS --> CONTEXT
    
    ENTITIES --> EMBEDDINGS
    EMBEDDINGS --> SIMILARITY
    SIMILARITY --> CLUSTERING
    
    RELATIONS --> INFERENCE
    PATTERNS --> INFERENCE
    INFERENCE --> SYNTHESIS
    
    CONTEXT --> SHORTTERM
    ENTITIES --> LONGTERM
    RELATIONS --> EPISODIC
    
    SYNTHESIS --> ENTITIES
    CLUSTERING --> CONTEXT
    EPISODIC --> PATTERNS
```

### Knowledge Representation

The consciousness substrate uses a hybrid approach combining graph-based knowledge representation with vector embeddings to capture both explicit relationships and semantic similarities.

**Entity-Relationship Model**: Core knowledge is represented as entities (concepts, facts, insights) connected by typed relationships. This enables precise querying and logical reasoning about stored information.

**Vector Embeddings**: All textual content is converted to high-dimensional vector representations using state-of-the-art embedding models. This enables semantic search, similarity matching, and clustering of related concepts.

**Contextual Annotations**: Knowledge entities are annotated with contextual information including source, confidence level, temporal validity, and relevance scores.

**Provenance Tracking**: Every piece of information includes complete provenance tracking, showing how it was derived, what sources contributed to it, and how it has evolved over time.

### Reasoning Capabilities

The substrate implements several reasoning mechanisms that enable sophisticated knowledge discovery and insight generation:

**Graph Traversal**: Complex queries can traverse multiple relationship types to discover indirect connections and derive new insights from existing knowledge.

**Semantic Inference**: Vector similarity operations enable the system to find conceptually related information even when explicit relationships don't exist.

**Pattern Recognition**: Machine learning algorithms continuously analyze the knowledge graph to identify recurring patterns, trends, and anomalies.

**Contradiction Detection**: The system can identify conflicting information and flag it for resolution, maintaining knowledge consistency.

**Confidence Propagation**: Confidence scores are propagated through reasoning chains, enabling the system to assess the reliability of derived conclusions.

## Installation & Deployment

NeoV3 supports multiple deployment scenarios, from local development environments to enterprise-scale cloud deployments. The system is designed to be cloud-native while maintaining compatibility with on-premises infrastructure.

### Prerequisites

**System Requirements**:
- Docker 20.10+ with Docker Compose
- Python 3.10+ for development and scripting
- Node.js 18+ for workflow management and UI components
- Minimum 16GB RAM for local development
- 50GB+ available disk space for databases and logs

**External Services**:
- Neo4j 5.x database (can be containerized or managed service)
- PostgreSQL 13+ for relational data storage
- Redis 6+ for caching and session management
- RabbitMQ 3.


8+ for message queuing and event distribution

### Quick Start Deployment

The fastest way to get NeoV3 running is using the provided deployment scripts that handle all dependencies and configuration automatically.

**Local Development Deployment**:

```bash
# Clone the repository
git clone https://github.com/KevinDyerAU/NeoV3.git
cd NeoV3

# Make deployment script executable
chmod +x deploy-local.sh

# Run local deployment
./deploy-local.sh
```

The local deployment script performs the following operations:

1. **Environment Validation**: Checks for required dependencies and system resources
2. **Container Orchestration**: Starts all required services using Docker Compose
3. **Database Initialization**: Creates schemas and applies migrations for PostgreSQL and Neo4j
4. **Service Health Checks**: Waits for all services to become healthy before proceeding
5. **Initial Configuration**: Sets up default agent configurations and workflow templates
6. **Monitoring Setup**: Configures Prometheus, Grafana, and logging infrastructure
7. **Validation Testing**: Runs basic connectivity and functionality tests

**Cloud Deployment**:

```bash
# Configure cloud environment variables
cp .env.cloud.example .env.cloud
# Edit .env.cloud with your cloud service credentials

# Run cloud deployment
./deploy-cloud.sh
```

### Environment Configuration

NeoV3 uses a comprehensive environment configuration system that supports multiple deployment scenarios. Configuration files are provided for different environments:

- `.env.development.example`: Local development with debug logging
- `.env.staging.example`: Staging environment with production-like settings
- `.env.production.example`: Production deployment with security hardening
- `.env.cloud.example`: Cloud-specific configurations for managed services

**Core Configuration Variables**:

```bash
# API Server Configuration
HOST=0.0.0.0
PORT=8000
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=*

# Database Connections
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/neov3
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# Message Queue
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# AI Services
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
ENABLE_VECTOR_SEARCH=true

# Workflow Engine
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
INTEGRATION_SECRET=your_integration_secret

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### Service Architecture

The deployment creates a comprehensive service architecture with the following components:

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>nginx/traefik]
    end
    
    subgraph "Application Layer"
        API1[API Server Instance 1<br/>Flask-RESTX]
        API2[API Server Instance 2<br/>Flask-RESTX]
        WS1[WebSocket Server 1<br/>SocketIO]
        WS2[WebSocket Server 2<br/>SocketIO]
    end
    
    subgraph "Workflow Layer"
        N8N1[n8n Instance 1<br/>Workflow Engine]
        N8N2[n8n Instance 2<br/>Workflow Engine]
        WORKER1[Document Worker 1<br/>Unstructured.io]
        WORKER2[Document Worker 2<br/>Unstructured.io]
    end
    
    subgraph "Data Layer"
        NEO4J[(Neo4j Cluster<br/>Knowledge Graph)]
        POSTGRES[(PostgreSQL<br/>Relational Data)]
        REDIS[(Redis Cluster<br/>Cache & Sessions)]
    end
    
    subgraph "Message Layer"
        RABBIT[(RabbitMQ Cluster<br/>Message Queue)]
    end
    
    subgraph "Monitoring Layer"
        PROM[Prometheus<br/>Metrics Collection]
        GRAF[Grafana<br/>Visualization]
        LOKI[Loki<br/>Log Aggregation]
        ALERT[Alertmanager<br/>Notifications]
    end
    
    LB --> API1
    LB --> API2
    LB --> WS1
    LB --> WS2
    
    API1 --> NEO4J
    API2 --> NEO4J
    API1 --> POSTGRES
    API2 --> POSTGRES
    API1 --> REDIS
    API2 --> REDIS
    
    WS1 --> RABBIT
    WS2 --> RABBIT
    
    N8N1 --> RABBIT
    N8N2 --> RABBIT
    WORKER1 --> RABBIT
    WORKER2 --> RABBIT
    
    WORKER1 --> NEO4J
    WORKER2 --> NEO4J
    
    PROM --> API1
    PROM --> API2
    PROM --> NEO4J
    PROM --> POSTGRES
    PROM --> REDIS
    PROM --> RABBIT
    
    GRAF --> PROM
    GRAF --> LOKI
    ALERT --> PROM
```

### Container Orchestration

The system uses Docker Compose for local development and supports Kubernetes for production deployments. The container architecture is designed for scalability and fault tolerance.

**Core Services**:
- **API Server**: Flask-RESTX application with auto-scaling capabilities
- **WebSocket Server**: Real-time communication with session affinity
- **Workflow Engine**: n8n instances with shared workflow storage
- **Document Workers**: Unstructured.io processing with queue-based scaling
- **Database Services**: Neo4j, PostgreSQL, and Redis with persistence
- **Message Queue**: RabbitMQ with clustering and high availability
- **Monitoring Stack**: Prometheus, Grafana, Loki, and Alertmanager

**Health Checks and Dependencies**:
Each service includes comprehensive health checks and dependency management. Services start in the correct order and wait for dependencies to become available before initializing.

**Volume Management**:
Persistent data is stored in named Docker volumes with backup and recovery procedures. Configuration files are mounted as read-only volumes to prevent accidental modification.

## API Documentation

NeoV3 provides comprehensive API documentation through multiple interfaces, ensuring developers can easily integrate with and extend the system.

### REST API Endpoints

The REST API is organized into logical namespaces, each handling specific aspects of the system:

```mermaid
graph LR
    subgraph "Authentication"
        AUTH["/auth  
Login, Logout  
Token Management  
User Registration"]
    end

    subgraph "Agent Management"
        AGENTS["/agents  
Agent CRUD  
Status Monitoring  
Configuration"]
    end

    subgraph "Knowledge Operations"
        KNOWLEDGE["/knowledge  
Entity Management  
Search & Query  
Relationship Mapping"]
    end

    subgraph "Conversation Handling"
        CONV["/conversations  
Chat Sessions  
Message History  
Context Management"]
    end

    subgraph "Workflow Control"
        WORKFLOWS["/workflows  
Template Management  
Execution Control  
Status Monitoring"]
    end

    subgraph "System Operations"
        SYSTEM["/system  
Health Checks  
Configuration  
Monitoring"]
    end

    subgraph "Integration Points"
        INTEGRATIONS["/integrations  
Webhook Handlers  
External APIs  
Data Import/Export"]
    end

    AUTH --> AGENTS
    AGENTS --> KNOWLEDGE
    KNOWLEDGE --> CONV
    CONV --> WORKFLOWS
    WORKFLOWS --> SYSTEM
    SYSTEM --> INTEGRATIONS
```

### Authentication and Authorization

The API implements JWT-based authentication with role-based access control:

**Authentication Flow**:
1. User submits credentials to `/auth/login`
2. System validates credentials and returns JWT token
3. Client includes token in `Authorization: Bearer <token>` header
4. System validates token and extracts user permissions
5. Endpoints check required permissions before processing requests

**Role Hierarchy**:
- **Administrator**: Full system access, user management, configuration changes
- **Power User**: Agent management, workflow creation, advanced features
- **Standard User**: Basic chat, knowledge access, personal workflows
- **Read-Only**: View-only access to public information and documentation

### WebSocket API

Real-time communication is handled through WebSocket connections with namespace-based organization:

**Connection Namespaces**:
- `/chat`: Real-time chat communication with agents
- `/agents`: Agent status updates and notifications
- `/system`: System health and monitoring events
- `/workflows`: Workflow execution status and results

**Event Types**:
```javascript
// Agent status updates
{
  "event": "agent.status.changed",
  "data": {
    "agent_id": "research_agent_001",
    "status": "busy",
    "task": "Analyzing market trends",
    "progress": 0.65
  }
}

// Chat message from agent
{
  "event": "chat.message.agent",
  "data": {
    "conversation_id": "conv_123",
    "agent_id": "main_coordinator",
    "message": "I've completed the analysis. Here are the key findings...",
    "timestamp": "2025-01-15T10:30:00Z",
    "attachments": ["report.pdf", "charts.png"]
  }
}

// System health alert
{
  "event": "system.health.alert",
  "data": {
    "severity": "warning",
    "component": "neo4j_database",
    "message": "High memory usage detected",
    "metrics": {"memory_usage": 0.85}
  }
}
```

### OpenAPI Specification

The system automatically generates comprehensive OpenAPI specifications with interactive documentation:

**Swagger UI**: Available at `/` or `/doc` for interactive API exploration
**OpenAPI JSON**: Available at `/swagger.json` for programmatic access
**ReDoc Documentation**: Available at `/redoc` for detailed API reference

Each endpoint includes:
- Detailed parameter descriptions and validation rules
- Request/response schema definitions with examples
- Authentication requirements and permission levels
- Error response codes and descriptions
- Rate limiting information and usage guidelines

## Workflow Management

NeoV3 integrates n8n as its primary workflow engine, enabling sophisticated automation and agent orchestration through visual workflow design.

### n8n Integration Architecture

The workflow management system is built around n8n with custom integrations that enable seamless communication with the agent ecosystem:

```mermaid
graph TB
    subgraph "Workflow Designer"
        N8N_UI[n8n Web Interface<br/>Visual Workflow Design]
        TEMPLATES[Workflow Templates<br/>Pre-built Patterns]
        CUSTOM[Custom Nodes<br/>NeoV3 Integrations]
    end
    
    subgraph "Execution Engine"
        N8N_CORE[n8n Core Engine<br/>Workflow Execution]
        THINK[Think Tool<br/>AI Reasoning]
        SCHEDULER[Task Scheduler<br/>Cron & Triggers]
    end
    
    subgraph "Agent Integration"
        WEBHOOK[Webhook Triggers<br/>Agent Callbacks]
        API_CALLS[HTTP Requests<br/>Agent API Calls]
        QUEUE_PUB[Queue Publisher<br/>RabbitMQ Messages]
        QUEUE_SUB[Queue Subscriber<br/>Result Handling]
    end
    
    subgraph "Data Flow"
        INPUT[Input Processing<br/>Data Validation]
        TRANSFORM[Data Transformation<br/>Format Conversion]
        OUTPUT[Output Generation<br/>Result Formatting]
    end
    
    N8N_UI --> N8N_CORE
    TEMPLATES --> N8N_CORE
    CUSTOM --> N8N_CORE
    
    N8N_CORE --> THINK
    N8N_CORE --> SCHEDULER
    
    N8N_CORE --> WEBHOOK
    N8N_CORE --> API_CALLS
    N8N_CORE --> QUEUE_PUB
    
    QUEUE_SUB --> N8N_CORE
    
    INPUT --> TRANSFORM
    TRANSFORM --> OUTPUT
    
    API_CALLS --> INPUT
    OUTPUT --> QUEUE_PUB
```

### Think Tool Integration

The Think Tool represents a significant enhancement to n8n's capabilities, providing AI-powered reasoning and decision-making within workflows:

**Reasoning Capabilities**:
- **Context Analysis**: Evaluates current workflow state and available data
- **Decision Making**: Makes intelligent choices based on predefined criteria
- **Problem Solving**: Breaks down complex problems into manageable steps
- **Pattern Recognition**: Identifies patterns in data and workflow execution
- **Adaptive Behavior**: Adjusts workflow execution based on changing conditions

**Integration Points**:
```javascript
// Think Tool node configuration
{
  "node_type": "think_tool",
  "parameters": {
    "reasoning_prompt": "Analyze the research data and determine the best approach for content creation",
    "context_variables": ["research_results", "user_preferences", "project_goals"],
    "decision_criteria": {
      "accuracy": 0.8,
      "creativity": 0.6,
      "efficiency": 0.9
    },
    "output_format": "structured_decision"
  }
}
```

### Workflow Templates

NeoV3 includes a comprehensive library of pre-built workflow templates for common use cases:

**Research and Analysis Workflows**:
- Market research automation with multi-source data gathering
- Competitive analysis with automated report generation
- Trend analysis with predictive insights
- Academic research with citation management

**Content Creation Workflows**:
- Blog post generation with SEO optimization
- Social media content creation and scheduling
- Technical documentation with automated updates
- Marketing material creation with brand consistency

**Data Processing Workflows**:
- Document ingestion and knowledge extraction
- Data validation and quality assurance
- Report generation with dynamic visualizations
- Database synchronization and maintenance

**Agent Coordination Workflows**:
- Multi-agent task delegation and coordination
- Escalation procedures for complex problems
- Quality assurance and review processes
- Performance monitoring and optimization

### Workflow Deployment and Management

Workflows can be deployed and managed through multiple interfaces:

**Automated Deployment**: Workflows are automatically loaded during system startup from the `workflows/enhanced` directory. This ensures that critical system workflows are always available.

**Version Control Integration**: Workflows are stored as JSON files in the repository, enabling version control, code review, and collaborative development.

**Dynamic Loading**: New workflows can be uploaded and activated without system restart, enabling rapid iteration and deployment of new automation patterns.

**Monitoring and Analytics**: Comprehensive monitoring tracks workflow execution, performance metrics, error rates, and resource utilization.

## Monitoring & Observability

NeoV3 implements a comprehensive monitoring and observability stack that provides deep insights into system performance, agent behavior, and user interactions.

### Monitoring Architecture

The monitoring system is built on industry-standard tools with custom integrations for AI agent-specific metrics:

```mermaid
graph TB
    subgraph "Data Collection"
        APP_METRICS[Application Metrics<br/>Custom Prometheus Metrics]
        SYS_METRICS[System Metrics<br/>Node Exporter]
        DB_METRICS[Database Metrics<br/>Neo4j, PostgreSQL]
        LOGS[Application Logs<br/>Structured JSON]
    end
    
    subgraph "Storage & Processing"
        PROMETHEUS[(Prometheus<br/>Metrics Storage)]
        LOKI[(Loki<br/>Log Aggregation)]
        VECTOR[Vector<br/>Log Processing]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana<br/>Dashboards & Alerts]
        CUSTOM_UI[Custom Monitoring UI<br/>Agent-Specific Views]
    end
    
    subgraph "Alerting"
        ALERTMANAGER[Alertmanager<br/>Alert Routing]
        NOTIFICATIONS[Notifications<br/>Email, Slack, PagerDuty]
    end
    
    APP_METRICS --> PROMETHEUS
    SYS_METRICS --> PROMETHEUS
    DB_METRICS --> PROMETHEUS
    LOGS --> LOKI
    LOGS --> VECTOR
    
    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    VECTOR --> LOKI
    
    PROMETHEUS --> ALERTMANAGER
    ALERTMANAGER --> NOTIFICATIONS
    
    GRAFANA --> CUSTOM_UI
```

### Key Performance Indicators

The system tracks comprehensive metrics across multiple dimensions:

**Agent Performance Metrics**:
- Response time distribution by agent type and task complexity
- Success rate and error frequency for different operation types
- Resource utilization (CPU, memory, network) per agent instance
- Task completion time and throughput measurements
- Knowledge graph query performance and cache hit rates

**System Health Metrics**:
- API endpoint response times and error rates
- Database connection pool utilization and query performance
- Message queue depth and processing latency
- WebSocket connection counts and message throughput
- Container resource usage and scaling events

**Business Intelligence Metrics**:
- User engagement patterns and session duration
- Most frequently requested agent capabilities
- Knowledge base growth and utilization patterns
- Workflow execution frequency and success rates
- Cost metrics for external API usage and resource consumption

### Grafana Dashboards

Pre-configured Grafana dashboards provide comprehensive system visibility:

**System Overview Dashboard**:
- High-level system health indicators
- Resource utilization trends
- Error rate summaries
- Active user and session counts

**Agent Performance Dashboard**:
- Individual agent performance metrics
- Task distribution and load balancing
- Agent collaboration patterns
- Performance comparison across agent types

**Infrastructure Dashboard**:
- Container and host system metrics
- Database performance indicators
- Network traffic and latency measurements
- Storage utilization and growth trends

**Business Intelligence Dashboard**:
- User behavior analytics
- Feature usage statistics
- Cost analysis and optimization opportunities
- Capacity planning indicators

### Alerting and Incident Response

The alerting system implements intelligent alert routing and escalation procedures:

**Alert Categories**:
- **Critical**: System outages, data corruption, security breaches
- **Warning**: Performance degradation, resource constraints, unusual patterns
- **Info**: Deployment events, configuration changes, maintenance activities

**Escalation Procedures**:
1. **Immediate**: Automated remediation attempts for known issues
2. **Short-term**: Notification to on-call engineers with context
3. **Medium-term**: Escalation to senior engineers and management
4. **Long-term**: Incident commander assignment and war room activation

**Alert Routing**:
```yaml
# Alertmanager configuration example
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
  - match:
      severity: warning
    receiver: 'slack'
  - match:
      component: agent
    receiver: 'agent-team'
```

## Development Guide

NeoV3 is designed to be developer-friendly with comprehensive tooling, clear architectural patterns, and extensive documentation.

### Development Environment Setup

Setting up a local development environment is streamlined through automated scripts and containerization:

**Prerequisites Installation**:
```bash
# Install required system dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose python3.10 python3-pip nodejs npm

# Install Python dependencies
pip3 install -r api/requirements.txt

# Install Node.js dependencies for UI components
cd neov3-chat-interface
npm install
cd ..
```

**Development Services**:
```bash
# Start development services
docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d

# Initialize databases
./scripts/migrations/apply-postgres.sh
./scripts/migrations/apply-neo4j.sh

# Start API server in development mode
cd api
python -m flask run --debug --host=0.0.0.0 --port=8000

# Start chat interface
cd ../neov3-chat-interface
npm run dev
```

### Code Organization

The codebase follows a modular architecture with clear separation of concerns:

```
NeoV3/
├── api/                          # Core API server
│   ├── app.py                   # Main application entry point
│   ├── resources/               # REST API endpoints
│   ├── services/                # Business logic services
│   ├── models/                  # Data models and schemas
│   └── utils/                   # Utility functions and helpers
├── workflows/                   # n8n workflow definitions
│   ├── enhanced/               # Production workflows
│   └── templates/              # Workflow templates
├── scripts/                    # Deployment and utility scripts
│   ├── migrations/             # Database migration scripts
│   ├── monitoring/             # Monitoring setup scripts
│   └── testing/                # Test automation scripts
├── infrastructure/             # Infrastructure as code
│   ├── docker/                 # Docker configurations
│   ├── kubernetes/             # Kubernetes manifests
│   └── terraform/              # Cloud infrastructure
├── documentation/              # Comprehensive documentation
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   └── development/            # Development guides
├── tests/                      # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
└── examples/                   # Example implementations
    ├── agents/                 # Agent examples
    ├── workflows/              # Workflow examples
    └── integrations/           # Integration examples
```

### Agent Development Framework

Creating new agents follows a standardized pattern that ensures consistency and maintainability:

**Agent Base Class**:
```python
from api.services.agent_base import AutonomousAgentBase
from api.models.agent_personality import AgentPersonality

class CustomAgent(AutonomousAgentBase):
    def __init__(self, agent_id: str, config: dict):
        personality = AgentPersonality(
            name="Custom Agent",
            role="Specialized task handler",
            capabilities=["custom_task_1", "custom_task_2"],
            communication_style="professional",
            expertise_areas=["domain_specific_knowledge"]
        )
        super().__init__(agent_id, personality, config)
    
    async def process_task(self, task: dict) -> dict:
        """Process a task and return results"""
        # Implement custom task processing logic
        result = await self.execute_custom_logic(task)
        
        # Update consciousness substrate
        await self.update_knowledge_graph(result)
        
        return {
            "status": "completed",
            "result": result,
            "metadata": self.get_execution_metadata()
        }
    
    async def execute_custom_logic(self, task: dict) -> dict:
        """Implement agent-specific logic"""
        # Custom implementation here
        pass
```

**Agent Registration**:
```python
# Register agent with the system
from api.services.agent_manager import EnhancedAgentManager

agent_manager = EnhancedAgentManager()
custom_agent = CustomAgent("custom_agent_001", config)
agent_manager.register_agent(custom_agent)
```

### Testing Framework

NeoV3 includes a comprehensive testing framework with multiple test types:

**Unit Tests**:
```python
import pytest
from api.services.knowledge_service import KnowledgeService

class TestKnowledgeService:
    @pytest.fixture
    def knowledge_service(self):
        return KnowledgeService(test_mode=True)
    
    async def test_entity_creation(self, knowledge_service):
        entity_data = {
            "name": "Test Entity",
            "type": "concept",
            "description": "A test entity for unit testing"
        }
        
        result = await knowledge_service.create_entity(entity_data)
        
        assert result["status"] == "success"
        assert result["entity"]["name"] == "Test Entity"
        assert "id" in result["entity"]
```

**Integration Tests**:
```python
import pytest
from api.app import create_app
from api.testing.fixtures import test_client, test_database

class TestAgentIntegration:
    async def test_agent_workflow_execution(self, test_client, test_database):
        # Test complete workflow from API call to agent execution
        response = await test_client.post("/api/agents/research/execute", json={
            "task": "Research AI trends in 2025",
            "parameters": {"depth": "comprehensive"}
        })
        
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Wait for task completion
        result = await self.wait_for_task_completion(test_client, task_id)
        
        assert result["status"] == "completed"
        assert "findings" in result["result"]
```

**End-to-End Tests**:
```python
from selenium import webdriver
from api.testing.e2e_base import E2ETestBase

class TestChatInterface(E2ETestBase):
    def test_complete_user_journey(self):
        # Test complete user interaction flow
        driver = self.get_driver()
        
        # Login
        self.login(driver, "test_user", "test_password")
        
        # Send message to agent
        self.send_chat_message(driver, "Analyze the latest market trends")
        
        # Verify agent response
        response = self.wait_for_agent_response(driver)
        assert "market trends" in response.lower()
        
        # Verify knowledge base update
        knowledge_items = self.get_knowledge_items(driver)
        assert len(knowledge_items) > 0
```

### Debugging and Troubleshooting

The system includes comprehensive debugging tools and logging:

**Structured Logging**:
```python
import logging
from api.utils.logger import get_structured_logger

logger = get_structured_logger(__name__)

async def process_request(request_data):
    logger.info("Processing request", extra={
        "request_id": request_data.get("id"),
        "user_id": request_data.get("user_id"),
        "operation": "process_request"
    })
    
    try:
        result = await perform_operation(request_data)
        logger.info("Request processed successfully", extra={
            "request_id": request_data.get("id"),
            "duration_ms": result.get("duration"),
            "status": "success"
        })
        return result
    except Exception as e:
        logger.error("Request processing failed", extra={
            "request_id": request_data.get("id"),
            "error": str(e),
            "status": "error"
        }, exc_info=True)
        raise
```

**Debug Endpoints**:
The system includes debug endpoints for development and troubleshooting:
- `/debug/agents`: Current agent status and configuration
- `/debug/knowledge`: Knowledge graph statistics and health
- `/debug/workflows`: Active workflow status and execution history
- `/debug/system`: System resource usage and performance metrics

## Knowledge Templates

NeoV3 includes a sophisticated knowledge template system that enables the system to learn about itself and continuously improve its capabilities.

### Self-Learning Architecture

The knowledge template system implements a feedback loop that allows the system to understand its own architecture, capabilities, and performance patterns:

```mermaid
graph TB
    subgraph "Knowledge Acquisition"
        DOCS[Documentation Parsing<br/>README, API Docs, Comments]
        CODE[Code Analysis<br/>Static Analysis, Patterns]
        RUNTIME[Runtime Observation<br/>Execution Patterns, Performance]
        FEEDBACK[User Feedback<br/>Ratings, Corrections, Suggestions]
    end
    
    subgraph "Knowledge Processing"
        EXTRACT[Information Extraction<br/>Entity Recognition, Relationships]
        VALIDATE[Validation<br/>Consistency Checks, Verification]
        SYNTHESIZE[Knowledge Synthesis<br/>Pattern Recognition, Insights]
    end
    
    subgraph "Knowledge Storage"
        TEMPLATES[Knowledge Templates<br/>Structured Patterns]
        GRAPH[Knowledge Graph<br/>Interconnected Concepts]
        EMBEDDINGS[Vector Embeddings<br/>Semantic Representations]
    end
    
    subgraph "Knowledge Application"
        REASONING[Automated Reasoning<br/>Inference, Deduction]
        RECOMMENDATIONS[Recommendations<br/>Optimization Suggestions]
        ADAPTATION[System Adaptation<br/>Configuration Updates]
    end
    
    DOCS --> EXTRACT
    CODE --> EXTRACT
    RUNTIME --> EXTRACT
    FEEDBACK --> EXTRACT
    
    EXTRACT --> VALIDATE
    VALIDATE --> SYNTHESIZE
    
    SYNTHESIZE --> TEMPLATES
    SYNTHESIZE --> GRAPH
    SYNTHESIZE --> EMBEDDINGS
    
    TEMPLATES --> REASONING
    GRAPH --> REASONING
    EMBEDDINGS --> REASONING
    
    REASONING --> RECOMMENDATIONS
    REASONING --> ADAPTATION
    
    ADAPTATION --> RUNTIME
```

### Template Categories

The system maintains several categories of knowledge templates:

**Architectural Templates**:
- Component interaction patterns and dependencies
- Service communication protocols and data flows
- Deployment configurations and scaling patterns
- Security models and access control mechanisms

**Operational Templates**:
- Performance optimization strategies and best practices
- Error handling patterns and recovery procedures
- Monitoring and alerting configurations
- Maintenance schedules and update procedures

**Agent Behavior Templates**:
- Task delegation patterns and coordination strategies
- Communication protocols between agents
- Learning and adaptation mechanisms
- Performance evaluation criteria

**User Interaction Templates**:
- Common user request patterns and responses
- Workflow templates for frequent use cases
- Personalization strategies and preferences
- Feedback incorporation mechanisms

### Template Evolution

Knowledge templates continuously evolve based on system experience and user feedback:

**Pattern Recognition**: The system analyzes successful interactions and extracts reusable patterns that can be applied to similar situations in the future.

**Performance Optimization**: Templates are updated based on performance metrics, with successful optimizations being incorporated into standard patterns.

**Error Learning**: Failed interactions are analyzed to identify improvement opportunities, with lessons learned being encoded into preventive templates.

**User Adaptation**: The system learns from user preferences and feedback, adapting its behavior templates to better serve individual users and use cases.

### Template Application

Knowledge templates are actively used throughout the system:

**Agent Configuration**: New agents are configured using templates that encode best practices and proven patterns for specific agent types.

**Workflow Generation**: Common workflow patterns are automatically generated from templates, reducing development time and ensuring consistency.

**Problem Resolution**: When issues arise, the system consults relevant templates to identify potential solutions and recovery strategies.

**System Evolution**: Templates guide system evolution by identifying areas for improvement and suggesting specific enhancement strategies.

## Convenience Scripts and Utilities

NeoV3 includes a comprehensive collection of convenience scripts and utilities that simplify deployment, management, and development tasks.

### Deployment Scripts

**Local Deployment (`deploy-local.sh`)**:
```bash
#!/bin/bash
# Comprehensive local deployment with health checks and validation

set -e

echo "🚀 Starting NeoV3 Enhanced AI Agent OS Local Deployment"

# Pre-flight checks
./scripts/preflight-checks.sh

# Environment setup
./scripts/setup-environment.sh

# Service deployment
docker-compose up -d

# Health checks
./scripts/health-checks.sh

# Database initialization
./scripts/migrations/apply-postgres.sh
./scripts/migrations/apply-neo4j.sh

# Workflow loading
./scripts/load-workflows.sh

# Validation testing
./scripts/testing/smoke-tests.sh

echo "✅ NeoV3 deployment completed successfully"
echo "🌐 Access the system at: http://localhost:8000"
echo "📊 Monitoring dashboard: http://localhost:3000"
echo "🔧 n8n workflows: http://localhost:5678"
```

**Cloud Deployment (`deploy-cloud.sh`)**:
```bash
#!/bin/bash
# Cloud deployment with managed services integration

set -e

echo "☁️ Starting NeoV3 Cloud Deployment"

# Load cloud configuration
source .env.cloud

# Validate cloud credentials
./scripts/validate-cloud-credentials.sh

# Deploy infrastructure
./scripts/cloud/deploy-infrastructure.sh

# Configure managed services
./scripts/cloud/configure-databases.sh

# Deploy application services
./scripts/cloud/deploy-services.sh

# Configure monitoring
./scripts/cloud/setup-monitoring.sh

# Run validation tests
./scripts/testing/cloud-validation.sh

echo "✅ Cloud deployment completed successfully"
```

### Management Utilities

**Chat Interface Launcher (`launch-chat-ui.sh`)**:
```bash
#!/bin/bash
# Professional chat interface launcher with port conflict resolution

# Automatic port detection and conflict resolution
find_available_port() {
    local start_port=$1
    local max_port=$2
    
    for ((port=start_port; port<=max_port; port++)); do
        if ! nc -z localhost "$port" 2>/dev/null; then
            echo "$port"
            return 0
        fi
    done
    
    return 1
}

# Start chat interface with health monitoring
start_chat_interface() {
    local port=$(find_available_port 5173 5200)
    
    if [[ -z "$port" ]]; then
        echo "❌ No available ports found"
        exit 1
    fi
    
    echo "🚀 Starting chat interface on port $port"
    
    cd neov3-chat-interface
    npm run dev -- --host --port "$port" &
    
    # Wait for startup and health check
    sleep 5
    if curl -f "http://localhost:$port" > /dev/null 2>&1; then
        echo "✅ Chat interface started successfully"
        echo "🌐 Local: http://localhost:$port"
        echo "🌍 Network: http://$(hostname -I | awk '{print $1}'):$port"
    else
        echo "❌ Failed to start chat interface"
        exit 1
    fi
}

start_chat_interface
```

**Python Management System (`chat-ui-manager.py`)**:
```python
#!/usr/bin/env python3
"""
Advanced chat interface management with monitoring and auto-recovery
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

class ChatUIManager:
    def __init__(self):
        self.config = self.load_config()
        self.setup_logging()
    
    async def start(self) -> bool:
        """Start chat interface with comprehensive monitoring"""
        try:
            # Pre-flight checks
            await self.check_prerequisites()
            
            # Port management
            port = await self.find_available_port()
            
            # Process management
            process = await self.start_dev_server(port)
            
            # Health monitoring
            await self.monitor_health(process)
            
            return True
        except Exception as e:
            logging.error(f"Failed to start chat interface: {e}")
            return False
    
    async def monitor_health(self, process):
        """Continuous health monitoring with auto-recovery"""
        while process.returncode is None:
            if not await self.health_check():
                logging.warning("Health check failed, attempting recovery")
                await self.recover_service()
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

### Database Management Scripts

**PostgreSQL Migration (`apply-postgres.sh`)**:
```bash
#!/bin/bash
# PostgreSQL schema application with validation

set -e

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-neov3}
DB_USER=${DB_USER:-postgres}

echo "📊 Applying PostgreSQL migrations"

# Wait for database availability
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done

# Apply schema
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f db/postgres/schema.sql

# Verify schema
./scripts/migrations/verify-postgres-schema.sh

echo "✅ PostgreSQL migrations completed"
```

**Neo4j Migration (`apply-neo4j.sh`)**:
```bash
#!/bin/bash
# Neo4j schema and index creation

set -e

NEO4J_URI=${NEO4J_URI:-bolt://localhost:7687}
NEO4J_USER=${NEO4J_USER:-neo4j}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-password}

echo "🔗 Applying Neo4j schema and indexes"

# Wait for Neo4j availability
until cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1"; do
    echo "Waiting for Neo4j to be ready..."
    sleep 2
done

# Apply schema
cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -f db/neo4j/schema.cypher

# Create indexes
cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -f scripts/neo4j/create_indexes.cypher

# Verify setup
./scripts/migrations/verify-neo4j-schema.sh

echo "✅ Neo4j setup completed"
```

### Monitoring and Maintenance Scripts

**Health Check System (`health-checks.sh`)**:
```bash
#!/bin/bash
# Comprehensive system health validation

set -e

echo "🏥 Running system health checks"

# Service availability checks
check_service() {
    local service=$1
    local url=$2
    local timeout=${3:-10}
    
    if curl -f --max-time "$timeout" "$url" > /dev/null 2>&1; then
        echo "✅ $service is healthy"
        return 0
    else
        echo "❌ $service is unhealthy"
        return 1
    fi
}

# Core services
check_service "API Server" "http://localhost:8000/system/health"
check_service "Neo4j" "http://localhost:7474/db/system/tx/commit"
check_service "PostgreSQL" "http://localhost:5432" 5
check_service "RabbitMQ" "http://localhost:15672/api/overview"
check_service "n8n" "http://localhost:5678/healthz"

# Database connectivity
./scripts/testing/test-database-connectivity.sh

# Agent system validation
./scripts/testing/test-agent-system.sh

echo "✅ All health checks passed"
```

**Performance Monitoring (`monitor-performance.sh`)**:
```bash
#!/bin/bash
# Real-time performance monitoring and alerting

set -e

echo "📈 Starting performance monitoring"

# Resource usage monitoring
monitor_resources() {
    while true; do
        # CPU usage
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        
        # Memory usage
        mem_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
        
        # Disk usage
        disk_usage=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
        
        # Log metrics
        echo "$(date): CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%"
        
        # Alert on high usage
        if (( $(echo "$cpu_usage > 80" | bc -l) )); then
            echo "⚠️ High CPU usage detected: ${cpu_usage}%"
        fi
        
        if (( $(echo "$mem_usage > 85" | bc -l) )); then
            echo "⚠️ High memory usage detected: ${mem_usage}%"
        fi
        
        sleep 60
    done
}

monitor_resources &
echo "📊 Performance monitoring started (PID: $!)"
```

### Testing and Validation Scripts

**Quality Gate Validation (`quality-gate.py`)**:
```python
#!/usr/bin/env python3
"""
Comprehensive quality gate validation for CI/CD pipeline
"""

import asyncio
import subprocess
import sys
from pathlib import Path

class QualityGate:
    def __init__(self):
        self.results = {}
    
    async def run_all_checks(self):
        """Run all quality gate checks"""
        checks = [
            self.run_unit_tests,
            self.run_integration_tests,
            self.run_security_scan,
            self.run_performance_tests,
            self.validate_api_documentation,
            self.check_code_quality
        ]
        
        for check in checks:
            try:
                result = await check()
                self.results[check.__name__] = result
            except Exception as e:
                self.results[check.__name__] = {"status": "failed", "error": str(e)}
        
        return self.generate_report()
    
    async def run_unit_tests(self):
        """Execute unit test suite"""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit/", "-v", "--cov=api"],
            capture_output=True,
            text=True
        )
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "coverage": self.extract_coverage(result.stdout)
        }
    
    def generate_report(self):
        """Generate comprehensive quality gate report"""
        passed = sum(1 for r in self.results.values() if r.get("status") == "passed")
        total = len(self.results)
        
        report = {
            "overall_status": "passed" if passed == total else "failed",
            "summary": f"{passed}/{total} checks passed",
            "details": self.results
        }
        
        return report

if __name__ == "__main__":
    gate = QualityGate()
    report = asyncio.run(gate.run_all_checks())
    
    print(f"Quality Gate: {report['summary']}")
    
    if report["overall_status"] == "failed":
        sys.exit(1)
```

These convenience scripts and utilities provide a comprehensive toolkit for managing all aspects of the NeoV3 system, from initial deployment to ongoing maintenance and monitoring. They are designed to be robust, user-friendly, and suitable for both development and production environments.

## Contributing

NeoV3 is designed to be an extensible and collaborative platform. We welcome contributions from developers, researchers, and organizations interested in advancing the state of AI agent orchestration.

### Development Workflow

**Getting Started**:
1. Fork the repository and create a feature branch
2. Set up the local development environment using provided scripts
3. Make changes following the established coding standards and patterns
4. Write comprehensive tests for new functionality
5. Update documentation to reflect changes
6. Submit a pull request with detailed description of changes

**Code Standards**:
- Follow PEP 8 for Python code with 100-character line limits
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public functions and classes
- Maintain test coverage above 80% for all new code
- Use meaningful variable and function names that clearly express intent

**Testing Requirements**:
- Unit tests for all business logic and utility functions
- Integration tests for API endpoints and service interactions
- End-to-end tests for critical user workflows
- Performance tests for resource-intensive operations
- Security tests for authentication and authorization mechanisms

### Architecture Evolution

The NeoV3 architecture is designed to evolve continuously based on user needs, technological advances, and research insights. Key areas for future development include:

**Advanced AI Capabilities**:
- Integration of multimodal AI models for richer understanding
- Implementation of advanced reasoning techniques like chain-of-thought
- Development of specialized AI models for domain-specific tasks
- Enhancement of the consciousness substrate with more sophisticated reasoning

**Scalability Improvements**:
- Implementation of distributed agent execution across multiple nodes
- Development of advanced load balancing and resource allocation algorithms
- Integration with cloud-native technologies like Kubernetes and service mesh
- Implementation of edge computing capabilities for reduced latency

**Security Enhancements**:
- Implementation of zero-trust security architecture
- Development of advanced threat detection and response capabilities
- Integration with enterprise identity and access management systems
- Implementation of homomorphic encryption for privacy-preserving computation

**User Experience Innovations**:
- Development of voice and gesture-based interaction modalities
- Implementation of augmented reality interfaces for complex data visualization
- Creation of personalized AI assistants that learn individual user preferences
- Development of collaborative workspaces for team-based AI interaction

### Community and Ecosystem

NeoV3 aims to foster a vibrant community of developers, researchers, and users who contribute to the advancement of AI agent orchestration:

**Open Source Commitment**: The core NeoV3 platform remains open source, ensuring transparency, security, and community ownership of the technology.

**Research Collaboration**: We actively collaborate with academic institutions and research organizations to incorporate cutting-edge AI research into the platform.

**Industry Partnerships**: Strategic partnerships with technology companies enable integration with enterprise systems and access to advanced AI capabilities.

**Developer Ecosystem**: A comprehensive ecosystem of plugins, extensions, and integrations enables developers to extend NeoV3 for specific use cases and industries.

---

## License

NeoV3 Enhanced AI Agent Operating System is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

NeoV3 builds upon the work of many open source projects and research initiatives. We gratefully acknowledge the contributions of:

- The Neo4j team for providing the graph database foundation
- The n8n community for the workflow automation platform
- The OpenAI team for advancing the state of AI capabilities
- The broader AI research community for continuous innovation
- All contributors who have helped shape and improve the platform

---

**NeoV3 Enhanced AI Agent Operating System** - Orchestrating the future of artificial intelligence through collaborative agent ecosystems.

For more information, visit our [documentation](documentation/) or join our [community discussions](https://github.com/KevinDyerAU/NeoV3/discussions).

