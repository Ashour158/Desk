#!/usr/bin/env python
"""
Test runner script that properly initializes Django before running tests.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test_optimized')
    django.setup()

def run_tests():
    """Run Django tests"""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["core.tests.test_models"])
    
    return failures

if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures))
