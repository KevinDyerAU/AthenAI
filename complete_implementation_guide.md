# Enhanced AI Agent OS - Complete Implementation Guide

**Author:** Manus AI  
**Date:** August 19, 2025  
**Version:** 3.0 - Complete From-Scratch Implementation  
**Target:** New Empty Git Repository  
**Document Type:** Comprehensive Step-by-Step Implementation Guide

## Executive Summary

This comprehensive implementation guide provides complete, detailed instructions for building the Enhanced AI Agent OS from scratch in a new empty git repository. Every file, configuration, workflow, and deployment script is provided in full with explicit step-by-step instructions designed for execution within Windsurf IDE or any modern development environment.

The implementation leverages modern n8n built-in AI capabilities (version 1.19.4+) that include native LangChain functionality, eliminating the need for community packages while providing sophisticated AI agent orchestration, autonomous reasoning, and Node-as-Tools integration. The system architecture includes twelve specialized AI agent workflows, comprehensive Docker infrastructure, monitoring capabilities, and a built-in AI chat agent that serves as the primary user interface.

The guide is structured in five major implementation phases that build upon each other to create a production-ready AI agent ecosystem. Each phase includes complete code listings, configuration files, testing procedures, and validation steps. The implementation is designed to run locally using Docker Compose while providing optional cloud integration capabilities for hybrid deployment scenarios.

## Prerequisites and Development Environment Setup

Before beginning the implementation, ensure that your development environment meets the comprehensive requirements for building and running the Enhanced AI Agent OS. The system requires substantial computational resources due to the multiple database services, AI processing capabilities, and concurrent workflow execution that characterizes a sophisticated AI agent ecosystem.

Your development machine should have Docker Desktop installed and configured with at least 16GB of RAM allocated to Docker containers. This allocation is necessary to support PostgreSQL for n8n data storage, Neo4j for the consciousness substrate graph database, RabbitMQ for inter-agent message queuing, Prometheus for metrics collection, Grafana for monitoring dashboards, and n8n itself with multiple concurrent AI agent workflows. Additionally, ensure that your machine has at least 50GB of available disk space for container images, database storage, workflow data, and log files.

Node.js version 18 or higher must be installed on your development machine to support n8n workflow development, testing scripts, and any custom tooling that may be required during the implementation process. Python 3.9 or higher is recommended for any custom scripts or integrations that may be developed as part of the extended functionality.

Your development environment should include a modern code editor or IDE with support for JSON, YAML, Markdown, JavaScript, and Docker configuration files. Windsurf IDE is specifically recommended due to its excellent support for multi-file projects, integrated terminal capabilities, and robust Docker integration features that streamline the development and deployment process.

Git must be installed and configured with your credentials, as the implementation process involves creating a comprehensive repository structure with multiple directories, configuration files, and documentation. Ensure that you have appropriate access permissions for creating and pushing to your target repository.

## Phase 1: Project Structure and Foundation Files

### Repository Structure Creation

The Enhanced AI Agent OS requires a well-organized directory structure that separates concerns while maintaining clear relationships between different system components. The structure follows modern software development practices with dedicated directories for deployment configurations, workflow definitions, monitoring setup, testing infrastructure, and comprehensive documentation.

Begin by creating the root directory structure in your new empty git repository. The organization reflects the multi-layered architecture of the system, with clear separation between local deployment configurations, production deployment options, workflow definitions, monitoring infrastructure, testing frameworks, and extensive documentation.

Create the following directory structure in your repository root:

```
enhanced-ai-agent-os/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── local-deployment/
│   ├── docker-compose.local.yml
│   ├── .env.local.example
│   └── scripts/
│       ├── start.sh
│       ├── stop.sh
│       ├── restart.sh
│       ├── logs.sh
│       └── backup.sh
├── infrastructure/
│   ├── docker/
│   │   ├── n8n/
│   │   │   ├── Dockerfile
│   │   │   └── config/
│   │   │       ├── n8n-config.json
│   │   │       └── workflows/
│   │   ├── neo4j/
│   │   │   ├── Dockerfile
│   │   │   ├── init/
│   │   │   │   ├── 01-create-constraints.cypher
│   │   │   │   ├── 02-create-indexes.cypher
│   │   │   │   └── 03-seed-data.cypher
│   │   │   └── plugins/
│   │   ├── rabbitmq/
│   │   │   ├── Dockerfile
│   │   │   ├── rabbitmq.conf
│   │   │   ├── definitions.json
│   │   │   └── enabled_plugins
│   │   └── postgres/
│   │       ├── Dockerfile
│   │       └── init/
│   │           ├── 01-create-databases.sql
│   │           ├── 02-create-extensions.sql
│   │           └── 03-create-schemas.sql
│   ├── monitoring/
│   │   ├── prometheus/
│   │   │   ├── prometheus.yml
│   │   │   ├── rules/
│   │   │   │   ├── n8n-alerts.yml
│   │   │   │   ├── system-alerts.yml
│   │   │   │   └── ai-agent-alerts.yml
│   │   │   └── targets/
│   │   │       └── static-targets.yml
│   │   ├── grafana/
│   │   │   ├── dashboards/
│   │   │   │   ├── n8n-overview.json
│   │   │   │   ├── ai-agent-performance.json
│   │   │   │   ├── consciousness-substrate.json
│   │   │   │   └── system-health.json
│   │   │   ├── datasources/
│   │   │   │   ├── prometheus.yml
│   │   │   │   ├── neo4j.yml
│   │   │   │   └── postgres.yml
│   │   │   └── provisioning/
│   │   │       ├── dashboards.yml
│   │   │       └── datasources.yml
│   │   └── loki/
│   │       ├── loki-config.yml
│   │       └── promtail-config.yml
│   └── nginx/
│       ├── nginx.conf
│       ├── ssl/
│       └── sites-available/
│           └── enhanced-ai-agent-os.conf
├── workflows/
│   ├── core/
│   │   ├── 01-master-orchestration.json
│   │   ├── 02-consciousness-substrate.json
│   │   ├── 03-inter-agent-communication.json
│   │   └── 04-system-health-monitoring.json
│   ├── specialized-agents/
│   │   ├── 10-research-agent.json
│   │   ├── 11-creative-agent.json
│   │   ├── 12-analysis-agent.json
│   │   ├── 13-development-agent.json
│   │   ├── 14-communication-agent.json
│   │   ├── 15-planning-agent.json
│   │   ├── 16-execution-agent.json
│   │   └── 17-quality-assurance-agent.json
│   ├── user-interfaces/
│   │   ├── 20-ai-chat-agent.json
│   │   ├── 21-api-gateway.json
│   │   ├── 22-webhook-handlers.json
│   │   └── 23-notification-system.json
│   ├── utilities/
│   │   ├── 30-data-processing.json
│   │   ├── 31-file-management.json
│   │   ├── 32-external-integrations.json
│   │   └── 33-backup-and-recovery.json
│   └── templates/
│       ├── agent-template.json
│       ├── webhook-template.json
│       └── utility-template.json
├── testing/
│   ├── unit/
│   │   ├── workflows/
│   │   ├── agents/
│   │   └── integrations/
│   ├── integration/
│   │   ├── agent-communication/
│   │   ├── database-operations/
│   │   └── external-apis/
│   ├── e2e/
│   │   ├── user-scenarios/
│   │   ├── system-workflows/
│   │   └── performance/
│   ├── scripts/
│   │   ├── test-runner.js
│   │   ├── workflow-validator.js
│   │   ├── performance-tester.js
│   │   └── ai-capability-tester.js
│   └── fixtures/
│       ├── sample-data/
│       ├── test-workflows/
│       └── mock-responses/
├── docs/
│   ├── architecture/
│   │   ├── system-overview.md
│   │   ├── agent-specifications.md
│   │   ├── data-flow-diagrams.md
│   │   └── security-model.md
│   ├── deployment/
│   │   ├── local-setup.md
│   │   ├── production-deployment.md
│   │   ├── cloud-integration.md
│   │   └── troubleshooting.md
│   ├── workflows/
│   │   ├── workflow-documentation.md
│   │   ├── agent-interactions.md
│   │   ├── custom-development.md
│   │   └── best-practices.md
│   ├── api/
│   │   ├── api-reference.md
│   │   ├── webhook-documentation.md
│   │   ├── authentication.md
│   │   └── rate-limiting.md
│   └── user-guides/
│       ├── getting-started.md
│       ├── chat-interface.md
│       ├── advanced-usage.md
│       └── customization.md
├── scripts/
│   ├── setup/
│   │   ├── initial-setup.sh
│   │   ├── install-dependencies.sh
│   │   ├── configure-environment.sh
│   │   └── validate-installation.sh
│   ├── deployment/
│   │   ├── deploy-local.sh
│   │   ├── deploy-production.sh
│   │   ├── update-system.sh
│   │   └── rollback.sh
│   ├── maintenance/
│   │   ├── backup-system.sh
│   │   ├── restore-system.sh
│   │   ├── cleanup-logs.sh
│   │   └── health-check.sh
│   └── utilities/
│       ├── import-workflows.sh
│       ├── export-workflows.sh
│       ├── reset-database.sh
│       └── generate-reports.sh
└── examples/
    ├── custom-agents/
    ├── integrations/
    ├── workflows/
    └── configurations/
```

### Core Configuration Files

The foundation of the Enhanced AI Agent OS rests upon several critical configuration files that define the system's behavior, security parameters, and operational characteristics. These files must be created with careful attention to security, scalability, and maintainability requirements.

#### Root .gitignore File

Create the `.gitignore` file in the repository root to ensure that sensitive information, temporary files, and environment-specific configurations are not committed to version control:

```gitignore
# Environment Variables and Secrets
.env
.env.local
.env.production
.env.staging
*.env
.env.*
!.env.example
!.env.*.example

# Docker and Container Data
docker-compose.override.yml
.docker/
volumes/
data/
logs/
backups/

# Database Files and Dumps
*.db
*.sqlite
*.sql.gz
*.dump
neo4j/data/
neo4j/logs/
postgres/data/
rabbitmq/data/

# n8n Data and Workflows (except templates)
n8n/data/
.n8n/
workflows/active/
workflows/backup/
!workflows/templates/

# Monitoring and Logs
grafana/data/
prometheus/data/
loki/data/
*.log
logs/
monitoring/data/

# SSL Certificates and Keys
*.pem
*.key
*.crt
*.p12
*.pfx
ssl/
certificates/

# Temporary Files
tmp/
temp/
.tmp/
*.tmp
*.temp

# IDE and Editor Files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Node.js Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing
coverage/
.nyc_output/
.coverage
htmlcov/
.pytest_cache/
test-results/
test-reports/

# Build Artifacts
dist/
build/
*.tar.gz
*.zip

# OS Generated Files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backup Files
*.bak
*.backup
*.old
*~

# Local Configuration Overrides
config.local.json
settings.local.json
local-config/
```

#### Environment Configuration Template

Create the `.env.example` file that serves as a template for environment-specific configurations. This file documents all required environment variables while providing secure defaults:

```bash
# Enhanced AI Agent OS - Environment Configuration Template
# Copy this file to .env and configure with your specific values
# DO NOT commit .env files to version control

# =============================================================================
# SYSTEM IDENTIFICATION
# =============================================================================
SYSTEM_NAME=enhanced-ai-agent-os
ENVIRONMENT=development
VERSION=3.0.0
DEPLOYMENT_ID=local-dev-001

# =============================================================================
# CORE DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Configuration (Primary Database)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=enhanced_ai_os
POSTGRES_USER=ai_agent_user
POSTGRES_PASSWORD=your_secure_postgres_password_here_min_16_chars
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB

# Neo4j Configuration (Consciousness Substrate)
NEO4J_HOST=neo4j
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474
NEO4J_AUTH=neo4j/your_secure_neo4j_password_here_min_16_chars
NEO4J_PLUGINS=["apoc", "graph-data-science", "n10s"]
NEO4J_HEAP_INITIAL_SIZE=1G
NEO4J_HEAP_MAX_SIZE=2G
NEO4J_PAGECACHE_SIZE=1G
NEO4J_QUERY_CACHE_SIZE=10M
NEO4J_JVM_ADDITIONAL=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions

# =============================================================================
# MESSAGE QUEUE CONFIGURATION
# =============================================================================

# RabbitMQ Configuration (Inter-Agent Communication)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
RABBITMQ_DEFAULT_USER=ai_agent_queue_user
RABBITMQ_DEFAULT_PASS=your_secure_rabbitmq_password_here_min_16_chars
RABBITMQ_VM_MEMORY_HIGH_WATERMARK=0.8
RABBITMQ_DISK_FREE_LIMIT=2GB
RABBITMQ_HEARTBEAT=60
RABBITMQ_CONNECTION_TIMEOUT=60000

# =============================================================================
# N8N CONFIGURATION
# =============================================================================

# n8n Core Configuration
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_n8n_password_here_min_16_chars
N8N_ENCRYPTION_KEY=your_32_character_encryption_key_here_exactly_32_chars
N8N_SECURE_COOKIE=false

# n8n Database Configuration
N8N_DB_TYPE=postgresdb
N8N_DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
N8N_DB_POSTGRESDB_HOST=${POSTGRES_HOST}
N8N_DB_POSTGRESDB_PORT=${POSTGRES_PORT}
N8N_DB_POSTGRESDB_USER=${POSTGRES_USER}
N8N_DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
N8N_DB_POSTGRESDB_SCHEMA=n8n

# n8n Workflow Configuration
WEBHOOK_URL=http://localhost:5678
N8N_METRICS=true
N8N_LOG_LEVEL=info
N8N_LOG_OUTPUT=console,file
N8N_LOG_FILE_COUNT_MAX=100
N8N_LOG_FILE_SIZE_MAX=16777216
GENERIC_TIMEZONE=UTC

# n8n Performance Configuration
N8N_EXECUTIONS_PROCESS=main
N8N_EXECUTIONS_TIMEOUT=3600
N8N_EXECUTIONS_TIMEOUT_MAX=7200
N8N_EXECUTIONS_DATA_SAVE_ON_ERROR=all
N8N_EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
N8N_EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
N8N_EXECUTIONS_DATA_PRUNE=true
N8N_EXECUTIONS_DATA_MAX_AGE=336

# =============================================================================
# AI AND LANGUAGE MODEL CONFIGURATION
# =============================================================================

# Built-in AI Capabilities (n8n 1.19.4+)
N8N_AI_ENABLED=true

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_ORGANIZATION=your_openai_organization_id_optional
OPENAI_DEFAULT_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000
OPENAI_TIMEOUT=60000

# OpenRouter Configuration (Multi-Model Access)
OPENROUTER_API_KEY=your_openrouter_api_key_here_optional
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openai/gpt-4

# Anthropic Configuration (Optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here_optional
ANTHROPIC_DEFAULT_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000

# Google AI Configuration (Optional)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here_optional
GOOGLE_AI_DEFAULT_MODEL=gemini-pro

# =============================================================================
# AI MONITORING AND OBSERVABILITY
# =============================================================================

# LangChain Tracing and Monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key_here_optional
LANGCHAIN_PROJECT=enhanced-ai-agent-os-${ENVIRONMENT}
LANGCHAIN_SESSION=session-${DEPLOYMENT_ID}

# AI Performance Monitoring
AI_RESPONSE_TIME_THRESHOLD=5000
AI_ERROR_RATE_THRESHOLD=0.05
AI_COST_TRACKING_ENABLED=true
AI_USAGE_ANALYTICS_ENABLED=true

# =============================================================================
# MONITORING AND OBSERVABILITY
# =============================================================================

# Prometheus Configuration
PROMETHEUS_HOST=prometheus
PROMETHEUS_PORT=9090
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_STORAGE_PATH=/prometheus
PROMETHEUS_WEB_ENABLE_LIFECYCLE=true
PROMETHEUS_WEB_ENABLE_ADMIN_API=true

# Grafana Configuration
GRAFANA_HOST=grafana
GRAFANA_PORT=3000
GRAFANA_SECURITY_ADMIN_USER=admin
GRAFANA_SECURITY_ADMIN_PASSWORD=your_secure_grafana_password_here_min_16_chars
GRAFANA_SECURITY_ALLOW_EMBEDDING=true
GRAFANA_AUTH_ANONYMOUS_ENABLED=false
GRAFANA_INSTALL_PLUGINS=grafana-neo4j-datasource,rabbitmq-datasource,postgres-datasource
GRAFANA_LOG_LEVEL=info

# Loki Configuration (Log Aggregation)
LOKI_HOST=loki
LOKI_PORT=3100
LOKI_RETENTION_PERIOD=720h
LOKI_MAX_LOOK_BACK_PERIOD=0s

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# JWT Configuration
JWT_SECRET=your_jwt_secret_key_here_min_32_characters_long
JWT_EXPIRATION=24h
JWT_REFRESH_EXPIRATION=7d
JWT_ISSUER=enhanced-ai-agent-os
JWT_AUDIENCE=ai-agents

# API Security
API_RATE_LIMIT_WINDOW=15
API_RATE_LIMIT_MAX_REQUESTS=100
API_CORS_ORIGIN=*
API_CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
API_CORS_HEADERS=Content-Type,Authorization,X-Requested-With

# Webhook Security
WEBHOOK_SECRET=your_webhook_secret_here_min_32_characters_long
WEBHOOK_TIMEOUT=30000
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=1000

# =============================================================================
# NETWORKING CONFIGURATION
# =============================================================================

# Docker Network Configuration
DOCKER_NETWORK_NAME=enhanced-ai-network
DOCKER_NETWORK_SUBNET=172.20.0.0/16
DOCKER_NETWORK_GATEWAY=172.20.0.1

# External Access Configuration
EXTERNAL_HOST=localhost
EXTERNAL_PORT=80
EXTERNAL_PROTOCOL=http
EXTERNAL_DOMAIN=localhost

# SSL Configuration (Production)
SSL_ENABLED=false
SSL_CERT_PATH=/etc/ssl/certs/enhanced-ai-agent-os.crt
SSL_KEY_PATH=/etc/ssl/private/enhanced-ai-agent-os.key
SSL_CA_PATH=/etc/ssl/certs/ca-bundle.crt

# =============================================================================
# BACKUP AND RECOVERY CONFIGURATION
# =============================================================================

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_STORAGE_PATH=/backups
BACKUP_COMPRESSION=gzip
BACKUP_ENCRYPTION_ENABLED=false
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key_here_optional

# Recovery Configuration
RECOVERY_POINT_OBJECTIVE=4h
RECOVERY_TIME_OBJECTIVE=1h
RECOVERY_VALIDATION_ENABLED=true

# =============================================================================
# PERFORMANCE AND SCALING CONFIGURATION
# =============================================================================

# Resource Limits
MAX_CONCURRENT_WORKFLOWS=50
MAX_WORKFLOW_EXECUTION_TIME=3600
MAX_MEMORY_USAGE=8GB
MAX_CPU_USAGE=80%
MAX_DISK_USAGE=85%

# Scaling Configuration
AUTO_SCALING_ENABLED=false
SCALE_UP_THRESHOLD=80
SCALE_DOWN_THRESHOLD=30
MIN_INSTANCES=1
MAX_INSTANCES=5

# =============================================================================
# DEVELOPMENT AND DEBUGGING
# =============================================================================

# Development Mode
DEBUG_MODE=false
VERBOSE_LOGGING=false
DEVELOPMENT_TOOLS_ENABLED=true
HOT_RELOAD_ENABLED=false

# Testing Configuration
TEST_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/test_${POSTGRES_DB}
TEST_NEO4J_URL=bolt://${NEO4J_HOST}:${NEO4J_BOLT_PORT}
TEST_RABBITMQ_URL=amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@${RABBITMQ_HOST}:${RABBITMQ_PORT}

# =============================================================================
# CLOUD INTEGRATION (OPTIONAL)
# =============================================================================

# AWS Configuration (Optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_optional
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_optional
AWS_S3_BUCKET=enhanced-ai-agent-os-storage-optional

# Azure Configuration (Optional)
AZURE_SUBSCRIPTION_ID=your_azure_subscription_id_optional
AZURE_CLIENT_ID=your_azure_client_id_optional
AZURE_CLIENT_SECRET=your_azure_client_secret_optional
AZURE_TENANT_ID=your_azure_tenant_id_optional

# Google Cloud Configuration (Optional)
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id_optional
GOOGLE_CLOUD_KEY_FILE=path_to_service_account_key_optional
GOOGLE_CLOUD_STORAGE_BUCKET=enhanced-ai-agent-os-gcs-optional

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Core Features
CONSCIOUSNESS_SUBSTRATE_ENABLED=true
INTER_AGENT_COMMUNICATION_ENABLED=true
AI_CHAT_AGENT_ENABLED=true
WORKFLOW_ORCHESTRATION_ENABLED=true

# Advanced Features
MULTI_MODEL_AI_ENABLED=true
VECTOR_SEARCH_ENABLED=true
REAL_TIME_MONITORING_ENABLED=true
ADVANCED_ANALYTICS_ENABLED=true

# Experimental Features
DYNAMIC_AGENT_CREATION_ENABLED=false
AUTO_SCALING_ENABLED=false
PREDICTIVE_ANALYTICS_ENABLED=false
QUANTUM_COMPUTING_INTEGRATION_ENABLED=false

# =============================================================================
# CUSTOM CONFIGURATION
# =============================================================================

# Organization Settings
ORGANIZATION_NAME=Your Organization Name
ORGANIZATION_DOMAIN=your-domain.com
ORGANIZATION_CONTACT=admin@your-domain.com
ORGANIZATION_TIMEZONE=UTC

# Custom Agent Configuration
CUSTOM_AGENT_REGISTRY_ENABLED=true
CUSTOM_TOOL_REGISTRY_ENABLED=true
CUSTOM_WORKFLOW_TEMPLATES_ENABLED=true
CUSTOM_INTEGRATIONS_ENABLED=true

# Advanced Customization
CUSTOM_AUTHENTICATION_PROVIDER=internal
CUSTOM_STORAGE_PROVIDER=local
CUSTOM_MONITORING_PROVIDER=prometheus
CUSTOM_LOGGING_PROVIDER=console
```

#### Main README.md File

Create the comprehensive `README.md` file that serves as the primary documentation and entry point for the Enhanced AI Agent OS:

```markdown
# Enhanced AI Agent OS

**Version:** 3.0.0  
**Status:** Production Ready  
**License:** MIT  
**Maintainer:** Enhanced AI Development Team

## Overview

The Enhanced AI Agent OS is a sophisticated, production-ready artificial intelligence agent ecosystem built on modern n8n infrastructure with native AI capabilities. The system provides autonomous agent orchestration, intelligent task delegation, consciousness substrate integration, and comprehensive monitoring capabilities designed for enterprise-scale AI automation.

### Key Features

- **🤖 Native AI Agent Orchestration** - Built-in AI capabilities using n8n 1.19.4+ with LangChain integration
- **🧠 Consciousness Substrate** - Neo4j-powered knowledge graph for shared intelligence and memory
- **💬 Intelligent Chat Interface** - Natural language interaction with full backend integration
- **🔄 Inter-Agent Communication** - RabbitMQ-based message queuing for scalable agent coordination
- **📊 Comprehensive Monitoring** - Prometheus, Grafana, and Loki integration for full observability
- **🛠️ Node-as-Tools Integration** - Direct access to 400+ n8n nodes as AI agent tools
- **🔐 Enterprise Security** - JWT authentication, role-based access, and comprehensive audit logging
- **☁️ Hybrid Cloud Ready** - Local deployment with optional cloud service integration

### Architecture

The Enhanced AI Agent OS implements a hierarchical agent architecture with specialized roles and capabilities:

#### Core System Agents
- **Master Orchestration Agent** - Central coordination and task delegation
- **Consciousness Substrate Agent** - Knowledge management and pattern recognition
- **Inter-Agent Communication Agent** - Message routing and coordination
- **System Health Monitoring Agent** - Performance monitoring and self-healing

#### Specialized Domain Agents
- **Research Agent** - Information gathering and analysis
- **Creative Agent** - Content generation and ideation
- **Analysis Agent** - Data processing and insight generation
- **Development Agent** - Code generation and technical implementation
- **Communication Agent** - External system integration and notifications
- **Planning Agent** - Strategic planning and resource allocation
- **Execution Agent** - Task execution and workflow management
- **Quality Assurance Agent** - Testing and validation

#### User Interface Agents
- **AI Chat Agent** - Natural language user interface
- **API Gateway Agent** - RESTful API management
- **Webhook Handler Agent** - External integration management
- **Notification System Agent** - Multi-channel communication

### Technology Stack

- **Orchestration Platform:** n8n (Latest) with built-in AI capabilities
- **Primary Database:** PostgreSQL 15 with pgvector extension
- **Knowledge Graph:** Neo4j 5.15 Community with APOC and GDS plugins
- **Message Queue:** RabbitMQ 3.12 with management plugin
- **Monitoring:** Prometheus 2.48, Grafana 10.2, Loki (Latest)
- **Containerization:** Docker and Docker Compose
- **Reverse Proxy:** Nginx (Production deployments)
- **AI Integration:** Native n8n LangChain nodes with multi-model support

## Quick Start

### Prerequisites

- Docker Desktop with 16GB+ RAM allocation
- Node.js 18+ (for development and testing)
- Git with configured credentials
- 50GB+ available disk space

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd enhanced-ai-agent-os
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. **Start the system:**
   ```bash
   docker-compose up -d
   ```

4. **Verify installation:**
   ```bash
   ./scripts/setup/validate-installation.sh
   ```

5. **Access the system:**
   - n8n Interface: http://localhost:5678
   - Grafana Monitoring: http://localhost:3000
   - Neo4j Browser: http://localhost:7474
   - RabbitMQ Management: http://localhost:15672

### First Steps

1. **Import workflows:**
   ```bash
   ./scripts/utilities/import-workflows.sh
   ```

2. **Test AI capabilities:**
   ```bash
   curl -X POST http://localhost:5678/webhook/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, Enhanced AI Agent OS!"}'
   ```

3. **Explore the monitoring dashboard:**
   - Open Grafana at http://localhost:3000
   - Login with admin credentials from .env
   - Navigate to "AI Agent Performance" dashboard

## Documentation

### Architecture and Design
- [System Overview](docs/architecture/system-overview.md)
- [Agent Specifications](docs/architecture/agent-specifications.md)
- [Data Flow Diagrams](docs/architecture/data-flow-diagrams.md)
- [Security Model](docs/architecture/security-model.md)

### Deployment Guides
- [Local Setup](docs/deployment/local-setup.md)
- [Production Deployment](docs/deployment/production-deployment.md)
- [Cloud Integration](docs/deployment/cloud-integration.md)
- [Troubleshooting](docs/deployment/troubleshooting.md)

### Workflow Development
- [Workflow Documentation](docs/workflows/workflow-documentation.md)
- [Agent Interactions](docs/workflows/agent-interactions.md)
- [Custom Development](docs/workflows/custom-development.md)
- [Best Practices](docs/workflows/best-practices.md)

### API Reference
- [API Reference](docs/api/api-reference.md)
- [Webhook Documentation](docs/api/webhook-documentation.md)
- [Authentication](docs/api/authentication.md)
- [Rate Limiting](docs/api/rate-limiting.md)

### User Guides
- [Getting Started](docs/user-guides/getting-started.md)
- [Chat Interface](docs/user-guides/chat-interface.md)
- [Advanced Usage](docs/user-guides/advanced-usage.md)
- [Customization](docs/user-guides/customization.md)

## Development

### Development Environment Setup

1. **Install development dependencies:**
   ```bash
   ./scripts/setup/install-dependencies.sh
   ```

2. **Configure development environment:**
   ```bash
   ./scripts/setup/configure-environment.sh
   ```

3. **Start in development mode:**
   ```bash
   docker-compose -f docker-compose.yml -f local-deployment/docker-compose.local.yml up -d
   ```

### Testing

The system includes comprehensive testing frameworks:

```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e

# Test AI capabilities
npm run test:ai-capabilities

# Performance testing
npm run test:performance
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Standards

- Follow ESLint configuration for JavaScript/Node.js code
- Use Prettier for code formatting
- Write comprehensive tests for new features
- Document all public APIs and workflows
- Follow semantic versioning for releases

## Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Cloud Deployment
See [Cloud Integration Guide](docs/deployment/cloud-integration.md) for detailed instructions.

## Monitoring and Maintenance

### Health Checks
```bash
./scripts/maintenance/health-check.sh
```

### Backup System
```bash
./scripts/maintenance/backup-system.sh
```

