"""
Monitoring services for system metrics collection and alerting.
"""

import psutil
import time
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection
from django.core.mail import send_mail
from django.conf import settings
from .models import SystemMetric, Alert, HealthCheck, MonitoringConfiguration

logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Service for collecting system metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def collect_cpu_metrics(self):
        """Collect CPU usage metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics = {
                'cpu_usage': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_frequency': cpu_freq.current if cpu_freq else None,
            }
            
            # Store metrics
            for name, value in metrics.items():
                if value is not None:
                    SystemMetric.objects.create(
                        metric_type='cpu',
                        name=name,
                        value=value,
                        unit='percent' if 'usage' in name else 'count' if 'count' in name else 'mhz',
                        metadata={'timestamp': timezone.now().isoformat()}
                    )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            return {}
    
    def collect_memory_metrics(self):
        """Collect memory usage metrics."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics = {
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'swap_usage': swap.percent,
                'swap_total': swap.total,
            }
            
            # Store metrics
            for name, value in metrics.items():
                SystemMetric.objects.create(
                    metric_type='memory',
                    name=name,
                    value=value,
                    unit='percent' if 'usage' in name else 'bytes',
                    metadata={'timestamp': timezone.now().isoformat()}
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return {}
    
    def collect_disk_metrics(self):
        """Collect disk usage metrics."""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            metrics = {
                'disk_usage': (disk_usage.used / disk_usage.total) * 100,
                'disk_free': disk_usage.free,
                'disk_total': disk_usage.total,
                'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
            }
            
            # Store metrics
            for name, value in metrics.items():
                SystemMetric.objects.create(
                    metric_type='disk',
                    name=name,
                    value=value,
                    unit='percent' if 'usage' in name else 'bytes',
                    metadata={'timestamp': timezone.now().isoformat()}
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return {}
    
    def collect_network_metrics(self):
        """Collect network usage metrics."""
        try:
            network_io = psutil.net_io_counters()
            
            metrics = {
                'network_bytes_sent': network_io.bytes_sent,
                'network_bytes_recv': network_io.bytes_recv,
                'network_packets_sent': network_io.packets_sent,
                'network_packets_recv': network_io.packets_recv,
            }
            
            # Store metrics
            for name, value in metrics.items():
                SystemMetric.objects.create(
                    metric_type='network',
                    name=name,
                    value=value,
                    unit='bytes' if 'bytes' in name else 'packets',
                    metadata={'timestamp': timezone.now().isoformat()}
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return {}
    
    def collect_database_metrics(self):
        """Collect database performance metrics."""
        try:
            start_time = time.time()
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get database size
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database())")
                db_size = cursor.fetchone()[0]
            
            metrics = {
                'db_response_time': response_time,
                'db_size': db_size,
                'db_connections': len(connection.queries),
            }
            
            # Store metrics
            for name, value in metrics.items():
                SystemMetric.objects.create(
                    metric_type='database',
                    name=name,
                    value=value,
                    unit='ms' if 'time' in name else 'bytes' if 'size' in name else 'count',
                    metadata={'timestamp': timezone.now().isoformat()}
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {}
    
    def collect_all_metrics(self):
        """Collect all system metrics."""
        logger.info("Collecting system metrics...")
        
        all_metrics = {}
        all_metrics.update(self.collect_cpu_metrics())
        all_metrics.update(self.collect_memory_metrics())
        all_metrics.update(self.collect_disk_metrics())
        all_metrics.update(self.collect_network_metrics())
        all_metrics.update(self.collect_database_metrics())
        
        logger.info(f"Collected {len(all_metrics)} metrics")
        return all_metrics


class AlertManager:
    """Service for managing alerts and notifications."""
    
    def __init__(self):
        self.configurations = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load monitoring configurations."""
        try:
            configs = MonitoringConfiguration.objects.all()
            for config in configs:
                self.configurations[config.metric_type] = config
        except Exception as e:
            logger.error(f"Error loading monitoring configurations: {e}")
    
    def check_metrics_for_alerts(self):
        """Check metrics against thresholds and create alerts."""
        logger.info("Checking metrics for alerts...")
        
        # Get recent metrics
        recent_metrics = SystemMetric.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        ).order_by('metric_type', 'name', '-timestamp')
        
        alerts_created = 0
        
        for metric in recent_metrics:
            if metric.metric_type in self.configurations:
                config = self.configurations[metric.metric_type]
                
                if not config.enabled or not config.alert_enabled:
                    continue
                
                # Check if alert already exists for this metric
                existing_alert = Alert.objects.filter(
                    metric_type=metric.metric_type,
                    status__in=['active', 'acknowledged'],
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()
                
                if existing_alert:
                    continue
                
                # Check thresholds
                severity = None
                if metric.value >= config.threshold_critical:
                    severity = 'critical'
                elif metric.value >= config.threshold_warning:
                    severity = 'medium'
                
                if severity:
                    alert = Alert.objects.create(
                        title=f"{metric.metric_type.title()} Alert: {metric.name}",
                        description=f"{metric.name} is {metric.value}{metric.unit}, exceeding {severity} threshold",
                        severity=severity,
                        metric_type=metric.metric_type,
                        threshold_value=config.threshold_critical if severity == 'critical' else config.threshold_warning,
                        actual_value=metric.value,
                        metadata={
                            'metric_name': metric.name,
                            'metric_unit': metric.unit,
                            'timestamp': metric.timestamp.isoformat()
                        }
                    )
                    
                    # Send notification
                    self._send_alert_notification(alert)
                    alerts_created += 1
        
        logger.info(f"Created {alerts_created} new alerts")
        return alerts_created
    
    def _send_alert_notification(self, alert):
        """Send alert notification."""
        try:
            if hasattr(settings, 'ALERT_EMAIL_RECIPIENTS'):
                recipients = settings.ALERT_EMAIL_RECIPIENTS
            else:
                recipients = ['admin@helpdesk.com']
            
            subject = f"[{alert.severity.upper()}] {alert.title}"
            message = f"""
Alert Details:
- Title: {alert.title}
- Description: {alert.description}
- Severity: {alert.severity}
- Metric Type: {alert.metric_type}
- Actual Value: {alert.actual_value}
- Threshold: {alert.threshold_value}
- Time: {alert.created_at}

Please check the monitoring dashboard for more details.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            logger.info(f"Alert notification sent for {alert.title}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")


class HealthChecker:
    """Service for performing health checks."""
    
    def check_database_health(self):
        """Check database health."""
        try:
            start_time = time.time()
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 1000:  # Less than 1 second
                status = 'healthy'
                error_message = ''
            else:
                status = 'degraded'
                error_message = f'Slow response time: {response_time}ms'
            
            HealthCheck.objects.create(
                service_name='Database',
                service_type='database',
                status=status,
                response_time=response_time,
                error_message=error_message,
                metadata={'check_type': 'connectivity'}
            )
            
            return status == 'healthy'
            
        except Exception as e:
            HealthCheck.objects.create(
                service_name='Database',
                service_type='database',
                status='unhealthy',
                error_message=str(e),
                metadata={'check_type': 'connectivity'}
            )
            return False
    
    def check_redis_health(self):
        """Check Redis health."""
        try:
            import redis
            
            r = redis.from_url(settings.CACHES['default']['LOCATION'])
            start_time = time.time()
            
            r.ping()
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 100:  # Less than 100ms
                status = 'healthy'
                error_message = ''
            else:
                status = 'degraded'
                error_message = f'Slow response time: {response_time}ms'
            
            HealthCheck.objects.create(
                service_name='Redis',
                service_type='redis',
                status=status,
                response_time=response_time,
                error_message=error_message,
                metadata={'check_type': 'connectivity'}
            )
            
            return status == 'healthy'
            
        except Exception as e:
            HealthCheck.objects.create(
                service_name='Redis',
                service_type='redis',
                status='unhealthy',
                error_message=str(e),
                metadata={'check_type': 'connectivity'}
            )
            return False
    
    def check_email_health(self):
        """Check email service health."""
        try:
            # Test email configuration
            from django.core.mail import get_connection
            
            connection = get_connection()
            connection.open()
            connection.close()
            
            HealthCheck.objects.create(
                service_name='Email',
                service_type='email',
                status='healthy',
                response_time=0,
                error_message='',
                metadata={'check_type': 'configuration'}
            )
            
            return True
            
        except Exception as e:
            HealthCheck.objects.create(
                service_name='Email',
                service_type='email',
                status='unhealthy',
                error_message=str(e),
                metadata={'check_type': 'configuration'}
            )
            return False
    
    def run_all_health_checks(self):
        """Run all health checks."""
        logger.info("Running health checks...")
        
        results = {
            'database': self.check_database_health(),
            'redis': self.check_redis_health(),
            'email': self.check_email_health(),
        }
        
        healthy_services = sum(1 for status in results.values() if status)
        total_services = len(results)
        
        logger.info(f"Health check results: {healthy_services}/{total_services} services healthy")
        return results


class MonitoringService:
    """Main monitoring service that orchestrates all monitoring activities."""
    
    def __init__(self):
        self.metrics_collector = SystemMetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle."""
        logger.info("Starting monitoring cycle...")
        
        try:
            # Collect metrics
            metrics = self.metrics_collector.collect_all_metrics()
            
            # Check for alerts
            alerts_created = self.alert_manager.check_metrics_for_alerts()
            
            # Run health checks
            health_results = self.health_checker.run_all_health_checks()
            
            # Clean up old data
            self._cleanup_old_data()
            
            logger.info("Monitoring cycle completed successfully")
            
            return {
                'metrics_collected': len(metrics),
                'alerts_created': alerts_created,
                'health_results': health_results,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            return None
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        try:
            # Clean up old metrics (keep last 30 days)
            cutoff_date = timezone.now() - timedelta(days=30)
            old_metrics = SystemMetric.objects.filter(timestamp__lt=cutoff_date)
            metrics_deleted = old_metrics.count()
            old_metrics.delete()
            
            # Clean up old health checks (keep last 7 days)
            cutoff_date = timezone.now() - timedelta(days=7)
            old_health_checks = HealthCheck.objects.filter(checked_at__lt=cutoff_date)
            health_checks_deleted = old_health_checks.count()
            old_health_checks.delete()
            
            logger.info(f"Cleaned up {metrics_deleted} old metrics and {health_checks_deleted} old health checks")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
