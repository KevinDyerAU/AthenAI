# Enhanced AI Agent OS - Local Deployment Guide

**Version:** 1.0  
**Author:** Manus AI  
**Date:** August 2025  

## Overview

This directory contains all the necessary scripts, configurations, and documentation for deploying the Enhanced AI Agent OS in a local development environment. The local deployment provides a complete AI agent ecosystem with enterprise-grade monitoring, security, and AI capabilities optimized for development and testing.

## Quick Start

For immediate deployment, run the one-click deployment script:

```bash
./deploy.sh
```

This script will automatically:
- Check system requirements
- Generate secure configurations
- Deploy all services
- Verify deployment health
- Provide access information

## System Requirements

### Minimum Requirements
- **Operating System:** Linux, macOS, or Windows with WSL2
- **RAM:** 8GB (16GB recommended)
  - For systems with 8GB RAM, the script automatically adjusts memory limits
  - For systems with less than 8GB RAM, manual memory configuration may be required
- **CPU:** 4 cores (8 cores recommended)
- **Storage:** 20GB available space
- **Docker:** Version 20.10 or later
- **Docker Compose:** Version 2.0 or later

**Note:** The deployment script automatically detects available system memory and adjusts service memory limits accordingly. On systems with limited RAM, Neo4j memory settings are automatically reduced to prevent startup failures.

### Recommended Requirements
- **RAM:** 16GB or more for optimal performance
- **CPU:** 8 cores or more for concurrent AI processing
- **Storage:** 50GB or more for data growth and backups
- **Network:** Stable internet connection for AI model access

## Architecture Overview

The local deployment includes the following services:

### Core Services
- **PostgreSQL + pgvector:** Vector database for AI embeddings
- **Neo4j:** Knowledge graph consciousness substrate
- **RabbitMQ:** Message queue for inter-service communication
- **n8n:** AI workflow orchestration platform

### Monitoring Stack
- **Prometheus:** Metrics collection and storage
- **Grafana:** Visualization and dashboards
- **Loki:** Log aggregation and analysis
- **Alertmanager:** Alert routing and management

### Supporting Services
- **Promtail:** Log collection agent
- **Node Exporter:** System metrics collection
- **Nginx:** Reverse proxy (production profile)

## Directory Structure

```
deploy-local/
├── README.md                 # This file
├── deploy.sh                 # One-click deployment script
├── scripts/
│   ├── check-requirements.sh # System requirements checker
│   ├── generate-config.sh    # Configuration generator
│   ├── start-services.sh     # Service startup orchestrator
│   ├── verify-deployment.sh  # Deployment verification
│   └── cleanup.sh           # Environment cleanup
├── configs/
│   ├── .env.template        # Environment template
│   ├── docker-compose.yml   # Service orchestration
│   └── monitoring/          # Monitoring configurations
├── docs/
│   ├── troubleshooting.md   # Common issues and solutions
│   ├── configuration.md     # Advanced configuration guide
│   └── maintenance.md       # Maintenance procedures
└── examples/
    ├── workflows/           # Sample n8n workflows
    └── dashboards/          # Sample Grafana dashboards
```

## Pre-Deployment Steps

### 1. Install Prerequisites

**Docker Installation:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS (using Homebrew)
brew install --cask docker

# Windows
# Download Docker Desktop from https://docker.com
```

**Docker Compose Installation:**
```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# macOS/Windows
# Included with Docker Desktop
```

### 2. Clone Repository

```bash
git clone https://github.com/KevinDyerAU/NeoV3.git
cd NeoV3/enhanced-ai-agent-os/deploy-local
```

### 3. Configure AI API Keys

Before deployment, you'll need API keys for AI services. Edit the generated `.env` file after running the deployment script:

```bash
# Required for full functionality
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Deployment Process

### Automated Deployment (Recommended)

The automated deployment script handles all aspects of the deployment process:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
1. Check system requirements and dependencies
2. Verify port availability and resolve conflicts
3. Generate secure environment configuration
4. Deploy services in dependency order
5. Verify service health and connectivity
6. Display access information and credentials

