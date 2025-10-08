#!/bin/bash
# NetHunter SSH Zsh Setup - Optimized for Termux Mobile Connection
# Designed for SSH connections from Android Termux to NetHunter
# Ultra-lightweight configuration for mobile performance
# Author: SampleMind AI Project
# Date: October 2025

set -e

# Colors for output (SSH/Termux compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check SSH environment and mobile optimization
check_ssh_environment() {
    print_header "Checking SSH/Mobile Environment"
    
    if [[ -n "$SSH_CLIENT" ]] || [[ -n "$SSH_TTY" ]]; then
        print_success "SSH connection detected - optimizing for mobile"
        export MOBILE_SSH=true
    else
        print_warning "No SSH detected, but optimizing for mobile anyway"
        export MOBILE_SSH=true
    fi
    
    # Check terminal capabilities
    if [[ "$TERM" == *"screen"* ]] || [[ "$TERM" == *"tmux"* ]]; then
        print_status "Terminal multiplexer detected"
        export TERM_MULTIPLEXER=true
    fi
    
    # Check for Termux environment indicators
    if [[ -n "$PREFIX" ]] || [[ "$PATH" == *"com.termux"* ]]; then
        print_status "Termux environment detected on host side"
    fi
    
    print_success "Environment optimized for SSH/mobile usage"
}

# Lightweight system update
update_system_lightweight() {
    print_header "Lightweight System Update"
    
    # Only update package lists, don't upgrade everything
    apt update
    
    # Install only essential packages
    apt install -y curl wget git zsh
    
    # Skip heavy packages that might not be needed over SSH
    print_success "Essential packages installed"
}

# Install Oh My Zsh with mobile optimizations
install_ohmyzsh_mobile() {
    print_header "Installing Oh My Zsh (Mobile Optimized)"
    
    # Backup existing configurations
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        print_warning "Backing up existing Oh My Zsh..."
        mv "$HOME/.oh-my-zsh" "$HOME/.oh-my-zsh.backup.$(date +%s)"
    fi
    
    if [[ -f "$HOME/.zshrc" ]]; then
        print_warning "Backing up existing .zshrc..."
        cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%s)"
    fi
    
    # Install Oh My Zsh with mobile-friendly settings
    print_status "Installing Oh My Zsh (unattended)..."
    RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    
    print_success "Oh My Zsh installed with mobile optimizations"
}

# Install ultra-lightweight Spaceship alternative
install_spaceship_lite() {
    print_header "Installing Spaceship Theme (SSH Optimized)"
    
    # For SSH/mobile, we'll use a lighter alternative or minimal Spaceship
    if [[ -d "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt" ]]; then
        print_warning "Updating existing Spaceship theme..."
        cd "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt"
        git pull
    else
        print_status "Installing Spaceship theme..."
        git clone https://github.com/spaceship-prompt/spaceship-prompt.git "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt" --depth=1
    fi
    
    # Create symlink
    ln -sf "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt/spaceship.zsh-theme" "$HOME/.oh-my-zsh/custom/themes/spaceship.zsh-theme"
    
    print_success "Spaceship theme installed"
}

# Install minimal plugin set for SSH performance
install_essential_plugins() {
    print_header "Installing Essential Plugins (SSH Optimized)"
    
    # Only install the most essential plugins for SSH usage
    # zsh-autosuggestions (lightweight)
    if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions" ]]; then
        print_status "Installing zsh-autosuggestions..."
        git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions --depth=1
    fi
    
    # Skip syntax highlighting for SSH performance
    print_status "Skipping syntax highlighting for better SSH performance"
    
    print_success "Essential plugins installed"
}

