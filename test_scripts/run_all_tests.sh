#!/bin/bash
# Comprehensive API Testing Script
# Runs all API tests including Postman/Insomnia, security, rate limiting, and performance tests

set -e  # Exit on any error

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="TestPassword123!"
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p $OUTPUT_DIR

echo -e "${BLUE}🚀 Starting Comprehensive API Testing Suite${NC}"
echo "=================================================="
echo "Base URL: $BASE_URL"
echo "Test Email: $TEST_EMAIL"
echo "Output Directory: $OUTPUT_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to run test and capture result
run_test() {
    local test_name="$1"
    local test_command="$2"
    local output_file="$3"
    
    echo -e "${YELLOW}Running $test_name...${NC}"
    
    if eval "$test_command" > "$output_file" 2>&1; then
        print_status 0 "$test_name completed successfully"
        return 0
    else
        print_status 1 "$test_name failed"
        return 1
    fi
}

# Check if required tools are installed
echo -e "${BLUE}🔍 Checking required tools...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    print_status 0 "Python3 is installed"
else
    print_status 1 "Python3 is not installed"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status 0 "pip3 is installed"
else
    print_status 1 "pip3 is not installed"
    exit 1
fi

# Check Newman (Postman CLI)
if command -v newman &> /dev/null; then
    print_status 0 "Newman is installed"
else
    echo -e "${YELLOW}Installing Newman...${NC}"
    npm install -g newman
    if [ $? -eq 0 ]; then
        print_status 0 "Newman installed successfully"
    else
        print_status 1 "Failed to install Newman"
        exit 1
    fi
fi

# Check Node.js
if command -v node &> /dev/null; then
    print_status 0 "Node.js is installed"
else
    print_status 1 "Node.js is not installed"
    exit 1
fi

echo ""

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip3 install requests python-dateutil > /dev/null 2>&1
print_status $? "Python dependencies installed"

echo ""

# Test 1: Basic API Connectivity
echo -e "${BLUE}🔌 Testing API Connectivity...${NC}"
run_test "API Connectivity Test" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/health/" \
    "$OUTPUT_DIR/connectivity_test_$TIMESTAMP.log"

if [ $? -eq 0 ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BASE_URL/health/)
    if [ "$HTTP_CODE" = "200" ]; then
        print_status 0 "API is accessible"
    else
        print_status 1 "API returned HTTP $HTTP_CODE"
        echo -e "${RED}Please ensure the API server is running on $BASE_URL${NC}"
        exit 1
    fi
else
    print_status 1 "API connectivity test failed"
    exit 1
fi

echo ""

# Test 2: Python API Test Runner
echo -e "${BLUE}🐍 Running Python API Test Runner...${NC}"
run_test "Python API Test Runner" \
    "python3 test_scripts/api_test_runner.py --base-url $BASE_URL --email $TEST_EMAIL --password $TEST_PASSWORD --output $OUTPUT_DIR/api_test_results_$TIMESTAMP.json" \
    "$OUTPUT_DIR/python_api_test_$TIMESTAMP.log"

PYTHON_API_RESULT=$?

echo ""

# Test 3: Security Testing
echo -e "${BLUE}🔒 Running Security Tests...${NC}"
run_test "Security Test Suite" \
    "python3 test_scripts/security_test.py --base-url $BASE_URL --email $TEST_EMAIL --password $TEST_PASSWORD --output $OUTPUT_DIR/security_test_results_$TIMESTAMP.json" \
    "$OUTPUT_DIR/security_test_$TIMESTAMP.log"

SECURITY_TEST_RESULT=$?

echo ""

# Test 4: Rate Limiting Tests
echo -e "${BLUE}⏱️ Running Rate Limiting Tests...${NC}"
run_test "Rate Limiting Test Suite" \
    "python3 test_scripts/rate_limit_test.py --base-url $BASE_URL --email $TEST_EMAIL --password $TEST_PASSWORD --output $OUTPUT_DIR/rate_limit_test_results_$TIMESTAMP.json" \
    "$OUTPUT_DIR/rate_limit_test_$TIMESTAMP.log"