### Manual Deployment (Advanced Users)

For advanced users who prefer manual control:

```bash
# 1. Check requirements
./scripts/check-requirements.sh

# 2. Generate configuration
./scripts/generate-config.sh

# 3. Start services
./scripts/start-services.sh

# 4. Verify deployment
./scripts/verify-deployment.sh
```

## Post-Deployment Configuration

### 1. Access Services

After successful deployment, access the following services:

- **n8n Orchestration:** http://localhost:5678
- **Grafana Monitoring:** http://localhost:3000
- **Prometheus Metrics:** http://localhost:9090
- **RabbitMQ Management:** http://localhost:15672
- **Neo4j Browser:** http://localhost:7474

### 2. Import Workflows

Import the sample AI agent workflows:

1. Access n8n at http://localhost:5678
2. Log in with credentials from deployment output
3. Navigate to "Import from File"
4. Import workflows from `examples/workflows/`
5. Activate imported workflows

### 3. Configure Monitoring

Set up monitoring dashboards:

1. Access Grafana at http://localhost:3000
2. Log in with admin credentials
3. Import dashboards from `examples/dashboards/`
4. Configure alert notifications (optional)

### 4. Test AI Capabilities

Verify AI agent functionality:

1. Access the AI Chat Agent workflow in n8n
2. Test with a simple query
3. Monitor execution in Grafana dashboards
4. Check logs for any issues

## Service Management

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d n8n

# Start with logs
docker-compose up
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Data loss)
docker-compose down -v

# Stop specific service
docker-compose stop n8n
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f n8n

# View recent logs
docker-compose logs --tail=100 n8n
```

### Service Health Checks

```bash
# Check service status
docker-compose ps

# Check service health
./scripts/verify-deployment.sh

# View resource usage
docker stats
```

## Configuration Management

### Environment Variables

The `.env` file contains all configuration options. Key sections include:

**Database Configuration:**
```bash
POSTGRES_PASSWORD=generated_secure_password
NEO4J_AUTH=neo4j/generated_secure_password
RABBITMQ_DEFAULT_PASS=generated_secure_password
```

**AI Service Configuration:**
```bash
OPENAI_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key
GOOGLE_AI_API_KEY=your_api_key
```

**Resource Limits:**
```bash
POSTGRES_MEMORY_LIMIT=1g
NEO4J_MEMORY_LIMIT=2g
N8N_MEMORY_LIMIT=1g
```

### Advanced Configuration

For advanced configuration options, see `docs/configuration.md`.

## Monitoring and Observability

### Metrics and Dashboards

The deployment includes comprehensive monitoring:

- **System Metrics:** CPU, memory, disk, network usage
- **Application Metrics:** n8n workflow execution, database performance
- **AI Metrics:** Model response times, token usage, error rates
- **Business Metrics:** Task completion rates, user satisfaction

### Log Aggregation

Centralized logging through Loki:

- **Application Logs:** n8n, database, message queue logs
- **System Logs:** Docker container and host system logs
- **Audit Logs:** Security events and access logs

### Alerting

Automated alerting for:

- **Resource Exhaustion:** High CPU, memory, or disk usage
- **Service Failures:** Container crashes or health check failures
- **Performance Issues:** Slow response times or high error rates
- **Security Events:** Unauthorized access attempts

## Security Considerations

### Network Security

- Services isolated in Docker networks
- External access limited to essential ports
- Reverse proxy for production deployments

### Authentication and Authorization

- Unique passwords generated for each service
- JWT-based session management
- Role-based access control where supported

### Data Protection

- Encrypted storage volumes
- Secure credential storage
- Backup encryption capabilities

## Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Check port usage
sudo lsof -i :5678

# Kill conflicting process
sudo kill -9 <PID>
```

**Memory Issues:**
```bash
# Check available memory
free -h

# Adjust resource limits in .env file
NEO4J_MEMORY_LIMIT=1g
```

