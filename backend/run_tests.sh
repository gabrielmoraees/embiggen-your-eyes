#!/bin/bash
# Test runner script for Embiggen Your Eyes API

set -e

echo "======================================================================"
echo "  Embiggen Your Eyes - Test Suite"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements.txt
fi

# Parse arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    unit)
        echo -e "${BLUE}Running unit tests...${NC}"
        pytest tests/unit/ -v
        ;;
    integration)
        echo -e "${BLUE}Running integration tests...${NC}"
        pytest tests/integration/ -v
        ;;
    e2e)
        echo -e "${BLUE}Running end-to-end tests...${NC}"
        pytest tests/e2e/ -v
        ;;
    coverage)
        echo -e "${BLUE}Running tests with coverage...${NC}"
        pytest --cov=. --cov-report=html --cov-report=term
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    all)
        echo -e "${BLUE}Running all tests...${NC}"
        pytest -v
        ;;
    *)
        echo "Usage: $0 {unit|integration|e2e|coverage|all}"
        echo ""
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  e2e         - Run end-to-end tests only"
        echo "  coverage    - Run all tests with coverage report"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}======================================================================"
echo -e "  Tests completed!"
echo -e "======================================================================${NC}"