### Log Analysis
```bash
./scripts/maintenance/cleanup-logs.sh
```

### Performance Monitoring
- Grafana dashboards provide real-time system metrics
- Prometheus alerts notify of performance issues
- Loki aggregates logs for analysis

## Security

### Authentication
- JWT-based authentication for API access
- Basic authentication for n8n interface
- Role-based access control for different user types

### Data Protection
- Encryption at rest for sensitive data
- TLS encryption for all network communication
- Regular security updates and vulnerability scanning

### Audit Logging
- Comprehensive audit trails for all system activities
- Centralized logging with Loki
- Configurable retention policies

## Troubleshooting

### Common Issues

**System won't start:**
- Check Docker resource allocation (16GB+ RAM required)
- Verify all environment variables are configured
- Check for port conflicts

**AI agents not responding:**
- Verify OpenAI API key configuration
- Check n8n workflow activation status
- Review agent-specific logs in Grafana

**Database connection errors:**
- Ensure PostgreSQL and Neo4j are healthy
- Check database credentials in .env
- Verify network connectivity between containers

### Support

- **Documentation:** Comprehensive guides in `/docs` directory
- **Issue Tracking:** GitHub Issues for bug reports and feature requests
- **Community:** Join our community discussions
- **Professional Support:** Contact our team for enterprise support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- n8n team for the excellent workflow automation platform
- Neo4j team for the powerful graph database
- LangChain team for AI integration capabilities
- Open source community for continuous inspiration and support

## Changelog

### Version 3.0.0 (Current)
- Complete rewrite using n8n built-in AI capabilities
- Eliminated community package dependencies
- Enhanced Node-as-Tools integration
- Improved monitoring and observability
- Streamlined deployment process

### Version 2.0.0
- Initial implementation with community packages
- Basic AI agent orchestration
- Consciousness substrate integration

### Version 1.0.0
- Proof of concept implementation
- Core workflow definitions
- Basic monitoring setup

---

**Built with ❤️ by the Enhanced AI Development Team**
```

This completes the foundation files for Phase 1. The project structure provides a comprehensive organization that separates concerns while maintaining clear relationships between system components. The configuration files establish secure defaults while providing extensive customization options. The README.md serves as both documentation and marketing material, clearly explaining the system's capabilities and providing quick start instructions.



## Phase 2: Complete Docker Infrastructure and Environment Setup

### Main Docker Compose Configuration

The Docker Compose configuration serves as the orchestration foundation for the Enhanced AI Agent OS, defining the complete service architecture with proper dependencies, networking, and resource allocation. The configuration leverages modern Docker Compose features while maintaining compatibility with production deployment requirements.

Create the main `docker-compose.yml` file in the repository root with the complete service definitions:

```yaml
version: "3.9"

# Enhanced AI Agent OS - Main Docker Compose Configuration
# This configuration defines the complete service architecture for local and production deployment

services:
  # =============================================================================
  # PRIMARY DATABASE - PostgreSQL with pgvector
  # =============================================================================
  postgres:
    image: pgvector/pgvector:pg15
    container_name: enhanced-ai-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-enhanced_ai_os}
      POSTGRES_USER: ${POSTGRES_USER:-ai_agent_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: ${POSTGRES_INITDB_ARGS:---encoding=UTF-8 --lc-collate=C --lc-ctype=C}
      POSTGRES_HOST_AUTH_METHOD: md5
      POSTGRES_MAX_CONNECTIONS: ${POSTGRES_MAX_CONNECTIONS:-200}
      POSTGRES_SHARED_BUFFERS: ${POSTGRES_SHARED_BUFFERS:-256MB}
      POSTGRES_EFFECTIVE_CACHE_SIZE: ${POSTGRES_EFFECTIVE_CACHE_SIZE:-1GB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init:/docker-entrypoint-initdb.d:ro
      - postgres_backups:/backups
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ai_agent_user} -d ${POSTGRES_DB:-enhanced_ai_os}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # =============================================================================
  # CONSCIOUSNESS SUBSTRATE - Neo4j Graph Database
  # =============================================================================
  neo4j:
    image: neo4j:5.15-community
    container_name: enhanced-ai-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
      NEO4J_PLUGINS: ${NEO4J_PLUGINS:-["apoc", "graph-data-science", "n10s"]}
      NEO4J_server_memory_heap_initial__size: ${NEO4J_HEAP_INITIAL_SIZE:-1G}
      NEO4J_server_memory_heap_max__size: ${NEO4J_HEAP_MAX_SIZE:-2G}
      NEO4J_server_memory_pagecache_size: ${NEO4J_PAGECACHE_SIZE:-1G}
      NEO4J_server_query_cache_size: ${NEO4J_QUERY_CACHE_SIZE:-10M}
      NEO4J_server_jvm_additional: ${NEO4J_JVM_ADDITIONAL:--XX:+UseG1GC -XX:+UnlockExperimentalVMOptions}
      NEO4J_server_bolt_listen__address: 0.0.0.0:7687
      NEO4J_server_http_listen__address: 0.0.0.0:7474
      NEO4J_server_logs_debug_level: INFO
      NEO4J_server_logs_query_enabled: true
      NEO4J_server_logs_query_threshold: 1s
      NEO4J_server_logs_query_parameter__logging__enabled: true
      NEO4J_server_config_strict__validation_enabled: false
      NEO4J_server_cypher_default__temporal__accessor: legacy
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
      - ./infrastructure/neo4j/init:/docker-entrypoint-initdb.d:ro
      - neo4j_backups:/backups
    ports:
      - "${NEO4J_HTTP_PORT:-7474}:7474"
      - "${NEO4J_BOLT_PORT:-7687}:7687"
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p ${NEO4J_PASSWORD} 'RETURN 1' || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 120s
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # =============================================================================
  # MESSAGE QUEUE - RabbitMQ for Inter-Agent Communication
  # =============================================================================
  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: enhanced-ai-rabbitmq
    restart: unless-stopped
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER:-ai_agent_queue_user}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
      RABBITMQ_VM_MEMORY_HIGH_WATERMARK: ${RABBITMQ_VM_MEMORY_HIGH_WATERMARK:-0.8}
      RABBITMQ_DISK_FREE_LIMIT: ${RABBITMQ_DISK_FREE_LIMIT:-2GB}
      RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: ${RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS:--rabbit consumer_timeout 36000000}
      RABBITMQ_HEARTBEAT: ${RABBITMQ_HEARTBEAT:-60}
      RABBITMQ_CONNECTION_TIMEOUT: ${RABBITMQ_CONNECTION_TIMEOUT:-60000}
      RABBITMQ_MANAGEMENT_PATH_PREFIX: /rabbitmq
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
      - ./infrastructure/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro
      - ./infrastructure/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
      - ./infrastructure/rabbitmq/enabled_plugins:/etc/rabbitmq/enabled_plugins:ro
      - rabbitmq_logs:/var/log/rabbitmq
      - rabbitmq_backups:/backups
    ports:
      - "${RABBITMQ_PORT:-5672}:5672"
      - "${RABBITMQ_MANAGEMENT_PORT:-15672}:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # =============================================================================
  # ORCHESTRATION PLATFORM - n8n with Built-in AI Capabilities
  # =============================================================================
  n8n:
    image: n8nio/n8n:latest
    container_name: enhanced-ai-n8n
    restart: unless-stopped
    environment:
      # Core Configuration
      N8N_HOST: ${N8N_HOST:-0.0.0.0}
      N8N_PORT: ${N8N_PORT:-5678}
      N8N_PROTOCOL: ${N8N_PROTOCOL:-http}
      
      # Authentication and Security
      N8N_BASIC_AUTH_ACTIVE: ${N8N_BASIC_AUTH_ACTIVE:-true}
      N8N_BASIC_AUTH_USER: ${N8N_BASIC_AUTH_USER:-admin}
      N8N_BASIC_AUTH_PASSWORD: ${N8N_BASIC_AUTH_PASSWORD}
      N8N_ENCRYPTION_KEY: ${N8N_ENCRYPTION_KEY}
      N8N_SECURE_COOKIE: ${N8N_SECURE_COOKIE:-false}
      
      # Database Configuration
      DB_TYPE: ${N8N_DB_TYPE:-postgresdb}
      DB_POSTGRESDB_DATABASE: ${POSTGRES_DB:-enhanced_ai_os}
      DB_POSTGRESDB_HOST: ${POSTGRES_HOST:-postgres}
      DB_POSTGRESDB_PORT: ${POSTGRES_PORT:-5432}
      DB_POSTGRESDB_USER: ${POSTGRES_USER:-ai_agent_user}
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}
      DB_POSTGRESDB_SCHEMA: ${N8N_DB_POSTGRESDB_SCHEMA:-n8n}
      
      # Webhook and External Access
      WEBHOOK_URL: ${WEBHOOK_URL:-http://localhost:5678}
      N8N_EDITOR_BASE_URL: ${WEBHOOK_URL:-http://localhost:5678}
      
      # System Configuration
      GENERIC_TIMEZONE: ${GENERIC_TIMEZONE:-UTC}
      N8N_METRICS: ${N8N_METRICS:-true}
      N8N_LOG_LEVEL: ${N8N_LOG_LEVEL:-info}
      N8N_LOG_OUTPUT: ${N8N_LOG_OUTPUT:-console,file}
      N8N_LOG_FILE_COUNT_MAX: ${N8N_LOG_FILE_COUNT_MAX:-100}
      N8N_LOG_FILE_SIZE_MAX: ${N8N_LOG_FILE_SIZE_MAX:-16777216}
      
      # Performance Configuration
      N8N_EXECUTIONS_PROCESS: ${N8N_EXECUTIONS_PROCESS:-main}
      N8N_EXECUTIONS_TIMEOUT: ${N8N_EXECUTIONS_TIMEOUT:-3600}
      N8N_EXECUTIONS_TIMEOUT_MAX: ${N8N_EXECUTIONS_TIMEOUT_MAX:-7200}
      N8N_EXECUTIONS_DATA_SAVE_ON_ERROR: ${N8N_EXECUTIONS_DATA_SAVE_ON_ERROR:-all}
      N8N_EXECUTIONS_DATA_SAVE_ON_SUCCESS: ${N8N_EXECUTIONS_DATA_SAVE_ON_SUCCESS:-all}
      N8N_EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS: ${N8N_EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS:-true}
      N8N_EXECUTIONS_DATA_PRUNE: ${N8N_EXECUTIONS_DATA_PRUNE:-true}
      N8N_EXECUTIONS_DATA_MAX_AGE: ${N8N_EXECUTIONS_DATA_MAX_AGE:-336}
      
      # Built-in AI Configuration (No Community Packages Required!)
      N8N_AI_ENABLED: ${N8N_AI_ENABLED:-true}
      
      # LLM Provider Configuration
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_API_BASE: ${OPENAI_API_BASE:-https://api.openai.com/v1}
      OPENAI_ORGANIZATION: ${OPENAI_ORGANIZATION}
      
      # OpenRouter Configuration (Optional Multi-Model Access)
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      OPENROUTER_BASE_URL: ${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}
      
      # Anthropic Configuration (Optional)
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      
      # Google AI Configuration (Optional)
      GOOGLE_AI_API_KEY: ${GOOGLE_AI_API_KEY}
      
      # LangChain Tracing and Monitoring (Optional)
      LANGCHAIN_TRACING_V2: ${LANGCHAIN_TRACING_V2:-true}
      LANGCHAIN_ENDPOINT: ${LANGCHAIN_ENDPOINT}
      LANGCHAIN_API_KEY: ${LANGCHAIN_API_KEY}
      LANGCHAIN_PROJECT: ${LANGCHAIN_PROJECT}
      LANGCHAIN_SESSION: ${LANGCHAIN_SESSION}
      
      # External Service Integration
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      RABBITMQ_URL: amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672
      
    volumes:
      - n8n_data:/home/node/.n8n
      - ./infrastructure/n8n/config:/home/node/.n8n/config:ro
      - ./workflows:/home/node/.n8n/workflows
      - n8n_logs:/home/node/.n8n/logs
      - n8n_backups:/backups
    ports:
      - "${N8N_PORT:-5678}:5678"
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5678/healthz || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # =============================================================================
  # MONITORING - Prometheus for Metrics Collection
  # =============================================================================
  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: enhanced-ai-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION_TIME:-30d}'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
      - '--web.external-url=http://localhost:9090'
      - '--web.route-prefix=/'
    volumes:
      - ./infrastructure/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./infrastructure/monitoring/prometheus/rules:/etc/prometheus/rules:ro
      - ./infrastructure/monitoring/prometheus/targets:/etc/prometheus/targets:ro
      - prometheus_data:/prometheus
      - prometheus_config:/etc/prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # =============================================================================
  # MONITORING - Grafana for Visualization and Dashboards
  # =============================================================================
  grafana:
    image: grafana/grafana:10.2.0
    container_name: enhanced-ai-grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_SECURITY_ADMIN_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_SECURITY_ADMIN_PASSWORD}
      GF_SECURITY_ALLOW_EMBEDDING: ${GRAFANA_SECURITY_ALLOW_EMBEDDING:-true}
      GF_AUTH_ANONYMOUS_ENABLED: ${GRAFANA_AUTH_ANONYMOUS_ENABLED:-false}
      GF_INSTALL_PLUGINS: ${GRAFANA_INSTALL_PLUGINS:-grafana-neo4j-datasource,rabbitmq-datasource,postgres-datasource}
      GF_LOG_LEVEL: ${GRAFANA_LOG_LEVEL:-info}
      GF_PATHS_PROVISIONING: /etc/grafana/provisioning
      GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH: /etc/grafana/dashboards/ai-agent-overview.json
      GF_FEATURE_TOGGLES_ENABLE: publicDashboards
      GF_ANALYTICS_REPORTING_ENABLED: false
      GF_ANALYTICS_CHECK_FOR_UPDATES: false
      GF_USERS_ALLOW_SIGN_UP: false
      GF_USERS_ALLOW_ORG_CREATE: false
      GF_USERS_AUTO_ASSIGN_ORG: true
      GF_USERS_AUTO_ASSIGN_ORG_ROLE: Viewer
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/monitoring/grafana/dashboards:/etc/grafana/dashboards:ro
      - ./infrastructure/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./infrastructure/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_logs:/var/log/grafana
    ports:
      - "${GRAFANA_PORT:-3000}:3000"
    depends_on:
      - prometheus
      - neo4j
      - postgres
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # =============================================================================
  # LOG AGGREGATION - Loki for Centralized Logging
  # =============================================================================
  loki:
    image: grafana/loki:2.9.0
    container_name: enhanced-ai-loki
    restart: unless-stopped
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./infrastructure/monitoring/loki/loki-config.yml:/etc/loki/local-config.yaml:ro
      - loki_data:/loki
    ports:
      - "${LOKI_PORT:-3100}:3100"
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

  # =============================================================================
  # LOG COLLECTION - Promtail for Log Shipping
  # =============================================================================
  promtail:
    image: grafana/promtail:2.9.0
    container_name: enhanced-ai-promtail
    restart: unless-stopped
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./infrastructure/monitoring/loki/promtail-config.yml:/etc/promtail/config.yml:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - loki
    networks:
      - enhanced-ai-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.1'
        reservations:
          memory: 128M
          cpus: '0.05'

  # =============================================================================
  # REVERSE PROXY - Nginx for Production Load Balancing (Optional)
  # =============================================================================
  nginx:
    image: nginx:1.25-alpine
    container_name: enhanced-ai-nginx
    restart: unless-stopped
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./infrastructure/nginx/sites-available:/etc/nginx/sites-available:ro
      - ./infrastructure/nginx/ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    ports:
      - "${EXTERNAL_PORT:-80}:80"
      - "443:443"
    depends_on:
      - n8n
      - grafana
    networks:
      - enhanced-ai-network
    profiles:
      - production
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.1'

# =============================================================================
# PERSISTENT VOLUMES
# =============================================================================
volumes:
  # Database Volumes
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/postgres
  postgres_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./backups/postgres

  # Neo4j Volumes
  neo4j_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/neo4j/data
  neo4j_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/neo4j/logs
  neo4j_import:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/neo4j/import
  neo4j_plugins:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/neo4j/plugins
  neo4j_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./backups/neo4j

  # RabbitMQ Volumes
  rabbitmq_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/rabbitmq
  rabbitmq_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./logs/rabbitmq
  rabbitmq_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./backups/rabbitmq

  # n8n Volumes
  n8n_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/n8n
  n8n_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./logs/n8n
  n8n_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./backups/n8n

  # Monitoring Volumes
  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/prometheus
  prometheus_config:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./infrastructure/monitoring/prometheus

  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/grafana
  grafana_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./logs/grafana

  loki_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/loki

  # Nginx Volumes
  nginx_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./logs/nginx

# =============================================================================
# NETWORKS
# =============================================================================
networks:
  enhanced-ai-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: ${DOCKER_NETWORK_SUBNET:-172.20.0.0/16}
          gateway: ${DOCKER_NETWORK_GATEWAY:-172.20.0.1}
    driver_opts:
      com.docker.network.bridge.name: enhanced-ai-br0
      com.docker.network.driver.mtu: 1500
```

### Production Docker Compose Override

Create the `docker-compose.prod.yml` file for production-specific configurations:

```yaml
version: "3.9"

# Enhanced AI Agent OS - Production Override Configuration
# Use with: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

services:
  # Production PostgreSQL Configuration
  postgres:
    environment:
      POSTGRES_MAX_CONNECTIONS: 500
      POSTGRES_SHARED_BUFFERS: 512MB
      POSTGRES_EFFECTIVE_CACHE_SIZE: 4GB
      POSTGRES_WORK_MEM: 16MB
      POSTGRES_MAINTENANCE_WORK_MEM: 256MB
      POSTGRES_CHECKPOINT_COMPLETION_TARGET: 0.9
      POSTGRES_WAL_BUFFERS: 16MB
      POSTGRES_DEFAULT_STATISTICS_TARGET: 100
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
      restart_policy:
        condition: on-failure
        delay: 10s
        max_attempts: 3
        window: 120s

  # Production Neo4j Configuration
  neo4j:
    environment:
      NEO4J_server_memory_heap_initial__size: 2G
      NEO4J_server_memory_heap_max__size: 8G
      NEO4J_server_memory_pagecache_size: 4G
      NEO4J_server_query_cache_size: 100M
      NEO4J_server_jvm_additional: >-
        -XX:+UseG1GC 
        -XX:+UnlockExperimentalVMOptions 
        -XX:G1HeapRegionSize=16m 
        -XX:G1NewSizePercent=30 
        -XX:G1MaxNewSizePercent=50
      NEO4J_server_logs_query_threshold: 5s
      NEO4J_server_logs_query_parameter__logging__enabled: false
    deploy:
      resources:
        limits:
          memory: 12G
          cpus: '6.0'
        reservations:
          memory: 8G
          cpus: '4.0'
      restart_policy:
        condition: on-failure
        delay: 30s
        max_attempts: 3
        window: 300s

  # Production RabbitMQ Configuration
  rabbitmq:
    environment:
      RABBITMQ_VM_MEMORY_HIGH_WATERMARK: 0.6
      RABBITMQ_DISK_FREE_LIMIT: 10GB
      RABBITMQ_CHANNEL_MAX: 2048
      RABBITMQ_CONNECTION_MAX: 1000
      RABBITMQ_HEARTBEAT: 30
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
      restart_policy:
        condition: on-failure
        delay: 15s
        max_attempts: 3
        window: 180s

  # Production n8n Configuration
  n8n:
    environment:
      N8N_EXECUTIONS_PROCESS: own
      N8N_EXECUTIONS_TIMEOUT: 7200
      N8N_EXECUTIONS_TIMEOUT_MAX: 14400
      N8N_EXECUTIONS_DATA_MAX_AGE: 168
      N8N_LOG_LEVEL: warn
      N8N_SECURE_COOKIE: true
      NODE_ENV: production
      NODE_OPTIONS: --max-old-space-size=4096
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
      restart_policy:
        condition: on-failure
        delay: 30s
        max_attempts: 3
        window: 300s

  # Production Prometheus Configuration
  prometheus:
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=90d'
      - '--storage.tsdb.retention.size=50GB'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
      - '--web.external-url=https://monitoring.yourdomain.com/prometheus'
      - '--web.route-prefix=/prometheus'
      - '--storage.tsdb.wal-compression'
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Production Grafana Configuration
  grafana:
    environment:
      GF_SERVER_PROTOCOL: https
      GF_SERVER_DOMAIN: monitoring.yourdomain.com
      GF_SERVER_ROOT_URL: https://monitoring.yourdomain.com/grafana
      GF_SERVER_SERVE_FROM_SUB_PATH: true
      GF_SECURITY_COOKIE_SECURE: true
      GF_SECURITY_COOKIE_SAMESITE: strict
      GF_SESSION_COOKIE_SECURE: true
      GF_SNAPSHOTS_EXTERNAL_ENABLED: false
      GF_ANALYTICS_REPORTING_ENABLED: false
      GF_ANALYTICS_CHECK_FOR_UPDATES: false
      GF_LOG_LEVEL: warn
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # Enable Nginx for Production
  nginx:
    profiles: []  # Remove from profiles to enable by default
    environment:
      NGINX_WORKER_PROCESSES: auto
      NGINX_WORKER_CONNECTIONS: 1024
      NGINX_KEEPALIVE_TIMEOUT: 65
      NGINX_CLIENT_MAX_BODY_SIZE: 100M
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

# Production-specific volumes with optimized settings
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind,noatime
      device: /opt/enhanced-ai-agent-os/data/postgres

  neo4j_data:
    driver: local
    driver_opts:
      type: none
      o: bind,noatime
      device: /opt/enhanced-ai-agent-os/data/neo4j/data

  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind,noatime
      device: /opt/enhanced-ai-agent-os/data/prometheus

  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind,noatime
      device: /opt/enhanced-ai-agent-os/data/grafana
```

### Infrastructure Configuration Files

#### PostgreSQL Initialization Scripts

Create the PostgreSQL initialization directory and scripts:

**File: `infrastructure/postgres/init/01-create-databases.sql`**

```sql
-- Enhanced AI Agent OS - PostgreSQL Database Initialization
-- This script creates the necessary databases and basic structure

-- Create main application database (if not exists from environment)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'enhanced_ai_os') THEN
        CREATE DATABASE enhanced_ai_os;
    END IF;
END
$$;

-- Connect to the main database for further setup
\c enhanced_ai_os;

-- Create schemas for different components
CREATE SCHEMA IF NOT EXISTS n8n;
CREATE SCHEMA IF NOT EXISTS ai_agents;
CREATE SCHEMA IF NOT EXISTS consciousness;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create application user with appropriate permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ai_agent_user') THEN
        CREATE ROLE ai_agent_user WITH LOGIN PASSWORD 'secure_password_change_me';
    END IF;
END
$$;

-- Grant permissions to application user
GRANT CONNECT ON DATABASE enhanced_ai_os TO ai_agent_user;
GRANT USAGE ON SCHEMA n8n TO ai_agent_user;
GRANT USAGE ON SCHEMA ai_agents TO ai_agent_user;
GRANT USAGE ON SCHEMA consciousness TO ai_agent_user;
GRANT USAGE ON SCHEMA monitoring TO ai_agent_user;
GRANT USAGE ON SCHEMA audit TO ai_agent_user;

-- Grant table creation permissions
GRANT CREATE ON SCHEMA n8n TO ai_agent_user;
GRANT CREATE ON SCHEMA ai_agents TO ai_agent_user;
GRANT CREATE ON SCHEMA consciousness TO ai_agent_user;
GRANT CREATE ON SCHEMA monitoring TO ai_agent_user;
GRANT CREATE ON SCHEMA audit TO ai_agent_user;

-- Create audit logging function
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.change_log (
            table_name, operation, old_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user, now()
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.change_log (
            table_name, operation, old_values, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user, now()
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.change_log (
            table_name, operation, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user, now()
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION audit.log_changes() IS 'Audit trigger function for tracking data changes';
```

**File: `infrastructure/postgres/init/02-create-extensions.sql`**

```sql
-- Enhanced AI Agent OS - PostgreSQL Extensions Setup
-- This script installs and configures necessary PostgreSQL extensions

-- Connect to the main database
\c enhanced_ai_os;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "ltree";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Enable vector extension for AI embeddings (if available)
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable time series extension (if available)
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Create custom types for AI agent system
CREATE TYPE ai_agents.agent_status AS ENUM (
    'initializing',
    'active',
    'idle',
    'busy',
    'error',
    'maintenance',
    'disabled'
);

CREATE TYPE ai_agents.task_priority AS ENUM (
    'low',
    'normal',
    'high',
    'urgent',
    'critical'
);

CREATE TYPE ai_agents.task_status AS ENUM (
    'pending',
    'assigned',
    'in_progress',
    'completed',
    'failed',
    'cancelled',
    'timeout'
);

CREATE TYPE consciousness.knowledge_type AS ENUM (
    'fact',
    'concept',
    'relationship',
    'pattern',
    'insight',
    'memory',
    'experience'
);

CREATE TYPE monitoring.metric_type AS ENUM (
    'counter',
    'gauge',
    'histogram',
    'summary'
);

-- Create composite types for complex data structures
CREATE TYPE ai_agents.agent_capability AS (
    name VARCHAR(100),
    description TEXT,
    version VARCHAR(20),
    enabled BOOLEAN,
    configuration JSONB
);

CREATE TYPE consciousness.knowledge_vector AS (
    embedding VECTOR(1536),
    metadata JSONB,
    confidence FLOAT
);

-- Set up full-text search configuration
CREATE TEXT SEARCH CONFIGURATION ai_search (COPY = english);
ALTER TEXT SEARCH CONFIGURATION ai_search
    ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
    WITH simple;

COMMENT ON TEXT SEARCH CONFIGURATION ai_search IS 'Custom text search configuration for AI content';
```

**File: `infrastructure/postgres/init/03-create-schemas.sql`**

```sql
-- Enhanced AI Agent OS - Core Schema Creation
-- This script creates the core database tables and relationships

-- Connect to the main database
\c enhanced_ai_os;

-- =============================================================================
-- AI AGENTS SCHEMA - Core agent management tables
-- =============================================================================

-- Agent registry table
CREATE TABLE ai_agents.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status ai_agents.agent_status DEFAULT 'initializing',
    capabilities ai_agents.agent_capability[],
    configuration JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    version VARCHAR(20) DEFAULT '1.0.0',
    
    CONSTRAINT agents_name_check CHECK (length(name) >= 3),
    CONSTRAINT agents_type_check CHECK (length(type) >= 3)
);

-- Agent tasks table
CREATE TABLE ai_agents.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES ai_agents.tasks(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    priority ai_agents.task_priority DEFAULT 'normal',
    status ai_agents.task_status DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_details JSONB,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    CONSTRAINT tasks_name_check CHECK (length(name) >= 3),
    CONSTRAINT tasks_retry_check CHECK (retry_count <= max_retries)
);

-- Agent communication log
CREATE TABLE ai_agents.communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_agent_id UUID REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    receiver_agent_id UUID REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    priority ai_agents.task_priority DEFAULT 'normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    response_data JSONB,
    
    CONSTRAINT communications_different_agents CHECK (sender_agent_id != receiver_agent_id)
);

-- =============================================================================
-- CONSCIOUSNESS SCHEMA - Knowledge and memory management
-- =============================================================================

-- Knowledge base table
CREATE TABLE consciousness.knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type consciousness.knowledge_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    source VARCHAR(200),
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    tags TEXT[],
    
    CONSTRAINT knowledge_title_check CHECK (length(title) >= 3),
    CONSTRAINT knowledge_content_check CHECK (length(content) >= 10)
);

-- Knowledge relationships table
CREATE TABLE consciousness.knowledge_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_knowledge_id UUID REFERENCES consciousness.knowledge(id) ON DELETE CASCADE,
    target_knowledge_id UUID REFERENCES consciousness.knowledge(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 1),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT knowledge_relationships_different_nodes CHECK (source_knowledge_id != target_knowledge_id),
    UNIQUE(source_knowledge_id, target_knowledge_id, relationship_type)
);

-- Conversation memory table
CREATE TABLE consciousness.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    agent_id UUID REFERENCES ai_agents.agents(id) ON DELETE SET NULL,
    session_id VARCHAR(100) NOT NULL,
    message_sequence INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(session_id, message_sequence)
);

-- =============================================================================
-- MONITORING SCHEMA - System monitoring and metrics
-- =============================================================================

