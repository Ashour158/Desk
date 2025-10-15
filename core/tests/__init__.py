"""
Test package initialization
"""

# Ensure Django is properly configured before importing any models
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test_optimized')

# Setup Django
if not django.apps.apps.ready:
    django.setup()

# Now it's safe to import models
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model

# Export common test utilities
__all__ = ['TestCase', 'TransactionTestCase', 'get_user_model']