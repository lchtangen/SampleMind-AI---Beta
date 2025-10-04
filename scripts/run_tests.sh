#!/bin/bash

# SampleMind AI Test Runner
# Comprehensive test execution script with reporting

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$PROJECT_ROOT/test_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}🧪 SampleMind AI Test Suite${NC}"
echo -e "${BLUE}=============================${NC}"
echo ""

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to run tests
run_test_suite() {
    local test_type=$1
    local test_path=$2
    local markers=$3
    
    echo -e "${YELLOW}Running $test_type tests...${NC}"
    
    if [ -n "$markers" ]; then
        pytest "$test_path" -m "$markers" \
            --html="$REPORT_DIR/${test_type}_${TIMESTAMP}.html" \
            --self-contained-html \
            --json-report \
            --json-report-file="$REPORT_DIR/${test_type}_${TIMESTAMP}.json" \
            -v
    else
        pytest "$test_path" \
            --html="$REPORT_DIR/${test_type}_${TIMESTAMP}.html" \
            --self-contained-html \
            --json-report \
            --json-report-file="$REPORT_DIR/${test_type}_${TIMESTAMP}.json" \
            -v
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $test_type tests passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_type tests failed${NC}"
        return 1
    fi
}

# Parse command line arguments
TEST_TYPE="${1:-all}"
SKIP_SERVICES="${2:-false}"

# Start required services if not skipped
if [ "$SKIP_SERVICES" != "true" ]; then
    echo -e "${YELLOW}📦 Starting test services...${NC}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}✗ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    
    # Start MongoDB and Redis
    docker-compose -f docker-compose.yml up -d mongodb redis
    
    echo -e "${GREEN}✓ Test services started${NC}"
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    sleep 5
fi

# Run tests based on type
case $TEST_TYPE in
    "unit")
        echo -e "${BLUE}📝 Running Unit Tests Only${NC}"
        run_test_suite "unit" "tests/unit" "unit"
        ;;
    
    "integration")
        echo -e "${BLUE}🔗 Running Integration Tests Only${NC}"
        run_test_suite "integration" "tests/integration" "integration"
        ;;
    
    "e2e")
        echo -e "${BLUE}🌐 Running E2E Tests Only${NC}"
        # Install playwright if not already installed
        if ! command -v playwright &> /dev/null; then
            echo -e "${YELLOW}Installing Playwright...${NC}"
            pip install playwright pytest-playwright
            playwright install chromium
        fi
        run_test_suite "e2e" "tests/e2e" "e2e"
        ;;
    
    "load")
        echo -e "${BLUE}⚡ Running Load Tests${NC}"
        echo -e "${YELLOW}Starting Locust web interface...${NC}"
        echo -e "${YELLOW}Open http://localhost:8089 to configure and run load tests${NC}"
        locust -f tests/load/locustfile.py --host=http://localhost:8000
        ;;
    
    "quick")
        echo -e "${BLUE}⚡ Running Quick Test Suite (Unit only, no slow tests)${NC}"
        pytest tests/unit -m "not slow" \
            --html="$REPORT_DIR/quick_${TIMESTAMP}.html" \
            --self-contained-html \
            -v
        ;;
    
    "all")
        echo -e "${BLUE}🎯 Running Complete Test Suite${NC}"
        
        # Run unit tests
        run_test_suite "unit" "tests/unit" "unit"
        UNIT_RESULT=$?
        
        # Run integration tests
        run_test_suite "integration" "tests/integration" "integration"
        INTEGRATION_RESULT=$?
        
        # Generate coverage report
        echo -e "${YELLOW}📊 Generating coverage report...${NC}"
        pytest tests/unit tests/integration \
            --cov=src \
            --cov-report=html:"$REPORT_DIR/coverage_${TIMESTAMP}" \
            --cov-report=term \
            --cov-report=xml:"$REPORT_DIR/coverage_${TIMESTAMP}.xml"
        
        echo ""
        echo -e "${BLUE}=============================${NC}"
        echo -e "${BLUE}📊 Test Summary${NC}"
        echo -e "${BLUE}=============================${NC}"
        
        if [ $UNIT_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Unit Tests: PASSED${NC}"
        else
            echo -e "${RED}✗ Unit Tests: FAILED${NC}"
        fi
        
        if [ $INTEGRATION_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Integration Tests: PASSED${NC}"
        else
            echo -e "${RED}✗ Integration Tests: FAILED${NC}"
        fi
        
        echo ""
        echo -e "${BLUE}📁 Reports generated in: ${REPORT_DIR}${NC}"
        
        # Exit with error if any test suite failed
        if [ $UNIT_RESULT -ne 0 ] || [ $INTEGRATION_RESULT -ne 0 ]; then
            exit 1
        fi
        ;;
    
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [test_type] [skip_services]"
        echo ""
        echo "Test types:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  e2e         - Run end-to-end tests only"
        echo "  load        - Run load tests with Locust"
        echo "  quick       - Run quick tests (unit, no slow)"
        echo "  all         - Run all tests (default)"
        echo ""
        echo "skip_services: Set to 'true' to skip starting Docker services"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Test execution complete!${NC}"
echo -e "${BLUE}📁 Reports: ${REPORT_DIR}${NC}"