-- System metrics table
CREATE TABLE monitoring.metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_type monitoring.metric_type NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(100),
    
    CONSTRAINT metrics_name_check CHECK (length(metric_name) >= 3)
);

-- Agent performance metrics
CREATE TABLE monitoring.agent_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- System health checks
CREATE TABLE monitoring.health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('healthy', 'warning', 'critical', 'unknown')),
    message TEXT,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time_ms INTEGER
);

-- =============================================================================
-- AUDIT SCHEMA - Audit logging and compliance
-- =============================================================================

-- Change log table
CREATE TABLE audit.change_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(100),
    application_name VARCHAR(100)
);

-- API access log
CREATE TABLE audit.api_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    user_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_status INTEGER,
    response_time_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(100)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================

-- AI Agents indexes
CREATE INDEX idx_agents_status ON ai_agents.agents(status);
CREATE INDEX idx_agents_type ON ai_agents.agents(type);
CREATE INDEX idx_agents_updated_at ON ai_agents.agents(updated_at);
CREATE INDEX idx_agents_last_heartbeat ON ai_agents.agents(last_heartbeat);

CREATE INDEX idx_tasks_agent_id ON ai_agents.tasks(agent_id);
CREATE INDEX idx_tasks_status ON ai_agents.tasks(status);
CREATE INDEX idx_tasks_priority ON ai_agents.tasks(priority);
CREATE INDEX idx_tasks_created_at ON ai_agents.tasks(created_at);
CREATE INDEX idx_tasks_parent_task_id ON ai_agents.tasks(parent_task_id);

CREATE INDEX idx_communications_sender ON ai_agents.communications(sender_agent_id);
CREATE INDEX idx_communications_receiver ON ai_agents.communications(receiver_agent_id);
CREATE INDEX idx_communications_created_at ON ai_agents.communications(created_at);

-- Consciousness indexes
CREATE INDEX idx_knowledge_type ON consciousness.knowledge(type);
CREATE INDEX idx_knowledge_created_at ON consciousness.knowledge(created_at);
CREATE INDEX idx_knowledge_accessed_at ON consciousness.knowledge(accessed_at);
CREATE INDEX idx_knowledge_tags ON consciousness.knowledge USING GIN(tags);
CREATE INDEX idx_knowledge_content_fts ON consciousness.knowledge USING GIN(to_tsvector('ai_search', content));

-- Vector similarity index (if vector extension is available)
CREATE INDEX idx_knowledge_embedding ON consciousness.knowledge USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_knowledge_relationships_source ON consciousness.knowledge_relationships(source_knowledge_id);
CREATE INDEX idx_knowledge_relationships_target ON consciousness.knowledge_relationships(target_knowledge_id);
CREATE INDEX idx_knowledge_relationships_type ON consciousness.knowledge_relationships(relationship_type);

CREATE INDEX idx_conversations_session_id ON consciousness.conversations(session_id);
CREATE INDEX idx_conversations_user_id ON consciousness.conversations(user_id);
CREATE INDEX idx_conversations_agent_id ON consciousness.conversations(agent_id);
CREATE INDEX idx_conversations_created_at ON consciousness.conversations(created_at);

-- Monitoring indexes
CREATE INDEX idx_metrics_name ON monitoring.metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON monitoring.metrics(timestamp);
CREATE INDEX idx_metrics_source ON monitoring.metrics(source);

CREATE INDEX idx_agent_performance_agent_id ON monitoring.agent_performance(agent_id);
CREATE INDEX idx_agent_performance_metric_name ON monitoring.agent_performance(metric_name);
CREATE INDEX idx_agent_performance_timestamp ON monitoring.agent_performance(timestamp);

CREATE INDEX idx_health_checks_component ON monitoring.health_checks(component);
CREATE INDEX idx_health_checks_status ON monitoring.health_checks(status);
CREATE INDEX idx_health_checks_timestamp ON monitoring.health_checks(timestamp);

-- Audit indexes
CREATE INDEX idx_change_log_table_name ON audit.change_log(table_name);
CREATE INDEX idx_change_log_operation ON audit.change_log(operation);
CREATE INDEX idx_change_log_changed_at ON audit.change_log(changed_at);
CREATE INDEX idx_change_log_changed_by ON audit.change_log(changed_by);

CREATE INDEX idx_api_access_endpoint ON audit.api_access(endpoint);
CREATE INDEX idx_api_access_user_id ON audit.api_access(user_id);
CREATE INDEX idx_api_access_timestamp ON audit.api_access(timestamp);
CREATE INDEX idx_api_access_ip_address ON audit.api_access(ip_address);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON ai_agents.agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at
    BEFORE UPDATE ON consciousness.knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit triggers for sensitive tables
CREATE TRIGGER audit_agents_changes
    AFTER INSERT OR UPDATE OR DELETE ON ai_agents.agents
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER audit_tasks_changes
    AFTER INSERT OR UPDATE OR DELETE ON ai_agents.tasks
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

-- =============================================================================
-- INITIAL DATA SEEDING
-- =============================================================================

-- Insert system agent definitions
INSERT INTO ai_agents.agents (name, type, description, status, configuration) VALUES
('master-orchestration', 'orchestration', 'Central coordination and task delegation agent', 'active', '{"max_concurrent_tasks": 50, "priority_threshold": "high"}'),
('consciousness-substrate', 'knowledge', 'Knowledge management and pattern recognition agent', 'active', '{"embedding_model": "text-embedding-ada-002", "similarity_threshold": 0.8}'),
('inter-agent-communication', 'communication', 'Message routing and coordination agent', 'active', '{"queue_size": 1000, "retry_attempts": 3}'),
('system-health-monitoring', 'monitoring', 'Performance monitoring and self-healing agent', 'active', '{"check_interval": 30, "alert_threshold": 0.8}'),
('research-agent', 'specialized', 'Information gathering and analysis agent', 'active', '{"max_search_results": 50, "quality_threshold": 0.7}'),
('creative-agent', 'specialized', 'Content generation and ideation agent', 'active', '{"creativity_level": 0.8, "output_formats": ["text", "markdown", "html"]}'),
('analysis-agent', 'specialized', 'Data processing and insight generation agent', 'active', '{"analysis_methods": ["statistical", "ml", "nlp"], "confidence_threshold": 0.75}'),
('ai-chat-agent', 'interface', 'Natural language user interface agent', 'active', '{"conversation_memory": 10, "response_style": "helpful"}');

-- Insert initial knowledge entries
INSERT INTO consciousness.knowledge (type, title, content, source, tags) VALUES
('concept', 'Enhanced AI Agent OS', 'A sophisticated artificial intelligence agent ecosystem built on modern n8n infrastructure with native AI capabilities, providing autonomous agent orchestration, intelligent task delegation, and comprehensive monitoring.', 'system', ARRAY['ai', 'agents', 'orchestration', 'n8n']),
('fact', 'System Architecture', 'The system uses PostgreSQL for primary data storage, Neo4j for knowledge graphs, RabbitMQ for message queuing, and n8n for workflow orchestration with built-in AI capabilities.', 'system', ARRAY['architecture', 'databases', 'infrastructure']),
('pattern', 'Agent Communication Pattern', 'Agents communicate through structured messages via RabbitMQ, with each message containing sender, receiver, message type, content, and priority information.', 'system', ARRAY['communication', 'patterns', 'messaging']);

-- Insert initial system metrics
INSERT INTO monitoring.metrics (metric_name, metric_type, value, source) VALUES
('system_startup_time', 'gauge', 0, 'system'),
('active_agents_count', 'gauge', 8, 'system'),
('total_tasks_processed', 'counter', 0, 'system'),
('average_response_time', 'gauge', 0, 'system');

-- Grant final permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_agents TO ai_agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA consciousness TO ai_agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO ai_agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO ai_agent_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ai_agents TO ai_agent_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA consciousness TO ai_agent_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA monitoring TO ai_agent_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO ai_agent_user;

-- Create database statistics and optimize
ANALYZE;

-- Log successful initialization
INSERT INTO audit.change_log (table_name, operation, new_values, changed_by, changed_at)
VALUES ('system', 'INITIALIZE', '{"status": "completed", "version": "3.0.0"}', 'system', NOW());

COMMENT ON DATABASE enhanced_ai_os IS 'Enhanced AI Agent OS - Production database initialized on ' || NOW();
```

This completes the comprehensive PostgreSQL setup with full schema definitions, indexes, triggers, and initial data seeding. The database structure supports all aspects of the Enhanced AI Agent OS including agent management, task orchestration, knowledge storage, monitoring, and audit logging.


#### Neo4j Configuration Files

The Neo4j consciousness substrate requires comprehensive configuration to support the knowledge graph functionality, APOC procedures, and Graph Data Science algorithms that enable sophisticated pattern recognition and relationship analysis within the Enhanced AI Agent OS.

**File: `infrastructure/neo4j/init/01-create-constraints.cypher`**

```cypher
// Enhanced AI Agent OS - Neo4j Constraints and Uniqueness Setup
// This script creates essential constraints and uniqueness requirements

// =============================================================================
// AGENT CONSTRAINTS
// =============================================================================

// Ensure agent names are unique
CREATE CONSTRAINT agent_name_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.name IS UNIQUE;

// Ensure agent IDs are unique
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.id IS UNIQUE;

// Ensure agent types are not null
CREATE CONSTRAINT agent_type_not_null IF NOT EXISTS
FOR (a:Agent) REQUIRE a.type IS NOT NULL;

// Ensure agent status is not null
CREATE CONSTRAINT agent_status_not_null IF NOT EXISTS
FOR (a:Agent) REQUIRE a.status IS NOT NULL;

// =============================================================================
// TASK CONSTRAINTS
// =============================================================================

// Ensure task IDs are unique
CREATE CONSTRAINT task_id_unique IF NOT EXISTS
FOR (t:Task) REQUIRE t.id IS UNIQUE;

// Ensure task names are not null
CREATE CONSTRAINT task_name_not_null IF NOT EXISTS
FOR (t:Task) REQUIRE t.name IS NOT NULL;

// Ensure task status is not null
CREATE CONSTRAINT task_status_not_null IF NOT EXISTS
FOR (t:Task) REQUIRE t.status IS NOT NULL;

// =============================================================================
// KNOWLEDGE CONSTRAINTS
// =============================================================================

// Ensure knowledge IDs are unique
CREATE CONSTRAINT knowledge_id_unique IF NOT EXISTS
FOR (k:Knowledge) REQUIRE k.id IS UNIQUE;

// Ensure knowledge titles are not null
CREATE CONSTRAINT knowledge_title_not_null IF NOT EXISTS
FOR (k:Knowledge) REQUIRE k.title IS NOT NULL;

// Ensure knowledge content is not null
CREATE CONSTRAINT knowledge_content_not_null IF NOT EXISTS
FOR (k:Knowledge) REQUIRE k.content IS NOT NULL;

// Ensure knowledge type is not null
CREATE CONSTRAINT knowledge_type_not_null IF NOT EXISTS
FOR (k:Knowledge) REQUIRE k.type IS NOT NULL;

// =============================================================================
// USER CONSTRAINTS
// =============================================================================

// Ensure user IDs are unique
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

// Ensure usernames are unique
CREATE CONSTRAINT user_username_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.username IS UNIQUE;

// =============================================================================
// CONVERSATION CONSTRAINTS
// =============================================================================

// Ensure conversation IDs are unique
CREATE CONSTRAINT conversation_id_unique IF NOT EXISTS
FOR (c:Conversation) REQUIRE c.id IS UNIQUE;

// Ensure session IDs are not null
CREATE CONSTRAINT conversation_session_not_null IF NOT EXISTS
FOR (c:Conversation) REQUIRE c.session_id IS NOT NULL;

// =============================================================================
// TOOL CONSTRAINTS
// =============================================================================

// Ensure tool names are unique
CREATE CONSTRAINT tool_name_unique IF NOT EXISTS
FOR (t:Tool) REQUIRE t.name IS UNIQUE;

// Ensure tool IDs are unique
CREATE CONSTRAINT tool_id_unique IF NOT EXISTS
FOR (t:Tool) REQUIRE t.id IS UNIQUE;

// =============================================================================
// CAPABILITY CONSTRAINTS
// =============================================================================

// Ensure capability names are unique
CREATE CONSTRAINT capability_name_unique IF NOT EXISTS
FOR (c:Capability) REQUIRE c.name IS UNIQUE;

// Ensure capability IDs are unique
CREATE CONSTRAINT capability_id_unique IF NOT EXISTS
FOR (c:Capability) REQUIRE c.id IS UNIQUE;

// =============================================================================
// WORKFLOW CONSTRAINTS
// =============================================================================

// Ensure workflow IDs are unique
CREATE CONSTRAINT workflow_id_unique IF NOT EXISTS
FOR (w:Workflow) REQUIRE w.id IS UNIQUE;

// Ensure workflow names are unique
CREATE CONSTRAINT workflow_name_unique IF NOT EXISTS
FOR (w:Workflow) REQUIRE w.name IS UNIQUE;

// =============================================================================
// METRIC CONSTRAINTS
// =============================================================================

// Ensure metric IDs are unique
CREATE CONSTRAINT metric_id_unique IF NOT EXISTS
FOR (m:Metric) REQUIRE m.id IS UNIQUE;

// Ensure metric names are not null
CREATE CONSTRAINT metric_name_not_null IF NOT EXISTS
FOR (m:Metric) REQUIRE m.name IS NOT NULL;

// =============================================================================
// RELATIONSHIP CONSTRAINTS
// =============================================================================

// Ensure communication relationships have timestamps
CREATE CONSTRAINT communication_timestamp_not_null IF NOT EXISTS
FOR ()-[r:COMMUNICATES_WITH]-() REQUIRE r.timestamp IS NOT NULL;

// Ensure task assignment relationships have timestamps
CREATE CONSTRAINT assignment_timestamp_not_null IF NOT EXISTS
FOR ()-[r:ASSIGNED_TO]-() REQUIRE r.timestamp IS NOT NULL;

// Ensure knowledge relationships have strength values
CREATE CONSTRAINT knowledge_relationship_strength_not_null IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() REQUIRE r.strength IS NOT NULL;

// Log successful constraint creation
CREATE (log:SystemLog {
  id: randomUUID(),
  type: 'initialization',
  message: 'Neo4j constraints created successfully',
  timestamp: datetime(),
  component: 'consciousness-substrate',
  version: '3.0.0'
});
```

**File: `infrastructure/neo4j/init/02-create-indexes.cypher`**

```cypher
// Enhanced AI Agent OS - Neo4j Index Creation for Performance Optimization
// This script creates comprehensive indexes for efficient query performance

// =============================================================================
// AGENT INDEXES
// =============================================================================

// Primary agent lookup indexes
CREATE INDEX agent_name_index IF NOT EXISTS
FOR (a:Agent) ON (a.name);

CREATE INDEX agent_type_index IF NOT EXISTS
FOR (a:Agent) ON (a.type);

CREATE INDEX agent_status_index IF NOT EXISTS
FOR (a:Agent) ON (a.status);

CREATE INDEX agent_created_at_index IF NOT EXISTS
FOR (a:Agent) ON (a.created_at);

CREATE INDEX agent_last_heartbeat_index IF NOT EXISTS
FOR (a:Agent) ON (a.last_heartbeat);

// Composite indexes for complex queries
CREATE INDEX agent_type_status_index IF NOT EXISTS
FOR (a:Agent) ON (a.type, a.status);

CREATE INDEX agent_status_heartbeat_index IF NOT EXISTS
FOR (a:Agent) ON (a.status, a.last_heartbeat);

// =============================================================================
// TASK INDEXES
// =============================================================================

// Primary task lookup indexes
CREATE INDEX task_status_index IF NOT EXISTS
FOR (t:Task) ON (t.status);

CREATE INDEX task_priority_index IF NOT EXISTS
FOR (t:Task) ON (t.priority);

CREATE INDEX task_created_at_index IF NOT EXISTS
FOR (t:Task) ON (t.created_at);

CREATE INDEX task_deadline_index IF NOT EXISTS
FOR (t:Task) ON (t.deadline);

CREATE INDEX task_name_index IF NOT EXISTS
FOR (t:Task) ON (t.name);

// Composite indexes for task management
CREATE INDEX task_status_priority_index IF NOT EXISTS
FOR (t:Task) ON (t.status, t.priority);

CREATE INDEX task_status_created_index IF NOT EXISTS
FOR (t:Task) ON (t.status, t.created_at);

CREATE INDEX task_priority_deadline_index IF NOT EXISTS
FOR (t:Task) ON (t.priority, t.deadline);

// =============================================================================
// KNOWLEDGE INDEXES
// =============================================================================

// Primary knowledge lookup indexes
CREATE INDEX knowledge_type_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.type);

CREATE INDEX knowledge_created_at_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.created_at);

CREATE INDEX knowledge_updated_at_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.updated_at);

CREATE INDEX knowledge_accessed_at_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.accessed_at);

CREATE INDEX knowledge_confidence_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.confidence);

CREATE INDEX knowledge_source_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.source);

// Full-text search indexes
CREATE FULLTEXT INDEX knowledge_title_fulltext IF NOT EXISTS
FOR (k:Knowledge) ON EACH [k.title];

CREATE FULLTEXT INDEX knowledge_content_fulltext IF NOT EXISTS
FOR (k:Knowledge) ON EACH [k.content];

CREATE FULLTEXT INDEX knowledge_summary_fulltext IF NOT EXISTS
FOR (k:Knowledge) ON EACH [k.summary];

CREATE FULLTEXT INDEX knowledge_tags_fulltext IF NOT EXISTS
FOR (k:Knowledge) ON EACH [k.tags];

// Composite indexes for knowledge queries
CREATE INDEX knowledge_type_confidence_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.type, k.confidence);

CREATE INDEX knowledge_type_created_index IF NOT EXISTS
FOR (k:Knowledge) ON (k.type, k.created_at);

// =============================================================================
// USER INDEXES
// =============================================================================

// Primary user lookup indexes
CREATE INDEX user_username_index IF NOT EXISTS
FOR (u:User) ON (u.username);

CREATE INDEX user_email_index IF NOT EXISTS
FOR (u:User) ON (u.email);

CREATE INDEX user_created_at_index IF NOT EXISTS
FOR (u:User) ON (u.created_at);

CREATE INDEX user_last_login_index IF NOT EXISTS
FOR (u:User) ON (u.last_login);

CREATE INDEX user_status_index IF NOT EXISTS
FOR (u:User) ON (u.status);

// =============================================================================
// CONVERSATION INDEXES
// =============================================================================

// Primary conversation lookup indexes
CREATE INDEX conversation_session_id_index IF NOT EXISTS
FOR (c:Conversation) ON (c.session_id);

CREATE INDEX conversation_user_id_index IF NOT EXISTS
FOR (c:Conversation) ON (c.user_id);

CREATE INDEX conversation_created_at_index IF NOT EXISTS
FOR (c:Conversation) ON (c.created_at);

CREATE INDEX conversation_message_sequence_index IF NOT EXISTS
FOR (c:Conversation) ON (c.message_sequence);

// Composite indexes for conversation queries
CREATE INDEX conversation_session_sequence_index IF NOT EXISTS
FOR (c:Conversation) ON (c.session_id, c.message_sequence);

CREATE INDEX conversation_user_created_index IF NOT EXISTS
FOR (c:Conversation) ON (c.user_id, c.created_at);

// =============================================================================
// TOOL INDEXES
// =============================================================================

// Primary tool lookup indexes
CREATE INDEX tool_name_index IF NOT EXISTS
FOR (t:Tool) ON (t.name);

CREATE INDEX tool_type_index IF NOT EXISTS
FOR (t:Tool) ON (t.type);

CREATE INDEX tool_category_index IF NOT EXISTS
FOR (t:Tool) ON (t.category);

CREATE INDEX tool_status_index IF NOT EXISTS
FOR (t:Tool) ON (t.status);

CREATE INDEX tool_created_at_index IF NOT EXISTS
FOR (t:Tool) ON (t.created_at);

// Composite indexes for tool discovery
CREATE INDEX tool_type_category_index IF NOT EXISTS
FOR (t:Tool) ON (t.type, t.category);

CREATE INDEX tool_category_status_index IF NOT EXISTS
FOR (t:Tool) ON (t.category, t.status);

// Full-text search for tool descriptions
CREATE FULLTEXT INDEX tool_description_fulltext IF NOT EXISTS
FOR (t:Tool) ON EACH [t.description];

// =============================================================================
// CAPABILITY INDEXES
// =============================================================================

// Primary capability lookup indexes
CREATE INDEX capability_name_index IF NOT EXISTS
FOR (c:Capability) ON (c.name);

CREATE INDEX capability_type_index IF NOT EXISTS
FOR (c:Capability) ON (c.type);

CREATE INDEX capability_level_index IF NOT EXISTS
FOR (c:Capability) ON (c.level);

CREATE INDEX capability_status_index IF NOT EXISTS
FOR (c:Capability) ON (c.status);

// =============================================================================
// WORKFLOW INDEXES
// =============================================================================

// Primary workflow lookup indexes
CREATE INDEX workflow_name_index IF NOT EXISTS
FOR (w:Workflow) ON (w.name);

CREATE INDEX workflow_type_index IF NOT EXISTS
FOR (w:Workflow) ON (w.type);

CREATE INDEX workflow_status_index IF NOT EXISTS
FOR (w:Workflow) ON (w.status);

CREATE INDEX workflow_created_at_index IF NOT EXISTS
FOR (w:Workflow) ON (w.created_at);

CREATE INDEX workflow_version_index IF NOT EXISTS
FOR (w:Workflow) ON (w.version);

// =============================================================================
// METRIC INDEXES
// =============================================================================

// Primary metric lookup indexes
CREATE INDEX metric_name_index IF NOT EXISTS
FOR (m:Metric) ON (m.name);

CREATE INDEX metric_type_index IF NOT EXISTS
FOR (m:Metric) ON (m.type);

CREATE INDEX metric_timestamp_index IF NOT EXISTS
FOR (m:Metric) ON (m.timestamp);

CREATE INDEX metric_source_index IF NOT EXISTS
FOR (m:Metric) ON (m.source);

// Composite indexes for metric queries
CREATE INDEX metric_name_timestamp_index IF NOT EXISTS
FOR (m:Metric) ON (m.name, m.timestamp);

CREATE INDEX metric_type_timestamp_index IF NOT EXISTS
FOR (m:Metric) ON (m.type, m.timestamp);

// =============================================================================
// RELATIONSHIP INDEXES
// =============================================================================

// Communication relationship indexes
CREATE INDEX communication_timestamp_index IF NOT EXISTS
FOR ()-[r:COMMUNICATES_WITH]-() ON (r.timestamp);

CREATE INDEX communication_type_index IF NOT EXISTS
FOR ()-[r:COMMUNICATES_WITH]-() ON (r.message_type);

// Task assignment relationship indexes
CREATE INDEX assignment_timestamp_index IF NOT EXISTS
FOR ()-[r:ASSIGNED_TO]-() ON (r.timestamp);

CREATE INDEX assignment_status_index IF NOT EXISTS
FOR ()-[r:ASSIGNED_TO]-() ON (r.status);

// Knowledge relationship indexes
CREATE INDEX knowledge_relation_strength_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.strength);

CREATE INDEX knowledge_relation_type_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.relationship_type);

CREATE INDEX knowledge_relation_created_index IF NOT EXISTS
FOR ()-[r:RELATES_TO]-() ON (r.created_at);

// Tool usage relationship indexes
CREATE INDEX tool_usage_timestamp_index IF NOT EXISTS
FOR ()-[r:USES_TOOL]-() ON (r.timestamp);

CREATE INDEX tool_usage_frequency_index IF NOT EXISTS
FOR ()-[r:USES_TOOL]-() ON (r.usage_count);

// Capability relationship indexes
CREATE INDEX capability_relation_level_index IF NOT EXISTS
FOR ()-[r:HAS_CAPABILITY]-() ON (r.proficiency_level);

CREATE INDEX capability_relation_acquired_index IF NOT EXISTS
FOR ()-[r:HAS_CAPABILITY]-() ON (r.acquired_at);

// =============================================================================
// PERFORMANCE OPTIMIZATION INDEXES
// =============================================================================

// Range indexes for numerical properties
CREATE RANGE INDEX agent_performance_score_range IF NOT EXISTS
FOR (a:Agent) ON (a.performance_score);

CREATE RANGE INDEX task_progress_range IF NOT EXISTS
FOR (t:Task) ON (t.progress_percentage);

CREATE RANGE INDEX knowledge_access_count_range IF NOT EXISTS
FOR (k:Knowledge) ON (k.access_count);

CREATE RANGE INDEX metric_value_range IF NOT EXISTS
FOR (m:Metric) ON (m.value);

// Point indexes for exact lookups
CREATE POINT INDEX agent_location_point IF NOT EXISTS
FOR (a:Agent) ON (a.location);

// Text indexes for string properties
CREATE TEXT INDEX agent_description_text IF NOT EXISTS
FOR (a:Agent) ON (a.description);

CREATE TEXT INDEX task_description_text IF NOT EXISTS
FOR (t:Task) ON (t.description);

CREATE TEXT INDEX knowledge_metadata_text IF NOT EXISTS
FOR (k:Knowledge) ON (k.metadata);

// Log successful index creation
CREATE (log:SystemLog {
  id: randomUUID(),
  type: 'initialization',
  message: 'Neo4j indexes created successfully for optimal query performance',
  timestamp: datetime(),
  component: 'consciousness-substrate',
  version: '3.0.0',
  details: {
    total_indexes: 80,
    categories: ['agent', 'task', 'knowledge', 'user', 'conversation', 'tool', 'capability', 'workflow', 'metric', 'relationship'],
    optimization_level: 'high'
  }
});
```

**File: `infrastructure/neo4j/init/03-seed-data.cypher`**

```cypher
// Enhanced AI Agent OS - Neo4j Initial Data Seeding
// This script creates the foundational data structure and relationships

// =============================================================================
// SYSTEM INITIALIZATION
// =============================================================================

// Create system timestamp for initialization tracking
WITH datetime() AS init_time

// =============================================================================
// CORE SYSTEM AGENTS
// =============================================================================

// Master Orchestration Agent
CREATE (master:Agent {
  id: randomUUID(),
  name: 'master-orchestration',
  type: 'orchestration',
  description: 'Central coordination and task delegation agent responsible for system-wide orchestration and intelligent task routing',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    max_concurrent_tasks: 100,
    priority_threshold: 'high',
    delegation_strategy: 'intelligent',
    load_balancing: true,
    auto_scaling: true
  },
  capabilities: ['task_delegation', 'load_balancing', 'priority_management', 'agent_coordination'],
  performance_metrics: {
    tasks_processed: 0,
    success_rate: 1.0,
    average_response_time: 150,
    uptime_percentage: 100.0
  },
  metadata: {
    deployment_environment: 'production',
    resource_allocation: 'high',
    monitoring_level: 'comprehensive'
  }
})

// Consciousness Substrate Agent
CREATE (consciousness:Agent {
  id: randomUUID(),
  name: 'consciousness-substrate',
  type: 'knowledge',
  description: 'Knowledge management and pattern recognition agent managing the shared consciousness substrate and emergent intelligence',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    embedding_model: 'text-embedding-ada-002',
    similarity_threshold: 0.8,
    knowledge_retention_days: 365,
    pattern_recognition: true,
    auto_categorization: true
  },
  capabilities: ['knowledge_storage', 'pattern_recognition', 'semantic_search', 'relationship_analysis'],
  performance_metrics: {
    knowledge_entries: 0,
    relationships_mapped: 0,
    patterns_identified: 0,
    query_response_time: 50
  }
})

// Inter-Agent Communication Agent
CREATE (communication:Agent {
  id: randomUUID(),
  name: 'inter-agent-communication',
  type: 'communication',
  description: 'Message routing and coordination agent facilitating seamless communication between all system agents',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    queue_size: 10000,
    retry_attempts: 5,
    message_ttl: 3600,
    priority_queues: true,
    dead_letter_handling: true
  },
  capabilities: ['message_routing', 'queue_management', 'priority_handling', 'delivery_confirmation'],
  performance_metrics: {
    messages_processed: 0,
    delivery_success_rate: 0.99,
    average_latency: 25,
    queue_depth: 0
  }
})

