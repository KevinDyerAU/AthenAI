#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Loading n8n workflows at deploy time...${NC}"

# Configuration
N8N_USER="${N8N_BASIC_AUTH_USER:-admin}"
N8N_PASS="${N8N_BASIC_AUTH_PASSWORD}"
N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOW_DIR="${WORKFLOW_DIR:-./workflows/enhanced}"
MAX_RETRIES=30
RETRY_DELAY=10

# Validate required environment variables
if [ -z "$N8N_PASS" ]; then
    echo -e "${RED}❌ N8N_BASIC_AUTH_PASSWORD environment variable is required${NC}"
    exit 1
fi

# Function to wait for n8n to be ready
wait_for_n8n() {
    echo -e "${YELLOW}⏳ Waiting for n8n service to be ready...${NC}"
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s -u "$N8N_USER:$N8N_PASS" "$N8N_URL/api/v1/workflows" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ n8n is ready and accessible${NC}"
            return 0
        fi
        
        echo "Waiting for n8n... (attempt $((retries + 1))/$MAX_RETRIES)"
        sleep $RETRY_DELAY
        ((retries++))
    done
    
    echo -e "${RED}❌ n8n failed to become ready after $MAX_RETRIES attempts${NC}"
    return 1
}

# Function to validate workflow JSON
validate_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    
    # Check if file exists and is readable
    if [ ! -r "$workflow_file" ]; then
        echo -e "${RED}❌ Cannot read workflow file: $workflow_file${NC}"
        return 1
    fi
    
    # Validate JSON syntax
    if ! jq empty "$workflow_file" 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON syntax in: $workflow_name${NC}"
        return 1
    fi
    
    # Check required fields
    local required_fields=("name" "nodes")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$workflow_file" >/dev/null 2>&1; then
            echo -e "${RED}❌ Missing required field '$field' in: $workflow_name${NC}"
            return 1
        fi
    done
    
    # Check for empty nodes array
    local node_count=$(jq '.nodes | length' "$workflow_file" 2>/dev/null || echo "0")
    if [ "$node_count" -eq 0 ]; then
        echo -e "${RED}❌ Workflow has no nodes: $workflow_name${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Workflow validation passed: $workflow_name${NC}"
    return 0
}

# Function to import workflow
import_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    
    echo -e "${BLUE}📥 Importing workflow: $workflow_name${NC}"
    
    # Validate workflow before import
    if ! validate_workflow "$workflow_file"; then
        return 1
    fi
    
    # Prepare workflow data
    local workflow_data=$(jq -c . "$workflow_file")
    
    # Import workflow via n8n API
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -u "$N8N_USER:$N8N_PASS" \
        -d "$workflow_data" \
        "$N8N_URL/api/v1/workflows" 2>/dev/null)
    
    local http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    local body=$(echo "$response" | sed -e 's/HTTPSTATUS\:.*//g')
    
    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        local workflow_id=$(echo "$body" | jq -r '.id // empty' 2>/dev/null)
        echo -e "${GREEN}✅ Successfully imported: $workflow_name (ID: $workflow_id)${NC}"
        
        # Try to activate the workflow if it has a trigger
        if jq -e '.nodes[] | select(.type | contains("trigger") or contains("webhook"))' "$workflow_file" >/dev/null 2>&1; then
            activate_workflow "$workflow_id" "$workflow_name"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Failed to import: $workflow_name (HTTP: $http_code)${NC}"
        if [ -n "$body" ]; then
            echo -e "${RED}   Error details: $(echo "$body" | jq -r '.message // .error // .' 2>/dev/null || echo "$body")${NC}"
        fi
        return 1
    fi
}

# Function to activate workflow
activate_workflow() {
    local workflow_id="$1"
    local workflow_name="$2"
    
    if [ -z "$workflow_id" ] || [ "$workflow_id" = "null" ]; then
        echo -e "${YELLOW}⚠️  Cannot activate workflow without valid ID: $workflow_name${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🚀 Activating workflow: $workflow_name${NC}"
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X PATCH \
        -H "Content-Type: application/json" \
        -u "$N8N_USER:$N8N_PASS" \
        -d '{"active": true}' \
        "$N8N_URL/api/v1/workflows/$workflow_id" 2>/dev/null)
    
    local http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Successfully activated: $workflow_name${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Failed to activate: $workflow_name (HTTP: $http_code)${NC}"
        return 1
    fi
}

