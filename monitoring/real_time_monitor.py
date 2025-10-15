#!/usr/bin/env python3
"""
Real-Time Performance Monitor
Comprehensive monitoring system for production deployment
"""

import os
import sys
import time
import json
import psutil
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/performance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    response_time: float
    error_rate: float
    active_connections: int
    database_connections: int
    cache_hit_rate: float
    queue_size: int
    throughput: float

@dataclass
class Alert:
    """Alert data structure"""
    timestamp: str
    severity: str
    category: str
    message: str
    metric: str
    value: float
    threshold: float
    service: str

class RealTimeMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, config_file: str = 'monitoring/config.json'):
        self.config = self.load_config(config_file)
        self.metrics_queue = queue.Queue()
        self.alerts_queue = queue.Queue()
        self.running = False
        self.monitoring_threads = []
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 500.0,  # milliseconds
            'error_rate': 5.0,  # percentage
            'cache_hit_rate': 70.0,  # percentage
            'queue_size': 1000
        }
        
        # Service endpoints
        self.services = {
            'django': 'http://localhost:8000/health/',
            'ai_service': 'http://localhost:8001/health/',
            'realtime': 'http://localhost:3000/health/',
            'database': 'postgresql://localhost:5432/helpdesk'
        }
        
        logger.info("Real-time monitor initialized")
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "monitoring": {
                "interval": 30,
                "retention_days": 30,
                "alert_cooldown": 300
            },
            "alerts": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "alerts@helpdesk-platform.com",
                    "to_emails": ["admin@helpdesk-platform.com"]
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#alerts"
                }
            },
            "services": {
                "django": "http://localhost:8000/health/",
                "ai_service": "http://localhost:8001/health/",
                "realtime": "http://localhost:3000/health/"
            }
        }
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_available_gb': memory_available,
                'disk_percent': disk_percent,
                'disk_free_gb': disk_free,
                'network_io': network_io
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def check_service_health(self, service_name: str, endpoint: str) -> Dict[str, Any]:
        """Check service health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=10)
            response_time = (time.time() - start_time) * 1000  # milliseconds
            
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'status_code': 0,
                'response_time': 10000,  # 10 seconds timeout
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error checking {service_name} health: {e}")
            return {
                'status': 'error',
                'status_code': 0,
                'response_time': 0,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        try:
            metrics = {}
            
            # Check all services
            for service_name, endpoint in self.services.items():
                if service_name != 'database':
                    health = self.check_service_health(service_name, endpoint)
                    metrics[f'{service_name}_health'] = health
            
            # Database metrics (simplified)
            try:
                import psycopg2
                conn = psycopg2.connect(self.services['database'])
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM information_schema.tables")
                table_count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                metrics['database_health'] = {
                    'status': 'healthy',
                    'table_count': table_count,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                metrics['database_health'] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {}
    
    def calculate_performance_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        
        # Calculate response time (average of all services)
        response_times = []
        for service_name in ['django', 'ai_service', 'realtime']:
            health_key = f'{service_name}_health'
            if health_key in app_metrics:
                response_times.append(app_metrics[health_key].get('response_time', 0))
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate error rate (simplified)
        error_count = 0
        total_services = 0
        for service_name in ['django', 'ai_service', 'realtime']:
            health_key = f'{service_name}_health'
            if health_key in app_metrics:
                total_services += 1
                if app_metrics[health_key].get('status') != 'healthy':
                    error_count += 1
        
        error_rate = (error_count / total_services * 100) if total_services > 0 else 0
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=system_metrics.get('cpu_percent', 0),
            memory_percent=system_metrics.get('memory_percent', 0),
            disk_percent=system_metrics.get('disk_percent', 0),
            network_io=system_metrics.get('network_io', {}),
            response_time=avg_response_time,
            error_rate=error_rate,
            active_connections=0,  # Would need database query
            database_connections=0,  # Would need database query
            cache_hit_rate=0,  # Would need cache metrics
            queue_size=0,  # Would need queue metrics
            throughput=0  # Would need request counting
        )
    
    def check_thresholds(self, metrics: PerformanceMetrics) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # CPU threshold
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity='warning',
                category='performance',
                message=f'High CPU usage: {metrics.cpu_percent:.1f}%',
                metric='cpu_percent',
                value=metrics.cpu_percent,
                threshold=self.thresholds['cpu_percent'],
                service='system'
            ))
        
        # Memory threshold
        if metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity='critical',
                category='performance',
                message=f'High memory usage: {metrics.memory_percent:.1f}%',
                metric='memory_percent',
                value=metrics.memory_percent,
                threshold=self.thresholds['memory_percent'],
                service='system'
            ))
        
        # Disk threshold
        if metrics.disk_percent > self.thresholds['disk_percent']:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity='critical',
                category='storage',
                message=f'High disk usage: {metrics.disk_percent:.1f}%',
                metric='disk_percent',
                value=metrics.disk_percent,
                threshold=self.thresholds['disk_percent'],
                service='system'
            ))
        
        # Response time threshold
        if metrics.response_time > self.thresholds['response_time']:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity='warning',
                category='performance',
                message=f'Slow response time: {metrics.response_time:.1f}ms',
                metric='response_time',
                value=metrics.response_time,
                threshold=self.thresholds['response_time'],
                service='application'
            ))
        
        # Error rate threshold
        if metrics.error_rate > self.thresholds['error_rate']:
            alerts.append(Alert(
                timestamp=datetime.now().isoformat(),
                severity='critical',
                category='reliability',
                message=f'High error rate: {metrics.error_rate:.1f}%',
                metric='error_rate',
                value=metrics.error_rate,
                threshold=self.thresholds['error_rate'],
                service='application'
            ))
        
        return alerts
    
    def send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            if not self.config['alerts']['email']['enabled']:
                return
            
            email_config = self.config['alerts']['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.service} - {alert.message}"
            
            body = f"""
