#!/usr/bin/env python3
"""
Comprehensive Health Check System
Multi-service health monitoring with detailed diagnostics
"""

import os
import sys
import time
import json
import requests
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
import queue
import subprocess
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/health.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthCheck:
    """Health check result"""
    service: str
    status: str  # healthy, unhealthy, degraded
    timestamp: str
    response_time: float
    details: Dict[str, Any]
    errors: List[str]

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    url: str
    timeout: int
    expected_status: int
    health_endpoint: str
    dependencies: List[str]
    critical: bool = True

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self, config_file: str = 'monitoring/health_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.services = self.initialize_services()
        self.health_history = []
        self.running = False
        self.check_threads = []
        
        logger.info("Health checker initialized")
    
    def load_config(self) -> Dict[str, Any]:
        """Load health check configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "check_interval": 30,
            "timeout": 10,
            "retry_count": 3,
            "services": {
                "django": {
                    "url": "http://localhost:8000",
                    "health_endpoint": "/health/",
                    "timeout": 10,
                    "expected_status": 200,
                    "dependencies": ["database", "redis"],
                    "critical": True
                },
                "ai_service": {
                    "url": "http://localhost:8001",
                    "health_endpoint": "/health/",
                    "timeout": 10,
                    "expected_status": 200,
                    "dependencies": [],
                    "critical": False
                },
                "realtime": {
                    "url": "http://localhost:3000",
                    "health_endpoint": "/health/",
                    "timeout": 10,
                    "expected_status": 200,
                    "dependencies": [],
                    "critical": False
                },
                "database": {
                    "url": "postgresql://localhost:5432/helpdesk",
                    "health_endpoint": None,
                    "timeout": 5,
                    "expected_status": None,
                    "dependencies": [],
                    "critical": True
                },
                "redis": {
                    "url": "redis://localhost:6379",
                    "health_endpoint": None,
                    "timeout": 5,
                    "expected_status": None,
                    "dependencies": [],
                    "critical": True
                }
            },
            "system_checks": {
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "disk_threshold": 90.0,
                "network_threshold": 1000  # ms
            }
        }
    
    def initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        services = {}
        
        for name, config in self.config['services'].items():
            services[name] = ServiceConfig(
                name=name,
                url=config['url'],
                timeout=config['timeout'],
                expected_status=config.get('expected_status'),
                health_endpoint=config.get('health_endpoint'),
                dependencies=config.get('dependencies', []),
                critical=config.get('critical', True)
            )
        
        return services
    
    def check_http_service(self, service: ServiceConfig) -> HealthCheck:
        """Check HTTP service health"""
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # Build health check URL
            health_url = f"{service.url}{service.health_endpoint}" if service.health_endpoint else service.url
            
            # Make request
            response = requests.get(
                health_url,
                timeout=service.timeout,
                headers={'User-Agent': 'HealthChecker/1.0'}
            )
            
            response_time = (time.time() - start_time) * 1000  # milliseconds
            
            # Check status
            if response.status_code == service.expected_status:
                status = "healthy"
                details = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            else:
                status = "unhealthy"
                errors.append(f"Unexpected status code: {response.status_code}")
                details = {"status_code": response.status_code}
            
        except requests.exceptions.Timeout:
            status = "unhealthy"
            errors.append("Request timeout")
            response_time = service.timeout * 1000
        except requests.exceptions.ConnectionError:
            status = "unhealthy"
            errors.append("Connection refused")
            response_time = 0
        except Exception as e:
            status = "unhealthy"
            errors.append(f"Request failed: {str(e)}")
            response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            service=service.name,
            status=status,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            details=details,
            errors=errors
        )
    
    def check_database_service(self, service: ServiceConfig) -> HealthCheck:
        """Check database service health"""
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            import psycopg2
            
            # Parse connection string
            if service.url.startswith('postgresql://'):
                conn = psycopg2.connect(service.url)
                cursor = conn.cursor()
                
                # Simple query to test connection
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                response_time = (time.time() - start_time) * 1000
                
                if result and result[0] == 1:
                    status = "healthy"
                    details = {"connection": "active", "query_time": response_time}
                else:
                    status = "unhealthy"
                    errors.append("Database query failed")
                
                cursor.close()
                conn.close()
            else:
                status = "unhealthy"
                errors.append("Unsupported database type")
                
        except ImportError:
            status = "unhealthy"
            errors.append("psycopg2 not installed")
            response_time = 0
        except Exception as e:
            status = "unhealthy"
            errors.append(f"Database connection failed: {str(e)}")
            response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            service=service.name,
            status=status,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            details=details,
            errors=errors
        )
    
    def check_redis_service(self, service: ServiceConfig) -> HealthCheck:
        """Check Redis service health"""
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            import redis
            
            # Parse connection string
            if service.url.startswith('redis://'):
                r = redis.from_url(service.url)
                
                # Test connection
                r.ping()
                
                response_time = (time.time() - start_time) * 1000
                status = "healthy"
                details = {"connection": "active", "ping_time": response_time}
                
            else:
                status = "unhealthy"
                errors.append("Unsupported Redis URL format")
                response_time = 0
                
        except ImportError:
            status = "unhealthy"
            errors.append("redis-py not installed")
            response_time = 0
        except Exception as e:
            status = "unhealthy"
            errors.append(f"Redis connection failed: {str(e)}")
            response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            service=service.name,
            status=status,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            details=details,
            errors=errors
        )
    
    def check_system_health(self) -> HealthCheck:
        """Check overall system health"""
        start_time = time.time()
        errors = []
        details = {}
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                network_status = "connected"
            except:
                network_status = "disconnected"
                errors.append("No internet connectivity")
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine overall status
            if (cpu_percent > self.config['system_checks']['cpu_threshold'] or
                memory_percent > self.config['system_checks']['memory_threshold'] or
                disk_percent > self.config['system_checks']['disk_threshold']):
                status = "degraded"
            elif network_status == "disconnected":
                status = "unhealthy"
            else:
                status = "healthy"
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_status": network_status,
                "uptime": time.time() - psutil.boot_time()
            }
            
        except Exception as e:
            status = "unhealthy"
            errors.append(f"System check failed: {str(e)}")
            response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            service="system",
            status=status,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            details=details,
            errors=errors
        )
    
    def check_service_health(self, service: ServiceConfig) -> HealthCheck:
        """Check individual service health"""
        if service.name in ['database']:
            return self.check_database_service(service)
        elif service.name in ['redis']:
            return self.check_redis_service(service)
        else:
            return self.check_http_service(service)
    
    def check_all_services(self) -> List[HealthCheck]:
        """Check all configured services"""
        health_checks = []
        
        # Check system health
        system_health = self.check_system_health()
        health_checks.append(system_health)
        
        # Check individual services
        for service in self.services.values():
            health_check = self.check_service_health(service)
            health_checks.append(health_check)
        
        # Store in history
        self.health_history.extend(health_checks)
        
        # Keep only last 1000 checks
        if len(self.health_history) > 1000:
            self.health_history = self.health_history[-1000:]
        
        return health_checks
    
    def get_service_status(self, service_name: str) -> Optional[HealthCheck]:
        """Get latest status for a specific service"""
        for check in reversed(self.health_history):
            if check.service == service_name:
                return check
        return None
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        if not self.health_history:
            return {"status": "unknown", "message": "No health checks performed"}
        
        # Get latest checks
        latest_checks = {}
        for check in reversed(self.health_history):
            if check.service not in latest_checks:
                latest_checks[check.service] = check
        
        # Determine overall status
        critical_services = [s.name for s in self.services.values() if s.critical]
        unhealthy_critical = [
            name for name in critical_services
            if latest_checks.get(name, {}).status == "unhealthy"
        ]
        
        if unhealthy_critical:
            return {
                "status": "unhealthy",
                "message": f"Critical services down: {', '.join(unhealthy_critical)}",
                "services": latest_checks
            }
        
        degraded_services = [
            name for name, check in latest_checks.items()
            if check.status == "degraded"
        ]
        
        if degraded_services:
            return {
                "status": "degraded",
                "message": f"Services degraded: {', '.join(degraded_services)}",
                "services": latest_checks
            }
        
        return {
            "status": "healthy",
            "message": "All services operational",
            "services": latest_checks
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary with statistics"""
        if not self.health_history:
            return {"message": "No health data available"}
        
        # Calculate statistics
        services = set(check.service for check in self.health_history)
        summary = {}
        
        for service in services:
            service_checks = [c for c in self.health_history if c.service == service]
            
            total_checks = len(service_checks)
            healthy_checks = len([c for c in service_checks if c.status == "healthy"])
            unhealthy_checks = len([c for c in service_checks if c.status == "unhealthy"])
            degraded_checks = len([c for c in service_checks if c.status == "degraded"])
            
            avg_response_time = sum(c.response_time for c in service_checks) / total_checks
            
            summary[service] = {
                "total_checks": total_checks,
                "healthy_count": healthy_checks,
                "unhealthy_count": unhealthy_checks,
                "degraded_count": degraded_checks,
                "uptime_percent": (healthy_checks / total_checks) * 100,
                "avg_response_time": avg_response_time,
                "last_check": service_checks[-1].timestamp if service_checks else None
            }
        
        return summary
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting health monitoring loop")
        
        while self.running:
            try:
                # Perform health checks
                health_checks = self.check_all_services()
                
                # Log results
                for check in health_checks:
                    if check.status == "unhealthy":
                        logger.error(f"Service {check.service} is unhealthy: {check.errors}")
                    elif check.status == "degraded":
                        logger.warning(f"Service {check.service} is degraded")
                    else:
                        logger.info(f"Service {check.service} is healthy")
                
                # Wait for next check
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def start_monitoring(self):
        """Start health monitoring"""
        logger.info("Starting health monitoring system")
        
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.check_threads.append(monitor_thread)
        
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        logger.info("Stopping health monitoring system")
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.check_threads:
            thread.join(timeout=5)
        
        logger.info("Health monitoring stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            'running': self.running,
            'services_configured': len(self.services),
            'health_history_size': len(self.health_history),
            'overall_status': self.get_overall_status(),
            'check_interval': self.config['check_interval']
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Checker')
    parser.add_argument('--config', default='monitoring/health_config.json', help='Config file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--check', action='store_true', help='Run single health check')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--summary', action='store_true', help='Show health summary')
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.config)
    
    if args.status:
        status = checker.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.summary:
        summary = checker.get_health_summary()
        print(json.dumps(summary, indent=2))
        return
    
    if args.check:
        # Run single health check
        health_checks = checker.check_all_services()
        for check in health_checks:
            print(json.dumps(asdict(check), indent=2))
        return
    
    try:
        if args.daemon:
            checker.start_monitoring()
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("Health checker ready")
            
    except KeyboardInterrupt:
        logger.info("Shutting down health checker")
        checker.stop_monitoring()
    except Exception as e:
        logger.error(f"Error running health checker: {e}")

if __name__ == '__main__':
    main()
