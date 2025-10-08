#!/bin/bash
# NetHunter Oh My Zsh + Spaceship Theme Installation Script
# Optimized for Kali NetHunter Pro Rootless with performance enhancements
# Author: SampleMind AI Project
# Date: October 2025

set -e

# Colors for output
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

# Check if we're in NetHunter environment
check_nethunter() {
    print_header "Checking NetHunter Environment"
    
    if [[ ! -f /etc/os-release ]] || ! grep -q "Kali" /etc/os-release; then
        print_warning "This doesn't appear to be a Kali environment"
        print_status "Continuing anyway... (might work on other Debian-based systems)"
    else
        print_success "Kali NetHunter environment detected"
    fi
    
    # Check if we have network connectivity
    if ping -c 1 google.com &> /dev/null; then
        print_success "Network connectivity confirmed"
    else
        print_error "No network connectivity. Please check your connection."
        exit 1
    fi
}

# Update system packages
update_system() {
    print_header "Updating System Packages"
    
    apt update -y
    apt install -y curl wget git zsh fonts-powerline
    
    print_success "System packages updated"
}

# Install Oh My Zsh
install_ohmyzsh() {
    print_header "Installing Oh My Zsh"
    
    # Remove existing Oh My Zsh installation if present
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        print_warning "Existing Oh My Zsh installation found. Backing up..."
        mv "$HOME/.oh-my-zsh" "$HOME/.oh-my-zsh.backup.$(date +%s)"
    fi
    
    if [[ -f "$HOME/.zshrc" ]]; then
        print_warning "Existing .zshrc found. Backing up..."
        cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%s)"
    fi
    
    # Install Oh My Zsh (unattended installation)
    print_status "Downloading Oh My Zsh installer..."
    RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    
    print_success "Oh My Zsh installed successfully"
}

# Install Spaceship theme
install_spaceship() {
    print_header "Installing Spaceship Theme"
    
    # Clone Spaceship theme
    if [[ -d "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt" ]]; then
        print_warning "Spaceship theme already exists. Updating..."
        cd "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt"
        git pull
    else
        print_status "Cloning Spaceship theme..."
        git clone https://github.com/spaceship-prompt/spaceship-prompt.git "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt" --depth=1
    fi
    
    # Create symlink
    ln -sf "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt/spaceship.zsh-theme" "$HOME/.oh-my-zsh/custom/themes/spaceship.zsh-theme"
    
    print_success "Spaceship theme installed"
}

# Install useful Oh My Zsh plugins
install_plugins() {
    print_header "Installing Useful Plugins"
    
    # zsh-autosuggestions
    if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions" ]]; then
        print_status "Installing zsh-autosuggestions..."
        git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    fi
    
    # zsh-syntax-highlighting
    if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting" ]]; then
        print_status "Installing zsh-syntax-highlighting..."
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    fi
    
    # fast-syntax-highlighting (faster alternative)
    if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/fast-syntax-highlighting" ]]; then
        print_status "Installing fast-syntax-highlighting..."
        git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
    fi
    
    print_success "Plugins installed"
}

