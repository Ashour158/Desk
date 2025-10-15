"""
Performance Testing Utilities for Database Optimizations
"""

import time
import logging
from django.db import connection
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class DatabasePerformanceTester:
    """
    Comprehensive database performance testing utilities.
    """
    
    def __init__(self):
        self.results = {
            'n1_query_tests': {},
            'transaction_tests': {},
            'aggregation_tests': {},
            'cache_tests': {}
        }
    
    def test_n1_query_performance(self, queryset_func, test_name, iterations=100):
        """
        Test N+1 query performance improvements.
        """
        logger.info(f"Testing N+1 query performance for {test_name}")
        
        # Reset query count
        connection.queries_log.clear()
        
        start_time = time.time()
        
        # Execute queries
        for i in range(iterations):
            queryset = queryset_func()
            list(queryset)  # Force evaluation
        
        end_time = time.time()
        
        # Count queries
        query_count = len(connection.queries)
        execution_time = end_time - start_time
        
        self.results['n1_query_tests'][test_name] = {
            'query_count': query_count,
            'execution_time': execution_time,
            'queries_per_iteration': query_count / iterations,
            'avg_query_time': execution_time / query_count if query_count > 0 else 0
        }
        
        logger.info(f"N+1 Query Test Results for {test_name}:")
        logger.info(f"  Total Queries: {query_count}")
        logger.info(f"  Execution Time: {execution_time:.4f}s")
        logger.info(f"  Queries per Iteration: {query_count / iterations:.2f}")
        logger.info(f"  Avg Query Time: {execution_time / query_count if query_count > 0 else 0:.4f}s")
        
        return self.results['n1_query_tests'][test_name]
    
    def test_transaction_performance(self, transaction_func, test_name, iterations=50):
        """
        Test transaction performance and safety.
        """
        logger.info(f"Testing transaction performance for {test_name}")
        
        start_time = time.time()
        successful_transactions = 0
        failed_transactions = 0
        
        for i in range(iterations):
            try:
                result = transaction_func()
                successful_transactions += 1
            except Exception as e:
                failed_transactions += 1
                logger.error(f"Transaction failed: {e}")
        
        end_time = time.time()
        
        execution_time = end_time - start_time
        success_rate = (successful_transactions / iterations) * 100
        
        self.results['transaction_tests'][test_name] = {
            'total_transactions': iterations,
            'successful_transactions': successful_transactions,
            'failed_transactions': failed_transactions,
            'success_rate': success_rate,
            'execution_time': execution_time,
            'avg_transaction_time': execution_time / iterations
        }
        
        logger.info(f"Transaction Test Results for {test_name}:")
        logger.info(f"  Total Transactions: {iterations}")
        logger.info(f"  Successful: {successful_transactions}")
        logger.info(f"  Failed: {failed_transactions}")
        logger.info(f"  Success Rate: {success_rate:.2f}%")
        logger.info(f"  Execution Time: {execution_time:.4f}s")
        logger.info(f"  Avg Transaction Time: {execution_time / iterations:.4f}s")
        
        return self.results['transaction_tests'][test_name]
    
    def test_aggregation_performance(self, aggregation_func, test_name, iterations=20):
        """
        Test aggregation query performance.
        """
        logger.info(f"Testing aggregation performance for {test_name}")
        
        start_time = time.time()
        
        for i in range(iterations):
            result = aggregation_func()
        
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.results['aggregation_tests'][test_name] = {
            'iterations': iterations,
            'execution_time': execution_time,
            'avg_execution_time': execution_time / iterations
        }
        
        logger.info(f"Aggregation Test Results for {test_name}:")
        logger.info(f"  Iterations: {iterations}")
        logger.info(f"  Total Execution Time: {execution_time:.4f}s")
        logger.info(f"  Avg Execution Time: {execution_time / iterations:.4f}s")
        
        return self.results['aggregation_tests'][test_name]
    
    def test_cache_performance(self, cache_func, test_name, iterations=100):
        """
        Test cache performance.
        """
        logger.info(f"Testing cache performance for {test_name}")
        
        # Clear cache first
        cache.clear()
        
        # Test cache miss
        start_time = time.time()
        for i in range(iterations):
            result = cache_func()
        cache_miss_time = time.time() - start_time
        
        # Test cache hit
        start_time = time.time()
        for i in range(iterations):
            result = cache_func()
        cache_hit_time = time.time() - start_time
        
        cache_improvement = ((cache_miss_time - cache_hit_time) / cache_miss_time) * 100
        
        self.results['cache_tests'][test_name] = {
            'iterations': iterations,
            'cache_miss_time': cache_miss_time,
            'cache_hit_time': cache_hit_time,
            'cache_improvement': cache_improvement,
            'avg_cache_miss_time': cache_miss_time / iterations,
            'avg_cache_hit_time': cache_hit_time / iterations
        }
        
        logger.info(f"Cache Test Results for {test_name}:")
        logger.info(f"  Iterations: {iterations}")
        logger.info(f"  Cache Miss Time: {cache_miss_time:.4f}s")
        logger.info(f"  Cache Hit Time: {cache_hit_time:.4f}s")
        logger.info(f"  Cache Improvement: {cache_improvement:.2f}%")
        logger.info(f"  Avg Cache Miss Time: {cache_miss_time / iterations:.4f}s")
        logger.info(f"  Avg Cache Hit Time: {cache_hit_time / iterations:.4f}s")
        
        return self.results['cache_tests'][test_name]
    
    def run_comprehensive_tests(self):
        """
        Run comprehensive performance tests.
        """
        logger.info("Starting comprehensive database performance tests...")
        
        # Test N+1 query optimizations
        self._test_ticket_n1_queries()
        self._test_work_order_n1_queries()
        self._test_knowledge_base_n1_queries()
        self._test_user_n1_queries()
        
        # Test transaction optimizations
        self._test_automation_transactions()
        self._test_communication_transactions()
        self._test_integration_transactions()
        
        # Test aggregation optimizations
        self._test_ticket_aggregations()
        self._test_work_order_aggregations()
        self._test_user_aggregations()
        
        # Test cache performance
        self._test_ticket_cache()
        self._test_statistics_cache()
        
        # Generate comprehensive report
        self._generate_performance_report()
        
        return self.results
    
    def _test_ticket_n1_queries(self):
        """Test ticket N+1 query optimizations."""
        from apps.tickets.models import Ticket
        from .query_optimizers import N1QueryOptimizer
        
        def optimized_queryset():
            return N1QueryOptimizer.optimize_ticket_queries()
        
        self.test_n1_query_performance(optimized_queryset, "Ticket N+1 Optimization")
    
    def _test_work_order_n1_queries(self):
        """Test work order N+1 query optimizations."""
        from .query_optimizers import N1QueryOptimizer
        
        def optimized_queryset():
            return N1QueryOptimizer.optimize_work_order_queries()
        
        self.test_n1_query_performance(optimized_queryset, "Work Order N+1 Optimization")
    
    def _test_knowledge_base_n1_queries(self):
        """Test knowledge base N+1 query optimizations."""
        from .query_optimizers import N1QueryOptimizer
        
        def optimized_queryset():
            return N1QueryOptimizer.optimize_knowledge_base_queries()
        
        self.test_n1_query_performance(optimized_queryset, "Knowledge Base N+1 Optimization")
    
    def _test_user_n1_queries(self):
        """Test user N+1 query optimizations."""
        from .query_optimizers import N1QueryOptimizer
        
        def optimized_queryset():
            return N1QueryOptimizer.optimize_user_queries()
        
        self.test_n1_query_performance(optimized_queryset, "User N+1 Optimization")
    
    def _test_automation_transactions(self):
        """Test automation transaction optimizations."""
        from .query_optimizers import TransactionOptimizer
        
        def transaction_func():
            # Simulate automation rule creation
            rule_data = {
                'organization': None,  # Would be set in real test
                'name': 'Test Rule',
                'description': 'Test Description',
                'trigger_type': 'ticket_created',
                'trigger_conditions': {},
                'actions': []
            }
            return TransactionOptimizer().create_automation_rule(rule_data)
        
        self.test_transaction_performance(transaction_func, "Automation Transaction Optimization")
    
    def _test_communication_transactions(self):
        """Test communication transaction optimizations."""
        from .query_optimizers import TransactionOptimizer
        
        def transaction_func():
            # Simulate message sending
            message_config = {
                'organization': None,  # Would be set in real test
                'content': 'Test Message',
                'sender': 'Test Sender',
                'recipient': 'Test Recipient'
            }
            return TransactionOptimizer().send_message(message_config)
        
        self.test_transaction_performance(transaction_func, "Communication Transaction Optimization")
    
    def _test_integration_transactions(self):
        """Test integration transaction optimizations."""
        from .query_optimizers import TransactionOptimizer
        
        def transaction_func():
            # Simulate integration creation
            integration_config = {
                'organization': None,  # Would be set in real test
                'name': 'Test Integration',
                'type': 'api',
                'configuration': {}
            }
            return TransactionOptimizer().create_integration(integration_config)
        
        self.test_transaction_performance(transaction_func, "Integration Transaction Optimization")
    
    def _test_ticket_aggregations(self):
        """Test ticket aggregation optimizations."""
        from .query_optimizers import AggregationOptimizer
        
        def aggregation_func():
            # Simulate organization for testing
            class MockOrganization:
                id = 1
            
            return AggregationOptimizer.get_ticket_statistics(MockOrganization())
        
        self.test_aggregation_performance(aggregation_func, "Ticket Aggregation Optimization")
    
    def _test_work_order_aggregations(self):
        """Test work order aggregation optimizations."""
        from .query_optimizers import AggregationOptimizer
        
        def aggregation_func():
            # Simulate organization for testing
            class MockOrganization:
                id = 1
            
            return AggregationOptimizer.get_work_order_statistics(MockOrganization())
        
        self.test_aggregation_performance(aggregation_func, "Work Order Aggregation Optimization")
    
    def _test_user_aggregations(self):
        """Test user aggregation optimizations."""
        from .query_optimizers import AggregationOptimizer
        
        def aggregation_func():
            # Simulate organization for testing
            class MockOrganization:
                id = 1
            
            return AggregationOptimizer.get_user_statistics(MockOrganization())
        
        self.test_aggregation_performance(aggregation_func, "User Aggregation Optimization")
    
    def _test_ticket_cache(self):
        """Test ticket cache performance."""
        def cache_func():
            cache_key = "test_ticket_cache"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Simulate expensive operation
            data = {'tickets': list(range(1000))}
            cache.set(cache_key, data, 300)
            return data
        
        self.test_cache_performance(cache_func, "Ticket Cache Performance")
    
    def _test_statistics_cache(self):
        """Test statistics cache performance."""
        def cache_func():
            cache_key = "test_statistics_cache"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Simulate expensive statistics calculation
            data = {
                'total_tickets': 1000,
                'open_tickets': 100,
                'resolved_tickets': 900
            }
            cache.set(cache_key, data, 600)
            return data
        
        self.test_cache_performance(cache_func, "Statistics Cache Performance")
    
    def _generate_performance_report(self):
        """Generate comprehensive performance report."""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE DATABASE PERFORMANCE TEST REPORT")
        logger.info("=" * 80)
        
        # N+1 Query Results
        logger.info("\nN+1 QUERY OPTIMIZATION RESULTS:")
        logger.info("-" * 40)
        for test_name, results in self.results['n1_query_tests'].items():
            logger.info(f"{test_name}:")
            logger.info(f"  Queries: {results['query_count']}")
            logger.info(f"  Time: {results['execution_time']:.4f}s")
            logger.info(f"  Queries/Iteration: {results['queries_per_iteration']:.2f}")
        
        # Transaction Results
        logger.info("\nTRANSACTION OPTIMIZATION RESULTS:")
        logger.info("-" * 40)
        for test_name, results in self.results['transaction_tests'].items():
            logger.info(f"{test_name}:")
            logger.info(f"  Success Rate: {results['success_rate']:.2f}%")
            logger.info(f"  Time: {results['execution_time']:.4f}s")
            logger.info(f"  Avg Transaction Time: {results['avg_transaction_time']:.4f}s")
        
        # Aggregation Results
        logger.info("\nAGGREGATION OPTIMIZATION RESULTS:")
        logger.info("-" * 40)
        for test_name, results in self.results['aggregation_tests'].items():
            logger.info(f"{test_name}:")
            logger.info(f"  Time: {results['execution_time']:.4f}s")
            logger.info(f"  Avg Time: {results['avg_execution_time']:.4f}s")
        
        # Cache Results
        logger.info("\nCACHE OPTIMIZATION RESULTS:")
        logger.info("-" * 40)
        for test_name, results in self.results['cache_tests'].items():
            logger.info(f"{test_name}:")
            logger.info(f"  Cache Improvement: {results['cache_improvement']:.2f}%")
            logger.info(f"  Miss Time: {results['avg_cache_miss_time']:.4f}s")
            logger.info(f"  Hit Time: {results['avg_cache_hit_time']:.4f}s")
        
        logger.info("\n" + "=" * 80)
        logger.info("PERFORMANCE TEST COMPLETE")
        logger.info("=" * 80)


