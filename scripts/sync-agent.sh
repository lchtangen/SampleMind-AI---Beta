#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# SampleMind AI — Sync with Agent Branch
# ═══════════════════════════════════════════════════════════════════════════
#
# Keeps your local VS Code / WSL clone in sync with the cloud agent.
# Run this after the agent pushes changes, or set it as a cron/watch.
#
# Usage:
#   bash scripts/sync-agent.sh              # sync current branch
#   bash scripts/sync-agent.sh --watch      # auto-sync every 30 seconds
#   bash scripts/sync-agent.sh --deps       # sync + reinstall dependencies
#
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BRANCH=$(git branch --show-current)
REPO_ROOT=$(git rev-parse --show-toplevel)

log() { echo -e "${BLUE}[sync]${NC} $*"; }
ok()  { echo -e "${GREEN}  ✅${NC} $*"; }
warn(){ echo -e "${YELLOW}  ⚠️${NC} $*"; }
err() { echo -e "${RED}  ❌${NC} $*"; }

sync_once() {
    log "Fetching from origin..."
    git fetch --all --prune 2>/dev/null

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse "origin/${BRANCH}" 2>/dev/null || echo "")

    if [ -z "$REMOTE" ]; then
        warn "Remote branch 'origin/${BRANCH}' not found. Skipping pull."
        return
    fi

    if [ "$LOCAL" = "$REMOTE" ]; then
        ok "Already up to date on ${BRANCH} (${LOCAL:0:8})"
        return
    fi

    log "Local:  ${LOCAL:0:8}"
    log "Remote: ${REMOTE:0:8}"

    # Check for uncommitted changes
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        warn "You have uncommitted changes. Stashing before pull..."
        git stash push -m "sync-agent auto-stash $(date +%H:%M:%S)"
        STASHED=true
    else
        STASHED=false
    fi

    log "Pulling changes from origin/${BRANCH}..."
    if git pull --rebase origin "$BRANCH"; then
        ok "Synced to $(git rev-parse --short HEAD)"
        # Show what changed
        git --no-pager log --oneline "${LOCAL}..HEAD" 2>/dev/null | head -10
    else
        err "Pull failed. You may have conflicts to resolve."
        git rebase --abort 2>/dev/null || true
        git pull --no-rebase origin "$BRANCH" || true
    fi

    # Restore stashed changes
    if [ "$STASHED" = true ]; then
        log "Restoring stashed changes..."
        git stash pop || warn "Stash pop failed — resolve manually with 'git stash list'"
    fi
}

install_deps() {
    log "Installing Python dependencies..."
    cd "$REPO_ROOT"
    if command -v uv &>/dev/null; then
        uv sync 2>/dev/null && ok "Python deps synced (uv)" || warn "uv sync failed"
    elif [ -f .venv/bin/pip ]; then
        .venv/bin/pip install -e '.[dev]' -q && ok "Python deps installed (pip)" || warn "pip install failed"
    fi

    if [ -f apps/web/package.json ]; then
        log "Installing frontend dependencies..."
        cd apps/web
        npm install --legacy-peer-deps 2>/dev/null && ok "Frontend deps installed" || warn "npm install failed"
        cd "$REPO_ROOT"
    fi
}

watch_mode() {
    log "👀 Watching for changes every 30 seconds on branch: ${BRANCH}"
    log "Press Ctrl+C to stop."
    echo ""
    while true; do
        sync_once
        sleep 30
    done
}

# ── Main ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}🎵 SampleMind AI — Agent Sync${NC}"
echo -e "   Branch: ${GREEN}${BRANCH}${NC}"
echo -e "   Repo:   ${REPO_ROOT}"
echo ""

case "${1:-}" in
    --watch|-w)
        watch_mode
        ;;
    --deps|-d)
        sync_once
        install_deps
        ;;
    *)
        sync_once
        ;;
esac
