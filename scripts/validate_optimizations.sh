#!/usr/bin/env bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SampleMind AI v6 - Optimization Validation Suite      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track results
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# ============================================================================
# Test 1: Python Environment
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 1: Python Environment & Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if python -c "import uvloop" 2>/dev/null; then
    pass "uvloop is installed"
else
    fail "uvloop not installed"
fi

if python -c "import orjson" 2>/dev/null; then
    pass "orjson is installed"
else
    fail "orjson not installed"
fi

if python -c "from fastapi.responses import ORJSONResponse" 2>/dev/null; then
    pass "ORJSONResponse available"
else
    fail "ORJSONResponse not available"
fi

if python -c "import blake3" 2>/dev/null; then
    pass "blake3 (fast hashing) installed"
else
    fail "blake3 not installed"
fi

if python -c "import httpx; import h2" 2>/dev/null; then
    pass "HTTP/2 support (httpx + h2) available"
else
    fail "HTTP/2 support not available"
fi

# ============================================================================
# Test 2: AI Performance Modules
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 2: AI Performance Modules${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if python -c "from src.samplemind.ai import get_http_client" 2>/dev/null; then
    pass "HTTP client module loadable"
else
    fail "HTTP client module not loadable"
fi

if python -c "from src.samplemind.ai import get_cache_stats, cache_response" 2>/dev/null; then
    pass "Cache module loadable"
else
    fail "Cache module not loadable"
fi

if python -c "from src.samplemind.ai import route_request, Provider, TaskType" 2>/dev/null; then
    pass "Router module loadable"
else
    fail "Router module not loadable"
fi

if python -c "from src.samplemind.ai import warm_all_caches, COMMON_PROMPTS" 2>/dev/null; then
    pass "Cache warming module loadable"
    
    # Check prompt count
    PROMPT_COUNT=$(python -c "from src.samplemind.ai import COMMON_PROMPTS; print(sum(len(p) for p in COMMON_PROMPTS.values()))")
    info "Cache warming has $PROMPT_COUNT pre-configured prompts"
else
    fail "Cache warming module not loadable"
fi

# ============================================================================
# Test 3: Docker Services
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 3: Docker Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if Redis is running
if docker compose ps redis 2>/dev/null | grep -q "running"; then
    pass "Redis is running"
    
    # Test Redis connectivity
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        pass "Redis responds to ping"
    else
        fail "Redis not responding"
    fi
else
    fail "Redis is not running"
fi

# Check if Ollama is running
if docker compose ps ollama 2>/dev/null | grep -q "running"; then
    pass "Ollama is running"
    
    # Check models
    MODEL_COUNT=$(docker compose exec ollama ollama list 2>/dev/null | grep -c "llama\|phi\|qwen" || echo "0")
    if [ "$MODEL_COUNT" -gt 0 ]; then
        pass "Ollama has $MODEL_COUNT model(s) available"
    else
        warn "Ollama has no models loaded"
    fi
else
    warn "Ollama is not running"
fi

# Check MongoDB
if docker compose ps mongodb 2>/dev/null | grep -q "running\|restarting"; then
    if docker compose ps mongodb 2>/dev/null | grep -q "running"; then
        pass "MongoDB is running"
    else
        warn "MongoDB is restarting (may be intermittent)"
    fi
else
    warn "MongoDB is not running"
fi

# ============================================================================
# Test 4: Performance Features
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 4: Performance Features${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check main.py for uvloop
if grep -q "uvloop.install()" src/samplemind/interfaces/api/main.py 2>/dev/null; then
    pass "uvloop integration in main.py"
else
    fail "uvloop not integrated in main.py"
fi

# Check for ORJSONResponse
if grep -q "default_response_class=ORJSONResponse" src/samplemind/interfaces/api/main.py 2>/dev/null; then
    pass "ORJSONResponse configured as default"
else
    fail "ORJSONResponse not configured"
fi

# Check HTTP client lifecycle
if grep -q "get_http_client()" src/samplemind/interfaces/api/main.py 2>/dev/null; then
    pass "HTTP client lifecycle management present"
else
    fail "HTTP client lifecycle not implemented"
fi

# Check enhanced health endpoint
if grep -q "/health/detailed" src/samplemind/interfaces/api/routes/health.py 2>/dev/null; then
    pass "Enhanced health endpoint (/health/detailed) present"
else
    fail "Enhanced health endpoint not found"
fi

# ============================================================================
# Test 5: Test Infrastructure
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 5: Test Infrastructure${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check pytest configuration
if [ -f "pytest.ini" ]; then
    pass "pytest.ini exists"
    
    if grep -q "\-n auto" pytest.ini 2>/dev/null; then
        pass "Parallel test execution configured"
    else
        warn "Parallel execution not configured"
    fi
else
    fail "pytest.ini not found"
fi

# Check for test fixtures
if grep -q "mock_ai_http_requests" tests/conftest.py 2>/dev/null; then
    pass "AI mocking fixtures present"
else
    warn "AI mocking fixtures not found"
fi

# Check test accelerators
if python -c "import pytest_xdist" 2>/dev/null; then
    pass "pytest-xdist (parallel) installed"
else
    warn "pytest-xdist not installed"
fi

if python -c "import respx" 2>/dev/null; then
    pass "respx (HTTP mocking) installed"
else
    warn "respx not installed"
fi

# ============================================================================
# Test 6: Docker Optimization
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 6: Docker Optimization${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Dockerfile
if [ -f "Dockerfile" ]; then
    if grep -q "syntax=docker/dockerfile:1.7" Dockerfile 2>/dev/null; then
        pass "Dockerfile uses BuildKit 1.7 syntax"
    else
        warn "Dockerfile not using BuildKit 1.7"
    fi
else
    fail "Dockerfile not found"
fi

# Check .dockerignore
if [ -f ".dockerignore" ]; then
    LINE_COUNT=$(wc -l < .dockerignore)
    pass ".dockerignore exists ($LINE_COUNT lines)"
else
    warn ".dockerignore not found"
fi

# Check BuildKit cache directory
if [ -d ".buildx-cache" ]; then
    pass "BuildKit cache directory exists"
else
    info "BuildKit cache directory not created yet"
fi

# ============================================================================
# Test 7: Documentation
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 7: Documentation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DOCS=(
    "PERFORMANCE_OPTIMIZATION_MASTER_PLAN.md"
    "OPTIMIZATION_PROGRESS.md"
    "SESSION_COMPLETE.md"
    "CONTINUATION_SESSION_SUMMARY.md"
    "FINAL_SESSION_SUMMARY.md"
    "QUICK_REFERENCE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        pass "$doc present"
    else
        warn "$doc not found"
    fi
done

# ============================================================================
# Summary
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      VALIDATION SUMMARY                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC}   $PASSED tests"
echo -e "${RED}Failed:${NC}   $FAILED tests"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS tests"
echo ""

TOTAL=$((PASSED + FAILED + WARNINGS))
SUCCESS_RATE=$((PASSED * 100 / TOTAL))

echo -e "Success Rate: ${SUCCESS_RATE}%"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL CRITICAL TESTS PASSED!${NC}"
    echo -e "${GREEN}🎉 Platform is ready for production!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Review above for details.${NC}"
    exit 1
fi
