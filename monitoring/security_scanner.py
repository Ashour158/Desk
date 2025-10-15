#!/usr/bin/env python3
"""
Automated Security Scanner
Daily vulnerability scanning and alerting system
"""

import subprocess
import json
import smtplib
import os
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class SecurityScanner:
    def __init__(self, config_file='monitoring/config.json'):
        self.config = self.load_config(config_file)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'python_scan': {},
            'nodejs_scan': {},
            'overall_status': 'UNKNOWN',
            'vulnerabilities': []
        }
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "slack": {
                "webhook_url": "",
                "channel": "#security-alerts"
            },
            "scan_paths": {
                "python_main": "requirements.txt",
                "python_ai": "ai-service/requirements.txt",
                "nodejs_customer": "customer-portal",
                "nodejs_realtime": "realtime-service"
            },
            "alert_thresholds": {
                "critical": 0,
                "high": 0,
                "medium": 5,
                "low": 10
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def run_python_scan(self, requirements_file):
        """Run safety scan on Python requirements"""
        try:
            result = subprocess.run(
                ['safety', 'check', '-r', requirements_file, '--json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'PASS', 'vulnerabilities': []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {'status': 'FAIL', 'vulnerabilities': vulnerabilities}
                except json.JSONDecodeError:
                    return {'status': 'ERROR', 'vulnerabilities': []}
        except Exception as e:
            return {'status': 'ERROR', 'vulnerabilities': [], 'error': str(e)}
    
    def run_nodejs_scan(self, project_path):
        """Run npm audit on Node.js project"""
        try:
            result = subprocess.run(
                ['npm', 'audit', '--audit-level=moderate', '--json'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'PASS', 'vulnerabilities': []}
            else:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get('vulnerabilities', {})
                    return {'status': 'FAIL', 'vulnerabilities': vulnerabilities}
                except json.JSONDecodeError:
                    return {'status': 'ERROR', 'vulnerabilities': []}
        except Exception as e:
            return {'status': 'ERROR', 'vulnerabilities': [], 'error': str(e)}
    
    def scan_all_projects(self):
        """Scan all projects for vulnerabilities"""
        self.log("Starting comprehensive security scan...")
        
        # Scan Python projects
        for name, path in self.config['scan_paths'].items():
            if 'python' in name:
                self.log(f"Scanning Python project: {name}")
                result = self.run_python_scan(path)
                self.results['python_scan'][name] = result
                
                if result['status'] == 'FAIL':
                    for vuln in result['vulnerabilities']:
                        self.results['vulnerabilities'].append({
                            'type': 'python',
                            'project': name,
                            'package': vuln.get('package_name', 'unknown'),
                            'version': vuln.get('installed_version', 'unknown'),
                            'severity': vuln.get('severity', 'unknown'),
                            'description': vuln.get('advisory', 'No description')
                        })
        
        # Scan Node.js projects
        for name, path in self.config['scan_paths'].items():
            if 'nodejs' in name:
                self.log(f"Scanning Node.js project: {name}")
                result = self.run_nodejs_scan(path)
                self.results['nodejs_scan'][name] = result
                
                if result['status'] == 'FAIL':
                    for vuln_name, vuln_data in result['vulnerabilities'].items():
                        self.results['vulnerabilities'].append({
                            'type': 'nodejs',
                            'project': name,
                            'package': vuln_name,
                            'severity': vuln_data.get('severity', 'unknown'),
                            'description': vuln_data.get('description', 'No description')
                        })
    
    def analyze_results(self):
        """Analyze scan results and determine overall status"""
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for vuln in self.results['vulnerabilities']:
            severity = vuln.get('severity', '').lower()
            if 'critical' in severity:
                critical_count += 1
            elif 'high' in severity:
                high_count += 1
            elif 'medium' in severity:
                medium_count += 1
            else:
                low_count += 1
        
        # Determine overall status
        if critical_count > self.config['alert_thresholds']['critical']:
            self.results['overall_status'] = 'CRITICAL'
        elif high_count > self.config['alert_thresholds']['high']:
            self.results['overall_status'] = 'HIGH'
        elif medium_count > self.config['alert_thresholds']['medium']:
            self.results['overall_status'] = 'MEDIUM'
        elif low_count > self.config['alert_thresholds']['low']:
            self.results['overall_status'] = 'LOW'
        else:
            self.results['overall_status'] = 'SECURE'
        
        self.results['summary'] = {
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
            'low': low_count,
            'total': len(self.results['vulnerabilities'])
        }
    
    def send_email_alert(self):
        """Send email alert if vulnerabilities found"""
        if self.results['overall_status'] in ['CRITICAL', 'HIGH']:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = ', '.join(self.config['email']['to_emails'])
            msg['Subject'] = f"Security Alert: {self.results['overall_status']} vulnerabilities detected"
            
            body = self.generate_alert_message()
            msg.attach(MIMEText(body, 'html'))
            
            try:
                server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
                server.starttls()
                server.login(self.config['email']['username'], self.config['email']['password'])
                server.send_message(msg)
                server.quit()
                self.log("Email alert sent successfully")
            except Exception as e:
                self.log(f"Failed to send email alert: {str(e)}", 'ERROR')
    
    def send_slack_alert(self):
        """Send Slack alert if vulnerabilities found"""
        if self.results['overall_status'] in ['CRITICAL', 'HIGH']:
            import requests
            
            message = {
                "channel": self.config['slack']['channel'],
                "text": f"🚨 Security Alert: {self.results['overall_status']} vulnerabilities detected",
                "attachments": [
                    {
                        "color": "danger" if self.results['overall_status'] == 'CRITICAL' else "warning",
                        "fields": [
                            {
                                "title": "Vulnerability Summary",
                                "value": f"Critical: {self.results['summary']['critical']}\nHigh: {self.results['summary']['high']}\nMedium: {self.results['summary']['medium']}\nLow: {self.results['summary']['low']}",
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            try:
                response = requests.post(self.config['slack']['webhook_url'], json=message)
                if response.status_code == 200:
                    self.log("Slack alert sent successfully")
                else:
                    self.log(f"Failed to send Slack alert: {response.status_code}", 'ERROR')
            except Exception as e:
                self.log(f"Failed to send Slack alert: {str(e)}", 'ERROR')
    
    def generate_alert_message(self):
        """Generate HTML alert message"""
        status_color = {
            'CRITICAL': '#ff0000',
            'HIGH': '#ff6600',
            'MEDIUM': '#ffaa00',
            'LOW': '#ffdd00',
            'SECURE': '#00ff00'
        }
        
        html = f"""
        <html>
        <body>
            <h2 style="color: {status_color.get(self.results['overall_status'], '#000000')}">
                Security Scan Results - {self.results['overall_status']}
            </h2>
            <p><strong>Scan Time:</strong> {self.results['timestamp']}</p>
            
            <h3>Vulnerability Summary</h3>
            <ul>
                <li><strong>Critical:</strong> {self.results['summary']['critical']}</li>
                <li><strong>High:</strong> {self.results['summary']['high']}</li>
                <li><strong>Medium:</strong> {self.results['summary']['medium']}</li>
                <li><strong>Low:</strong> {self.results['summary']['low']}</li>
                <li><strong>Total:</strong> {self.results['summary']['total']}</li>
            </ul>
            
            <h3>Detailed Vulnerabilities</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Type</th>
                    <th>Project</th>
                    <th>Package</th>
                    <th>Severity</th>
                    <th>Description</th>
                </tr>
        """
        
        for vuln in self.results['vulnerabilities']:
            html += f"""
                <tr>
                    <td>{vuln['type']}</td>
                    <td>{vuln['project']}</td>
                    <td>{vuln['package']}</td>
                    <td>{vuln['severity']}</td>
                    <td>{vuln['description'][:100]}...</td>
                </tr>
            """
        
        html += """
            </table>
            
            <p><em>This is an automated security scan. Please review and address any critical or high-severity vulnerabilities immediately.</em></p>
        </body>
        </html>
        """
        
        return html
    
    def save_results(self):
        """Save scan results to file"""
        results_file = f"monitoring/scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to {results_file}")
    
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_scan(self):
        """Run complete security scan"""
        self.log("Starting automated security scan...")
        
        # Scan all projects
        self.scan_all_projects()
        
        # Analyze results
        self.analyze_results()
        
        # Send alerts if needed
        if self.results['overall_status'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
            self.send_email_alert()
            self.send_slack_alert()
        
        # Save results
        self.save_results()
        
        # Print summary
        self.log("=" * 60)
        self.log("SECURITY SCAN SUMMARY")
        self.log("=" * 60)
        self.log(f"Overall Status: {self.results['overall_status']}")
        self.log(f"Total Vulnerabilities: {self.results['summary']['total']}")
        self.log(f"Critical: {self.results['summary']['critical']}")
        self.log(f"High: {self.results['summary']['high']}")
        self.log(f"Medium: {self.results['summary']['medium']}")
        self.log(f"Low: {self.results['summary']['low']}")
        self.log("=" * 60)
        
        return self.results

def main():
    """Main function"""
    scanner = SecurityScanner()
    results = scanner.run_scan()
    
    # Exit with appropriate code
    if results['overall_status'] in ['CRITICAL', 'HIGH']:
        exit(2)
    elif results['overall_status'] == 'MEDIUM':
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()
