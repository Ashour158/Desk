# Test Suite

This directory contains integration and system-level tests for the Django Multi-Tenant Helpdesk & FSM Platform.

## Test Files

- `test_data_integrity.py` - Data integrity and consistency tests
- `test_health_checks.py` - System health check tests
- `test_monitoring_suite.py` - Monitoring and observability tests
- `test_updated_dependencies.py` - Dependency update validation tests

## Running Tests

```bash
# Run all tests in this directory
pytest tests/

# Run specific test file
pytest tests/test_health_checks.py

# Run with coverage
pytest tests/ --cov=core --cov-report=html
```

## Unit Tests

For unit tests specific to Django apps, see:
- `core/tests/` - Core Django application tests
- `core/apps/*/tests/` - App-specific unit tests
