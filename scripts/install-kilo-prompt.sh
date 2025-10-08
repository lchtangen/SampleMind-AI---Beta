#!/bin/bash

# ============================================================================
# Kilo Code Master Prompt Installation Script
# ============================================================================
# This script helps you install the comprehensive master prompt into Kilo Code
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 KILO CODE MASTER PROMPT INSTALLATION                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

PROMPT_FILE="docs/KILO_CODE_MASTER_PROMPT.md"
USER_SETTINGS="$HOME/.config/Code/User/settings.json"

# Check if master prompt exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo "❌ Error: Master prompt not found at: $PROMPT_FILE"
    exit 1
fi

echo "✅ Master prompt found: $PROMPT_FILE"
echo "   Size: $(wc -l < "$PROMPT_FILE") lines"
echo ""

# Display instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 INSTALLATION METHODS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "METHOD 1: VS Code Settings UI (EASIEST - RECOMMENDED)"
echo "────────────────────────────────────────────────────────"
echo "1. Press: Ctrl+, (opens Settings)"
echo "2. Search: \"kilo code custom\""
echo "3. Find: \"Kilo Code > Custom Instructions\""
echo "4. Copy ALL content from: $PROMPT_FILE"
echo "5. Paste into the custom instructions field"
echo "6. Save (auto-saves)"
echo ""
echo "METHOD 2: Copy to Clipboard (Linux)"
echo "────────────────────────────────────────────────────────"

# Check if xclip is available
if command -v xclip &> /dev/null; then
    echo "✅ xclip detected!"
    echo ""
    read -p "Copy master prompt to clipboard? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat "$PROMPT_FILE" | xclip -selection clipboard
        echo "✅ Master prompt copied to clipboard!"
        echo ""
        echo "Next steps:"
        echo "1. Press: Ctrl+,"
        echo "2. Search: \"kilo code custom\""
        echo "3. Paste: Ctrl+V"
        echo "4. Done!"
        echo ""
    fi
else
    echo "⚠️  xclip not installed"
    echo "   Install with: sudo apt install xclip"
    echo "   Then run this script again"
    echo ""
fi

echo "METHOD 3: Edit settings.json Manually"
echo "────────────────────────────────────────────────────────"
echo "1. Open: $USER_SETTINGS"
echo "2. Find: \"kilo-code.customInstructions\""
echo "3. Replace value with entire prompt from:"
echo "   $PROMPT_FILE"
echo "   (You'll need to escape quotes and format as JSON string)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 WHAT'S IN THE MASTER PROMPT?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Complete tech stack (Python FastAPI, React TypeScript)"
echo "✅ 80+ dependency specifications"
echo "✅ Backend architecture patterns (async-first, microservices)"
echo "✅ Frontend patterns (React 19, Zustand, Radix UI)"
echo "✅ Modern UI/UX system (glassmorphism, animations)"
echo "✅ Performance targets (<100ms backend, <120ms frontend)"
echo "✅ Security standards (OWASP 100% compliance)"
echo "✅ Real implementation examples (components, APIs)"
echo "✅ Code quality rules (type safety, error handling)"
echo "✅ Complete file organization"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 AFTER INSTALLATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Kilo Code will:"
echo "• Understand your entire architecture automatically"
echo "• Generate production-ready code (no placeholders)"
echo "• Follow your exact patterns (async, Pydantic, Zustand)"
echo "• Create beautiful UI (glassmorphic, smooth animations)"
echo "• Optimize for performance (2-4x speedups)"
echo "• Implement security (OWASP compliant)"
echo "• Match your code style perfectly"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ READY TO INSTALL!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose a method above and follow the steps."
echo "The master prompt will transform Kilo Code into your"
echo "personal senior engineer! 🚀"
echo ""
