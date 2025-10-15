"""
Test database setup and configuration utilities
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.test import TransactionTestCase
from django.core.management import call_command

def setup_test_database():
    """Setup test database with proper configuration"""
    # Ensure Django is configured
    if not django.apps.apps.ready:
        django.setup()
    
    # Create test database
    db_name = settings.DATABASES['default']['NAME']
    if ':memory:' not in db_name and not db_name.endswith('.sqlite3'):
        # For non-SQLite databases, create the test database
        from django.db import connections
        connection = connections['default']
        connection.creation.create_test_db(verbosity=1, autoclobber=True)
    
    return True

def teardown_test_database():
    """Clean up test database"""
    from django.db import connections
    connection = connections['default']
    if hasattr(connection, 'creation'):
        connection.creation.destroy_test_db(settings.DATABASES['default']['NAME'], verbosity=1)

class DatabaseTestCase(TransactionTestCase):
    """Base test case with proper database setup"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_test_database()
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Clean up if needed
        pass
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        # Create any necessary test data here
    
    def tearDown(self):
        """Clean up after test"""
        super().tearDown()
        # Clean up test data here