# Configure ultra-optimized .zshrc for SSH/mobile
configure_mobile_zshrc() {
    print_header "Configuring Mobile/SSH Optimized .zshrc"
    
    cat > "$HOME/.zshrc" << 'EOF'
# Oh My Zsh Configuration - SSH/Mobile Optimized
# Ultra-lightweight setup for Termux SSH connections
# Optimized for minimal latency and mobile performance

# Path to Oh My Zsh installation
export ZSH="$HOME/.oh-my-zsh"

# Use lightweight theme - Spaceship with minimal config
ZSH_THEME="spaceship"

# Performance optimizations for SSH/Mobile
DISABLE_AUTO_UPDATE="true"        # Never check for updates over mobile
DISABLE_UPDATE_PROMPT="true"      # No update prompts
DISABLE_CORRECTION="true"         # No command correction (saves time)
COMPLETION_WAITING_DOTS="false"   # No dots animation over SSH
DISABLE_UNTRACKED_FILES_DIRTY="true"  # Faster git status

# Minimal history for mobile storage
HIST_STAMPS="mm/dd"
HISTSIZE=1000                     # Reduced for mobile
SAVEHIST=1000                     # Reduced for mobile
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_REDUCE_BLANKS
setopt HIST_SAVE_NO_DUPS

# Minimal plugin set (only essentials for SSH)
plugins=(
    git                           # Essential for development
    sudo                         # Quick sudo commands
    zsh-autosuggestions         # Lightweight completion
    # Removed all heavy plugins for SSH performance
)

# Load Oh My Zsh
source $ZSH/oh-my-zsh.sh

# Spaceship Ultra-Minimal Configuration (SSH Optimized)
SPACESHIP_PROMPT_ORDER=(
  user          # Username section
  dir           # Current directory section
  git           # Git section (essential)
  line_sep      # Line break
  char          # Prompt character
)

# Disable ALL resource-intensive sections for SSH
SPACESHIP_TIME_SHOW=false
SPACESHIP_HOST_SHOW=false         # Not needed over SSH
SPACESHIP_EXEC_TIME_SHOW=false
SPACESHIP_BATTERY_SHOW=false      # Not relevant over SSH
SPACESHIP_VI_MODE_SHOW=false

# Git optimization (essential but fast)
SPACESHIP_GIT_STATUS_SHOW=true
SPACESHIP_GIT_STATUS_UNTRACKED="?"
SPACESHIP_GIT_STATUS_ADDED="+"
SPACESHIP_GIT_STATUS_MODIFIED="!"
SPACESHIP_GIT_STATUS_DELETED="✘"
SPACESHIP_GIT_STATUS_STASHED="$"
SPACESHIP_GIT_STATUS_AHEAD="↑"
SPACESHIP_GIT_STATUS_BEHIND="↓"

# Disable ALL language-specific sections
SPACESHIP_PACKAGE_SHOW=false
SPACESHIP_NODE_SHOW=false
SPACESHIP_RUBY_SHOW=false
SPACESHIP_ELM_SHOW=false
SPACESHIP_ELIXIR_SHOW=false
SPACESHIP_XCODE_SHOW=false
SPACESHIP_SWIFT_SHOW=false
SPACESHIP_GOLANG_SHOW=false
SPACESHIP_PHP_SHOW=false
SPACESHIP_RUST_SHOW=false
SPACESHIP_HASKELL_SHOW=false
SPACESHIP_JULIA_SHOW=false
SPACESHIP_DOCKER_SHOW=false
SPACESHIP_AWS_SHOW=false
SPACESHIP_VENV_SHOW=false         # Disabled for SSH performance
SPACESHIP_CONDA_SHOW=false
SPACESHIP_PYENV_SHOW=false
SPACESHIP_DOTNET_SHOW=false
SPACESHIP_EMBER_SHOW=false
SPACESHIP_KUBECTL_SHOW=false
SPACESHIP_TERRAFORM_SHOW=false
SPACESHIP_IBMCLOUD_SHOW=false
SPACESHIP_ASYNC_SHOW=false

# SSH/Mobile optimizations
export TERM="screen-256color"     # Better SSH compatibility
export KEYTIMEOUT=1               # Fast key response

# Optimize autosuggestions for mobile
ZSH_AUTOSUGGEST_MANUAL_REBIND=1
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=10  # Very small for mobile
ZSH_AUTOSUGGEST_USE_ASYNC=false     # Sync for SSH reliability

# CRITICAL: Fast paste mode for mobile copy-paste
# This prevents lag when pasting commands from mobile
autoload -Uz bracketed-paste-magic
zle -N bracketed-paste bracketed-paste-magic
zstyle ':bracketed-paste-magic' active-widgets '.self-*'

# Mobile-friendly aliases (short and efficient)
alias l='ls -CF'
alias ll='ls -lh'
alias la='ls -la'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Essential NetHunter aliases (short for mobile typing)
alias n='nmap'
alias nq='nmap -T4 -F'              # Quick scan
alias nf='nmap -T4 -A'              # Full scan
alias nik='nikto -h'
alias sql='sqlmap --batch'
alias msf='msfconsole -q'

# Network shortcuts
alias myip='curl -s ipinfo.io/ip'
alias ports='ss -tuln'
alias net='ip a'

# System shortcuts
alias mem='free -h'
alias cpu='htop'
alias disk='df -h'
alias proc='ps aux'

# Git shortcuts (essential for development)
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -10'

# Python shortcuts
alias py='python3'
alias pip='pip3'
alias venv='python3 -m venv'

# Quick functions for mobile
function mkcd() { mkdir -p "$1" && cd "$1"; }
function backup() { cp "$1" "$1.backup.$(date +%s)"; }

# Minimal welcome message
echo "📱 SSH NetHunter Ready (Mobile Optimized)"

EOF

    print_success "Mobile-optimized .zshrc created"
}