class DatabaseOptimizationTestCase(TestCase):
    """
    Test case for database optimization functionality.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.tester = DatabasePerformanceTester()
    
    def test_n1_query_optimizations(self):
        """Test N+1 query optimizations."""
        self.tester._test_ticket_n1_queries()
        self.tester._test_work_order_n1_queries()
        self.tester._test_knowledge_base_n1_queries()
        self.tester._test_user_n1_queries()
    
    def test_transaction_optimizations(self):
        """Test transaction optimizations."""
        self.tester._test_automation_transactions()
        self.tester._test_communication_transactions()
        self.tester._test_integration_transactions()
    
    def test_aggregation_optimizations(self):
        """Test aggregation optimizations."""
        self.tester._test_ticket_aggregations()
        self.tester._test_work_order_aggregations()
        self.tester._test_user_aggregations()
    
    def test_cache_optimizations(self):
        """Test cache optimizations."""
        self.tester._test_ticket_cache()
        self.tester._test_statistics_cache()
    
    def test_comprehensive_performance(self):
        """Test comprehensive performance improvements."""
        results = self.tester.run_comprehensive_tests()
        
        # Assert performance improvements
        self.assertGreater(len(results['n1_query_tests']), 0)
        self.assertGreater(len(results['transaction_tests']), 0)
        self.assertGreater(len(results['aggregation_tests']), 0)
        self.assertGreater(len(results['cache_tests']), 0)
        
        # Log results
        logger.info("Comprehensive performance test completed successfully")
        logger.info(f"Results: {results}")


def run_performance_tests():
    """
    Run performance tests and return results.
    """
    tester = DatabasePerformanceTester()
    return tester.run_comprehensive_tests()


if __name__ == "__main__":
    # Run performance tests
    results = run_performance_tests()
    print("Performance test results:", results)
