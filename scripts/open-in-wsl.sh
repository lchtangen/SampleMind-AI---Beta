#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# scripts/open-in-wsl.sh — Open SampleMind AI in VS Code WSL Remote
#
# This script:
#   1. Detects whether it's running inside WSL or Windows
#   2. If in WSL: ensures deps are installed, then opens VS Code here
#   3. If in Windows (Git Bash / PowerShell): clones into WSL and opens
#
# Usage:
#   bash scripts/open-in-wsl.sh                    # auto-detect
#   bash scripts/open-in-wsl.sh --setup-only       # just set up WSL env
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_URL="https://github.com/lchtangen/SampleMind-AI---Beta.git"
WSL_PROJECT_DIR="\$HOME/projects/SampleMind-AI---Beta"
PYTHON_VERSION="3.12"

# ── Helpers ───────────────────────────────────────────────────────────────────

log()  { printf "\033[36m[wsl-setup]\033[0m %s\n" "$*"; }
warn() { printf "\033[33m[wsl-setup]\033[0m %s\n" "$*"; }
err()  { printf "\033[31m[wsl-setup]\033[0m %s\n" "$*" >&2; }

is_wsl() {
  [[ -f /proc/version ]] && grep -qi "microsoft\|wsl" /proc/version 2>/dev/null
}

check_command() {
  command -v "$1" &>/dev/null
}

# ── WSL Environment Setup ────────────────────────────────────────────────────

setup_wsl_env() {
  log "Setting up WSL development environment..."

  # System packages
  if check_command apt-get; then
    log "Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
      build-essential curl git libffi-dev libsndfile1 ffmpeg \
      python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev \
      2>/dev/null || warn "Some system packages may have failed to install"
  fi

  # uv (Python package manager)
  if ! check_command uv; then
    log "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="\$HOME/.local/bin:\$PATH"
  fi

  # Node.js via nvm (for Next.js frontend)
  if ! check_command node; then
    log "Installing Node.js 22 via nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="\$HOME/.nvm"
    # shellcheck disable=SC1091
    [ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh"
    nvm install 22
  fi

  log "✅ WSL environment ready"
}

# ── Clone / Update Repo ──────────────────────────────────────────────────────

ensure_repo() {
  local target_dir="$1"

  if [[ -d "$target_dir/.git" ]]; then
    log "Repository found at $target_dir — pulling latest..."
    cd "$target_dir"
    git pull --ff-only || warn "Pull failed; working on current state"
  else
    log "Cloning repository into $target_dir..."
    mkdir -p "$(dirname "$target_dir")"
    git clone "$REPO_URL" "$target_dir"
    cd "$target_dir"
  fi
}

# ── Install Project Dependencies ─────────────────────────────────────────────

install_deps() {
  log "Installing Python dependencies..."
  if check_command uv; then
    uv sync 2>/dev/null || uv pip install -e ".[dev]" 2>/dev/null || {
      warn "uv install failed, trying pip..."
      python${PYTHON_VERSION} -m pip install -e ".[dev]" 2>/dev/null || true
    }
  else
    python${PYTHON_VERSION} -m pip install -e ".[dev]" 2>/dev/null || true
  fi

  # Frontend deps (optional — prefer pnpm, fall back to npm)
  if [[ -f "apps/web/package.json" ]]; then
    if check_command pnpm; then
      log "Installing frontend dependencies (pnpm)..."
      cd apps/web && pnpm install --frozen-lockfile 2>/dev/null || true
      cd ../..
    elif check_command npm; then
      log "Installing frontend dependencies (npm)..."
      cd apps/web && npm install --legacy-peer-deps 2>/dev/null || true
      cd ../..
    fi
  fi

  log "✅ Dependencies installed"
}

# ── Open in VS Code ──────────────────────────────────────────────────────────

open_vscode() {
  local project_dir="$1"

  if check_command code; then
    log "Opening VS Code in $project_dir..."
    code "$project_dir"
  else
    warn "VS Code CLI ('code') not found in PATH."
    warn "Install it: VS Code → Cmd Palette → 'Shell Command: Install code in PATH'"
    warn "Then run:  code $project_dir"
  fi
}

open_vscode_wsl_from_windows() {
  local wsl_path="$1"
  log "Opening VS Code with WSL Remote..."
  # From Windows, use code --remote wsl+Ubuntu <path>
  code --remote wsl+Ubuntu "$wsl_path" 2>/dev/null || {
    warn "Could not open via 'code --remote'. Try manually:"
    warn "  1. Open VS Code"
    warn "  2. Ctrl+Shift+P → 'Remote-WSL: Open Folder in WSL...'"
    warn "  3. Navigate to: $wsl_path"
  }
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  local setup_only=false
  [[ "${1:-}" == "--setup-only" ]] && setup_only=true

  if is_wsl; then
    # Running inside WSL
    local repo_dir
    repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    log "Detected: WSL environment"
    setup_wsl_env
    install_deps

    if [[ "$setup_only" == true ]]; then
      log "✅ Setup complete. Run 'code .' to open in VS Code."
      return 0
    fi

    open_vscode "$repo_dir"
    log "✅ VS Code opened with WSL Remote"
    log ""
    log "Quick start:"
    log "  make dev          — Start FastAPI dev server"
    log "  make test-unit    — Run unit tests"
    log "  make lint         — Lint check"
    log "  Ctrl+Shift+P → 'Tasks: Run Task' → 'Sync with Agent Branch'"

  else
    # Running from Windows (Git Bash / PowerShell)
    log "Detected: Windows environment"
    log "Setting up repo in WSL..."

    # Expand WSL_PROJECT_DIR for the WSL side
    local wsl_dir
    wsl_dir=$(wsl bash -c "echo $WSL_PROJECT_DIR" 2>/dev/null || echo "$WSL_PROJECT_DIR")

    # Run setup in WSL
    wsl bash -c "
      set -e
      export REPO_URL='$REPO_URL'
      export TARGET='$wsl_dir'

      # Clone or pull
      if [ -d \"\$TARGET/.git\" ]; then
        cd \"\$TARGET\" && git pull --ff-only
      else
        mkdir -p \"\$(dirname \"\$TARGET\")\"
        git clone \"\$REPO_URL\" \"\$TARGET\"
      fi

      # Run the WSL setup from inside WSL
      cd \"\$TARGET\"
      if [ -f scripts/open-in-wsl.sh ]; then
        bash scripts/open-in-wsl.sh --setup-only
      fi
    " || err "WSL setup encountered errors"

    if [[ "$setup_only" != true ]]; then
      open_vscode_wsl_from_windows "$wsl_dir"
    fi
  fi
}

main "$@"
