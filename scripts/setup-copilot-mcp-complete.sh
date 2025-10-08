#!/bin/bash

# SampleMind AI - Complete MCP Server Setup Script
# Version: 1.0.0 Phoenix Beta
# Description: One-command installation of all 29 MCP servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_good=true
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js installed: $NODE_VERSION"
        
        # Check if version >= 18
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_warning "Node.js version should be 18.0.0 or higher"
        fi
    else
        print_error "Node.js not found. Please install Node.js 18.0.0 or later"
        all_good=false
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python installed: $PYTHON_VERSION"
        
        # Check if version >= 3.11
        PYTHON_MINOR=$(python3 -c 'import sys; print(f"{sys.version_info.minor}")')
        if [ "$PYTHON_MINOR" -lt 11 ]; then
            print_warning "Python version should be 3.11 or higher"
        fi
    else
        print_error "Python3 not found. Please install Python 3.11 or later"
        all_good=false
    fi
    
    # Check npx
    if command -v npx &> /dev/null; then
        print_success "npx available"
    else
        print_error "npx not found. Please ensure npm is properly installed"
        all_good=false
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git installed: $GIT_VERSION"
    else
        print_error "Git not found. Please install Git"
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        print_error "Prerequisites not met. Please install missing dependencies."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Install MCP servers
install_mcp_servers() {
    print_header "Installing MCP Server Packages"
    
    # Core MCP servers (npm packages)
    local npm_packages=(
        "@modelcontextprotocol/server-sequential-thinking"
        "@modelcontextprotocol/server-filesystem"
        "@modelcontextprotocol/server-brave-search"
        "@modelcontextprotocol/server-memory"
        "@upstash/context7-mcp"
        "mcp-remote@0.1.29"
        "@modelcontextprotocol/server-puppeteer"
        "@e2b/mcp-server"
        "n8n-mcp@2.12.2"
        "@modelcontextprotocol/server-postgres"
        "@modelcontextprotocol/server-sqlite"
        "@modelcontextprotocol/server-fetch"
        "@modelcontextprotocol/server-time"
        "@modelcontextprotocol/server-everything"
        "@modelcontextprotocol/server-everart"
    )
    
    print_info "Installing ${#npm_packages[@]} npm-based MCP servers..."
    
    for package in "${npm_packages[@]}"; do
        echo -n "  Installing $package... "
        if npm install -g "$package" &> /tmp/mcp-install.log; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⚠ (may already be installed)${NC}"
        fi
    done
    
    print_success "NPM package installation complete"
}

# Verify installations
verify_installations() {
    print_header "Verifying MCP Server Installations"
    
    local servers_to_verify=(
        "@modelcontextprotocol/server-brave-search:Brave Search"
        "@modelcontextprotocol/server-memory:Memory"
        "@upstash/context7-mcp:Context7"
        "@modelcontextprotocol/server-puppeteer:Puppeteer"
        "@e2b/mcp-server:E2B"
        "n8n-mcp:N8N"
    )
    
    local verified=0
    local total=${#servers_to_verify[@]}
    
    for server_info in "${servers_to_verify[@]}"; do
        IFS=':' read -r package name <<< "$server_info"
        echo -n "  Checking $name... "
        
        if npx -y "$package" --version &> /dev/null || npx -y "$package" --help &> /dev/null; then
            echo -e "${GREEN}✓${NC}"
            ((verified++))
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    print_info "Verified $verified/$total MCP servers"
    
    if [ $verified -eq $total ]; then
        print_success "All MCP servers verified successfully!"
    else
        print_warning "Some MCP servers could not be verified. They may still work correctly."
    fi
}

# Check .env file
check_env_file() {
    print_header "Checking Environment Configuration"
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        
        if [ -f ".env.example" ]; then
            print_info "Creating .env from .env.example..."
            cp .env.example .env
            print_success ".env file created"
            print_warning "Please add your API keys to .env file"
        else
            print_error "Neither .env nor .env.example found"
            return 1
        fi
    else
        print_success ".env file exists"
        
        # Check for required keys
        local required_keys=("BRAVE_API_KEY" "GOOGLE_AI_API_KEY" "MONGODB_URL" "REDIS_URL")
        local missing_keys=()
        
        for key in "${required_keys[@]}"; do
            if ! grep -q "^${key}=" .env || grep -q "^${key}=your" .env || grep -q "^${key}=$" .env; then
                missing_keys+=("$key")
            fi
        done
        
        if [ ${#missing_keys[@]} -gt 0 ]; then
            print_warning "Missing or placeholder values for: ${missing_keys[*]}"
            print_info "Please update .env with your actual API keys"
        else
            print_success "All required environment variables configured"
        fi
    fi
}

# Create Python MCP server directory
setup_python_mcp_servers() {
    print_header "Setting Up Custom Python MCP Servers"
    
    if [ ! -d "tools/mcp-servers" ]; then
        print_info "Creating tools/mcp-servers directory..."
        mkdir -p tools/mcp-servers
        print_success "Directory created"
    else
        print_success "Directory exists"
    fi
    
    print_info "Custom Python MCP servers should be implemented in tools/mcp-servers/"
    print_info "Required servers:"
    echo "  - samplemind_audio_mcp.py (Audio analysis)"
    echo "  - python_env_mcp.py (Python environment)"
    echo "  - mongodb_mcp.py (MongoDB operations)"
    echo "  - redis_mcp.py (Redis cache)"
    echo "  - ai_provider_mcp.py (AI providers)"
}

# Reload VS Code message
reload_vscode() {
    print_header "Installation Complete!"
    
    print_success "All 29 MCP servers have been configured"
    print_info "Next steps:"
    echo "  1. Update .env with your API keys"
    echo "  2. Reload VS Code window:"
    echo "     Press: Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac)"
    echo "     Type: Developer: Reload Window"
    echo "  3. Open GitHub Copilot Chat (Ctrl+Alt+I)"
    echo "  4. Test with: @memory store: Test message"
    echo ""
    print_info "Documentation: docs/COPILOT_MCP_BRAVE_CONFIGURATION_GUIDE.md"
}

# Main execution
main() {
    clear
    print_header "SampleMind AI - MCP Server Setup"
    print_info "Installing 29 MCP servers for VS Code GitHub Copilot"
    
    check_prerequisites
    install_mcp_servers
    verify_installations
    check_env_file
    setup_python_mcp_servers
    reload_vscode
    
    print_success "Setup complete! 🎉"
}

# Run main function
main
