#!/bin/bash

# Deep System Cleanup for NetHunter/Termux - Aggressive Memory & Storage Recovery
# Author: GitHub Copilot
# Version: 1.0

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to show memory usage
show_memory() {
    echo -e "\n${BLUE}Current Memory Usage:${NC}"
    free -h
    echo -e "\n${BLUE}Disk Usage:${NC}"
    df -h / 2>/dev/null || df -h
}

# Check if running as root (needed for some operations)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root - will perform system-wide cleanup"
        IS_ROOT=true
    else
        log "Running as user - will perform user-space cleanup"
        IS_ROOT=false
    fi
}

# Initial system state
header "Initial System State"
show_memory

# 1. AGGRESSIVE CACHE CLEANUP
header "1. Aggressive Cache Cleanup"

# Clear APT cache (if available)
if command -v apt >/dev/null 2>&1; then
    log "Cleaning APT cache..."
    if [ "$IS_ROOT" = true ]; then
        apt clean 2>/dev/null || true
        apt autoclean 2>/dev/null || true
        apt autoremove -y 2>/dev/null || true
    else
        sudo apt clean 2>/dev/null || true
        sudo apt autoclean 2>/dev/null || true
        sudo apt autoremove -y 2>/dev/null || true
    fi
fi

# Clear pkg cache (Termux)
if command -v pkg >/dev/null 2>&1; then
    log "Cleaning pkg cache..."
    pkg clean 2>/dev/null || true
fi

# Clear pip cache
if command -v pip >/dev/null 2>&1; then
    log "Clearing pip cache..."
    pip cache purge 2>/dev/null || true
fi

# Clear npm cache
if command -v npm >/dev/null 2>&1; then
    log "Clearing npm cache..."
    npm cache clean --force 2>/dev/null || true
fi

# Clear yarn cache  
if command -v yarn >/dev/null 2>&1; then
    log "Clearing yarn cache..."
    yarn cache clean 2>/dev/null || true
fi

# 2. TEMPORARY FILES CLEANUP
header "2. Temporary Files Cleanup"

# System temp directories
log "Clearing system temporary files..."
for temp_dir in /tmp /var/tmp ~/.tmp ~/.cache; do
    if [ -d "$temp_dir" ]; then
        log "Clearing $temp_dir..."
        if [ "$IS_ROOT" = true ] || [[ "$temp_dir" == ~/.* ]]; then
            find "$temp_dir" -type f -atime +1 -delete 2>/dev/null || true
            find "$temp_dir" -empty -type d -delete 2>/dev/null || true
        else
            sudo find "$temp_dir" -type f -atime +1 -delete 2>/dev/null || true
            sudo find "$temp_dir" -empty -type d -delete 2>/dev/null || true
        fi
    fi
done

