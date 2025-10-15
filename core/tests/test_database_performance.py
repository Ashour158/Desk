"""
Comprehensive Database Performance Tests
Tests critical database performance logic including query optimization, N+1 query detection, and performance monitoring.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from decimal import Decimal
from django.db import connection
from django.test.utils import override_settings

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician
from apps.knowledge_base.models import KBArticle
from apps.automation.models import AutomationRule
from apps.analytics.models import AnalyticsDashboard, Report
from apps.database_optimizations.performance_tester import DatabasePerformanceTester
from apps.database_optimizations.query_optimizers import QueryOptimizer
from apps.database_optimizations.application_validators import DataIntegrityValidator

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class DatabasePerformanceTesterTest(EnhancedTransactionTestCase):
    """Test Database Performance Tester with comprehensive performance testing coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.performance_tester = DatabasePerformanceTester()
        
        # Create test data
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data for performance testing."""
        # Create users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f"user{i}@example.com",
                password="password",
                organization=self.organization,
                first_name=f"User{i}",
                last_name="Test"
            )
            self.users.append(user)
        
        # Create tickets
        self.tickets = []
        for i in range(50):
            ticket = Ticket.objects.create(
                organization=self.organization,
                customer=self.users[i % 10],
                subject=f"Test Ticket {i}",
                description=f"Test ticket description {i}",
                priority="medium",
                status="open"
            )
            self.tickets.append(ticket)
        
        # Create technicians
        self.technicians = []
        for i in range(5):
            technician = Technician.objects.create(
                organization=self.organization,
                user=self.users[i],
                name=f"Technician {i}",
                skills=["technical", "hardware"],
                is_active=True
            )
            self.technicians.append(technician)
        
        # Create work orders
        self.work_orders = []
        for i in range(20):
            work_order = WorkOrder.objects.create(
                organization=self.organization,
                technician=self.technicians[i % 5],
                subject=f"Test Work Order {i}",
                description=f"Test work order description {i}",
                priority="medium",
                status="pending"
            )
            self.work_orders.append(work_order)
    
    def test_run_query_tests_success(self):
        """Test successful query performance testing."""
        with patch.object(self.performance_tester, '_test_simple_queries') as mock_simple:
            mock_simple.return_value = {'status': 'success', 'execution_time': 100}
            
            with patch.object(self.performance_tester, '_test_complex_queries') as mock_complex:
                mock_complex.return_value = {'status': 'success', 'execution_time': 500}
                
                with patch.object(self.performance_tester, '_test_n_plus_one_queries') as mock_n_plus_one:
                    mock_n_plus_one.return_value = {'status': 'success', 'n_plus_one_detected': False}
                    
                    result = self.performance_tester.run_query_tests()
                    
                    self.assertIn('overall_status', result)
                    self.assertIn('simple_queries', result)
                    self.assertIn('complex_queries', result)
                    self.assertIn('n_plus_one_queries', result)
                    self.assertEqual(result['overall_status'], 'success')
    
    def test_run_query_tests_performance_issues(self):
        """Test query performance testing with performance issues."""
        with patch.object(self.performance_tester, '_test_simple_queries') as mock_simple:
            mock_simple.return_value = {'status': 'warning', 'execution_time': 2000}  # Slow query
            
            with patch.object(self.performance_tester, '_test_complex_queries') as mock_complex:
                mock_complex.return_value = {'status': 'warning', 'execution_time': 5000}  # Very slow query
                
                with patch.object(self.performance_tester, '_test_n_plus_one_queries') as mock_n_plus_one:
                    mock_n_plus_one.return_value = {'status': 'warning', 'n_plus_one_detected': True}
                    
                    result = self.performance_tester.run_query_tests()
                    
                    self.assertEqual(result['overall_status'], 'warning')
                    self.assertIn('performance_issues', result)
    
    def test_run_query_tests_error(self):
        """Test query performance testing with error."""
        with patch.object(self.performance_tester, '_test_simple_queries') as mock_simple:
            mock_simple.side_effect = Exception("Query test failed")
            
            result = self.performance_tester.run_query_tests()
            
            self.assertEqual(result['overall_status'], 'error')
            self.assertIn('error', result)
            self.assertIn('Query test failed', result['error'])
    
    def test_test_simple_queries_success(self):
        """Test successful simple query testing."""
        with patch.object(self.performance_tester, '_execute_query') as mock_execute:
            mock_execute.return_value = {'execution_time': 50, 'rows_affected': 10}
            
            result = self.performance_tester._test_simple_queries()
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('execution_time', result)
            self.assertIn('queries_tested', result)
    
    def test_test_simple_queries_slow(self):
        """Test simple query testing with slow queries."""
        with patch.object(self.performance_tester, '_execute_query') as mock_execute:
            mock_execute.return_value = {'execution_time': 2000, 'rows_affected': 10}  # Slow query
            
            result = self.performance_tester._test_simple_queries()
            
            self.assertEqual(result['status'], 'warning')
            self.assertIn('slow_queries', result)
    
    def test_test_complex_queries_success(self):
        """Test successful complex query testing."""
        with patch.object(self.performance_tester, '_execute_query') as mock_execute:
            mock_execute.return_value = {'execution_time': 200, 'rows_affected': 50}
            
            result = self.performance_tester._test_complex_queries()
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('execution_time', result)
            self.assertIn('queries_tested', result)
    
    def test_test_complex_queries_slow(self):
        """Test complex query testing with slow queries."""
        with patch.object(self.performance_tester, '_execute_query') as mock_execute:
            mock_execute.return_value = {'execution_time': 5000, 'rows_affected': 50}  # Very slow query
            
            result = self.performance_tester._test_complex_queries()
            
            self.assertEqual(result['status'], 'warning')
            self.assertIn('slow_queries', result)
    
    def test_test_n_plus_one_queries_success(self):
        """Test successful N+1 query testing."""
        with patch.object(self.performance_tester, '_detect_n_plus_one') as mock_detect:
            mock_detect.return_value = {'n_plus_one_detected': False, 'query_count': 1}
            
            result = self.performance_tester._test_n_plus_one_queries()
            
            self.assertEqual(result['status'], 'success')
            self.assertFalse(result['n_plus_one_detected'])
    
    def test_test_n_plus_one_queries_detected(self):
        """Test N+1 query testing with N+1 queries detected."""
        with patch.object(self.performance_tester, '_detect_n_plus_one') as mock_detect:
            mock_detect.return_value = {'n_plus_one_detected': True, 'query_count': 11}  # 1 + 10 queries
            
            result = self.performance_tester._test_n_plus_one_queries()
            
            self.assertEqual(result['status'], 'warning')
            self.assertTrue(result['n_plus_one_detected'])
            self.assertIn('optimization_recommendations', result)
    
    def test_detect_n_plus_one_success(self):
        """Test successful N+1 query detection."""
        with patch.object(self.performance_tester, '_count_queries') as mock_count:
            mock_count.return_value = 1  # Single query
            
            result = self.performance_tester._detect_n_plus_one()
            
            self.assertFalse(result['n_plus_one_detected'])
            self.assertEqual(result['query_count'], 1)
    
    def test_detect_n_plus_one_detected(self):
        """Test N+1 query detection with N+1 queries detected."""
        with patch.object(self.performance_tester, '_count_queries') as mock_count:
            mock_count.return_value = 11  # 1 + 10 queries
            
            result = self.performance_tester._detect_n_plus_one()
            
            self.assertTrue(result['n_plus_one_detected'])
            self.assertEqual(result['query_count'], 11)
    
    def test_analyze_slow_queries_success(self):
        """Test successful slow query analysis."""
        with patch.object(self.performance_tester, '_get_slow_queries') as mock_slow:
            mock_slow.return_value = [
                {'query': 'SELECT * FROM tickets', 'execution_time': 2000, 'rows_examined': 1000}
            ]
            
            result = self.performance_tester.analyze_slow_queries()
            
            self.assertIn('slow_queries', result)
            self.assertIn('analysis', result)
            self.assertEqual(len(result['slow_queries']), 1)
    
    def test_analyze_slow_queries_error(self):
        """Test slow query analysis with error."""
        with patch.object(self.performance_tester, '_get_slow_queries') as mock_slow:
            mock_slow.side_effect = Exception("Slow query analysis failed")
            
            result = self.performance_tester.analyze_slow_queries()
            
            self.assertIn('error', result)
            self.assertIn('Slow query analysis failed', result['error'])
    
    def test_optimize_indexes_success(self):
        """Test successful index optimization."""
        with patch.object(self.performance_tester, '_analyze_index_usage') as mock_analyze:
            mock_analyze.return_value = [
                {'table': 'tickets', 'index': 'idx_priority', 'usage': 'low'}
            ]
            
            with patch.object(self.performance_tester, '_create_index') as mock_create:
                mock_create.return_value = {'created': True, 'index_name': 'idx_optimized'}
                
                result = self.performance_tester.optimize_indexes()
                
                self.assertIn('optimization_status', result)
                self.assertIn('indexes_analyzed', result)
                self.assertIn('indexes_created', result)
    
    def test_optimize_indexes_error(self):
        """Test index optimization with error."""
        with patch.object(self.performance_tester, '_analyze_index_usage') as mock_analyze:
            mock_analyze.side_effect = Exception("Index analysis failed")
            
            result = self.performance_tester.optimize_indexes()
            
            self.assertIn('error', result)
            self.assertIn('Index analysis failed', result['error'])
    
    def test_execute_query_success(self):
        """Test successful query execution."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            mock_cursor.return_value.fetchall.return_value = [('row1',), ('row2',)]
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.05]  # 50ms execution time
                
                result = self.performance_tester._execute_query("SELECT * FROM tickets")
                
                self.assertEqual(result['execution_time'], 50)
                self.assertEqual(result['rows_affected'], 2)
    
    def test_execute_query_error(self):
        """Test query execution with error."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Query execution failed")
            
            with self.assertRaises(Exception):
                self.performance_tester._execute_query("INVALID QUERY")
    
    def test_count_queries_success(self):
        """Test successful query counting."""
        with patch('django.db.connection.queries') as mock_queries:
            mock_queries.__len__ = Mock(return_value=5)
            
            result = self.performance_tester._count_queries()
            
            self.assertEqual(result, 5)
    
    def test_count_queries_error(self):
        """Test query counting with error."""
        with patch('django.db.connection.queries') as mock_queries:
            mock_queries.__len__ = Mock(side_effect=Exception("Query counting failed"))
            
            with self.assertRaises(Exception):
                self.performance_tester._count_queries()


class QueryOptimizerTest(EnhancedTransactionTestCase):
    """Test Query Optimizer with comprehensive query optimization coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.query_optimizer = QueryOptimizer()
        
        # Create test data
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data for query optimization testing."""
        # Create users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f"user{i}@example.com",
                password="password",
                organization=self.organization,
                first_name=f"User{i}",
                last_name="Test"
            )
            self.users.append(user)
        
        # Create tickets
        self.tickets = []
        for i in range(50):
            ticket = Ticket.objects.create(
                organization=self.organization,
                customer=self.users[i % 10],
                subject=f"Test Ticket {i}",
                description=f"Test ticket description {i}",
                priority="medium",
                status="open"
            )
            self.tickets.append(ticket)
    
    def test_optimize_queries_success(self):
        """Test successful query optimization."""
        with patch.object(self.query_optimizer, '_analyze_query_performance') as mock_analyze:
            mock_analyze.return_value = {'performance_score': 0.8, 'optimization_opportunities': []}
            
            with patch.object(self.query_optimizer, '_apply_optimizations') as mock_apply:
                mock_apply.return_value = {'optimizations_applied': 0}
                
                result = self.query_optimizer.optimize_queries()
                
                self.assertIn('optimization_status', result)
                self.assertIn('performance_score', result)
                self.assertIn('optimizations_applied', result)
    
    def test_optimize_queries_optimization_opportunities(self):
        """Test query optimization with optimization opportunities."""
        with patch.object(self.query_optimizer, '_analyze_query_performance') as mock_analyze:
            mock_analyze.return_value = {
                'performance_score': 0.4,
                'optimization_opportunities': [
                    {'type': 'missing_index', 'table': 'tickets', 'column': 'priority'},
                    {'type': 'n_plus_one', 'query': 'SELECT * FROM tickets'}
                ]
            }
            
            with patch.object(self.query_optimizer, '_apply_optimizations') as mock_apply:
                mock_apply.return_value = {'optimizations_applied': 2}
                
                result = self.query_optimizer.optimize_queries()
                
                self.assertEqual(result['optimization_status'], 'optimized')
                self.assertEqual(result['optimizations_applied'], 2)
    
    def test_optimize_queries_error(self):
        """Test query optimization with error."""
        with patch.object(self.query_optimizer, '_analyze_query_performance') as mock_analyze:
            mock_analyze.side_effect = Exception("Query analysis failed")
            
            result = self.query_optimizer.optimize_queries()
            
            self.assertIn('error', result)
            self.assertIn('Query analysis failed', result['error'])
    
    def test_analyze_query_performance_success(self):
        """Test successful query performance analysis."""
        with patch.object(self.query_optimizer, '_get_query_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'execution_time': 100,
                'rows_examined': 1000,
                'rows_returned': 100
            }
            
            result = self.query_optimizer._analyze_query_performance("SELECT * FROM tickets")
            
            self.assertIn('performance_score', result)
            self.assertIn('optimization_opportunities', result)
            self.assertGreaterEqual(result['performance_score'], 0.0)
            self.assertLessEqual(result['performance_score'], 1.0)
    
    def test_analyze_query_performance_error(self):
        """Test query performance analysis with error."""
        with patch.object(self.query_optimizer, '_get_query_metrics') as mock_metrics:
            mock_metrics.side_effect = Exception("Metrics collection failed")
            
            with self.assertRaises(Exception):
                self.query_optimizer._analyze_query_performance("SELECT * FROM tickets")
    
    def test_apply_optimizations_success(self):
        """Test successful optimization application."""
        optimizations = [
            {'type': 'missing_index', 'table': 'tickets', 'column': 'priority'},
            {'type': 'n_plus_one', 'query': 'SELECT * FROM tickets'}
        ]
        
        with patch.object(self.query_optimizer, '_create_index') as mock_create_index:
            mock_create_index.return_value = {'created': True}
            
            with patch.object(self.query_optimizer, '_fix_n_plus_one') as mock_fix_n_plus_one:
                mock_fix_n_plus_one.return_value = {'fixed': True}
                
                result = self.query_optimizer._apply_optimizations(optimizations)
                
                self.assertEqual(result['optimizations_applied'], 2)
                self.assertIn('indexes_created', result)
                self.assertIn('n_plus_one_fixed', result)
    
    def test_apply_optimizations_error(self):
        """Test optimization application with error."""
        optimizations = [
            {'type': 'missing_index', 'table': 'tickets', 'column': 'priority'}
        ]
        
        with patch.object(self.query_optimizer, '_create_index') as mock_create_index:
            mock_create_index.side_effect = Exception("Index creation failed")
            
            result = self.query_optimizer._apply_optimizations(optimizations)
            
            self.assertEqual(result['optimizations_applied'], 0)
            self.assertIn('error', result)
            self.assertIn('Index creation failed', result['error'])
    
    def test_create_index_success(self):
        """Test successful index creation."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            
            result = self.query_optimizer._create_index('tickets', 'priority')
            
            self.assertTrue(result['created'])
            self.assertIn('index_name', result)
    
    def test_create_index_error(self):
        """Test index creation with error."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Index creation failed")
            
            result = self.query_optimizer._create_index('tickets', 'priority')
            
            self.assertFalse(result['created'])
            self.assertIn('error', result)
            self.assertIn('Index creation failed', result['error'])
    
    def test_fix_n_plus_one_success(self):
        """Test successful N+1 query fix."""
        with patch.object(self.query_optimizer, '_optimize_query') as mock_optimize:
            mock_optimize.return_value = {'optimized': True, 'query': 'SELECT * FROM tickets JOIN users ON tickets.customer_id = users.id'}
            
            result = self.query_optimizer._fix_n_plus_one("SELECT * FROM tickets")
            
            self.assertTrue(result['fixed'])
            self.assertIn('optimized_query', result)
    
    def test_fix_n_plus_one_error(self):
        """Test N+1 query fix with error."""
        with patch.object(self.query_optimizer, '_optimize_query') as mock_optimize:
            mock_optimize.side_effect = Exception("Query optimization failed")
            
            result = self.query_optimizer._fix_n_plus_one("SELECT * FROM tickets")
            
            self.assertFalse(result['fixed'])
            self.assertIn('error', result)
            self.assertIn('Query optimization failed', result['error'])
    
    def test_get_query_metrics_success(self):
        """Test successful query metrics collection."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            mock_cursor.return_value.fetchall.return_value = [('row1',), ('row2',)]
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.1]  # 100ms execution time
                
                result = self.query_optimizer._get_query_metrics("SELECT * FROM tickets")
                
                self.assertEqual(result['execution_time'], 100)
                self.assertEqual(result['rows_returned'], 2)
    
    def test_get_query_metrics_error(self):
        """Test query metrics collection with error."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Query execution failed")
            
            with self.assertRaises(Exception):
                self.query_optimizer._get_query_metrics("INVALID QUERY")


class DataIntegrityValidatorTest(EnhancedTransactionTestCase):
    """Test Data Integrity Validator with comprehensive data integrity testing coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.data_validator = DataIntegrityValidator()
        
        # Create test data
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data for data integrity testing."""
        # Create users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f"user{i}@example.com",
                password="password",
                organization=self.organization,
                first_name=f"User{i}",
                last_name="Test"
            )
            self.users.append(user)
        
        # Create tickets
        self.tickets = []
        for i in range(50):
            ticket = Ticket.objects.create(
                organization=self.organization,
                customer=self.users[i % 10],
                subject=f"Test Ticket {i}",
                description=f"Test ticket description {i}",
                priority="medium",
                status="open"
            )
            self.tickets.append(ticket)
    
    def test_validate_integrity_success(self):
        """Test successful data integrity validation."""
        with patch.object(self.data_validator, '_check_foreign_keys') as mock_fk:
            mock_fk.return_value = {'status': 'valid', 'issues': []}
            
            with patch.object(self.data_validator, '_check_constraints') as mock_constraints:
                mock_constraints.return_value = {'status': 'valid', 'issues': []}
                
                with patch.object(self.data_validator, '_check_data_consistency') as mock_consistency:
                    mock_consistency.return_value = {'status': 'valid', 'issues': []}
                    
                    result = self.data_validator.validate_integrity()
                    
                    self.assertEqual(result['overall_status'], 'valid')
                    self.assertIn('foreign_keys', result)
                    self.assertIn('constraints', result)
                    self.assertIn('data_consistency', result)
    
    def test_validate_integrity_issues(self):
        """Test data integrity validation with issues."""
        with patch.object(self.data_validator, '_check_foreign_keys') as mock_fk:
            mock_fk.return_value = {'status': 'invalid', 'issues': ['Orphaned records found']}
            
            with patch.object(self.data_validator, '_check_constraints') as mock_constraints:
                mock_constraints.return_value = {'status': 'valid', 'issues': []}
                
                with patch.object(self.data_validator, '_check_data_consistency') as mock_consistency:
                    mock_consistency.return_value = {'status': 'valid', 'issues': []}
                    
                    result = self.data_validator.validate_integrity()
                    
                    self.assertEqual(result['overall_status'], 'invalid')
                    self.assertIn('issues', result)
                    self.assertIn('Orphaned records found', result['issues'])
    
    def test_validate_integrity_error(self):
        """Test data integrity validation with error."""
        with patch.object(self.data_validator, '_check_foreign_keys') as mock_fk:
            mock_fk.side_effect = Exception("Foreign key check failed")
            
            result = self.data_validator.validate_integrity()
            
            self.assertEqual(result['overall_status'], 'error')
            self.assertIn('error', result)
            self.assertIn('Foreign key check failed', result['error'])
    
    def test_check_foreign_keys_success(self):
        """Test successful foreign key validation."""
        with patch.object(self.data_validator, '_check_orphaned_records') as mock_orphaned:
            mock_orphaned.return_value = {'orphaned_count': 0, 'issues': []}
            
            result = self.data_validator._check_foreign_keys()
            
            self.assertEqual(result['status'], 'valid')
            self.assertEqual(result['orphaned_count'], 0)
            self.assertEqual(len(result['issues']), 0)
    
    def test_check_foreign_keys_orphaned_records(self):
        """Test foreign key validation with orphaned records."""
        with patch.object(self.data_validator, '_check_orphaned_records') as mock_orphaned:
            mock_orphaned.return_value = {'orphaned_count': 5, 'issues': ['5 orphaned records found']}
            
            result = self.data_validator._check_foreign_keys()
            
            self.assertEqual(result['status'], 'invalid')
            self.assertEqual(result['orphaned_count'], 5)
            self.assertIn('5 orphaned records found', result['issues'])
    
    def test_check_constraints_success(self):
        """Test successful constraint validation."""
        with patch.object(self.data_validator, '_check_unique_constraints') as mock_unique:
            mock_unique.return_value = {'status': 'valid', 'issues': []}
            
            with patch.object(self.data_validator, '_check_check_constraints') as mock_check:
                mock_check.return_value = {'status': 'valid', 'issues': []}
                
                result = self.data_validator._check_constraints()
                
                self.assertEqual(result['status'], 'valid')
                self.assertEqual(len(result['issues']), 0)
    
    def test_check_constraints_violations(self):
        """Test constraint validation with violations."""
        with patch.object(self.data_validator, '_check_unique_constraints') as mock_unique:
            mock_unique.return_value = {'status': 'invalid', 'issues': ['Duplicate email found']}
            
            with patch.object(self.data_validator, '_check_check_constraints') as mock_check:
                mock_check.return_value = {'status': 'valid', 'issues': []}
                
                result = self.data_validator._check_constraints()
                
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('Duplicate email found', result['issues'])
    
    def test_check_data_consistency_success(self):
        """Test successful data consistency validation."""
        with patch.object(self.data_validator, '_check_referential_integrity') as mock_ref:
            mock_ref.return_value = {'status': 'valid', 'issues': []}
            
            with patch.object(self.data_validator, '_check_data_types') as mock_types:
                mock_types.return_value = {'status': 'valid', 'issues': []}
                
                result = self.data_validator._check_data_consistency()
                
                self.assertEqual(result['status'], 'valid')
                self.assertEqual(len(result['issues']), 0)
    
    def test_check_data_consistency_inconsistencies(self):
        """Test data consistency validation with inconsistencies."""
        with patch.object(self.data_validator, '_check_referential_integrity') as mock_ref:
            mock_ref.return_value = {'status': 'invalid', 'issues': ['Referential integrity violation']}
            
            with patch.object(self.data_validator, '_check_data_types') as mock_types:
                mock_types.return_value = {'status': 'valid', 'issues': []}
                
                result = self.data_validator._check_data_consistency()
                
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('Referential integrity violation', result['issues'])
    
    def test_repair_data_success(self):
        """Test successful data repair."""
        with patch.object(self.data_validator, '_repair_orphaned_records') as mock_repair_orphaned:
            mock_repair_orphaned.return_value = {'repaired': 5, 'status': 'success'}
            
            with patch.object(self.data_validator, '_repair_constraint_violations') as mock_repair_constraints:
                mock_repair_constraints.return_value = {'repaired': 2, 'status': 'success'}
                
                result = self.data_validator.repair_data()
                
                self.assertEqual(result['repair_status'], 'success')
                self.assertEqual(result['orphaned_records_repaired'], 5)
                self.assertEqual(result['constraint_violations_repaired'], 2)
    
    def test_repair_data_error(self):
        """Test data repair with error."""
        with patch.object(self.data_validator, '_repair_orphaned_records') as mock_repair_orphaned:
            mock_repair_orphaned.side_effect = Exception("Data repair failed")
            
            result = self.data_validator.repair_data()
            
            self.assertEqual(result['repair_status'], 'error')
            self.assertIn('error', result)
            self.assertIn('Data repair failed', result['error'])
    
    def test_check_orphaned_records_success(self):
        """Test successful orphaned records check."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            mock_cursor.return_value.fetchall.return_value = []  # No orphaned records
            
            result = self.data_validator._check_orphaned_records()
            
            self.assertEqual(result['orphaned_count'], 0)
            self.assertEqual(len(result['issues']), 0)
    
    def test_check_orphaned_records_found(self):
        """Test orphaned records check with orphaned records found."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            mock_cursor.return_value.fetchall.return_value = [
                ('orphaned1',), ('orphaned2',), ('orphaned3',)
            ]  # 3 orphaned records
            
            result = self.data_validator._check_orphaned_records()
            
            self.assertEqual(result['orphaned_count'], 3)
            self.assertIn('3 orphaned records found', result['issues'])
    
    def test_repair_orphaned_records_success(self):
        """Test successful orphaned records repair."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            
            result = self.data_validator._repair_orphaned_records()
            
            self.assertEqual(result['repaired'], 0)  # No orphaned records to repair
            self.assertEqual(result['status'], 'success')
    
    def test_repair_orphaned_records_error(self):
        """Test orphaned records repair with error."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Repair failed")
            
            result = self.data_validator._repair_orphaned_records()
            
            self.assertEqual(result['repaired'], 0)
            self.assertEqual(result['status'], 'error')
            self.assertIn('Repair failed', result['error'])


# Export test classes
__all__ = [
    'DatabasePerformanceTesterTest',
    'QueryOptimizerTest',
    'DataIntegrityValidatorTest'
]
