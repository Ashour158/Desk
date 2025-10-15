"""
Management command to run monitoring cycle.
"""

from django.core.management.base import BaseCommand
from apps.monitoring.services import MonitoringService


class Command(BaseCommand):
    """Run monitoring cycle command."""
    
    help = 'Run a complete monitoring cycle including metrics collection, alerting, and health checks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run monitoring continuously',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds for continuous monitoring (default: 60)',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        monitoring_service = MonitoringService()
        
        if options['continuous']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting continuous monitoring with {options['interval']}s interval"
                )
            )
            
            import time
            while True:
                try:
                    result = monitoring_service.run_monitoring_cycle()
                    if result:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Monitoring cycle completed: {result['metrics_collected']} metrics, "
                                f"{result['alerts_created']} alerts"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR("Monitoring cycle failed")
                        )
                    
                    time.sleep(options['interval'])
                    
                except KeyboardInterrupt:
                    self.stdout.write(
                        self.style.WARNING("Monitoring stopped by user")
                    )
                    break
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error in monitoring cycle: {e}")
                    )
                    time.sleep(options['interval'])
        else:
            self.stdout.write(
                self.style.SUCCESS("Running single monitoring cycle...")
            )
            
            result = monitoring_service.run_monitoring_cycle()
            if result:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Monitoring cycle completed successfully:\n"
                        f"- Metrics collected: {result['metrics_collected']}\n"
                        f"- Alerts created: {result['alerts_created']}\n"
                        f"- Health checks: {result['health_results']}\n"
                        f"- Timestamp: {result['timestamp']}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR("Monitoring cycle failed")
                )
