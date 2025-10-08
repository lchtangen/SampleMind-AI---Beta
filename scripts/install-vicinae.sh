#!/usr/bin/env bash

################################################################################
# Vicinae Installation Script for Ubuntu
# Version: 1.0.0
# Description: Automated installation of Vicinae launcher on Ubuntu 22.04+
# Author: SampleMind AI
# Date: October 6, 2025
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VICINAE_VERSION="v0.14.1"
APPIMAGE_URL="https://github.com/vicinaehq/vicinae/releases/download/${VICINAE_VERSION}/Vicinae-2486a0e0d-x86_64.AppImage"
INSTALL_DIR="$HOME/.local/bin"
ICON_URL="https://raw.githubusercontent.com/vicinaehq/vicinae/main/extra/vicinae.png"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           Vicinae Installation Script for Ubuntu              ║"
    echo "║                                                                ║"
    echo "║  A high-performance, native launcher for Linux                ║"
    echo "║  Version: ${VICINAE_VERSION}                                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_ubuntu() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot detect OS. /etc/os-release not found."
        exit 1
    fi

    . /etc/os-release

    if [[ "$ID" != "ubuntu" ]] && [[ "$ID_LIKE" != *"ubuntu"* ]]; then
        print_warning "This script is designed for Ubuntu. Detected OS: $ID"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    print_step "OS Check: $PRETTY_NAME"
}

install_dependencies() {
    print_info "Installing dependencies..."

    # Update package list
    sudo apt update -qq

    # Install FUSE (required for AppImage)
    if ! dpkg -l | grep -q libfuse2; then
        print_info "Installing libfuse2..."
        sudo apt install -y libfuse2
    else
        print_step "libfuse2 already installed"
    fi

    # Install optional dependencies
    if ! dpkg -l | grep -q libqalculate; then
        print_info "Installing libqalculate (optional, for calculator features)..."
        sudo apt install -y libqalculate22 libqalculate-dev || print_warning "Could not install libqalculate"
    else
        print_step "libqalculate already installed"
    fi

    print_step "Dependencies installed successfully"
}

download_appimage() {
    print_info "Downloading Vicinae AppImage..."

    # Create install directory
    mkdir -p "$INSTALL_DIR"

    # Download AppImage
    local appimage_path="$INSTALL_DIR/vicinae"

    if [[ -f "$appimage_path" ]]; then
        print_warning "Vicinae already exists at $appimage_path"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping download"
            return 0
        fi
        rm -f "$appimage_path"
    fi

    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "$appimage_path" "$APPIMAGE_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$appimage_path" "$APPIMAGE_URL" --progress-bar
    else
        print_error "Neither wget nor curl found. Please install one of them."
        exit 1
    fi

    # Make executable
    chmod +x "$appimage_path"

    print_step "AppImage downloaded to: $appimage_path"
}

create_desktop_entry() {
    print_info "Creating desktop entry..."

    local desktop_dir="$HOME/.local/share/applications"
    local icon_dir="$HOME/.local/share/icons"

    mkdir -p "$desktop_dir" "$icon_dir"

    # Download icon
    local icon_path="$icon_dir/vicinae.png"
    if [[ ! -f "$icon_path" ]]; then
        print_info "Downloading icon..."
        if command -v wget &> /dev/null; then
            wget -q -O "$icon_path" "$ICON_URL" || print_warning "Could not download icon"
        elif command -v curl &> /dev/null; then
            curl -sL -o "$icon_path" "$ICON_URL" || print_warning "Could not download icon"
        fi
    fi

    # Create .desktop file
    cat > "$desktop_dir/vicinae.desktop" << EOF
[Desktop Entry]
Name=Vicinae
Comment=A focused launcher for your desktop — native, fast, extensible
Exec=$INSTALL_DIR/vicinae server
Icon=$icon_path
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true
EOF

    print_step "Desktop entry created"
}

setup_keyboard_shortcut() {
    local desktop_env=""

    if [[ -n "${XDG_CURRENT_DESKTOP:-}" ]]; then
        desktop_env="$XDG_CURRENT_DESKTOP"
    elif [[ -n "${DESKTOP_SESSION:-}" ]]; then
        desktop_env="$DESKTOP_SESSION"
    fi

    print_info "Detected desktop environment: ${desktop_env:-Unknown}"
    echo
    print_warning "Vicinae cannot auto-register keyboard shortcuts on Linux."
    print_info "You need to manually set a keyboard shortcut:"
    echo

    case "${desktop_env,,}" in
        *gnome*|*ubuntu*)
            echo "  GNOME/Ubuntu:"
            echo "  1. Open Settings → Keyboard → Keyboard Shortcuts"
            echo "  2. Click 'Add Custom Shortcut'"
            echo "  3. Name: Vicinae"
            echo "  4. Command: $INSTALL_DIR/vicinae toggle"
            echo "  5. Shortcut: Super+Space (or your preference)"
            ;;
        *kde*|*plasma*)
            echo "  KDE Plasma:"
            echo "  1. System Settings → Shortcuts → Custom Shortcuts"
            echo "  2. Add new Global Shortcut"
            echo "  3. Trigger: Meta+Space"
            echo "  4. Action: $INSTALL_DIR/vicinae toggle"
            ;;
        *hyprland*|*sway*)
            echo "  Hyprland/Sway (add to config file):"
            echo "  bind = \$mod, SPACE, exec, $INSTALL_DIR/vicinae toggle"
            ;;
        *)
            echo "  Generic method:"
            echo "  Set a keyboard shortcut to run: $INSTALL_DIR/vicinae toggle"
            ;;
    esac

    echo
}

test_installation() {
    print_info "Testing installation..."

    if [[ ! -x "$INSTALL_DIR/vicinae" ]]; then
        print_error "Vicinae binary not found or not executable"
        exit 1
    fi

    # Test if binary can be executed
    if "$INSTALL_DIR/vicinae" --version &> /dev/null; then
        print_step "Installation verified successfully"
    else
        print_warning "Could not verify installation (this may be normal)"
    fi
}

print_next_steps() {
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Installation Complete! 🎉                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    print_info "Next Steps:"
    echo
    echo "  1. Start Vicinae server:"
    echo -e "     ${BLUE}$INSTALL_DIR/vicinae server${NC}"
    echo
    echo "  2. Set up keyboard shortcut (see instructions above)"
    echo
    echo "  3. Open Vicinae:"
    echo -e "     ${BLUE}$INSTALL_DIR/vicinae toggle${NC}"
    echo
    echo "  4. Explore features:"
    echo "     - Clipboard history"
    echo "     - Emoji picker"
    echo "     - Extension store (type 'store')"
    echo
    print_info "Documentation: https://docs.vicinae.com"
    print_info "GitHub: https://github.com/vicinaehq/vicinae"
    print_info "Discord: https://discord.com/invite/rP4ecD42p7"
    echo
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    print_header

    # Check if running on Ubuntu
    check_ubuntu

    # Install dependencies
    install_dependencies

    # Download AppImage
    download_appimage

    # Create desktop entry
    create_desktop_entry

    # Test installation
    test_installation

    # Show keyboard shortcut instructions
    setup_keyboard_shortcut

    # Print next steps
    print_next_steps
}

# Run main function
main "$@"
