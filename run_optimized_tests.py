#!/usr/bin/env python
"""
Optimized test runner for both frontend and backend tests
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_frontend_tests():
    """Run frontend tests with optimizations"""
    print("🚀 Running Frontend Tests...")
    
    frontend_dir = Path("customer-portal")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    try:
        # Run tests with optimizations
        cmd = [
            "npm", "test", 
            "--", 
            "--watchAll=false",
            "--maxWorkers=1",
            "--bail=1",
            "--verbose=false",
            "--coverage=false"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Frontend tests passed")
            return True
        else:
            print(f"❌ Frontend tests failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Frontend tests timed out")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False
    finally:
        os.chdir("..")

def run_backend_tests():
    """Run backend tests with optimizations"""
    print("🚀 Running Backend Tests...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.test_optimized'
        
        # Run Django tests
        cmd = [
            sys.executable, 
            "core/manage_test.py",
            "core.tests.test_models"
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Backend tests passed")
            return True
        else:
            print(f"❌ Backend tests failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Backend tests timed out")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def run_performance_tests():
    """Run performance tests"""
    print("🚀 Running Performance Tests...")
    
    # Frontend performance tests
    frontend_perf = run_frontend_performance_tests()
    
    # Backend performance tests
    backend_perf = run_backend_performance_tests()
    
    return frontend_perf and backend_perf

def run_frontend_performance_tests():
    """Run frontend performance tests"""
    try:
        frontend_dir = Path("customer-portal")
        os.chdir(frontend_dir)
        
        # Run performance tests
        cmd = ["npm", "test", "--", "--testNamePattern=Performance"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        os.chdir("..")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Frontend performance test error: {e}")
        return False

def run_backend_performance_tests():
    """Run backend performance tests"""
    try:
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.test_optimized'
        
        cmd = [
            sys.executable, 
            "core/manage_test.py",
            "core.tests.test_performance"
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Backend performance test error: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 Starting Optimized Test Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run tests
    frontend_success = run_frontend_tests()
    backend_success = run_backend_tests()
    
    # Run performance tests if basic tests pass
    perf_success = True
    if frontend_success and backend_success:
        perf_success = run_performance_tests()
    
    # Calculate results
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"⏱️  Total Duration: {duration:.2f} seconds")
    print(f"🎯 Frontend Tests: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    print(f"🎯 Backend Tests: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"🎯 Performance Tests: {'✅ PASSED' if perf_success else '❌ FAILED'}")
    
    overall_success = frontend_success and backend_success and perf_success
    print(f"🏆 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(main())
