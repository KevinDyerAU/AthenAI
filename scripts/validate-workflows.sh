#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Validating n8n workflows...${NC}"

# Configuration
WORKFLOW_DIR="${WORKFLOW_DIR:-./workflows/enhanced}"
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0
TOTAL_WORKFLOWS=0

# Required n8n version for Think Tool support
MIN_N8N_VERSION="1.60.0"

# Function to compare versions
version_compare() {
    local version1="$1"
    local version2="$2"
    
    if [ "$version1" = "$version2" ]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($version1) ver2=($version2)
    
    # Fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Function to validate individual workflow
validate_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    local errors=0
    local warnings=0
    
    echo -e "${BLUE}🔍 Validating: $workflow_name${NC}"
    
    # Check if file exists and is readable
    if [ ! -r "$workflow_file" ]; then
        echo -e "${RED}❌ Cannot read workflow file: $workflow_file${NC}"
        return 1
    fi
    
    # Check file size (empty files)
    if [ ! -s "$workflow_file" ]; then
        echo -e "${RED}❌ Empty workflow file: $workflow_name${NC}"
        return 1
    fi
    
    # Validate JSON syntax
    if ! jq empty "$workflow_file" 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON syntax in: $workflow_name${NC}"
        ((errors++))
    fi
    
    # Check required top-level fields
    local required_fields=("name" "nodes")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$workflow_file" >/dev/null 2>&1; then
            echo -e "${RED}❌ Missing required field '$field' in: $workflow_name${NC}"
            ((errors++))
        fi
    done
    
    # Check workflow name consistency
    local json_name=$(jq -r '.name // empty' "$workflow_file" 2>/dev/null)
    if [ -n "$json_name" ] && [ "$json_name" != "$workflow_name" ]; then
        echo -e "${YELLOW}⚠️  Workflow name mismatch: file='$workflow_name', json='$json_name'${NC}"
        ((warnings++))
    fi
    
    # Check for empty nodes array
    local node_count=$(jq '.nodes | length' "$workflow_file" 2>/dev/null || echo "0")
    if [ "$node_count" -eq 0 ]; then
        echo -e "${RED}❌ Workflow has no nodes: $workflow_name${NC}"
        ((errors++))
    else
        echo -e "${GREEN}   ✓ Node count: $node_count${NC}"
    fi
    
    # Validate individual nodes
    local node_errors=0
    local node_index=0
    
    while [ $node_index -lt $node_count ]; do
        local node=$(jq ".nodes[$node_index]" "$workflow_file" 2>/dev/null)
        
        # Check required node fields
        local node_required_fields=("id" "name" "type" "position")
        for node_field in "${node_required_fields[@]}"; do
            if ! echo "$node" | jq -e ".$node_field" >/dev/null 2>&1; then
                echo -e "${RED}❌ Node $node_index missing required field '$node_field' in: $workflow_name${NC}"
                ((node_errors++))
            fi
        done
        
        # Check node type format
        local node_type=$(echo "$node" | jq -r '.type // empty' 2>/dev/null)
        if [ -n "$node_type" ]; then
            if [[ ! "$node_type" =~ ^[a-zA-Z0-9@/_.-]+$ ]]; then
                echo -e "${RED}❌ Invalid node type format '$node_type' in: $workflow_name${NC}"
                ((node_errors++))
            fi
        fi
        
        # Check for duplicate node IDs
        local node_id=$(echo "$node" | jq -r '.id // empty' 2>/dev/null)
        if [ -n "$node_id" ]; then
            local id_count=$(jq "[.nodes[] | select(.id == \"$node_id\")] | length" "$workflow_file" 2>/dev/null || echo "0")
            if [ "$id_count" -gt 1 ]; then
                echo -e "${RED}❌ Duplicate node ID '$node_id' in: $workflow_name${NC}"
                ((node_errors++))
            fi
        fi
        
        ((node_index++))
    done
    
    errors=$((errors + node_errors))
    
    # Check connections structure
    if jq -e '.connections' "$workflow_file" >/dev/null 2>&1; then
        local connection_count=$(jq '.connections | keys | length' "$workflow_file" 2>/dev/null || echo "0")
        echo -e "${GREEN}   ✓ Connection groups: $connection_count${NC}"
        
        # Validate connection references
        local connection_errors=0
        local node_ids=$(jq -r '.nodes[].id' "$workflow_file" 2>/dev/null)
        
        for connection_source in $(jq -r '.connections | keys[]' "$workflow_file" 2>/dev/null); do
            if ! echo "$node_ids" | grep -q "^$connection_source$"; then
                echo -e "${RED}❌ Connection references non-existent node: $connection_source in $workflow_name${NC}"
                ((connection_errors++))
            fi
        done
        
        errors=$((errors + connection_errors))
    else
        echo -e "${YELLOW}⚠️  No connections defined in: $workflow_name${NC}"
        ((warnings++))
    fi
    
    # Check for AI Agent workflows and Think Tool integration
    local has_ai_agent=$(jq -e '.nodes[] | select(.type | contains("langchain.agent"))' "$workflow_file" >/dev/null 2>&1 && echo "true" || echo "false")
    local has_think_tool=$(jq -e '.nodes[] | select(.type | contains("toolThink"))' "$workflow_file" >/dev/null 2>&1 && echo "true" || echo "false")
    
    if [ "$has_ai_agent" = "true" ] && [ "$has_think_tool" = "false" ]; then
        echo -e "${YELLOW}⚠️  AI Agent workflow without Think Tool integration: $workflow_name${NC}"
        echo -e "${YELLOW}     Consider adding Think Tool for better reasoning capabilities${NC}"
        ((warnings++))
    fi
    
    # Check for webhook/trigger nodes
    local has_trigger=$(jq -e '.nodes[] | select(.type | contains("trigger") or contains("webhook"))' "$workflow_file" >/dev/null 2>&1 && echo "true" || echo "false")
    if [ "$has_trigger" = "true" ]; then
        echo -e "${GREEN}   ✓ Has trigger/webhook node${NC}"
    else
        echo -e "${YELLOW}⚠️  No trigger/webhook node found in: $workflow_name${NC}"
        echo -e "${YELLOW}     Workflow may need manual execution${NC}"
        ((warnings++))
    fi
    
    # Check for credentials references
    local credential_refs=$(jq -r '.nodes[].credentials // empty | keys[]' "$workflow_file" 2>/dev/null | sort -u)
    if [ -n "$credential_refs" ]; then
        echo -e "${BLUE}   ℹ️  Required credentials: $(echo "$credential_refs" | tr '\n' ' ')${NC}"
    fi
    
    # Check workflow settings
    if jq -e '.settings' "$workflow_file" >/dev/null 2>&1; then
        local execution_order=$(jq -r '.settings.executionOrder // empty' "$workflow_file" 2>/dev/null)
        if [ -n "$execution_order" ]; then
            echo -e "${GREEN}   ✓ Execution order: $execution_order${NC}"
        fi
    fi
    
    # Summary for this workflow
    if [ $errors -eq 0 ]; then
        if [ $warnings -eq 0 ]; then
            echo -e "${GREEN}✅ Validation passed: $workflow_name${NC}"
        else
            echo -e "${YELLOW}⚠️  Validation passed with $warnings warning(s): $workflow_name${NC}"
        fi
    else
        echo -e "${RED}❌ Validation failed with $errors error(s): $workflow_name${NC}"
    fi
    
    echo "" # Empty line for readability
    
    # Update global counters
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + errors))
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + warnings))
    
    return $errors
}