# Function to get workflow statistics
get_workflow_stats() {
    echo -e "${BLUE}📊 Gathering workflow statistics...${NC}"
    
    local response=$(curl -s -u "$N8N_USER:$N8N_PASS" "$N8N_URL/api/v1/workflows" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        local total_workflows=$(echo "$response" | jq '.data | length' 2>/dev/null || echo "0")
        local active_workflows=$(echo "$response" | jq '[.data[] | select(.active == true)] | length' 2>/dev/null || echo "0")
        
        echo -e "${GREEN}📈 Workflow Statistics:${NC}"
        echo -e "   - Total workflows: $total_workflows"
        echo -e "   - Active workflows: $active_workflows"
        echo -e "   - Inactive workflows: $((total_workflows - active_workflows))"
    else
        echo -e "${YELLOW}⚠️  Could not retrieve workflow statistics${NC}"
    fi
}

# Main execution
main() {
    # Wait for n8n to be ready
    if ! wait_for_n8n; then
        exit 1
    fi
    
    # Check if workflow directory exists
    if [ ! -d "$WORKFLOW_DIR" ]; then
        echo -e "${RED}❌ Workflow directory not found: $WORKFLOW_DIR${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📁 Workflow directory: $WORKFLOW_DIR${NC}"
    
    # Initialize counters
    local total_workflows=0
    local successful_imports=0
    local failed_imports=0
    
    # Import workflows from main directory
    echo -e "${BLUE}🔍 Processing workflows in main directory...${NC}"
    for workflow_file in "$WORKFLOW_DIR"/*.json; do
        if [ -f "$workflow_file" ]; then
            ((total_workflows++))
            if import_workflow "$workflow_file"; then
                ((successful_imports++))
            else
                ((failed_imports++))
            fi
            sleep 2  # Rate limiting
        fi
    done
    
    # Import workflows from subdirectories
    echo -e "${BLUE}🔍 Processing workflows in subdirectories...${NC}"
    for tool_dir in "$WORKFLOW_DIR"/*/; do
        if [ -d "$tool_dir" ]; then
            local tool_name=$(basename "$tool_dir")
            echo -e "${BLUE}📂 Processing tool directory: $tool_name${NC}"
            
            for workflow_file in "$tool_dir"/*.json; do
                if [ -f "$workflow_file" ]; then
                    ((total_workflows++))
                    if import_workflow "$workflow_file"; then
                        ((successful_imports++))
                    else
                        ((failed_imports++))
                    fi
                    sleep 2  # Rate limiting
                fi
            done
        fi
    done
    
    # Display summary
    echo -e "${BLUE}📊 Workflow loading summary:${NC}"
    echo -e "   - Total workflows processed: $total_workflows"
    echo -e "   - Successful imports: ${GREEN}$successful_imports${NC}"
    echo -e "   - Failed imports: ${RED}$failed_imports${NC}"
    
    # Get final statistics
    sleep 5  # Wait for workflows to be fully processed
    get_workflow_stats
    
    # Determine exit code
    if [ $failed_imports -eq 0 ]; then
        echo -e "${GREEN}🎉 All workflows loaded successfully!${NC}"
        exit 0
    elif [ $successful_imports -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some workflows failed to load, but $successful_imports were successful.${NC}"
        exit 0  # Partial success is acceptable
    else
        echo -e "${RED}❌ All workflow imports failed. Check n8n logs and configuration.${NC}"
        exit 1
    fi
}

# Handle script interruption
cleanup() {
    echo -e "\n${YELLOW}🛑 Workflow loading interrupted${NC}"
    exit 1
}

trap cleanup INT TERM

# Run main function
main "$@"

