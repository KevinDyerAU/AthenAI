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

### Production Reverse Proxy (Nginx + TLS)

Nginx config is provided in `infrastructure/nginx/`. To enable HTTPS with HSTS:

1. Place your certs in `infrastructure/nginx/ssl/` as `server.crt` and `server.key`.
2. Start Nginx with the production profile:
   ```bash
   docker compose --profile production up -d nginx
   ```
3. The site config `infrastructure/nginx/sites-available/enhanced-ai-agent-os.conf` serves:
   - `/` → `n8n:5678` (WebSocket upgrades supported)
   - `/grafana/` → `grafana:3000`
   - `/neo4j/` → `neo4j:7474`
   - `/rabbitmq/` → `rabbitmq:15672`
   - `/prometheus/` → `prometheus:9090`
   - `/loki/` → `loki:3100`

Note: A redirect from HTTP→HTTPS is included; confirm certificates before enforcing.

> TODO: TLS hardening (OCSP stapling, modern cipher suites, strict HSTS rollout) — see issue `todo-tls-hardening`.

### Enable Node Exporter

To enable Node Exporter for Prometheus monitoring, add the following service to your `docker-compose.yml` file:

```yml
  node-exporter:
    image: prometheus/node-exporter:latest
    ports:
      - "9100:9100"
    restart: always
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc|rootfs/var/lib/docker/containers|rootfs/var/lib/docker/overlay2|rootfs/run/docker/netns|rootfs/var/lib/docker/aufs)($|/)'

```

Then, update your Prometheus configuration to scrape the Node Exporter:

```yml
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
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

### Alerting (Alertmanager)

Alertmanager routes Prometheus alerts to Slack and/or Email.

- Config: `infrastructure/monitoring/alertmanager/alertmanager.yml`
- Templates: `infrastructure/monitoring/alertmanager/templates/` (e.g. `slack.tmpl`)
- Service: `alertmanager` (exposed on `${ALERTMANAGER_PORT:-9093}`)

Routing:
- Critical alerts → `${SLACK_CHANNEL_CRITICAL}`
- Ops services (`rabbitmq`, `n8n`) → `${SLACK_CHANNEL_OPS}`
- Platform services (`neo4j`, `prometheus`, `loki`, `promtail`, `node-exporter`) → `${SLACK_CHANNEL_PLATFORM}`
- Warning/Critical also sent to email as backup

Setup steps:
1. Set environment variables in `.env`:
   - `SLACK_WEBHOOK_URL`, `SLACK_CHANNEL` (e.g. `#alerts`)
   - `ALERT_EMAIL_TO`, `ALERT_EMAIL_FROM`, `SMTP_SMARTHOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`
2. Start Alertmanager:
   ```bash
   docker compose up -d alertmanager
   ```
3. Prometheus is already configured to send alerts to `alertmanager:9093` in `prometheus.yml`.
4. Verify at `http://localhost:${ALERTMANAGER_PORT:-9093}`.

Create a silence (PowerShell):
```powershell
./scripts/monitoring/create-silence.ps1 -AlertName RabbitMQQueueDepthHigh -Severity warning -Duration 2h -Comment "Maintenance window"
```

### Workflow Orchestration

Starter workflows are provided in `workflows/` and can be imported into n8n:

- `workflows/ai-task-orchestrator.json`
  - Webhook: `POST /webhook/orchestrate` with body `{ "task": { "type": "research|creative|generic", ... } }`
  - Routes to downstream agent handlers via internal webhooks.
- `workflows/agent-handlers.json`
  - Webhooks: `/webhook/agent/research`, `/webhook/agent/creative`, `/webhook/agent/generic`
  - Placeholder handlers return an acknowledgment; extend with real agent logic.
 - `workflows/hello-world.json`
   - Webhook: `GET /webhook/hello` → returns a JSON greeting payload

Import steps:
1. Open n8n → Workflows → Import from file → select the JSON files above.
2. Activate the workflows (ensure Webhook URLs match your base URL/reverse proxy if using Nginx).
3. Test:
   ```bash
   curl -sS -X POST http://localhost:5678/webhook/orchestrate \
     -H 'Content-Type: application/json' \
     -d '{"task": {"type": "research", "prompt": "Find latest Neo4j release notes"}}'
   ```
   ```bash
   curl -sS http://localhost:5678/webhook/hello | jq
   ```

### Dashboards

Grafana dashboards are auto-provisioned from `infrastructure/monitoring/grafana/dashboards/`:

- AI Agent Performance: `ai-agent-performance.json`
  - End-to-end agent latencies (p95), HTTP 5xx rate, RabbitMQ queue depth
- System Health: `system-health.json`
  - Targets up, job availability, Prometheus scrape durations, Loki ingest rate
- Consciousness Substrate (Neo4j): `consciousness-substrate.json`
  - Bolt connections, query latency (p95), page cache hit ratio
- n8n Overview: `n8n-overview.json`
  - Target up, workflow execution duration percentiles

Access Grafana at `http://localhost:${GRAFANA_PORT:-3000}` and open the dashboards by title. No manual import is needed.

## Security

### Authentication
- JWT-based authentication for API access
- Basic authentication for n8n interface
- Role-based access control for different user types

### Data Protection
- Encryption at rest for sensitive data
- TLS encryption for all network communication
> TODO: Security hardening (Docker secrets for sensitive env, Nginx rate limiting, firewall/ports review) — see issue `todo-security-hardening`.
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
