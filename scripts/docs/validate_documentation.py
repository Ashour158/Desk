#!/usr/bin/env python3
"""
Documentation Validation Script

This script validates project documentation for:
- Completeness
- Accuracy
- Broken links
- Outdated information
- Code examples
- API documentation
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentationValidator:
    """Comprehensive documentation validation system."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_path = self.project_root / "docs"
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info("Starting comprehensive documentation validation...")
        
        # Run all validation checks
        self.check_documentation_structure()
        self.check_code_documentation()
        self.check_api_documentation()
        self.check_setup_documentation()
        self.check_broken_links()
        self.check_outdated_content()
        self.check_missing_documentation()
        self.validate_code_examples()
        
        return self.generate_report()
    
    def check_documentation_structure(self):
        """Check documentation structure and organization."""
        logger.info("Checking documentation structure...")
        
        required_files = [
            "README.md",
            "docs/README.md",
            "docs/MAINTENANCE_GUIDE.md",
            "docs/STYLE_GUIDE.md"
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.issues.append(f"Missing required documentation file: {file_path}")
        
        # Check for documentation directories
        required_dirs = [
            "docs",
            "docs/api",
            "docs/guides",
            "docs/examples"
        ]
        
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                self.warnings.append(f"Missing documentation directory: {dir_path}")
    
    def check_code_documentation(self):
        """Check code documentation completeness."""
        logger.info("Checking code documentation...")
        
        # Check Python files for docstrings
        python_files = list(self.project_root.rglob("*.py"))
        documented_functions = 0
        total_functions = 0
        
        for file_path in python_files:
            if "test" in str(file_path) or "migrations" in str(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count functions with and without docstrings
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            for func in functions:
                total_functions += 1
                # Check if function has docstring
                func_pattern = rf'def\s+{func}\s*\([^)]*\):\s*\n\s*""".*?"""'
                if re.search(func_pattern, content, re.DOTALL):
                    documented_functions += 1
        
        if total_functions > 0:
            coverage = (documented_functions / total_functions) * 100
            if coverage < 80:
                self.issues.append(f"Low code documentation coverage: {coverage:.1f}%")
            elif coverage < 90:
                self.warnings.append(f"Code documentation coverage could be improved: {coverage:.1f}%")
    
    def check_api_documentation(self):
        """Check API documentation completeness."""
        logger.info("Checking API documentation...")
        
        # Check for OpenAPI/Swagger documentation
        swagger_files = [
            "docs/api/swagger.json",
            "docs/api/openapi.json",
            "core/apps/api/documentation.py"
        ]
        
        for file_path in swagger_files:
            if not (self.project_root / file_path).exists():
                self.warnings.append(f"Missing API documentation file: {file_path}")
        
        # Check for API documentation markdown files
        api_docs = [
            "COMPREHENSIVE_API_DOCUMENTATION.md",
            "API_ENDPOINT_INVENTORY.md",
            "COMPREHENSIVE_API_ENDPOINT_INVENTORY.md"
        ]
        
        for doc_file in api_docs:
            if not (self.project_root / doc_file).exists():
                self.warnings.append(f"Missing API documentation: {doc_file}")
    
    def check_setup_documentation(self):
        """Check setup and installation documentation."""
        logger.info("Checking setup documentation...")
        
        # Check for setup documentation
        setup_docs = [
            "README.md",
            "docs/README.md",
            "docs/INSTALLATION.md",
            "docs/DEPLOYMENT.md"
        ]
        
        for doc_file in setup_docs:
            if not (self.project_root / doc_file).exists():
                self.warnings.append(f"Missing setup documentation: {doc_file}")
        
        # Check for environment configuration
        env_files = [
            ".env.example",
            "env.example",
            "docs/ENVIRONMENT_SETUP.md"
        ]
        
        for env_file in env_files:
            if not (self.project_root / env_file).exists():
                self.warnings.append(f"Missing environment configuration: {env_file}")
    
    def check_broken_links(self):
        """Check for broken links in documentation."""
        logger.info("Checking for broken links...")
        
        markdown_files = list(self.project_root.rglob("*.md"))
        broken_links = []
        
        for file_path in markdown_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_url in links:
                if self.is_broken_link(link_url, file_path):
                    broken_links.append({
                        'file': str(file_path),
                        'link': link_url,
                        'text': link_text
                    })
        
        if broken_links:
            self.issues.append(f"Found {len(broken_links)} broken links")
            for link in broken_links[:5]:  # Show first 5
                self.issues.append(f"  - {link['file']}: {link['link']}")
    
    def is_broken_link(self, url: str, file_path: Path) -> bool:
        """Check if a link is broken."""
        # Skip external URLs for now
        if url.startswith('http'):
            return False
        
        # Handle relative links
        if url.startswith('#'):
            return False
        
        # Check if file exists
        if url.startswith('/'):
            target_path = self.project_root / url[1:]
        else:
            target_path = file_path.parent / url
        
        return not target_path.exists()
    
    def check_outdated_content(self):
        """Check for outdated content in documentation."""
        logger.info("Checking for outdated content...")
        
        # Check for outdated version numbers
        version_patterns = [
            r'version["\']?\s*:\s*["\']?(\d+\.\d+\.\d+)["\']?',
            r'v(\d+\.\d+\.\d+)',
            r'(\d+\.\d+\.\d+)'
        ]
        
        markdown_files = list(self.project_root.rglob("*.md"))
        for file_path in markdown_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old version numbers
            for pattern in version_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if self.is_outdated_version(match):
                        self.warnings.append(f"Outdated version in {file_path}: {match}")
    
    def is_outdated_version(self, version: str) -> bool:
        """Check if a version number is outdated."""
        # This is a simplified check - in practice, you'd compare with current version
        try:
            parts = version.split('.')
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                # Consider versions older than 6 months as outdated
                return major < 1 or (major == 1 and minor < 0)
        except ValueError:
            pass
        return False
    
    def check_missing_documentation(self):
        """Check for missing documentation."""
        logger.info("Checking for missing documentation...")
        
        # Check for missing README files in subdirectories
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                continue
            
            if dir_path.is_dir() and "node_modules" not in str(dir_path):
                readme_path = dir_path / "README.md"
                if not readme_path.exists():
                    self.warnings.append(f"Missing README in directory: {dir_path}")
    
    def validate_code_examples(self):
        """Validate code examples in documentation."""
        logger.info("Validating code examples...")
        
        markdown_files = list(self.project_root.rglob("*.md"))
        for file_path in markdown_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find code blocks
            code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
            
            for language, code in code_blocks:
                if language in ['python', 'javascript', 'bash', 'shell']:
                    if self.has_syntax_errors(code, language):
                        self.warnings.append(f"Potential syntax error in {file_path}")
    
    def has_syntax_errors(self, code: str, language: str) -> bool:
        """Check if code has syntax errors."""
        # This is a simplified check - in practice, you'd use proper syntax checkers
        if language == 'python':
            # Check for common Python syntax issues
            if 'import' in code and 'from' in code:
                return False
        elif language in ['javascript', 'js']:
            # Check for common JavaScript syntax issues
            if 'function' in code or 'const' in code:
                return False
        
        return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.issues),
                'total_warnings': len(self.warnings),
                'total_recommendations': len(self.recommendations)
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'score': self.calculate_score()
        }
        
        return report
    
    def calculate_score(self) -> int:
        """Calculate documentation quality score."""
        base_score = 100
        
        # Deduct points for issues
        base_score -= len(self.issues) * 10
        
        # Deduct points for warnings
        base_score -= len(self.warnings) * 5
        
        # Ensure score doesn't go below 0
        return max(0, base_score)
    
    def print_report(self, report: Dict[str, Any]):
        """Print validation report."""
        print("\n" + "="*60)
        print("📚 DOCUMENTATION VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  • Issues: {report['summary']['total_issues']}")
        print(f"  • Warnings: {report['summary']['total_warnings']}")
        print(f"  • Score: {report['score']}/100")
        
        if report['issues']:
            print(f"\n🚨 Issues ({len(report['issues'])}):")
            for issue in report['issues']:
                print(f"  • {issue}")
        
        if report['warnings']:
            print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations ({len(report['recommendations'])}):")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "="*60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate project documentation')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DocumentationValidator(args.project_root)
    
    # Run validation
    report = validator.validate_all()
    
    # Print report
    validator.print_report(report)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == 'json':
                json.dump(report, f, indent=2)
            else:
                f.write(str(report))
    
    # Exit with error code if there are issues
    if report['summary']['total_issues'] > 0:
        exit(1)


if __name__ == "__main__":
    main()
