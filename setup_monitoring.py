#!/usr/bin/env python3
"""
Monitoring Setup Script
Sets up comprehensive monitoring system for security and performance
"""

import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class MonitoringSetup:
    def __init__(self):
        self.setup_log = []
        self.required_packages = [
            'psutil',
            'requests',
            'safety',
            'pip-audit'
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
            'monitoring/reports',
            'monitoring/alerts',
            'monitoring/metrics'
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
    
    def create_cron_jobs(self):
        """Create cron jobs for automated monitoring"""
        self.log("Setting up automated monitoring...")
        
        cron_entries = [
            "# Security scanning - daily at 2 AM",
            "0 2 * * * cd /path/to/project && python monitoring/security_scanner.py >> monitoring/logs/security_scan.log 2>&1",
            "",
            "# Performance monitoring - every 5 minutes",
            "*/5 * * * * cd /path/to/project && python monitoring/performance_monitor.py >> monitoring/logs/performance.log 2>&1",
            "",
            "# Dashboard update - every minute",
            "* * * * * cd /path/to/project && python monitoring/dashboard.py >> monitoring/logs/dashboard.log 2>&1"
        ]
        
        cron_file = 'monitoring/cron_jobs.txt'
        with open(cron_file, 'w') as f:
            f.write('\n'.join(cron_entries))
        
        self.log(f"Cron jobs saved to {cron_file}")
        self.log("To activate cron jobs, run: crontab monitoring/cron_jobs.txt")
    
    def create_systemd_services(self):
        """Create systemd services for monitoring"""
        self.log("Creating systemd services...")
        
        # Security scanner service
        security_service = f"""[Unit]
Description=Helpdesk Security Scanner
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python3 monitoring/security_scanner.py
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
"""
        
        with open('monitoring/helpdesk-security.service', 'w') as f:
            f.write(security_service)
        
        # Performance monitor service
        performance_service = f"""[Unit]
Description=Helpdesk Performance Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python3 monitoring/performance_monitor.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
"""
        
        with open('monitoring/helpdesk-performance.service', 'w') as f:
            f.write(performance_service)
        
        self.log("Systemd services created")
        self.log("To install services, run:")
        self.log("sudo cp monitoring/*.service /etc/systemd/system/")
        self.log("sudo systemctl daemon-reload")
        self.log("sudo systemctl enable helpdesk-security helpdesk-performance")
        self.log("sudo systemctl start helpdesk-security helpdesk-performance")
    
    def create_monitoring_scripts(self):
        """Create monitoring management scripts"""
        self.log("Creating monitoring management scripts...")
        
        # Start monitoring script
        start_script = """#!/bin/bash
# Start Helpdesk Monitoring System

echo "Starting Helpdesk Monitoring System..."

# Start security scanner
python3 monitoring/security_scanner.py &
SECURITY_PID=$!

# Start performance monitor
python3 monitoring/performance_monitor.py &
PERFORMANCE_PID=$!

# Start dashboard
python3 monitoring/dashboard.py &
DASHBOARD_PID=$!

echo "Monitoring system started:"
echo "Security Scanner PID: $SECURITY_PID"
echo "Performance Monitor PID: $PERFORMANCE_PID"
echo "Dashboard PID: $DASHBOARD_PID"

# Save PIDs
echo $SECURITY_PID > monitoring/security.pid
echo $PERFORMANCE_PID > monitoring/performance.pid
echo $DASHBOARD_PID > monitoring/dashboard.pid

echo "PIDs saved to monitoring/*.pid files"
echo "To stop monitoring, run: ./monitoring/stop_monitoring.sh"
"""
        
        with open('monitoring/start_monitoring.sh', 'w') as f:
            f.write(start_script)
        
        # Stop monitoring script
        stop_script = """#!/bin/bash
# Stop Helpdesk Monitoring System

echo "Stopping Helpdesk Monitoring System..."

# Read PIDs and kill processes
if [ -f monitoring/security.pid ]; then
    kill $(cat monitoring/security.pid) 2>/dev/null
    rm monitoring/security.pid
fi

if [ -f monitoring/performance.pid ]; then
    kill $(cat monitoring/performance.pid) 2>/dev/null
    rm monitoring/performance.pid
fi

if [ -f monitoring/dashboard.pid ]; then
    kill $(cat monitoring/dashboard.pid) 2>/dev/null
    rm monitoring/dashboard.pid
fi

echo "Monitoring system stopped"
"""
        
        with open('monitoring/stop_monitoring.sh', 'w') as f:
            f.write(stop_script)
        
        # Make scripts executable
        os.chmod('monitoring/start_monitoring.sh', 0o755)
        os.chmod('monitoring/stop_monitoring.sh', 0o755)
        
        self.log("Monitoring management scripts created")
    
    def test_monitoring_system(self):
        """Test the monitoring system"""
        self.log("Testing monitoring system...")
        
        try:
            # Test security scanner
            self.log("Testing security scanner...")
            result = subprocess.run(['python3', 'monitoring/security_scanner.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode in [0, 1, 2]:
                self.log("Security scanner test completed")
            else:
                self.log("Security scanner test failed", 'ERROR')
            
            # Test performance monitor
            self.log("Testing performance monitor...")
            result = subprocess.run(['python3', 'monitoring/performance_monitor.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode in [0, 1, 2]:
                self.log("Performance monitor test completed")
            else:
                self.log("Performance monitor test failed", 'ERROR')
            
            # Test dashboard
            self.log("Testing dashboard...")
            result = subprocess.run(['python3', 'monitoring/dashboard.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log("Dashboard test completed")
            else:
                self.log("Dashboard test failed", 'ERROR')
            
        except Exception as e:
            self.log(f"Error testing monitoring system: {str(e)}", 'ERROR')
    
    def create_documentation(self):
        """Create monitoring documentation"""
        self.log("Creating monitoring documentation...")
        
        documentation = """# Helpdesk Monitoring System

## Overview
Comprehensive monitoring system for security and performance tracking.

## Components

### 1. Security Scanner (`monitoring/security_scanner.py`)
- Daily vulnerability scanning
- Email and Slack alerts
- JSON report generation

### 2. Performance Monitor (`monitoring/performance_monitor.py`)
- Real-time system metrics
- Application health checks
- Performance alerting

### 3. Dashboard (`monitoring/dashboard.py`)
- Web-based monitoring interface
- Real-time status display
- Alert management

## Quick Start

### Start Monitoring
```bash
./monitoring/start_monitoring.sh
```

### Stop Monitoring
```bash
./monitoring/stop_monitoring.sh
```

### View Dashboard
Open `monitoring/dashboard.html` in your browser

## Configuration

Edit `monitoring/config.json` to configure:
- Email settings
- Slack webhooks
- Alert thresholds
- Scan paths

## Automated Monitoring

### Cron Jobs
```bash
crontab monitoring/cron_jobs.txt
```

### Systemd Services
```bash
sudo cp monitoring/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-security helpdesk-performance
sudo systemctl start helpdesk-security helpdesk-performance
```

## Logs and Reports

- Security scan results: `monitoring/scan_results_*.json`
- Performance metrics: `monitoring/metrics_*.json`
- Alert logs: `monitoring/alerts_*.log`
- Dashboard: `monitoring/dashboard.html`

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status helpdesk-security
sudo systemctl status helpdesk-performance
```

### View Logs
```bash
tail -f monitoring/logs/security_scan.log
tail -f monitoring/logs/performance.log
tail -f monitoring/logs/dashboard.log
```

### Manual Testing
```bash
python3 monitoring/security_scanner.py
python3 monitoring/performance_monitor.py
python3 monitoring/dashboard.py
```

## Alert Configuration

### Email Alerts
Configure SMTP settings in `monitoring/config.json`:
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_email": "security-alerts@yourcompany.com",
    "to_emails": ["admin@yourcompany.com"]
  }
}
```

### Slack Alerts
Configure webhook in `monitoring/config.json`:
```json
{
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "channel": "#security-alerts"
  }
}
```

## Security Best Practices

1. **Regular Updates**: Keep monitoring tools updated
2. **Access Control**: Restrict access to monitoring files
3. **Log Rotation**: Implement log rotation to prevent disk space issues
4. **Backup**: Regular backup of monitoring configuration and logs
5. **Alerting**: Configure appropriate alert thresholds

## Performance Optimization

1. **Resource Limits**: Set appropriate resource limits for monitoring processes
2. **Scan Frequency**: Balance security scanning frequency with system performance
3. **Log Management**: Implement log rotation and cleanup
4. **Database**: Consider using a database for large-scale monitoring data

## Support

For issues or questions:
1. Check logs in `monitoring/logs/`
2. Review configuration in `monitoring/config.json`
3. Test individual components manually
4. Check system resources and permissions
"""
        
        with open('monitoring/README.md', 'w') as f:
            f.write(documentation)
        
        self.log("Documentation created: monitoring/README.md")
    
    def run_setup(self):
        """Run complete monitoring setup"""
        self.log("=" * 60)
        self.log("HELPDESK MONITORING SETUP")
        self.log("=" * 60)
        
        try:
            # Setup steps
            self.create_directories()
            self.install_required_packages()
            self.create_cron_jobs()
            self.create_systemd_services()
            self.create_monitoring_scripts()
            self.test_monitoring_system()
            self.create_documentation()
            
            # Save setup log
            with open('monitoring/setup.log', 'w') as f:
                f.write('\n'.join(self.setup_log))
            
            self.log("=" * 60)
            self.log("MONITORING SETUP COMPLETED")
            self.log("=" * 60)
            self.log("Next steps:")
            self.log("1. Configure monitoring/config.json")
            self.log("2. Run: ./monitoring/start_monitoring.sh")
            self.log("3. Open monitoring/dashboard.html in browser")
            self.log("4. Set up cron jobs: crontab monitoring/cron_jobs.txt")
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
        print("\n✅ Monitoring system setup completed successfully!")
        print("📊 Dashboard: monitoring/dashboard.html")
        print("📋 Documentation: monitoring/README.md")
        print("🚀 Start monitoring: ./monitoring/start_monitoring.sh")
    else:
        print("\n❌ Monitoring system setup failed!")
        print("Check monitoring/setup.log for details")

if __name__ == "__main__":
    main()
