#!/bin/bash
# NetHunter Installation Script for Ubuntu x86_64 Desktop
# Installs Kali NetHunter tools and environment on Ubuntu
# Author: SampleMind AI Project
# Date: October 2025

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${PURPLE}================================${NC}"; echo -e "${PURPLE}$1${NC}"; echo -e "${PURPLE}================================${NC}"; }

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        print_status "Run as regular user. sudo will be used when needed."
        exit 1
    fi
}

# Detect system info
detect_system() {
    print_header "System Detection"
    
    OS=$(lsb_release -si 2>/dev/null || echo "Unknown")
    VERSION=$(lsb_release -sr 2>/dev/null || echo "Unknown")
    ARCH=$(uname -m)
    
    print_status "Operating System: $OS $VERSION"
    print_status "Architecture: $ARCH"
    
    if [[ "$OS" != "Ubuntu" ]]; then
        print_warning "This script is optimized for Ubuntu. Continuing anyway..."
    fi
    
    if [[ "$ARCH" != "x86_64" ]]; then
        print_error "This script requires x86_64 architecture"
        exit 1
    fi
    
    print_success "System compatibility confirmed"
}

# Update system
update_system() {
    print_header "Updating System"
    
    print_status "Updating package lists..."
    sudo apt update
    
    print_status "Installing essential packages..."
    sudo apt install -y \
        curl \
        wget \
        git \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        software-properties-common \
        dirmngr \
        gpg-agent
    
    print_success "System updated"
}

# Add Kali repositories
add_kali_repos() {
    print_header "Adding Kali Linux Repositories"
    
    # Add Kali GPG key
    print_status "Adding Kali GPG key..."
    wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add -
    
    # Add Kali repository
    print_status "Adding Kali repository..."
    echo "deb https://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" | sudo tee /etc/apt/sources.list.d/kali.list
    
    # Set lower priority for Kali packages to avoid conflicts
    print_status "Setting repository priorities..."
    cat << 'EOF' | sudo tee /etc/apt/preferences.d/kali.pref
Package: *
Pin: release o=Kali
Pin-Priority: 50
EOF
    
    # Update package lists
    sudo apt update
    
    print_success "Kali repositories added"
}

# Install NetHunter tools
install_nethunter_tools() {
    print_header "Installing NetHunter Tools"
    
    print_status "Installing core penetration testing tools..."
    
    # Core tools
    sudo apt install -y -t kali-rolling \
        nmap \
        nikto \
        sqlmap \
        metasploit-framework \
        aircrack-ng \
        wireshark \
        john \
        hashcat \
        hydra \
        dirb \
        gobuster \
        wfuzz \
        burpsuite \
        zaproxy \
        ettercap-text-only \
        dnsrecon \
        fierce \
        theharvester \
        whatweb \
        masscan \
        recon-ng \
        maltego \
        social-engineer-toolkit
    
    print_success "Core tools installed"
    
    print_status "Installing additional security tools..."
    
    # Additional tools
    sudo apt install -y -t kali-rolling \
        beef-xss \
        wpscan \
        searchsploit \
        exploitdb \
        crackmapexec \
        responder \
        impacket-scripts \
        bloodhound \
        neo4j \
        wifite \
        bettercap \
        kismet \
        pixiewps \
        reaver \
        bully \
        hostapd-wpe
    
    print_success "Additional tools installed"
}

# Install modern tools from GitHub
install_modern_tools() {
    print_header "Installing Modern Security Tools"
    
    # Create tools directory
    mkdir -p ~/tools
    cd ~/tools
    
    print_status "Installing Go (required for many modern tools)..."
    if ! command -v go &> /dev/null; then
        wget -q https://golang.org/dl/go1.21.3.linux-amd64.tar.gz
        sudo tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        export PATH=$PATH:/usr/local/go/bin
        rm go1.21.3.linux-amd64.tar.gz
    fi
    
    print_status "Installing ProjectDiscovery tools..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest
    
    print_status "Installing additional modern tools..."
    
    # RustScan
    if ! command -v rustscan &> /dev/null; then
        wget -q https://github.com/RustScan/RustScan/releases/download/2.0.1/rustscan_2.0.1_amd64.deb
        sudo dpkg -i rustscan_2.0.1_amd64.deb
        rm rustscan_2.0.1_amd64.deb
    fi
    
    # Amass
    go install -v github.com/owasp-amass/amass/v4/...@master
    
    print_success "Modern tools installed"
    
    # Update PATH for Go tools
    echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
    export PATH=$PATH:~/go/bin
}

