#!/bin/bash
# Git Pre-Commit Hook - Automatic Security Scan
# Copy this to .git/hooks/pre-commit and make it executable

set -e

echo "🔒 Running pre-commit security scan..."
echo ""

# Run security scan
./scripts/security-scan.sh

# If scan fails, prevent commit
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Commit blocked due to security issues!"
    echo "   Fix the issues above and try again."
    exit 1
fi

echo ""
echo "✅ Security scan passed! Proceeding with commit..."
exit 0