# User-specific caches
log "Clearing user caches..."
rm -rf ~/.cache/* 2>/dev/null || true
rm -rf ~/.thumbnails/* 2>/dev/null || true
rm -rf ~/.local/share/Trash/* 2>/dev/null || true

# Browser caches
log "Clearing browser caches..."
rm -rf ~/.mozilla/firefox/*/Cache* 2>/dev/null || true
rm -rf ~/.cache/google-chrome* 2>/dev/null || true
rm -rf ~/.cache/chromium* 2>/dev/null || true
rm -rf ~/.config/google-chrome/*/Cache* 2>/dev/null || true

# 3. MEMORY OPTIMIZATION
header "3. Memory Optimization"

# Drop caches (requires root)
if [ "$IS_ROOT" = true ]; then
    log "Dropping system caches..."
    sync
    echo 3 > /proc/sys/vm/drop_caches
elif sudo -n true 2>/dev/null; then
    log "Dropping system caches with sudo..."
    sync
    sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
fi

# Clear swap (if available)
log "Optimizing swap..."
if [ -f /proc/swaps ] && grep -q "/dev" /proc/swaps; then
    if [ "$IS_ROOT" = true ]; then
        swapoff -a 2>/dev/null || true
        swapon -a 2>/dev/null || true
    elif sudo -n true 2>/dev/null; then
        sudo swapoff -a 2>/dev/null || true
        sudo swapon -a 2>/dev/null || true
    fi
fi

# 4. PROCESS CLEANUP
header "4. Process Cleanup"

# Kill memory-heavy processes (be careful with NetHunter tools)
log "Identifying memory-heavy processes..."
ps aux --sort=-%mem | head -10

# Kill common memory hogs (excluding essential NetHunter tools)
log "Stopping non-essential services..."
for service in apache2 mysql postgresql redis-server mongodb; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        warn "Stopping $service..."
        if [ "$IS_ROOT" = true ]; then
            systemctl stop "$service" 2>/dev/null || true
        else
            sudo systemctl stop "$service" 2>/dev/null || true
        fi
    fi
done

# 5. LOG CLEANUP
header "5. Log Cleanup"

# System logs
if [ "$IS_ROOT" = true ]; then
    log "Clearing system logs..."
    journalctl --vacuum-time=1d 2>/dev/null || true
    find /var/log -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true
    find /var/log -name "*.log.*" -delete 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    log "Clearing system logs with sudo..."
    sudo journalctl --vacuum-time=1d 2>/dev/null || true
    sudo find /var/log -name "*.log" -type f -exec truncate -s 0 {} \; 2>/dev/null || true
    sudo find /var/log -name "*.log.*" -delete 2>/dev/null || true
fi

# User logs
log "Clearing user logs..."
rm -rf ~/.xsession-errors* 2>/dev/null || true
rm -rf ~/.local/share/xorg/* 2>/dev/null || true

# 6. FILESYSTEM OPTIMIZATION
header "6. Filesystem Optimization"

# Remove old kernels (Ubuntu/Debian)
if command -v apt >/dev/null 2>&1; then
    log "Removing old kernels..."
    if [ "$IS_ROOT" = true ]; then
        apt autoremove --purge -y 2>/dev/null || true
    else
        sudo apt autoremove --purge -y 2>/dev/null || true
    fi
fi

# Trim filesystem (SSD optimization)
log "Trimming filesystem..."
if [ "$IS_ROOT" = true ]; then
    fstrim -av 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    sudo fstrim -av 2>/dev/null || true
fi

# 7. ZRAM SETUP (if not already configured)
header "7. ZRAM Setup"

if ! lsmod | grep -q zram; then
    log "Setting up ZRAM for compressed memory..."
    if [ "$IS_ROOT" = true ]; then
        modprobe zram 2>/dev/null || true
        echo 512M > /sys/block/zram0/disksize 2>/dev/null || true
        mkswap /dev/zram0 2>/dev/null || true
        swapon /dev/zram0 2>/dev/null || true
    elif sudo -n true 2>/dev/null; then
        sudo modprobe zram 2>/dev/null || true
        sudo sh -c 'echo 512M > /sys/block/zram0/disksize' 2>/dev/null || true
        sudo mkswap /dev/zram0 2>/dev/null || true
        sudo swapon /dev/zram0 2>/dev/null || true
    fi
else
    log "ZRAM already configured"
fi

# 8. KERNEL PARAMETER TUNING
header "8. Kernel Parameter Tuning"

# Optimize for low memory systems
if [ "$IS_ROOT" = true ]; then
    log "Tuning kernel parameters for low memory..."
    sysctl -w vm.swappiness=10 2>/dev/null || true
    sysctl -w vm.vfs_cache_pressure=50 2>/dev/null || true
    sysctl -w vm.dirty_ratio=15 2>/dev/null || true
    sysctl -w vm.dirty_background_ratio=5 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    log "Tuning kernel parameters with sudo..."
    sudo sysctl -w vm.swappiness=10 2>/dev/null || true
    sudo sysctl -w vm.vfs_cache_pressure=50 2>/dev/null || true
    sudo sysctl -w vm.dirty_ratio=15 2>/dev/null || true
    sudo sysctl -w vm.dirty_background_ratio=5 2>/dev/null || true
fi

# 9. PROJECT-SPECIFIC CLEANUP
header "9. Project-Specific Cleanup"

# Clean Node.js projects
log "Cleaning Node.js project dependencies..."
find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name ".npm" -type d -prune -exec rm -rf {} + 2>/dev/null || true

# Clean Python cache
log "Cleaning Python cache..."
find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name ".pytest_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true

# Clean build artifacts
log "Cleaning build artifacts..."
find . -name "build" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name "dist" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name ".eggs" -type d -prune -exec rm -rf {} + 2>/dev/null || true

# 10. FINAL SYSTEM STATE
header "10. Final System State"
show_memory

# Summary
header "Cleanup Summary"
log "Deep cleanup completed!"
log "Recommendations:"
log "  1. Reboot your system for maximum effect"
log "  2. Consider reducing background services"
log "  3. Use 'htop' to monitor resource usage"
log "  4. Run this script weekly for maintenance"

# Optional: Force garbage collection
log "Forcing final memory cleanup..."
sync
if [ "$IS_ROOT" = true ]; then
    echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches' 2>/dev/null || true
fi

header "Done!"
echo -e "${GREEN}System cleanup completed. Consider rebooting for maximum effect.${NC}"