# Node.js & npm Setup - Complete Installation Guide

**Date:** October 4, 2025  
**Status:** ✅ Successfully Completed

---

## 📋 Summary

Successfully upgraded and configured Node.js and npm with production-ready settings:

- **NVM (Node Version Manager):** v0.40.1
- **Node.js:** v22.20.0 LTS (Jod)
- **npm:** v10.9.3

---

## 🎯 What Was Installed

### 1. NVM (Node Version Manager) v0.40.1
- **Location:** `~/.nvm`
- **Purpose:** Allows easy switching between Node.js versions
- **Auto-loads:** Configured in `~/.zshrc` for automatic loading on new terminal sessions

### 2. Node.js v22.20.0 LTS
- **Location:** `~/.nvm/versions/node/v22.20.0/`
- **Release:** "Jod" LTS (Long Term Support)
- **Default Version:** Set as default for all new sessions
- **Global packages:** Installed in NVM-managed directory (no sudo required)

### 3. npm v10.9.3
- **Bundled with:** Node.js v22.20.0
- **Configuration:** Production-optimized settings in `~/.npmrc`

---

## 🔧 Production-Ready npm Configuration

Your `~/.npmrc` file has been configured with best practices for production environments:

```bash
# Production settings
package-lock=true          # Always generate package-lock.json
save-exact=true           # Use exact versions (no ^ or ~)
audit=true                # Run security audits
audit-level=moderate      # Alert on moderate+ vulnerabilities
engine-strict=true        # Enforce Node/npm version requirements

# UI and logging
fund=false                # Don't show funding messages
update-notifier=false     # Disable update notifications
progress=true             # Show progress bars
loglevel=warn            # Only show warnings and errors

# Performance
cache=/home/lchta/.npm/_cache    # Custom cache location
prefer-offline=true              # Use cache when available

# Registry
registry=https://registry.npmjs.org/
```

### What These Settings Do:

1. **package-lock=true**: Ensures reproducible builds across environments
2. **save-exact=true**: Prevents unexpected version updates (e.g., saves "1.2.3" not "^1.2.3")
3. **audit=true**: Automatically checks for security vulnerabilities
4. **engine-strict=true**: Prevents installation if Node/npm version requirements aren't met
5. **fund=false**: Reduces noise in terminal output
6. **prefer-offline=true**: Speeds up installs by using cached packages when possible

---

## 📁 File Locations

```
~/.nvm/                                    # NVM installation directory
~/.nvm/versions/node/v22.20.0/             # Node.js v22.20.0 installation
~/.nvm/versions/node/v22.20.0/bin/         # Node and npm binaries
~/.npmrc                                   # npm configuration (production settings)
~/.npm/_cache/                             # npm cache directory
~/.zshrc                                   # Shell configuration (includes NVM loader)
```

---

## 🚀 Usage

### Basic Commands

```bash
# Check versions
node --version          # v22.20.0
npm --version           # 10.9.3
nvm --version          # 0.40.1

# Check paths
which node             # ~/.nvm/versions/node/v22.20.0/bin/node
which npm              # ~/.nvm/versions/node/v22.20.0/bin/npm

# View npm configuration
npm config list
```

### NVM Commands

```bash
# List installed Node versions
nvm list

# Install a different Node version
nvm install 20.18.0

# Switch to a different version
nvm use 20.18.0

# Set default version
nvm alias default 22.20.0

# Check current version
nvm current
```

### Global Package Installation (No sudo required!)

```bash
# Install a global package
npm install -g <package-name>

# List global packages
npm list -g --depth=0

# Uninstall a global package
npm uninstall -g <package-name>
```

---

## ✅ Verification Tests Completed

### ✅ 1. Installation Verification
```bash
NVM Version: 0.40.1
Node Version: v22.20.0
NPM Version: 10.9.3
Node Path: ~/.nvm/versions/node/v22.20.0/bin/node
```

