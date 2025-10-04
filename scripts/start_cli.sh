#!/bin/bash
# SampleMind AI v6 - CLI Startup Script
# Automatically sets up environment and starts the CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎵 SampleMind AI v6 - Starting CLI${NC}\n"

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠${NC} No .env file found, using system environment"
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠${NC} No .venv found, using system Python"
fi

# Check API keys
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} GOOGLE_AI_API_KEY not set"
else
    echo -e "${GREEN}✓${NC} Gemini API key configured"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY not set (optional fallback)"
else
    echo -e "${GREEN}✓${NC} OpenAI API key configured (fallback)"
fi

echo ""

# Start the CLI
if [ "$1" = "--demo" ]; then
    echo -e "${BLUE}Running demo...${NC}\n"
    python demo_gemini_cli.py
elif [ "$1" = "--verify" ]; then
    echo -e "${BLUE}Running verification...${NC}\n"
    python verify_setup.py
elif [ -n "$1" ]; then
    echo -e "${BLUE}Running command: python main.py $@${NC}\n"
    python main.py "$@"
else
    echo -e "${BLUE}Starting interactive CLI...${NC}\n"
    python main.py
fi
