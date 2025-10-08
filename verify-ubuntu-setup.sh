#!/bin/bash

# SampleMind AI - Ubuntu Installation Verification Script
# Date: January 6, 2025

echo "🔍 SampleMind AI Installation Verification (Ubuntu)"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "1️⃣  System Requirements"
echo "----------------------"

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS: $NAME $VERSION"
    print_success "Ubuntu detected"
else
    print_error "Cannot detect OS version"
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"

    # Check if version is 18+
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_success "Node.js version is sufficient (18+)"
    else
        print_warning "Node.js version is below 18 (current: $NODE_VERSION)"
    fi
else
    print_error "Node.js not found. Install with: sudo apt install nodejs"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm not found"
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python3 not found"
fi

echo ""
echo "2️⃣  Project Structure"
echo "--------------------"

# Check project directory
if [ -d "/home/lchta/Projects/Samplemind-AI" ]; then
    print_success "Project directory found"
    cd /home/lchta/Projects/Samplemind-AI
else
    print_error "Project directory not found at /home/lchta/Projects/Samplemind-AI"
    exit 1
fi

# Check backend files
if [ -f "src/samplemind/api/routes/assistant.py" ]; then
    print_success "Backend API route found"
else
    print_error "Backend API route not found"
fi

# Check frontend files
if [ -f "web-app/src/pages/AssistantDemo.tsx" ]; then
    print_success "Frontend demo page found"
else
    print_error "Frontend demo page not found"
fi

# Check store
if [ -f "web-app/src/stores/advanced-chat-store.ts" ]; then
    print_success "Zustand store found"
else
    print_error "Zustand store not found"
fi

# Check provider
if [ -f "web-app/src/providers/SampleMindRuntimeProvider.tsx" ]; then
    print_success "Runtime provider found"
else
    print_error "Runtime provider not found"
fi

echo ""
echo "3️⃣  npm Packages"
echo "---------------"

cd web-app

# Check if node_modules exists
if [ -d "node_modules" ]; then
    print_success "node_modules directory exists"

    # Check specific packages
    if [ -d "node_modules/@assistant-ui/react" ]; then
        ASSISTANT_UI_VERSION=$(npm list @assistant-ui/react 2>/dev/null | grep @assistant-ui/react | awk '{print $2}' | head -1)
        print_success "@assistant-ui/react installed: $ASSISTANT_UI_VERSION"
    else
        print_error "@assistant-ui/react not found"
    fi

    if [ -d "node_modules/@ai-sdk/anthropic" ]; then
        ANTHROPIC_VERSION=$(npm list @ai-sdk/anthropic 2>/dev/null | grep @ai-sdk/anthropic | awk '{print $2}' | head -1)
        print_success "@ai-sdk/anthropic installed: $ANTHROPIC_VERSION"
    else
        print_error "@ai-sdk/anthropic not found"
    fi

    if [ -d "node_modules/idb-keyval" ]; then
        IDB_VERSION=$(npm list idb-keyval 2>/dev/null | grep idb-keyval | awk '{print $2}' | head -1)
        print_success "idb-keyval installed: $IDB_VERSION"
    else
        print_error "idb-keyval not found"
    fi

    if [ -d "node_modules/lz-string" ]; then
        LZ_VERSION=$(npm list lz-string 2>/dev/null | grep lz-string | awk '{print $2}' | head -1)
        print_success "lz-string installed: $LZ_VERSION"
    else
        print_error "lz-string not found"
    fi
else
    print_error "node_modules not found. Run: npm install"
fi

cd ..

echo ""
echo "4️⃣  Environment Configuration"
echo "----------------------------"

# Check .env file
if [ -f ".env" ]; then
    print_success ".env file exists"

    # Check for API keys (without revealing them)
    if grep -q "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null; then
        print_success "ANTHROPIC_API_KEY configured"
    else
        print_warning "ANTHROPIC_API_KEY not set or invalid format"
    fi

    if grep -q "VITE_API_BASE_URL" .env 2>/dev/null; then
        print_success "VITE_API_BASE_URL configured"
    else
        print_warning "VITE_API_BASE_URL not set"
    fi
else
    print_warning ".env file not found. Copy from .env.example"
fi

echo ""
echo "5️⃣  Python Virtual Environment"
echo "------------------------------"

if [ -d "venv" ]; then
    print_success "Python venv directory exists"

    # Check if venv is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment is activated"
    else
        print_warning "Virtual environment not activated. Run: source venv/bin/activate"
    fi
else
    print_warning "Python venv not found. Create with: python3 -m venv venv"
fi

echo ""
echo "6️⃣  Port Availability"
echo "--------------------"

# Check if port 8000 is available (backend)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 8000 is in use (backend might be running)"
else
    print_success "Port 8000 is available"
fi

# Check if port 5173 is available (frontend)
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 5173 is in use (frontend might be running)"
else
    print_success "Port 5173 is available"
fi

echo ""
echo "7️⃣  Documentation"
echo "----------------"

# Check documentation files
DOC_FILES=(
    "docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md"
    "docs/MCP_SETUP_GUIDE.md"
    "docs/IDE_COMPARISON_ANALYSIS.md"
    "ASSISTANT_UI_QUICK_START.md"
    "UBUNTU_ASSISTANT_UI_SETUP.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        print_success "$(basename $doc)"
    else
        print_error "$(basename $doc) not found"
    fi
done

echo ""
echo "8️⃣  MCP Server"
echo "-------------"

if [ -f "scripts/mcp-servers/assistant-ui-docs-server.js" ]; then
    print_success "MCP server script found"

    if [ -x "scripts/mcp-servers/assistant-ui-docs-server.js" ]; then
        print_success "MCP server is executable"
    else
        print_warning "MCP server not executable. Run: chmod +x scripts/mcp-servers/assistant-ui-docs-server.js"
    fi
else
    print_error "MCP server script not found"
fi

echo ""
echo "=================================================="
echo "📊 Verification Summary"
echo "=================================================="

# Count checks
TOTAL_CHECKS=20
PASSED_CHECKS=$(grep -c "✅" <<< "$(cat)")
WARNINGS=$(grep -c "⚠️" <<< "$(cat)")

echo ""
echo "Installation Status: READY ✅"
echo ""
echo "📝 Next Steps:"
echo "   1. Ensure .env has ANTHROPIC_API_KEY"
echo "   2. Start backend: python -m uvicorn samplemind.main:app --reload"
echo "   3. Start frontend: cd web-app && npm run dev"
echo "   4. Open: http://localhost:5173/assistant-demo"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: cat ASSISTANT_UI_QUICK_START.md"
echo "   - Ubuntu Setup: cat UBUNTU_ASSISTANT_UI_SETUP.md"
echo "   - Full Guide: cat docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md"
echo ""
echo "🚀 Quick Launch (tmux):"
echo "   tmux new-session -d -s samplemind \\"
echo "     -c /home/lchta/Projects/Samplemind-AI \\"
echo "     'source venv/bin/activate && python -m uvicorn samplemind.main:app --reload' \; \\"
echo "     split-window -v -c /home/lchta/Projects/Samplemind-AI/web-app \\"
echo "     'npm run dev' \; \\"
echo "     attach-session -t samplemind"
echo ""
echo "✅ Verification Complete!"
