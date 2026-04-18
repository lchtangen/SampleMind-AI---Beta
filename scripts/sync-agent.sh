#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# scripts/sync-agent.sh — Sync local repo with remote branch
#
# Usage:
#   bash scripts/sync-agent.sh            # one-shot sync
#   bash scripts/sync-agent.sh --watch    # continuous 30s polling
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

POLL_INTERVAL="${SYNC_INTERVAL:-30}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT"

# ── Helpers ───────────────────────────────────────────────────────────────────

log() { printf "\033[36m[sync]\033[0m %s\n" "$*"; }
err() { printf "\033[31m[sync]\033[0m %s\n" "$*" >&2; }

sync_once() {
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD)"

  log "Fetching from origin..."
  git fetch origin "$branch" --quiet 2>/dev/null || {
    err "Failed to fetch origin/$branch"
    return 1
  }

  local local_sha remote_sha
  local_sha="$(git rev-parse HEAD)"
  remote_sha="$(git rev-parse "origin/$branch" 2>/dev/null || echo "")"

  if [[ -z "$remote_sha" ]]; then
    err "Remote branch origin/$branch not found"
    return 1
  fi

  if [[ "$local_sha" == "$remote_sha" ]]; then
    log "Already up to date ($branch @ ${local_sha:0:8})"
    return 0
  fi

  log "Pulling changes on $branch (${local_sha:0:8} → ${remote_sha:0:8})..."
  git pull --ff-only origin "$branch" --quiet 2>/dev/null || {
    err "Pull failed (possible merge conflict). Resolve manually."
    return 1
  }

  # Sync Python dependencies if uv is available
  if command -v uv &>/dev/null; then
    log "Syncing Python dependencies (uv sync)..."
    uv sync --quiet 2>/dev/null || true
  elif [[ -f "pyproject.toml" ]]; then
    log "Syncing Python dependencies (pip)..."
    pip install -q -e ".[dev]" 2>/dev/null || true
  fi

  # Sync Node.js dependencies if package.json changed
  if git diff --name-only "$local_sha" "$remote_sha" | grep -q "package.json"; then
    if command -v pnpm &>/dev/null; then
      log "Syncing Node.js dependencies (pnpm install)..."
      pnpm install --frozen-lockfile --silent 2>/dev/null || true
    elif command -v npm &>/dev/null; then
      log "Syncing Node.js dependencies (npm ci)..."
      npm ci --silent 2>/dev/null || true
    fi
  fi

  log "✅ Synced to ${remote_sha:0:8}"
}

# ── Main ──────────────────────────────────────────────────────────────────────

if [[ "${1:-}" == "--watch" ]]; then
  log "Watch mode: polling every ${POLL_INTERVAL}s (Ctrl+C to stop)"
  while true; do
    sync_once || true
    sleep "$POLL_INTERVAL"
  done
else
  sync_once
fi
