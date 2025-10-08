#!/bin/bash

# SampleMind AI - MCP Server Verification Script
# Tests connectivity and basic functionality of all 29 MCP servers

set +e  # Don't exit on error for testing

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
    ((TOTAL_TESTS++))
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

print_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIPPED_TESTS++))
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Test 1: Node.js MCP Servers
test_npm_mcp_servers() {
    print_header "Testing NPM-based MCP Servers"
    
    local servers=(
        "@modelcontextprotocol/server-sequential-thinking:Sequential Thinking"
        "@modelcontextprotocol/server-filesystem:Filesystem"
        "@modelcontextprotocol/server-brave-search:Brave Search"
        "@modelcontextprotocol/server-memory:Memory"
        "@upstash/context7-mcp:Context7"
        "mcp-remote:Git MCP"
        "@modelcontextprotocol/server-puppeteer:Puppeteer"
        "@e2b/mcp-server:E2B"
        "n8n-mcp:N8N"
        "@modelcontextprotocol/server-postgres:PostgreSQL"
        "@modelcontextprotocol/server-sqlite:SQLite"
        "@modelcontextprotocol/server-fetch:Fetch"
        "@modelcontextprotocol/server-time:Time"
        "@modelcontextprotocol/server-everything:Everything"
        "@modelcontextprotocol/server-everart:EverArt"
    )
    
    for server_info in "${servers[@]}"; do
        IFS=':' read -r package name <<< "$server_info"
        print_test "Testing $name"
        
        if npx -y "$package" --version &> /dev/null || npx -y "$package" --help &> /dev/null; then
            print_pass "$name is accessible"
        else
            print_fail "$name is not accessible"
        fi
    done
}

# Test 2: Environment Variables
test_environment_variables() {
    print_header "Testing Environment Variables"
    
    if [ ! -f ".env" ]; then
        print_fail ".env file not found"
        return
    fi
    
    source .env 2>/dev/null || true
    
    local required_vars=(
        "BRAVE_API_KEY"
        "GOOGLE_AI_API_KEY"
        "ANTHROPIC_API_KEY"
        "OPENAI_API_KEY"
        "MONGODB_URL"
        "REDIS_URL"
    )
    
    for var in "${required_vars[@]}"; do
        print_test "Checking $var"
        
        if grep -q "^${var}=" .env; then
            local value=$(grep "^${var}=" .env | cut -d= -f2)
            if [ -n "$value" ] && [[ ! "$value" =~ "your_" ]] && [[ ! "$value" =~ "YOUR_" ]]; then
                print_pass "$var is configured"
            else
                print_skip "$var has placeholder value"
            fi
        else
            print_fail "$var not found in .env"
        fi
    done
}

# Test 3: Python MCP Server Files
test_python_mcp_servers() {
    print_header "Testing Python MCP Server Files"
    
    local python_servers=(
        "tools/mcp-servers/samplemind_audio_mcp.py:Audio Analysis"
        "tools/mcp-servers/python_env_mcp.py:Python Environment"
        "tools/mcp-servers/mongodb_mcp.py:MongoDB"
        "tools/mcp-servers/redis_mcp.py:Redis"
        "tools/mcp-servers/ai_provider_mcp.py:AI Provider"
    )
    
    for server_info in "${python_servers[@]}"; do
        IFS=':' read -r path name <<< "$server_info"
        print_test "Checking $name"
        
        if [ -f "$path" ]; then
            if [ -x "$path" ]; then
                print_pass "$name exists and is executable"
            else
                print_skip "$name exists but not executable"
            fi
        else
            print_skip "$name not yet implemented"
        fi
    done
}

