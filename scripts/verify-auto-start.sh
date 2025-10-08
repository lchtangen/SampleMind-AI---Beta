#!/bin/bash

##############################################################################
# SampleMind AI - Auto-Start Verification Script
# Verifies all auto-start configurations are working
##############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SampleMind AI - Auto-Start Verification                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

##############################################################################
# Test 1: GitHub Copilot Instructions File
##############################################################################

echo -e "${YELLOW}[Test 1/10]${NC} GitHub Copilot Instructions File..."

if [ -f "$PROJECT_ROOT/.github/copilot-instructions.md" ]; then
    LINES=$(wc -l < "$PROJECT_ROOT/.github/copilot-instructions.md")
    echo -e "${GREEN}✓ PASS${NC} - .github/copilot-instructions.md exists ($LINES lines)"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - .github/copilot-instructions.md not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 2: KILO CODE MASTER PROMPT
##############################################################################

echo -e "${YELLOW}[Test 2/10]${NC} KILO CODE MASTER PROMPT..."

if [ -f "$PROJECT_ROOT/docs/KILO_CODE_MASTER_PROMPT.md" ]; then
    LINES=$(wc -l < "$PROJECT_ROOT/docs/KILO_CODE_MASTER_PROMPT.md")
    echo -e "${GREEN}✓ PASS${NC} - docs/KILO_CODE_MASTER_PROMPT.md exists ($LINES lines)"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - docs/KILO_CODE_MASTER_PROMPT.md not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 3: MCP Servers Configuration
##############################################################################

echo -e "${YELLOW}[Test 3/10]${NC} MCP Servers Configuration..."

if grep -q "github.copilot.chat.mcpServers" "$PROJECT_ROOT/.vscode/settings.json"; then
    MCP_COUNT=$(grep -c '".*":' "$PROJECT_ROOT/.vscode/settings.json" | head -1)
    echo -e "${GREEN}✓ PASS${NC} - MCP servers configured in .vscode/settings.json"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - MCP servers not found in settings"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 4: VS Code Tasks
##############################################################################

echo -e "${YELLOW}[Test 4/10]${NC} VS Code Tasks Configuration..."

if [ -f "$PROJECT_ROOT/.vscode/tasks.json" ]; then
    echo -e "${GREEN}✓ PASS${NC} - .vscode/tasks.json exists"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - .vscode/tasks.json not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 5: Launch Configuration
##############################################################################

echo -e "${YELLOW}[Test 5/10]${NC} Launch Configuration..."

if [ -f "$PROJECT_ROOT/.vscode/launch.json" ]; then
    echo -e "${GREEN}✓ PASS${NC} - .vscode/launch.json exists"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - .vscode/launch.json not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 6: MCP Auto-Start Script
##############################################################################

echo -e "${YELLOW}[Test 6/10]${NC} MCP Auto-Start Script..."

if [ -f "$PROJECT_ROOT/scripts/mcp-auto-start.sh" ] && [ -x "$PROJECT_ROOT/scripts/mcp-auto-start.sh" ]; then
    echo -e "${GREEN}✓ PASS${NC} - scripts/mcp-auto-start.sh exists and is executable"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - scripts/mcp-auto-start.sh not found or not executable"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 7: Workspace Startup Script
##############################################################################

echo -e "${YELLOW}[Test 7/10]${NC} Workspace Startup Script..."

if [ -f "$PROJECT_ROOT/start-workspace.sh" ] && [ -x "$PROJECT_ROOT/start-workspace.sh" ]; then
    echo -e "${GREEN}✓ PASS${NC} - start-workspace.sh exists and is executable"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - start-workspace.sh not found or not executable"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 8: Shell Aliases
##############################################################################

echo -e "${YELLOW}[Test 8/10]${NC} Shell Aliases Configuration..."

if [ -f "$PROJECT_ROOT/.auto-start-alias.sh" ]; then
    echo -e "${GREEN}✓ PASS${NC} - .auto-start-alias.sh exists"
    echo -e "   ${BLUE}→${NC} Add to ~/.zshrc: source $PROJECT_ROOT/.auto-start-alias.sh"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - .auto-start-alias.sh not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 9: Systemd Service
##############################################################################

echo -e "${YELLOW}[Test 9/10]${NC} Systemd Service Configuration..."

if [ -f "$PROJECT_ROOT/.config/systemd/user/samplemind-mcp.service" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Systemd service file exists"
    echo -e "   ${BLUE}→${NC} Install: systemctl --user enable samplemind-mcp.service"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - Systemd service file not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Test 10: Documentation
##############################################################################

echo -e "${YELLOW}[Test 10/10]${NC} Auto-Start Documentation..."

if [ -f "$PROJECT_ROOT/docs/AUTO_START_SETUP.md" ]; then
    echo -e "${GREEN}✓ PASS${NC} - docs/AUTO_START_SETUP.md exists"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC} - docs/AUTO_START_SETUP.md not found"
    ((FAIL_COUNT++))
fi

##############################################################################
# Summary
##############################################################################

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Test Summary                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

TOTAL=$((PASS_COUNT + FAIL_COUNT))
PASS_PERCENT=$((PASS_COUNT * 100 / TOTAL))

echo -e "Total Tests:  ${BLUE}$TOTAL${NC}"
echo -e "Passed:       ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed:       ${RED}$FAIL_COUNT${NC}"
echo -e "Success Rate: ${GREEN}$PASS_PERCENT%${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       ✅ ALL TESTS PASSED - AUTO-START READY!                ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}🚀 To Start Working:${NC}"
    echo -e "   ${GREEN}./start-workspace.sh${NC}     # Initialize everything & launch VS Code"
    echo -e "   ${GREEN}code .${NC}                   # Just VS Code (Copilot auto-loads)"
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo -e "   ${BLUE}docs/AUTO_START_SETUP.md${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║       ⚠️  SOME TESTS FAILED - CHECK CONFIGURATION           ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}📝 To Fix:${NC}"
    echo -e "   Run: ${GREEN}./scripts/configure-auto-start.sh${NC}"
    echo ""
    exit 1
fi