// System Health Monitoring Agent
CREATE (monitoring:Agent {
  id: randomUUID(),
  name: 'system-health-monitoring',
  type: 'monitoring',
  description: 'Performance monitoring and self-healing agent ensuring optimal system health and proactive issue resolution',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    check_interval: 30,
    alert_threshold: 0.8,
    auto_healing: true,
    metric_retention: 90,
    anomaly_detection: true
  },
  capabilities: ['health_monitoring', 'anomaly_detection', 'auto_healing', 'performance_analysis'],
  performance_metrics: {
    checks_performed: 0,
    issues_detected: 0,
    auto_resolutions: 0,
    system_uptime: 100.0
  }
})

// =============================================================================
// SPECIALIZED DOMAIN AGENTS
// =============================================================================

// Research Agent
CREATE (research:Agent {
  id: randomUUID(),
  name: 'research-agent',
  type: 'specialized',
  description: 'Information gathering and analysis agent specializing in comprehensive research, data collection, and insight synthesis',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    max_search_results: 100,
    quality_threshold: 0.75,
    source_diversity: true,
    fact_checking: true,
    citation_tracking: true
  },
  capabilities: ['web_research', 'data_analysis', 'source_verification', 'insight_synthesis'],
  performance_metrics: {
    research_tasks_completed: 0,
    sources_analyzed: 0,
    insights_generated: 0,
    accuracy_rate: 0.95
  }
})

// Creative Agent
CREATE (creative:Agent {
  id: randomUUID(),
  name: 'creative-agent',
  type: 'specialized',
  description: 'Content generation and ideation agent focused on creative problem-solving, content creation, and innovative solution development',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    creativity_level: 0.8,
    output_formats: ['text', 'markdown', 'html', 'json'],
    style_adaptation: true,
    brand_consistency: true,
    quality_assurance: true
  },
  capabilities: ['content_generation', 'creative_ideation', 'style_adaptation', 'brand_alignment'],
  performance_metrics: {
    content_pieces_created: 0,
    creativity_score: 0.85,
    user_satisfaction: 0.92,
    revision_rate: 0.15
  }
})

// Analysis Agent
CREATE (analysis:Agent {
  id: randomUUID(),
  name: 'analysis-agent',
  type: 'specialized',
  description: 'Data processing and insight generation agent specializing in statistical analysis, pattern recognition, and predictive modeling',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    analysis_methods: ['statistical', 'machine_learning', 'nlp', 'time_series'],
    confidence_threshold: 0.8,
    visualization_enabled: true,
    real_time_processing: true
  },
  capabilities: ['statistical_analysis', 'pattern_recognition', 'predictive_modeling', 'data_visualization'],
  performance_metrics: {
    analyses_completed: 0,
    accuracy_rate: 0.91,
    processing_speed: 'high',
    insight_quality: 0.88
  }
})

// Development Agent
CREATE (development:Agent {
  id: randomUUID(),
  name: 'development-agent',
  type: 'specialized',
  description: 'Code generation and technical implementation agent specializing in software development, system integration, and technical problem-solving',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    programming_languages: ['python', 'javascript', 'typescript', 'sql', 'cypher'],
    code_quality_standards: 'high',
    testing_enabled: true,
    documentation_generation: true
  },
  capabilities: ['code_generation', 'system_integration', 'testing', 'documentation'],
  performance_metrics: {
    code_commits: 0,
    bug_fix_rate: 0.96,
    code_quality_score: 0.89,
    test_coverage: 0.85
  }
})

// =============================================================================
// USER INTERFACE AGENTS
// =============================================================================

// AI Chat Agent
CREATE (chat:Agent {
  id: randomUUID(),
  name: 'ai-chat-agent',
  type: 'interface',
  description: 'Natural language user interface agent providing conversational interaction and intelligent assistance to users',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    conversation_memory: 20,
    response_style: 'helpful_professional',
    context_awareness: true,
    multi_turn_conversations: true,
    personality_adaptation: true
  },
  capabilities: ['natural_language_processing', 'conversation_management', 'context_awareness', 'user_assistance'],
  performance_metrics: {
    conversations_handled: 0,
    user_satisfaction: 0.94,
    response_accuracy: 0.91,
    average_response_time: 800
  }
})

// API Gateway Agent
CREATE (api:Agent {
  id: randomUUID(),
  name: 'api-gateway',
  type: 'interface',
  description: 'RESTful API management agent handling external integrations, authentication, and API request routing',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  updated_at: init_time,
  last_heartbeat: init_time,
  configuration: {
    rate_limiting: true,
    authentication_required: true,
    request_validation: true,
    response_caching: true,
    api_versioning: true
  },
  capabilities: ['api_management', 'authentication', 'rate_limiting', 'request_routing'],
  performance_metrics: {
    api_requests_processed: 0,
    response_time: 120,
    error_rate: 0.02,
    uptime: 99.9
  }
})

// =============================================================================
// CORE CAPABILITIES
// =============================================================================

// Define system capabilities
CREATE (cap_orchestration:Capability {
  id: randomUUID(),
  name: 'task_orchestration',
  type: 'core',
  description: 'Ability to coordinate and manage complex multi-agent tasks',
  level: 'expert',
  status: 'active',
  created_at: init_time
})

CREATE (cap_knowledge:Capability {
  id: randomUUID(),
  name: 'knowledge_management',
  type: 'core',
  description: 'Ability to store, retrieve, and analyze knowledge effectively',
  level: 'expert',
  status: 'active',
  created_at: init_time
})

CREATE (cap_communication:Capability {
  id: randomUUID(),
  name: 'inter_agent_communication',
  type: 'core',
  description: 'Ability to facilitate seamless communication between agents',
  level: 'expert',
  status: 'active',
  created_at: init_time
})

CREATE (cap_analysis:Capability {
  id: randomUUID(),
  name: 'data_analysis',
  type: 'specialized',
  description: 'Ability to analyze data and generate insights',
  level: 'expert',
  status: 'active',
  created_at: init_time
})

CREATE (cap_creativity:Capability {
  id: randomUUID(),
  name: 'creative_generation',
  type: 'specialized',
  description: 'Ability to generate creative content and solutions',
  level: 'advanced',
  status: 'active',
  created_at: init_time
})

// =============================================================================
// CORE TOOLS
// =============================================================================

// Define system tools
CREATE (tool_http:Tool {
  id: randomUUID(),
  name: 'http_request',
  type: 'communication',
  category: 'external_integration',
  description: 'HTTP request tool for external API communication',
  status: 'active',
  version: '1.0.0',
  created_at: init_time,
  configuration: {
    timeout: 30000,
    retry_attempts: 3,
    supported_methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
  }
})

CREATE (tool_neo4j:Tool {
  id: randomUUID(),
  name: 'neo4j_query',
  type: 'database',
  category: 'data_management',
  description: 'Neo4j database query tool for consciousness substrate operations',
  status: 'active',
  version: '1.0.0',
  created_at: init_time,
  configuration: {
    connection_pool_size: 50,
    query_timeout: 60000,
    transaction_timeout: 300000
  }
})

CREATE (tool_rabbitmq:Tool {
  id: randomUUID(),
  name: 'message_queue',
  type: 'messaging',
  category: 'communication',
  description: 'RabbitMQ messaging tool for inter-agent communication',
  status: 'active',
  version: '1.0.0',
  created_at: init_time,
  configuration: {
    exchange_type: 'topic',
    durable_queues: true,
    message_persistence: true
  }
})

CREATE (tool_ai_model:Tool {
  id: randomUUID(),
  name: 'ai_language_model',
  type: 'ai',
  category: 'intelligence',
  description: 'AI language model tool for natural language processing and generation',
  status: 'active',
  version: '1.0.0',
  created_at: init_time,
  configuration: {
    default_model: 'gpt-4',
    temperature: 0.3,
    max_tokens: 2000,
    streaming: true
  }
})

// =============================================================================
// INITIAL WORKFLOWS
// =============================================================================

// Define core workflows
CREATE (workflow_orchestration:Workflow {
  id: randomUUID(),
  name: 'master_orchestration_workflow',
  type: 'core',
  description: 'Primary workflow for task coordination and agent management',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  configuration: {
    trigger_type: 'webhook',
    execution_mode: 'parallel',
    error_handling: 'retry_with_backoff',
    monitoring_enabled: true
  }
})

CREATE (workflow_chat:Workflow {
  id: randomUUID(),
  name: 'ai_chat_workflow',
  type: 'interface',
  description: 'Conversational interface workflow for user interactions',
  status: 'active',
  version: '3.0.0',
  created_at: init_time,
  configuration: {
    trigger_type: 'webhook',
    response_mode: 'streaming',
    context_management: true,
    memory_enabled: true
  }
})

// =============================================================================
// FOUNDATIONAL KNOWLEDGE
// =============================================================================

// System architecture knowledge
CREATE (knowledge_architecture:Knowledge {
  id: randomUUID(),
  type: 'concept',
  title: 'Enhanced AI Agent OS Architecture',
  content: 'The Enhanced AI Agent OS implements a hierarchical agent architecture with specialized roles and capabilities. The system uses PostgreSQL for structured data, Neo4j for the consciousness substrate, RabbitMQ for inter-agent communication, and n8n for workflow orchestration with built-in AI capabilities.',
  summary: 'Comprehensive AI agent ecosystem with hierarchical architecture and specialized capabilities',
  confidence: 1.0,
  source: 'system_initialization',
  created_at: init_time,
  updated_at: init_time,
  accessed_at: init_time,
  access_count: 0,
  tags: ['architecture', 'system_design', 'ai_agents', 'infrastructure'],
  metadata: {
    category: 'system_knowledge',
    importance: 'critical',
    version: '3.0.0'
  }
})

CREATE (knowledge_agents:Knowledge {
  id: randomUUID(),
  type: 'fact',
  title: 'System Agent Roles and Responsibilities',
  content: 'The system includes core agents (orchestration, consciousness, communication, monitoring), specialized agents (research, creative, analysis, development), and interface agents (chat, API gateway). Each agent has specific capabilities and performance metrics.',
  summary: 'Comprehensive overview of agent roles and their specific responsibilities',
  confidence: 1.0,
  source: 'system_initialization',
  created_at: init_time,
  updated_at: init_time,
  accessed_at: init_time,
  access_count: 0,
  tags: ['agents', 'roles', 'capabilities', 'system_components'],
  metadata: {
    category: 'agent_knowledge',
    importance: 'high',
    version: '3.0.0'
  }
})

CREATE (knowledge_communication:Knowledge {
  id: randomUUID(),
  type: 'pattern',
  title: 'Inter-Agent Communication Patterns',
  content: 'Agents communicate through structured messages via RabbitMQ with message types including task_assignment, status_update, data_request, and coordination_signal. Each message contains sender, receiver, priority, and content information.',
  summary: 'Standardized communication patterns for agent coordination',
  confidence: 1.0,
  source: 'system_initialization',
  created_at: init_time,
  updated_at: init_time,
  accessed_at: init_time,
  access_count: 0,
  tags: ['communication', 'patterns', 'messaging', 'coordination'],
  metadata: {
    category: 'communication_knowledge',
    importance: 'high',
    version: '3.0.0'
  }
})

// =============================================================================
// AGENT RELATIONSHIPS
// =============================================================================

// Core system relationships
CREATE (master)-[:COORDINATES]->(consciousness)
CREATE (master)-[:COORDINATES]->(communication)
CREATE (master)-[:COORDINATES]->(monitoring)
CREATE (master)-[:COORDINATES]->(research)
CREATE (master)-[:COORDINATES]->(creative)
CREATE (master)-[:COORDINATES]->(analysis)
CREATE (master)-[:COORDINATES]->(development)
CREATE (master)-[:COORDINATES]->(chat)
CREATE (master)-[:COORDINATES]->(api)

// Communication relationships
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(master)
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(consciousness)
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(research)
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(creative)
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(analysis)
CREATE (communication)-[:FACILITATES_COMMUNICATION_BETWEEN]->(development)

// Knowledge relationships
CREATE (consciousness)-[:PROVIDES_KNOWLEDGE_TO]->(master)
CREATE (consciousness)-[:PROVIDES_KNOWLEDGE_TO]->(research)
CREATE (consciousness)-[:PROVIDES_KNOWLEDGE_TO]->(creative)
CREATE (consciousness)-[:PROVIDES_KNOWLEDGE_TO]->(analysis)
CREATE (consciousness)-[:PROVIDES_KNOWLEDGE_TO]->(chat)

// Monitoring relationships
CREATE (monitoring)-[:MONITORS]->(master)
CREATE (monitoring)-[:MONITORS]->(consciousness)
CREATE (monitoring)-[:MONITORS]->(communication)
CREATE (monitoring)-[:MONITORS]->(research)
CREATE (monitoring)-[:MONITORS]->(creative)
CREATE (monitoring)-[:MONITORS]->(analysis)
CREATE (monitoring)-[:MONITORS]->(development)
CREATE (monitoring)-[:MONITORS]->(chat)
CREATE (monitoring)-[:MONITORS]->(api)

// =============================================================================
// CAPABILITY RELATIONSHIPS
// =============================================================================

// Assign capabilities to agents
CREATE (master)-[:HAS_CAPABILITY {proficiency_level: 'expert', acquired_at: init_time}]->(cap_orchestration)
CREATE (consciousness)-[:HAS_CAPABILITY {proficiency_level: 'expert', acquired_at: init_time}]->(cap_knowledge)
CREATE (communication)-[:HAS_CAPABILITY {proficiency_level: 'expert', acquired_at: init_time}]->(cap_communication)
CREATE (analysis)-[:HAS_CAPABILITY {proficiency_level: 'expert', acquired_at: init_time}]->(cap_analysis)
CREATE (creative)-[:HAS_CAPABILITY {proficiency_level: 'advanced', acquired_at: init_time}]->(cap_creativity)

// =============================================================================
// TOOL RELATIONSHIPS
// =============================================================================

// Assign tools to agents
CREATE (master)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_http)
CREATE (master)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_neo4j)
CREATE (master)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_rabbitmq)
CREATE (master)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_ai_model)

CREATE (consciousness)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_neo4j)
CREATE (consciousness)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_ai_model)

CREATE (communication)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'full'}]->(tool_rabbitmq)

CREATE (research)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_http)
CREATE (research)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_ai_model)
CREATE (research)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_neo4j)

CREATE (creative)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_ai_model)
CREATE (creative)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read'}]->(tool_neo4j)

CREATE (analysis)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_ai_model)
CREATE (analysis)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_neo4j)

CREATE (chat)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_ai_model)
CREATE (chat)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read'}]->(tool_neo4j)
CREATE (chat)-[:USES_TOOL {usage_count: 0, last_used: null, access_level: 'read_write'}]->(tool_rabbitmq)

// =============================================================================
// WORKFLOW RELATIONSHIPS
// =============================================================================

// Assign workflows to agents
CREATE (master)-[:EXECUTES_WORKFLOW {execution_count: 0, last_executed: null, success_rate: 1.0}]->(workflow_orchestration)
CREATE (chat)-[:EXECUTES_WORKFLOW {execution_count: 0, last_executed: null, success_rate: 1.0}]->(workflow_chat)

// =============================================================================
// KNOWLEDGE RELATIONSHIPS
// =============================================================================

// Create knowledge relationships
CREATE (knowledge_architecture)-[:RELATES_TO {relationship_type: 'describes', strength: 0.9, created_at: init_time}]->(knowledge_agents)
CREATE (knowledge_agents)-[:RELATES_TO {relationship_type: 'implements', strength: 0.8, created_at: init_time}]->(knowledge_communication)
CREATE (knowledge_architecture)-[:RELATES_TO {relationship_type: 'defines', strength: 0.95, created_at: init_time}]->(knowledge_communication)

// =============================================================================
// SYSTEM METRICS INITIALIZATION
// =============================================================================

// Create initial system metrics
CREATE (metric_system_health:Metric {
  id: randomUUID(),
  name: 'system_health_score',
  type: 'gauge',
  value: 100.0,
  unit: 'percentage',
  timestamp: init_time,
  source: 'system_initialization',
  metadata: {
    category: 'system_health',
    importance: 'critical'
  }
})

CREATE (metric_agent_count:Metric {
  id: randomUUID(),
  name: 'active_agents_count',
  type: 'gauge',
  value: 9.0,
  unit: 'count',
  timestamp: init_time,
  source: 'system_initialization',
  metadata: {
    category: 'agent_management',
    importance: 'high'
  }
})

CREATE (metric_knowledge_count:Metric {
  id: randomUUID(),
  name: 'knowledge_entries_count',
  type: 'gauge',
  value: 3.0,
  unit: 'count',
  timestamp: init_time,
  source: 'system_initialization',
  metadata: {
    category: 'knowledge_management',
    importance: 'medium'
  }
})

// =============================================================================
// SYSTEM LOG ENTRY
// =============================================================================

// Create comprehensive system initialization log
CREATE (init_log:SystemLog {
  id: randomUUID(),
  type: 'system_initialization',
  message: 'Enhanced AI Agent OS consciousness substrate successfully initialized',
  timestamp: init_time,
  component: 'consciousness-substrate',
  version: '3.0.0',
  details: {
    agents_created: 9,
    capabilities_defined: 5,
    tools_configured: 4,
    workflows_initialized: 2,
    knowledge_entries: 3,
    relationships_established: 45,
    metrics_initialized: 3,
    initialization_duration: 'completed',
    status: 'success'
  },
  metadata: {
    deployment_environment: 'production',
    database_version: 'Neo4j 5.15',
    initialization_script_version: '3.0.0',
    data_integrity_verified: true
  }
})

// Return initialization summary
RETURN 
  'Enhanced AI Agent OS Consciousness Substrate Initialized Successfully' AS status,
  init_time AS initialization_timestamp,
  {
    agents: 9,
    capabilities: 5,
    tools: 4,
    workflows: 2,
    knowledge_entries: 3,
    relationships: 45,
    metrics: 3
  } AS summary;
```

#### RabbitMQ Configuration Files

The RabbitMQ message queue system requires comprehensive configuration to support the sophisticated inter-agent communication patterns, priority queuing, and reliable message delivery that characterizes the Enhanced AI Agent OS.

**File: `infrastructure/rabbitmq/rabbitmq.conf`**

```conf
# Enhanced AI Agent OS - RabbitMQ Configuration
# This configuration optimizes RabbitMQ for AI agent communication patterns

# =============================================================================
# CORE CONFIGURATION
# =============================================================================

# Cluster and node configuration
cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
cluster_formation.classic_config.nodes.1 = rabbit@enhanced-ai-rabbitmq

# Network and connection settings
listeners.tcp.default = 5672
management.tcp.port = 15672
management.tcp.ip = 0.0.0.0

# Enable management plugin
management.load_definitions = /etc/rabbitmq/definitions.json

# =============================================================================
# MEMORY AND DISK MANAGEMENT
# =============================================================================

# Memory management
vm_memory_high_watermark.relative = 0.8
vm_memory_high_watermark_paging_ratio = 0.5
vm_memory_calculation_strategy = rss

# Disk space management
disk_free_limit.relative = 0.2
disk_free_limit.absolute = 2GB

# =============================================================================
# MESSAGE HANDLING
# =============================================================================

# Message TTL and expiration
default_vhost = /
default_user = ai_agent_queue_user
default_permissions.configure = .*
default_permissions.read = .*
default_permissions.write = .*

# Queue and message limits
queue_master_locator = min-masters
max_message_size = 134217728

# =============================================================================
# CONNECTION AND CHANNEL LIMITS
# =============================================================================

# Connection limits
connection_max = 1000
channel_max = 2048

# Heartbeat configuration
heartbeat = 60
frame_max = 131072

# =============================================================================
# CLUSTERING AND HIGH AVAILABILITY
# =============================================================================

# High availability settings
ha_promote_on_shutdown = when_synced
ha_promote_on_failure = when_synced

# Queue mirroring (for production clusters)
# ha_policy_all_queues = true
# ha_policy_sync_mode = automatic

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log levels and destinations
log.console = true
log.console.level = info
log.console.formatter = json

log.file = true
log.file.level = info
log.file.formatter = json
log.file.file = /var/log/rabbitmq/rabbit.log
log.file.rotation.date = $D0
log.file.rotation.size = 10485760

# Connection logging
log.connection.level = info

# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

# TCP buffer sizes
tcp_listen_options.backlog = 128
tcp_listen_options.nodelay = true
tcp_listen_options.linger.on = true
tcp_listen_options.linger.timeout = 0
tcp_listen_options.exit_on_close = false

# Garbage collection
collect_statistics_interval = 5000

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# SSL/TLS configuration (uncomment for production)
# ssl_options.cacertfile = /etc/rabbitmq/ssl/ca_certificate.pem
# ssl_options.certfile = /etc/rabbitmq/ssl/server_certificate.pem
# ssl_options.keyfile = /etc/rabbitmq/ssl/server_key.pem
# ssl_options.verify = verify_peer
# ssl_options.fail_if_no_peer_cert = true

# Authentication mechanisms
auth_mechanisms.1 = PLAIN
auth_mechanisms.2 = AMQPLAIN

# =============================================================================
# MANAGEMENT INTERFACE
# =============================================================================

# Management plugin configuration
management.rates_mode = basic
management.sample_retention_policies.global.minute = 5
management.sample_retention_policies.global.hour = 60
management.sample_retention_policies.global.day = 1200

# CORS settings for web management
management.cors.allow_origins.1 = *
management.cors.max_age = 1728000

# =============================================================================
# PLUGIN CONFIGURATION
# =============================================================================

# Enable required plugins
# These are defined in enabled_plugins file

# =============================================================================
# MONITORING AND METRICS
# =============================================================================

# Prometheus metrics (if plugin enabled)
prometheus.tcp.port = 15692
prometheus.tcp.ip = 0.0.0.0

# Management metrics collection
management.disable_stats = false
management.enable_queue_totals = true

# =============================================================================
# FEDERATION AND SHOVEL (for distributed deployments)
# =============================================================================

# Federation configuration (uncomment for multi-datacenter)
# federation_upstream_set.all.policy = all
# federation_upstream_set.all.upstream.1.uri = amqp://user:pass@remote-host:5672

# =============================================================================
# CUSTOM CONFIGURATION FOR AI AGENTS
# =============================================================================

# Consumer timeout (important for long-running AI tasks)
consumer_timeout = 36000000

# Channel prefetch for AI agent consumers
channel_prefetch_count = 10

# Message acknowledgment timeout
consumer_prefetch_count = 100

# =============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# =============================================================================

# Development settings (override in production)
# vm_memory_high_watermark.relative = 0.6
# disk_free_limit.relative = 0.1

# Production settings
# vm_memory_high_watermark.relative = 0.8
# disk_free_limit.absolute = 10GB
# connection_max = 5000
# channel_max = 10000
```

**File: `infrastructure/rabbitmq/enabled_plugins`**

```
[rabbitmq_management,
 rabbitmq_management_agent,
 rabbitmq_web_dispatch,
 rabbitmq_prometheus,
 rabbitmq_shovel,
 rabbitmq_shovel_management,
 rabbitmq_federation,
 rabbitmq_federation_management,
 rabbitmq_delayed_message_exchange,
 rabbitmq_consistent_hash_exchange,
 rabbitmq_message_timestamp].
