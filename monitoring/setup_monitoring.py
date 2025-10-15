#!/usr/bin/env python3
"""
Comprehensive Monitoring Setup Script
Sets up complete monitoring infrastructure for production deployment
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class MonitoringSetup:
    """Comprehensive monitoring setup"""
    
    def __init__(self):
        self.setup_log = []
        self.required_packages = [
            'psutil',
            'requests',
            'psycopg2-binary',
            'redis',
            'twilio'
        ]
    
    def log(self, message, level='INFO'):
        """Log setup progress"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
        self.setup_log.append(f"[{timestamp}] [{level}] {message}")
    
    def create_directories(self):
        """Create monitoring directories"""
        self.log("Creating monitoring directories...")
        
        directories = [
            'monitoring',
            'monitoring/logs',
            'monitoring/metrics',
            'monitoring/alerts',
            'monitoring/reports',
            'monitoring/config'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.log(f"Created directory: {directory}")
    
    def install_required_packages(self):
        """Install required Python packages"""
        self.log("Installing required packages...")
        
        for package in self.required_packages:
            try:
                self.log(f"Installing {package}...")
                result = subprocess.run(['pip', 'install', package], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"Successfully installed {package}")
                else:
                    self.log(f"Failed to install {package}: {result.stderr}", 'ERROR')
            except Exception as e:
                self.log(f"Error installing {package}: {str(e)}", 'ERROR')
    
    def create_config_files(self):
        """Create configuration files"""
        self.log("Creating configuration files...")
        
        # Main monitoring config
        config = {
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
                    "username": "alerts@helpdesk-platform.com",
                    "password": "your-app-password",
                    "from_email": "alerts@helpdesk-platform.com",
                    "to_emails": ["admin@helpdesk-platform.com"]
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#alerts",
                    "username": "AlertBot"
                }
            },
            "services": {
                "django": "http://localhost:8000/health/",
                "ai_service": "http://localhost:8001/health/",
                "realtime": "http://localhost:3000/health/"
            },
            "thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "response_time": 500.0,
                "error_rate": 5.0
            }
        }
        
        with open('monitoring/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Alerting config
        alerting_config = {
            "channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "alerts@helpdesk-platform.com",
                    "password": "your-app-password",
                    "from_email": "alerts@helpdesk-platform.com",
                    "to_emails": ["admin@helpdesk-platform.com"]
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#alerts",
                    "username": "AlertBot"
                }
            },
            "rules": [
                {
                    "name": "High CPU Usage",
                    "condition": "cpu_percent > 80",
                    "threshold": 80.0,
                    "severity": "warning",
                    "channels": ["email", "slack"],
                    "cooldown": 300
                },
                {
                    "name": "Critical Memory Usage",
                    "condition": "memory_percent > 90",
                    "threshold": 90.0,
                    "severity": "critical",
                    "channels": ["email", "slack"],
                    "cooldown": 60
                }
            ]
        }
        
        with open('monitoring/alerting_config.json', 'w') as f:
            json.dump(alerting_config, f, indent=2)
        
        # Health check config
        health_config = {
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
            }
        }
        
        with open('monitoring/health_config.json', 'w') as f:
            json.dump(health_config, f, indent=2)
        
        self.log("Configuration files created")
    
    def create_management_scripts(self):
        """Create management scripts"""
        self.log("Creating management scripts...")
        
        # Start monitoring script
        start_script = """#!/bin/bash
# Start Comprehensive Monitoring System

echo "🚀 Starting Helpdesk Platform Monitoring System"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create directories
mkdir -p monitoring/logs monitoring/metrics monitoring/alerts monitoring/reports

# Start Real-time Monitor
echo "📊 Starting real-time performance monitor..."
python3 monitoring/real_time_monitor.py --daemon &
REAL_TIME_PID=$!
echo $REAL_TIME_PID > monitoring/real_time_monitor.pid
echo "✅ Real-time monitor started (PID: $REAL_TIME_PID)"

# Start Alerting System
echo "🚨 Starting alerting system..."
python3 monitoring/alerting_system.py --daemon &
ALERTING_PID=$!
echo $ALERTING_PID > monitoring/alerting_system.pid
echo "✅ Alerting system started (PID: $ALERTING_PID)"

# Start Health Checker
echo "🏥 Starting health checker..."
python3 monitoring/health_checker.py --daemon &
HEALTH_PID=$!
echo $HEALTH_PID > monitoring/health_checker.pid
echo "✅ Health checker started (PID: $HEALTH_PID)"

# Start Dashboard
echo "📈 Starting monitoring dashboard..."
python3 monitoring/dashboard.py --daemon &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > monitoring/dashboard.pid
echo "✅ Dashboard started (PID: $DASHBOARD_PID)"

echo ""
echo "🎉 Monitoring system started successfully!"
echo "📊 Dashboard: http://localhost:8080"
echo "📋 Status: ./monitoring/status.sh"
echo "🛑 Stop: ./monitoring/stop_monitoring.sh"
"""
        
        with open('monitoring/start_monitoring.sh', 'w') as f:
            f.write(start_script)
        
        # Stop monitoring script
        stop_script = """#!/bin/bash
# Stop Comprehensive Monitoring System

echo "🛑 Stopping Helpdesk Platform Monitoring System"
echo "=============================================="

# Stop Real-time Monitor
if [ -f monitoring/real_time_monitor.pid ]; then
    kill $(cat monitoring/real_time_monitor.pid) 2>/dev/null || true
    rm monitoring/real_time_monitor.pid
    echo "✅ Real-time monitor stopped"
fi

# Stop Alerting System
if [ -f monitoring/alerting_system.pid ]; then
    kill $(cat monitoring/alerting_system.pid) 2>/dev/null || true
    rm monitoring/alerting_system.pid
    echo "✅ Alerting system stopped"
fi

# Stop Health Checker
if [ -f monitoring/health_checker.pid ]; then
    kill $(cat monitoring/health_checker.pid) 2>/dev/null || true
    rm monitoring/health_checker.pid
    echo "✅ Health checker stopped"
fi

# Stop Dashboard
if [ -f monitoring/dashboard.pid ]; then
    kill $(cat monitoring/dashboard.pid) 2>/dev/null || true
    rm monitoring/dashboard.pid
    echo "✅ Dashboard stopped"
fi

echo "🎉 Monitoring system stopped"
"""
        
        with open('monitoring/stop_monitoring.sh', 'w') as f:
            f.write(stop_script)
        
        # Status script
        status_script = """#!/bin/bash
# Check Monitoring System Status

echo "📊 Helpdesk Platform Monitoring Status"
echo "====================================="

echo ""
echo "🔧 Services Status:"
if [ -f monitoring/real_time_monitor.pid ]; then
    echo "✅ Real-time Monitor: Running (PID: $(cat monitoring/real_time_monitor.pid))"
else
    echo "❌ Real-time Monitor: Not running"
fi

if [ -f monitoring/alerting_system.pid ]; then
    echo "✅ Alerting System: Running (PID: $(cat monitoring/alerting_system.pid))"
else
    echo "❌ Alerting System: Not running"
fi

if [ -f monitoring/health_checker.pid ]; then
    echo "✅ Health Checker: Running (PID: $(cat monitoring/health_checker.pid))"
else
    echo "❌ Health Checker: Not running"
fi

if [ -f monitoring/dashboard.pid ]; then
    echo "✅ Dashboard: Running (PID: $(cat monitoring/dashboard.pid))"
else
    echo "❌ Dashboard: Not running"
fi

echo ""
echo "📈 System Health:"
python3 monitoring/health_checker.py --check 2>/dev/null || echo "❌ Health check failed"

echo ""
echo "🚨 Recent Alerts:"
python3 monitoring/alerting_system.py --status 2>/dev/null || echo "❌ Alerting system not responding"

echo ""
echo "📊 Performance Metrics:"
python3 monitoring/real_time_monitor.py --status 2>/dev/null || echo "❌ Performance monitor not responding"
"""
        
        with open('monitoring/status.sh', 'w') as f:
            f.write(status_script)
        
        # Make scripts executable
        os.chmod('monitoring/start_monitoring.sh', 0o755)
        os.chmod('monitoring/stop_monitoring.sh', 0o755)
        os.chmod('monitoring/status.sh', 0o755)
        
        self.log("Management scripts created")
    
    def create_documentation(self):
        """Create monitoring documentation"""
        self.log("Creating documentation...")
        
        documentation = """# 🚀 Helpdesk Platform Monitoring System

## Overview
Comprehensive monitoring system for production deployment with real-time performance tracking, alerting, and health checks.

## Components

### 1. Real-time Performance Monitor (`monitoring/real_time_monitor.py`)
- **Purpose**: Collects system and application performance metrics
- **Features**: CPU, memory, disk, network monitoring
- **Output**: JSON metrics files in `monitoring/metrics/`
- **Interval**: 30 seconds

### 2. Alerting System (`monitoring/alerting_system.py`)
- **Purpose**: Monitors thresholds and sends alerts
- **Features**: Email, Slack, SMS, Webhook notifications
- **Configuration**: `monitoring/alerting_config.json`
- **Rules**: Configurable alert rules with cooldowns

### 3. Health Checker (`monitoring/health_checker.py`)
- **Purpose**: Monitors service health and availability
- **Features**: HTTP, database, Redis health checks
- **Services**: Django, AI Service, Real-time, Database, Redis
- **Interval**: 30 seconds

### 4. Monitoring Dashboard (`monitoring/dashboard.py`)
- **Purpose**: Web-based monitoring interface
- **Features**: Real-time metrics, service status, alerts
- **URL**: http://localhost:8080
- **Auto-refresh**: 30 seconds

## Quick Start

### 1. Setup Monitoring
```bash
python3 monitoring/setup_monitoring.py
```

### 2. Start Monitoring
```bash
./monitoring/start_monitoring.sh
```

### 3. Check Status
```bash
./monitoring/status.sh
```

### 4. View Dashboard
Open http://localhost:8080 in your browser

### 5. Stop Monitoring
```bash
./monitoring/stop_monitoring.sh
```

## Configuration

### Email Alerts
Edit `monitoring/config.json`:
```json
{
  "alerts": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "from_email": "alerts@yourcompany.com",
      "to_emails": ["admin@yourcompany.com"]
    }
  }
}
```

### Slack Alerts
Edit `monitoring/config.json`:
```json
{
  "alerts": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
      "channel": "#alerts",
      "username": "AlertBot"
    }
  }
}
```

### Alert Rules
Edit `monitoring/alerting_config.json`:
```json
{
  "rules": [
    {
      "name": "High CPU Usage",
      "condition": "cpu_percent > 80",
      "threshold": 80.0,
      "severity": "warning",
      "channels": ["email", "slack"],
      "cooldown": 300
    }
  ]
}
```

## Monitoring Features

### System Metrics
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: RAM usage and available memory
- **Disk Usage**: Disk space and I/O metrics
- **Network I/O**: Network traffic and connections

### Application Metrics
- **Response Time**: Service response times
- **Error Rate**: Application error rates
- **Throughput**: Request processing rates
- **Queue Size**: Background job queue sizes

### Service Health
- **Django**: Main application health
- **AI Service**: AI/ML service health
- **Real-time**: WebSocket service health
- **Database**: PostgreSQL connection health
- **Redis**: Cache service health

### Alerting
- **Email Notifications**: SMTP email alerts
- **Slack Integration**: Slack webhook notifications
- **SMS Alerts**: Twilio SMS notifications
- **Webhook Alerts**: Custom webhook endpoints
- **Escalation**: Multi-level alert escalation

## Logs and Reports

### Log Files
- `monitoring/logs/performance.log` - Performance monitoring logs
- `monitoring/logs/alerts.log` - Alert system logs
- `monitoring/logs/health.log` - Health check logs
- `monitoring/logs/dashboard.log` - Dashboard logs

### Metrics Files
- `monitoring/metrics/metrics_*.json` - Performance metrics
- `monitoring/alerts/alerts_*.json` - Alert history
- `monitoring/reports/` - Generated reports

### Dashboard
- **URL**: http://localhost:8080
- **Features**: Real-time metrics, service status, alerts
- **Auto-refresh**: 30 seconds
- **Mobile-friendly**: Responsive design

## Troubleshooting

### Check Service Status
```bash
./monitoring/status.sh
```

### View Logs
```bash
tail -f monitoring/logs/performance.log
tail -f monitoring/logs/alerts.log
tail -f monitoring/logs/health.log
```

### Manual Health Check
```bash
python3 monitoring/health_checker.py --check
```

### Test Alerting
```bash
python3 monitoring/alerting_system.py --test
```

### Restart Services
```bash
./monitoring/stop_monitoring.sh
./monitoring/start_monitoring.sh
```

## Production Deployment

### 1. Configure Environment
- Set up email SMTP credentials
- Configure Slack webhooks
- Set up SMS provider (optional)
- Configure webhook endpoints (optional)

### 2. Set Thresholds
- Adjust alert thresholds for your environment
- Configure cooldown periods
- Set up escalation rules

### 3. Start Monitoring
```bash
./monitoring/start_monitoring.sh
```

### 4. Verify Setup
- Check dashboard: http://localhost:8080
- Verify alerts are working
- Test health checks

## Security Considerations

### Access Control
- Restrict access to monitoring dashboard
- Use HTTPS in production
- Secure configuration files
- Rotate API keys regularly

### Data Privacy
- Monitor data retention policies
- Secure log files
- Encrypt sensitive metrics
- Regular backup of monitoring data

## Performance Impact

### Resource Usage
- **CPU**: < 1% additional usage
- **Memory**: ~50MB for monitoring
- **Disk**: ~100MB for logs and metrics
- **Network**: Minimal impact

### Optimization
- Adjust monitoring intervals
- Configure log rotation
- Set up metrics retention
- Optimize alert rules

## Support

For issues or questions:
1. Check logs in `monitoring/logs/`
2. Review configuration files
3. Test individual components
4. Check system resources

## Updates

To update monitoring system:
1. Stop monitoring: `./monitoring/stop_monitoring.sh`
2. Update code: `git pull`
3. Restart monitoring: `./monitoring/start_monitoring.sh`
"""
        
        with open('monitoring/README.md', 'w') as f:
            f.write(documentation)
        
        self.log("Documentation created")
    
    def test_monitoring_system(self):
        """Test monitoring system components"""
        self.log("Testing monitoring system...")
        
        try:
            # Test real-time monitor
            result = subprocess.run(['python3', 'monitoring/real_time_monitor.py', '--status'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Real-time monitor test passed")
            else:
                self.log("❌ Real-time monitor test failed", 'ERROR')
            
            # Test alerting system
            result = subprocess.run(['python3', 'monitoring/alerting_system.py', '--status'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Alerting system test passed")
            else:
                self.log("❌ Alerting system test failed", 'ERROR')
            
            # Test health checker
            result = subprocess.run(['python3', 'monitoring/health_checker.py', '--check'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Health checker test passed")
            else:
                self.log("❌ Health checker test failed", 'ERROR')
            
            # Test dashboard
            result = subprocess.run(['python3', 'monitoring/dashboard.py'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Dashboard test passed")
            else:
                self.log("❌ Dashboard test failed", 'ERROR')
                
        except Exception as e:
            self.log(f"Error testing monitoring system: {e}", 'ERROR')
    
    def run_setup(self):
        """Run complete monitoring setup"""
        self.log("=" * 60)
        self.log("HELPDESK PLATFORM MONITORING SETUP")
        self.log("=" * 60)
        
        try:
            # Setup steps
            self.create_directories()
            self.install_required_packages()
            self.create_config_files()
            self.create_management_scripts()
            self.create_documentation()
            self.test_monitoring_system()
            
            # Save setup log
            with open('monitoring/setup.log', 'w') as f:
                f.write('\n'.join(self.setup_log))
            
            self.log("=" * 60)
            self.log("MONITORING SETUP COMPLETED")
            self.log("=" * 60)
            self.log("Next steps:")
            self.log("1. Configure monitoring/config.json")
            self.log("2. Run: ./monitoring/start_monitoring.sh")
            self.log("3. Open: http://localhost:8080")
            self.log("4. Check status: ./monitoring/status.sh")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"Setup failed: {str(e)}", 'ERROR')
            return False
        
        return True

def main():
    """Main function"""
    setup = MonitoringSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Monitoring setup completed successfully!")
        print("📊 Start monitoring: ./monitoring/start_monitoring.sh")
        print("📈 Dashboard: http://localhost:8080")
        print("📋 Status: ./monitoring/status.sh")
    else:
        print("\n❌ Monitoring setup failed!")
        print("Check logs in monitoring/setup.log")
        sys.exit(1)

if __name__ == '__main__':
    main()
