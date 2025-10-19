#!/bin/bash

# Exit on error
set -e

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first:"
    echo "https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "Please log in to GitHub CLI first:"
    echo "gh auth login"
    exit 1
fi

# Repository details (update these if needed)
OWNER="lchtangen"
REPO="SampleMind-AI---Beta"
BRANCH="main"

# Set branch protection rules
echo "Setting up branch protection rules for $BRANCH branch..."

# Enable branch protection with required status checks
gh api -X PUT \
  -H "Accept: application/vnd.github.v3+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/branches/$BRANCH/protection \
  -f "{
    \"required_status_checks\": {
      \"strict\": true,
      \"contexts\": [\"build-and-test\"]
    },
    \"enforce_admins\": false,
    \"required_pull_request_reviews\": {
      \"dismiss_stale_reviews\": true,
      \"require_code_owner_reviews\": true,
      \"required_approving_review_count\": 1
    },
    \"restrictions\": null,
    \"required_linear_history\": true,
    \"allow_force_pushes\": false,
    \"allow_deletions\": false,
    \"block_creations\": false,
    \"required_conversation_resolution\": true,
    \"lock_branch\": false,
    \"allow_fork_syncing\": true
  }"

echo "Branch protection rules have been configured for the $BRANCH branch."
echo "You can view and modify these settings at: https://github.com/$OWNER/$REPO/settings/branches"

# Make the script executable
chmod +x "./scripts/setup-branch-protection.sh"