# Create NetHunter launcher
create_nethunter_launcher() {
    print_header "Creating NetHunter Launcher"
    
    # Create the main launcher script
    cat > ~/nethunter << 'EOF'
#!/bin/bash
# NetHunter Launcher for Ubuntu Desktop
# Provides access to all installed security tools

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Ensure Go tools are in PATH
export PATH=$PATH:/usr/local/go/bin:~/go/bin

print_header() {
    clear
    echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    NetHunter Desktop                      ║${NC}"
    echo -e "${PURPLE}║                Ubuntu x86_64 Edition                      ║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🛡️  Kali NetHunter Tools Environment${NC}"
    echo -e "${BLUE}📊 System: $(lsb_release -d | cut -f2)${NC}"
    echo -e "${BLUE}🏗️  Architecture: $(uname -m)${NC}"
    echo -e "${BLUE}👤 User: $(whoami)${NC}"
    echo ""
}

show_menu() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Select an option:${NC}"
    echo ""
    echo -e "${GREEN} 1)${NC} Network Scanning & Reconnaissance"
    echo -e "${GREEN} 2)${NC} Web Application Testing"
    echo -e "${GREEN} 3)${NC} Wireless Security Testing"
    echo -e "${GREEN} 4)${NC} Exploitation & Post-Exploitation"
    echo -e "${GREEN} 5)${NC} Password Attacks"
    echo -e "${GREEN} 6)${NC} Social Engineering"
    echo -e "${GREEN} 7)${NC} OSINT & Information Gathering"
    echo -e "${GREEN} 8)${NC} Modern Security Tools"
    echo -e "${GREEN} 9)${NC} Launch Full Kali Shell"
    echo -e "${GREEN}10)${NC} System Information"
    echo -e "${GREEN}11)${NC} Update Tools"
    echo -e "${RED} 0)${NC} Exit"
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
}

network_tools() {
    echo -e "${BLUE}Network Scanning & Reconnaissance Tools:${NC}"
    echo "1) nmap - Network Mapper"
    echo "2) masscan - Fast port scanner"
    echo "3) rustscan - Modern port scanner"
    echo "4) naabu - Fast port discovery"
    echo "5) dnsrecon - DNS reconnaissance"
    echo "6) fierce - DNS scanner"
    echo "7) theharvester - Email/subdomain harvester"
    echo "8) subfinder - Subdomain discovery"
    echo "9) amass - Attack surface mapping"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) nmap ;;
        2) masscan ;;
        3) rustscan ;;
        4) naabu ;;
        5) dnsrecon ;;
        6) fierce ;;
        7) theharvester ;;
        8) subfinder ;;
        9) amass ;;
        0) return ;;
    esac
}

web_tools() {
    echo -e "${BLUE}Web Application Testing Tools:${NC}"
    echo "1) nikto - Web vulnerability scanner"
    echo "2) sqlmap - SQL injection tool"
    echo "3) dirb - Directory brute forcer"
    echo "4) gobuster - Directory/DNS brute forcer"
    echo "5) wfuzz - Web fuzzer"
    echo "6) burpsuite - Web proxy"
    echo "7) zaproxy - OWASP ZAP"
    echo "8) whatweb - Web technology identifier"
    echo "9) wpscan - WordPress scanner"
    echo "10) httpx - HTTP toolkit"
    echo "11) nuclei - Vulnerability scanner"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) nikto ;;
        2) sqlmap ;;
        3) dirb ;;
        4) gobuster ;;
        5) wfuzz ;;
        6) burpsuite ;;
        7) zaproxy ;;
        8) whatweb ;;
        9) wpscan ;;
        10) httpx ;;
        11) nuclei ;;
        0) return ;;
    esac
}

