# 🎯 SampleMind AI - Command Aliases Reference Card

**Quick access commands for your SampleMind AI v6 project**

## 🚀 Getting Started

After opening a new terminal, the aliases are automatically loaded.

**First time setup:** Already done! ✅  
**View all commands:** Type `sm-help`  
**Check status:** Type `sm-info`

---

## 📂 Navigation (Most Used)

| Command | Action |
|---------|--------|
| `sm` | Go to project root |
| `smf` | Go to frontend directory |
| `smb` | Go to backend source |
| `smapi` | Go to API code |
| `smcore` | Go to core backend code |

**Example:**
```bash
sm          # Jump to /home/lchta/Projects/samplemind-ai-v6
smf         # Jump to frontend/web
```

---

## 🚀 Starting Services (Essential)

| Command | Action |
|---------|--------|
| `sm-api` | Start FastAPI backend server |
| `sm-worker` | Start Celery background worker |
| `sm-web` | Start Next.js frontend |
| `sm-flower` | Start Flower monitoring UI |
| `sm-db-up` | Start all databases (MongoDB, Redis, ChromaDB) |

**Quick Start Workflow:**
```bash
sm-db-up       # Start databases (run once)
sm-api         # Terminal 1: Start API
sm-worker      # Terminal 2: Start worker
sm-web         # Terminal 3: Start frontend
```

**Or use the all-in-one command:**
```bash
sm-start       # Starts everything (databases + API + worker + frontend)
```

---

## ⏹️ Stopping Services

| Command | Action |
|---------|--------|
| `sm-stop` | Stop API and Celery workers |
| `sm-db-down` | Stop all databases |
| Ctrl+C | Stop service in current terminal |

```bash
sm-stop        # Stop backend services
sm-db-down     # Stop databases
```

---

## 🔍 Monitoring & Status

| Command | Action |
|---------|--------|
| `sm-info` | Show all services and URLs |
| `sm-ps` | Show running processes |
| `sm-health` | Check API health (JSON) |
| `sm-ports` | Show which ports are in use |
| `sm-logs` | View all logs |

**Check what's running:**
```bash
sm-info        # Quick overview
sm-ps          # Detailed process list
sm-health      # API health check
```

---

## 💾 Database Management

| Command | Action |
|---------|--------|
| `sm-db-up` | Start all databases |
| `sm-db-down` | Stop all databases |
| `sm-db-status` | Check database status |
| `sm-mongo` | Open MongoDB shell |
| `sm-redis` | Open Redis CLI |

**Database operations:**
```bash
sm-db-up       # Start databases
sm-db-status   # Check if running
sm-mongo       # Access MongoDB
```

---

## 🌐 Open in Browser

| Command | Action |
|---------|--------|
| `sm-frontend-ui` | Open http://localhost:3000 |
| `sm-api-docs` | Open http://localhost:8000/api/docs |
| `sm-flower-ui` | Open http://localhost:5555 |

```bash
sm-frontend-ui # Opens your app in browser
sm-api-docs    # Opens API documentation
```

---

## 📚 Documentation

| Command | Action |
|---------|--------|
| `sm-help` | Show all available commands |
| `sm-status` | Show project status (first 50 lines) |
| `sm-readme` | View full status document |
| `smdocs` | List all documentation files |

```bash
sm-help        # Show this help
sm-status      # Quick project status
```

---

## 🛠 Development Tools

| Command | Action |
|---------|--------|
| `sm-venv` | Activate Python virtual environment |
| `sm-python` | Run Python with venv activated |
| `sm-npm` | Run npm commands in frontend |
| `sm-build` | Build frontend for production |
| `sm-lint` | Check frontend code quality |

**Python development:**
```bash
sm-venv        # Activate virtual environment
sm-python      # Run Python
sm-pip install package-name  # Install Python package
```

**Frontend development:**
```bash
sm-npm install     # Install npm packages
sm-build          # Build for production
sm-lint           # Check code
```

---

## 🧪 Testing

| Command | Action |
|---------|--------|
| `sm-test` | Run Python tests |
| `sm-test-cov` | Run tests with coverage |
| `sm-format` | Format Python code (black + isort) |
| `sm-check` | Type check with mypy |

---

## 📝 Git Shortcuts

| Command | Action |
|---------|--------|
| `sm-status-git` | Git status |
| `sm-diff` | Git diff |
| `sm-log` | Last 10 commits |
| `sm-commit "message"` | Add all and commit |
| `sm-push` | Push to remote |

```bash
sm-status-git          # Check git status
sm-commit "Add feature"  # Commit changes
sm-push                # Push to remote
```

---

## 🔧 Utility Functions

| Function | Action |
|---------|--------|
| `sm-backup` | Create backup of project |
| `sm-search "term"` | Search in project files |
| `sm-clean` | Clean cache and build files |

```bash
sm-backup              # Create timestamped backup
sm-search "api_key"    # Search for "api_key" in code
sm-clean               # Clean cache
```

---

## 🎯 Common Workflows

### 1. Start Fresh Development Session
```bash
sm                # Go to project
sm-db-up          # Start databases
sm-api &          # Start API in background
sm-worker &       # Start worker in background
sm-web            # Start frontend (foreground)
```

### 2. Check Everything is Running
```bash
sm-info           # Overview
sm-health         # Check API
sm-frontend-ui    # Open app
```

### 3. View Logs When Debugging
```bash
sm-logs           # All logs
sm-api-logs       # Just API logs
sm-worker-logs    # Just worker logs
```

### 4. Stop Everything
```bash
sm-stop           # Stop backend
Ctrl+C            # Stop frontend
sm-db-down        # Stop databases (optional)
```

### 5. Quick Restart
```bash
sm-restart        # Stop all + restart everything
```

---

## 🎨 Advanced: Tmux Session

**Run everything in one tmux session:**
```bash
sm-tmux           # Start all services in tmux
# Ctrl+B then D to detach
sm-tmux-kill      # Kill tmux session
```

---

## 💡 Pro Tips

1. **Tab Completion**: Type `sm-` then press TAB to see all available commands
2. **Command History**: Use ↑ arrow or Ctrl+R to search command history
3. **Quick Status**: Run `sm-quick-status` anytime to see what's running
4. **Chaining Commands**: `sm && sm-db-up && sm-api` (run multiple commands)
5. **Background Jobs**: Add `&` at end to run in background: `sm-api &`

---

## 🆘 Troubleshooting

**If aliases don't work:**
```bash
source ~/.zshrc    # Reload shell configuration
```

**If services won't start:**
```bash
sm-ps              # Check what's running
sm-stop            # Stop everything
sm-db-restart      # Restart databases
```

**If port is in use:**
```bash
sm-ports           # See what's using ports
sm-stop            # Kill services
```

---

## 📍 Quick URL Reference

When services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Flower (monitoring)**: http://localhost:5555
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

---

## 🔑 Remember These 5 Commands

```bash
sm-help      # Show all commands
sm-info      # Check what's running
sm-db-up     # Start databases
sm-api       # Start API
sm-web       # Start frontend
```

---

**That's it! You're ready to go! 🚀**

Type `sm-help` anytime for a quick reminder of commands.

---

**Print this reference:**
```bash
cat /home/lchta/Projects/samplemind-ai-v6/ALIASES_REFERENCE.md
```

**Or view it in your browser:**
```bash
sm && cat ALIASES_REFERENCE.md | less
```
