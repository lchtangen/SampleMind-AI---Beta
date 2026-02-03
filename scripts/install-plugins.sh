#!/bin/bash
#
# SampleMind AI Plugin Installation Script
# Quick installer for FL Studio and Ableton Live plugins
# Usage: bash scripts/install-plugins.sh [options]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INSTALLER_PY="$PROJECT_ROOT/plugins/installer.py"

print_banner() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  SampleMind AI - Plugin Installer                        ║${NC}"
    echo -e "${BLUE}║                       Professional Audio Intelligence                    ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.11 or later."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_info "Using Python $PYTHON_VERSION"
}

check_installer() {
    if [ ! -f "$INSTALLER_PY" ]; then
        print_error "Installer script not found at $INSTALLER_PY"
        exit 1
    fi

    print_info "Installer found at $INSTALLER_PY"
}

activate_venv() {
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        print_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
        print_success "Virtual environment activated"
    else
        print_warning "Virtual environment not found at $PROJECT_ROOT/.venv"
        print_info "Continuing without virtual environment..."
    fi
}

run_installer() {
    local args="$@"

    if [ -z "$args" ]; then
        print_info "No arguments provided. Running in interactive mode..."
        python3 "$INSTALLER_PY"
    else
        python3 "$INSTALLER_PY" $args
    fi
}

show_help() {
    cat <<EOF
${BLUE}SampleMind AI Plugin Installer${NC}

Usage: bash scripts/install-plugins.sh [OPTIONS]

Options:
  --install-all              Install all available plugins
  --install fl_studio        Install only FL Studio plugin
  --install ableton          Install only Ableton Live plugin
  --uninstall fl_studio      Uninstall FL Studio plugin
  --uninstall ableton        Uninstall Ableton Live plugin
  --uninstall-all            Uninstall all plugins
  --list                     List detected DAWs
  --verify                   Verify plugin installations
  --log <file>               Save installation log to file
  --help                     Show this help message

Examples:
  bash scripts/install-plugins.sh --install-all
  bash scripts/install-plugins.sh --install fl_studio
  bash scripts/install-plugins.sh --verify
  bash scripts/install-plugins.sh --list

Requirements:
  • Python 3.11 or later
  • Administrator/sudo privileges (for installation)
  • Supported DAWs installed (FL Studio 20+, Ableton Live 11+)

Supported Platforms:
  • Windows (Visual Studio plugins)
  • macOS (dylib plugins)
  • Linux (shared object plugins)

For more information, visit the plugin documentation:
  docs/PHASE_13_2_DAW_PLUGIN_PLAN.md
  plugins/fl_studio/BUILD.md
  plugins/ableton/README.md

EOF
}

main() {
    print_banner

    # Parse arguments
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        show_help
        exit 0
    fi

    # Pre-flight checks
    print_info "Running pre-flight checks..."
    check_python
    check_installer
    activate_venv

    echo ""

    # Check if running with sudo if installing
    if [[ "$*" == *"--install"* ]] || [[ "$*" == *"--uninstall"* ]]; then
        if [ "$EUID" -ne 0 ] && [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "cygwin" ]]; then
            print_warning "Installation/Uninstallation may require elevated privileges"
            print_info "You may be prompted for your password (sudo)"
            echo ""
        fi
    fi

    # Run installer
    run_installer "$@"

    EXIT_CODE=$?
    echo ""

    if [ $EXIT_CODE -eq 0 ]; then
        print_success "Plugin installation completed successfully!"
        print_info "Next steps:"
        echo "  1. Restart your DAW (FL Studio, Ableton Live)"
        echo "  2. Look for 'SampleMind AI' in your plugin list"
        echo "  3. For Ableton: Look in Generators (Max Instrument category)"
        echo "  4. For FL Studio: Look in Generators"
    else
        print_error "Plugin installation failed (exit code: $EXIT_CODE)"
        exit $EXIT_CODE
    fi
}

# Run main function with all arguments
main "$@"
