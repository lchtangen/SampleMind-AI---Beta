#!/bin/bash

# SampleMind AI - Gemini API Key Setup
# Quick setup script to get a new Google Gemini API key

echo "🤖 SampleMind AI - Gemini API Key Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}📋 GOOGLE GEMINI API SETUP INSTRUCTIONS:${NC}"
echo ""
echo -e "${YELLOW}1.${NC} 🌐 Go to: ${BLUE}https://aistudio.google.com/app/apikey${NC}"
echo -e "${YELLOW}2.${NC} 🔐 Sign in with your Google account"
echo -e "${YELLOW}3.${NC} ➕ Click '+ Create API Key'"
echo -e "${YELLOW}4.${NC} 📋 Copy your new API key"
echo -e "${YELLOW}5.${NC} 🔒 Paste it below"
echo ""

# Wait for user to get the key
echo -e "${BLUE}Press Enter when you have your API key ready...${NC}"
read -r

# Get the API key
echo -e "${YELLOW}🔐 Please enter your new Google Gemini API Key:${NC}"
read -s -p "API Key: " GOOGLE_AI_API_KEY
echo ""

if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo -e "${RED}❌ No API key provided. Exiting...${NC}"
    exit 1
fi

# Backup existing .env file
if [ -f ".env" ]; then
    echo -e "${YELLOW}📄 Backing up existing .env file...${NC}"
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Update the .env file
echo -e "${BLUE}📝 Updating .env file with new API key...${NC}"

# Read current .env and update the GOOGLE_AI_API_KEY line
if [ -f ".env" ]; then
    # Update existing file
    sed -i "s/^GOOGLE_AI_API_KEY=.*/GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY/" .env
else
    # Create new .env file
    cat > .env << EOF
# SampleMind AI v6 - Environment Configuration
GOOGLE_AI_API_KEY=$GOOGLE_AI_API_KEY

# Music AI Configuration
DEFAULT_MODEL=gemini-1.5-pro
MUSIC_MODEL=gemini-1.5-pro
MAX_TOKENS=8192
TEMPERATURE=0.7

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
fi

echo -e "${GREEN}✅ API key updated successfully!${NC}"
echo ""

# Test the API key
echo -e "${BLUE}🧪 Testing API key...${NC}"

# Test using the CLI
if [ -f "gemini-cli.py" ]; then
    echo -e "${YELLOW}Testing with Gemini CLI...${NC}"
    .venv/bin/python gemini-cli.py ask "Hello, just testing the API connection. Please respond with just 'API key working perfectly!'"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ API key test successful!${NC}"
        echo ""
        echo -e "${CYAN}🚀 You can now use the Gemini CLI:${NC}"
        echo -e "${YELLOW}• Quick question:${NC} .venv/bin/python gemini-cli.py ask \"your question\""
        echo -e "${YELLOW}• Interactive chat:${NC} .venv/bin/python gemini-cli.py chat"
        echo -e "${YELLOW}• Music production:${NC} .venv/bin/python gemini-cli.py music"
        echo -e "${YELLOW}• Check status:${NC} .venv/bin/python gemini-cli.py status"
    else
        echo -e "${RED}❌ API key test failed. Please check your key and try again.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Gemini CLI not found. API key updated but not tested.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"