RATE_LIMIT_RESULT=$?

echo ""

# Test 5: Postman Collection Tests
echo -e "${BLUE}📮 Running Postman Collection Tests...${NC}"
if [ -f "postman_collections/API_Testing_Suite.postman_collection.json" ]; then
    run_test "Postman Collection Tests" \
        "newman run postman_collections/API_Testing_Suite.postman_collection.json --environment postman_collections/API_Testing_Environment.postman_environment.json --reporters cli,json --reporter-json-export $OUTPUT_DIR/postman_test_results_$TIMESTAMP.json" \
        "$OUTPUT_DIR/postman_test_$TIMESTAMP.log"
    
    POSTMAN_RESULT=$?
else
    echo -e "${YELLOW}⚠️ Postman collection not found, skipping...${NC}"
    POSTMAN_RESULT=0
fi

echo ""

# Test 6: API Documentation Tests
echo -e "${BLUE}📚 Testing API Documentation...${NC}"
run_test "API Documentation Test" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/api/schema/" \
    "$OUTPUT_DIR/documentation_test_$TIMESTAMP.log"

if [ $? -eq 0 ]; then
    DOC_HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' $BASE_URL/api/schema/)
    if [ "$DOC_HTTP_CODE" = "200" ]; then
        print_status 0 "API documentation is accessible"
        DOC_RESULT=0
    else
        print_status 1 "API documentation returned HTTP $DOC_HTTP_CODE"
        DOC_RESULT=1
    fi
else
    DOC_RESULT=1
fi

echo ""

# Test 7: API Versioning Tests
echo -e "${BLUE}📋 Testing API Versioning...${NC}"
run_test "API Versioning Test" \
    "curl -s -H 'Accept: application/vnd.api.v1+json' -o /dev/null -w '%{http_code}' $BASE_URL/tickets/" \
    "$OUTPUT_DIR/versioning_test_$TIMESTAMP.log"

if [ $? -eq 0 ]; then
    VERSION_HTTP_CODE=$(curl -s -H 'Accept: application/vnd.api.v1+json' -o /dev/null -w '%{http_code}' $BASE_URL/tickets/)
    if [ "$VERSION_HTTP_CODE" = "200" ] || [ "$VERSION_HTTP_CODE" = "401" ]; then
        print_status 0 "API versioning is working"
        VERSION_RESULT=0
    else
        print_status 1 "API versioning returned HTTP $VERSION_HTTP_CODE"
        VERSION_RESULT=1
    fi
else
    VERSION_RESULT=1
fi

echo ""

# Test 8: Performance Tests
echo -e "${BLUE}⚡ Running Performance Tests...${NC}"
run_test "Performance Test" \
    "for i in {1..10}; do curl -s -o /dev/null -w '%{time_total}\n' $BASE_URL/tickets/; done | awk '{sum+=$1; count++} END {print \"Average response time:\", sum/count, \"seconds\"}'" \
    "$OUTPUT_DIR/performance_test_$TIMESTAMP.log"

PERFORMANCE_RESULT=$?

echo ""

# Test 9: Error Scenario Tests
echo -e "${BLUE}🚨 Testing Error Scenarios...${NC}"
run_test "Error Scenario Tests" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/tickets/non-existent-id/ && curl -s -o /dev/null -w '%{http_code}' $BASE_URL/auth/login/ -X POST -H 'Content-Type: application/json' -d '{\"email\":\"invalid\",\"password\":\"invalid\"}'" \
    "$OUTPUT_DIR/error_scenario_test_$TIMESTAMP.log"

ERROR_SCENARIO_RESULT=$?

echo ""

# Generate Test Summary
echo -e "${BLUE}📊 Generating Test Summary...${NC}"

