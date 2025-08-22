#!/bin/bash

# Enhanced AI Agent OS - Local Deployment Script
# Version: 1.0
# Author: Manus AI
# Description: One-click deployment script for local development environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
LOG_FILE="$SCRIPT_DIR/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

header() {
    echo -e "${PURPLE}[PHASE]${NC} $1" | tee -a "$LOG_FILE"
}

# Wrapper to call Docker Compose v2 (docker compose) or v1 (docker-compose)
docker_compose() {
    if docker compose version --short >/dev/null 2>&1; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# Display banner
display_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Enhanced AI Agent OS - Local Deployment                  ║
║                                                                              ║
║  🤖 Enterprise-grade AI agent ecosystem for local development               ║
║  🔧 Automated deployment with intelligent configuration                      ║
║  📊 Complete monitoring stack with Prometheus & Grafana                     ║
║  🛡️  Security-first design with encrypted communications                     ║
║                                                                              ║
║  Version: 1.0 | Author: Manus AI | Date: August 2025                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# System requirements check
check_system_requirements() {
    header "Checking System Requirements"
    
    local requirements_met=true
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker and try again."
        requirements_met=false
    else
        local docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        info "Docker version: $docker_version"
        
        # Check if Docker daemon is running
        if ! docker info &> /dev/null; then
            error "Docker daemon is not running. Please start Docker and try again."
            requirements_met=false
        fi
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose and try again."
        requirements_met=false
    else
        if command -v docker-compose &> /dev/null; then
            local compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            info "Docker Compose version: $compose_version"
        else
            local compose_version=$(docker compose version --short)
            info "Docker Compose version: $compose_version"
        fi
    fi
    
    # Check available memory
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
        local total_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')
        info "Available memory: ${available_memory}MB / ${total_memory}MB"
        
        if [ "$available_memory" -lt 4096 ]; then
            warning "Available memory is less than 4GB. Performance may be impacted."
            warning "Consider closing other applications or adding more RAM."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        local total_memory=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024)}')
        info "Total memory: ${total_memory}MB"
        
        if [ "$total_memory" -lt 8192 ]; then
            warning "Total memory is less than 8GB. Performance may be impacted."
        fi
    fi
    
    # Check available disk space
    local available_space=$(df -BG "$SCRIPT_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    info "Available disk space: ${available_space}GB"
    
    if [ "$available_space" -lt 20 ]; then
        warning "Available disk space is less than 20GB. Consider freeing up space."
        warning "The deployment requires approximately 15GB for images and data."
    fi
    
    # Check CPU cores
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        local cpu_cores=$(nproc)
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        local cpu_cores=$(sysctl -n hw.ncpu)
    else
        local cpu_cores="unknown"
    fi
    
    if [[ "$cpu_cores" != "unknown" ]]; then
        info "CPU cores: $cpu_cores"
        if [ "$cpu_cores" -lt 4 ]; then
            warning "Less than 4 CPU cores detected. Performance may be impacted."
        fi
    fi
    
    # Check network connectivity
    if ! ping -c 1 google.com &> /dev/null; then
        warning "Network connectivity check failed. Internet access is required for image downloads."
    else
        info "Network connectivity: OK"
    fi
    
    if [ "$requirements_met" = false ]; then
        error "System requirements not met. Please address the issues above and try again."
    fi
    
    success "System requirements check completed successfully."
}