# Configure optimized .zshrc
configure_zshrc() {
    print_header "Configuring Optimized .zshrc"
    
    cat > "$HOME/.zshrc" << 'EOF'
# Oh My Zsh Configuration - NetHunter Optimized
# Performance optimizations for better terminal responsiveness

# Path to Oh My Zsh installation
export ZSH="$HOME/.oh-my-zsh"

# Theme configuration
ZSH_THEME="spaceship"

# Performance optimizations
DISABLE_AUTO_UPDATE="true"    # Disable automatic updates
DISABLE_UPDATE_PROMPT="true"  # Don't prompt for updates
COMPLETION_WAITING_DOTS="true" # Show dots while waiting for completion

# History configuration for better performance
HIST_STAMPS="yyyy-mm-dd"
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_VERIFY
setopt SHARE_HISTORY

# Plugin configuration (optimized selection)
plugins=(
    git
    sudo
    command-not-found
    zsh-autosuggestions
    fast-syntax-highlighting
    # Removed heavy plugins for better performance
)

# Load Oh My Zsh
source $ZSH/oh-my-zsh.sh

# Spaceship Theme Configuration (Performance Optimized)
SPACESHIP_PROMPT_ORDER=(
  time          # Time stamps section
  user          # Username section
  dir           # Current directory section
  host          # Hostname section
  git           # Git section (git_branch + git_status)
  node          # Node.js section
  python        # Python section
  exec_time     # Execution time
  line_sep      # Line break
  battery       # Battery level and status
  vi_mode       # Vi-mode indicator
  jobs          # Background jobs indicator
  exit_code     # Exit code section
  char          # Prompt character
)

# Performance optimizations for Spaceship
SPACESHIP_PROMPT_ASYNC=true
SPACESHIP_PROMPT_SEPARATE_LINE=true
SPACESHIP_PROMPT_FIRST_PREFIX_SHOW=true

# Spaceship sections configuration (disable heavy ones)
SPACESHIP_TIME_SHOW=true
SPACESHIP_TIME_COLOR="yellow"
SPACESHIP_USER_SHOW=needed
SPACESHIP_HOST_SHOW=true
SPACESHIP_HOST_COLOR="green"
SPACESHIP_DIR_TRUNC=3
SPACESHIP_DIR_TRUNC_REPO=false

# Git optimization
SPACESHIP_GIT_STATUS_SHOW=true
SPACESHIP_GIT_STATUS_UNTRACKED="?"
SPACESHIP_GIT_STATUS_ADDED="+"
SPACESHIP_GIT_STATUS_MODIFIED="!"
SPACESHIP_GIT_STATUS_RENAMED="»"
SPACESHIP_GIT_STATUS_DELETED="✘"
SPACESHIP_GIT_STATUS_STASHED="$"
SPACESHIP_GIT_STATUS_UNMERGED="="
SPACESHIP_GIT_STATUS_AHEAD="⇡"
SPACESHIP_GIT_STATUS_BEHIND="⇣"
SPACESHIP_GIT_STATUS_DIVERGED="⇕"

# Disable resource-heavy sections for better performance
SPACESHIP_PACKAGE_SHOW=false
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
SPACESHIP_VENV_SHOW=true
SPACESHIP_CONDA_SHOW=false
SPACESHIP_PYENV_SHOW=false
SPACESHIP_DOTNET_SHOW=false
SPACESHIP_EMBER_SHOW=false
SPACESHIP_KUBECTL_SHOW=false
SPACESHIP_TERRAFORM_SHOW=false
SPACESHIP_IBMCLOUD_SHOW=false
SPACESHIP_ASYNC_SHOW=false

# Performance tweaks for terminal
export TERM="xterm-256color"

# Reduce key timeout for better responsiveness
export KEYTIMEOUT=1

# Optimize autosuggestions
ZSH_AUTOSUGGEST_MANUAL_REBIND=1
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20

# Fast paste mode for large pastes
autoload -Uz bracketed-paste-magic
zle -N bracketed-paste bracketed-paste-magic

# NetHunter specific aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Security tools aliases
alias nmap-quick='nmap -T4 -F'
alias nmap-full='nmap -T4 -A -v'
alias nikto-quick='nikto -h'
alias sqlmap-quick='sqlmap --batch --smart'

# Python virtual environment helpers
alias venv-create='python3 -m venv'
alias venv-activate='source venv/bin/activate'

# Network aliases
alias myip='curl -s http://whatismyip.akamai.com/'
alias localip="ip route get 1 | awk '{print \$NF;exit}'"
alias ports='netstat -tulanp'

# System info
alias sysinfo='uname -a && lsb_release -a'
alias meminfo='free -h'
alias cpuinfo='lscpu'

# Quick directory navigation
alias projects='cd ~/Projects'
alias downloads='cd ~/Downloads'
alias desktop='cd ~/Desktop'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias gd='git diff'

# Custom functions
function mkcd() {
    mkdir -p "$1" && cd "$1"
}

function extract() {
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)   tar xjf $1     ;;
            *.tar.gz)    tar xzf $1     ;;
            *.bz2)       bunzip2 $1     ;;
            *.rar)       unrar e $1     ;;
            *.gz)        gunzip $1      ;;
            *.tar)       tar xf $1      ;;
            *.tbz2)      tar xjf $1     ;;
            *.tgz)       tar xzf $1     ;;
            *.zip)       unzip $1       ;;
            *.Z)         uncompress $1  ;;
            *.7z)        7z x $1        ;;
            *)     echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Welcome message
echo "🚀 NetHunter Terminal Ready!"
echo "💻 Spaceship theme loaded with performance optimizations"
echo "🛡️  Security tools aliases available (nmap-quick, nikto-quick, etc.)"
echo ""

EOF

    print_success ".zshrc configured with performance optimizations"
}