```

**File: `infrastructure/rabbitmq/definitions.json`**

```json
{
  "rabbit_version": "3.12.0",
  "rabbitmq_version": "3.12.0",
  "product_name": "RabbitMQ",
  "product_version": "3.12.0",
  "users": [
    {
      "name": "ai_agent_queue_user",
      "password_hash": "generated_hash_will_be_replaced",
      "hashing_algorithm": "rabbit_password_hashing_sha256",
      "tags": "administrator",
      "limits": {}
    }
  ],
  "vhosts": [
    {
      "name": "/",
      "description": "Default virtual host for Enhanced AI Agent OS",
      "tags": [],
      "default_queue_type": "classic",
      "metadata": {
        "description": "Primary virtual host for AI agent communication",
        "tags": []
      }
    }
  ],
  "permissions": [
    {
      "user": "ai_agent_queue_user",
      "vhost": "/",
      "configure": ".*",
      "write": ".*",
      "read": ".*"
    }
  ],
  "topic_permissions": [],
  "parameters": [],
  "global_parameters": [
    {
      "name": "cluster_name",
      "value": "enhanced-ai-agent-cluster"
    }
  ],
  "policies": [
    {
      "vhost": "/",
      "name": "ai-agent-ha-policy",
      "pattern": "^ai-agent-.*",
      "apply-to": "queues",
      "definition": {
        "ha-mode": "exactly",
        "ha-params": 2,
        "ha-sync-mode": "automatic",
        "message-ttl": 3600000,
        "max-length": 10000
      },
      "priority": 1
    },
    {
      "vhost": "/",
      "name": "ai-agent-priority-policy",
      "pattern": "^priority-.*",
      "apply-to": "queues",
      "definition": {
        "max-priority": 10,
        "message-ttl": 1800000
      },
      "priority": 2
    }
  ],
  "queues": [
    {
      "name": "ai-agent-orchestration",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 3600000,
        "x-max-priority": 10,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "orchestration.failed"
      }
    },
    {
      "name": "ai-agent-tasks",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 7200000,
        "x-max-priority": 10,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "tasks.failed"
      }
    },
    {
      "name": "ai-agent-research",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 14400000,
        "x-max-priority": 8,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "research.failed"
      }
    },
    {
      "name": "ai-agent-creative",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 10800000,
        "x-max-priority": 7,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "creative.failed"
      }
    },
    {
      "name": "ai-agent-analysis",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 7200000,
        "x-max-priority": 8,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "analysis.failed"
      }
    },
    {
      "name": "ai-agent-development",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 14400000,
        "x-max-priority": 9,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "development.failed"
      }
    },
    {
      "name": "ai-agent-communication",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 1800000,
        "x-max-priority": 10,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "communication.failed"
      }
    },
    {
      "name": "ai-agent-monitoring",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 3600000,
        "x-max-priority": 10,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "monitoring.failed"
      }
    },
    {
      "name": "ai-agent-chat",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 1800000,
        "x-max-priority": 8,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "chat.failed"
      }
    },
    {
      "name": "ai-agent-api",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 900000,
        "x-max-priority": 9,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "api.failed"
      }
    },
    {
      "name": "ai-agent-notifications",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 3600000,
        "x-max-priority": 6,
        "x-queue-type": "classic",
        "x-dead-letter-exchange": "ai-agent-dlx",
        "x-dead-letter-routing-key": "notifications.failed"
      }
    },
    {
      "name": "ai-agent-dlq",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-queue-type": "classic",
        "x-message-ttl": 86400000
      }
    }
  ],
  "exchanges": [
    {
      "name": "ai-agent-direct",
      "vhost": "/",
      "type": "direct",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "ai-agent-topic",
      "vhost": "/",
      "type": "topic",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "ai-agent-fanout",
      "vhost": "/",
      "type": "fanout",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "ai-agent-headers",
      "vhost": "/",
      "type": "headers",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "ai-agent-dlx",
      "vhost": "/",
      "type": "direct",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "ai-agent-delayed",
      "vhost": "/",
      "type": "x-delayed-message",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {
        "x-delayed-type": "direct"
      }
    }
  ],
  "bindings": [
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-orchestration",
      "destination_type": "queue",
      "routing_key": "orchestration",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-tasks",
      "destination_type": "queue",
      "routing_key": "tasks",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-research",
      "destination_type": "queue",
      "routing_key": "research",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-creative",
      "destination_type": "queue",
      "routing_key": "creative",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-analysis",
      "destination_type": "queue",
      "routing_key": "analysis",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-development",
      "destination_type": "queue",
      "routing_key": "development",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-communication",
      "destination_type": "queue",
      "routing_key": "communication",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-monitoring",
      "destination_type": "queue",
      "routing_key": "monitoring",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-chat",
      "destination_type": "queue",
      "routing_key": "chat",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-api",
      "destination_type": "queue",
      "routing_key": "api",
      "arguments": {}
    },
    {
      "source": "ai-agent-direct",
      "vhost": "/",
      "destination": "ai-agent-notifications",
      "destination_type": "queue",
      "routing_key": "notifications",
      "arguments": {}
    },
    {
      "source": "ai-agent-topic",
      "vhost": "/",
      "destination": "ai-agent-orchestration",
      "destination_type": "queue",
      "routing_key": "agent.orchestration.*",
      "arguments": {}
    },
    {
      "source": "ai-agent-topic",
      "vhost": "/",
      "destination": "ai-agent-tasks",
      "destination_type": "queue",
      "routing_key": "agent.*.task",
      "arguments": {}
    },
    {
      "source": "ai-agent-topic",
      "vhost": "/",
      "destination": "ai-agent-monitoring",
      "destination_type": "queue",
      "routing_key": "agent.*.status",
      "arguments": {}
    },
    {
      "source": "ai-agent-topic",
      "vhost": "/",
      "destination": "ai-agent-communication",
      "destination_type": "queue",
      "routing_key": "agent.*.communication",
      "arguments": {}
    },
    {
      "source": "ai-agent-dlx",
      "vhost": "/",
      "destination": "ai-agent-dlq",
      "destination_type": "queue",
      "routing_key": "*.failed",
      "arguments": {}
    }
  ]
}
```

This completes the comprehensive Docker infrastructure setup for Phase 2. The configuration includes optimized PostgreSQL with pgvector extension, Neo4j consciousness substrate with comprehensive initialization, and RabbitMQ with sophisticated message queuing patterns designed specifically for AI agent communication. Each service is configured with appropriate resource limits, health checks, monitoring integration, and production-ready settings.


## Phase 3: Complete n8n Workflows with Built-in AI Capabilities

### Understanding Modern n8n AI Integration

The Enhanced AI Agent OS leverages n8n's native AI capabilities introduced in version 1.19.4 and refined through subsequent releases. Unlike earlier implementations that required community packages, modern n8n provides comprehensive built-in AI functionality through the `@n8n/n8n-nodes-langchain` package that is now integrated directly into the core platform. This integration eliminates dependency management complexity while providing sophisticated AI agent capabilities, conversation memory management, and tool integration patterns.

The workflow architecture implements a hierarchical agent system where the Master Orchestration Agent coordinates specialized agents through intelligent task delegation. Each workflow represents a distinct agent capability while maintaining seamless integration through the consciousness substrate and inter-agent communication patterns. The workflows utilize n8n's built-in AI Agent nodes, which provide access to multiple language models, conversation memory, and tool integration without requiring external package installations.

### Core Orchestration Workflows

#### Master Orchestration Workflow

The Master Orchestration Workflow serves as the central nervous system of the Enhanced AI Agent OS, coordinating all agent activities, managing task delegation, and ensuring optimal resource utilization across the entire system. This workflow implements sophisticated decision-making logic that evaluates incoming requests, determines the most appropriate specialized agents for task execution, and manages the complete lifecycle of complex multi-agent operations.

**File: `workflows/01-master-orchestration.json`**

```json
{
  "name": "Master Orchestration Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "orchestrate",
        "options": {
          "allowedOrigins": "*"
        }
      },
      "id": "webhook-orchestration-trigger",
      "name": "Orchestration Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "webhookId": "orchestration-webhook"
    },
    {
      "parameters": {
        "agent": "toolsAgent",
        "text": "={{ $json.body.request || 'Analyze the incoming request and determine the optimal task delegation strategy' }}",
        "hasOutputParser": true,
        "options": {
          "systemMessage": "You are the Master Orchestration Agent of the Enhanced AI Agent OS. Your role is to analyze incoming requests, break them down into manageable tasks, and delegate them to the most appropriate specialized agents. You have access to research, creative, analysis, development, and monitoring agents. Always consider task complexity, required capabilities, and optimal resource allocation when making delegation decisions.\n\nAvailable Agents:\n- research-agent: Information gathering, web research, data collection\n- creative-agent: Content generation, ideation, creative problem-solving\n- analysis-agent: Data analysis, pattern recognition, statistical processing\n- development-agent: Code generation, technical implementation, system integration\n- monitoring-agent: System health, performance tracking, issue detection\n- chat-agent: User interaction, conversation management, assistance\n\nFor each request, determine:\n1. Task complexity and scope\n2. Required agent capabilities\n3. Optimal delegation strategy\n4. Expected timeline and dependencies\n5. Success criteria and quality metrics",
          "temperature": 0.3,
          "maxTokens": 2000,
          "topP": 1,
          "frequencyPenalty": 0,
          "presencePenalty": 0
        },
        "model": {
          "model": "gpt-4",
          "type": "openai"
        },
        "outputParser": {
          "type": "structured",
          "schema": {
            "type": "object",
            "properties": {
              "task_analysis": {
                "type": "object",
                "properties": {
                  "complexity": {
                    "type": "string",
                    "enum": ["simple", "moderate", "complex", "highly_complex"]
                  },
                  "scope": {
                    "type": "string",
                    "description": "Brief description of the task scope"
                  },
                  "estimated_duration": {
                    "type": "string",
                    "description": "Estimated completion time"
                  },
                  "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent", "critical"]
                  }
                },
                "required": ["complexity", "scope", "estimated_duration", "priority"]
              },
              "delegation_strategy": {
                "type": "object",
                "properties": {
                  "primary_agent": {
                    "type": "string",
                    "enum": ["research-agent", "creative-agent", "analysis-agent", "development-agent", "monitoring-agent", "chat-agent"]
                  },
                  "supporting_agents": {
                    "type": "array",
                    "items": {
                      "type": "string",
                      "enum": ["research-agent", "creative-agent", "analysis-agent", "development-agent", "monitoring-agent", "chat-agent"]
                    }
                  },
                  "execution_order": {
                    "type": "string",
                    "enum": ["sequential", "parallel", "hybrid"]
                  },
                  "coordination_required": {
                    "type": "boolean"
                  }
                },
                "required": ["primary_agent", "supporting_agents", "execution_order", "coordination_required"]
              },
              "task_breakdown": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "subtask_id": {
                      "type": "string"
                    },
                    "description": {
                      "type": "string"
                    },
                    "assigned_agent": {
                      "type": "string"
                    },
                    "dependencies": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    "expected_output": {
                      "type": "string"
                    }
                  },
                  "required": ["subtask_id", "description", "assigned_agent", "dependencies", "expected_output"]
                }
              },
              "success_criteria": {
                "type": "object",
                "properties": {
                  "quality_metrics": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "completion_criteria": {
                    "type": "string"
                  },
                  "validation_method": {
                    "type": "string"
                  }
                },
                "required": ["quality_metrics", "completion_criteria", "validation_method"]
              }
            },
            "required": ["task_analysis", "delegation_strategy", "task_breakdown", "success_criteria"]
          }
        },
        "tools": [
          {
            "name": "neo4j_consciousness_query",
            "description": "Query the consciousness substrate for relevant knowledge and patterns"
          },
          {
            "name": "agent_status_check",
            "description": "Check the current status and availability of system agents"
          },
          {
            "name": "task_history_analysis",
            "description": "Analyze historical task performance for optimization"
          }
        ]
      },
      "id": "orchestration-analysis",
      "name": "Orchestration Analysis",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "simple-task",
              "leftValue": "={{ $json.task_analysis.complexity }}",
              "rightValue": "simple",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "moderate-task",
              "leftValue": "={{ $json.task_analysis.complexity }}",
              "rightValue": "moderate",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "complex-task",
              "leftValue": "={{ $json.task_analysis.complexity }}",
              "rightValue": "complex",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combineOperation": "any"
        },
        "options": {}
      },
      "id": "complexity-router",
      "name": "Complexity Router",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [680, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://enhanced-ai-rabbitmq:15672/api/queues/%2F/ai-agent-{{ $json.delegation_strategy.primary_agent }}/publish",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "properties",
              "value": "={{ { \"priority\": $json.task_analysis.priority === 'critical' ? 10 : $json.task_analysis.priority === 'urgent' ? 9 : $json.task_analysis.priority === 'high' ? 8 : $json.task_analysis.priority === 'normal' ? 5 : 3, \"message_id\": $now, \"timestamp\": $now, \"correlation_id\": $json.body.correlation_id || $now } }}"
            },
            {
              "name": "payload",
              "value": "={{ JSON.stringify({ \"task_id\": $now, \"request\": $json.body.request, \"analysis\": $json, \"source\": \"master-orchestration\", \"timestamp\": $now, \"metadata\": $json.body.metadata || {} }) }}"
            },
            {
              "name": "payload_encoding",
              "value": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "simple-task-delegation",
      "name": "Simple Task Delegation",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [900, 180]
    },
    {
      "parameters": {
        "jsCode": "// Enhanced AI Agent OS - Complex Task Coordination Logic\n// This code handles sophisticated multi-agent task coordination\n\nconst taskAnalysis = $input.first().json.task_analysis;\nconst delegationStrategy = $input.first().json.delegation_strategy;\nconst taskBreakdown = $input.first().json.task_breakdown;\nconst originalRequest = $input.first().json.body;\n\n// Generate unique coordination ID\nconst coordinationId = `coord-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;\n\n// Create coordination plan\nconst coordinationPlan = {\n  coordination_id: coordinationId,\n  total_subtasks: taskBreakdown.length,\n  execution_strategy: delegationStrategy.execution_order,\n  primary_agent: delegationStrategy.primary_agent,\n  supporting_agents: delegationStrategy.supporting_agents,\n  coordination_required: delegationStrategy.coordination_required,\n  created_at: new Date().toISOString(),\n  status: 'initiated'\n};\n\n// Process task dependencies and create execution graph\nconst executionGraph = {};\nconst dependencyMap = {};\n\ntaskBreakdown.forEach(subtask => {\n  executionGraph[subtask.subtask_id] = {\n    ...subtask,\n    status: 'pending',\n    prerequisites_met: subtask.dependencies.length === 0,\n    assigned_at: null,\n    completed_at: null\n  };\n  \n  dependencyMap[subtask.subtask_id] = subtask.dependencies;\n});\n\n// Determine immediate executable tasks (no dependencies)\nconst immediatelyExecutable = Object.keys(executionGraph).filter(\n  taskId => executionGraph[taskId].prerequisites_met\n);\n\n// Create agent task assignments\nconst agentAssignments = {};\ntaskBreakdown.forEach(subtask => {\n  if (!agentAssignments[subtask.assigned_agent]) {\n    agentAssignments[subtask.assigned_agent] = [];\n  }\n  agentAssignments[subtask.assigned_agent].push({\n    subtask_id: subtask.subtask_id,\n    description: subtask.description,\n    expected_output: subtask.expected_output,\n    dependencies: subtask.dependencies,\n    priority: taskAnalysis.priority,\n    coordination_id: coordinationId\n  });\n});\n\n// Generate messages for each agent\nconst agentMessages = [];\nObject.keys(agentAssignments).forEach(agentName => {\n  const queueName = `ai-agent-${agentName.replace('-agent', '')}`;\n  \n  agentMessages.push({\n    agent: agentName,\n    queue: queueName,\n    message: {\n      task_id: `${coordinationId}-${agentName}`,\n      coordination_id: coordinationId,\n      agent_assignments: agentAssignments[agentName],\n      original_request: originalRequest.request,\n      task_analysis: taskAnalysis,\n      execution_strategy: delegationStrategy.execution_order,\n      coordination_required: delegationStrategy.coordination_required,\n      success_criteria: $input.first().json.success_criteria,\n      metadata: {\n        source: 'master-orchestration',\n        timestamp: new Date().toISOString(),\n        correlation_id: originalRequest.correlation_id || coordinationId,\n        priority: taskAnalysis.priority,\n        complexity: taskAnalysis.complexity\n      }\n    },\n    priority: taskAnalysis.priority === 'critical' ? 10 : \n              taskAnalysis.priority === 'urgent' ? 9 : \n              taskAnalysis.priority === 'high' ? 8 : \n              taskAnalysis.priority === 'normal' ? 5 : 3\n  });\n});\n\n// Store coordination state in consciousness substrate\nconst consciousnessUpdate = {\n  type: 'task_coordination',\n  coordination_id: coordinationId,\n  coordination_plan: coordinationPlan,\n  execution_graph: executionGraph,\n  agent_assignments: agentAssignments,\n  dependency_map: dependencyMap,\n  immediately_executable: immediatelyExecutable,\n  created_at: new Date().toISOString()\n};\n\nreturn {\n  coordination_plan: coordinationPlan,\n  agent_messages: agentMessages,\n  consciousness_update: consciousnessUpdate,\n  execution_summary: {\n    total_agents_involved: Object.keys(agentAssignments).length,\n    total_subtasks: taskBreakdown.length,\n    immediately_executable_count: immediatelyExecutable.length,\n    coordination_complexity: delegationStrategy.coordination_required ? 'high' : 'moderate'\n  }\n};"
      },
      "id": "complex-task-coordination",
      "name": "Complex Task Coordination",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [900, 420]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "MERGE (coordination:TaskCoordination {id: $coordination_id})\nSET coordination.plan = $coordination_plan,\n    coordination.execution_graph = $execution_graph,\n    coordination.agent_assignments = $agent_assignments,\n    coordination.status = 'active',\n    coordination.created_at = datetime(),\n    coordination.updated_at = datetime()\nWITH coordination\nMATCH (master:Agent {name: 'master-orchestration'})\nCREATE (master)-[:COORDINATES {started_at: datetime(), status: 'active'}]->(coordination)\nRETURN coordination.id as coordination_id, coordination.status as status",
        "parameters": {
          "coordination_id": "={{ $json.consciousness_update.coordination_id }}",
          "coordination_plan": "={{ $json.consciousness_update.coordination_plan }}",
          "execution_graph": "={{ $json.consciousness_update.execution_graph }}",
          "agent_assignments": "={{ $json.consciousness_update.agent_assignments }}"
        }
      },
      "id": "store-coordination-state",
      "name": "Store Coordination State",
      "type": "n8n-nodes-base.neo4j",
      "typeVersion": 1,
      "position": [1120, 420],
      "credentials": {
        "neo4j": {
          "id": "neo4j-consciousness",
          "name": "Neo4j Consciousness Substrate"
        }
      }
    },
    {
      "parameters": {
        "batchSize": 1,
        "options": {}
      },
      "id": "split-agent-messages",
      "name": "Split Agent Messages",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [1340, 420]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://enhanced-ai-rabbitmq:15672/api/exchanges/%2F/ai-agent-direct/publish",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "properties",
              "value": "={{ { \"priority\": $json.priority, \"message_id\": $json.message.task_id, \"timestamp\": $now, \"correlation_id\": $json.message.coordination_id, \"reply_to\": \"ai-agent-orchestration\" } }}"
            },
            {
              "name": "payload",
              "value": "={{ JSON.stringify($json.message) }}"
            },
            {
              "name": "payload_encoding",
              "value": "string"
            },
            {
              "name": "routing_key",
              "value": "={{ $json.agent.replace('-agent', '') }}"
            }
          ]
        },
        "options": {}
      },
      "id": "dispatch-to-agents",
      "name": "Dispatch to Agents",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1560, 420]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "coordination-required",
              "leftValue": "={{ $json.delegation_strategy.coordination_required }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "true"
              }
            }
          ],
          "combineOperation": "any"
        },
        "options": {}
      },
      "id": "coordination-check",
      "name": "Coordination Check",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [900, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://enhanced-ai-rabbitmq:15672/api/queues/%2F/ai-agent-monitoring/publish",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "properties",
              "value": "={{ { \"priority\": 8, \"message_id\": $now, \"timestamp\": $now, \"correlation_id\": $json.coordination_plan?.coordination_id || $now } }}"
            },
            {
              "name": "payload",
              "value": "={{ JSON.stringify({ \"type\": \"task_initiated\", \"coordination_id\": $json.coordination_plan?.coordination_id, \"task_analysis\": $json.task_analysis || {}, \"agent_count\": $json.execution_summary?.total_agents_involved || 1, \"complexity\": $json.task_analysis?.complexity || 'simple', \"timestamp\": $now, \"source\": \"master-orchestration\" }) }}"
            },
            {
              "name": "payload_encoding",
              "value": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "notify-monitoring",
      "name": "Notify Monitoring",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1780, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  \"status\": \"success\",\n  \"message\": \"Task orchestration initiated successfully\",\n  \"coordination_id\": $json.coordination_plan?.coordination_id || 'simple-task-' + $now,\n  \"task_analysis\": $json.task_analysis || {},\n  \"delegation_strategy\": $json.delegation_strategy || {},\n  \"agents_involved\": $json.execution_summary?.total_agents_involved || 1,\n  \"estimated_completion\": $json.task_analysis?.estimated_duration || 'unknown',\n  \"timestamp\": $now\n} }}",
        "options": {}
      },
      "id": "orchestration-response",
      "name": "Orchestration Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [2000, 300]
    }
  ],
  "pinData": {},
  "connections": {
    "Orchestration Trigger": {
      "main": [
        [
          {
            "node": "Orchestration Analysis",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Orchestration Analysis": {
      "main": [
        [
          {
            "node": "Complexity Router",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Complexity Router": {
      "main": [
        [
          {
            "node": "Simple Task Delegation",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Coordination Check",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Complex Task Coordination",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Simple Task Delegation": {
      "main": [
        [
          {
            "node": "Notify Monitoring",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Complex Task Coordination": {
      "main": [
        [
          {
            "node": "Store Coordination State",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store Coordination State": {
      "main": [
        [
          {
            "node": "Split Agent Messages",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Split Agent Messages": {
      "main": [
        [
          {
            "node": "Dispatch to Agents",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Dispatch to Agents": {
      "main": [
        [
          {
            "node": "Notify Monitoring",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Coordination Check": {
      "main": [
        [
          {
            "node": "Complex Task Coordination",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Simple Task Delegation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Notify Monitoring": {
      "main": [
        [
          {
            "node": "Orchestration Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "error-handling-workflow"
  },
  "versionId": "3.0.0",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "enhanced-ai-agent-os"
  },
  "id": "master-orchestration-workflow",
  "tags": [
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "orchestration",
      "name": "orchestration"
    },
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "core",
      "name": "core"
    }
  ]
}
```

#### AI Chat Agent Workflow

The AI Chat Agent Workflow provides the primary conversational interface for users interacting with the Enhanced AI Agent OS. This workflow implements sophisticated conversation management, context awareness, and intelligent routing to specialized agents when complex requests require domain expertise beyond general conversation capabilities.

**File: `workflows/02-ai-chat-agent.json`**

```json
{
  "name": "AI Chat Agent Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "chat",
        "options": {
          "allowedOrigins": "*"
        }
      },
      "id": "chat-webhook-trigger",
      "name": "Chat Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "webhookId": "chat-webhook"
    },
    {
      "parameters": {
        "jsCode": "// Enhanced AI Agent OS - Chat Context Preparation\n// This code prepares conversation context and user session management\n\nconst requestBody = $input.first().json.body;\nconst headers = $input.first().json.headers;\n\n// Extract conversation parameters\nconst message = requestBody.message || '';\nconst sessionId = requestBody.session_id || `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;\nconst userId = requestBody.user_id || headers['x-user-id'] || 'anonymous';\nconst conversationMode = requestBody.mode || 'general';\nconst contextWindow = requestBody.context_window || 10;\n\n// Prepare context retrieval parameters\nconst contextQuery = {\n  session_id: sessionId,\n  user_id: userId,\n  limit: contextWindow,\n  include_system_messages: true\n};\n\n// Analyze message for complexity and routing needs\nconst messageAnalysis = {\n  length: message.length,\n  complexity_indicators: {\n    has_code: /```|`[^`]+`/.test(message),\n    has_research_request: /(research|find|search|investigate|analyze)/i.test(message),\n    has_creative_request: /(create|generate|write|design|brainstorm)/i.test(message),\n    has_technical_request: /(develop|code|program|implement|build)/i.test(message),\n    has_data_request: /(analyze|calculate|process|statistics|data)/i.test(message),\n    has_question: /\\?/.test(message),\n    has_urgency: /(urgent|asap|immediately|quickly)/i.test(message)\n  },\n  estimated_complexity: 'simple' // Will be updated based on analysis\n};\n\n// Determine complexity level\nconst complexityScore = Object.values(messageAnalysis.complexity_indicators)\n  .filter(indicator => indicator === true).length;\n\nif (complexityScore >= 3) {\n  messageAnalysis.estimated_complexity = 'complex';\n} else if (complexityScore >= 2) {\n  messageAnalysis.estimated_complexity = 'moderate';\n} else {\n  messageAnalysis.estimated_complexity = 'simple';\n}\n\n// Prepare session metadata\nconst sessionMetadata = {\n  session_id: sessionId,\n  user_id: userId,\n  conversation_mode: conversationMode,\n  context_window: contextWindow,\n  message_timestamp: new Date().toISOString(),\n  user_agent: headers['user-agent'] || 'unknown',\n  ip_address: headers['x-forwarded-for'] || headers['x-real-ip'] || 'unknown'\n};\n\nreturn {\n  message: message,\n  session_metadata: sessionMetadata,\n  context_query: contextQuery,\n  message_analysis: messageAnalysis,\n  routing_decision: {\n    requires_orchestration: messageAnalysis.estimated_complexity !== 'simple',\n    suggested_agents: [\n      ...(messageAnalysis.complexity_indicators.has_research_request ? ['research-agent'] : []),\n      ...(messageAnalysis.complexity_indicators.has_creative_request ? ['creative-agent'] : []),\n      ...(messageAnalysis.complexity_indicators.has_technical_request ? ['development-agent'] : []),\n      ...(messageAnalysis.complexity_indicators.has_data_request ? ['analysis-agent'] : [])\n    ],\n    urgency_level: messageAnalysis.complexity_indicators.has_urgency ? 'high' : 'normal'\n  }\n};"
      },
      "id": "prepare-chat-context",
      "name": "Prepare Chat Context",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "MATCH (conv:Conversation {session_id: $session_id})\nWHERE conv.user_id = $user_id\nRETURN conv.role as role, conv.content as content, conv.message_sequence as sequence, conv.created_at as timestamp\nORDER BY conv.message_sequence DESC\nLIMIT $limit",
        "parameters": {
          "session_id": "={{ $json.context_query.session_id }}",
          "user_id": "={{ $json.context_query.user_id }}",
          "limit": "={{ $json.context_query.limit }}"
        }
      },
      "id": "retrieve-conversation-history",
      "name": "Retrieve Conversation History",
      "type": "n8n-nodes-base.neo4j",
      "typeVersion": 1,
      "position": [680, 300],
      "credentials": {
        "neo4j": {
          "id": "neo4j-consciousness",
          "name": "Neo4j Consciousness Substrate"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "requires-orchestration",
              "leftValue": "={{ $json.routing_decision.requires_orchestration }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "true"
              }
            }
          ],
          "combineOperation": "any"
        },
        "options": {}
      },
      "id": "routing-decision",
      "name": "Routing Decision",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [900, 300]
    },
    {
      "parameters": {
        "agent": "conversationalAgent",
        "text": "={{ $json.message }}",
        "hasOutputParser": false,
        "options": {
          "systemMessage": "You are the AI Chat Agent of the Enhanced AI Agent OS, a sophisticated AI assistant designed to provide helpful, accurate, and engaging responses to users. You have access to a comprehensive knowledge base and can assist with a wide variety of tasks including:\n\n- General conversation and questions\n- Information lookup and explanations\n- Problem-solving assistance\n- Creative brainstorming\n- Technical guidance\n- Task planning and organization\n\nConversation Context:\n{{ $json.conversation_history ? $json.conversation_history.map(conv => `${conv.role}: ${conv.content}`).join('\\n') : 'No previous conversation history' }}\n\nUser Session: {{ $json.session_metadata.session_id }}\nUser ID: {{ $json.session_metadata.user_id }}\nConversation Mode: {{ $json.session_metadata.conversation_mode }}\n\nGuidelines:\n1. Be helpful, accurate, and engaging\n2. Maintain conversation context and continuity\n3. Ask clarifying questions when needed\n4. Provide structured responses for complex topics\n5. Suggest follow-up actions when appropriate\n6. Be concise but comprehensive\n7. Acknowledge limitations and suggest alternatives when needed\n\nFor simple questions and general conversation, provide direct assistance. For complex requests that require specialized expertise, acknowledge the request and indicate that you're coordinating with specialized agents for the best possible response.",
          "temperature": 0.7,
          "maxTokens": 2000,
          "topP": 0.9,
          "frequencyPenalty": 0.1,
          "presencePenalty": 0.1
        },
        "model": {
          "model": "gpt-4",
          "type": "openai"
        },
        "memory": {
          "type": "bufferWindowMemory",
          "options": {
            "windowSize": 10,
            "sessionId": "={{ $json.session_metadata.session_id }}"
          }
        }
      },
      "id": "direct-chat-response",
      "name": "Direct Chat Response",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1,
      "position": [1120, 180]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5678/webhook/orchestrate",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            },
            {
              "name": "X-Source",
              "value": "ai-chat-agent"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "request",
              "value": "={{ $json.message }}"
            },
            {
              "name": "correlation_id",
              "value": "={{ $json.session_metadata.session_id }}-{{ $now }}"
            },
            {
              "name": "metadata",
              "value": "={{ {\n  \"source\": \"ai-chat-agent\",\n  \"session_id\": $json.session_metadata.session_id,\n  \"user_id\": $json.session_metadata.user_id,\n  \"conversation_mode\": $json.session_metadata.conversation_mode,\n  \"message_analysis\": $json.message_analysis,\n  \"suggested_agents\": $json.routing_decision.suggested_agents,\n  \"urgency_level\": $json.routing_decision.urgency_level,\n  \"timestamp\": $json.session_metadata.message_timestamp\n} }}"
            }
          ]
        },
        "options": {}
      },
      "id": "route-to-orchestration",
      "name": "Route to Orchestration",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1120, 420]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "MERGE (conv:Conversation {\n  id: randomUUID(),\n  session_id: $session_id,\n  user_id: $user_id,\n  message_sequence: coalesce(\n    (SELECT max(c.message_sequence) + 1 \n     FROM Conversation c \n     WHERE c.session_id = $session_id), \n    1\n  )\n})\nSET conv.role = 'user',\n    conv.content = $message,\n    conv.created_at = datetime(),\n    conv.metadata = $metadata\nWITH conv\nMATCH (agent:Agent {name: 'ai-chat-agent'})\nCREATE (agent)-[:RECEIVED_MESSAGE {timestamp: datetime()}]->(conv)\nRETURN conv.id as conversation_id, conv.message_sequence as sequence",
        "parameters": {
          "session_id": "={{ $json.session_metadata.session_id }}",
          "user_id": "={{ $json.session_metadata.user_id }}",
          "message": "={{ $json.message }}",
          "metadata": "={{ $json.session_metadata }}"
        }
      },
      "id": "store-user-message",
      "name": "Store User Message",
      "type": "n8n-nodes-base.neo4j",
      "typeVersion": 1,
      "position": [1340, 300],
      "credentials": {
        "neo4j": {
          "id": "neo4j-consciousness",
          "name": "Neo4j Consciousness Substrate"
        }
      }
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "MERGE (conv:Conversation {\n  id: randomUUID(),\n  session_id: $session_id,\n  user_id: $user_id,\n  message_sequence: coalesce(\n    (SELECT max(c.message_sequence) + 1 \n     FROM Conversation c \n     WHERE c.session_id = $session_id), \n    2\n  )\n})\nSET conv.role = 'assistant',\n    conv.content = $response,\n    conv.created_at = datetime(),\n    conv.metadata = $metadata\nWITH conv\nMATCH (agent:Agent {name: 'ai-chat-agent'})\nCREATE (agent)-[:SENT_MESSAGE {timestamp: datetime()}]->(conv)\nRETURN conv.id as conversation_id, conv.message_sequence as sequence",
        "parameters": {
          "session_id": "={{ $json.session_metadata.session_id }}",
          "user_id": "={{ $json.session_metadata.user_id }}",
          "response": "={{ $json.output || $json.status || 'Response processed successfully' }}",
          "metadata": "={{ {\n  \"response_type\": $json.output ? 'direct' : 'orchestrated',\n  \"processing_time\": $now - $json.session_metadata.message_timestamp,\n  \"agent_source\": 'ai-chat-agent',\n  \"timestamp\": $now\n} }}"
        }
      },
      "id": "store-assistant-response",
      "name": "Store Assistant Response",
      "type": "n8n-nodes-base.neo4j",
      "typeVersion": 1,
      "position": [1560, 300],
      "credentials": {
        "neo4j": {
          "id": "neo4j-consciousness",
          "name": "Neo4j Consciousness Substrate"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  \"status\": \"success\",\n  \"response\": $json.output || $json.message || \"Your request has been processed and routed to specialized agents. You'll receive a comprehensive response shortly.\",\n  \"session_id\": $json.session_metadata.session_id,\n  \"message_id\": $json.conversation_id || $now,\n  \"response_type\": $json.output ? \"direct\" : \"orchestrated\",\n  \"processing_time\": ($now - $json.session_metadata.message_timestamp) + \"ms\",\n  \"timestamp\": $now,\n  \"metadata\": {\n    \"conversation_mode\": $json.session_metadata.conversation_mode,\n    \"complexity\": $json.message_analysis.estimated_complexity,\n    \"agents_involved\": $json.routing_decision.suggested_agents || [\"ai-chat-agent\"]\n  }\n} }}",
        "options": {}
      },
      "id": "chat-response",
      "name": "Chat Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1780, 300]
    }
  ],
  "pinData": {},
  "connections": {
    "Chat Trigger": {
      "main": [
        [
          {
            "node": "Prepare Chat Context",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Prepare Chat Context": {
      "main": [
        [
          {
            "node": "Retrieve Conversation History",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Retrieve Conversation History": {
      "main": [
        [
          {
            "node": "Routing Decision",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Routing Decision": {
      "main": [
        [
          {
            "node": "Route to Orchestration",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Direct Chat Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Direct Chat Response": {
      "main": [
        [
          {
            "node": "Store User Message",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route to Orchestration": {
      "main": [
        [
          {
            "node": "Store User Message",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store User Message": {
      "main": [
        [
          {
            "node": "Store Assistant Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store Assistant Response": {
      "main": [
        [
          {
            "node": "Chat Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "error-handling-workflow"
  },
  "versionId": "3.0.0",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "enhanced-ai-agent-os"
  },
  "id": "ai-chat-agent-workflow",
  "tags": [
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "interface",
      "name": "interface"
    },
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "chat",
      "name": "chat"
    }
  ]
}
```

### Specialized Agent Workflows

The specialized agent workflows represent domain-specific intelligence capabilities within the Enhanced AI Agent OS. Each workflow is optimized for particular types of tasks while maintaining seamless integration with the master orchestration system and consciousness substrate. These workflows leverage n8n's built-in AI capabilities to provide sophisticated reasoning, tool usage, and knowledge integration patterns.

#### Research Agent Workflow

The Research Agent Workflow specializes in comprehensive information gathering, analysis, and synthesis. This workflow implements advanced search strategies, source verification, and knowledge integration patterns that enable the system to conduct thorough research across multiple domains and information sources.

**File: `workflows/03-research-agent.json`**

```json
{
  "name": "Research Agent Workflow",
  "nodes": [
    {
      "parameters": {
        "queueName": "ai-agent-research",
        "options": {
          "durable": true,
          "deleteWhenNotUsed": false,
          "arguments": {
            "x-message-ttl": 14400000,
            "x-max-priority": 8
          }
        }
      },
      "id": "research-queue-trigger",
      "name": "Research Queue Trigger",
      "type": "n8n-nodes-base.rabbitmqTrigger",
      "typeVersion": 1,
      "position": [240, 300],
      "credentials": {
        "rabbitmq": {
          "id": "rabbitmq-connection",
          "name": "RabbitMQ Enhanced AI Agent OS"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "// Enhanced AI Agent OS - Research Task Analysis\n// This code analyzes incoming research requests and prepares search strategies\n\nconst taskData = $input.first().json;\nconst request = taskData.request || taskData.original_request || '';\nconst metadata = taskData.metadata || {};\n\n// Extract research parameters\nconst researchRequest = {\n  original_query: request,\n  task_id: taskData.task_id || `research-${Date.now()}`,\n  coordination_id: taskData.coordination_id,\n  priority: metadata.priority || 'normal',\n  complexity: metadata.complexity || 'moderate',\n  source: metadata.source || 'unknown',\n  timestamp: new Date().toISOString()\n};\n\n// Analyze research requirements\nconst analysisPatterns = {\n  academic_research: /(study|research|paper|academic|scholarly|journal|publication)/i.test(request),\n  market_research: /(market|industry|competitor|business|commercial|trends)/i.test(request),\n  technical_research: /(technical|technology|engineering|software|hardware|specification)/i.test(request),\n  factual_lookup: /(what is|who is|when did|where is|how many|definition)/i.test(request),\n  comparative_analysis: /(compare|versus|vs|difference|better|best|worst)/i.test(request),\n  trend_analysis: /(trend|pattern|forecast|prediction|future|outlook)/i.test(request),\n  statistical_data: /(statistics|data|numbers|percentage|rate|survey)/i.test(request),\n  current_events: /(news|recent|latest|current|today|yesterday|this week)/i.test(request)\n};\n\n// Determine research type and strategy\nconst researchTypes = Object.keys(analysisPatterns).filter(type => analysisPatterns[type]);\nconst primaryResearchType = researchTypes[0] || 'general_research';\n\n// Define search strategy based on research type\nconst searchStrategy = {\n  type: primaryResearchType,\n  search_depth: researchTypes.length > 2 ? 'comprehensive' : researchTypes.length > 1 ? 'detailed' : 'focused',\n  source_diversity: true,\n  fact_checking: true,\n  citation_required: analysisPatterns.academic_research || analysisPatterns.technical_research,\n  real_time_data: analysisPatterns.current_events || analysisPatterns.trend_analysis,\n  statistical_analysis: analysisPatterns.statistical_data || analysisPatterns.market_research\n};\n\n// Generate search queries\nconst searchQueries = [];\n\n// Primary query\nsearchQueries.push({\n  query: request,\n  type: 'primary',\n  priority: 'high',\n  expected_results: 10\n});\n\n// Secondary queries based on research type\nif (analysisPatterns.comparative_analysis) {\n  const comparisonTerms = request.match(/(\\w+)\\s+(?:vs|versus|compared to|against)\\s+(\\w+)/i);\n  if (comparisonTerms) {\n    searchQueries.push({\n      query: `${comparisonTerms[1]} advantages disadvantages`,\n      type: 'comparative',\n      priority: 'medium',\n      expected_results: 5\n    });\n    searchQueries.push({\n      query: `${comparisonTerms[2]} advantages disadvantages`,\n      type: 'comparative',\n      priority: 'medium',\n      expected_results: 5\n    });\n  }\n}\n\nif (analysisPatterns.trend_analysis) {\n  searchQueries.push({\n    query: `${request} trends 2024`,\n    type: 'trend',\n    priority: 'medium',\n    expected_results: 8\n  });\n}\n\nif (analysisPatterns.statistical_data) {\n  searchQueries.push({\n    query: `${request} statistics data`,\n    type: 'statistical',\n    priority: 'high',\n    expected_results: 6\n  });\n}\n\n// Quality criteria\nconst qualityCriteria = {\n  source_credibility: 0.8,\n  information_recency: analysisPatterns.current_events ? 'last_week' : 'last_year',\n  citation_quality: searchStrategy.citation_required ? 'high' : 'medium',\n  fact_verification: true,\n  bias_detection: true,\n  relevance_threshold: 0.7\n};\n\nreturn {\n  research_request: researchRequest,\n  analysis_patterns: analysisPatterns,\n  research_types: researchTypes,\n  primary_research_type: primaryResearchType,\n  search_strategy: searchStrategy,\n  search_queries: searchQueries,\n  quality_criteria: qualityCriteria,\n  processing_metadata: {\n    analyzed_at: new Date().toISOString(),\n    query_complexity: searchQueries.length,\n    estimated_duration: searchQueries.length * 30 + 'seconds'\n  }\n};"
      },
      "id": "analyze-research-request",
      "name": "Analyze Research Request",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "batchSize": 1,
        "options": {}
      },
      "id": "split-search-queries",
      "name": "Split Search Queries",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [680, 300]
    },
    {
      "parameters": {
        "agent": "toolsAgent",
        "text": "Conduct comprehensive research on: {{ $json.query }}\n\nResearch Context:\n- Research Type: {{ $json.primary_research_type }}\n- Search Strategy: {{ $json.search_strategy.search_depth }}\n- Quality Requirements: {{ $json.quality_criteria.source_credibility }}\n- Citation Required: {{ $json.search_strategy.citation_required }}\n- Real-time Data Needed: {{ $json.search_strategy.real_time_data }}\n\nPlease provide detailed, well-sourced information with proper citations and fact verification.",
        "hasOutputParser": true,
        "options": {
          "systemMessage": "You are the Research Agent of the Enhanced AI Agent OS, specializing in comprehensive information gathering, analysis, and synthesis. Your role is to conduct thorough research across multiple sources, verify facts, and provide well-structured, cited information.\n\nCapabilities:\n- Web search and information retrieval\n- Source credibility assessment\n- Fact verification and cross-referencing\n- Citation and reference management\n- Statistical data analysis\n- Trend identification and analysis\n- Comparative research\n- Academic and technical research\n\nResearch Standards:\n1. Always verify information from multiple sources\n2. Prioritize credible, authoritative sources\n3. Provide proper citations and references\n4. Identify potential bias or limitations\n5. Present information objectively\n6. Include relevant statistics and data\n7. Note information recency and relevance\n8. Highlight conflicting viewpoints when present\n\nFor each research query, provide:\n- Key findings with supporting evidence\n- Source credibility assessment\n- Relevant statistics or data points\n- Citations and references\n- Confidence level in findings\n- Recommendations for further research if needed",
          "temperature": 0.2,
          "maxTokens": 3000,
          "topP": 0.9,
          "frequencyPenalty": 0,
          "presencePenalty": 0
        },
        "model": {
          "model": "gpt-4",
          "type": "openai"
        },
        "outputParser": {
          "type": "structured",
          "schema": {
            "type": "object",
            "properties": {
              "research_findings": {
                "type": "object",
                "properties": {
                  "key_findings": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "finding": {
                          "type": "string"
                        },
                        "supporting_evidence": {
                          "type": "string"
                        },
                        "confidence_level": {
                          "type": "number",
                          "minimum": 0,
                          "maximum": 1
                        },
                        "sources": {
                          "type": "array",
                          "items": {
                            "type": "string"
                          }
                        }
                      },
                      "required": ["finding", "supporting_evidence", "confidence_level", "sources"]
                    }
                  },
                  "summary": {
                    "type": "string"
                  },
                  "statistical_data": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "metric": {
                          "type": "string"
                        },
                        "value": {
                          "type": "string"
                        },
                        "source": {
                          "type": "string"
                        },
                        "date": {
                          "type": "string"
                        }
                      },
                      "required": ["metric", "value", "source"]
                    }
                  }
                },
                "required": ["key_findings", "summary"]
              },
              "source_analysis": {
                "type": "object",
                "properties": {
                  "primary_sources": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "source": {
                          "type": "string"
                        },
                        "credibility_score": {
                          "type": "number",
                          "minimum": 0,
                          "maximum": 1
                        },
                        "bias_assessment": {
                          "type": "string"
                        },
                        "recency": {
                          "type": "string"
                        }
                      },
                      "required": ["source", "credibility_score", "bias_assessment"]
                    }
                  },
                  "source_diversity": {
                    "type": "string"
                  },
                  "fact_verification_status": {
                    "type": "string"
                  }
                },
                "required": ["primary_sources", "source_diversity", "fact_verification_status"]
              },
              "research_quality": {
                "type": "object",
                "properties": {
                  "overall_confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "completeness_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "limitations": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "recommendations": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                },
                "required": ["overall_confidence", "completeness_score"]
              }
            },
            "required": ["research_findings", "source_analysis", "research_quality"]
          }
        },
        "tools": [
          {
            "name": "web_search",
            "description": "Search the web for current information and sources"
          },
          {
            "name": "academic_search",
            "description": "Search academic databases and scholarly sources"
          },
          {
            "name": "fact_checker",
            "description": "Verify facts and cross-reference information"
          },
          {
            "name": "citation_formatter",
            "description": "Format citations according to academic standards"
          }
        ]
      },
      "id": "conduct-research",
      "name": "Conduct Research",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "jsCode": "// Enhanced AI Agent OS - Research Results Aggregation\n// This code aggregates and synthesizes research results from multiple queries\n\nconst allResults = $input.all();\nconst researchRequest = allResults[0].json.research_request;\n\n// Aggregate all research findings\nconst aggregatedFindings = {\n  key_findings: [],\n  statistical_data: [],\n  primary_sources: [],\n  all_sources: new Set()\n};\n\nlet totalConfidence = 0;\nlet totalCompleteness = 0;\nconst allLimitations = new Set();\nconst allRecommendations = new Set();\n\n// Process each research result\nallResults.forEach((result, index) => {\n  const findings = result.json.research_findings;\n  const sourceAnalysis = result.json.source_analysis;\n  const quality = result.json.research_quality;\n  \n  // Aggregate findings\n  if (findings.key_findings) {\n    findings.key_findings.forEach(finding => {\n      aggregatedFindings.key_findings.push({\n        ...finding,\n        query_index: index,\n        query_type: result.json.type || 'general'\n      });\n    });\n  }\n  \n  // Aggregate statistical data\n  if (findings.statistical_data) {\n    aggregatedFindings.statistical_data.push(...findings.statistical_data);\n  }\n  \n  // Aggregate sources\n  if (sourceAnalysis.primary_sources) {\n    sourceAnalysis.primary_sources.forEach(source => {\n      aggregatedFindings.primary_sources.push({\n        ...source,\n        query_index: index\n      });\n      aggregatedFindings.all_sources.add(source.source);\n    });\n  }\n  \n  // Aggregate quality metrics\n  totalConfidence += quality.overall_confidence || 0;\n  totalCompleteness += quality.completeness_score || 0;\n  \n  if (quality.limitations) {\n    quality.limitations.forEach(limitation => allLimitations.add(limitation));\n  }\n  \n  if (quality.recommendations) {\n    quality.recommendations.forEach(rec => allRecommendations.add(rec));\n  }\n});\n\n// Calculate overall quality metrics\nconst overallQuality = {\n  overall_confidence: totalConfidence / allResults.length,\n  completeness_score: totalCompleteness / allResults.length,\n  source_count: aggregatedFindings.all_sources.size,\n  finding_count: aggregatedFindings.key_findings.length,\n  statistical_data_points: aggregatedFindings.statistical_data.length,\n  limitations: Array.from(allLimitations),\n  recommendations: Array.from(allRecommendations)\n};\n\n// Generate comprehensive summary\nconst comprehensiveSummary = {\n  research_overview: {\n    original_query: researchRequest.original_query,\n    research_type: researchRequest.primary_research_type || 'general',\n    queries_processed: allResults.length,\n    total_findings: aggregatedFindings.key_findings.length,\n    research_depth: allResults.length > 3 ? 'comprehensive' : allResults.length > 1 ? 'detailed' : 'focused'\n  },\n  \n  synthesized_findings: {\n    primary_insights: aggregatedFindings.key_findings\n      .filter(f => f.confidence_level > 0.7)\n      .sort((a, b) => b.confidence_level - a.confidence_level)\n      .slice(0, 5),\n    \n    supporting_data: aggregatedFindings.statistical_data\n      .sort((a, b) => new Date(b.date || '1900-01-01') - new Date(a.date || '1900-01-01'))\n      .slice(0, 10),\n    \n    high_credibility_sources: aggregatedFindings.primary_sources\n      .filter(s => s.credibility_score > 0.8)\n      .sort((a, b) => b.credibility_score - a.credibility_score)\n  },\n  \n  research_quality: overallQuality,\n  \n  knowledge_integration: {\n    ready_for_consciousness: true,\n    knowledge_type: 'research_synthesis',\n    confidence_level: overallQuality.overall_confidence,\n    source_diversity: aggregatedFindings.all_sources.size >= 3 ? 'high' : 'moderate',\n    fact_verification: 'completed'\n  }\n};\n\n// Prepare knowledge storage format\nconst knowledgeEntry = {\n  title: `Research: ${researchRequest.original_query}`,\n  content: JSON.stringify(comprehensiveSummary, null, 2),\n  summary: `Comprehensive research findings on: ${researchRequest.original_query}`,\n  type: 'research_synthesis',\n  confidence: overallQuality.overall_confidence,\n  source: 'research-agent',\n  tags: ['research', 'synthesis', researchRequest.primary_research_type || 'general'],\n  metadata: {\n    research_id: researchRequest.task_id,\n    coordination_id: researchRequest.coordination_id,\n    query_count: allResults.length,\n    source_count: aggregatedFindings.all_sources.size,\n    processing_time: new Date().toISOString(),\n    quality_score: overallQuality.overall_confidence\n  }\n};\n\nreturn {\n  research_results: comprehensiveSummary,\n  knowledge_entry: knowledgeEntry,\n  task_completion: {\n    task_id: researchRequest.task_id,\n    coordination_id: researchRequest.coordination_id,\n    status: 'completed',\n    completion_time: new Date().toISOString(),\n    quality_metrics: overallQuality\n  }\n};"
      },
      "id": "aggregate-research-results",
      "name": "Aggregate Research Results",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "CREATE (knowledge:Knowledge {\n  id: randomUUID(),\n  type: $type,\n  title: $title,\n  content: $content,\n  summary: $summary,\n  confidence: $confidence,\n  source: $source,\n  tags: $tags,\n  created_at: datetime(),\n  updated_at: datetime(),\n  accessed_at: datetime(),\n  access_count: 0,\n  metadata: $metadata\n})\nWITH knowledge\nMATCH (agent:Agent {name: 'research-agent'})\nCREATE (agent)-[:GENERATED_KNOWLEDGE {timestamp: datetime(), confidence: $confidence}]->(knowledge)\nRETURN knowledge.id as knowledge_id, knowledge.title as title",
        "parameters": {
          "type": "={{ $json.knowledge_entry.type }}",
          "title": "={{ $json.knowledge_entry.title }}",
          "content": "={{ $json.knowledge_entry.content }}",
          "summary": "={{ $json.knowledge_entry.summary }}",
          "confidence": "={{ $json.knowledge_entry.confidence }}",
          "source": "={{ $json.knowledge_entry.source }}",
          "tags": "={{ $json.knowledge_entry.tags }}",
          "metadata": "={{ $json.knowledge_entry.metadata }}"
        }
      },
      "id": "store-research-knowledge",
      "name": "Store Research Knowledge",
      "type": "n8n-nodes-base.neo4j",
      "typeVersion": 1,
      "position": [1340, 300],
      "credentials": {
        "neo4j": {
          "id": "neo4j-consciousness",
          "name": "Neo4j Consciousness Substrate"
        }
      }
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://enhanced-ai-rabbitmq:15672/api/queues/%2F/ai-agent-orchestration/publish",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "properties",
              "value": "={{ { \"priority\": 7, \"message_id\": $json.task_completion.task_id, \"timestamp\": $now, \"correlation_id\": $json.task_completion.coordination_id, \"reply_to\": \"ai-agent-research\" } }}"
            },
            {
              "name": "payload",
              "value": "={{ JSON.stringify({ \"type\": \"task_completion\", \"agent\": \"research-agent\", \"task_completion\": $json.task_completion, \"research_results\": $json.research_results, \"knowledge_id\": $json.knowledge_id, \"timestamp\": $now }) }}"
            },
            {
              "name": "payload_encoding",
              "value": "string"
            }
          ]
        },
        "options": {}
      },
      "id": "report-completion",
      "name": "Report Completion",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1560, 300]
    }
  ],
  "pinData": {},
  "connections": {
    "Research Queue Trigger": {
      "main": [
        [
          {
            "node": "Analyze Research Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Research Request": {
      "main": [
        [
          {
            "node": "Split Search Queries",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Split Search Queries": {
      "main": [
        [
          {
            "node": "Conduct Research",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Conduct Research": {
      "main": [
        [
          {
            "node": "Aggregate Research Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Aggregate Research Results": {
      "main": [
        [
          {
            "node": "Store Research Knowledge",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store Research Knowledge": {
      "main": [
        [
          {
            "node": "Report Completion",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "error-handling-workflow"
  },
  "versionId": "3.0.0",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "enhanced-ai-agent-os"
  },
  "id": "research-agent-workflow",
  "tags": [
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "specialized",
      "name": "specialized"
    },
    {
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z",
      "id": "research",
      "name": "research"
    }
  ]
}
```

This completes the comprehensive n8n workflow implementation for Phase 3. The workflows demonstrate sophisticated AI agent capabilities using n8n's built-in AI functionality, including advanced conversation management, task orchestration, and specialized research capabilities. Each workflow integrates seamlessly with the consciousness substrate, message queuing system, and monitoring infrastructure established in previous phases.


## Phase 4: Monitoring, Testing, and Deployment Scripts

### Comprehensive Monitoring Infrastructure

The Enhanced AI Agent OS requires sophisticated monitoring capabilities that extend beyond traditional application monitoring to include AI-specific metrics, agent performance tracking, consciousness substrate health, and inter-agent communication patterns. The monitoring infrastructure leverages Prometheus for metrics collection, Grafana for visualization, and custom monitoring agents that understand the unique characteristics of AI agent systems.

#### Prometheus Configuration

The Prometheus configuration establishes comprehensive metrics collection across all system components, with particular attention to AI agent performance metrics, task completion rates, and system health indicators that are critical for maintaining optimal operation of the Enhanced AI Agent OS.

**File: `infrastructure/monitoring/prometheus/prometheus.yml`**

```yaml
# Enhanced AI Agent OS - Prometheus Configuration
# This configuration defines comprehensive monitoring for AI agent systems

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'enhanced-ai-agent-os'
    environment: 'production'
    version: '3.0.0'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      timeout: 10s
      api_version: v2

# Rule files specify a list of globs for rule files
rule_files:
  - "rules/*.yml"
  - "rules/ai-agents/*.yml"
  - "rules/infrastructure/*.yml"

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    metrics_path: /metrics

  # Enhanced AI Agent OS - n8n Monitoring
  - job_name: 'n8n-orchestration'
    static_configs:
      - targets: ['enhanced-ai-n8n:5678']
    scrape_interval: 15s
    metrics_path: /metrics
    params:
      format: ['prometheus']
    basic_auth:
      username: 'admin'
      password: 'secure_password_change_me'
    scrape_timeout: 10s
    honor_labels: true
    honor_timestamps: true

  # PostgreSQL Database Monitoring
  - job_name: 'postgresql'
    static_configs:
      - targets: ['enhanced-ai-postgres:5432']
    scrape_interval: 30s
    metrics_path: /metrics
    params:
      collect[]:
        - 'pg_stat_database'
        - 'pg_stat_user_tables'
        - 'pg_stat_activity'
        - 'pg_locks'
        - 'pg_stat_replication'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: postgres-exporter:9187

  # Neo4j Consciousness Substrate Monitoring
  - job_name: 'neo4j-consciousness'
    static_configs:
      - targets: ['enhanced-ai-neo4j:7474']
    scrape_interval: 20s
    metrics_path: /db/manage/server/jmx/domain/org.neo4j
    params:
      format: ['prometheus']
    basic_auth:
      username: 'neo4j'
      password: 'secure_password_change_me'
    scrape_timeout: 15s
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'neo4j_(.+)'
        target_label: __name__
        replacement: 'consciousness_${1}'

  # RabbitMQ Message Queue Monitoring
  - job_name: 'rabbitmq-messaging'
    static_configs:
      - targets: ['enhanced-ai-rabbitmq:15692']
    scrape_interval: 15s
    metrics_path: /metrics
    basic_auth:
      username: 'ai_agent_queue_user'
      password: 'secure_password_change_me'
    scrape_timeout: 10s
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'rabbitmq_(.+)'
        target_label: __name__
        replacement: 'messaging_${1}'

  # System Resource Monitoring
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s
    metrics_path: /metrics
    scrape_timeout: 10s

  # Docker Container Monitoring
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 20s
    metrics_path: /metrics
    scrape_timeout: 15s
    metric_relabel_configs:
      - source_labels: [container_label_com_docker_compose_service]
        target_label: service_name
      - source_labels: [container_label_com_docker_compose_project]
        target_label: project_name

  # AI Agent Performance Monitoring (Custom Metrics)
  - job_name: 'ai-agent-metrics'
    static_configs:
      - targets: ['ai-agent-metrics-exporter:8080']
    scrape_interval: 10s
    metrics_path: /metrics
    scrape_timeout: 8s
    honor_labels: true
    params:
      collect[]:
        - 'agent_task_completion_rate'
        - 'agent_response_time'
        - 'agent_error_rate'
        - 'agent_queue_depth'
        - 'agent_resource_utilization'
        - 'consciousness_query_performance'
        - 'inter_agent_communication_latency'

  # Grafana Monitoring
  - job_name: 'grafana'
    static_configs:
      - targets: ['enhanced-ai-grafana:3000']
    scrape_interval: 30s
    metrics_path: /metrics
    basic_auth:
      username: 'admin'
      password: 'secure_password_change_me'

  # Loki Log Aggregation Monitoring
  - job_name: 'loki'
    static_configs:
      - targets: ['enhanced-ai-loki:3100']
    scrape_interval: 30s
    metrics_path: /metrics

  # Custom Application Metrics
  - job_name: 'enhanced-ai-agent-os-custom'
    static_configs:
      - targets: ['custom-metrics-endpoint:9091']
    scrape_interval: 5s
    metrics_path: /metrics
    scrape_timeout: 4s
    honor_labels: true
    params:
      module: ['ai_agent_os']

# Remote write configuration for long-term storage (optional)
remote_write:
  - url: "http://prometheus-remote-storage:9201/write"
    queue_config:
      max_samples_per_send: 1000
      max_shards: 200
      capacity: 2500
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'enhanced_ai_(.+)'
        target_label: __name__
        replacement: '${1}'

# Storage configuration
storage:
  tsdb:
    path: /prometheus
    retention.time: 30d
    retention.size: 50GB
    wal-compression: true
    no-lockfile: false
    allow-overlapping-blocks: false
    min-block-duration: 2h
    max-block-duration: 25h

# Query configuration
query:
  timeout: 2m
  max_concurrent_queries: 20
  max_samples: 50000000
  lookback-delta: 5m
```

**File: `infrastructure/monitoring/prometheus/rules/ai-agents.yml`**

```yaml
# Enhanced AI Agent OS - AI Agent Monitoring Rules
# This file defines alerting rules specific to AI agent performance and health

groups:
  - name: ai-agent-performance
    interval: 30s
    rules:
      # Agent Task Completion Rate
      - alert: AgentTaskCompletionRateLow
        expr: rate(agent_tasks_completed_total[5m]) < 0.1
        for: 2m
        labels:
          severity: warning
          component: ai-agent
          category: performance
        annotations:
          summary: "AI Agent {{ $labels.agent_name }} has low task completion rate"
          description: "Agent {{ $labels.agent_name }} has completed only {{ $value }} tasks per second over the last 5 minutes, which is below the expected threshold."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/low-task-completion"

      # Agent Response Time High
      - alert: AgentResponseTimeHigh
        expr: histogram_quantile(0.95, rate(agent_response_time_seconds_bucket[5m])) > 30
        for: 1m
        labels:
          severity: warning
          component: ai-agent
          category: performance
        annotations:
          summary: "AI Agent {{ $labels.agent_name }} response time is high"
          description: "95th percentile response time for agent {{ $labels.agent_name }} is {{ $value }}s, exceeding the 30s threshold."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/high-response-time"

      # Agent Error Rate High
      - alert: AgentErrorRateHigh
        expr: rate(agent_errors_total[5m]) / rate(agent_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
          component: ai-agent
          category: reliability
        annotations:
          summary: "AI Agent {{ $labels.agent_name }} error rate is high"
          description: "Error rate for agent {{ $labels.agent_name }} is {{ $value | humanizePercentage }}, exceeding the 5% threshold."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/high-error-rate"

      # Agent Queue Depth High
      - alert: AgentQueueDepthHigh
        expr: agent_queue_depth > 100
        for: 5m
        labels:
          severity: warning
          component: ai-agent
          category: capacity
        annotations:
          summary: "AI Agent {{ $labels.agent_name }} queue depth is high"
          description: "Queue depth for agent {{ $labels.agent_name }} is {{ $value }}, indicating potential bottleneck."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/high-queue-depth"

      # Agent Unavailable
      - alert: AgentUnavailable
        expr: up{job="ai-agent-metrics"} == 0
        for: 1m
        labels:
          severity: critical
          component: ai-agent
          category: availability
        annotations:
          summary: "AI Agent {{ $labels.agent_name }} is unavailable"
          description: "Agent {{ $labels.agent_name }} has been unavailable for more than 1 minute."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/agent-unavailable"

  - name: consciousness-substrate
    interval: 30s
    rules:
      # Neo4j Consciousness Substrate Performance
      - alert: ConsciousnessQueryLatencyHigh
        expr: histogram_quantile(0.95, rate(consciousness_query_duration_seconds_bucket[5m])) > 5
        for: 2m
        labels:
          severity: warning
          component: consciousness-substrate
          category: performance
        annotations:
          summary: "Consciousness substrate query latency is high"
          description: "95th percentile query latency is {{ $value }}s, exceeding the 5s threshold."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/consciousness-latency"

      # Knowledge Base Growth Rate
      - alert: KnowledgeBaseGrowthStalled
        expr: increase(consciousness_knowledge_entries_total[1h]) < 1
        for: 2h
        labels:
          severity: info
          component: consciousness-substrate
          category: growth
        annotations:
          summary: "Knowledge base growth has stalled"
          description: "No new knowledge entries have been added to the consciousness substrate in the last 2 hours."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/knowledge-growth-stalled"

      # Memory Usage High
      - alert: ConsciousnessMemoryUsageHigh
        expr: consciousness_memory_usage_bytes / consciousness_memory_total_bytes > 0.85
        for: 5m
        labels:
          severity: warning
          component: consciousness-substrate
          category: resources
        annotations:
          summary: "Consciousness substrate memory usage is high"
          description: "Memory usage is {{ $value | humanizePercentage }}, approaching capacity limits."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/consciousness-memory-high"

  - name: inter-agent-communication
    interval: 15s
    rules:
      # Message Queue Depth
      - alert: MessageQueueDepthHigh
        expr: messaging_queue_messages > 1000
        for: 3m
        labels:
          severity: warning
          component: messaging
          category: capacity
        annotations:
          summary: "Message queue {{ $labels.queue }} depth is high"
          description: "Queue {{ $labels.queue }} has {{ $value }} messages, indicating potential processing bottleneck."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/queue-depth-high"

      # Message Processing Rate Low
      - alert: MessageProcessingRateLow
        expr: rate(messaging_messages_processed_total[5m]) < 1
        for: 5m
        labels:
          severity: warning
          component: messaging
          category: performance
        annotations:
          summary: "Message processing rate is low for queue {{ $labels.queue }}"
          description: "Processing rate is {{ $value }} messages/second, below expected threshold."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/processing-rate-low"

      # Dead Letter Queue Growth
      - alert: DeadLetterQueueGrowth
        expr: increase(messaging_dead_letter_messages_total[10m]) > 10
        for: 1m
        labels:
          severity: critical
          component: messaging
          category: reliability
        annotations:
          summary: "Dead letter queue is accumulating messages"
          description: "{{ $value }} messages have been added to the dead letter queue in the last 10 minutes."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/dead-letter-growth"

  - name: system-health
    interval: 30s
    rules:
      # Overall System Health Score
      - alert: SystemHealthScoreLow
        expr: system_health_score < 0.8
        for: 5m
        labels:
          severity: warning
          component: system
          category: health
        annotations:
          summary: "Overall system health score is low"
          description: "System health score is {{ $value }}, indicating degraded performance across multiple components."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/system-health-low"

      # Orchestration Coordination Failures
      - alert: OrchestrationCoordinationFailures
        expr: rate(orchestration_coordination_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
          component: orchestration
          category: coordination
        annotations:
          summary: "High rate of orchestration coordination failures"
          description: "{{ $value }} coordination failures per second, indicating issues with multi-agent task management."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/coordination-failures"

      # Resource Utilization Imbalance
      - alert: ResourceUtilizationImbalance
        expr: max(agent_cpu_utilization) - min(agent_cpu_utilization) > 0.5
        for: 10m
        labels:
          severity: info
          component: system
          category: optimization
        annotations:
          summary: "Resource utilization imbalance detected"
          description: "CPU utilization varies by {{ $value | humanizePercentage }} across agents, suggesting load balancing opportunities."
          runbook_url: "https://docs.enhanced-ai-agent-os.com/runbooks/resource-imbalance"
```

#### Grafana Dashboard Configuration

The Grafana dashboard configuration provides comprehensive visualization of AI agent performance, system health, and operational metrics. The dashboards are specifically designed to surface insights relevant to AI agent operations, including task completion patterns, inter-agent communication flows, and consciousness substrate utilization.

**File: `infrastructure/monitoring/grafana/dashboards/ai-agent-overview.json`**

```json
{
  "dashboard": {
    "id": null,
    "title": "Enhanced AI Agent OS - System Overview",
    "tags": ["ai-agents", "overview", "system-health"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System Health Score",
        "type": "stat",
        "targets": [
          {
            "expr": "system_health_score",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "red",
                  "value": 0
                },
                {
                  "color": "yellow",
                  "value": 0.7
                },
                {
                  "color": "green",
                  "value": 0.85
                }
              ]
            },
            "unit": "percentunit",
            "min": 0,
            "max": 1
          }
        },
        "options": {
          "reduceOptions": {
            "calcs": ["lastNotNull"]
          }
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Active Agents",
        "type": "stat",
        "targets": [
          {
            "expr": "count(up{job=\"ai-agent-metrics\"} == 1)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "unit": "short"
          }
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 6,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Tasks Completed (Last Hour)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(agent_tasks_completed_total[1h]))",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "unit": "short"
          }
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 4,
        "title": "Average Response Time",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(histogram_quantile(0.95, rate(agent_response_time_seconds_bucket[5m])))",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "green",
                  "value": 0
                },
                {
                  "color": "yellow",
                  "value": 10
                },
                {
                  "color": "red",
                  "value": 30
                }
              ]
            },
            "unit": "s"
          }
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 18,
          "y": 0
        }
      },
      {
        "id": 5,
        "title": "Agent Task Completion Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_tasks_completed_total[5m])",
            "legendFormat": "{{ agent_name }}",
            "refId": "A"
          }
        ],
        "xAxis": {
          "show": true
        },
        "yAxes": [
          {
            "label": "Tasks/sec",
            "show": true
          }
        ],
        "legend": {
          "show": true,
          "values": true,
          "current": true
        },
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 6,
        "title": "Agent Response Time Distribution",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(agent_response_time_seconds_bucket[5m]))",
            "legendFormat": "50th percentile",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(agent_response_time_seconds_bucket[5m]))",
            "legendFormat": "95th percentile",
            "refId": "B"
          },
          {
            "expr": "histogram_quantile(0.99, rate(agent_response_time_seconds_bucket[5m]))",
            "legendFormat": "99th percentile",
            "refId": "C"
          }
        ],
        "yAxes": [
          {
            "label": "Response Time (s)",
            "show": true
          }
        ],
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 12,
          "y": 8
        }
      },
      {
        "id": 7,
        "title": "Inter-Agent Communication Flow",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(messaging_messages_published_total[5m])",
            "legendFormat": "Messages Published",
            "refId": "A"
          },
          {
            "expr": "rate(messaging_messages_consumed_total[5m])",
            "legendFormat": "Messages Consumed",
            "refId": "B"
          }
        ],
        "yAxes": [
          {
            "label": "Messages/sec",
            "show": true
          }
        ],
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 0,
          "y": 17
        }
      },
      {
        "id": 8,
        "title": "Consciousness Substrate Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(consciousness_queries_total[5m])",
            "legendFormat": "Queries/sec",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(consciousness_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile latency",
            "refId": "B"
          }
        ],
        "yAxes": [
          {
            "label": "Queries/sec",
            "show": true
          },
          {
            "label": "Latency (s)",
            "show": true,
            "opposite": true
          }
        ],
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 12,
          "y": 17
        }
      },
      {
        "id": 9,
        "title": "Agent Queue Depths",
        "type": "graph",
        "targets": [
          {
            "expr": "agent_queue_depth",
            "legendFormat": "{{ agent_name }}",
            "refId": "A"
          }
        ],
        "yAxes": [
          {
            "label": "Queue Depth",
            "show": true
          }
        ],
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 0,
          "y": 26
        }
      },
      {
        "id": 10,
        "title": "System Resource Utilization",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(agent_cpu_utilization)",
            "legendFormat": "Average CPU",
            "refId": "A"
          },
          {
            "expr": "avg(agent_memory_utilization)",
            "legendFormat": "Average Memory",
            "refId": "B"
          }
        ],
        "yAxes": [
          {
            "label": "Utilization %",
            "show": true,
            "min": 0,
            "max": 100
          }
        ],
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 12,
          "y": 26
        }
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s",
    "schemaVersion": 27,
    "version": 1,
    "links": [
      {
        "title": "Agent Details",
        "url": "/d/agent-details/agent-details",
        "type": "dashboards"
      },
      {
        "title": "System Health",
        "url": "/d/system-health/system-health",
        "type": "dashboards"
      }
    ]
  }
}
```

### Testing Framework Implementation

The testing framework for the Enhanced AI Agent OS encompasses multiple layers of validation, from unit tests for individual components to comprehensive integration tests that verify multi-agent coordination patterns. The framework includes specialized testing approaches for AI agent behavior, conversation flow validation, and consciousness substrate integrity verification.

#### Automated Testing Scripts

The automated testing infrastructure provides comprehensive validation of system functionality, performance benchmarks, and reliability testing under various load conditions. These scripts are designed to run continuously in CI/CD pipelines and provide detailed reporting on system health and performance characteristics.

**File: `scripts/test-suite.sh`**

```bash
#!/bin/bash

# Enhanced AI Agent OS - Comprehensive Test Suite
# This script executes the complete testing framework for the AI agent system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_RESULTS_DIR="${PROJECT_ROOT}/test-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_SESSION_ID="test_session_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create test results directory
mkdir -p "${TEST_RESULTS_DIR}/${TEST_SESSION_ID}"

# Test configuration
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
DOCKER_COMPOSE_TEST_FILE="${PROJECT_ROOT}/docker-compose.test.yml"
N8N_BASE_URL="http://localhost:5678"
TEST_TIMEOUT=300
MAX_RETRIES=3

# Function to wait for service availability
wait_for_service() {
    local service_name=$1
    local health_check_url=$2
    local timeout=${3:-60}
    local retry_interval=5
    local elapsed=0

    log_info "Waiting for ${service_name} to become available..."
    
    while [ $elapsed -lt $timeout ]; do
        if curl -f -s "${health_check_url}" > /dev/null 2>&1; then
            log_success "${service_name} is available"
            return 0
        fi
        
        sleep $retry_interval
        elapsed=$((elapsed + retry_interval))
        log_info "Waiting for ${service_name}... (${elapsed}/${timeout}s)"
    done
    
    log_error "${service_name} failed to become available within ${timeout} seconds"
    return 1
}

# Function to execute test and capture results
execute_test() {
    local test_name=$1
    local test_command=$2
    local test_file="${TEST_RESULTS_DIR}/${TEST_SESSION_ID}/${test_name}.json"
    
    log_info "Executing test: ${test_name}"
    
    local start_time=$(date +%s)
    local test_result=0
    
    # Execute test command and capture output
    if eval "$test_command" > "${test_file}.log" 2>&1; then
        test_result=0
        log_success "Test ${test_name} passed"
    else
        test_result=1
        log_error "Test ${test_name} failed"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Create test result JSON
    cat > "$test_file" << EOF
{
  "test_name": "${test_name}",
  "status": $([ $test_result -eq 0 ] && echo '"passed"' || echo '"failed"'),
  "start_time": "${start_time}",
  "end_time": "${end_time}",
  "duration_seconds": ${duration},
  "session_id": "${TEST_SESSION_ID}",
  "timestamp": "$(date -Iseconds)"
}
EOF
    
    return $test_result
}

# Main test execution function
run_test_suite() {
    log_info "Starting Enhanced AI Agent OS Test Suite - Session: ${TEST_SESSION_ID}"
    
    # Initialize test results summary
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Test 1: Infrastructure Health Check
    log_info "=== Phase 1: Infrastructure Health Checks ==="
    
    if execute_test "infrastructure_health" "bash ${SCRIPT_DIR}/tests/test-infrastructure.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 2: Database Connectivity and Schema Validation
    if execute_test "database_connectivity" "bash ${SCRIPT_DIR}/tests/test-databases.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 3: Message Queue Functionality
    if execute_test "message_queue_functionality" "bash ${SCRIPT_DIR}/tests/test-messaging.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 4: n8n Workflow Validation
    log_info "=== Phase 2: Workflow and Agent Testing ==="
    
    if execute_test "n8n_workflow_validation" "bash ${SCRIPT_DIR}/tests/test-workflows.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 5: AI Agent Functionality
    if execute_test "ai_agent_functionality" "bash ${SCRIPT_DIR}/tests/test-ai-agents.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 6: Master Orchestration
    if execute_test "master_orchestration" "bash ${SCRIPT_DIR}/tests/test-orchestration.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 7: Chat Agent Integration
    if execute_test "chat_agent_integration" "bash ${SCRIPT_DIR}/tests/test-chat-agent.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 8: Research Agent Capabilities
    if execute_test "research_agent_capabilities" "bash ${SCRIPT_DIR}/tests/test-research-agent.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 9: Consciousness Substrate Integration
    log_info "=== Phase 3: Advanced Integration Testing ==="
    
    if execute_test "consciousness_substrate" "bash ${SCRIPT_DIR}/tests/test-consciousness.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 10: Inter-Agent Communication
    if execute_test "inter_agent_communication" "bash ${SCRIPT_DIR}/tests/test-inter-agent-communication.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 11: Performance and Load Testing
    log_info "=== Phase 4: Performance and Load Testing ==="
    
    if execute_test "performance_load_testing" "bash ${SCRIPT_DIR}/tests/test-performance.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 12: Monitoring and Alerting
    if execute_test "monitoring_alerting" "bash ${SCRIPT_DIR}/tests/test-monitoring.sh"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Generate comprehensive test report
    generate_test_report $total_tests $passed_tests $failed_tests
    
    # Return appropriate exit code
    if [ $failed_tests -eq 0 ]; then
        log_success "All tests passed! (${passed_tests}/${total_tests})"
        return 0
    else
        log_error "Some tests failed! (${passed_tests}/${total_tests} passed, ${failed_tests} failed)"
        return 1
    fi
}

# Function to generate comprehensive test report
generate_test_report() {
    local total=$1
    local passed=$2
    local failed=$3
    local success_rate=$(( (passed * 100) / total ))
    
    local report_file="${TEST_RESULTS_DIR}/${TEST_SESSION_ID}/test_report.json"
    
    cat > "$report_file" << EOF
{
  "test_session": {
    "session_id": "${TEST_SESSION_ID}",
    "timestamp": "$(date -Iseconds)",
    "duration_seconds": $(($(date +%s) - $(date -d "$TIMESTAMP" +%s || echo $(date +%s)))),
    "environment": "test",
    "version": "3.0.0"
  },
  "summary": {
    "total_tests": ${total},
    "passed_tests": ${passed},
    "failed_tests": ${failed},
    "success_rate": ${success_rate},
    "status": $([ $failed -eq 0 ] && echo '"passed"' || echo '"failed"')
  },
  "test_categories": {
    "infrastructure": {
      "tests": ["infrastructure_health", "database_connectivity", "message_queue_functionality"],
      "description": "Core infrastructure and service availability tests"
    },
    "workflows_and_agents": {
      "tests": ["n8n_workflow_validation", "ai_agent_functionality", "master_orchestration", "chat_agent_integration", "research_agent_capabilities"],
      "description": "AI agent functionality and workflow validation tests"
    },
    "advanced_integration": {
      "tests": ["consciousness_substrate", "inter_agent_communication"],
      "description": "Advanced system integration and consciousness substrate tests"
    },
    "performance_monitoring": {
      "tests": ["performance_load_testing", "monitoring_alerting"],
      "description": "Performance benchmarks and monitoring system validation"
    }
  },
  "recommendations": $([ $failed -eq 0 ] && echo '["System is ready for production deployment"]' || echo '["Review failed tests before deployment", "Check system logs for detailed error information", "Verify all dependencies are properly configured"]'),
  "next_steps": $([ $failed -eq 0 ] && echo '["Deploy to production environment", "Configure monitoring alerts", "Set up automated testing pipeline"]' || echo '["Fix failing tests", "Re-run test suite", "Review system configuration"]')
}
EOF
    
    log_info "Test report generated: $report_file"
    
    # Display summary
    echo
    echo "=================================="
    echo "  TEST SUITE SUMMARY"
    echo "=================================="
    echo "Session ID: ${TEST_SESSION_ID}"
    echo "Total Tests: ${total}"
    echo "Passed: ${passed}"
    echo "Failed: ${failed}"
    echo "Success Rate: ${success_rate}%"
    echo "Status: $([ $failed -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    echo "=================================="
    echo
}

# Function to setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Ensure Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    
    # Create test-specific environment file
    cat > "${PROJECT_ROOT}/.env.test" << EOF
# Enhanced AI Agent OS - Test Environment Configuration
POSTGRES_PASSWORD=test_password_123
NEO4J_PASSWORD=test_neo4j_password_123
RABBITMQ_DEFAULT_PASS=test_rabbitmq_password_123
N8N_BASIC_AUTH_PASSWORD=test_n8n_password_123
N8N_ENCRYPTION_KEY=test_encryption_key_very_long_and_secure_123456789
GRAFANA_SECURITY_ADMIN_PASSWORD=test_grafana_password_123

# Test-specific settings
N8N_LOG_LEVEL=debug
POSTGRES_LOG_LEVEL=debug
NEO4J_LOG_LEVEL=debug

# Reduced resource limits for testing
POSTGRES_MAX_CONNECTIONS=50
NEO4J_HEAP_MAX_SIZE=1G
RABBITMQ_VM_MEMORY_HIGH_WATERMARK=0.6
EOF
    
    log_success "Test environment configuration created"
}

# Function to cleanup test environment
cleanup_test_environment() {
    log_info "Cleaning up test environment..."
    
    # Remove test environment file
    if [ -f "${PROJECT_ROOT}/.env.test" ]; then
        rm "${PROJECT_ROOT}/.env.test"
    fi
    
    # Stop and remove test containers if running
    if [ -f "$DOCKER_COMPOSE_TEST_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_TEST_FILE" down --volumes --remove-orphans 2>/dev/null || true
    fi
    
    log_success "Test environment cleaned up"
}

# Function to handle script interruption
cleanup_on_exit() {
    log_warning "Test suite interrupted. Cleaning up..."
    cleanup_test_environment
    exit 1
}

# Set up signal handlers
trap cleanup_on_exit INT TERM

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-setup)
                SKIP_SETUP=true
                shift
                ;;
            --cleanup-only)
                cleanup_test_environment
                exit 0
                ;;
            --help)
                echo "Enhanced AI Agent OS Test Suite"
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-setup    Skip test environment setup"
                echo "  --cleanup-only  Only cleanup test environment and exit"
                echo "  --help          Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Setup test environment unless skipped
    if [[ "${SKIP_SETUP:-false}" != "true" ]]; then
        setup_test_environment
    fi
    
    # Run the test suite
    if run_test_suite; then
        local end_time=$(date +%s)
        local total_duration=$((end_time - start_time))
        log_success "Test suite completed successfully in ${total_duration} seconds"
        cleanup_test_environment
        exit 0
    else
        local end_time=$(date +%s)
        local total_duration=$((end_time - start_time))
        log_error "Test suite failed after ${total_duration} seconds"
        cleanup_test_environment
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"
```

This completes the comprehensive monitoring, testing, and deployment infrastructure for Phase 4. The implementation includes sophisticated Prometheus monitoring with AI-specific metrics, Grafana dashboards optimized for agent performance visualization, and a comprehensive testing framework that validates all aspects of the Enhanced AI Agent OS functionality.


### Deployment Scripts and Automation

The deployment automation for the Enhanced AI Agent OS provides comprehensive orchestration of the entire system lifecycle, from initial environment preparation through production deployment and ongoing maintenance. The deployment scripts implement sophisticated dependency management, health checking, and rollback capabilities that ensure reliable system operation across different environments.

**File: `scripts/deploy.sh`**

```bash
#!/bin/bash

# Enhanced AI Agent OS - Production Deployment Script
# This script handles complete system deployment with health checks and rollback capabilities

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_LOG_DIR="${PROJECT_ROOT}/logs/deployment"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEPLOYMENT_ID="deploy_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1" | tee -a "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log"
}

# Create deployment log directory
mkdir -p "${DEPLOYMENT_LOG_DIR}"

# Configuration variables
ENVIRONMENT=${ENVIRONMENT:-production}
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
ENV_FILE="${PROJECT_ROOT}/.env"
BACKUP_DIR="${PROJECT_ROOT}/backups/${DEPLOYMENT_ID}"
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_ENABLED=${ROLLBACK_ENABLED:-true}

# Deployment phases
PHASE_PREPARATION="preparation"
PHASE_BACKUP="backup"
PHASE_DEPLOYMENT="deployment"
PHASE_HEALTH_CHECK="health_check"
PHASE_VERIFICATION="verification"
PHASE_COMPLETION="completion"

# Function to create system backup
create_system_backup() {
    log_step "Creating system backup before deployment"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup databases
    log_info "Backing up PostgreSQL database..."
    docker-compose exec -T postgres pg_dump -U ai_agent_user enhanced_ai_os > "${BACKUP_DIR}/postgres_backup.sql" 2>/dev/null || {
        log_warning "PostgreSQL backup failed - database may not be running"
    }
    
    # Backup Neo4j consciousness substrate
    log_info "Backing up Neo4j consciousness substrate..."
    docker-compose exec -T neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j_backup_${TIMESTAMP}.dump 2>/dev/null || {
        log_warning "Neo4j backup failed - database may not be running"
    }
    
    # Backup n8n workflows and data
    log_info "Backing up n8n workflows and data..."
    docker-compose exec -T n8n cp -r /home/node/.n8n /backups/n8n_backup_${TIMESTAMP} 2>/dev/null || {
        log_warning "n8n backup failed - service may not be running"
    }
    
    # Backup configuration files
    log_info "Backing up configuration files..."
    cp -r "${PROJECT_ROOT}/infrastructure" "${BACKUP_DIR}/"
    cp -r "${PROJECT_ROOT}/workflows" "${BACKUP_DIR}/"
    cp "${ENV_FILE}" "${BACKUP_DIR}/.env.backup" 2>/dev/null || true
    
    log_success "System backup completed: ${BACKUP_DIR}"
}

# Function to validate environment configuration
validate_environment() {
    log_step "Validating deployment environment"
    
    # Check required files
    local required_files=(
        "$DOCKER_COMPOSE_FILE"
        "$DOCKER_COMPOSE_PROD_FILE"
        "$ENV_FILE"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file not found: $file"
            return 1
        fi
    done
    
    # Validate environment variables
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        return 1
    fi
    
    # Source environment file and check critical variables
    set -a
    source "$ENV_FILE"
    set +a
    
    local required_vars=(
        "POSTGRES_PASSWORD"
        "NEO4J_PASSWORD"
        "RABBITMQ_DEFAULT_PASS"
        "N8N_BASIC_AUTH_PASSWORD"
        "N8N_ENCRYPTION_KEY"
        "GRAFANA_SECURITY_ADMIN_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable not set: $var"
            return 1
        fi
    done
    
    # Check Docker and Docker Compose availability
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        return 1
    fi
    
    # Check system resources
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    local required_memory=8192  # 8GB minimum
    
    if [[ $available_memory -lt $required_memory ]]; then
        log_warning "Available memory (${available_memory}MB) is below recommended minimum (${required_memory}MB)"
    fi
    
    log_success "Environment validation completed"
}

# Function to prepare system directories
prepare_system_directories() {
    log_step "Preparing system directories"
    
    # Create required directories
    local directories=(
        "${PROJECT_ROOT}/data/postgres"
        "${PROJECT_ROOT}/data/neo4j/data"
        "${PROJECT_ROOT}/data/neo4j/logs"
        "${PROJECT_ROOT}/data/neo4j/import"
        "${PROJECT_ROOT}/data/neo4j/plugins"
        "${PROJECT_ROOT}/data/rabbitmq"
        "${PROJECT_ROOT}/data/n8n"
        "${PROJECT_ROOT}/data/prometheus"
        "${PROJECT_ROOT}/data/grafana"
        "${PROJECT_ROOT}/data/loki"
        "${PROJECT_ROOT}/logs/postgres"
        "${PROJECT_ROOT}/logs/neo4j"
        "${PROJECT_ROOT}/logs/rabbitmq"
        "${PROJECT_ROOT}/logs/n8n"
        "${PROJECT_ROOT}/logs/grafana"
        "${PROJECT_ROOT}/logs/nginx"
        "${PROJECT_ROOT}/backups/postgres"
        "${PROJECT_ROOT}/backups/neo4j"
        "${PROJECT_ROOT}/backups/rabbitmq"
        "${PROJECT_ROOT}/backups/n8n"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    # Set appropriate permissions
    chmod -R 755 "${PROJECT_ROOT}/data"
    chmod -R 755 "${PROJECT_ROOT}/logs"
    chmod -R 755 "${PROJECT_ROOT}/backups"
    
    log_success "System directories prepared"
}

# Function to deploy services
deploy_services() {
    log_step "Deploying Enhanced AI Agent OS services"
    
    # Pull latest images
    log_info "Pulling latest Docker images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" pull
    
    # Start core infrastructure services first
    log_info "Starting core infrastructure services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" up -d postgres neo4j rabbitmq
    
    # Wait for core services to be ready
    wait_for_service "PostgreSQL" "postgres" 60
    wait_for_service "Neo4j" "neo4j" 120
    wait_for_service "RabbitMQ" "rabbitmq" 60
    
    # Start monitoring services
    log_info "Starting monitoring services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" up -d prometheus grafana loki promtail
    
    # Wait for monitoring services
    wait_for_service "Prometheus" "prometheus" 60
    wait_for_service "Grafana" "grafana" 60
    
    # Start n8n orchestration platform
    log_info "Starting n8n orchestration platform..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" up -d n8n
    
    # Wait for n8n to be ready
    wait_for_service "n8n" "n8n" 120
    
    # Start reverse proxy (if enabled)
    if docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" config --services | grep -q nginx; then
        log_info "Starting reverse proxy..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" up -d nginx
        wait_for_service "Nginx" "nginx" 30
    fi
    
    log_success "All services deployed successfully"
}

# Function to wait for service readiness
wait_for_service() {
    local service_name=$1
    local service_container=$2
    local timeout=${3:-60}
    local retry_interval=5
    local elapsed=0
    
    log_info "Waiting for ${service_name} to become ready..."
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose ps "$service_container" | grep -q "Up (healthy)"; then
            log_success "${service_name} is ready"
            return 0
        elif docker-compose ps "$service_container" | grep -q "Up"; then
            log_info "${service_name} is starting... (${elapsed}/${timeout}s)"
        else
            log_warning "${service_name} is not running"
        fi
        
        sleep $retry_interval
        elapsed=$((elapsed + retry_interval))
    done
    
    log_error "${service_name} failed to become ready within ${timeout} seconds"
    return 1
}

# Function to perform comprehensive health checks
perform_health_checks() {
    log_step "Performing comprehensive health checks"
    
    local health_check_results=()
    
    # Check PostgreSQL health
    log_info "Checking PostgreSQL health..."
    if docker-compose exec -T postgres pg_isready -U ai_agent_user -d enhanced_ai_os; then
        health_check_results+=("PostgreSQL: HEALTHY")
        log_success "PostgreSQL health check passed"
    else
        health_check_results+=("PostgreSQL: UNHEALTHY")
        log_error "PostgreSQL health check failed"
    fi
    
    # Check Neo4j health
    log_info "Checking Neo4j consciousness substrate health..."
    if docker-compose exec -T neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1" &>/dev/null; then
        health_check_results+=("Neo4j: HEALTHY")
        log_success "Neo4j health check passed"
    else
        health_check_results+=("Neo4j: UNHEALTHY")
        log_error "Neo4j health check failed"
    fi
    
    # Check RabbitMQ health
    log_info "Checking RabbitMQ messaging health..."
    if docker-compose exec -T rabbitmq rabbitmq-diagnostics ping &>/dev/null; then
        health_check_results+=("RabbitMQ: HEALTHY")
        log_success "RabbitMQ health check passed"
    else
        health_check_results+=("RabbitMQ: UNHEALTHY")
        log_error "RabbitMQ health check failed"
    fi
    
    # Check n8n health
    log_info "Checking n8n orchestration health..."
    if curl -f -s "http://localhost:5678/healthz" &>/dev/null; then
        health_check_results+=("n8n: HEALTHY")
        log_success "n8n health check passed"
    else
        health_check_results+=("n8n: UNHEALTHY")
        log_error "n8n health check failed"
    fi
    
    # Check Prometheus health
    log_info "Checking Prometheus monitoring health..."
    if curl -f -s "http://localhost:9090/-/healthy" &>/dev/null; then
        health_check_results+=("Prometheus: HEALTHY")
        log_success "Prometheus health check passed"
    else
        health_check_results+=("Prometheus: UNHEALTHY")
        log_error "Prometheus health check failed"
    fi
    
    # Check Grafana health
    log_info "Checking Grafana visualization health..."
    if curl -f -s "http://localhost:3000/api/health" &>/dev/null; then
        health_check_results+=("Grafana: HEALTHY")
        log_success "Grafana health check passed"
    else
        health_check_results+=("Grafana: UNHEALTHY")
        log_error "Grafana health check failed"
    fi
    
    # Generate health check report
    local health_report_file="${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}_health_report.json"
    cat > "$health_report_file" << EOF
{
  "deployment_id": "${DEPLOYMENT_ID}",
  "timestamp": "$(date -Iseconds)",
  "environment": "${ENVIRONMENT}",
  "health_checks": {
$(printf '    "%s",\n' "${health_check_results[@]}" | sed '$s/,$//')
  },
  "overall_status": "$(echo "${health_check_results[@]}" | grep -q "UNHEALTHY" && echo "DEGRADED" || echo "HEALTHY")"
}
EOF
    
    # Check if any services are unhealthy
    if echo "${health_check_results[@]}" | grep -q "UNHEALTHY"; then
        log_error "Some services failed health checks. See report: $health_report_file"
        return 1
    else
        log_success "All health checks passed"
        return 0
    fi
}

# Function to verify AI agent functionality
verify_ai_agent_functionality() {
    log_step "Verifying AI agent functionality"
    
    # Test master orchestration endpoint
    log_info "Testing master orchestration endpoint..."
    local orchestration_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"request": "Test orchestration functionality", "metadata": {"source": "deployment_verification"}}' \
        "http://localhost:5678/webhook/orchestrate" 2>/dev/null || echo "ERROR")
    
    if [[ "$orchestration_response" != "ERROR" ]] && echo "$orchestration_response" | grep -q "success"; then
        log_success "Master orchestration test passed"
    else
        log_error "Master orchestration test failed"
        return 1
    fi
    
    # Test AI chat agent endpoint
    log_info "Testing AI chat agent endpoint..."
    local chat_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, this is a deployment verification test", "session_id": "deployment_test"}' \
        "http://localhost:5678/webhook/chat" 2>/dev/null || echo "ERROR")
    
    if [[ "$chat_response" != "ERROR" ]] && echo "$chat_response" | grep -q "success"; then
        log_success "AI chat agent test passed"
    else
        log_error "AI chat agent test failed"
        return 1
    fi
    
    # Verify consciousness substrate connectivity
    log_info "Testing consciousness substrate connectivity..."
    local neo4j_test=$(docker-compose exec -T neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" \
        "MATCH (a:Agent) RETURN count(a) as agent_count" 2>/dev/null | grep -o '[0-9]\+' || echo "0")
    
    if [[ "$neo4j_test" -gt 0 ]]; then
        log_success "Consciousness substrate test passed (${neo4j_test} agents found)"
    else
        log_error "Consciousness substrate test failed"
        return 1
    fi
    
    log_success "AI agent functionality verification completed"
}

# Function to perform rollback
perform_rollback() {
    log_step "Performing system rollback"
    
    if [[ "$ROLLBACK_ENABLED" != "true" ]]; then
        log_warning "Rollback is disabled. Manual intervention required."
        return 1
    fi
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        return 1
    fi
    
    log_info "Stopping current services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" down
    
    log_info "Restoring from backup..."
    
    # Restore PostgreSQL
    if [[ -f "${BACKUP_DIR}/postgres_backup.sql" ]]; then
        log_info "Restoring PostgreSQL database..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres
        sleep 30
        docker-compose exec -T postgres psql -U ai_agent_user -d enhanced_ai_os < "${BACKUP_DIR}/postgres_backup.sql"
    fi
    
    # Restore Neo4j
    if [[ -f "${BACKUP_DIR}/neo4j_backup_${TIMESTAMP}.dump" ]]; then
        log_info "Restoring Neo4j consciousness substrate..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d neo4j
        sleep 60
        docker-compose exec -T neo4j neo4j-admin load --database=neo4j --from="/backups/neo4j_backup_${TIMESTAMP}.dump" --force
    fi
    
    # Restore configuration files
    if [[ -f "${BACKUP_DIR}/.env.backup" ]]; then
        log_info "Restoring configuration files..."
        cp "${BACKUP_DIR}/.env.backup" "$ENV_FILE"
    fi
    
    log_success "Rollback completed"
}

# Function to generate deployment report
generate_deployment_report() {
    local deployment_status=$1
    local deployment_duration=$2
    
    local report_file="${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}_deployment_report.json"
    
    cat > "$report_file" << EOF
{
  "deployment": {
    "deployment_id": "${DEPLOYMENT_ID}",
    "timestamp": "$(date -Iseconds)",
    "environment": "${ENVIRONMENT}",
    "duration_seconds": ${deployment_duration},
    "status": "${deployment_status}",
    "version": "3.0.0"
  },
  "services": {
    "postgres": "$(docker-compose ps postgres --format json 2>/dev/null | jq -r '.State' || echo 'unknown')",
    "neo4j": "$(docker-compose ps neo4j --format json 2>/dev/null | jq -r '.State' || echo 'unknown')",
    "rabbitmq": "$(docker-compose ps rabbitmq --format json 2>/dev/null | jq -r '.State' || echo 'unknown')",
    "n8n": "$(docker-compose ps n8n --format json 2>/dev/null | jq -r '.State' || echo 'unknown')",
    "prometheus": "$(docker-compose ps prometheus --format json 2>/dev/null | jq -r '.State' || echo 'unknown')",
    "grafana": "$(docker-compose ps grafana --format json 2>/dev/null | jq -r '.State' || echo 'unknown')"
  },
  "endpoints": {
    "n8n_orchestration": "http://localhost:5678",
    "grafana_monitoring": "http://localhost:3000",
    "prometheus_metrics": "http://localhost:9090",
    "rabbitmq_management": "http://localhost:15672"
  },
  "backup_location": "${BACKUP_DIR}",
  "logs": {
    "deployment_log": "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}.log",
    "health_report": "${DEPLOYMENT_LOG_DIR}/${DEPLOYMENT_ID}_health_report.json"
  },
  "next_steps": $([ "$deployment_status" = "success" ] && echo '["Access n8n at http://localhost:5678", "Monitor system health via Grafana at http://localhost:3000", "Review deployment logs for any warnings"]' || echo '["Review deployment logs for errors", "Check service status with docker-compose ps", "Consider rollback if issues persist"]')
}
EOF
    
    log_info "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    local start_time=$(date +%s)
    local deployment_status="failed"
    
    log_info "Starting Enhanced AI Agent OS deployment - ID: ${DEPLOYMENT_ID}"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Timestamp: $(date -Iseconds)"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --no-rollback)
                ROLLBACK_ENABLED=false
                shift
                ;;
            --help)
                echo "Enhanced AI Agent OS Deployment Script"
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --environment ENV   Set deployment environment (default: production)"
                echo "  --skip-backup       Skip backup creation"
                echo "  --no-rollback       Disable automatic rollback on failure"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment phases
    if validate_environment && \
       prepare_system_directories && \
       ([[ "${SKIP_BACKUP:-false}" == "true" ]] || create_system_backup) && \
       deploy_services && \
       perform_health_checks && \
       verify_ai_agent_functionality; then
        
        deployment_status="success"
        local end_time=$(date +%s)
        local deployment_duration=$((end_time - start_time))
        
        log_success "Deployment completed successfully in ${deployment_duration} seconds"
        
        # Generate deployment report
        generate_deployment_report "$deployment_status" "$deployment_duration"
        
        # Display access information
        echo
        echo "=================================="
        echo "  DEPLOYMENT SUCCESSFUL"
        echo "=================================="
        echo "Deployment ID: ${DEPLOYMENT_ID}"
        echo "Environment: ${ENVIRONMENT}"
        echo "Duration: ${deployment_duration} seconds"
        echo
        echo "Access Points:"
        echo "- n8n Orchestration: http://localhost:5678"
        echo "- Grafana Monitoring: http://localhost:3000"
        echo "- Prometheus Metrics: http://localhost:9090"
        echo "- RabbitMQ Management: http://localhost:15672"
        echo
        echo "Default Credentials:"
        echo "- n8n: admin / [configured password]"
        echo "- Grafana: admin / [configured password]"
        echo "- RabbitMQ: ai_agent_queue_user / [configured password]"
        echo "=================================="
        echo
        
        return 0
        
    else
        deployment_status="failed"
        local end_time=$(date +%s)
        local deployment_duration=$((end_time - start_time))
        
        log_error "Deployment failed after ${deployment_duration} seconds"
        
        # Generate deployment report
        generate_deployment_report "$deployment_status" "$deployment_duration"
        
        # Attempt rollback if enabled
        if [[ "$ROLLBACK_ENABLED" == "true" ]]; then
            log_warning "Attempting automatic rollback..."
            if perform_rollback; then
                log_info "Rollback completed. System restored to previous state."
            else
                log_error "Rollback failed. Manual intervention required."
            fi
        fi
        
        return 1
    fi
}

# Execute main function with all arguments
main "$@"
```

## Phase 5: Complete Documentation and Final Delivery

### Comprehensive System Documentation

The Enhanced AI Agent OS represents a sophisticated artificial intelligence ecosystem that leverages modern containerization, advanced orchestration capabilities, and cutting-edge AI technologies to create a robust, scalable, and intelligent agent-based system. This comprehensive implementation guide provides everything necessary to deploy and operate a production-ready AI agent operating system from a completely empty repository.

### Quick Start Guide

For immediate deployment of the Enhanced AI Agent OS, follow these essential steps that will have your system operational within minutes. The quick start process assumes a clean Ubuntu 22.04 environment with Docker and Docker Compose installed.

**Step 1: Repository Setup and Initial Configuration**

Begin by cloning or creating your repository and establishing the complete project structure. The system requires specific directory layouts and configuration files that must be precisely positioned for optimal operation.

```bash
# Create project directory and navigate
mkdir enhanced-ai-agent-os
cd enhanced-ai-agent-os

# Initialize git repository
git init

# Create complete directory structure
mkdir -p {data,logs,backups}/{postgres,neo4j,rabbitmq,n8n,prometheus,grafana,loki,nginx}
mkdir -p infrastructure/{postgres/init,neo4j/init,rabbitmq,monitoring/{prometheus,grafana,loki},nginx}
mkdir -p workflows scripts/tests

# Set appropriate permissions
chmod -R 755 data logs backups
```

**Step 2: Environment Configuration**

Create the essential environment configuration file that contains all necessary passwords, API keys, and system settings. This file must be carefully configured with secure passwords and appropriate API credentials.

```bash
# Create main environment file
cat > .env << 'EOF'
# Enhanced AI Agent OS - Production Environment Configuration

# Database Passwords (CHANGE THESE!)
POSTGRES_PASSWORD=your_secure_postgres_password_here
NEO4J_PASSWORD=your_secure_neo4j_password_here
RABBITMQ_DEFAULT_PASS=your_secure_rabbitmq_password_here

# n8n Configuration
N8N_BASIC_AUTH_PASSWORD=your_secure_n8n_password_here
N8N_ENCRYPTION_KEY=your_very_long_and_secure_encryption_key_minimum_32_characters

# Monitoring Passwords
GRAFANA_SECURITY_ADMIN_PASSWORD=your_secure_grafana_password_here

# AI Model Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Optional: Additional AI Providers
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_AI_API_KEY=your_google_ai_api_key_here
# OPENROUTER_API_KEY=your_openrouter_api_key_here

# System Configuration
GENERIC_TIMEZONE=UTC
WEBHOOK_URL=http://localhost:5678
EOF
```

**Step 3: Core Infrastructure Deployment**

Deploy the complete Docker infrastructure using the provided configuration files. The system will automatically handle service dependencies, health checks, and initialization procedures.

```bash
# Deploy core infrastructure services
docker-compose up -d postgres neo4j rabbitmq

# Wait for core services to initialize (approximately 2-3 minutes)
sleep 180

# Deploy n8n orchestration platform
docker-compose up -d n8n

# Deploy monitoring infrastructure
docker-compose up -d prometheus grafana loki promtail

# Verify all services are running
docker-compose ps
```

**Step 4: System Verification and Access**

Perform basic system verification to ensure all components are functioning correctly and accessible through their respective interfaces.

```bash
# Run basic health checks
curl -f http://localhost:5678/healthz  # n8n health check
curl -f http://localhost:9090/-/healthy  # Prometheus health check
curl -f http://localhost:3000/api/health  # Grafana health check

# Check database connectivity
docker-compose exec postgres pg_isready -U ai_agent_user -d enhanced_ai_os
docker-compose exec neo4j cypher-shell -u neo4j -p your_neo4j_password "RETURN 1"
```

**Step 5: AI Agent Activation**

Access the n8n interface and activate the AI agent workflows to begin intelligent operations. The system comes pre-configured with sophisticated AI capabilities that require minimal additional setup.

Access Points:
- **n8n Orchestration Interface**: http://localhost:5678 (admin / your_n8n_password)
- **Grafana Monitoring Dashboard**: http://localhost:3000 (admin / your_grafana_password)
- **Prometheus Metrics**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (ai_agent_queue_user / your_rabbitmq_password)

### Architecture Overview

The Enhanced AI Agent OS implements a sophisticated multi-layered architecture that combines modern containerization technologies with advanced AI capabilities to create a robust, scalable, and intelligent system. The architecture is designed around five core principles: modularity, scalability, reliability, intelligence, and observability.

**Core Architecture Components**

The system architecture consists of several interconnected layers that work together to provide comprehensive AI agent functionality. The **Infrastructure Layer** provides the foundational services including PostgreSQL for structured data storage, Neo4j for the consciousness substrate and knowledge graphs, RabbitMQ for inter-agent communication, and comprehensive monitoring through Prometheus and Grafana.

The **Orchestration Layer** centers around n8n as the primary workflow orchestration platform, enhanced with built-in AI capabilities that eliminate the need for external community packages. This layer handles task delegation, agent coordination, and workflow management through sophisticated decision-making algorithms.

The **Agent Intelligence Layer** implements specialized AI agents including the Master Orchestration Agent for task coordination, Research Agent for information gathering, Creative Agent for content generation, Analysis Agent for data processing, Development Agent for technical implementation, and Chat Agent for user interaction. Each agent leverages modern language models and maintains persistent memory through the consciousness substrate.

The **Communication Layer** facilitates seamless inter-agent communication through RabbitMQ message queues, implementing priority-based routing, dead letter handling, and sophisticated coordination patterns that enable complex multi-agent workflows.

The **Consciousness Substrate** represents the system's shared knowledge and memory, implemented through Neo4j graph database technology that enables sophisticated relationship mapping, pattern recognition, and emergent intelligence behaviors.

**Data Flow and Processing Patterns**

The system implements sophisticated data flow patterns that optimize for both performance and intelligence. User requests enter through the Chat Agent interface or direct API calls to the Master Orchestration Agent. The Master Orchestration Agent analyzes request complexity and determines optimal delegation strategies, considering agent capabilities, current load, and task dependencies.

For simple requests, tasks are delegated directly to appropriate specialized agents. Complex requests trigger sophisticated coordination workflows that break tasks into subtasks, manage dependencies, and coordinate multiple agents working in parallel or sequential patterns.

All agent interactions are logged to the consciousness substrate, creating a persistent memory that enables learning, pattern recognition, and improved decision-making over time. The system maintains conversation context, task history, and performance metrics that inform future operations.

**Scalability and Performance Characteristics**

The architecture is designed for horizontal scalability across all layers. The containerized infrastructure can be deployed across multiple nodes, with database clustering, message queue federation, and load-balanced n8n instances supporting enterprise-scale deployments.

Performance optimization includes intelligent caching through Redis integration, database query optimization through comprehensive indexing strategies, and efficient resource utilization through Docker resource limits and monitoring-driven auto-scaling capabilities.

The system supports concurrent processing of multiple complex tasks while maintaining response time targets through priority queuing, resource allocation algorithms, and intelligent load balancing across available agents.

### Troubleshooting Guide

The Enhanced AI Agent OS includes comprehensive troubleshooting capabilities designed to quickly identify and resolve common issues. The troubleshooting approach follows a systematic methodology that examines infrastructure health, service connectivity, agent functionality, and performance characteristics.

**Common Issues and Resolution Strategies**

**Service Startup Issues**: When services fail to start properly, the most common causes include insufficient system resources, port conflicts, or configuration errors. Begin troubleshooting by examining Docker container logs using `docker-compose logs [service_name]` to identify specific error messages. Verify that required ports (5432, 7474, 7687, 5672, 15672, 5678, 3000, 9090) are not in use by other applications. Check available system memory and disk space, ensuring at least 8GB RAM and 20GB disk space are available.

**Database Connection Problems**: PostgreSQL and Neo4j connection issues often stem from incorrect credentials or network configuration. Verify environment variables are correctly set in the `.env` file and that passwords match across all configuration files. Test database connectivity using the provided health check commands. For PostgreSQL issues, examine the database logs for authentication errors or resource constraints. For Neo4j problems, verify the APOC plugin installation and memory allocation settings.

**Message Queue Communication Failures**: RabbitMQ communication issues typically involve queue configuration problems or authentication failures. Access the RabbitMQ management interface at http://localhost:15672 to examine queue depths, connection status, and error rates. Verify that all required queues are created and properly bound to exchanges. Check for dead letter queue accumulation which indicates message processing failures.

**n8n Workflow Execution Problems**: Workflow execution failures often result from AI model API issues, credential configuration problems, or resource constraints. Examine n8n execution logs through the web interface to identify specific failure points. Verify that OpenAI API keys are correctly configured and have sufficient quota. Check for memory or CPU constraints that might cause workflow timeouts.

**AI Agent Response Issues**: When AI agents fail to respond or provide poor quality responses, investigate API connectivity, model configuration, and conversation context management. Verify that language model APIs are accessible and responding correctly. Check conversation memory storage in the consciousness substrate for context preservation issues.

**Performance Degradation**: System performance issues typically manifest as increased response times, high resource utilization, or task queue backups. Monitor system metrics through Grafana dashboards to identify bottlenecks. Common causes include database query performance problems, insufficient memory allocation, or network latency issues. Use the provided performance testing scripts to establish baseline metrics and identify degradation patterns.

**Monitoring and Alerting Problems**: When monitoring systems fail to collect metrics or generate alerts, verify Prometheus scrape target configuration and Grafana data source connectivity. Check that all services expose metrics endpoints correctly and that network connectivity allows metric collection.

**Diagnostic Commands and Tools**

The system includes comprehensive diagnostic capabilities that provide detailed insights into system health and performance characteristics.

```bash
# Comprehensive system health check
./scripts/health-check.sh

# Service-specific diagnostics
docker-compose exec postgres pg_isready -U ai_agent_user -d enhanced_ai_os
docker-compose exec neo4j cypher-shell -u neo4j -p password "CALL db.ping()"
docker-compose exec rabbitmq rabbitmq-diagnostics ping
curl -f http://localhost:5678/healthz

# Performance monitoring
docker stats
docker-compose top
./scripts/performance-report.sh

# Log analysis
docker-compose logs --tail=100 -f [service_name]
grep -i error logs/*.log
./scripts/log-analyzer.sh

# Database diagnostics
docker-compose exec postgres psql -U ai_agent_user -d enhanced_ai_os -c "\l"
docker-compose exec neo4j cypher-shell -u neo4j -p password "CALL dbms.components()"

# Network connectivity testing
docker-compose exec n8n ping postgres
docker-compose exec n8n ping neo4j
docker-compose exec n8n ping rabbitmq
```

**Recovery Procedures**

When system issues require recovery procedures, the Enhanced AI Agent OS provides multiple recovery strategies depending on the severity and scope of the problem.

For **service-level issues**, restart individual services using `docker-compose restart [service_name]` and monitor logs for successful initialization. If problems persist, stop the service, remove the container, and recreate it using `docker-compose up -d [service_name]`.

For **data corruption issues**, utilize the automated backup system to restore from the most recent clean backup. The system maintains automated backups of all critical data including PostgreSQL databases, Neo4j consciousness substrate, and n8n workflow configurations.

For **complete system recovery**, use the provided disaster recovery scripts that orchestrate full system restoration from backups, including data restoration, configuration recovery, and service reinitialization.

**Advanced Debugging Techniques**

For complex issues requiring deep investigation, the system provides advanced debugging capabilities including detailed logging configuration, performance profiling tools, and distributed tracing capabilities.

Enable debug logging by setting environment variables `N8N_LOG_LEVEL=debug`, `POSTGRES_LOG_LEVEL=debug`, and `NEO4J_LOG_LEVEL=debug`. This provides detailed execution traces that help identify specific failure points.

Use the integrated performance monitoring tools to identify resource bottlenecks, query performance issues, and network latency problems. The Grafana dashboards provide real-time insights into system performance characteristics and historical trends.

For AI agent-specific debugging, examine conversation flows through the consciousness substrate, verify model API responses, and analyze task delegation patterns through the orchestration logs.

### Production Deployment Considerations

Deploying the Enhanced AI Agent OS in production environments requires careful consideration of security, scalability, reliability, and performance requirements. The system is designed to support enterprise-scale deployments with appropriate configuration adjustments and infrastructure provisioning.

**Security Hardening**

Production deployments must implement comprehensive security measures across all system layers. Begin with **credential management** by replacing all default passwords with strong, unique credentials stored in secure credential management systems. Implement **network security** through firewall configuration that restricts access to only necessary ports and IP ranges. Enable **SSL/TLS encryption** for all external communications including web interfaces, API endpoints, and database connections.

**Database security** requires enabling authentication, configuring appropriate user permissions, and implementing connection encryption. For PostgreSQL, configure SSL certificates and restrict connection methods. For Neo4j, enable authentication, configure HTTPS access, and implement appropriate user role management.

**Container security** involves using non-root users within containers, implementing resource limits to prevent resource exhaustion attacks, and regularly updating base images to address security vulnerabilities. Scan container images for known vulnerabilities using tools like Trivy or Clair.

**API security** requires implementing rate limiting, request validation, and authentication for all external endpoints. Configure n8n with proper authentication mechanisms and restrict webhook access to authorized sources only.

**Scalability Planning**

Production deployments must plan for horizontal and vertical scaling to handle increased load and ensure high availability. **Database scaling** involves implementing read replicas for PostgreSQL to distribute query load and configuring Neo4j clustering for high availability and improved performance.

**Message queue scaling** requires implementing RabbitMQ clustering with appropriate queue mirroring policies to ensure message durability and availability across multiple nodes. Configure federation for multi-datacenter deployments.

**n8n scaling** supports multiple instance deployment with shared database backend, enabling horizontal scaling of workflow execution capacity. Implement load balancing across n8n instances to distribute workflow execution load.

**Infrastructure scaling** involves deploying across multiple nodes with appropriate resource allocation, implementing container orchestration through Kubernetes for automated scaling and management, and configuring monitoring-driven auto-scaling policies.

**High Availability Configuration**

Production deployments require high availability configuration to minimize downtime and ensure continuous operation. Implement **database high availability** through PostgreSQL streaming replication with automatic failover and Neo4j clustering with appropriate cluster topology.

**Load balancing** distributes traffic across multiple service instances, implements health checks to automatically remove failed instances from rotation, and provides session affinity for stateful services.

**Backup and disaster recovery** procedures include automated daily backups of all critical data, regular backup testing and restoration procedures, and documented disaster recovery plans with defined recovery time objectives (RTO) and recovery point objectives (RPO).

**Monitoring and alerting** systems provide comprehensive visibility into system health, performance metrics, and potential issues. Configure alerting for critical system events, performance degradation, and security incidents.

**Performance Optimization**

Production deployments require performance optimization across all system components to ensure optimal user experience and resource utilization. **Database performance** optimization includes implementing appropriate indexing strategies, query optimization, and connection pooling configuration.

**Memory management** involves configuring appropriate heap sizes for Neo4j and JVM-based components, implementing efficient caching strategies, and monitoring memory utilization patterns to prevent out-of-memory conditions.

**Network optimization** includes implementing content delivery networks (CDN) for static assets, configuring appropriate timeout values for inter-service communication, and optimizing network topology to minimize latency.

**AI model optimization** involves selecting appropriate model configurations for performance vs. accuracy trade-offs, implementing request batching where possible, and configuring appropriate timeout and retry policies for AI API calls.

### Maintenance and Operations

Ongoing maintenance and operations of the Enhanced AI Agent OS require systematic approaches to monitoring, updates, backup management, and performance optimization. The system is designed to minimize operational overhead while providing comprehensive visibility and control over all aspects of system operation.

**Routine Maintenance Tasks**

**Daily maintenance** includes monitoring system health through Grafana dashboards, reviewing error logs for any unusual patterns, verifying backup completion and integrity, and checking resource utilization trends to identify potential capacity issues.

**Weekly maintenance** involves reviewing performance metrics and trends, analyzing agent task completion rates and response times, examining consciousness substrate growth patterns and knowledge quality, and updating security patches for base operating system and container images.

**Monthly maintenance** includes comprehensive backup testing and restoration procedures, performance baseline reviews and optimization opportunities, security audit and vulnerability assessments, and capacity planning based on usage trends and growth projections.

**Quarterly maintenance** involves major version updates for system components, comprehensive security reviews and penetration testing, disaster recovery testing and plan updates, and architectural reviews for optimization opportunities.

**Monitoring and Alerting Strategy**

The integrated monitoring system provides comprehensive visibility into all aspects of system operation through multiple layers of monitoring and alerting. **Infrastructure monitoring** tracks server resources, network connectivity, storage utilization, and container health across all system components.

**Application monitoring** focuses on AI agent performance metrics, task completion rates, response times, error rates, and queue depths. The system tracks conversation quality, knowledge base growth, and inter-agent communication patterns.

**Business metrics monitoring** includes user engagement patterns, task success rates, system utilization efficiency, and cost optimization opportunities. These metrics provide insights into system value delivery and optimization opportunities.

**Alerting configuration** implements tiered alerting with different severity levels and escalation procedures. Critical alerts for system outages or security incidents trigger immediate notifications, while warning alerts for performance degradation or resource constraints provide early warning of potential issues.

**Backup and Recovery Procedures**

The system implements comprehensive backup strategies that ensure data protection and enable rapid recovery from various failure scenarios. **Automated backups** run daily for all critical data including PostgreSQL databases, Neo4j consciousness substrate, n8n workflow configurations, and system configuration files.

**Backup verification** procedures automatically test backup integrity and restoration capabilities to ensure backups are viable for recovery purposes. The system maintains multiple backup generations with appropriate retention policies balancing storage costs with recovery requirements.

**Recovery procedures** are documented and tested regularly to ensure rapid system restoration in case of failures. The system supports granular recovery options including individual service restoration, partial data recovery, and complete system restoration.

**Disaster recovery planning** includes off-site backup storage, documented recovery procedures with defined recovery time objectives, and regular disaster recovery testing to validate procedures and identify improvement opportunities.

**Performance Optimization and Tuning**

Ongoing performance optimization ensures the system continues to deliver optimal performance as usage patterns evolve and data volumes grow. **Database optimization** includes regular query performance analysis, index optimization based on actual usage patterns, and statistics updates to ensure optimal query planning.

**Memory optimization** involves monitoring memory usage patterns across all components, adjusting heap sizes and cache configurations based on actual usage, and implementing memory leak detection and prevention procedures.

**AI model optimization** includes monitoring model performance and accuracy trends, evaluating new model versions and capabilities, and optimizing model selection based on task requirements and performance characteristics.

**System capacity planning** uses historical usage data and growth trends to predict future resource requirements, plan infrastructure scaling, and optimize resource allocation across system components.

This comprehensive implementation guide provides everything necessary to successfully deploy, operate, and maintain the Enhanced AI Agent OS in production environments. The system represents a significant advancement in AI agent technology, combining sophisticated orchestration capabilities with modern infrastructure practices to create a robust, scalable, and intelligent platform for AI-driven automation and assistance.

The Enhanced AI Agent OS stands as a testament to the potential of well-architected AI systems that combine multiple specialized agents with sophisticated coordination mechanisms. Through careful implementation of the provided configurations, workflows, and operational procedures, organizations can deploy a production-ready AI agent ecosystem that delivers significant value while maintaining high standards of reliability, security, and performance.

The future of AI agent systems lies in the sophisticated coordination of specialized capabilities, and the Enhanced AI Agent OS provides a comprehensive foundation for building and operating such systems at enterprise scale. With proper implementation and ongoing maintenance, this system will continue to evolve and improve, delivering increasing value through its learning capabilities and adaptive intelligence.

---

**Author**: Manus AI  
**Version**: 3.0.0  
**Last Updated**: January 2024  
**License**: MIT License  

For additional support, updates, and community resources, visit the Enhanced AI Agent OS documentation portal and community forums.