# Port availability check
check_port_availability() {
    header "Checking Port Availability"
    
    local required_ports=(5432 7474 7687 5672 15672 5678 3000 9090 9093 3100 9100)
    local conflicting_ports=()
    local alternative_ports=()
    
    for port in "${required_ports[@]}"; do
        if command -v lsof &> /dev/null; then
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                conflicting_ports+=($port)
                # Suggest alternative port
                local alt_port=$((port + 1000))
                alternative_ports+=($alt_port)
                warning "Port $port is in use. Will attempt to use port $alt_port instead."
            else
                info "Port $port is available."
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -ln | grep -q ":$port "; then
                conflicting_ports+=($port)
                local alt_port=$((port + 1000))
                alternative_ports+=($alt_port)
                warning "Port $port is in use. Will attempt to use port $alt_port instead."
            else
                info "Port $port is available."
            fi
        else
            warning "Cannot check port availability. lsof and netstat not found."
            break
        fi
    done
    
    if [ ${#conflicting_ports[@]} -gt 0 ]; then
        warning "Found ${#conflicting_ports[@]} port conflicts. Alternative ports will be used."
        info "Conflicting ports: ${conflicting_ports[*]}"
        info "Alternative ports: ${alternative_ports[*]}"
        
        # Store alternative ports for configuration generation
        export PORT_CONFLICTS="${conflicting_ports[*]}"
        export ALTERNATIVE_PORTS="${alternative_ports[*]}"
    else
        success "All required ports are available."
    fi
}

# Generate secure environment configuration
generate_environment_config() {
    header "Generating Environment Configuration"
    
    if [ -f "$ENV_FILE" ]; then
        warning "Environment file already exists. Creating backup."
        cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"
    fi
    
    info "Generating secure passwords and configuration..."
    
    # Generate secure random passwords
    local postgres_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local neo4j_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local rabbitmq_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local n8n_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local grafana_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local jwt_secret=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    local encryption_key=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    # Determine resource limits based on available memory
    local postgres_memory="1g"
    local neo4j_memory="1g"
    local neo4j_heap_memory="512m"
    local neo4j_pagecache_memory="256m"
    local n8n_memory="1g"
    local prometheus_memory="1g"
    local grafana_memory="512m"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        local total_memory=$(free -m | awk 'NR==2{printf "%.0f", $2}')
        if [ "$total_memory" -lt 8192 ]; then
            postgres_memory="512m"
            neo4j_memory="512m"
            neo4j_heap_memory="256m"
            neo4j_pagecache_memory="128m"
            n8n_memory="512m"
            prometheus_memory="512m"
            grafana_memory="256m"
            info "Adjusted memory limits for system with ${total_memory}MB RAM"
        fi
    fi
    
    # Handle port conflicts
    local postgres_port=5432
    local neo4j_http_port=7474
    local neo4j_bolt_port=7687
    local rabbitmq_port=5672
    local rabbitmq_mgmt_port=15672
    local n8n_port=5678
    local grafana_port=3000
    local prometheus_port=9090
    local alertmanager_port=9093
    local loki_port=3100
    local node_exporter_port=9100
    
    if [ -n "${PORT_CONFLICTS:-}" ]; then
        IFS=' ' read -ra conflicts <<< "$PORT_CONFLICTS"
        IFS=' ' read -ra alternatives <<< "$ALTERNATIVE_PORTS"
        
        for i in "${!conflicts[@]}"; do
            case "${conflicts[i]}" in
                5432) postgres_port="${alternatives[i]}" ;;
                7474) neo4j_http_port="${alternatives[i]}" ;;
                7687) neo4j_bolt_port="${alternatives[i]}" ;;
                5672) rabbitmq_port="${alternatives[i]}" ;;
                15672) rabbitmq_mgmt_port="${alternatives[i]}" ;;
                5678) n8n_port="${alternatives[i]}" ;;
                3000) grafana_port="${alternatives[i]}" ;;
                9090) prometheus_port="${alternatives[i]}" ;;
                9093) alertmanager_port="${alternatives[i]}" ;;
                3100) loki_port="${alternatives[i]}" ;;
                9100) node_exporter_port="${alternatives[i]}" ;;
            esac
        done
    fi
    
    cat > "$ENV_FILE" << EOF
# Enhanced AI Agent OS - Local Environment Configuration
# Generated on $(date)
# 
# This file contains all configuration for the Enhanced AI Agent OS local deployment.
# Modify values as needed for your environment.

# =============================================================================
# CORE SYSTEM CONFIGURATION
# =============================================================================

# Environment
NODE_ENV=development
ENVIRONMENT=local
COMPOSE_PROJECT_NAME=enhanced-ai-agent-os

# Network Configuration
DOCKER_NETWORK_SUBNET=172.20.0.0/16
DOCKER_NETWORK_GATEWAY=172.20.0.1

# =============================================================================
# SERVICE PORT CONFIGURATION
# =============================================================================

# PostgreSQL
POSTGRES_PORT=${postgres_port}

# Neo4j
NEO4J_HTTP_PORT=${neo4j_http_port}
NEO4J_BOLT_PORT=${neo4j_bolt_port}

# RabbitMQ
RABBITMQ_PORT=${rabbitmq_port}
RABBITMQ_MANAGEMENT_PORT=${rabbitmq_mgmt_port}

# n8n
N8N_PORT=${n8n_port}

# Monitoring Services
GRAFANA_PORT=${grafana_port}
PROMETHEUS_PORT=${prometheus_port}
ALERTMANAGER_PORT=${alertmanager_port}
LOKI_PORT=${loki_port}
NODE_EXPORTER_PORT=${node_exporter_port}

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_DB=enhanced_ai_agent_os
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB

# Neo4j Configuration
NEO4J_HOST=neo4j
NEO4J_AUTH=neo4j/${neo4j_password}
NEO4J_PLUGINS=["apoc"]
NEO4J_server_memory_heap_initial__size=512m
NEO4J_server_memory_heap_max__size=${neo4j_heap_memory}
NEO4J_server_memory_pagecache_size=${neo4j_pagecache_memory}

