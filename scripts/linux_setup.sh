#!/bin/bash
#
# SampleMind AI v6 - Linux Automated Setup Script
# Supports: Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux
#
# Usage: ./scripts/linux_setup.sh
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
echo -e "${BLUE}║     🎵 SampleMind AI v6 - Linux Setup Wizard 🎵         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
        VERSION=$DISTRIB_RELEASE
    else
        DISTRO="unknown"
        VERSION="unknown"
    fi

    echo -e "${GREEN}✓${NC} Detected: $DISTRO $VERSION"
}

# Check if running as root
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}✗${NC} Please do not run this script as root!"
        echo -e "  Run as normal user. Script will prompt for sudo when needed."
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo -e "\n${BLUE}📦 Installing system dependencies...${NC}"

    case "$DISTRO" in
        ubuntu|debian|pop|linuxmint)
            echo -e "${YELLOW}→${NC} Using apt package manager..."
            sudo apt update
            sudo apt install -y \
                python3.11 \
                python3.11-venv \
                python3-pip \
                python3-tk \
                zenity \
                ffmpeg \
                portaudio19-dev \
                libsndfile1 \
                libportaudio2 \
                libportaudiocpp0 \
                git \
                curl \
                build-essential
            ;;

        fedora|rhel|centos)
            echo -e "${YELLOW}→${NC} Using dnf package manager..."
            sudo dnf install -y \
                python3.11 \
                python3-tkinter \
                zenity \
                ffmpeg \
                portaudio-devel \
                libsndfile \
                git \
                curl \
                gcc \
                gcc-c++ \
                make
            ;;

        arch|manjaro)
            echo -e "${YELLOW}→${NC} Using pacman package manager..."
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                tk \
                zenity \
                ffmpeg \
                portaudio \
                libsndfile \
                git \
                curl \
                base-devel
            ;;

        *)
            echo -e "${YELLOW}⚠${NC} Unknown distribution. Please install dependencies manually:"
            echo "  - Python 3.11+"
            echo "  - python3-venv, python3-tk"
            echo "  - zenity (GTK) or kdialog (KDE)"
            echo "  - ffmpeg, portaudio, libsndfile"
            echo "  - git, curl, build-essential"
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
            ;;
    esac

    echo -e "${GREEN}✓${NC} System dependencies installed"
}

# Setup Python virtual environment
setup_venv() {
    echo -e "\n${BLUE}🐍 Setting up Python environment...${NC}"

    cd "$PROJECT_ROOT"

    # Check Python version
    PYTHON_VERSION=$(python3.11 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    echo -e "${YELLOW}→${NC} Python version: $PYTHON_VERSION"

    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}→${NC} Creating virtual environment..."
        python3.11 -m venv .venv
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

# Create desktop shortcut (optional)
create_desktop_shortcut() {
    echo -e "\n${BLUE}🖥️ Creating desktop shortcut...${NC}"

    read -p "Create desktop launcher? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    DESKTOP_FILE="$HOME/.local/share/applications/samplemind-ai.desktop"

    mkdir -p "$HOME/.local/share/applications"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=SampleMind AI
Comment=AI-Powered Music Production Assistant
Exec=$PROJECT_ROOT/start_cli.sh
Icon=$PROJECT_ROOT/assets/icon.png
Terminal=true
Categories=AudioVideo;Audio;Music;
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓${NC} Desktop launcher created"
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
        SHELL_RC="$HOME/.bashrc"
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
    echo -e "     ${BLUE}./start_cli.sh analyze /path/to/song.wav${NC}"
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo -e "  • Quick Start: ${BLUE}cat QUICKSTART.md${NC}"
    echo -e "  • Linux Guide: ${BLUE}cat LINUX_GUIDE.md${NC}"
    echo -e "  • CLI Guide:   ${BLUE}cat GEMINI_CLI_GUIDE.md${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
    echo -e "  • Logs: ${BLUE}~/.samplemind/logs/${NC}"
    echo -e "  • Issues: ${BLUE}https://github.com/yourusername/samplemind-ai-v6/issues${NC}"
    echo ""
}

# Main installation flow
main() {
    echo -e "${YELLOW}→${NC} Starting automated setup..."
    echo ""

    check_not_root
    detect_distro
    install_system_deps
    setup_venv
    install_python_packages
    configure_api_keys
    run_verification
    create_desktop_shortcut
    create_alias
    show_next_steps

    echo -e "${GREEN}🎉 Installation complete!${NC}"
}

# Run main
main