**Service Startup Failures:**
```bash
# Check service logs
docker-compose logs service_name

# Restart specific service
docker-compose restart service_name
```

### Neo4j Memory Configuration Issues

If Neo4j fails to start with memory configuration errors:

1. **Check available system memory**:
   ```bash
   free -h
   ```

2. **For systems with less than 8GB RAM**, the deployment script automatically adjusts memory limits, but you may need to manually reduce them further in the `.env` file:
   ```bash
   NEO4J_server_memory_heap_max__size=256m
   NEO4J_server_memory_pagecache_size=128m
   ```

3. **Check Neo4j logs** for specific memory errors:
   ```bash
   docker compose logs neo4j
   ```

4. **Restart deployment** after adjusting memory settings:
   ```bash
   docker compose down -v
   ./deploy.sh
   ```

### Service Startup Timeouts

If services take longer than 5 minutes to start:

1. **Check Docker resource limits** in Docker Desktop settings
2. **Verify internet connectivity** for image downloads
3. **Monitor system resources** during startup:
   ```bash
   htop
   docker stats
   ```

For detailed troubleshooting, see `docs/troubleshooting.md`.

## Maintenance

### Regular Maintenance Tasks

- **Daily:** Monitor service health and resource usage
- **Weekly:** Review logs for errors and performance issues
- **Monthly:** Update Docker images and security patches
- **Quarterly:** Review and optimize resource allocation

### Backup Procedures

```bash
# Backup databases
./scripts/backup-databases.sh

# Backup configurations
./scripts/backup-configs.sh

# Full system backup
./scripts/full-backup.sh
```

### Updates and Upgrades

```bash
# Update Docker images
docker-compose pull

# Restart with new images
docker-compose up -d

# Verify update
./scripts/verify-deployment.sh
```

## Performance Optimization

### Resource Tuning

Adjust resource limits based on your system:

```bash
# For systems with 8GB RAM
POSTGRES_MEMORY_LIMIT=512m
NEO4J_MEMORY_LIMIT=1g
N8N_MEMORY_LIMIT=512m

# For systems with 16GB+ RAM
POSTGRES_MEMORY_LIMIT=2g
NEO4J_MEMORY_LIMIT=4g
N8N_MEMORY_LIMIT=2g
```

### Database Optimization

- Configure PostgreSQL connection pooling
- Optimize Neo4j heap sizes
- Implement query optimization strategies

### Workflow Optimization

- Design efficient n8n workflows
- Implement caching strategies
- Optimize AI model selection

## Development Workflow

### Workflow Development

1. Create workflows in n8n interface
2. Export workflows for version control
3. Test in development environment
4. Deploy to production when ready

### Custom Node Development

1. Develop custom n8n nodes
2. Build and test locally
3. Deploy through Docker volumes
4. Document and share with team

### Integration Development

1. Develop API integrations
2. Test with local services
3. Implement error handling
4. Monitor performance metrics

## Support and Resources

### Documentation

- **Configuration Guide:** `docs/configuration.md`
- **Troubleshooting Guide:** `docs/troubleshooting.md`
- **Maintenance Guide:** `docs/maintenance.md`

### Community Resources

- **GitHub Repository:** https://github.com/KevinDyerAU/NeoV3
- **n8n Documentation:** https://docs.n8n.io/
- **Docker Documentation:** https://docs.docker.com/

### Getting Help

1. Check the troubleshooting guide
2. Review service logs for errors
3. Search existing GitHub issues
4. Create new issue with detailed information

## License and Contributing

This project is part of the Enhanced AI Agent OS ecosystem. Please refer to the main repository for license information and contribution guidelines.

---

**Next Steps:**
1. Run `./deploy.sh` to start your deployment
2. Configure your AI API keys
3. Import sample workflows
4. Explore the monitoring dashboards
5. Begin developing your AI agent workflows

For questions or issues, please refer to the troubleshooting guide or create an issue in the GitHub repository.

