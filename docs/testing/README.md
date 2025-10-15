# Testing Documentation

This directory contains all testing-related documentation, coverage reports, and test execution guides.

## Contents

### Test Coverage
- **COMPREHENSIVE_TEST_COVERAGE_ANALYSIS_REPORT.md** - Complete coverage analysis
- **COMPREHENSIVE_TEST_COVERAGE_REPORT.md** - Coverage report
- **TEST_COVERAGE_ANALYSIS_REPORT.md** - Coverage analysis
- **COMPREHENSIVE_UNTESTED_CODE_ANALYSIS_REPORT.md** - Untested code analysis
- **UNTESTED_CODE_ANALYSIS_REPORT.md** - Untested code report
- **UPDATED_UNTESTED_CODE_ANALYSIS_REPORT.md** - Updated analysis
- **REMAINING_UNTESTED_CODE_IMPLEMENTATION_COMPLETE.md** - Remaining untested code

### Test Execution
- **COMPREHENSIVE_TEST_EXECUTION_REPORT.md** - Complete execution report
- **COMPREHENSIVE_TEST_EXECUTION_SUMMARY.md** - Execution summary
- **TEST_EXECUTION_GUIDE.md** - Guide for running tests
- **TEST_EXECUTION_REPORT.md** - Execution results
- **TEST_EXECUTION_RESULTS_REPORT.md** - Detailed results

### Code Quality & Testing
- **CODE_QUALITY_FIXES_COMPLETE.md** - Code quality improvements
- **FINAL_CODE_QUALITY_REPORT.md** - Final quality report
- **CODE_SMELL_ANALYSIS_REPORT.md** - Code smell analysis
- **CODE_SMELL_REFACTORING_REPORT.md** - Refactoring report

### Test Implementation
- **CRITICAL_BUSINESS_LOGIC_AND_ERROR_SCENARIO_TESTS_IMPLEMENTATION_REPORT.md** - Critical tests
- **ERROR_HANDLING_COVERAGE_REPORT.md** - Error handling tests
- **TEST_FIXES_IMPLEMENTATION_REPORT.md** - Test fixes
- **TEST_QUALITY_ANALYSIS_REPORT.md** - Test quality analysis
- **TEST_QUALITY_IMPROVEMENT_REPORT.md** - Quality improvements

### Validation & Verification
- **FINAL_TESTING_VALIDATION_REPORT.md** - Final validation
- **MONITORING_TEST_REPORT.md** - Monitoring tests

### Specialized Testing
- **API_TESTING_SUITE.md** - API testing documentation
- **DATABASE_TESTING_REPORT.md** - Database testing
- **COMPREHENSIVE_DATABASE_TESTING_REPORT.md** - Complete database testing

## Running Tests

### Unit Tests
```bash
# Core Django tests
cd core
python manage.py test

# Pytest
pytest core/tests/
```

### Integration Tests
```bash
# Run integration tests
pytest tests/
```

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=core --cov-report=html
coverage report
```

### Specific Test Types
```bash
# API tests
pytest tests/test_apis.py

# Performance tests
pytest tests/test_performance.py

# Security tests
pytest test_scripts/security_test.py
```

## Test Organization

- **tests/** - Integration and system tests
- **core/tests/** - Django unit tests
- **test_scripts/** - Specialized test scripts

## Quick Start

1. Read [Test Execution Guide](TEST_EXECUTION_GUIDE.md)
2. Review [Test Coverage Report](COMPREHENSIVE_TEST_COVERAGE_REPORT.md)
3. Run tests with `pytest tests/`