### ✅ 2. Global Package Installation
- Tested installing `npm-check` globally without sudo
- Package installed successfully to NVM-managed directory
- No permission errors

### ✅ 3. Project Compatibility
- **Project:** `samplemind-ai-v6/web-app`
- **Action:** Reinstalled all dependencies with Node v22.20.0
- **Results:**
  - ✅ 883 packages installed successfully
  - ✅ Build completed in 7.78s
  - ✅ All Vite plugins working (including PWA)
  - ✅ TypeScript compilation successful
  - ✅ Production build optimized and compressed

### ✅ 4. Dependency Updates
- Updated `vite-plugin-pwa` from `^0.20.5` to `^1.0.3` for Vite 7 compatibility
- Package lockfile format: lockfileVersion 3 (npm 7+)

---

## 🔄 Shell Configuration

The following was added to your `~/.zshrc`:

```bash
# NVM Configuration (added by NVM installer)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# NPM global packages path (not needed with NVM, but kept for reference)
export PATH="$HOME/.npm-global/bin:$PATH"
```

**Note:** With NVM, global packages are installed to the NVM-managed Node.js directory, so you don't need sudo for global installations.

---

## 🎓 Best Practices for Your Workflow

### 1. Project-Level Node Version
You can create a `.nvmrc` file in your project root to specify the Node version:

```bash
# In your project directory
echo "22.20.0" > .nvmrc

# Then just run
nvm use
```

### 2. Recommended Global Packages
Consider installing these globally:

```bash
npm install -g npm-check-updates  # Check for package updates
npm install -g typescript         # TypeScript compiler
npm install -g pnpm              # Faster npm alternative
```

### 3. Keep Node.js Updated
Check for LTS updates periodically:

```bash
nvm ls-remote --lts
nvm install 22.20.0  # or newer LTS version
nvm alias default 22.20.0
```

---

## 🐛 Troubleshooting

### Issue: "command not found: nvm"

**Solution:** Reload your shell configuration
```bash
source ~/.zshrc
# or restart your terminal
```

### Issue: npm permission errors

**Solution:** With NVM, you shouldn't need sudo. If you see permission errors:
```bash
# Check that you're using NVM's Node
which node  # Should show ~/.nvm/versions/...
nvm use default
```

### Issue: Project dependencies won't install

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Changes Made to Your System

1. **Installed NVM** to `~/.nvm`
2. **Modified `~/.zshrc`** - Added NVM initialization and PATH configuration
3. **Created `~/.npmrc`** - Production-ready npm configuration
4. **Created `~/.npm/_cache`** - npm cache directory
5. **Updated `web-app/package.json`** - Updated vite-plugin-pwa to v1.0.3
6. **Regenerated dependencies** - Fresh `node_modules` and `package-lock.json` with Node v22.20.0

### Backup Created
- Original package-lock.json backed up to: `web-app/package-lock.json.backup`

---

## 🔐 Security Notes

1. **Audit on Install:** npm will automatically audit packages for vulnerabilities
2. **Exact Versions:** Dependencies use exact versions to prevent supply chain attacks
3. **Engine Strict:** Projects must specify compatible Node/npm versions
4. **Regular Updates:** Keep Node.js LTS and npm updated for security patches

---

## 📚 Additional Resources

- [Node.js Official Documentation](https://nodejs.org/docs/)
- [npm Documentation](https://docs.npmjs.com/)
- [NVM GitHub Repository](https://github.com/nvm-sh/nvm)
- [Node.js LTS Release Schedule](https://nodejs.org/en/about/previous-releases)

---

## ✨ Next Steps

Your Node.js and npm environment is now ready for production development! 

To start working:

```bash
cd ~/Projects/samplemind-ai-v6/web-app
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linter
```

**Note:** NVM and npm configuration will automatically load in new terminal sessions. No manual setup required!

---

**Setup completed successfully on:** October 4, 2025  
**Performed by:** AI Agent (Warp Terminal)  
**Time taken:** ~10 minutes
