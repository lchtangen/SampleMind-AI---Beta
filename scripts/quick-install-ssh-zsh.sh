#!/bin/bash
# Quick NetHunter SSH Zsh Installation
# Run this in your NetHunter SSH session from Termux

echo "🚀 Installing Oh My Zsh + Spaceship for NetHunter SSH..."

# Download and run the installation script
curl -fsSL https://raw.githubusercontent.com/lchtangen/samplemind-ai-v2-phoenix/performance-upgrade-v7/scripts/setup-nethunter-ssh-zsh.sh | bash

echo "✅ Installation complete! Restart your SSH session or run: source ~/.zshrc"