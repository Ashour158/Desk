#!/usr/bin/env python3
"""
Production Readiness Validation Script

Validates that all production improvements have been properly implemented.
Run this script before deploying to production.

Usage:
    python validate_production_readiness.py
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} NOT FOUND")
        return False


def check_string_in_file(file_path, search_string, description):
    """Check if a string exists in a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} NOT FOUND")
                return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False


def main():
    """Run all validation checks."""
    print("=" * 80)
    print("PRODUCTION READINESS VALIDATION")
    print("=" * 80)
    print()
    
    checks_passed = 0
    checks_failed = 0
    
    # Base directory
    base_dir = Path(__file__).resolve().parent
    core_dir = base_dir / "core"
    
    print("📁 Checking New Files...")
    print("-" * 80)
    
    # Check new files
    new_files = [
        (core_dir / "apps/common/file_validators.py", "File validators module"),
        (core_dir / "apps/common/sanitizers.py", "Input sanitizers module"),
        (core_dir / "apps/common/query_optimization.py", "Query optimization helpers"),
        (core_dir / "apps/tickets/migrations/0007_add_sla_performance_indexes.py", "SLA indexes migration"),
        (base_dir / "realtime-service/src/socketManager.js", "WebSocket connection manager"),
        (base_dir / "PRODUCTION_READINESS_CHECKLIST.md", "Production checklist"),
        (base_dir / "PRODUCTION_READINESS_IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
    ]
    
    for file_path, description in new_files:
        if check_file_exists(file_path, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    print()
    print("⚙️  Checking Configuration Changes...")
    print("-" * 80)
    
    # Check configuration changes
    config_checks = [
        (
            core_dir / "config/settings/base.py",
            "DEFAULT_THROTTLE_CLASSES",
            "Rate limiting classes configured"
        ),
        (
            core_dir / "config/settings/base.py",
            "DEFAULT_THROTTLE_RATES",
            "Rate limiting rates configured"
        ),
        (
            core_dir / "config/settings/base.py",
            "django.middleware.gzip.GZipMiddleware",
            "GZip compression middleware enabled"
        ),
        (
            core_dir / "config/settings/production.py",
            "if DEBUG:",
            "DEBUG validation in production"
        ),
        (
            core_dir / "config/settings/production.py",
            "mail_admins",
            "Admin email handler configured"
        ),
        (
            core_dir / "config/settings/production.py",
            "require_debug_false",
            "Debug filter configured"
        ),
    ]
    
    for file_path, search_string, description in config_checks:
        if check_string_in_file(file_path, search_string, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    print()
    print("💾 Checking Model Changes...")
    print("-" * 80)
    
    # Check model changes
    model_checks = [
        (
            core_dir / "apps/tickets/models.py",
            'assigned_agent", "status',
            "Assigned agent + status index"
        ),
        (
            core_dir / "apps/tickets/models.py",
            'sla_policy',
            "SLA policy index"
        ),
        (
            core_dir / "apps/tickets/models.py",
            'first_response_due',
            "First response due index"
        ),
        (
            core_dir / "apps/tickets/models.py",
            'resolution_due',
            "Resolution due index"
        ),
    ]
    
    for file_path, search_string, description in model_checks:
        if check_string_in_file(file_path, search_string, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    print()
    print("🔄 Checking Task Improvements...")
    print("-" * 80)
    
    # Check task improvements
    task_checks = [
        (
            core_dir / "apps/tickets/tasks.py",
            "MaxRetriesExceededError",
            "MaxRetriesExceededError imported"
        ),
        (
            core_dir / "apps/tickets/tasks.py",
            "max_retries=3",
            "Task retry configuration"
        ),
        (
            core_dir / "apps/tickets/tasks.py",
            "retry_backoff=True",
            "Exponential backoff enabled"
        ),
        (
            core_dir / "apps/tickets/tasks.py",
            "retry_jitter=True",
            "Retry jitter enabled"
        ),
    ]
    
    for file_path, search_string, description in task_checks:
        if check_string_in_file(file_path, search_string, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    print()
    print("📊 Validation Summary")
    print("=" * 80)
    print(f"✅ Checks Passed: {checks_passed}")
    print(f"❌ Checks Failed: {checks_failed}")
    print(f"📈 Success Rate: {(checks_passed / (checks_passed + checks_failed) * 100):.1f}%")
    print()
    
    if checks_failed == 0:
        print("🎉 All production readiness checks passed!")
        print("✅ The application is ready for production deployment.")
        print()
        print("Next steps:")
        print("1. Review PRODUCTION_READINESS_CHECKLIST.md")
        print("2. Run: python manage.py check --deploy")
        print("3. Run: python manage.py migrate --dry-run")
        print("4. Run full test suite")
        print("5. Deploy to staging first")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        print("❌ DO NOT deploy to production until all checks pass.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