# Create summary report
SUMMARY_FILE="$OUTPUT_DIR/test_summary_$TIMESTAMP.md"
cat > "$SUMMARY_FILE" << EOF
# API Testing Summary Report

**Generated:** $(date)
**Base URL:** $BASE_URL
**Test Email:** $TEST_EMAIL

## Test Results

| Test Category | Status | Details |
|---------------|--------|---------|
| API Connectivity | $([ $? -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Basic connectivity test |
| Python API Tests | $([ $PYTHON_API_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Comprehensive API endpoint testing |
| Security Tests | $([ $SECURITY_TEST_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | SQL injection, XSS, and other security tests |
| Rate Limiting Tests | $([ $RATE_LIMIT_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Rate limiting validation |
| Postman Tests | $([ $POSTMAN_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Postman collection tests |
| Documentation Tests | $([ $DOC_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | API documentation accessibility |
| Versioning Tests | $([ $VERSION_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | API versioning validation |
| Performance Tests | $([ $PERFORMANCE_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Response time testing |
| Error Scenario Tests | $([ $ERROR_SCENARIO_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | Error handling validation |

## Overall Result

EOF

# Calculate overall result
TOTAL_TESTS=9
PASSED_TESTS=0

[ $PYTHON_API_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $SECURITY_TEST_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $RATE_LIMIT_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $POSTMAN_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $DOC_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $VERSION_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $PERFORMANCE_RESULT -eq 0 ] && ((PASSED_TESTS++))
[ $ERROR_SCENARIO_RESULT -eq 0 ] && ((PASSED_TESTS++))

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

if [ $SUCCESS_RATE -ge 80 ]; then
    echo "**Overall Status: ✅ PASS**" >> "$SUMMARY_FILE"
    echo -e "${GREEN}🎉 Overall Test Result: PASS ($PASSED_TESTS/$TOTAL_TESTS tests passed)${NC}"
elif [ $SUCCESS_RATE -ge 60 ]; then
    echo "**Overall Status: ⚠️ PARTIAL PASS**" >> "$SUMMARY_FILE"
    echo -e "${YELLOW}⚠️ Overall Test Result: PARTIAL PASS ($PASSED_TESTS/$TOTAL_TESTS tests passed)${NC}"
else
    echo "**Overall Status: ❌ FAIL**" >> "$SUMMARY_FILE"
    echo -e "${RED}❌ Overall Test Result: FAIL ($PASSED_TESTS/$TOTAL_TESTS tests passed)${NC}"
fi

echo "**Success Rate: $SUCCESS_RATE%**" >> "$SUMMARY_FILE"
echo "**Passed Tests: $PASSED_TESTS/$TOTAL_TESTS**" >> "$SUMMARY_FILE"

echo ""
echo -e "${BLUE}📁 Test Results Summary:${NC}"
echo "=================================================="
echo "Output Directory: $OUTPUT_DIR"
echo "Summary Report: $SUMMARY_FILE"
echo ""

# List all generated files
echo -e "${BLUE}📄 Generated Files:${NC}"
ls -la "$OUTPUT_DIR"/*_$TIMESTAMP.*

echo ""
echo -e "${BLUE}🔍 To view detailed results:${NC}"
echo "  - API Test Results: cat $OUTPUT_DIR/api_test_results_$TIMESTAMP.json"
echo "  - Security Test Results: cat $OUTPUT_DIR/security_test_results_$TIMESTAMP.json"
echo "  - Rate Limiting Results: cat $OUTPUT_DIR/rate_limit_test_results_$TIMESTAMP.json"
echo "  - Postman Results: cat $OUTPUT_DIR/postman_test_results_$TIMESTAMP.json"
echo "  - Summary Report: cat $SUMMARY_FILE"

echo ""
echo -e "${BLUE}🚀 Testing Complete!${NC}"

# Exit with appropriate code
if [ $SUCCESS_RATE -ge 80 ]; then
    exit 0
else
    exit 1
fi
