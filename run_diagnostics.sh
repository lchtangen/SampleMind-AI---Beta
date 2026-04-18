#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# SampleMind AI — Comprehensive Diagnostics Runner
# ══════════════════════════════════════════════════════════════════════════════
#
# Runs a full project health-check and writes individual report files into a
# timestamped directory under the project root (DIAGNOSTICS_REPORT_<ts>/).
#
# Diagnostics performed (10 steps):
#   1. System & environment info (Python version, tools, structure)
#   2. Dependency import check (numpy, scipy, pydantic, …)
#   3. Ruff linting analysis (with --statistics)
#   4. Code format check (black + isort)
#   5. Type checking via mypy (60 s timeout)
#   6. Test discovery (pytest --collect-only)
#   7. Unit test execution (120 s timeout)
#   8. Validation scripts (validate_docs.py, debug_forensics.py)
#   9. Project structure analysis (file counts)
#  10. pyproject.toml summary (name, version, dep counts)
#
# Usage:
#   bash run_diagnostics.sh
#
# Output:
#   A DIAGNOSTICS_REPORT_<timestamp>/ directory containing per-step text
#   files and a combined FULL_DIAGNOSTICS.txt.
#
# NOTE: This script assumes it is run from the project root with an active
# .venv virtualenv.
# ══════════════════════════════════════════════════════════════════════════════
set -e

PROJECT_DIR="/home/lchtangen/projects/ai/SampleMind-AI---Beta"
cd "$PROJECT_DIR"
source .venv/bin/activate

REPORT_DIR="$PROJECT_DIR/DIAGNOSTICS_REPORT_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   SAMPLEMIND AI - COMPREHENSIVE DIAGNOSTICS REPORT    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Report Directory: $REPORT_DIR"
echo "⏰ Timestamp: $(date)"
echo ""

# ════════════════════════════════════════════════════════════
# 1. SYSTEM & ENVIRONMENT INFO
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  SYSTEM & ENVIRONMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Python Version: $(python --version)"
    echo "Virtual Env: $(which python)"
    echo "OS: $(uname -s)"
    echo "Arch: $(uname -m)"
    echo ""
    echo "Installed Tools:"
    echo "  - ruff: $(ruff --version)"
    echo "  - mypy: $(mypy --version 2>&1 | head -1)"
    echo "  - pytest: $(pytest --version)"
    echo ""
    echo "Project Structure:"
    find "$PROJECT_DIR" -maxdepth 2 -type d | head -20
} | tee "$REPORT_DIR/01_environment.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 2. DEPENDENCY CHECK
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  DEPENDENCY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Checking core imports..."
    python -c "
import sys
modules = ['numpy', 'scipy', 'pydantic', 'pytest', 'ruff', 'mypy', 'black', 'isort']
for mod in modules:
    try:
        __import__(mod)
        print(f'✓ {mod}')
    except ImportError as e:
        print(f'✗ {mod}: {e}')
" || true
} | tee "$REPORT_DIR/02_dependencies.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 3. LINTING WITH RUFF
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  RUFF LINTING ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Running ruff check..."
    ruff check . --statistics 2>&1 || true
} | tee "$REPORT_DIR/03_ruff_lint.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 4. CODE FORMAT CHECK
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  CODE FORMAT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Checking black formatting..."
    black --check src/ tests/ 2>&1 | head -50 || true
    echo ""
    echo "Checking isort import sorting..."
    isort --check-only src/ tests/ 2>&1 | head -50 || true
} | tee "$REPORT_DIR/04_format_check.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 5. TYPE CHECKING
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  TYPE CHECKING (MYPY)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Running mypy type checker..."
    timeout 60 mypy src/ 2>&1 | tail -100 || true
    echo ""
    echo "(Type checking may have timed out after 60s - check detailed log)"
} | tee "$REPORT_DIR/05_mypy_types.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 6. TEST DISCOVERY
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  TEST DISCOVERY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Collecting available tests..."
    timeout 30 pytest tests/ --collect-only -q 2>&1 || true
} | tee "$REPORT_DIR/06_test_discovery.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 7. RUN UNIT TESTS (IF POSSIBLE)
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  UNIT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Running unit tests (timeout: 120s)..."
    timeout 120 pytest tests/unit/ -v --tb=short 2>&1 || true
} | tee "$REPORT_DIR/07_unit_tests.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 8. VALIDATION SCRIPTS
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  RUN VALIDATION SCRIPTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    if [ -f "scripts/validate_docs.py" ]; then
        echo "Running document validation..."
        timeout 30 python scripts/validate_docs.py 2>&1 || echo "Skipped or failed"
    fi
    if [ -f "scripts/debug_forensics.py" ]; then
        echo "Running codebase forensics..."
        timeout 30 python scripts/debug_forensics.py 2>&1 | head -100 || echo "Skipped or failed"
    fi
} | tee "$REPORT_DIR/08_validation_scripts.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 9. PROJECT STRUCTURE ANALYSIS
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  PROJECT STRUCTURE ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "Source files count:"
    find src -type f -name "*.py" | wc -l | xargs echo "  Python files:"
    echo ""
    echo "Test files count:"
    find tests -type f -name "*.py" 2>/dev/null | wc -l | xargs echo "  Test files:"
    echo ""
    echo "Documentation files:"
    find docs -type f -name "*.md" 2>/dev/null | wc -l | xargs echo "  Markdown files:"
} | tee "$REPORT_DIR/09_structure_analysis.txt"
echo ""

# ════════════════════════════════════════════════════════════
# 10. PYPROJECT.TOML ANALYSIS
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟 CONFIGURATION ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
{
    echo "pyproject.toml Summary:"
    python << 'EOF'
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(f"Project: {data['project']['name']}")
    print(f"Version: {data['project']['version']}")
    print(f"Python: {data['project']['requires-python']}")
    print(f"Dependencies: {len(data['project']['dependencies'])} total")
    print(f"Dev Dependencies: {len(data['dependency-groups']['dev'])} total")
EOF
} | tee "$REPORT_DIR/10_config_analysis.txt"
echo ""

# ════════════════════════════════════════════════════════════
# SUMMARY REPORT
# ════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DIAGNOSTICS COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Report saved to: $REPORT_DIR"
echo ""
echo "📋 Files generated:"
ls -1 "$REPORT_DIR" | sed 's/^/   /'
echo ""
echo "🔗 Combined report:"
cat "$REPORT_DIR"/*.txt > "$REPORT_DIR/FULL_DIAGNOSTICS.txt"
echo "   $REPORT_DIR/FULL_DIAGNOSTICS.txt"
echo ""