# Set zsh as default shell
set_default_shell() {
    print_header "Setting Zsh as Default Shell"
    
    # Check if zsh is available
    if command -v zsh >/dev/null 2>&1; then
        # In NetHunter proot, we might not be able to change shell system-wide
        # So we'll add it to the startup script instead
        print_status "Configuring zsh as default for NetHunter..."
        
        # Add to .bashrc to auto-launch zsh
        if ! grep -q "exec zsh" ~/.bashrc 2>/dev/null; then
            echo "" >> ~/.bashrc
            echo "# Auto-launch zsh in NetHunter" >> ~/.bashrc
            echo "if [[ -t 1 && \$- == *i* && \$(ps -o comm= \$\$) != \"zsh\" ]]; then" >> ~/.bashrc
            echo "    exec zsh" >> ~/.bashrc
            echo "fi" >> ~/.bashrc
        fi
        
        print_success "Zsh will launch automatically in new terminals"
    else
        print_error "Zsh not found. Please install zsh first."
        exit 1
    fi
}

# Install additional fonts for better theme support
install_fonts() {
    print_header "Installing Additional Fonts"
    
    # Create fonts directory
    mkdir -p ~/.local/share/fonts
    
    # Download and install Nerd Fonts (FiraCode)
    if [[ ! -f ~/.local/share/fonts/FiraCode-Regular.ttf ]]; then
        print_status "Downloading FiraCode Nerd Font..."
        cd /tmp
        wget -q https://github.com/ryanoasis/nerd-fonts/releases/download/v2.3.3/FiraCode.zip
        unzip -q FiraCode.zip -d FiraCode
        cp FiraCode/*.ttf ~/.local/share/fonts/
        rm -rf FiraCode FiraCode.zip
        
        # Refresh font cache
        fc-cache -fv ~/.local/share/fonts
        
        print_success "FiraCode Nerd Font installed"
    else
        print_status "FiraCode Nerd Font already installed"
    fi
}

# Create PowerLevel10k alternative setup
create_p10k_alternative() {
    print_header "Creating PowerLevel10k Alternative Setup"
    
    cat > "$HOME/switch-to-p10k.sh" << 'EOF'
#!/bin/bash
# Switch to PowerLevel10k (faster alternative to Spaceship)

echo "Installing PowerLevel10k theme..."

# Clone PowerLevel10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k

# Update .zshrc to use PowerLevel10k
sed -i 's/ZSH_THEME="spaceship"/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc

echo "PowerLevel10k installed! Restart your terminal and run 'p10k configure' to set it up."
echo "PowerLevel10k is generally faster than Spaceship for low-resource environments."
EOF

    chmod +x "$HOME/switch-to-p10k.sh"
    print_success "PowerLevel10k alternative script created at ~/switch-to-p10k.sh"
}

# Performance optimization tips
show_performance_tips() {
    print_header "Performance Optimization Tips"
    
    cat << 'EOF'

🚀 NetHunter Zsh Performance Tips:
════════════════════════════════════

1. Terminal Settings:
   • Use a terminal with good hardware acceleration
   • Limit scrollback buffer (1000-5000 lines max)
   • Disable unnecessary terminal features

2. Theme Optimization:
   • Current setup disables heavy language sections
   • If still slow, run ~/switch-to-p10k.sh for PowerLevel10k
   • Consider minimal themes for very slow devices

3. Plugin Management:
   • Only enabled essential plugins
   • Remove unused plugins from .zshrc if needed
   • fast-syntax-highlighting is used instead of zsh-syntax-highlighting

4. Network-dependent features:
   • Git status checks can be slow on large repos
   • Consider setting SPACESHIP_GIT_STATUS_SHOW=false for huge repos

5. System Resources:
   • Close unused apps to free RAM
   • Use 'htop' to monitor resource usage
   • Consider reducing HISTSIZE if memory is very limited

6. Quick Commands:
   • Use aliases for common commands
   • 'nmap-quick' instead of full nmap scans
   • 'nikto-quick' for faster web scans

7. If terminal is still slow:
   • Run: ~/switch-to-p10k.sh (PowerLevel10k is faster)
   • Or use minimal theme: ZSH_THEME="clean"
   • Or disable theme: ZSH_THEME=""

EOF
}

# Main installation function
main() {
    print_header "NetHunter Oh My Zsh + Spaceship Setup"
    print_status "Starting installation process..."
    
    check_nethunter
    update_system
    install_ohmyzsh
    install_spaceship
    install_plugins
    configure_zshrc
    set_default_shell
    install_fonts
    create_p10k_alternative
    
    print_success "Installation completed successfully!"
    print_status "Please restart your terminal or run: source ~/.zshrc"
    
    show_performance_tips
    
    echo ""
    print_header "Quick Start Commands"
    echo "• Restart terminal or: source ~/.zshrc"
    echo "• Switch to PowerLevel10k: ~/switch-to-p10k.sh"
    echo "• Configure PowerLevel10k: p10k configure"
    echo "• Edit config: nano ~/.zshrc"
    echo ""
    print_success "Happy hacking in NetHunter! 🛡️✨"
}

# Run main function
main "$@"