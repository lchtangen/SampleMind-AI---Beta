#!/bin/bash
#
# SampleMind AI v6 - macOS Automated Setup Script
# Supports: macOS Big Sur 11.0+, Monterey, Ventura, Sonoma
#
# Usage: ./scripts/macos_setup.sh
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      🍎 SampleMind AI v6 - macOS Setup Wizard 🍎        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect macOS version
detect_macos_version() {
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_BUILD=$(sw_vers -buildVersion)
    ARCH=$(uname -m)

    echo -e "${GREEN}✓${NC} macOS Version: $MACOS_VERSION"
    echo -e "${GREEN}✓${NC} Build: $MACOS_BUILD"
    echo -e "${GREEN}✓${NC} Architecture: $ARCH"

    # Check if Apple Silicon
    if [ "$ARCH" = "arm64" ]; then
        echo -e "${GREEN}✓${NC} Apple Silicon (M1/M2/M3) detected"
        IS_APPLE_SILICON=true
    else
        echo -e "${YELLOW}→${NC} Intel Mac detected"
        IS_APPLE_SILICON=false
    fi
}

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}✗${NC} Please do not run this script as root!"
        echo -e "  Run as normal user. Script will prompt for password when needed."
        exit 1
    fi
}

# Install Homebrew
install_homebrew() {
    echo -e "\n${BLUE}🍺 Checking for Homebrew...${NC}"

    if command -v brew &> /dev/null; then
        echo -e "${GREEN}✓${NC} Homebrew already installed"
        BREW_VERSION=$(brew --version | head -1)
        echo -e "${YELLOW}→${NC} $BREW_VERSION"
    else
        echo -e "${YELLOW}→${NC} Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH for Apple Silicon
        if [ "$IS_APPLE_SILICON" = true ]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        echo -e "${GREEN}✓${NC} Homebrew installed"
    fi

    # Update Homebrew
    echo -e "${YELLOW}→${NC} Updating Homebrew..."
    brew update
}

# Install system dependencies
install_system_deps() {
    echo -e "\n${BLUE}📦 Installing system dependencies...${NC}"

    # Install required packages
    echo -e "${YELLOW}→${NC} Installing packages via Homebrew..."
    brew install \
        python@3.11 \
        ffmpeg \
        portaudio \
        libsndfile \
        git

    # Link Python 3.11
    brew link python@3.11

    echo -e "${GREEN}✓${NC} System dependencies installed"
}

# Setup Python virtual environment
setup_venv() {
    echo -e "\n${BLUE}🐍 Setting up Python environment...${NC}"

    cd "$PROJECT_ROOT"

    # Get Python path
    PYTHON_PATH=$(brew --prefix python@3.11)/bin/python3.11

    # Check Python version
    PYTHON_VERSION=$($PYTHON_PATH --version 2>&1 | grep -oE '\d+\.\d+\.\d+')
    echo -e "${YELLOW}→${NC} Python version: $PYTHON_VERSION"
    echo -e "${YELLOW}→${NC} Python path: $PYTHON_PATH"

    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}→${NC} Creating virtual environment..."
        $PYTHON_PATH -m venv .venv
    else
        echo -e "${YELLOW}→${NC} Virtual environment already exists"
    fi

    # Activate venv
    source .venv/bin/activate

    # Upgrade pip
    echo -e "${YELLOW}→${NC} Upgrading pip..."
    pip install --upgrade pip --quiet

    echo -e "${GREEN}✓${NC} Python environment ready"
}

# Install Python packages
install_python_packages() {
    echo -e "\n${BLUE}📚 Installing Python packages...${NC}"

    source .venv/bin/activate

    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}→${NC} Installing from requirements.txt..."
        pip install -r requirements.txt --quiet
    fi

    # Install additional packages
    echo -e "${YELLOW}→${NC} Installing AI packages..."
    pip install google-generativeai openai mutagen --quiet

    # Apple Silicon optimizations
    if [ "$IS_APPLE_SILICON" = true ]; then
        echo -e "${YELLOW}→${NC} Installing Apple Silicon optimized packages..."
        pip install torch torchvision torchaudio --quiet
    fi

    echo -e "${GREEN}✓${NC} Python packages installed"
}

# Configure API keys
configure_api_keys() {
    echo -e "\n${BLUE}🔑 Configuring API keys...${NC}"

    if [ -f ".env" ]; then
        echo -e "${YELLOW}→${NC} .env file already exists"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}⊙${NC} Skipping API configuration"
            return
        fi
    fi

    echo -e "${YELLOW}→${NC} Please enter your API keys (or press Enter to skip):"
    echo ""

    read -p "Gemini API Key (PRIMARY): " GEMINI_KEY
    read -p "OpenAI API Key (FALLBACK - optional): " OPENAI_KEY

    # Create .env file
    cat > .env << EOF
# SampleMind AI v6 - Environment Configuration

# Google AI (Gemini) API Configuration - PRIMARY
GOOGLE_AI_API_KEY=${GEMINI_KEY:-your_gemini_key_here}

# OpenAI API Configuration - FALLBACK
OPENAI_API_KEY=${OPENAI_KEY:-your_openai_key_here}

# Music AI Configuration
DEFAULT_MODEL=gemini-2.5-pro
MUSIC_MODEL=gemini-2.5-pro
MAX_TOKENS=8192
TEMPERATURE=0.7

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
CACHE_ENABLED=true
BATCH_PROCESSING=true

