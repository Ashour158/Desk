#!/usr/bin/env python3
"""
Performance Monitoring System
Real-time performance tracking and alerting
"""

import psutil
import requests
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, config_file='monitoring/config.json'):
        self.config = self.load_config(config_file)
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'application': {},
            'alerts': []
        }
    
    def load_config(self, config_file):
        """Load configuration"""
        default_config = {
            "endpoints": {
                "api": "http://localhost:8000/api/health",
                "ai_service": "http://localhost:8001/health",
                "frontend": "http://localhost:3000",
                "realtime": "http://localhost:8002/health"
            },
            "thresholds": {
                "response_time": 500,
                "error_rate": 2.0,
                "memory_usage": 80,
                "cpu_usage": 90,
                "disk_usage": 85
            },
            "alerting": {
                "email": True,
                "slack": True,
                "log_file": True
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def get_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_gb': round(memory_available, 2),
                'disk_percent': disk_percent,
                'disk_free_gb': round(disk_free, 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.log(f"Error collecting system metrics: {str(e)}", 'ERROR')
            return {}
    
    def check_endpoint_health(self, name, url):
        """Check health of application endpoint"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'status': 'UP' if response.status_code == 200 else 'DOWN',
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.Timeout:
            return {
                'name': name,
                'url': url,
                'status_code': 0,
                'response_time_ms': 10000,
                'status': 'TIMEOUT',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': name,
                'url': url,
                'status_code': 0,
                'response_time_ms': 0,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all_endpoints(self):
        """Check health of all application endpoints"""
        endpoints = self.config.get('endpoints', {})
        results = []
        
        for name, url in endpoints.items():
            result = self.check_endpoint_health(name, url)
            results.append(result)
        
        return results
    
    def analyze_metrics(self):
        """Analyze metrics and generate alerts"""
        alerts = []
        thresholds = self.config.get('thresholds', {})
        
        # Check system metrics
        system_metrics = self.metrics.get('system', {})
        
        if system_metrics.get('cpu_percent', 0) > thresholds.get('cpu_usage', 90):
            alerts.append({
                'type': 'CPU_HIGH',
                'severity': 'WARNING',
                'message': f"High CPU usage: {system_metrics.get('cpu_percent', 0)}%",
                'value': system_metrics.get('cpu_percent', 0),
                'threshold': thresholds.get('cpu_usage', 90)
            })
        
        if system_metrics.get('memory_percent', 0) > thresholds.get('memory_usage', 80):
            alerts.append({
                'type': 'MEMORY_HIGH',
                'severity': 'WARNING',
                'message': f"High memory usage: {system_metrics.get('memory_percent', 0)}%",
                'value': system_metrics.get('memory_percent', 0),
                'threshold': thresholds.get('memory_usage', 80)
            })
        
        if system_metrics.get('disk_percent', 0) > thresholds.get('disk_usage', 85):
            alerts.append({
                'type': 'DISK_HIGH',
                'severity': 'CRITICAL',
                'message': f"High disk usage: {system_metrics.get('disk_percent', 0)}%",
                'value': system_metrics.get('disk_percent', 0),
                'threshold': thresholds.get('disk_usage', 85)
            })
        
        # Check application metrics
        application_metrics = self.metrics.get('application', [])
        
        for endpoint in application_metrics:
            if endpoint.get('status') != 'UP':
                alerts.append({
                    'type': 'ENDPOINT_DOWN',
                    'severity': 'CRITICAL',
                    'message': f"Endpoint {endpoint.get('name')} is {endpoint.get('status')}",
                    'endpoint': endpoint.get('name'),
                    'status': endpoint.get('status')
                })
            
            response_time = endpoint.get('response_time_ms', 0)
            if response_time > thresholds.get('response_time', 500):
                alerts.append({
                    'type': 'SLOW_RESPONSE',
                    'severity': 'WARNING',
                    'message': f"Slow response from {endpoint.get('name')}: {response_time}ms",
                    'endpoint': endpoint.get('name'),
                    'response_time': response_time,
                    'threshold': thresholds.get('response_time', 500)
                })
        
        self.metrics['alerts'] = alerts
        return alerts
    
    def send_alerts(self, alerts):
        """Send alerts via configured channels"""
        if not alerts:
            return
        
        for alert in alerts:
            if alert['severity'] in ['CRITICAL', 'WARNING']:
                self.log(f"ALERT: {alert['message']}", 'WARNING')
                
                # Send to log file
                if self.config.get('alerting', {}).get('log_file', True):
                    self.log_to_file(alert)
                
                # Send email (implement if needed)
                if self.config.get('alerting', {}).get('email', False):
                    self.send_email_alert(alert)
                
                # Send Slack (implement if needed)
                if self.config.get('alerting', {}).get('slack', False):
                    self.send_slack_alert(alert)
    
    def log_to_file(self, alert):
        """Log alert to file"""
        log_file = f"monitoring/alerts_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {alert['severity']} - {alert['message']}\n")
    
    def send_email_alert(self, alert):
        """Send email alert (placeholder)"""
        # Implement email sending logic here
        pass
    
    def send_slack_alert(self, alert):
        """Send Slack alert (placeholder)"""
        # Implement Slack webhook logic here
        pass
    
    def generate_report(self):
        """Generate performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self.metrics.get('system', {}),
            'application_metrics': self.metrics.get('application', []),
            'alerts': self.metrics.get('alerts', []),
            'summary': {
                'total_endpoints': len(self.metrics.get('application', [])),
                'up_endpoints': len([e for e in self.metrics.get('application', []) if e.get('status') == 'UP']),
                'down_endpoints': len([e for e in self.metrics.get('application', []) if e.get('status') != 'UP']),
                'total_alerts': len(self.metrics.get('alerts', [])),
                'critical_alerts': len([a for a in self.metrics.get('alerts', []) if a.get('severity') == 'CRITICAL']),
                'warning_alerts': len([a for a in self.metrics.get('alerts', []) if a.get('severity') == 'WARNING'])
            }
        }
        
        return report
    
    def save_metrics(self):
        """Save metrics to file"""
        metrics_file = f"monitoring/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        self.log(f"Metrics saved to {metrics_file}")
    
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        self.log("Starting performance monitoring cycle...")
        
        # Collect system metrics
        self.metrics['system'] = self.get_system_metrics()
        
        # Check application endpoints
        self.metrics['application'] = self.check_all_endpoints()
        
        # Analyze metrics and generate alerts
        alerts = self.analyze_metrics()
        
        # Send alerts if any
        self.send_alerts(alerts)
        
        # Save metrics
        self.save_metrics()
        
        # Generate and print report
        report = self.generate_report()
        
        self.log("=" * 60)
        self.log("PERFORMANCE MONITORING REPORT")
        self.log("=" * 60)
        self.log(f"System CPU: {self.metrics['system'].get('cpu_percent', 0)}%")
        self.log(f"System Memory: {self.metrics['system'].get('memory_percent', 0)}%")
        self.log(f"System Disk: {self.metrics['system'].get('disk_percent', 0)}%")
        self.log(f"Endpoints UP: {report['summary']['up_endpoints']}/{report['summary']['total_endpoints']}")
        self.log(f"Total Alerts: {report['summary']['total_alerts']}")
        self.log(f"Critical Alerts: {report['summary']['critical_alerts']}")
        self.log(f"Warning Alerts: {report['summary']['warning_alerts']}")
        self.log("=" * 60)
        
        return report

def main():
    """Main function"""
    monitor = PerformanceMonitor()
    report = monitor.run_monitoring_cycle()
    
    # Exit with appropriate code based on alerts
    if report['summary']['critical_alerts'] > 0:
        exit(2)
    elif report['summary']['warning_alerts'] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()