# =============================================================================
# MESSAGE QUEUE CONFIGURATION
# =============================================================================

# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=${rabbitmq_password}
RABBITMQ_DEFAULT_VHOST=/
RABBITMQ_ERLANG_COOKIE=enhanced_ai_agent_os_cookie

# =============================================================================
# AI ORCHESTRATION CONFIGURATION
# =============================================================================

# n8n Configuration
N8N_HOST=0.0.0.0
N8N_PROTOCOL=http
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=${n8n_password}

# Webhook Configuration
WEBHOOK_URL=http://localhost:${n8n_port}

# Workflow Configuration
N8N_WORKFLOWS_FOLDER=/home/node/.n8n/workflows
N8N_USER_FOLDER=/home/node/.n8n

# =============================================================================
# AI SERVICE CONFIGURATION
# =============================================================================

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_ORGANIZATION=your_organization_id_here

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_API_BASE=https://api.anthropic.com

# Google AI Configuration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================

# Prometheus Configuration
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_STORAGE_TSDB_RETENTION_SIZE=10GB
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=${grafana_password}
GRAFANA_ALLOW_SIGN_UP=false
GRAFANA_DISABLE_GRAVATAR=true

# Alertmanager Configuration
ALERTMANAGER_SMTP_FROM=alerts@enhanced-ai-agent-os.local
ALERTMANAGER_SMTP_SMARTHOST=localhost:587

# Loki Configuration
LOKI_RETENTION_PERIOD=168h

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# JWT Configuration
JWT_SECRET=${jwt_secret}
JWT_EXPIRATION=24h
JWT_REFRESH_EXPIRATION=7d

# Encryption Configuration
ENCRYPTION_KEY=${encryption_key}
ENCRYPTION_ALGORITHM=AES-256-GCM

# SSL Configuration (for production)
SSL_CERT_PATH=/etc/ssl/certs/enhanced-ai-agent-os.crt
SSL_KEY_PATH=/etc/ssl/private/enhanced-ai-agent-os.key

# =============================================================================
# RESOURCE LIMITS
# =============================================================================

# Memory Limits
POSTGRES_MEMORY_LIMIT=${postgres_memory}
NEO4J_MEMORY_LIMIT=${neo4j_memory}
RABBITMQ_MEMORY_LIMIT=512m
N8N_MEMORY_LIMIT=${n8n_memory}
PROMETHEUS_MEMORY_LIMIT=${prometheus_memory}
GRAFANA_MEMORY_LIMIT=${grafana_memory}
LOKI_MEMORY_LIMIT=512m
ALERTMANAGER_MEMORY_LIMIT=256m

# CPU Limits
POSTGRES_CPU_LIMIT=1.0
NEO4J_CPU_LIMIT=2.0
RABBITMQ_CPU_LIMIT=0.5
N8N_CPU_LIMIT=1.0
PROMETHEUS_CPU_LIMIT=1.0
GRAFANA_CPU_LIMIT=0.5
LOKI_CPU_LIMIT=0.5
ALERTMANAGER_CPU_LIMIT=0.25

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================

# Backup Settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_ENABLED=true

# Backup Paths
BACKUP_PATH=/backups
POSTGRES_BACKUP_PATH=/backups/postgres
NEO4J_BACKUP_PATH=/backups/neo4j
N8N_BACKUP_PATH=/backups/n8n

# =============================================================================
# DEVELOPMENT CONFIGURATION
# =============================================================================

# Debug Settings
DEBUG_MODE=false
LOG_LEVEL=info
VERBOSE_LOGGING=false

# Development Features
HOT_RELOAD_ENABLED=true
DEV_TOOLS_ENABLED=true
MOCK_EXTERNAL_APIS=false

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Monitoring Features
ENABLE_PROMETHEUS=true
ENABLE_GRAFANA=true
ENABLE_LOKI=true
ENABLE_ALERTMANAGER=true
ENABLE_NODE_EXPORTER=true

# Security Features
ENABLE_SSL=false
ENABLE_RATE_LIMITING=true
ENABLE_AUDIT_LOGGING=true

# AI Features
ENABLE_MULTI_MODEL=true
ENABLE_CONVERSATION_MEMORY=true
ENABLE_TOOL_DISCOVERY=true