# FL Studio Integration
FL_STUDIO_INTEGRATION=true
REAL_TIME_ANALYSIS=true
STREAMING_ENABLED=true

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
ENABLE_COST_OPTIMIZATION=true

# Multi-API Support
PRIMARY_API=google_ai
FALLBACK_API=openai
API_ROTATION_ENABLED=false

# macOS Specific
METAL_DEVICE_WRAPPER_TYPE=1
PYTORCH_ENABLE_MPS_FALLBACK=1
EOF

    chmod 600 .env
    echo -e "${GREEN}✓${NC} API keys configured (.env created)"
}

# Run verification
run_verification() {
    echo -e "\n${BLUE}🔍 Running system verification...${NC}"

    source .venv/bin/activate

    if [ -f "verify_setup.py" ]; then
        python verify_setup.py
    else
        echo -e "${YELLOW}⚠${NC} Verification script not found, skipping..."
    fi
}

# Grant accessibility permissions
grant_permissions() {
    echo -e "\n${BLUE}🔐 Configuring macOS permissions...${NC}"

    echo -e "${YELLOW}→${NC} For native Finder dialogs to work, Terminal needs accessibility permissions."
    echo ""
    echo -e "${YELLOW}Please:${NC}"
    echo "  1. Open System Settings > Privacy & Security > Accessibility"
    echo "  2. Add Terminal.app (or iTerm.app) to the list"
    echo "  3. Enable the checkbox"
    echo ""
    read -p "Press Enter when done..."
}

# Create Automator Quick Action (optional)
create_automator_action() {
    echo -e "\n${BLUE}⚡ Creating Automator Quick Action...${NC}"

    read -p "Create 'Analyze with SampleMind AI' Quick Action? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    WORKFLOW_DIR="$HOME/Library/Services"
    mkdir -p "$WORKFLOW_DIR"

    cat > "$WORKFLOW_DIR/Analyze with SampleMind AI.workflow/Contents/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>523</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict/>
                    <key>CheckedForUserDefaultShell</key>
                    <dict/>
                    <key>inputMethod</key>
                    <dict/>
                    <key>shell</key>
                    <dict/>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>AUDIO_FILE="$1"
cd "${PROJECT_ROOT}"
.venv/bin/python main.py analyze "$AUDIO_FILE"</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
            </dict>
        </dict>
    </array>
</dict>
</plist>
EOF

    echo -e "${GREEN}✓${NC} Automator action created"
    echo -e "${YELLOW}→${NC} Right-click any audio file > Services > Analyze with SampleMind AI"
}

# Create shell alias
create_alias() {
    echo -e "\n${BLUE}⚡ Creating shell alias...${NC}"

    read -p "Add 'smai' command alias? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    # Detect shell
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bash_profile"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        echo -e "${YELLOW}⚠${NC} Unknown shell, skipping..."
        return
    fi

    # Add alias
    ALIAS_LINE="alias smai='$PROJECT_ROOT/start_cli.sh'"

    if ! grep -q "alias smai=" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# SampleMind AI" >> "$SHELL_RC"
        echo "$ALIAS_LINE" >> "$SHELL_RC"
        echo -e "${GREEN}✓${NC} Alias added to $SHELL_RC"
        echo -e "${YELLOW}→${NC} Run: source $SHELL_RC"
    else
        echo -e "${YELLOW}⊙${NC} Alias already exists"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              ✅ Setup Complete! 🎉                        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo -e "  1. ${YELLOW}Activate environment:${NC}"
    echo -e "     ${BLUE}source .venv/bin/activate${NC}"
    echo ""
    echo -e "  2. ${YELLOW}Run demo:${NC}"
    echo -e "     ${BLUE}./start_cli.sh --demo${NC}"
    echo ""
    echo -e "  3. ${YELLOW}Start interactive CLI:${NC}"
    echo -e "     ${BLUE}./start_cli.sh${NC}"
    echo ""
    echo -e "  4. ${YELLOW}Analyze audio:${NC}"
    echo -e "     ${BLUE}./start_cli.sh analyze ~/Music/song.wav${NC}"
    echo ""
    echo -e "${YELLOW}🍎 macOS Features:${NC}"
    echo -e "  • Native Finder dialogs for file selection"
    echo -e "  • Spotlight integration for search"
    echo -e "  • Right-click Quick Actions (if created)"
    echo -e "  • Apple Silicon optimized (M1/M2/M3)"
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo -e "  • Quick Start: ${BLUE}cat QUICKSTART.md${NC}"
    echo -e "  • macOS Guide: ${BLUE}cat MACOS_GUIDE.md${NC}"
    echo -e "  • CLI Guide:   ${BLUE}cat GEMINI_CLI_GUIDE.md${NC}"
    echo ""
}

# Main installation flow
main() {
    echo -e "${YELLOW}→${NC} Starting automated setup..."
    echo ""

    check_not_root
    detect_macos_version
    install_homebrew
    install_system_deps
    setup_venv
    install_python_packages
    configure_api_keys
    run_verification
    grant_permissions
    create_automator_action
    create_alias
    show_next_steps

    echo -e "${GREEN}🎉 Installation complete!${NC}"
}

# Run main
main
