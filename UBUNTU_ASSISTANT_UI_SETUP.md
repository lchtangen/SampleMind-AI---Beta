# 🐧 assistant-ui Setup Guide for Ubuntu

**Complete installation and configuration guide for Ubuntu 20.04, 22.04, and 24.04**

**Date:** January 6, 2025
**Status:** ✅ Packages Already Installed
**Platform:** Ubuntu Linux

---

## 📋 Prerequisites Check

### 1. System Requirements
```bash
# Check Ubuntu version
lsb_release -a

# Check Node.js (need 18+)
node --version

# Check npm
npm --version

# Check Python (need 3.11+)
python3 --version
```

**Required Versions:**
- Ubuntu: 20.04+ (tested on 22.04 and 24.04)
- Node.js: 18.0.0 or higher
- npm: 9.0.0 or higher
- Python: 3.11 or higher

---

## ✅ Installation Status

### Packages Already Installed
```bash
cd /home/lchta/Projects/Samplemind-AI/web-app

# Check installation
npm list | grep -E "assistant-ui|anthropic|idb-keyval|lz-string"

# Output shows:
# ✅ @assistant-ui/react@0.11.28
# ✅ @ai-sdk/anthropic@2.0.23
# ✅ idb-keyval@6.2.2
# ✅ lz-string@1.5.0
```

**All required packages are installed!** 🎉

---

## 🔧 Ubuntu-Specific Configuration

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install build essentials (for native modules)
sudo apt install -y build-essential

# Install libvips (for image processing, if needed)
sudo apt install -y libvips-dev

# Install git (if not already installed)
sudo apt install -y git
```

### Step 2: Python Backend Setup

```bash
# Install Python 3.11 (if not already installed)
sudo apt install -y python3.11 python3.11-venv python3-pip

# Create virtual environment
cd /home/lchta/Projects/Samplemind-AI
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install anthropic fastapi uvicorn[standard] pydantic loguru python-dotenv

# Or install from requirements
pip install -r requirements.txt
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor (nano, vim, or code)
nano .env

# Add your API keys:
# ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
# BRAVE_API_KEY=your-brave-api-key-here
# VITE_API_BASE_URL=http://localhost:8000
```

**Quick edit with sed (replace YOUR-KEY with actual key):**
```bash
sed -i 's/your-anthropic-api-key-here/sk-ant-api03-YOUR-KEY-HERE/' .env
sed -i 's/http:\/\/localhost:8000/http:\/\/localhost:8000/' .env
```

---

## 🚀 Running on Ubuntu

### Option 1: Using Terminal Multiplexer (tmux)

```bash
# Install tmux if not present
sudo apt install -y tmux

# Create new tmux session
tmux new -s samplemind

# Split window horizontally (Ctrl+B then ")
# In first pane (backend):
cd /home/lchta/Projects/Samplemind-AI
source venv/bin/activate
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# Switch to second pane (Ctrl+B then arrow key)
# In second pane (frontend):
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev

# Detach from tmux: Ctrl+B then D
# Reattach later: tmux attach -t samplemind
```

### Option 2: Using systemd Services (Production)

**Create backend service:**
```bash
sudo nano /etc/systemd/system/samplemind-backend.service
```

**Content:**
```ini
[Unit]
Description=SampleMind AI Backend
After=network.target

[Service]
Type=simple
User=lchta
WorkingDirectory=/home/lchta/Projects/Samplemind-AI
Environment="PATH=/home/lchta/Projects/Samplemind-AI/venv/bin"
ExecStart=/home/lchta/Projects/Samplemind-AI/venv/bin/uvicorn samplemind.interfaces.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Create frontend service:**
```bash
sudo nano /etc/systemd/system/samplemind-frontend.service
```

**Content:**
```ini
[Unit]
Description=SampleMind AI Frontend
After=network.target

[Service]
Type=simple
User=lchta
WorkingDirectory=/home/lchta/Projects/Samplemind-AI/web-app
ExecStart=/usr/bin/npm run dev
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable samplemind-backend
sudo systemctl enable samplemind-frontend

# Start services
sudo systemctl start samplemind-backend
sudo systemctl start samplemind-frontend

# Check status
sudo systemctl status samplemind-backend
sudo systemctl status samplemind-frontend

# View logs
sudo journalctl -u samplemind-backend -f
sudo journalctl -u samplemind-frontend -f
```