EOF

    # Store generated passwords for display
    export GENERATED_POSTGRES_PASSWORD="$postgres_password"
    export GENERATED_NEO4J_PASSWORD="$neo4j_password"
    export GENERATED_RABBITMQ_PASSWORD="$rabbitmq_password"
    export GENERATED_N8N_PASSWORD="$n8n_password"
    export GENERATED_GRAFANA_PASSWORD="$grafana_password"
    
    # Store port configuration for display
    export CONFIGURED_N8N_PORT="$n8n_port"
    export CONFIGURED_GRAFANA_PORT="$grafana_port"
    export CONFIGURED_PROMETHEUS_PORT="$prometheus_port"
    export CONFIGURED_RABBITMQ_MGMT_PORT="$rabbitmq_mgmt_port"
    export CONFIGURED_NEO4J_HTTP_PORT="$neo4j_http_port"
    
    success "Environment configuration generated successfully."
    info "Configuration saved to: $ENV_FILE"
    warning "Please update AI API keys in the .env file before full functionality."
}

# Create Docker Compose configuration
create_docker_compose() {
    header "Creating Docker Compose Configuration"
    
    cat > "$COMPOSE_FILE" << 'EOF'
# Enhanced AI Agent OS - Local Docker Compose Configuration
# This file defines all services required for the Enhanced AI Agent OS

services:
  # =============================================================================
  # DATABASE SERVICES
  # =============================================================================
  
  postgres:
    image: pgvector/pgvector:pg15
    container_name: enhanced-ai-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - postgres_backups:/backups
      - ./configs/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${POSTGRES_MEMORY_LIMIT}
          cpus: '${POSTGRES_CPU_LIMIT}'
        reservations:
          memory: 256M
          cpus: '0.25'

  neo4j:
    image: neo4j:5.13-community
    container_name: enhanced-ai-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
      NEO4J_PLUGINS: ${NEO4J_PLUGINS}
      NEO4J_server_memory_heap_initial__size: ${NEO4J_server_memory_heap_initial__size}
      NEO4J_server_memory_heap_max__size: ${NEO4J_server_memory_heap_max__size}
      NEO4J_server_memory_pagecache_size: ${NEO4J_server_memory_pagecache_size}
      NEO4J_dbms_security_procedures_unrestricted: apoc.*,gds.*
      NEO4J_dbms_security_procedures_allowlist: apoc.*,gds.*
    ports:
      - "${NEO4J_HTTP_PORT}:7474"
      - "${NEO4J_BOLT_PORT}:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
      - neo4j_backups:/backups
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "wget --spider -q http://localhost:7474 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 180s
    deploy:
      resources:
        limits:
          memory: ${NEO4J_MEMORY_LIMIT}
          cpus: '${NEO4J_CPU_LIMIT}'
        reservations:
          memory: 512M
          cpus: '0.5'

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: enhanced-ai-rabbitmq
    restart: unless-stopped
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
      RABBITMQ_DEFAULT_VHOST: ${RABBITMQ_DEFAULT_VHOST}
      RABBITMQ_ERLANG_COOKIE: ${RABBITMQ_ERLANG_COOKIE}
    ports:
      - "${RABBITMQ_PORT}:5672"
      - "${RABBITMQ_MANAGEMENT_PORT}:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
      - rabbitmq_logs:/var/log/rabbitmq
      - rabbitmq_backups:/backups
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "rabbitmq-diagnostics -q ping"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${RABBITMQ_MEMORY_LIMIT}
          cpus: '${RABBITMQ_CPU_LIMIT}'
        reservations:
          memory: 256M
          cpus: '0.25'

  # =============================================================================
  # AI ORCHESTRATION SERVICES
  # =============================================================================

  n8n:
    image: n8nio/n8n:latest
    container_name: enhanced-ai-n8n
    restart: unless-stopped
    environment:
      N8N_HOST: ${N8N_HOST}
      N8N_PORT: ${N8N_PORT}
      N8N_PROTOCOL: ${N8N_PROTOCOL}
      WEBHOOK_URL: ${WEBHOOK_URL}
      N8N_BASIC_AUTH_ACTIVE: ${N8N_BASIC_AUTH_ACTIVE}
      N8N_BASIC_AUTH_USER: ${N8N_BASIC_AUTH_USER}
      N8N_BASIC_AUTH_PASSWORD: ${N8N_BASIC_AUTH_PASSWORD}
      
      # Database Configuration
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: ${POSTGRES_DB}
      DB_POSTGRESDB_USER: ${POSTGRES_USER}
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}
      
      # AI Service Configuration
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      GOOGLE_AI_API_KEY: ${GOOGLE_AI_API_KEY}
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      
      # Workflow Configuration
      N8N_WORKFLOWS_FOLDER: ${N8N_WORKFLOWS_FOLDER}
      N8N_USER_FOLDER: ${N8N_USER_FOLDER}
      
      # Security Configuration
      N8N_ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      
      # Feature Flags
      N8N_DISABLE_UI: false
      N8N_METRICS: true
      N8N_LOG_LEVEL: ${LOG_LEVEL}
    ports:
      - "${N8N_PORT}:5678"
    volumes:
      - n8n_data:/home/node/.n8n
      - n8n_logs:/var/log/n8n
      - n8n_backups:/backups
      - ./examples/workflows:/home/node/.n8n/workflows:ro
    networks:
      - enhanced-ai-network
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5678/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: ${N8N_MEMORY_LIMIT}
          cpus: '${N8N_CPU_LIMIT}'
        reservations:
          memory: 512M
          cpus: '0.5'

  # =============================================================================
  # MONITORING SERVICES
  # =============================================================================

  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: enhanced-ai-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION_TIME}'
      - '--storage.tsdb.retention.size=${PROMETHEUS_STORAGE_TSDB_RETENTION_SIZE}'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    ports:
      - "${PROMETHEUS_PORT}:9090"
    volumes:
      - ./configs/monitoring/prometheus:/etc/prometheus:ro
      - prometheus_data:/prometheus
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:9090/-/healthy || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${PROMETHEUS_MEMORY_LIMIT}
          cpus: '${PROMETHEUS_CPU_LIMIT}'
        reservations:
          memory: 256M
          cpus: '0.25'

  grafana:
    image: grafana/grafana:10.1.0
    container_name: enhanced-ai-grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_USERS_ALLOW_SIGN_UP: ${GRAFANA_ALLOW_SIGN_UP}
      GF_USERS_DISABLE_GRAVATAR: ${GRAFANA_DISABLE_GRAVATAR}
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    ports:
      - "${GRAFANA_PORT}:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - grafana_logs:/var/log/grafana
      - ./configs/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./examples/dashboards:/var/lib/grafana/dashboards:ro
    networks:
      - enhanced-ai-network
    depends_on:
      - prometheus
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${GRAFANA_MEMORY_LIMIT}
          cpus: '${GRAFANA_CPU_LIMIT}'
        reservations:
          memory: 128M
          cpus: '0.1'

  loki:
    image: grafana/loki:2.9.0
    container_name: enhanced-ai-loki
    restart: unless-stopped
    command: -config.file=/etc/loki/local-config.yaml
    ports:
      - "${LOKI_PORT}:3100"
    volumes:
      - ./configs/monitoring/loki:/etc/loki:ro
      - loki_data:/loki
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3100/ready || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${LOKI_MEMORY_LIMIT}
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.1'

  promtail:
    image: grafana/promtail:2.9.0
    container_name: enhanced-ai-promtail
    restart: unless-stopped
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./configs/monitoring/promtail:/etc/promtail:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - enhanced-ai-network
    depends_on:
      - loki
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 64M
          cpus: '0.05'

  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: enhanced-ai-alertmanager
    restart: unless-stopped
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:${ALERTMANAGER_PORT}'
    ports:
      - "${ALERTMANAGER_PORT}:9093"
    volumes:
      - ./configs/monitoring/alertmanager:/etc/alertmanager:ro
      - alertmanager_data:/alertmanager
    networks:
      - enhanced-ai-network
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:9093/-/healthy || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: ${ALERTMANAGER_MEMORY_LIMIT}
          cpus: '0.25'
        reservations:
          memory: 64M
          cpus: '0.05'

  node-exporter:
    image: prom/node-exporter:v1.6.1
    container_name: enhanced-ai-node-exporter
    restart: unless-stopped
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "${NODE_EXPORTER_PORT}:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - enhanced-ai-network
    profiles:
      - linux
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'
        reservations:
          memory: 32M
          cpus: '0.02'

