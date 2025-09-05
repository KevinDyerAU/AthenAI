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

# Attempt to read only required keys from .env if creds are missing (without sourcing)
load_dotenv_if_needed() {
    if [ -n "$N8N_PASS" ] && [ -n "$N8N_USER" ] && [ -n "$N8N_URL" ]; then
        return 0
    fi

    if [ -f .env ]; then
        echo -e "${YELLOW}🔐 Loading credentials from .env...${NC}"

        # helper: extract a KEY=VALUE from .env safely (no execution)
        _dotenv_get() {
            # $1 = key
            local key="$1"
            local line
            # pick the last occurrence to respect later overrides
            line=$(grep -E "^[[:space:]]*(export[[:space:]]+)?${key}[[:space:]]*=" .env | tail -n1) || return 1
            # strip everything up to and including the first '='
            line="${line#*=}"
            # trim leading/trailing whitespace
            line=$(echo "$line" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')
            # remove trailing inline comment if present (unquoted)
            # naive: split on ' #' sequence
            line=$(echo "$line" | sed -E 's/[[:space:]]+#.*$//')
            # drop surrounding single or double quotes
            if [[ "$line" =~ ^\".*\"$ ]]; then
                line="${line:1:${#line}-2}"
            elif [[ "$line" =~ ^\'.*\'$ ]]; then
                line="${line:1:${#line}-2}"
            fi
            echo "$line"
        }

        # only pull required keys
        if [ -z "$N8N_USER" ]; then
            val=$(_dotenv_get "N8N_BASIC_AUTH_USER"); [ -n "$val" ] && N8N_USER="$val"
        fi
        if [ -z "$N8N_PASS" ]; then
            val=$(_dotenv_get "N8N_BASIC_AUTH_PASSWORD"); [ -n "$val" ] && N8N_PASS="$val"
        fi
        if [ -z "$N8N_URL" ]; then
            val=$(_dotenv_get "N8N_URL"); if [ -z "$val" ]; then val=$(_dotenv_get "N8N_BASE_URL"); fi; [ -n "$val" ] && N8N_URL="$val"
        fi
        if [ -z "$N8N_API_KEY" ]; then
            val=$(_dotenv_get "N8N_API_KEY"); [ -n "$val" ] && N8N_API_KEY="$val"
        fi
    else
        echo -e "${YELLOW}⚠️  .env not found; relying on current environment for credentials${NC}"
    fi
}

# Validate required environment variables
load_dotenv_if_needed
if [ -z "$N8N_PASS" ]; then
    echo -e "${RED}❌ N8N_BASIC_AUTH_PASSWORD is required (set in environment or .env)${NC}"
    exit 1
fi
echo -e "${BLUE}👤 Using n8n credentials for user '${YELLOW}${N8N_USER}${BLUE}' (password: ****)${NC}"
echo -e "${BLUE}🌐 Target n8n URL: ${YELLOW}${N8N_URL}${NC}"
if [ -n "$N8N_API_KEY" ]; then
    echo -e "${BLUE}🔑 API key: ${YELLOW}present${NC}"
else
    echo -e "${YELLOW}⚠️  N8N_API_KEY not set. This instance may require an API key for REST calls; imports could fail with 401.${NC}"
fi

# Ensure required tools are installed
check_dependencies() {
    local missing=0
    if ! command -v curl >/dev/null 2>&1; then
        echo -e "${RED}❌ Missing dependency: curl${NC}"
        missing=1
    fi
    if ! command -v jq >/dev/null 2>&1; then
        echo -e "${RED}❌ Missing dependency: jq${NC}"
        missing=1
    fi
    if [ $missing -eq 1 ]; then
        echo -e "${YELLOW}➡️  Install on Ubuntu/Debian: ${NC}sudo apt-get update && sudo apt-get install -y curl jq"
        echo -e "${YELLOW}➡️  Install on macOS (Homebrew): ${NC}brew install curl jq"
        exit 1
    fi
}

# Wrapper to safely import a workflow without causing the script to exit on errors
import_workflow_safe() {
    local wf_file="$1"
    set +e
    import_workflow "$wf_file"
    local rc=$?
    set -e
    return $rc
}

# Function to wait for n8n to be ready
wait_for_n8n() {
    echo -e "${YELLOW}⏳ Waiting for n8n service to be ready...${NC}"
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        # Probe both endpoints; consider ready if either returns 200
        http_code_healthz=$(curl -s -o /dev/null -w "%{http_code}" -u "$N8N_USER:$N8N_PASS" "$N8N_URL/healthz" || echo "000")
        http_code_rest=$(curl -s -o /dev/null -w "%{http_code}" -u "$N8N_USER:$N8N_PASS" "$N8N_URL/rest/health" || echo "000")

        if [ "$http_code_healthz" -eq 200 ] || [ "$http_code_rest" -eq 200 ]; then
            echo -e "${GREEN}✅ n8n is ready and accessible${NC}"
            return 0
        fi

        echo "Waiting for n8n... (attempt $((retries + 1))/$MAX_RETRIES), /healthz: $http_code_healthz, /rest/health: $http_code_rest"
        if [ "$http_code_healthz" -eq 401 ] || [ "$http_code_healthz" -eq 403 ] || [ "$http_code_rest" -eq 401 ] || [ "$http_code_rest" -eq 403 ]; then
            echo -e "${YELLOW}ℹ️  Auth not accepted yet. Ensure N8N_BASIC_AUTH_USER/PASSWORD are correct and n8n user management is initialized.${NC}"
        fi

        sleep $RETRY_DELAY
        ((retries+=1))
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
    
    # Validate JSON syntax and surface jq error details
    if ! err_output=$(jq empty "$workflow_file" 2>&1 >/dev/null); then
        echo -e "${RED}❌ Invalid JSON syntax in: $workflow_name${NC}"
        echo -e "${YELLOW}↳ jq error: ${NC}$err_output"
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
    
    echo -e "${BLUE}📥 Importing workflow: ${YELLOW}${workflow_name}${NC}"
    
    # Validate workflow before import
    if ! validate_workflow "$workflow_file"; then
        return 1
    fi
    
    # Prepare workflow data: unwrap common wrappers and strip unsupported fields
    # - Some exports store as {"workflow": {...}}; unwrap to inner object
    # - Remove fields not accepted on create (e.g., id, meta, versionId, createdAt, updatedAt, owner)
    # - Allow only known schema keys to avoid "additional properties" errors
    local workflow_data=$(jq -c '
      (.workflow // .) 
      | with_entries(select(.key | IN("name","nodes","connections","active","settings","staticData","tags","pinData")))
      | .connections = (.connections // {})
    ' "$workflow_file")
    
    # Import workflow via n8n API (API key required on secured instances)
    if [ -z "$N8N_API_KEY" ]; then
        echo -e "${RED}❌ No N8N_API_KEY provided; cannot import on instances requiring API key${NC}"
        return 1
    fi
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        "$N8N_URL/api/v1/workflows" \
        -d "$workflow_data" 2>/dev/null)
    
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
    
    if [ -z "$N8N_API_KEY" ]; then
        echo -e "${YELLOW}ℹ️  Skipping activation; N8N_API_KEY not set${NC}"
        return 0
    fi
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X PATCH \
        -H "Content-Type: application/json" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        "$N8N_URL/api/v1/workflows/$workflow_id" \
        -d '{"active":true}' 2>/dev/null)
    
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
    if [ -n "$N8N_API_KEY" ]; then
        local response=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/api/v1/workflows" 2>/dev/null)
    else
        local response=$(curl -s -u "$N8N_USER:$N8N_PASS" "$N8N_URL/api/v1/workflows" 2>/dev/null)
    fi
    
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
count_workflows() {
    local count=0
    if [ -d "$WORKFLOW_DIR" ]; then
        count=$(find "$WORKFLOW_DIR" -type f -name '*.json' | wc -l | tr -d ' ')
    fi
    echo "$count"
}

main() {
    # Verify required tools are available
    check_dependencies

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
    
    # Pre-count total workflows for progress display
    local total_to_process
    total_to_process=$(count_workflows)
    echo -e "${BLUE}🧮 Total workflows detected: ${YELLOW}${total_to_process}${NC}"

    # Initialize counters
    local total_workflows=0
    local successful_imports=0
    local failed_imports=0
    local processed=0
    
    # Import workflows recursively from all subfolders
    echo -e "${BLUE}🔍 Processing workflows recursively under: ${YELLOW}$WORKFLOW_DIR${NC}"
    files=()
    while IFS= read -r -d '' wf; do
        files+=("$wf")
    done < <(find "$WORKFLOW_DIR" -type f -name '*.json' -print0)

    echo -e "${BLUE}📄 Files discovered: ${YELLOW}${#files[@]}${NC}"
    if [ ${#files[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No workflow JSON files found under $WORKFLOW_DIR${NC}"
    fi

    for workflow_file in "${files[@]}"; do
        ((total_workflows+=1))
        ((processed+=1))
        echo -e "${YELLOW}➡️  [$processed/$total_to_process] ${workflow_file}${NC}"
        if import_workflow_safe "$workflow_file"; then
            ((successful_imports+=1))
            echo -e "${GREEN}   ✔ Imported successfully${NC}"
        else
            ((failed_imports+=1))
            echo -e "${RED}   ✖ Import failed (continuing)${NC}"
        fi
        sleep 2  # Rate limiting
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