Alert Details:
- Time: {alert.timestamp}
- Severity: {alert.severity.upper()}
- Service: {alert.service}
- Category: {alert.category}
- Message: {alert.message}
- Metric: {alert.metric}
- Value: {alert.value}
- Threshold: {alert.threshold}

Please investigate this issue immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert.service}")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        try:
            if not self.config['alerts']['slack']['enabled']:
                return
            
            slack_config = self.config['alerts']['slack']
            
            payload = {
                "channel": slack_config['channel'],
                "text": f"🚨 *{alert.severity.upper()} Alert*",
                "attachments": [
                    {
                        "color": "danger" if alert.severity == 'critical' else "warning",
                        "fields": [
                            {"title": "Service", "value": alert.service, "short": True},
                            {"title": "Category", "value": alert.category, "short": True},
                            {"title": "Message", "value": alert.message, "short": False},
                            {"title": "Metric", "value": f"{alert.metric}: {alert.value}", "short": True},
                            {"title": "Threshold", "value": str(alert.threshold), "short": True},
                            {"title": "Time", "value": alert.timestamp, "short": False}
                        ]
                    }
                ]
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload)
            if response.status_code == 200:
                logger.info(f"Slack alert sent for {alert.service}")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    def process_alerts(self):
        """Process alerts from queue"""
        while self.running:
            try:
                alert = self.alerts_queue.get(timeout=1)
                
                # Send email alert
                self.send_email_alert(alert)
                
                # Send Slack alert
                self.send_slack_alert(alert)
                
                # Log alert
                logger.warning(f"Alert processed: {alert.message}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
    
    def save_metrics(self, metrics: PerformanceMetrics):
        """Save metrics to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitoring/metrics_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(asdict(metrics), f, indent=2)
            
            logger.debug(f"Metrics saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        while self.running:
            try:
                # Collect metrics
                metrics = self.calculate_performance_metrics()
                
                # Save metrics
                self.save_metrics(metrics)
                
                # Check thresholds and generate alerts
                alerts = self.check_thresholds(metrics)
                
                # Queue alerts
                for alert in alerts:
                    self.alerts_queue.put(alert)
                
                # Log metrics
                logger.info(f"Metrics collected - CPU: {metrics.cpu_percent:.1f}%, "
                          f"Memory: {metrics.memory_percent:.1f}%, "
                          f"Response: {metrics.response_time:.1f}ms")
                
                # Wait for next interval
                time.sleep(self.config['monitoring']['interval'])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def start_monitoring(self):
        """Start monitoring system"""
        logger.info("Starting real-time monitoring system")
        
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.monitoring_threads.append(monitor_thread)
        
        # Start alert processing thread
        alert_thread = threading.Thread(target=self.process_alerts)
        alert_thread.daemon = True
        alert_thread.start()
        self.monitoring_threads.append(alert_thread)
        
        logger.info("Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        logger.info("Stopping monitoring system")
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.monitoring_threads:
            thread.join(timeout=5)
        
        logger.info("Monitoring system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'running': self.running,
            'threads': len(self.monitoring_threads),
            'queue_size': self.metrics_queue.qsize(),
            'alerts_queue_size': self.alerts_queue.qsize(),
            'thresholds': self.thresholds,
            'services': list(self.services.keys())
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Performance Monitor')
    parser.add_argument('--config', default='monitoring/config.json', help='Config file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--status', action='store_true', help='Show status')
    
    args = parser.parse_args()
    
    monitor = RealTimeMonitor(args.config)
    
    if args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
        return
    
    try:
        if args.daemon:
            monitor.start_monitoring()
            # Keep running
            while True:
                time.sleep(1)
        else:
            # Run once
            metrics = monitor.calculate_performance_metrics()
            print(json.dumps(asdict(metrics), indent=2))
            
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring system")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Error running monitor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