# =============================================================================
# NETWORKS
# =============================================================================

networks:
  enhanced-ai-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: ${DOCKER_NETWORK_SUBNET}
          gateway: ${DOCKER_NETWORK_GATEWAY}
    driver_opts:
      com.docker.network.bridge.name: enhanced-ai-br0
      com.docker.network.driver.mtu: 1500

# =============================================================================
# VOLUMES
# =============================================================================

volumes:
  # Database Volumes
  postgres_data:
    driver: local
  postgres_backups:
    driver: local

  # Neo4j Volumes
  neo4j_data:
    driver: local
  neo4j_logs:
    driver: local
  neo4j_import:
    driver: local
  neo4j_plugins:
    driver: local
  neo4j_backups:
    driver: local

  # RabbitMQ Volumes
  rabbitmq_data:
    driver: local
  rabbitmq_logs:
    driver: local
  rabbitmq_backups:
    driver: local

  # n8n Volumes
  n8n_data:
    driver: local
  n8n_logs:
    driver: local
  n8n_backups:
    driver: local

  # Monitoring Volumes
  prometheus_data:
    driver: local

  grafana_data:
    driver: local
  grafana_logs:
    driver: local

  alertmanager_data:
    driver: local

  loki_data:
    driver: local
EOF

    success "Docker Compose configuration created successfully."
}

