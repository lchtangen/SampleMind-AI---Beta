#!/bin/bash

# 🔥 SampleMind AI Phoenix - Easy Startup Script
# For Beginners - No technical knowledge required!

# Colors for visual feedback
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ASCII Art Logo
echo ""
echo "  🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥"
echo ""
echo "   ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗"
echo "   ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝"
echo "   ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  "
echo "   ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  "
echo "   ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗"
echo "   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝"
echo ""
echo "   ███╗   ███╗██╗███╗   ██╗██████╗"
echo "   ████╗ ████║██║████╗  ██║██╔══██╗"
echo "   ██╔████╔██║██║██╔██╗ ██║██║  ██║"
echo "   ██║╚██╔╝██║██║██║╚██╗██║██║  ██║"
echo "   ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝"
echo "   ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝"
echo ""
echo "        🔥 PHOENIX - Beta v2.0 🔥"
echo "    AI-Powered Music Production Platform"
echo ""
echo "  🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥 🔥"
echo ""

# Progress indicator function
show_progress() {
    local current=$1
    local total=$2
    local message=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 5))
    local empty=$((20 - filled))
    
    printf "\r${BLUE}[${NC}"
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "${BLUE}]${NC} ${percent}%% - ${message}"
}

# Check if we're in the right directory
echo -e "${BLUE}Step 1/5:${NC} Checking location..."
sleep 0.5

if [ ! -f "src/samplemind/__init__.py" ]; then
    echo -e "${RED}✗ Error: Please run this script from the project root directory!${NC}"
    echo -e "${YELLOW}  Try: cd ~/Projects/samplemind-ai-v6${NC}"
    exit 1
fi

show_progress 1 5 "Location verified"
echo ""

# Check for virtual environment
echo -e "${BLUE}Step 2/5:${NC} Setting up environment..."
sleep 0.5

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}  Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

show_progress 2 5 "Environment activated"
echo ""

# Install/update dependencies
echo -e "${BLUE}Step 3/5:${NC} Installing dependencies..."
sleep 0.5

# Check if packages are installed
if ! python -c "import rich" 2>/dev/null; then
    echo -e "${YELLOW}  Installing required packages...${NC}"
    pip install -q rich typer click 2>&1 | grep -v "already satisfied" || true
fi

show_progress 3 5 "Dependencies installed"
echo ""

# Install Phoenix
echo -e "${BLUE}Step 4/5:${NC} Installing Phoenix..."
sleep 0.5

pip install -q -e . 2>&1 | grep -v "already satisfied" || true

show_progress 4 5 "Phoenix installed"
echo ""

# Verify installation
echo -e "${BLUE}Step 5/5:${NC} Verifying installation..."
sleep 0.5

if command -v samplemind &> /dev/null; then
    show_progress 5 5 "Installation complete!"
    echo ""
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                      ║${NC}"
    echo -e "${GREEN}║  ✓ Phoenix is ready!                                 ║${NC}"
    echo -e "${GREEN}║                                                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Show version
    echo -e "${BLUE}Version Information:${NC}"
    samplemind --version 2>/dev/null || echo "SampleMind AI Phoenix Beta v2.0"
    echo ""
    
    # Quick start guide
    echo -e "${YELLOW}🚀 Quick Start Guide:${NC}"
    echo ""
    echo -e "  ${GREEN}1.${NC} Analyze a sample:"
    echo -e "     ${BLUE}samplemind analyze sample.wav${NC}"
    echo ""
    echo -e "  ${GREEN}2.${NC} Import your samples:"
    echo -e "     ${BLUE}samplemind import folder ~/Music/Samples${NC}"
    echo ""
    echo -e "  ${GREEN}3.${NC} Auto-tag with AI:"
    echo -e "     ${BLUE}samplemind tag auto kick.wav${NC}"
    echo ""
    echo -e "  ${GREEN}4.${NC} Get help anytime:"
    echo -e "     ${BLUE}samplemind --help${NC}"
    echo ""
    
    # Documentation links
    echo -e "${YELLOW}📚 Learn More:${NC}"
    echo ""
    echo -e "  • Beginner Guide:  ${BLUE}docs/QUICKSTART_PHOENIX_BEGINNER.md${NC}"
    echo -e "  • Full Roadmap:    ${BLUE}docs/V6_FEATURE_INTEGRATION_MASTER_PLAN.md${NC}"
    echo -e "  • Phase 1 Guide:   ${BLUE}docs/PHASE_1_PHOENIX_IMPLEMENTATION.md${NC}"
    echo ""
    
    # Environment reminder
    echo -e "${YELLOW}💡 Remember:${NC}"
    echo -e "  Your virtual environment is ${GREEN}activated${NC}"
    echo -e "  To deactivate later, type: ${BLUE}deactivate${NC}"
    echo ""
    
    # Success message
    echo -e "${GREEN}🎉 You're all set! Start creating! 🎵${NC}"
    echo ""
    
else
    echo ""
    echo -e "${RED}✗ Installation failed!${NC}"
    echo -e "${YELLOW}  Please check the error messages above.${NC}"
    echo ""
    echo -e "${YELLOW}Need help? Run:${NC}"
    echo -e "  ${BLUE}cat docs/QUICKSTART_PHOENIX_BEGINNER.md${NC}"
    echo ""
    exit 1
fi