### Option 3: Using Screen (Alternative to tmux)

```bash
# Install screen
sudo apt install -y screen

# Create backend screen
screen -S backend
cd /home/lchta/Projects/Samplemind-AI
source venv/bin/activate
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
# Detach: Ctrl+A then D

# Create frontend screen
screen -S frontend
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev
# Detach: Ctrl+A then D

# List screens
screen -ls

# Reattach to backend
screen -r backend

# Reattach to frontend
screen -r frontend
```

---

## 🔒 Ubuntu Firewall Configuration

### Allow Ports (if using ufw)

```bash
# Check firewall status
sudo ufw status

# Allow backend port
sudo ufw allow 8000/tcp comment 'SampleMind Backend'

# Allow frontend port
sudo ufw allow 5173/tcp comment 'SampleMind Frontend'

# Enable firewall (if not already enabled)
sudo ufw enable

# Verify rules
sudo ufw status numbered
```

---

## 🌐 Nginx Reverse Proxy (Optional - Production)

### Install Nginx

```bash
sudo apt install -y nginx
```

### Configure Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/samplemind
```

**Content:**
```nginx
server {
    listen 80;
    server_name samplemind.local;  # or your domain

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streaming support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

**Enable site:**
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/samplemind /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Add to /etc/hosts (for local testing)
echo "127.0.0.1 samplemind.local" | sudo tee -a /etc/hosts
```

**Access at:** http://samplemind.local

---

## 📦 MCP Server Setup on Ubuntu

### Install MCP SDK

```bash
cd /home/lchta/Projects/Samplemind-AI
npm install -g @modelcontextprotocol/sdk
```

### Make MCP Server Executable

```bash
chmod +x scripts/mcp-servers/assistant-ui-docs-server.js
```

### Test MCP Server

```bash
# Run server directly
node scripts/mcp-servers/assistant-ui-docs-server.js

# Should output: "assistant-ui MCP server running on stdio"
```

### VS Code MCP Configuration (Ubuntu)

**Location:** `~/.config/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json`

```bash
# Create directory if doesn't exist
mkdir -p ~/.config/Code/User/globalStorage/kilocode.kilo-code/settings

# Edit MCP settings
nano ~/.config/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json
```

**Add assistant-ui server:**
```json
{
  "mcpServers": {
    "assistant-ui-docs": {
      "command": "node",
      "args": [
        "/home/lchta/Projects/Samplemind-AI/scripts/mcp-servers/assistant-ui-docs-server.js"
      ],
      "alwaysAllow": [
        "search_docs",
        "get_component",
        "get_runtime",
        "get_example"
      ]
    }
  }
}
```

---

## 🐧 Ubuntu Desktop Integration

### Create Desktop Entry

```bash
nano ~/.local/share/applications/samplemind-ai.desktop
```

**Content:**
```desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=SampleMind AI
Comment=AI-Powered Music Production Assistant
Exec=gnome-terminal -- bash -c 'cd /home/lchta/Projects/Samplemind-AI && source venv/bin/activate && python -m uvicorn samplemind.interfaces.api.main:app --reload & cd web-app && npm run dev; exec bash'
Icon=/home/lchta/Projects/Samplemind-AI/web-app/public/logo.png
Terminal=true
Categories=AudioVideo;Audio;Development;
Keywords=AI;Music;Audio;Production;
```

**Make executable:**
```bash
chmod +x ~/.local/share/applications/samplemind-ai.desktop
```

**Update desktop database:**
```bash
update-desktop-database ~/.local/share/applications
```

Now you can launch from Applications menu!

---

## 🔧 Troubleshooting Ubuntu-Specific Issues

### Issue 1: Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>

# Or use different port
python -m uvicorn samplemind.interfaces.api.main:app --reload --port 8001
```

### Issue 2: Permission Denied on Ports < 1024

```bash
# Don't run on privileged ports, or use authbind
sudo apt install -y authbind
```

### Issue 3: Node/npm Permission Issues

```bash
# Fix npm permissions (Ubuntu-safe method)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Issue 4: Python venv Issues

```bash
# Remove and recreate venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue 5: Can't Access from Other Devices

```bash
# Find your local IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# Run backend with 0.0.0.0
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend with --host
cd web-app
npm run dev -- --host 0.0.0.0

# Update firewall
sudo ufw allow 8000/tcp
sudo ufw allow 5173/tcp
```

---

## 📱 Access from Mobile/Tablet on Same Network

```bash
# 1. Get Ubuntu machine's IP
hostname -I | awk '{print $1}'
# Example output: 192.168.1.100

# 2. Start servers with network access
# Backend:
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (edit vite.config.ts):
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})

# 3. Access from mobile browser:
# http://192.168.1.100:5173/assistant-demo
```

---

## 🚀 Quick Start Commands (Copy-Paste Ready)

### Development Mode

```bash
# Terminal 1 - Backend
cd /home/lchta/Projects/Samplemind-AI
source venv/bin/activate
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev
```

### Using tmux (Recommended)

```bash
# One-liner to start everything
tmux new-session -d -s samplemind \; \
  send-keys 'cd /home/lchta/Projects/Samplemind-AI && source venv/bin/activate && python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000' C-m \; \
  split-window -v \; \
  send-keys 'cd /home/lchta/Projects/Samplemind-AI/web-app && npm run dev' C-m \; \
  attach-session -t samplemind
```

### Using systemd (Production)

```bash
# Start services
sudo systemctl start samplemind-backend samplemind-frontend

# Check status
sudo systemctl status samplemind-backend samplemind-frontend

# View logs
sudo journalctl -u samplemind-backend -f
```

---

## ✅ Verification Checklist

### Backend Health Check
```bash
curl http://localhost:8000/api/assistant/health
# Expected: {"status":"healthy","model":"claude-sonnet-4.5-20250514"}
```

### Frontend Access
```bash
# Open browser
xdg-open http://localhost:5173/assistant-demo

# Or from command line
curl http://localhost:5173
```

### Streaming Test
```bash
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

### MCP Server Test (in VS Code)
```
# In Kilo Code chat:
@assistant-ui-docs get example zustand
```

---

## 📊 Performance Tuning for Ubuntu

### Increase File Watchers (for npm run dev)

```bash
# Check current limit
cat /proc/sys/fs/inotify/max_user_watches

# Increase limit (temporary)
sudo sysctl fs.inotify.max_user_watches=524288

# Make permanent
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Optimize Node.js Memory

```bash
# For systems with limited RAM
export NODE_OPTIONS="--max-old-space-size=4096"

# Add to ~/.bashrc for persistence
echo 'export NODE_OPTIONS="--max-old-space-size=4096"' >> ~/.bashrc
```

---

## 🎯 Next Steps

1. ✅ **Verify Installation**
   ```bash
   npm list | grep assistant-ui
   ```

2. ✅ **Start Servers**
   ```bash
   # Use tmux one-liner above
   ```

3. ✅ **Open Demo**
   ```bash
   xdg-open http://localhost:5173/assistant-demo
   ```

4. ✅ **Test Chat**
   - Click "+ New Chat"
   - Ask: "Explain FastAPI routing"
   - Watch Claude Sonnet 4.5 respond!

---

## 📚 Additional Resources

- **Full Implementation Guide:** `/docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md`
- **Quick Start:** `/ASSISTANT_UI_QUICK_START.md`
- **MCP Setup:** `/docs/MCP_SETUP_GUIDE.md`
- **IDE Comparison:** `/docs/IDE_COMPARISON_ANALYSIS.md`

---

## 🐧 Ubuntu-Specific Tips

### Use GNOME Extensions (if on GNOME)

```bash
# Install system monitor extension
sudo apt install -y gnome-shell-extension-system-monitor

# Shows CPU/RAM usage in top bar
```

### Setup Auto-Start on Login

```bash
# Create startup script
nano ~/.config/autostart/samplemind.desktop

# Add same content as desktop entry above
# But with:
# X-GNOME-Autostart-enabled=true
```

### Monitor Logs with Logwatch

```bash
sudo apt install -y logwatch
sudo logwatch --detail high --service all --range today
```

---

**Status:** ✅ Ready for Ubuntu
**Platform:** Ubuntu 20.04+ (tested on 22.04, 24.04)
**Installation:** All packages already installed!
**Next:** Start servers and begin chatting with Claude Sonnet 4.5!

🎉 **Welcome to SampleMind AI on Ubuntu!**
