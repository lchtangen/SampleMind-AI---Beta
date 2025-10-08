# 🚀 Auto-Start Configuration - Complete Guide

**Date:** October 6, 2025  
**Project:** SampleMind AI v1.0.0 Phoenix Beta  
**Status:** ✅ Configured

---

## ✅ What Was Configured

### 1. GitHub Copilot Auto-Load (Automatic)

**File:** `.github/copilot-instructions.md`  
**Status:** 🟢 **Automatically loads on every Copilot Chat session**

✅ No manual action needed - works automatically!

### 2. MCP Servers Auto-Start

**Script:** `scripts/mcp-auto-start.sh`  
**Status:** ✅ Ready to use

All 29 MCP servers can be initialized automatically.

### 3. VS Code Auto-Start Tasks

**File:** `.vscode/tasks.json`  
**Tasks Created:**
- 🚀 Initialize Environment (runs on folder open)
- 🔄 Reload Copilot with Custom Prompt
- 🧪 Verify MCP Servers

### 4. Workspace Startup Script

**Script:** `start-workspace.sh`  
**Usage:** 
```bash
./start-workspace.sh
```

This script:
- Initializes all MCP servers
- Launches VS Code with custom settings
- Auto-loads Copilot instructions

---

## 🎯 Usage Options

### Option 1: Quick Start (Recommended)

```bash
# From project root
./start-workspace.sh
```

This will:
1. ✅ Initialize all 29 MCP servers
2. ✅ Launch VS Code
3. ✅ Auto-load GitHub Copilot custom instructions
4. ✅ Apply KILO CODE MASTER PROMPT

### Option 2: Use Shell Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
source /home/lchta/Projects/Samplemind-AI/.auto-start-alias.sh
```

Then use:
```bash
samplemind      # Start workspace
sm-start        # Alternative
sm-verify       # Verify MCP servers
```

### Option 3: Manual VS Code Task

1. Open VS Code in project
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P`
3. Type: "Tasks: Run Task"
4. Select: "🚀 SampleMind AI - Initialize Environment"

### Option 4: System Auto-Start (Linux)

Enable systemd service:

```bash
# Copy service file
mkdir -p ~/.config/systemd/user
cp .config/systemd/user/samplemind-mcp.service ~/.config/systemd/user/

# Enable service
systemctl --user enable samplemind-mcp.service

# Start service
systemctl --user start samplemind-mcp.service

# Check status
systemctl --user status samplemind-mcp.service
```

---

## 🔍 Verification

### Test GitHub Copilot Auto-Load

1. Open VS Code
2. Open Copilot Chat
3. Ask: `@workspace What is SampleMind AI?`

**Expected:** Should describe the project with tech stack details

### Test MCP Servers

```bash
cd scripts/mcp-servers
node verify-setup.js
```

**Expected:** All 29 servers should show ✅

### Test Complete Startup

```bash
./start-workspace.sh
```

**Expected:**
- MCP servers initialize
- VS Code opens
- Copilot instructions loaded
- Ready to code!

---

## 📋 What Happens Automatically

### On VS Code Launch

1. ✅ GitHub Copilot reads `.github/copilot-instructions.md`
2. ✅ Loads custom system prompt (KILO CODE MASTER)
3. ✅ MCP servers available in `github.copilot.chat.mcpServers`
4. ✅ All 29 servers ready to use

### On Copilot Chat Open

1. ✅ Custom instructions automatically applied
2. ✅ Project context loaded
3. ✅ Tech stack awareness active
4. ✅ Coding standards enforced

### MCP Servers Available

All 29 servers are auto-configured:
- Sequential thinking
- Source code access (src, tests, docs)
- AI providers (Gemini, Claude, GPT-5)
- Development tools (Git, Docker, Kubernetes)
- Databases (MongoDB, PostgreSQL, Redis)
- Productivity (Slack, Linear, Notion)

---

## 🛠️ Troubleshooting

### Copilot Not Loading Instructions

**Solution:** Instructions load automatically. No action needed.

**Verify:** File exists at `.github/copilot-instructions.md` ✅

### MCP Servers Not Working

**Solution:** Run initialization:
```bash
./scripts/mcp-auto-start.sh
```

### VS Code Task Not Running

**Solution:** Check tasks.json exists:
```bash
cat .vscode/tasks.json
```

---

## 📚 Files Created

1. ✅ `scripts/mcp-auto-start.sh` - MCP initialization
2. ✅ `.vscode/tasks.json` - Auto-start tasks
3. ✅ `start-workspace.sh` - Complete startup
4. ✅ `.auto-start-alias.sh` - Shell aliases
5. ✅ `.config/systemd/user/samplemind-mcp.service` - System service
6. ✅ `docs/AUTO_START_SETUP.md` - This documentation

---

## ✅ Summary

**Everything is configured for automatic startup!**

### Automatic Features:
- ✅ GitHub Copilot custom instructions (auto-loads)
- ✅ KILO CODE MASTER PROMPT (referenced)
- ✅ 29 MCP servers (configured)
- ✅ VS Code tasks (ready)
- ✅ Workspace startup script (created)

### To Start Working:

**Option 1 (Easiest):**
```bash
./start-workspace.sh
```

**Option 2 (Just VS Code):**
```bash
code .
```
(Copilot instructions auto-load)

**Option 3 (With Alias):**
```bash
samplemind
```

**Everything else is AUTOMATIC!** 🚀

---

**Last Updated:** October 6, 2025  
**Status:** ✅ Fully Configured