wireless_tools() {
    echo -e "${BLUE}Wireless Security Testing Tools:${NC}"
    echo "1) aircrack-ng - WiFi security auditing"
    echo "2) wifite - Automated WiFi auditing"
    echo "3) bettercap - Network attack framework"
    echo "4) kismet - Wireless detector"
    echo "5) reaver - WPS attack tool"
    echo "6) bully - WPS brute force"
    echo "7) pixiewps - WPS PIN recovery"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) aircrack-ng ;;
        2) wifite ;;
        3) sudo bettercap ;;
        4) kismet ;;
        5) reaver ;;
        6) bully ;;
        7) pixiewps ;;
        0) return ;;
    esac
}

exploitation_tools() {
    echo -e "${BLUE}Exploitation & Post-Exploitation Tools:${NC}"
    echo "1) metasploit-framework - Exploitation framework"
    echo "2) searchsploit - Exploit database search"
    echo "3) crackmapexec - Post-exploitation tool"
    echo "4) responder - LLMNR/NBT-NS poisoner"
    echo "5) impacket-scripts - Network protocols toolkit"
    echo "6) bloodhound - Active Directory recon"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) msfconsole ;;
        2) searchsploit ;;
        3) crackmapexec ;;
        4) sudo responder ;;
        5) echo "Impacket scripts available: impacket-*" ;;
        6) bloodhound ;;
        0) return ;;
    esac
}

password_tools() {
    echo -e "${BLUE}Password Attack Tools:${NC}"
    echo "1) john - John the Ripper"
    echo "2) hashcat - Advanced password recovery"
    echo "3) hydra - Online password attack"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) john ;;
        2) hashcat ;;
        3) hydra ;;
        0) return ;;
    esac
}

social_tools() {
    echo -e "${BLUE}Social Engineering Tools:${NC}"
    echo "1) social-engineer-toolkit - SET"
    echo "2) maltego - Link analysis"
    echo "3) beef-xss - Browser exploitation"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) sudo setoolkit ;;
        2) maltego ;;
        3) sudo beef-xss ;;
        0) return ;;
    esac
}

osint_tools() {
    echo -e "${BLUE}OSINT & Information Gathering Tools:${NC}"
    echo "1) theharvester - Email/subdomain harvester"
    echo "2) recon-ng - Reconnaissance framework"
    echo "3) maltego - Link analysis"
    echo "4) subfinder - Subdomain discovery"
    echo "5) amass - Attack surface mapping"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) theharvester ;;
        2) recon-ng ;;
        3) maltego ;;
        4) subfinder ;;
        5) amass ;;
        0) return ;;
    esac
}

modern_tools() {
    echo -e "${BLUE}Modern Security Tools (2024/2025):${NC}"
    echo "1) nuclei - Modern vulnerability scanner"
    echo "2) httpx - HTTP toolkit"
    echo "3) subfinder - Fast subdomain discovery"
    echo "4) naabu - Port discovery"
    echo "5) katana - Web crawler"
    echo "6) rustscan - Rust port scanner"
    echo "0) Back to main menu"
    
    read -p "Select tool: " choice
    case $choice in
        1) nuclei ;;
        2) httpx ;;
        3) subfinder ;;
        4) naabu ;;
        5) katana ;;
        6) rustscan ;;
        0) return ;;
    esac
}

kali_shell() {
    echo -e "${GREEN}Launching NetHunter shell environment...${NC}"
    echo -e "${YELLOW}All NetHunter tools are available in your PATH${NC}"
    echo -e "${BLUE}Type 'exit' to return to the main menu${NC}"
    echo ""
    export PS1="\[\033[01;31m\]┌──(\[\033[01;33m\]\u\[\033[01;31m\]💀\[\033[01;33m\]\h\[\033[01;31m\])-[\[\033[01;37m\]\w\[\033[01;31m\]]\n└─\[\033[01;31m\]$ \[\033[00m\]"
    bash
}

system_info() {
    echo -e "${BLUE}System Information:${NC}"
    echo "OS: $(lsb_release -d | cut -f2)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo "Uptime: $(uptime -p)"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
    echo ""
    echo -e "${BLUE}Installed Tools Check:${NC}"
    
    tools=("nmap" "nikto" "sqlmap" "metasploit" "aircrack-ng" "john" "hashcat" "hydra" "subfinder" "httpx" "nuclei" "rustscan")
    for tool in "${tools[@]}"; do
        if command -v $tool &> /dev/null; then
            echo -e "${GREEN}✓${NC} $tool"
        else
            echo -e "${RED}✗${NC} $tool"
        fi
    done
    
    read -p "Press Enter to continue..."
}

