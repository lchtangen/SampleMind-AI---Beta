#!/usr/bin/env bash
# =============================================================================
# rewrite-commit-emails.sh — Permanently rewrite author/committer emails in
#                            git history using git-filter-repo.
#
# Run this script ONCE on your local clone to replace the two leaked email
# addresses with your canonical GitHub noreply address:
#
#   lchtangen@Larss-MacBook-Pro.local  → 194328900+lchtangen@users.noreply.github.com
#   lchtangen@users.noreply.github.com → 194328900+lchtangen@users.noreply.github.com
#
# After the rewrite you must FORCE PUSH every branch that was rewritten:
#
#   git push --force-with-lease origin main
#   git push --force-with-lease origin <other-branch>
#
# ⚠️  WARNING: This rewrites commit SHAs.  Anyone who has cloned or forked the
#              repository must re-clone after the force push.  Only do this on
#              a private repository or when you have coordinated with all
#              collaborators.
#
# Prerequisites:
#   pip install git-filter-repo      # or: brew install git-filter-repo
#
# Usage:
#   bash scripts/setup/rewrite-commit-emails.sh [--dry-run]
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
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      echo "Usage: bash scripts/setup/rewrite-commit-emails.sh [--dry-run]"
      echo "  --dry-run  Show what would be changed without modifying history"
      exit 0 ;;
  esac
done

# ── Must be run from repo root ────────────────────────────────────────────────
if [[ ! -d ".git" ]]; then
  error "Run this script from the root of the repository."
  exit 1
fi

# ── Check git-filter-repo is installed ───────────────────────────────────────
if ! command -v git-filter-repo &>/dev/null; then
  error "git-filter-repo is not installed."
  echo "Install it with:"
  echo "  pip install git-filter-repo"
  echo "  # or: brew install git-filter-repo"
  exit 1
fi

# ── Configuration ─────────────────────────────────────────────────────────────
CANONICAL_EMAIL="194328900+lchtangen@users.noreply.github.com"
CANONICAL_NAME="Lars Tangen"

# Emails to replace → canonical
declare -A EMAIL_MAP=(
  ["lchtangen@Larss-MacBook-Pro.local"]="$CANONICAL_EMAIL"
  ["lchtangen@users.noreply.github.com"]="$CANONICAL_EMAIL"
)

header "🔧 SampleMind — Git Commit Email Rewriter"

# ── Capture remote URL before filter-repo removes it ─────────────────────────
SAVED_REMOTE_URL="$(git remote get-url origin 2>/dev/null || echo '')"

# ── Dry-run: show affected commits ────────────────────────────────────────────
if $DRY_RUN; then
  warn "DRY RUN — no changes will be made."
  echo ""
  for old_email in "${!EMAIL_MAP[@]}"; do
    count=$(git log --all --format="%ae" | grep -c "^${old_email}$" 2>/dev/null || true)
    echo -e "  ${YELLOW}$old_email${RESET}  →  ${GREEN}${EMAIL_MAP[$old_email]}${RESET}  (${BOLD}$count commits${RESET})"
  done
  echo ""
  info "Re-run without --dry-run to apply the rewrite."
  exit 0
fi

# ── Confirm ───────────────────────────────────────────────────────────────────
echo -e "${YELLOW}This will rewrite git history.  All commit SHAs will change.${RESET}"
echo ""
for old_email in "${!EMAIL_MAP[@]}"; do
  count=$(git log --all --format="%ae" | grep -c "^${old_email}$" 2>/dev/null || true)
  echo -e "  Replace: ${RED}$old_email${RESET} (${count} commits)"
  echo -e "     With: ${GREEN}${EMAIL_MAP[$old_email]}${RESET}"
  echo ""
done
read -rp "Continue? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  info "Aborted — no changes made."
  exit 0
fi

# ── Build the mailmap file for git-filter-repo ────────────────────────────────
TMPMAP="$(mktemp "${TMPDIR:-/tmp}/mailmap-rewrite-XXXXX.txt")"
trap 'rm -f "$TMPMAP"' EXIT

for old_email in "${!EMAIL_MAP[@]}"; do
  new_email="${EMAIL_MAP[$old_email]}"
  # git-filter-repo mailmap format: New Name <new@email> Old Name <old@email>
  echo "$CANONICAL_NAME <$new_email> <$old_email>" >> "$TMPMAP"
done

info "Mailmap used for rewrite:"
cat "$TMPMAP"
echo ""

# ── Run git-filter-repo ───────────────────────────────────────────────────────
header "Rewriting history..."

git filter-repo \
  --mailmap "$TMPMAP" \
  --force

success "History rewritten!"

# ── Re-add remote (filter-repo removes it as a safety measure) ───────────────
echo ""
if ! git remote get-url origin &>/dev/null; then
  if [[ -n "$SAVED_REMOTE_URL" ]]; then
    info "Re-adding origin remote (removed by filter-repo as a safety measure)..."
    git remote add origin "$SAVED_REMOTE_URL"
    success "Remote re-added: $SAVED_REMOTE_URL"
  else
    warn "Could not restore remote — add it manually with:"
    warn "  git remote add origin <your-repo-url>"
  fi
fi

# ── Verify ────────────────────────────────────────────────────────────────────
echo ""
header "Verification — unique emails after rewrite:"
git log --all --use-mailmap --format="%aE" | sort -u | while read -r email; do
  echo "  ✓ $email"
done

# ── Instructions for force push ───────────────────────────────────────────────
echo ""
header "Next step: force push ALL branches to GitHub"
echo -e "${YELLOW}git-filter-repo rewrites every commit SHA.  You must force push:${RESET}"
echo ""

git branch | sed 's/\*//; s/ //' | while read -r branch; do
  echo "  git push --force-with-lease origin $branch"
done

echo ""
warn "Force-pushing rewrites public history.  Anyone with a local clone"
warn "must run 'git fetch && git reset --hard origin/<branch>' afterwards."
echo ""
success "Done!  Run the force-push commands above to publish the rewritten history."
