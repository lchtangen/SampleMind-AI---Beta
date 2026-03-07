#!/usr/bin/env bash
# =============================================================================
# fix-git-auth.sh — Fix SSH credential issues when pushing to GitHub
#
# Run this when you see:
#   "Permission denied (publickey)"
#   "git@github.com: Permission denied"
#   "Could not read from remote repository"
#
# Usage:
#   bash scripts/setup/fix-git-auth.sh
#   bash scripts/setup/fix-git-auth.sh --https    # non-interactive: switch to HTTPS
#   bash scripts/setup/fix-git-auth.sh --ssh-agent # non-interactive: load SSH key into agent
# =============================================================================

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}ℹ${RESET}  $*"; }
success() { echo -e "${GREEN}✅${RESET} $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET}  $*"; }
error()   { echo -e "${RED}❌${RESET} $*" >&2; }
header()  { echo -e "\n${BOLD}${CYAN}$*${RESET}\n"; }

# ── Parse flags ──────────────────────────────────────────────────────────────
MODE=""
for arg in "$@"; do
  case "$arg" in
    --https)      MODE="https" ;;
    --ssh-agent)  MODE="ssh-agent" ;;
    --help|-h)
      echo "Usage: bash scripts/setup/fix-git-auth.sh [--https|--ssh-agent]"
      echo "  --https      Switch remote from SSH to HTTPS (recommended, no key needed)"
      echo "  --ssh-agent  Load your SSH private key into ssh-agent instead"
      exit 0 ;;
  esac
done

# ── Detect remote URL ─────────────────────────────────────────────────────────
REMOTE_URL="$(git remote get-url origin 2>/dev/null || echo '')"

if [[ -z "$REMOTE_URL" ]]; then
  error "No 'origin' remote found. Add one with:"
  echo "  git remote add origin https://github.com/lchtangen/SampleMind-AI---Beta.git"
  exit 1
fi

header "🔐 SampleMind — Git Authentication Fix"
info "Current remote URL: ${BOLD}$REMOTE_URL${RESET}"