update_tools() {
    echo -e "${BLUE}Updating NetHunter tools...${NC}"
    sudo apt update
    sudo apt upgrade -y
    
    # Update Go tools
    echo -e "${BLUE}Updating Go-based tools...${NC}"
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest
    
    # Update Nuclei templates
    nuclei -update-templates
    
    echo -e "${GREEN}Tools updated successfully!${NC}"
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    print_header
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1) network_tools ;;
        2) web_tools ;;
        3) wireless_tools ;;
        4) exploitation_tools ;;
        5) password_tools ;;
        6) social_tools ;;
        7) osint_tools ;;
        8) modern_tools ;;
        9) kali_shell ;;
        10) system_info ;;
        11) update_tools ;;
        0) 
            echo -e "${GREEN}Goodbye! Happy hacking! 🛡️${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 2
            ;;
    esac
done
EOF

    chmod +x ~/nethunter
    
    # Create desktop launcher
    cat > ~/.local/share/applications/nethunter.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=NetHunter Desktop
Comment=Kali NetHunter Tools for Ubuntu
Exec=/home/USERNAME/nethunter
Icon=security-high
Terminal=true
Categories=System;Security;
EOF

    # Replace USERNAME with actual username
    sed -i "s/USERNAME/$(whoami)/g" ~/.local/share/applications/nethunter.desktop
    
    # Add to PATH
    if ! grep -q "export PATH=\$PATH:~" ~/.bashrc; then
        echo 'export PATH=$PATH:~/go/bin:/usr/local/go/bin' >> ~/.bashrc
    fi
    
    print_success "NetHunter launcher created"
    print_status "Run 'nethunter' command to start"
    print_status "Desktop launcher also created"
}

# Configure Wireshark
configure_wireshark() {
    print_header "Configuring Wireshark"
    
    print_status "Adding user to wireshark group..."
    sudo usermod -a -G wireshark $(whoami)
    
    print_warning "You need to log out and log back in for group changes to take effect"
    print_success "Wireshark configured"
}

# Install additional Python tools
install_python_tools() {
    print_header "Installing Python Security Tools"
    
    print_status "Installing Python pip and tools..."
    sudo apt install -y python3-pip python3-venv
    
    print_status "Creating virtual environment for security tools..."
    python3 -m venv ~/venv/security-tools
    source ~/venv/security-tools/bin/activate
    
    print_status "Installing Python security libraries..."
    pip install --upgrade pip
    pip install \
        scapy \
        requests \
        beautifulsoup4 \
        lxml \
        paramiko \
        pycrypto \
        dnspython \
        python-nmap \
        shodan \
        censys \
        waybackpy \
        builtwith \
        python-whois \
        ipwhois \
        geoip2
    
    deactivate
    
    print_success "Python security tools installed"
}

# Main installation function
main() {
    print_header "NetHunter Desktop Installation"
    print_status "Installing Kali NetHunter tools on Ubuntu Desktop..."
    
    check_permissions
    detect_system
    update_system
    add_kali_repos
    install_nethunter_tools
    install_modern_tools
    create_nethunter_launcher
    configure_wireshark
    install_python_tools
    
    print_success "NetHunter Desktop installation completed!"
    
    echo ""
    print_header "🎉 Installation Complete!"
    cat << 'EOF'

✅ What was installed:
• Core NetHunter/Kali penetration testing tools
• Modern security tools (2024/2025)
• ProjectDiscovery suite (subfinder, httpx, nuclei, etc.)
• Python security libraries
• Custom NetHunter launcher with menu system

🚀 How to use:
1. Run: nethunter
2. Or: ./nethunter (from home directory)
3. Desktop launcher also available

🔧 Post-installation:
• Log out and log back in (for Wireshark permissions)
• Run 'source ~/.bashrc' to update PATH
• Update tools anytime with option 11 in menu

🛡️ Available tool categories:
• Network Scanning & Reconnaissance
• Web Application Testing
• Wireless Security Testing
• Exploitation & Post-Exploitation
• Password Attacks
• Social Engineering
• OSINT & Information Gathering
• Modern Security Tools (2024/2025)

EOF

    print_success "Run 'nethunter' to start your security toolkit! 🛡️"
}

main "$@"