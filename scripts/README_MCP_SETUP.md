# MCP Server Setup Scripts

This directory contains automated scripts for setting up and verifying all 29 MCP servers in the SampleMind AI project.

## Scripts

### 1. `setup-copilot-mcp-complete.sh`
**Purpose:** One-command installation of all 29 MCP servers

**Usage:**
```bash
cd ~/Projects/Samplemind-AI
./scripts/setup-copilot-mcp-complete.sh
```

**What It Does:**
- ✅ Checks prerequisites (Node.js 18+, Python 3.11+, npx, git)
- ✅ Installs 15 npm-based MCP server packages
- ✅ Verifies package installations
- ✅ Checks/creates .env file
- ✅ Sets up tools/mcp-servers directory
- ✅ Provides next steps for configuration

**Requirements:**
- Node.js >= 18.0.0
- Python >= 3.11
- npm/npx installed
- Git installed
- Internet connection

**Output:**
- Colored status messages (✓ success, ✗ error, ⚠ warning, ℹ info)
- Installation progress for each package
- Verification results
- Next step instructions

---

### 2. `verify-mcp-servers.sh` (in tools/)
**Purpose:** Comprehensive verification of all 29 MCP servers

**Usage:**
```bash
cd ~/Projects/Samplemind-AI
./tools/verify-mcp-servers.sh
```

**Tests Performed:**
1. **NPM MCP Servers** - Tests 15 npm packages
2. **Environment Variables** - Checks .env configuration
3. **Python MCP Servers** - Verifies 5 custom servers
4. **VS Code Configuration** - Validates settings.json
5. **Documentation** - Confirms all docs exist
6. **Network Connectivity** - Tests API endpoints
7. **Database Connectivity** - Checks MongoDB/Redis

**Exit Codes:**
- `0` - All tests passed
- `1` - Some tests failed

**Output:**
- Test results with PASS/FAIL/SKIP status
- Total test count and pass rate
- Summary with recommendations

---

## Quick Start

### Complete Setup (New Installation)

```bash
# 1. Run setup script
./scripts/setup-copilot-mcp-complete.sh

# 2. Add API keys to .env
# Get Brave API key from: https://brave.com/search/api

# 3. Verify setup
./tools/verify-mcp-servers.sh

# 4. Reload VS Code
# Ctrl+Shift+P → Developer: Reload Window
```

### Verification Only (Existing Installation)

```bash
./tools/verify-mcp-servers.sh
```

---

## Troubleshooting

### Script Permission Denied

```bash
chmod +x scripts/setup-copilot-mcp-complete.sh
chmod +x tools/verify-mcp-servers.sh
```

### npm Install Fails

```bash
# Clear npm cache
npm cache clean --force

# Try installing packages individually
npx -y @modelcontextprotocol/server-brave-search --help
```

### Python Version Issues

```bash
# Check Python version
python3 --version

# Use specific Python version if needed
python3.11 --version
```

### Environment Variables Not Loading

```bash
# Ensure .env file has no syntax errors
cat .env | grep -v "^#" | grep "="

# Check for trailing spaces
sed -i 's/[[:space:]]*$//' .env
```

---

## Files Created by Setup Script

- `.env` (if not exists, copied from .env.example)
- `tools/mcp-servers/` directory
- npm global packages for MCP servers

## Files Checked by Verification Script

- `.env` (required environment variables)
- `.vscode/settings.json` (MCP server config)
- `.github/copilot-instructions.md`
- `.github/copilot-prompts/*.prompt.md`
- `docs/COPILOT_MCP_BRAVE_CONFIGURATION_GUIDE.md`
- `tools/mcp-servers/*.py` (custom Python servers)

---

## Advanced Usage

### Dry Run (Setup Script)

```bash
# View what would be installed without actually installing
DRY_RUN=1 ./scripts/setup-copilot-mcp-complete.sh
```

### Verbose Output (Verification Script)

```bash
# Show detailed test output
DEBUG=1 ./tools/verify-mcp-servers.sh
```

### Test Specific Category

```bash
# Modify verification script to run only specific tests
# Comment out unwanted test functions in main()
```

---

## Related Documentation

- [Complete Configuration Guide](../docs/COPILOT_MCP_BRAVE_CONFIGURATION_GUIDE.md)
- [VS Code MCP Setup](../docs/VSCODE_MCP_SETUP_GUIDE.md)
- [MCP Servers Guide](../docs/MCP_SERVERS_VSCODE_GUIDE.md)
- [Kilo Code Master Prompt](../docs/KILO_CODE_MASTER_PROMPT.md)

---

**Version:** 1.0.0 Phoenix Beta  
**Last Updated:** October 6, 2025  
**Status:** Production-Ready