# Function to validate directory structure
validate_directory_structure() {
    echo -e "${BLUE}📁 Validating directory structure...${NC}"
    
    if [ ! -d "$WORKFLOW_DIR" ]; then
        echo -e "${RED}❌ Workflow directory not found: $WORKFLOW_DIR${NC}"
        return 1
    fi
    
    # Check for expected subdirectories
    local expected_dirs=("analysis-tools" "communication-tools" "creative-tools" "development-tools" "execution-tools" "planning-tools" "qa-tools" "research-tools")
    local missing_dirs=0
    
    for dir in "${expected_dirs[@]}"; do
        if [ ! -d "$WORKFLOW_DIR/$dir" ]; then
            echo -e "${YELLOW}⚠️  Expected directory not found: $dir${NC}"
            ((missing_dirs++))
        else
            local workflow_count=$(find "$WORKFLOW_DIR/$dir" -name "*.json" | wc -l)
            echo -e "${GREEN}   ✓ $dir ($workflow_count workflows)${NC}"
        fi
    done
    
    if [ $missing_dirs -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $missing_dirs expected directories are missing${NC}"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + missing_dirs))
    fi
    
    return 0
}

# Function to check for common issues
check_common_issues() {
    echo -e "${BLUE}🔍 Checking for common issues...${NC}"
    
    # Check for workflows with similar names
    local workflow_names=$(find "$WORKFLOW_DIR" -name "*.json" -exec basename {} .json \; | sort)
    local duplicate_names=$(echo "$workflow_names" | uniq -d)
    
    if [ -n "$duplicate_names" ]; then
        echo -e "${YELLOW}⚠️  Potential duplicate workflow names found:${NC}"
        echo "$duplicate_names" | while read -r name; do
            echo -e "${YELLOW}     - $name${NC}"
        done
        ((VALIDATION_WARNINGS++))
    fi
    
    # Check for very large workflows (potential performance issues)
    find "$WORKFLOW_DIR" -name "*.json" | while read -r workflow_file; do
        local file_size=$(stat -f%z "$workflow_file" 2>/dev/null || stat -c%s "$workflow_file" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 100000 ]; then  # 100KB threshold
            local workflow_name=$(basename "$workflow_file" .json)
            echo -e "${YELLOW}⚠️  Large workflow file detected: $workflow_name ($(($file_size / 1024))KB)${NC}"
            echo -e "${YELLOW}     Consider breaking into smaller workflows for better performance${NC}"
        fi
    done
}

# Main validation function
main() {
    echo -e "${BLUE}🏁 Starting workflow validation...${NC}"
    echo -e "${BLUE}📁 Workflow directory: $WORKFLOW_DIR${NC}"
    echo ""
    
    # Validate directory structure
    if ! validate_directory_structure; then
        exit 1
    fi
    
    echo ""
    
    # Validate all workflows in main directory
    echo -e "${BLUE}🔍 Validating workflows in main directory...${NC}"
    for workflow_file in "$WORKFLOW_DIR"/*.json; do
        if [ -f "$workflow_file" ]; then
            ((TOTAL_WORKFLOWS++))
            validate_workflow "$workflow_file"
        fi
    done
    
    # Validate workflows in subdirectories
    echo -e "${BLUE}🔍 Validating workflows in subdirectories...${NC}"
    for tool_dir in "$WORKFLOW_DIR"/*/; do
        if [ -d "$tool_dir" ]; then
            local tool_name=$(basename "$tool_dir")
            echo -e "${BLUE}📂 Processing tool directory: $tool_name${NC}"
            
            for workflow_file in "$tool_dir"/*.json; do
                if [ -f "$workflow_file" ]; then
                    ((TOTAL_WORKFLOWS++))
                    validate_workflow "$workflow_file"
                fi
            done
        fi
    done
    
    # Check for common issues
    echo -e "${BLUE}🔍 Running additional checks...${NC}"
    check_common_issues
    
    echo ""
    
    # Display final summary
    echo -e "${BLUE}📊 Validation Summary:${NC}"
    echo -e "   - Total workflows validated: $TOTAL_WORKFLOWS"
    echo -e "   - Validation errors: ${RED}$VALIDATION_ERRORS${NC}"
    echo -e "   - Validation warnings: ${YELLOW}$VALIDATION_WARNINGS${NC}"
    
    if [ $VALIDATION_ERRORS -eq 0 ]; then
        if [ $VALIDATION_WARNINGS -eq 0 ]; then
            echo -e "${GREEN}🎉 All workflows passed validation with no issues!${NC}"
        else
            echo -e "${YELLOW}⚠️  All workflows passed validation, but with $VALIDATION_WARNINGS warning(s).${NC}"
            echo -e "${YELLOW}    Consider addressing warnings for optimal performance.${NC}"
        fi
        exit 0
    else
        echo -e "${RED}❌ Workflow validation failed with $VALIDATION_ERRORS error(s).${NC}"
        echo -e "${RED}   Please fix all errors before deployment.${NC}"
        exit 1
    fi
}

# Handle script interruption
cleanup() {
    echo -e "\n${YELLOW}🛑 Workflow validation interrupted${NC}"
    exit 1
}

trap cleanup INT TERM

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq is required but not installed. Please install jq to run this script.${NC}"
    exit 1
fi

# Run main function
main "$@"

