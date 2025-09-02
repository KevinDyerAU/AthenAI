#!/bin/bash

# NeoV3 Enhanced AI Agent OS - Chat Interface Launch Script
# This script launches the chat interface with automatic port conflict resolution
# and provides convenient management commands

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/neov3-chat-interface"
DEFAULT_PORT=5173
MAX_PORT=5200
LOG_FILE="${SCRIPT_DIR}/chat-ui.log"
PID_FILE="${SCRIPT_DIR}/chat-ui.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if port is available
is_port_available() {
    local port=$1
    ! nc -z localhost "$port" 2>/dev/null
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local max_port=$2
    
    for ((port=start_port; port<=max_port; port++)); do
        if is_port_available "$port"; then
            echo "$port"
            return 0
        fi
    done
    
    return 1
}

# Function to kill existing processes
kill_existing_processes() {
    info "Checking for existing chat UI processes..."
    
    # Kill processes using our PID file
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            warning "Killing existing process (PID: $pid)"
            kill "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                warning "Force killing process (PID: $pid)"
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any vite processes in our project directory
    local vite_pids=$(ps aux | grep "vite.*${PROJECT_DIR}" | grep -v grep | awk '{print $2}' || true)
    if [[ -n "$vite_pids" ]]; then
        warning "Killing existing vite processes: $vite_pids"
        echo "$vite_pids" | xargs kill 2>/dev/null || true
        sleep 2
        echo "$vite_pids" | xargs kill -9 2>/dev/null || true
    fi
}

# Function to check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check if netcat is available for port checking
    if ! command -v nc &> /dev/null; then
        warning "netcat (nc) not found. Installing..."
        sudo apt-get update && sudo apt-get install -y netcat-openbsd
    fi
    
    # Check if project directory exists
    if [[ ! -d "$PROJECT_DIR" ]]; then
        error "Project directory not found: $PROJECT_DIR"
        error "Please ensure the neov3-chat-interface project is in the same directory as this script."
        exit 1
    fi
    
    # Check if package.json exists
    if [[ ! -f "$PROJECT_DIR/package.json" ]]; then
        error "package.json not found in $PROJECT_DIR"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Function to install dependencies
install_dependencies() {
    info "Checking and installing dependencies..."
    
    cd "$PROJECT_DIR"
    
    # Check if node_modules exists and is not empty
    if [[ ! -d "node_modules" ]] || [[ -z "$(ls -A node_modules 2>/dev/null)" ]]; then
        info "Installing npm dependencies..."
        npm install
        success "Dependencies installed successfully"
    else
        info "Dependencies already installed"
    fi
}

# Function to start the development server
start_dev_server() {
    local port=$1
    
    info "Starting development server on port $port..."
    
    cd "$PROJECT_DIR"
    
    # Start the server in background
    npm run dev -- --host --port "$port" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait for server to start
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if nc -z localhost "$port" 2>/dev/null; then
            success "Development server started successfully!"
            success "Local URL: http://localhost:$port"
            success "Network URL: http://$(hostname -I | awk '{print $1}'):$port"
            return 0
        fi
        
        sleep 1
        ((attempt++))
        
        # Check if process is still running
        if ! kill -0 "$pid" 2>/dev/null; then
            error "Development server failed to start"
            cat "$LOG_FILE"
            return 1
        fi
    done
    
    error "Development server failed to start within timeout"
    return 1
}

# Function to show status
show_status() {
    info "Chat UI Status:"
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Chat UI is running (PID: $pid)"
            
            # Try to find the port
            local port=$(netstat -tlnp 2>/dev/null | grep "$pid" | grep -o ':[0-9]*' | head -1 | cut -d: -f2)
            if [[ -n "$port" ]]; then
                info "Running on port: $port"
                info "Local URL: http://localhost:$port"
                info "Network URL: http://$(hostname -I | awk '{print $1}'):$port"
            fi
        else
            warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        warning "Chat UI is not running"
    fi
}

