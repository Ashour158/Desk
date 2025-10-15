"""
Management command to run comprehensive test suite.
"""
from django.core.management.base import BaseCommand, CommandError
from django.test.utils import get_runner
from django.conf import settings
import sys
import time
import json
from datetime import datetime

from tests.test_runner import ComprehensiveTestRunner


class Command(BaseCommand):
    help = 'Run comprehensive test suite for all functionalities and services'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--suite',
            type=str,
            help='Run specific test suite (models, apis, services, performance, security, integration)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
        parser.add_argument(
            '--performance',
            action='store_true',
            help='Run performance tests only',
        )
        parser.add_argument(
            '--security',
            action='store_true',
            help='Run security tests only',
        )
        parser.add_argument(
            '--integration',
            action='store_true',
            help='Run integration tests only',
        )
        parser.add_argument(
            '--report',
            type=str,
            help='Save test report to file',
        )
        parser.add_argument(
            '--parallel',
            type=int,
            default=1,
            help='Number of parallel test processes',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Comprehensive Test Suite')
        )
        
        start_time = time.time()
        
        try:
            # Initialize test runner
            runner = ComprehensiveTestRunner()
            
            # Configure runner based on options
            if options['suite']:
                runner.test_suites = [options['suite']]
            
            if options['performance']:
                runner.test_suites = ['test_performance']
            
            if options['security']:
                runner.test_suites = ['test_security']
            
            if options['integration']:
                runner.test_suites = ['test_integration']
            
            # Run tests
            results = runner.run_all_tests()
            
            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Display results
            self.display_results(results, execution_time, options)
            
            # Save report if requested
            if options['report']:
                self.save_report(results, options['report'])
            
            # Exit with appropriate code
            if results['failed_tests'] > 0:
                sys.exit(1)
            else:
                sys.exit(0)
                
        except Exception as e:
            raise CommandError(f'Test execution failed: {str(e)}')
    
    def display_results(self, results, execution_time, options):
        """Display test results."""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 TEST RESULTS SUMMARY'))
        self.stdout.write('=' * 60)
        
        # Overall statistics
        self.stdout.write(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        self.stdout.write(f"📋 Total Tests: {results['total_tests']}")
        self.stdout.write(f"✅ Passed: {results['passed_tests']}")
        self.stdout.write(f"❌ Failed: {results['failed_tests']}")
        self.stdout.write(f"⏭️  Skipped: {results['skipped_tests']}")
        
        # Success rate
        if results['total_tests'] > 0:
            success_rate = (results['passed_tests'] / results['total_tests']) * 100
            self.stdout.write(f"📈 Success Rate: {success_rate:.2f}%")
        else:
            self.stdout.write("📈 Success Rate: N/A")
        
        # System health
        if 'system_health' in results:
            health = results['system_health']
            self.stdout.write(f"\n🏥 SYSTEM HEALTH:")
            self.stdout.write(f"   Database: {health.get('database', 'Unknown')}")
            self.stdout.write(f"   Cache: {health.get('cache', 'Unknown')}")
            self.stdout.write(f"   Memory: {health.get('memory_usage_mb', 0):.2f} MB")
            self.stdout.write(f"   CPU: {health.get('cpu_usage_percent', 0):.2f}%")
        
        # Performance metrics
        if 'performance_metrics' in results:
            perf = results['performance_metrics']
            self.stdout.write(f"\n⚡ PERFORMANCE METRICS:")
            self.stdout.write(f"   Total Time: {perf.get('total_execution_time', 0):.2f}s")
            self.stdout.write(f"   Memory Usage: {perf.get('memory_usage_mb', 0):.2f} MB")
            self.stdout.write(f"   CPU Usage: {perf.get('cpu_usage_percent', 0):.2f}%")
            self.stdout.write(f"   DB Queries: {perf.get('database_queries', 0)}")
            self.stdout.write(f"   Cache Hit Rate: {perf.get('cache_hit_rate', 0):.2f}")
        
        # Test suite results
        if options['verbose']:
            self.stdout.write(f"\n📋 TEST SUITE RESULTS:")
            for suite_name, suite_results in results['test_suites'].items():
                self.stdout.write(f"\n   {suite_name.upper()}:")
                self.stdout.write(f"   Status: {suite_results.get('status', 'Unknown')}")
                self.stdout.write(f"   Time: {suite_results.get('execution_time', 0):.2f}s")
                
                if 'results' in suite_results:
                    suite_data = suite_results['results']
                    self.stdout.write(f"   Tests: {suite_data.get('total_tests', 0)}")
                    self.stdout.write(f"   Passed: {suite_data.get('passed_tests', 0)}")
                    self.stdout.write(f"   Failed: {suite_data.get('failed_tests', 0)}")
                    
                    if 'test_cases' in suite_data:
                        for test_case in suite_data['test_cases']:
                            status_icon = "✅" if test_case['status'] == 'passed' else "❌"
                            self.stdout.write(f"     {status_icon} {test_case['name']}: {test_case['message']}")
        
        # Errors
        if results['errors']:
            self.stdout.write(f"\n❌ ERRORS:")
            for error in results['errors']:
                self.stdout.write(f"   {error}")
        
        # Final status
        self.stdout.write('\n' + '=' * 60)
        if results['failed_tests'] == 0:
            self.stdout.write(self.style.SUCCESS('🎉 ALL TESTS PASSED!'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ {results["failed_tests"]} TESTS FAILED'))
        self.stdout.write('=' * 60)
    
    def save_report(self, results, filename):
        """Save test report to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            self.stdout.write(f"\n📄 Test report saved to: {filename}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to save report: {str(e)}"))
