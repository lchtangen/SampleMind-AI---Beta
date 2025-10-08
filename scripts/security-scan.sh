#!/bin/bash
# SampleMind AI - Security Scan Script
# Run this before every commit to ensure no secrets are exposed

set -e

echo "🔒 SampleMind AI - Security Scan"
echo "================================="
echo ""

ERRORS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Scan for hardcoded API keys
echo "🔍 Scanning for hardcoded API keys..."
if grep -r "AIza[a-zA-Z0-9_-]\{35\}" src/ scripts/ 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: Google API key found in code!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No Google API keys found${NC}"
fi

if grep -r "sk-[a-zA-Z0-9]\{48\}" src/ scripts/ 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: OpenAI API key found in code!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No OpenAI API keys found${NC}"
fi

if grep -r "sk-ant-[a-zA-Z0-9_-]\{95\}" src/ scripts/ 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: Anthropic API key found in code!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No Anthropic API keys found${NC}"
fi

echo ""

# 2. Check for .env files in git
echo "🔍 Checking for .env files in Git..."
if git ls-files | grep -E "^\.env$" 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: .env file is tracked by Git!${NC}"
    echo "   Run: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
elif git ls-files | grep -E "\.env\.backup|\.env\.secure" 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: .env backup files are tracked by Git!${NC}"
    echo "   Run: git rm --cached .env.backup* .env.secure"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No sensitive .env files tracked by Git${NC}"
    echo -e "   (.env.example is OK to track)"
fi

echo ""

# 3. Check staged files for secrets
echo "🔍 Scanning staged changes for secrets..."
if git diff --cached | grep -iE "api_key.*=.*['\"][a-zA-Z0-9_-]{20,}" 2>/dev/null; then
    echo -e "${RED}❌ CRITICAL: API key found in staged changes!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No secrets in staged changes${NC}"
fi

echo ""

# 4. Check for debug statements
echo "🔍 Checking for debug code..."
if grep -r "breakpoint()" src/ tests/ --include="*.py" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: breakpoint() calls found${NC}"
fi

if grep -r "console\.log" web-app/src/ --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "// console.log" | head -5; then
    echo -e "${YELLOW}⚠️  WARNING: console.log statements found in web-app${NC}"
fi

echo ""

# 5. Check file sizes (large files warning)
echo "🔍 Checking for large files..."
LARGE_FILES=$(git ls-files | xargs ls -lh 2>/dev/null | awk '$5 ~ /M$/ && $5+0 > 5 {print $9, $5}')
if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Large files found (>5MB):${NC}"
    echo "$LARGE_FILES"
else
    echo -e "${GREEN}✅ No large files detected${NC}"
fi

echo ""

# Summary
echo "================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Security scan passed! Safe to commit.${NC}"
    exit 0
else
    echo -e "${RED}❌ Security scan failed with $ERRORS error(s)!${NC}"
    echo -e "${RED}   DO NOT COMMIT until issues are resolved!${NC}"
    exit 1
fi
