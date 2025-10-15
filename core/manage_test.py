#!/usr/bin/env python
"""
Django test management script that properly initializes the Django environment.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment for testing"""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test_optimized')
    
    # Configure Django
    django.setup()

def run_tests(test_labels=None):
    """Run Django tests with proper setup"""
    setup_django()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Run tests
    if test_labels is None:
        test_labels = ['core.tests']
    
    failures = test_runner.run_tests(test_labels)
    return failures

if __name__ == '__main__':
    # Get test labels from command line arguments
    test_labels = sys.argv[1:] if len(sys.argv) > 1 else None
    failures = run_tests(test_labels)
    sys.exit(bool(failures))
