#!/usr/bin/env python3
"""
Test script to run data integrity analysis without Django management commands.
"""

import os
import sys
import django
from pathlib import Path

# Add the core directory to Python path
core_dir = Path(__file__).parent / "core"
sys.path.insert(0, str(core_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-data-integrity-analysis')

# Configure Django
django.setup()

# Now import and run the data integrity analysis
from apps.database_optimizations.data_integrity_analyzer import DataIntegrityAnalyzer

def main():
    """Run data integrity analysis."""
    print("🔍 Starting Data Integrity Analysis...")
    print("=" * 50)
    
    # Create analyzer instance
    analyzer = DataIntegrityAnalyzer()
    
    # Run comprehensive analysis
    results = analyzer.analyze_all_integrity_issues()
    
    # Display results
    print(f"\n📊 Data Integrity Analysis Results:")
    print(f"Total Issues Found: {results['total_issues']}")
    print(f"Critical Issues: {len(results['critical_issues'])}")
    print(f"Warning Issues: {len(results['warning_issues'])}")
    print(f"Info Issues: {len(results['info_issues'])}")
    
    # Display critical issues
    if results['critical_issues']:
        print(f"\n🔴 CRITICAL ISSUES ({len(results['critical_issues'])}):")
        for i, issue in enumerate(results['critical_issues'], 1):
            print(f"  {i}. {issue['type'].upper()}: {issue['description']}")
            print(f"     Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']}")
    
    # Display warning issues
    if results['warning_issues']:
        print(f"\n🟡 WARNING ISSUES ({len(results['warning_issues'])}):")
        for i, issue in enumerate(results['warning_issues'], 1):
            print(f"  {i}. {issue['type'].upper()}: {issue['description']}")
            print(f"     Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']}")
    
    # Display info issues
    if results['info_issues']:
        print(f"\nℹ️  INFO ISSUES ({len(results['info_issues'])}):")
        for i, issue in enumerate(results['info_issues'], 1):
            print(f"  {i}. {issue['type'].upper()}: {issue['description']}")
            print(f"     Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']}")
    
    # Calculate integrity score
    total_issues = results['total_issues']
    if total_issues == 0:
        integrity_score = 100
        status = "🟢 EXCELLENT"
    elif total_issues <= 5:
        integrity_score = 90
        status = "🟢 GOOD"
    elif total_issues <= 15:
        integrity_score = 75
        status = "🟡 NEEDS ATTENTION"
    elif total_issues <= 30:
        integrity_score = 60
        status = "🟠 POOR"
    else:
        integrity_score = 40
        status = "🔴 CRITICAL"
    
    print(f"\n📈 Data Integrity Score: {integrity_score}/100 ({status})")
    
    # Export report
    export_report(results)
    
    return results

def export_report(results):
    """Export detailed report to file."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data_integrity_report_{timestamp}.md'
    
    with open(filename, 'w') as f:
        f.write(f"# Data Integrity Analysis Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Summary\n")
        f.write(f"- Total Issues: {results['total_issues']}\n")
        f.write(f"- Critical Issues: {len(results['critical_issues'])}\n")
        f.write(f"- Warning Issues: {len(results['warning_issues'])}\n")
        f.write(f"- Info Issues: {len(results['info_issues'])}\n\n")
        
        if results['critical_issues']:
            f.write(f"## Critical Issues\n\n")
            for i, issue in enumerate(results['critical_issues'], 1):
                f.write(f"### {i}. {issue['type'].upper()}\n")
                f.write(f"- **Table**: {issue['table']}\n")
                f.write(f"- **Field**: {issue['field']}\n")
                f.write(f"- **Count**: {issue['count']}\n")
                f.write(f"- **Description**: {issue['description']}\n\n")
        
        if results['warning_issues']:
            f.write(f"## Warning Issues\n\n")
            for i, issue in enumerate(results['warning_issues'], 1):
                f.write(f"### {i}. {issue['type'].upper()}\n")
                f.write(f"- **Table**: {issue['table']}\n")
                f.write(f"- **Field**: {issue['field']}\n")
                f.write(f"- **Count**: {issue['count']}\n")
                f.write(f"- **Description**: {issue['description']}\n\n")
    
    print(f"\n📄 Report exported to: {filename}")

if __name__ == "__main__":
    try:
        results = main()
        print(f"\n✅ Data integrity analysis completed successfully!")
        print(f"📊 Found {results['total_issues']} total issues")
        
        if results['total_issues'] == 0:
            print("🎉 No data integrity issues found! Database is healthy.")
        else:
            print("⚠️  Data integrity issues found. Review the report for details.")
            
    except Exception as e:
        print(f"❌ Error running data integrity analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