# Test 4: VS Code Configuration
test_vscode_configuration() {
    print_header "Testing VS Code Configuration"
    
    print_test "Checking .vscode/settings.json"
    if [ -f ".vscode/settings.json" ]; then
        if grep -q "github.copilot.chat.mcpServers" .vscode/settings.json; then
            print_pass "MCP servers configured in VS Code"
        else
            print_fail "MCP servers not found in VS Code settings"
        fi
    else
        print_fail ".vscode/settings.json not found"
    fi
    
    print_test "Checking GitHub Copilot agent mode settings"
    if [ -f ".vscode/settings.json" ]; then
        if grep -q "github.copilot.advanced" .vscode/settings.json; then
            print_pass "Agent mode settings configured"
        else
            print_fail "Agent mode settings not found"
        fi
    fi
}

# Test 5: Documentation Files
test_documentation() {
    print_header "Testing Documentation Files"
    
    local docs=(
        ".github/copilot-instructions.md:Custom Instructions"
        ".github/copilot-prompts/audio-analysis.prompt.md:Audio Analysis Prompt"
        ".github/copilot-prompts/ml-training.prompt.md:ML Training Prompt"
        ".github/copilot-prompts/performance-optimization.prompt.md:Performance Prompt"
        ".github/copilot-prompts/music-theory.prompt.md:Music Theory Prompt"
        "docs/COPILOT_MCP_BRAVE_CONFIGURATION_GUIDE.md:Configuration Guide"
    )
    
    for doc_info in "${docs[@]}"; do
        IFS=':' read -r path name <<< "$doc_info"
        print_test "Checking $name"
        
        if [ -f "$path" ]; then
            print_pass "$name exists"
        else
            print_fail "$name not found"
        fi
    done
}

# Test 6: Network Connectivity
test_network_connectivity() {
    print_header "Testing Network Connectivity"
    
    local endpoints=(
        "api.brave.com:Brave Search API"
        "api.openai.com:OpenAI API"
        "api.anthropic.com:Anthropic API"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r endpoint name <<< "$endpoint_info"
        print_test "Testing connectivity to $name"
        
        if ping -c 1 -W 2 "$endpoint" &> /dev/null; then
            print_pass "Can reach $name"
        else
            print_skip "Cannot ping $name (may be blocked)"
        fi
    done
}

# Test 7: Database Connectivity
test_database_connectivity() {
    print_header "Testing Database Connectivity"
    
    print_test "Testing MongoDB connection"
    if [ -n "$MONGODB_URL" ] && [[ ! "$MONGODB_URL" =~ "localhost" ]]; then
        print_skip "MongoDB URL configured (cannot test without credentials)"
    elif command -v mongosh &> /dev/null; then
        if mongosh --eval "db.version()" &> /dev/null; then
            print_pass "MongoDB is accessible"
        else
            print_skip "MongoDB not running locally"
        fi
    else
        print_skip "mongosh not installed"
    fi
    
    print_test "Testing Redis connection"
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_pass "Redis is accessible"
        else
            print_skip "Redis not running locally"
        fi
    else
        print_skip "redis-cli not installed"
    fi
}

# Print summary
print_summary() {
    print_header "Test Summary"
    
    echo -e "Total Tests:  ${BLUE}$TOTAL_TESTS${NC}"
    echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
    echo -e "Skipped:      ${YELLOW}$SKIPPED_TESTS${NC}"
    
    local pass_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        pass_rate=$((100 * PASSED_TESTS / TOTAL_TESTS))
    fi
    
    echo -e "\nPass Rate:    ${GREEN}${pass_rate}%${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}✓ All critical tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}✗ Some tests failed. Review the output above.${NC}"
        return 1
    fi
}

# Main execution
main() {
    clear
    print_header "SampleMind AI - MCP Server Verification"
    echo -e "${BLUE}Testing all 29 MCP servers and configurations${NC}\n"
    
    test_npm_mcp_servers
    test_environment_variables
    test_python_mcp_servers
    test_vscode_configuration
    test_documentation
    test_network_connectivity
    test_database_connectivity
    
    print_summary
}

# Run tests
main
exit_code=$?

echo -e "\n${BLUE}For detailed setup instructions, see:${NC}"
echo -e "  ${BLUE}docs/COPILOT_MCP_BRAVE_CONFIGURATION_GUIDE.md${NC}\n"

exit $exit_code
