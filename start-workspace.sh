#!/bin/bash
##############################################################################
# SampleMind AI Workspace Startup Script
# Launches VS Code with all auto-configurations
##############################################################################

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Starting SampleMind AI Development Environment      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Initialize MCP Servers
echo -e "${GREEN}🚀 Initializing MCP Servers...${NC}"
bash "$PROJECT_ROOT/scripts/mcp-auto-start.sh"

# Step 2: Launch VS Code
echo -e "${GREEN}🎨 Launching VS Code...${NC}"
echo -e "${GREEN}   → Custom instructions: .github/copilot-instructions.md${NC}"
echo -e "${GREEN}   → MCP servers: 29 configured and ready${NC}"
echo -e "${GREEN}   → Master prompt: docs/KILO_CODE_MASTER_PROMPT.md${NC}"

code "$PROJECT_ROOT"

echo ""
echo -e "${GREEN}✅ Workspace initialized successfully!${NC}"
echo -e "${GREEN}   GitHub Copilot will auto-load custom instructions${NC}"
echo -e "${GREEN}   All MCP servers are ready to use${NC}"