# Determine if remote is SSH or HTTPS
if [[ "$REMOTE_URL" == git@* || "$REMOTE_URL" == ssh://* ]]; then
  CURRENT_TRANSPORT="ssh"
else
  CURRENT_TRANSPORT="https"
fi

# ── Extract GitHub owner/repo from the URL ────────────────────────────────────
# Handles both: git@github.com:owner/repo.git  and  https://github.com/owner/repo.git
REPO_SLUG=$(echo "$REMOTE_URL" \
  | sed 's|git@github\.com:||' \
  | sed 's|https://github\.com/||' \
  | sed 's|\.git$||')

# Validate we extracted a proper owner/repo slug
if [[ -z "$REPO_SLUG" || "$REPO_SLUG" != */* ]]; then
  error "Could not determine GitHub owner/repo from remote URL: $REMOTE_URL"
  error "Expected format: git@github.com:owner/repo.git  or  https://github.com/owner/repo.git"
  exit 1
fi

HTTPS_URL="https://github.com/${REPO_SLUG}.git"
SSH_URL="git@github.com:${REPO_SLUG}.git"

# ── Already on HTTPS? ─────────────────────────────────────────────────────────
if [[ "$CURRENT_TRANSPORT" == "https" && -z "$MODE" ]]; then
  success "Remote is already using HTTPS — SSH keys are not required."
  echo ""
  info  "If you are still being asked for credentials, run:"
  echo "  git credential reject"
  echo "  git push  (and enter your GitHub token when prompted)"
  echo ""
  warn  "GitHub no longer accepts passwords — use a Personal Access Token (PAT)."
  echo "  Create one at: https://github.com/settings/tokens/new"
  echo "  Scopes needed: repo (all)"
  echo ""
  info  "To cache credentials so you're not asked again:"
  echo "  git config --global credential.helper store   # saves in ~/.git-credentials"
  echo "  # OR (safer, uses OS keychain on macOS/Linux):"
  echo "  git config --global credential.helper osxkeychain    # macOS"
  echo "  git config --global credential.helper libsecret      # Linux (GNOME)"
  exit 0
fi

# ── SSH remote: present options ───────────────────────────────────────────────
if [[ "$CURRENT_TRANSPORT" == "ssh" && -z "$MODE" ]]; then
  echo -e "${YELLOW}Your remote is set to SSH but your key requires a passphrase.${RESET}"
  echo ""
  echo "Choose a fix:"
  echo "  ${BOLD}1)${RESET} Switch to HTTPS  ${GREEN}(recommended — no SSH key needed)${RESET}"
  echo "  ${BOLD}2)${RESET} Load SSH key into ssh-agent  (keep using SSH, unlock key once per session)"
  echo "  ${BOLD}q)${RESET} Quit"
  echo ""
  read -rp "Enter choice [1/2/q]: " CHOICE
  case "$CHOICE" in
    1) MODE="https" ;;
    2) MODE="ssh-agent" ;;
    *) info "No changes made."; exit 0 ;;
  esac
fi

# =============================================================================
# OPTION 1 — Switch to HTTPS
# =============================================================================
switch_to_https() {
  header "Switching remote from SSH → HTTPS"
  info "New URL: ${BOLD}$HTTPS_URL${RESET}"
  git remote set-url origin "$HTTPS_URL"
  success "Remote updated!"
  echo ""
  info  "From now on 'git push' will use HTTPS.  Use a Personal Access Token (PAT)"
  info  "as your password — GitHub no longer accepts account passwords."
  echo ""
  info  "Create a PAT at: ${BOLD}https://github.com/settings/tokens/new${RESET}"
  echo "  → Expiration: 90 days (or no expiration)"
  echo "  → Scopes:     repo (full control)"
  echo ""
  info  "Cache your credentials so you're not prompted every time:"
  echo "  git config --global credential.helper store"
  echo "  git push   ← enter your GitHub username + PAT when asked"
  echo "              (stored in ~/.git-credentials for future pushes)"
  echo ""
  success "Done!  Try: git push"
}

# =============================================================================
# OPTION 2 — Load SSH key into ssh-agent
# =============================================================================
load_ssh_agent() {
  header "Loading SSH key into ssh-agent"

  # Start ssh-agent if not running
  if ! ssh-add -l &>/dev/null; then
    info "Starting ssh-agent..."
    eval "$(ssh-agent -s)"
  else
    info "ssh-agent is already running (PID ${SSH_AGENT_PID:-unknown})"
  fi

  # Find likely SSH private keys
  CANDIDATES=()
  for keyfile in ~/.ssh/id_ed25519 ~/.ssh/id_rsa ~/.ssh/id_ecdsa ~/.ssh/id_dsa; do
    [[ -f "$keyfile" ]] && CANDIDATES+=("$keyfile")
  done

  if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
    warn "No SSH private key found in ~/.ssh/"
    echo ""
    info "Generate a new passphrase-less key for this machine:"
    echo '  ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519'
    echo "  # Press Enter twice to skip the passphrase"
    echo ""
    info "Then add the public key to GitHub:"
    echo "  cat ~/.ssh/id_ed25519.pub"
    echo "  → Paste at: https://github.com/settings/ssh/new"
    exit 1
  fi

  # Offer to load each key
  for keyfile in "${CANDIDATES[@]}"; do
    echo ""
    info "Found key: ${BOLD}$keyfile${RESET}"
    # Check if key is already loaded
    KEY_FP="$(ssh-keygen -lf "$keyfile" 2>/dev/null | awk '{print $2}' || true)"
    if ssh-add -l 2>/dev/null | grep -qF "$KEY_FP"; then
      success "Key already loaded in agent — nothing to do."
    else
      info "Adding key to ssh-agent (you will be prompted for your passphrase)..."
      if ssh-add "$keyfile"; then
        success "Key loaded!  It will stay unlocked for this login session."
      else
        error "Failed to add key.  Check the passphrase and try again."
        exit 1
      fi
    fi
  done

  echo ""
  info "To avoid entering the passphrase on every login, add this to ~/.bashrc / ~/.zshrc:"
  echo '  # Auto-load SSH key on login'
  echo '  if [ -z "$SSH_AUTH_SOCK" ]; then'
  echo '    eval "$(ssh-agent -s)" > /dev/null'
  echo '    ssh-add ~/.ssh/id_ed25519 2>/dev/null'
  echo '  fi'
  echo ""
  success "Done!  Try: git push"
}

# ── Run chosen fix ─────────────────────────────────────────────────────────────
case "$MODE" in
  https)     switch_to_https ;;
  ssh-agent) load_ssh_agent ;;
  *)
    error "Unknown mode: $MODE"
    exit 1 ;;
esac

# ── Quick connectivity test ───────────────────────────────────────────────────
echo ""
info "Testing connection to GitHub..."
if [[ "$MODE" == "ssh-agent" ]]; then
  if ssh -T git@github.com -o BatchMode=yes -o ConnectTimeout=5 2>&1 | grep -q "successfully authenticated"; then
    success "SSH authentication to GitHub: OK"
  else
    warn "Could not verify SSH connection — try: ssh -T git@github.com"
  fi
else
  if git ls-remote --exit-code origin HEAD &>/dev/null; then
    success "HTTPS connection to GitHub: OK"
  else
    warn "Could not verify HTTPS connection — try 'git push' and enter your PAT when prompted."
  fi
fi
