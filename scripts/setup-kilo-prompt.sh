#!/bin/bash

# ============================================================================
# Kilo Code Master Prompt Setup Script
# ============================================================================
# This script helps you set up the SampleMind AI master prompt in Kilo Code
# ============================================================================

echo "🚀 Kilo Code Master Prompt Setup"
echo "=================================="
echo ""

PROMPT_FILE="docs/KILO_CODE_MASTER_PROMPT.md"
SETTINGS_FILE=".vscode/settings.json"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "❌ Error: $PROMPT_FILE not found!"
    exit 1
fi

echo "📄 Master prompt found at: $PROMPT_FILE"
echo "⚙️  Workspace settings: $SETTINGS_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 INSTRUCTIONS TO SET UP KILO CODE CUSTOM PROMPT:"
echo ""
echo "Method 1: VS Code Settings UI (RECOMMENDED - EASIEST)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Press: Ctrl+, (or Cmd+, on Mac)"
echo "2. Search: 'kilo code custom'"
echo "3. Click 'Edit in settings.json' or paste directly"
echo "4. Copy ALL content from: $PROMPT_FILE"
echo "5. Paste into the 'Custom Instructions' field"
echo ""
echo "Method 2: Manual JSON Edit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Open: $SETTINGS_FILE"
echo "2. Find the line: \"kiloCode.customInstructions\":"
echo "3. Replace with the entire prompt from $PROMPT_FILE"
echo "   (You'll need to escape quotes and format as JSON string)"
echo ""
echo "Method 3: Copy to Clipboard (Linux with xclip)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if xclip is available
if command -v xclip &> /dev/null; then
    echo "✅ xclip detected! Would you like to copy the prompt to clipboard? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cat "$PROMPT_FILE" | xclip -selection clipboard
        echo "✅ Prompt copied to clipboard!"
        echo "   Now paste it into Kilo Code settings (Ctrl+, → search 'kilo code')"
    fi
else
    echo "⚠️  Install xclip to enable clipboard copy: sudo apt install xclip"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 QUICK REFERENCE - Kilo Code Setting Keys:"
echo "   • kiloCode.customInstructions  - Main custom prompt"
echo "   • kiloCode.systemPrompt        - System-level instructions"
echo "   • kiloCode.temperature         - Model creativity (0.1 = precise)"
echo "   • kiloCode.maxTokens          - Response length (8000 recommended)"
echo ""
echo "✨ After setup, Kilo Code will generate production-ready code"
echo "   following your exact architecture, patterns, and standards!"
echo ""