# Create alternative minimal theme option
create_minimal_theme() {
    print_header "Creating Ultra-Minimal Theme Alternative"
    
    cat > "$HOME/switch-to-minimal.sh" << 'EOF'
#!/bin/bash
# Switch to ultra-minimal theme for maximum SSH performance

echo "Switching to minimal theme for maximum performance..."

# Create minimal theme
mkdir -p ~/.oh-my-zsh/custom/themes

cat > ~/.oh-my-zsh/custom/themes/ssh-minimal.zsh-theme << 'THEME_EOF'
# SSH Minimal Theme - Ultra fast for mobile
# Shows only: user@host:dir $ 

PROMPT='%F{green}%n@%m%f:%F{blue}%1~%f %# '
RPROMPT='%F{yellow}$(git_prompt_info)%f'

ZSH_THEME_GIT_PROMPT_PREFIX="("
ZSH_THEME_GIT_PROMPT_SUFFIX=")"
ZSH_THEME_GIT_PROMPT_DIRTY="*"
ZSH_THEME_GIT_PROMPT_CLEAN=""
THEME_EOF

# Update .zshrc to use minimal theme
sed -i 's/ZSH_THEME="spaceship"/ZSH_THEME="ssh-minimal"/' ~/.zshrc

echo "✅ Minimal theme activated! Restart terminal for ultra-fast performance."
echo "📱 Perfect for slow SSH connections or low-end mobile devices."
EOF

    chmod +x "$HOME/switch-to-minimal.sh"
    print_success "Minimal theme alternative created: ~/switch-to-minimal.sh"
}

# Configure SSH-specific optimizations
configure_ssh_optimizations() {
    print_header "Configuring SSH Connection Optimizations"
    
    # Create SSH config optimizations for the client side (Termux)
    cat > "$HOME/ssh-mobile-tips.txt" << 'EOF'
📱 SSH Mobile Performance Tips for Termux
═══════════════════════════════════════

🔧 Termux Client Optimizations:
• Install in Termux: pkg install openssh
• Use compression: ssh -C user@nethunter-ip
• Keep alive: ssh -o ServerAliveInterval=60 user@nethunter-ip
• Fast cipher: ssh -c aes128-ctr user@nethunter-ip

⚡ NetHunter Server Optimizations:
• Edit /etc/ssh/sshd_config:
  - Compression yes
  - TCPKeepAlive yes
  - ClientAliveInterval 60

📋 Quick Connection Command:
ssh -C -o ServerAliveInterval=60 -c aes128-ctr user@ip

🎯 Performance Features Enabled:
• Minimal prompt components
• Disabled heavy language checkers  
• Fast paste mode for mobile copy-paste
• Reduced history size
• No automatic updates over mobile
• Optimized git status checks

🚀 Quick Commands:
• Minimal theme: ~/switch-to-minimal.sh
• Current theme: echo $ZSH_THEME
• Restart zsh: exec zsh
• Performance test: time (git status && pwd && ls)

EOF

    print_success "SSH optimization guide created: ~/ssh-mobile-tips.txt"
}

# Set zsh as default (SSH compatible)
set_ssh_shell() {
    print_header "Configuring Zsh for SSH Sessions"
    
    # For SSH sessions, we need a different approach
    if ! grep -q "exec zsh" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# Auto-launch zsh for SSH sessions" >> ~/.bashrc
        echo "if [[ -t 1 && \$- == *i* && \$(ps -o comm= \$\$) != \"zsh\" ]]; then" >> ~/.bashrc
        echo "    exec zsh" >> ~/.bashrc
        echo "fi" >> ~/.bashrc
    fi
    
    # Also add to .profile for login shells
    if ! grep -q "exec zsh" ~/.profile 2>/dev/null; then
        echo "" >> ~/.profile
        echo "# Launch zsh for SSH login shells" >> ~/.profile  
        echo "if [[ -t 1 && \$- == *i* && -x \$(command -v zsh) && \$(ps -o comm= \$\$) != \"zsh\" ]]; then" >> ~/.profile
        echo "    exec zsh" >> ~/.profile
        echo "fi" >> ~/.profile
    fi
    
    print_success "Zsh configured for SSH sessions"
}

# Main installation function
main() {
    print_header "NetHunter SSH/Mobile Zsh Setup"
    print_status "Optimizing for Termux SSH connections..."
    
    check_ssh_environment
    update_system_lightweight
    install_ohmyzsh_mobile
    install_spaceship_lite
    install_essential_plugins
    configure_mobile_zshrc
    create_minimal_theme
    configure_ssh_optimizations
    set_ssh_shell
    
    print_success "SSH/Mobile installation completed!"
    
    echo ""
    print_header "📱 Mobile SSH Setup Complete!"
    cat << 'EOF'

✅ Installation Complete!

🚀 Next Steps:
1. Restart your SSH session or run: source ~/.zshrc
2. For ultra-minimal theme: ~/switch-to-minimal.sh
3. Read mobile tips: cat ~/ssh-mobile-tips.txt

📱 Optimizations Applied:
• Disabled heavy language checkers
• Minimal history for mobile storage
• Fast paste mode for mobile copy-paste
• Lightweight plugin set
• SSH connection optimizations
• Mobile-friendly aliases

⚡ Performance Features:
• Spaceship theme (minimal config)
• Ultra-minimal theme available
• Fast git status checks
• Optimized for SSH latency
• Mobile keyboard shortcuts

🔧 Troubleshooting:
• Slow? Run: ~/switch-to-minimal.sh
• Connection issues? Check: ~/ssh-mobile-tips.txt
• Reset config: rm ~/.zshrc && source ~/.bashrc

EOF

    print_success "Happy mobile hacking! 📱🛡️"
}

# Run main function
main "$@"