# Function to stop the server
stop_server() {
    info "Stopping chat UI server..."
    kill_existing_processes
    success "Chat UI server stopped"
}

# Function to restart the server
restart_server() {
    info "Restarting chat UI server..."
    stop_server
    sleep 2
    start_server
}

# Function to start the server
start_server() {
    info "Starting NeoV3 Enhanced AI Agent OS Chat Interface..."
    
    # Check prerequisites
    check_prerequisites
    
    # Kill existing processes
    kill_existing_processes
    
    # Install dependencies
    install_dependencies
    
    # Find available port
    local port
    port=$(find_available_port "$DEFAULT_PORT" "$MAX_PORT")
    
    if [[ -z "$port" ]]; then
        error "No available ports found between $DEFAULT_PORT and $MAX_PORT"
        exit 1
    fi
    
    if [[ "$port" != "$DEFAULT_PORT" ]]; then
        warning "Default port $DEFAULT_PORT is in use, using port $port instead"
    fi
    
    # Start development server
    if start_dev_server "$port"; then
        success "Chat UI is now running!"
        info "Press Ctrl+C to stop the server"
        
        # Wait for interrupt
        trap 'stop_server; exit 0' INT TERM
        
        # Keep script running
        while kill -0 "$(cat "$PID_FILE")" 2>/dev/null; do
            sleep 5
        done
        
        warning "Development server stopped unexpectedly"
    else
        error "Failed to start chat UI"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        info "Showing chat UI logs (last 50 lines):"
        tail -n 50 "$LOG_FILE"
    else
        warning "No log file found"
    fi
}

# Function to open in browser
open_browser() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            local port=$(netstat -tlnp 2>/dev/null | grep "$pid" | grep -o ':[0-9]*' | head -1 | cut -d: -f2)
            if [[ -n "$port" ]]; then
                local url="http://localhost:$port"
                info "Opening $url in browser..."
                
                # Try different browser commands
                if command -v xdg-open &> /dev/null; then
                    xdg-open "$url"
                elif command -v open &> /dev/null; then
                    open "$url"
                elif command -v firefox &> /dev/null; then
                    firefox "$url" &
                elif command -v google-chrome &> /dev/null; then
                    google-chrome "$url" &
                else
                    info "Please open $url in your browser"
                fi
            else
                error "Could not determine port"
            fi
        else
            error "Chat UI is not running"
        fi
    else
        error "Chat UI is not running"
    fi
}

# Function to show help
show_help() {
    echo -e "${PURPLE}NeoV3 Enhanced AI Agent OS - Chat Interface Launch Script${NC}"
    echo ""
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [command]"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo "  start     Start the chat UI (default)"
    echo "  stop      Stop the chat UI"
    echo "  restart   Restart the chat UI"
    echo "  status    Show current status"
    echo "  logs      Show recent logs"
    echo "  open      Open chat UI in browser"
    echo "  help      Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                # Start the chat UI"
    echo "  $0 start          # Start the chat UI"
    echo "  $0 stop           # Stop the chat UI"
    echo "  $0 restart        # Restart the chat UI"
    echo "  $0 status         # Check if running"
    echo "  $0 logs           # View logs"
    echo "  $0 open           # Open in browser"
    echo ""
    echo -e "${CYAN}Features:${NC}"
    echo "  • Automatic port conflict resolution"
    echo "  • Process management with PID tracking"
    echo "  • Comprehensive logging"
    echo "  • Dependency checking and installation"
    echo "  • Network and local URL display"
    echo "  • Browser integration"
    echo ""
    echo -e "${CYAN}Files:${NC}"
    echo "  Log file: $LOG_FILE"
    echo "  PID file: $PID_FILE"
    echo "  Project:  $PROJECT_DIR"
}

# Main script logic
main() {
    local command="${1:-start}"
    
    case "$command" in
        "start")
            start_server
            ;;
        "stop")
            stop_server
            ;;
        "restart")
            restart_server
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "open")
            open_browser
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Create log file if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Run main function
main "$@"

