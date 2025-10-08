#!/bin/bash
##############################################################################
# MCP Servers Auto-Start Script
# Initializes all Model Context Protocol servers
##############################################################################

echo "🚀 Initializing MCP Servers..."

# Navigate to MCP servers directory
cd "$(dirname "$0")/mcp-servers"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing MCP server dependencies..."
    npm install
fi

# Verify all MCP servers are ready
echo "✅ Verifying MCP servers..."
node verify-setup.js

echo "✅ MCP Servers initialized and ready!"