# Create directory structure
create_directory_structure() {
    header "Creating Directory Structure"
    
    local directories=(
        "data/postgres"
        "data/neo4j"
        "data/rabbitmq"
        "data/n8n"
        "data/prometheus"
        "data/grafana"
        "data/alertmanager"
        "data/loki"
        "logs/postgres"
        "logs/neo4j"
        "logs/rabbitmq"
        "logs/n8n"
        "logs/grafana"
        "backups/postgres"
        "backups/neo4j"
        "backups/rabbitmq"
        "backups/n8n"
        "import/neo4j"
        "plugins/neo4j"
        "configs/postgres"
        "configs/monitoring/prometheus"
        "configs/monitoring/grafana/provisioning/datasources"
        "configs/monitoring/grafana/provisioning/dashboards"
        "configs/monitoring/loki"
        "configs/monitoring/promtail"
        "configs/monitoring/alertmanager"
        "examples/workflows"
        "examples/dashboards"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$SCRIPT_DIR/$dir"
        info "Created directory: $dir"
    done
    
    # Set appropriate permissions
    # On Windows/WSL (NTFS mounts under /mnt/*), chmod may fail with "Operation not permitted".
    # Attempt to set permissions, but do not fail the deployment if it's unsupported.
    if ! chmod -R 755 "$SCRIPT_DIR/data" 2>/dev/null; then
        warning "Skipping chmod on $SCRIPT_DIR/data (likely NTFS/WSL mount)."
    fi
    if ! chmod -R 755 "$SCRIPT_DIR/logs" 2>/dev/null; then
        warning "Skipping chmod on $SCRIPT_DIR/logs (likely NTFS/WSL mount)."
    fi
    if ! chmod -R 755 "$SCRIPT_DIR/backups" 2>/dev/null; then
        warning "Skipping chmod on $SCRIPT_DIR/backups (likely NTFS/WSL mount)."
    fi
    
    success "Directory structure created successfully."
}

# Create configuration files
create_configuration_files() {
    header "Creating Configuration Files"
    
    # PostgreSQL initialization script
    cat > "$SCRIPT_DIR/configs/postgres/init.sql" << 'EOF'
-- Enhanced AI Agent OS - PostgreSQL Initialization Script
-- This script sets up the database schema and extensions

-- Create pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create additional useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schema for AI agent data
CREATE SCHEMA IF NOT EXISTS ai_agents;

-- Create table for vector embeddings
CREATE TABLE IF NOT EXISTS ai_agents.embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON ai_agents.embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create table for agent conversations
CREATE TABLE IF NOT EXISTS ai_agents.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    message_history JSONB NOT NULL DEFAULT '[]',
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS conversations_agent_id_idx ON ai_agents.conversations (agent_id);
CREATE INDEX IF NOT EXISTS conversations_user_id_idx ON ai_agents.conversations (user_id);
CREATE INDEX IF NOT EXISTS conversations_created_at_idx ON ai_agents.conversations (created_at);

-- Create table for workflow execution logs
CREATE TABLE IF NOT EXISTS ai_agents.workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for workflow execution logs
CREATE INDEX IF NOT EXISTS workflow_executions_workflow_id_idx ON ai_agents.workflow_executions (workflow_id);
CREATE INDEX IF NOT EXISTS workflow_executions_status_idx ON ai_agents.workflow_executions (status);
CREATE INDEX IF NOT EXISTS workflow_executions_started_at_idx ON ai_agents.workflow_executions (started_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_embeddings_updated_at BEFORE UPDATE ON ai_agents.embeddings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON ai_agents.conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to n8n user
GRANT USAGE ON SCHEMA ai_agents TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_agents TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ai_agents TO postgres;

-- Create user for n8n if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'n8n_user') THEN
        CREATE ROLE n8n_user WITH LOGIN PASSWORD 'n8n_password';
    END IF;
END
$$;

-- Grant permissions to n8n user
GRANT CONNECT ON DATABASE enhanced_ai_agent_os TO n8n_user;
GRANT USAGE ON SCHEMA ai_agents TO n8n_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_agents TO n8n_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ai_agents TO n8n_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_agents GRANT ALL ON TABLES TO n8n_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_agents GRANT ALL ON SEQUENCES TO n8n_user;
EOF

    # Prometheus configuration
    cat > "$SCRIPT_DIR/configs/monitoring/prometheus/prometheus.yml" << 'EOF'
# Enhanced AI Agent OS - Prometheus Configuration

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'enhanced-ai-agent-os'
    environment: 'local'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j:2004']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'alertmanager'
    static_configs:
      - targets: ['alertmanager:9093']
    scrape_interval: 30s
    metrics_path: /metrics
EOF

    # Grafana datasource configuration
    cat > "$SCRIPT_DIR/configs/monitoring/grafana/provisioning/datasources/datasources.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
EOF

    # Grafana dashboard configuration
    cat > "$SCRIPT_DIR/configs/monitoring/grafana/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

    # Loki configuration
    cat > "$SCRIPT_DIR/configs/monitoring/loki/local-config.yaml" << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093

limits_config:
  retention_period: 168h
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
EOF

    # Promtail configuration
    cat > "$SCRIPT_DIR/configs/monitoring/promtail/config.yml" << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          expressions:
            tag:
          source: attrs
      - regex:
          expression: (?P<container_name>(?:[^|]*))\|
          source: tag
      - timestamp:
          format: RFC3339Nano
          source: time
      - labels:
          stream:
          container_name:
      - output:
          source: output

  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog
EOF

    # Alertmanager configuration
    cat > "$SCRIPT_DIR/configs/monitoring/alertmanager/alertmanager.yml" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@enhanced-ai-agent-os.local'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

    success "Configuration files created successfully."
}

# Pull Docker images
pull_docker_images() {
    header "Pulling Docker Images"
    
    info "This may take several minutes depending on your internet connection..."
    
    # Pull images in parallel for faster download
    docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull --parallel || {
        warning "Parallel pull failed, trying sequential pull..."
        docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    }
    
    success "Docker images pulled successfully."
}

# Deploy services
deploy_services() {
    header "Deploying Services"
    
    info "Starting services in dependency order..."
    
    # Start foundation services first
    info "Starting foundation services (PostgreSQL, Neo4j, RabbitMQ)..."
    docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres neo4j rabbitmq
    
    # Wait for foundation services to be healthy
    info "Waiting for foundation services to be ready..."
    local max_wait=300  # 5 minutes
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps postgres | grep -q "healthy" && \
           docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps neo4j | grep -q "healthy" && \
           docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps rabbitmq | grep -q "healthy"; then
            success "Foundation services are ready."
            break
        fi
        
        info "Waiting for foundation services... ($((wait_time))s elapsed)"
        sleep 10
        wait_time=$((wait_time + 10))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        error "Foundation services failed to start within $max_wait seconds."
        info "Checking service logs for errors..."
        docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs postgres neo4j rabbitmq | tail -20
        error "Please check the logs above and system resources. You may need to adjust memory limits in the .env file."
        return 1
    fi
    
    # Start orchestration services
    info "Starting orchestration services (n8n)..."
    docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d n8n
    
    # Wait for n8n to be ready
    info "Waiting for n8n to be ready..."
    wait_time=0
    while [ $wait_time -lt $max_wait ]; do
        if docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps n8n | grep -q "healthy"; then
            success "n8n is ready."
            break
        fi
        
        info "Waiting for n8n... ($((wait_time))s elapsed)"
        sleep 10
        wait_time=$((wait_time + 10))
    done
    
    # Start monitoring services
    info "Starting monitoring services..."
    docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d prometheus grafana loki promtail alertmanager
    
    # Start node-exporter on Linux systems
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "Starting node-exporter (Linux only)..."
        docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile linux up -d node-exporter
    fi
    
    success "All services deployed successfully."
}

# Verify deployment
verify_deployment() {
    header "Verifying Deployment"
    
    # Check service health
    local services=(postgres neo4j rabbitmq n8n prometheus grafana loki alertmanager)
    local failed_services=()
    
    for service in "${services[@]}"; do
        if ! docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps "$service" | grep -q "Up"; then
            failed_services+=($service)
        else
            info "Service $service is running."
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        error "The following services failed to start: ${failed_services[*]}"
    fi
    
    # Test connectivity
    info "Testing service connectivity..."
    
    # Test n8n
    local n8n_url="http://localhost:${CONFIGURED_N8N_PORT}"
    if curl -f "$n8n_url" >/dev/null 2>&1; then
        success "n8n is accessible at $n8n_url"
    else
        warning "n8n may not be fully ready yet. Please wait a few more minutes."
    fi
    
    # Test Grafana
    local grafana_url="http://localhost:${CONFIGURED_GRAFANA_PORT}"
    if curl -f "$grafana_url" >/dev/null 2>&1; then
        success "Grafana is accessible at $grafana_url"
    else
        warning "Grafana may not be fully ready yet. Please wait a few more minutes."
    fi
    
    # Test Prometheus
    local prometheus_url="http://localhost:${CONFIGURED_PROMETHEUS_PORT}"
    if curl -f "$prometheus_url" >/dev/null 2>&1; then
        success "Prometheus is accessible at $prometheus_url"
    else
        warning "Prometheus may not be fully ready yet. Please wait a few more minutes."
    fi
    
    success "Deployment verification completed."
}

# Display deployment summary
display_summary() {
    header "Deployment Summary"
    
    echo ""
    echo -e "${GREEN}🎉 Enhanced AI Agent OS has been successfully deployed!${NC}"
    echo ""
    echo -e "${CYAN}📊 Service URLs:${NC}"
    echo "   • n8n Orchestration: http://localhost:${CONFIGURED_N8N_PORT}"
    echo "   • Grafana Monitoring: http://localhost:${CONFIGURED_GRAFANA_PORT}"
    echo "   • Prometheus Metrics: http://localhost:${CONFIGURED_PROMETHEUS_PORT}"
    echo "   • RabbitMQ Management: http://localhost:${CONFIGURED_RABBITMQ_MGMT_PORT}"
    echo "   • Neo4j Browser: http://localhost:${CONFIGURED_NEO4J_HTTP_PORT}"
    echo ""
    echo -e "${CYAN}🔐 Default Credentials:${NC}"
    echo "   • n8n: admin / ${GENERATED_N8N_PASSWORD}"
    echo "   • Grafana: admin / ${GENERATED_GRAFANA_PASSWORD}"
    echo "   • RabbitMQ: admin / ${GENERATED_RABBITMQ_PASSWORD}"
    echo "   • Neo4j: neo4j / ${GENERATED_NEO4J_PASSWORD}"
    echo "   • PostgreSQL: postgres / ${GENERATED_POSTGRES_PASSWORD}"
    echo ""
    echo -e "${YELLOW}⚠️  Important Notes:${NC}"
    echo "   • Credentials are saved in the .env file"
    echo "   • Update AI API keys in .env for full functionality"
    echo "   • Default configuration is optimized for development"
    echo ""
    echo -e "${CYAN}📝 Next Steps:${NC}"
    echo "   1. Configure your AI API keys in the .env file:"
    echo "      • OPENAI_API_KEY=your_openai_api_key_here"
    echo "      • ANTHROPIC_API_KEY=your_anthropic_api_key_here"
    echo "      • GOOGLE_AI_API_KEY=your_google_ai_api_key_here"
    echo "      • OPENROUTER_API_KEY=your_openrouter_api_key_here"
    echo ""
    echo "   2. Access n8n to import and activate workflows:"
    echo "      • Navigate to http://localhost:${CONFIGURED_N8N_PORT}"
    echo "      • Import workflows from examples/workflows/"
    echo "      • Activate the imported workflows"
    echo ""
    echo "   3. Review monitoring dashboards in Grafana:"
    echo "      • Navigate to http://localhost:${CONFIGURED_GRAFANA_PORT}"
    echo "      • Import dashboards from examples/dashboards/"
    echo "      • Configure alert notifications (optional)"
    echo ""
    echo "   4. Test AI agent functionality:"
    echo "      • Use the AI Chat Agent workflow in n8n"
    echo "      • Monitor execution in Grafana dashboards"
    echo "      • Check logs for any issues"
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    if docker compose version --short >/dev/null 2>&1; then
        echo "   • View logs: docker compose logs -f [service_name]"
        echo "   • Stop services: docker compose down"
        echo "   • Restart services: docker compose restart [service_name]"
        echo "   • Check status: docker compose ps"
    else
        echo "   • View logs: docker-compose logs -f [service_name]"
        echo "   • Stop services: docker-compose down"
        echo "   • Restart services: docker-compose restart [service_name]"
        echo "   • Check status: docker-compose ps"
    fi
    echo ""
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "   • Configuration Guide: docs/configuration.md"
    echo "   • Troubleshooting Guide: docs/troubleshooting.md"
    echo "   • Maintenance Guide: docs/maintenance.md"
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
}

# Cleanup function for error handling
cleanup() {
    if [ $? -ne 0 ]; then
        error "Deployment failed. Check the log file: $LOG_FILE"
        echo ""
        echo "To clean up and try again:"
        if docker compose version --short >/dev/null 2>&1; then
            echo "  docker compose down -v"
        else
            echo "  docker-compose down -v"
        fi
        echo "  ./deploy.sh"
    fi
}

# Main deployment function
main() {
    # Set up error handling
    trap cleanup EXIT
    
    # Clear log file
    > "$LOG_FILE"
    
    display_banner
    check_root
    check_system_requirements
    check_port_availability
    generate_environment_config
    create_docker_compose
    create_directory_structure
    create_configuration_files
    pull_docker_images
    deploy_services
    verify_deployment
    display_summary
    
    # Remove error trap on successful completion
    trap - EXIT
}

# Execute main function with all arguments
main "$@"

