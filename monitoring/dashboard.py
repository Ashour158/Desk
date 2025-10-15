#!/usr/bin/env python3
"""
Comprehensive Monitoring Dashboard
Real-time monitoring dashboard with web interface
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DashboardData:
    """Dashboard data structure"""
    timestamp: str
    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    services: Dict[str, Any]
    uptime: str

class MonitoringDashboard:
    """Comprehensive monitoring dashboard"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.data = DashboardData(
            timestamp=datetime.now().isoformat(),
            system_health={},
            performance_metrics={},
            alerts=[],
            services={},
            uptime="0:00:00"
        )
        self.running = False
        self.start_time = datetime.now()
        
        logger.info(f"Monitoring dashboard initialized on port {port}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health data"""
        try:
            import psutil
            
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
            
            # Determine overall health
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
                status = "critical"
            elif cpu_percent > 80 or memory_percent > 85 or disk_percent > 90:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "status": "critical" if cpu_percent > 90 else "warning" if cpu_percent > 80 else "healthy"
                },
                "memory": {
                    "percent": memory_percent,
                    "available_gb": memory_available,
                    "status": "critical" if memory_percent > 90 else "warning" if memory_percent > 85 else "healthy"
                },
                "disk": {
                    "percent": disk_percent,
                    "free_gb": disk_free,
                    "status": "critical" if disk_percent > 95 else "warning" if disk_percent > 90 else "healthy"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            import psutil
            
            # System load
            load_avg = psutil.getloadavg()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Boot time
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Network connections
            connections = len(psutil.net_connections())
            
            return {
                "load_average": {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                },
                "processes": {
                    "count": process_count,
                    "status": "warning" if process_count > 1000 else "healthy"
                },
                "uptime": {
                    "seconds": uptime_seconds,
                    "formatted": str(timedelta(seconds=int(uptime_seconds)))
                },
                "connections": {
                    "count": connections,
                    "status": "warning" if connections > 1000 else "healthy"
                }
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        services = {
            "django": {"url": "http://localhost:8000/health/", "status": "unknown"},
            "ai_service": {"url": "http://localhost:8001/health/", "status": "unknown"},
            "realtime": {"url": "http://localhost:3000/health/", "status": "unknown"},
            "database": {"url": "postgresql://localhost:5432/helpdesk", "status": "unknown"},
            "redis": {"url": "redis://localhost:6379", "status": "unknown"}
        }
        
        try:
            import requests
            
            for service_name, config in services.items():
                if service_name in ["database", "redis"]:
                    # Database and Redis checks would need specific implementations
                    services[service_name]["status"] = "unknown"
                else:
                    try:
                        response = requests.get(config["url"], timeout=5)
                        if response.status_code == 200:
                            services[service_name]["status"] = "healthy"
                        else:
                            services[service_name]["status"] = "unhealthy"
                    except:
                        services[service_name]["status"] = "unhealthy"
        except Exception as e:
            logger.error(f"Error checking service status: {e}")
        
        return services
    
    def get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        # This would typically read from alert logs or database
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "severity": "info",
                "message": "System monitoring active",
                "service": "monitoring"
            }
        ]
    
    def update_data(self):
        """Update dashboard data"""
        self.data.timestamp = datetime.now().isoformat()
        self.data.system_health = self.get_system_health()
        self.data.performance_metrics = self.get_performance_metrics()
        self.data.services = self.get_service_status()
        self.data.alerts = self.get_recent_alerts()
        
        # Calculate uptime
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        self.data.uptime = str(timedelta(seconds=int(uptime_seconds)))
    
    def data_update_loop(self):
        """Background data update loop"""
        while self.running:
            try:
                self.update_data()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error in data update loop: {e}")
                time.sleep(5)
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Helpdesk Platform Monitoring Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
        }}
        
        .card h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-healthy {{ background-color: #48bb78; }}
        .status-warning {{ background-color: #ed8936; }}
        .status-critical {{ background-color: #f56565; }}
        .status-unknown {{ background-color: #a0aec0; }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-weight: 500;
            color: #4a5568;
        }}
        
        .metric-value {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .service {{
            display: flex;
            align-items: center;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #e2e8f0;
        }}
        
        .service.healthy {{ border-left-color: #48bb78; }}
        .service.warning {{ border-left-color: #ed8936; }}
        .service.critical {{ border-left-color: #f56565; }}
        .service.unknown {{ border-left-color: #a0aec0; }}
        
        .service-name {{
            font-weight: 500;
            margin-left: 10px;
        }}
        
        .alerts {{
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .alert {{
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #e2e8f0;
        }}
        
        .alert.info {{ background: #ebf8ff; border-left-color: #3182ce; }}
        .alert.warning {{ background: #fffbeb; border-left-color: #ed8936; }}
        .alert.critical {{ background: #fed7d7; border-left-color: #f56565; }}
        
        .alert-time {{
            font-size: 0.8rem;
            color: #718096;
        }}
        
        .refresh-info {{
            text-align: center;
            color: white;
            margin-top: 20px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Helpdesk Platform Monitoring</h1>
            <p>Real-time system health and performance monitoring</p>
            <p>Last updated: {self.data.timestamp}</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Health Card -->
            <div class="card">
                <h3>🖥️ System Health</h3>
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value">
                        <span class="status-indicator status-{self.data.system_health.get('status', 'unknown')}"></span>
                        {self.data.system_health.get('status', 'unknown').title()}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value">{self.data.system_health.get('cpu', {}).get('percent', 0):.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage</span>
                    <span class="metric-value">{self.data.system_health.get('memory', {}).get('percent', 0):.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Disk Usage</span>
                    <span class="metric-value">{self.data.system_health.get('disk', {}).get('percent', 0):.1f}%</span>
                </div>
            </div>
            
            <!-- Performance Metrics Card -->
            <div class="card">
                <h3>📊 Performance Metrics</h3>
                <div class="metric">
                    <span class="metric-label">Load Average (1m)</span>
                    <span class="metric-value">{self.data.performance_metrics.get('load_average', {}).get('1min', 0):.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Processes</span>
                    <span class="metric-value">{self.data.performance_metrics.get('processes', {}).get('count', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Connections</span>
                    <span class="metric-value">{self.data.performance_metrics.get('connections', {}).get('count', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">{self.data.performance_metrics.get('uptime', {}).get('formatted', '0:00:00')}</span>
                </div>
            </div>
            
            <!-- Services Status Card -->
            <div class="card">
                <h3>🔧 Services Status</h3>
                <div class="services-grid">
                    {self.generate_services_html()}
                </div>
            </div>
            
            <!-- Recent Alerts Card -->
            <div class="card">
                <h3>🚨 Recent Alerts</h3>
                <div class="alerts">
                    {self.generate_alerts_html()}
                </div>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>Dashboard auto-refreshes every 30 seconds</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """
    
    def generate_services_html(self) -> str:
        """Generate services HTML"""
        html = ""
        for service_name, service_data in self.data.services.items():
            status = service_data.get('status', 'unknown')
            html += f"""
            <div class="service {status}">
                <span class="status-indicator status-{status}"></span>
                <span class="service-name">{service_name.title()}</span>
            </div>
            """
        return html
    
    def generate_alerts_html(self) -> str:
        """Generate alerts HTML"""
        html = ""
        for alert in self.data.alerts:
            severity = alert.get('severity', 'info')
            html += f"""
            <div class="alert {severity}">
                <div class="alert-time">{alert.get('timestamp', '')}</div>
                <div>{alert.get('message', '')}</div>
            </div>
            """
        return html

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                # Serve dashboard HTML
                dashboard.update_data()
                html = dashboard.generate_html_dashboard()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
                
            elif self.path == '/api/data':
                # Serve JSON data
                dashboard.update_data()
                data = asdict(dashboard.data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode())
                
            elif self.path == '/api/health':
                # Health check endpoint
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "healthy"}).encode())
                
            else:
                # 404 Not Found
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 Not Found')
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'500 Internal Server Error: {str(e)}'.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitoring Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run dashboard on')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    global dashboard
    dashboard = MonitoringDashboard(args.port)
    
    try:
        if args.daemon:
            # Start data update thread
            dashboard.running = True
            update_thread = threading.Thread(target=dashboard.data_update_loop)
            update_thread.daemon = True
            update_thread.start()
            
            # Start HTTP server
            server = HTTPServer(('0.0.0.0', args.port), DashboardHandler)
            logger.info(f"Dashboard server started on port {args.port}")
            logger.info(f"Access dashboard at: http://localhost:{args.port}")
            
            server.serve_forever()
        else:
            # Run once and generate HTML file
            dashboard.update_data()
            html = dashboard.generate_html_dashboard()
            
            with open('monitoring/dashboard.html', 'w') as f:
                f.write(html)
            
            logger.info("Dashboard HTML generated: monitoring/dashboard.html")
            
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard")
        dashboard.running = False
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")

if __name__ == '__main__':
    main()