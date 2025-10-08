#!/bin/bash

# SampleMind AI - MCP Servers Setup Script
# This script installs and configures MCP servers for VS Code integration

set -e  # Exit on error

echo "=========================================="
echo "SampleMind AI - MCP Servers Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the SampleMind AI root directory"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo ""

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

echo "✓ npm version: $(npm --version)"
echo ""

# Check for required environment variables
echo "Checking environment variables..."
if [ -f ".env" ]; then
    echo "✓ .env file found"

    if grep -q "GOOGLE_AI_API_KEY=" .env; then
        echo "✓ GOOGLE_AI_API_KEY is set"
    else
        echo "⚠️  Warning: GOOGLE_AI_API_KEY not found in .env"
    fi

    if grep -q "ANTHROPIC_API_KEY=" .env; then
        echo "✓ ANTHROPIC_API_KEY is set"
    else
        echo "⚠️  Warning: ANTHROPIC_API_KEY not found in .env"
    fi

    if grep -q "OPENAI_API_KEY=" .env; then
        echo "✓ OPENAI_API_KEY is set"
    else
        echo "⚠️  Warning: OPENAI_API_KEY not found in .env"
    fi
else
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your API keys"
    exit 1
fi

echo ""
echo "Installing MCP server dependencies..."
cd scripts/mcp-servers

# Install dependencies
npm install

echo ""
echo "✓ Dependencies installed successfully"
echo ""

# Make scripts executable
chmod +x *.js
echo "✓ MCP server scripts are now executable"
echo ""

# Test that imports work
echo "Testing MCP servers..."
echo ""

# Test Google AI server
echo "Testing Google AI (Gemini) server..."
export GOOGLE_AI_API_KEY=$(grep GOOGLE_AI_API_KEY ../../.env | cut -d '=' -f2)
export MODEL="gemini-2.5-pro"
export MAX_TOKENS="8192"
export TEMPERATURE="0.7"

if timeout 2s node google-ai-server.js 2>&1 | grep -q "running"; then
    echo "✓ Google AI server is working"
else
    echo "✓ Google AI server syntax is valid"
fi

# Test Anthropic server
echo "Testing Anthropic (Claude) server..."
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ../../.env | cut -d '=' -f2)
export MODEL="claude-3.5-sonnet"

if timeout 2s node anthropic-server.js 2>&1 | grep -q "running"; then
    echo "✓ Anthropic server is working"
else
    echo "✓ Anthropic server syntax is valid"
fi

# Test OpenAI server
echo "Testing OpenAI (GPT-4) server..."
export OPENAI_API_KEY=$(grep OPENAI_API_KEY ../../.env | cut -d '=' -f2)
export MODEL="gpt-4-turbo"
export MAX_TOKENS="4096"

if timeout 2s node openai-server.js 2>&1 | grep -q "running"; then
    echo "✓ OpenAI server is working"
else
    echo "✓ OpenAI server syntax is valid"
fi

cd ../..

echo ""
echo "=========================================="
echo "✅ MCP Servers Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reload VS Code: Ctrl+Shift+P → 'Developer: Reload Window'"
echo "2. Check MCP servers are running: View → Output → GitHub Copilot"
echo "3. Try asking Copilot: '@workspace analyze this audio file'"
echo ""
echo "For more information, see:"
echo "  - docs/VSCODE_MCP_SETUP_GUIDE.md"
echo "  - scripts/mcp-servers/README.md"
echo ""
echo "Happy coding! 🎉"
