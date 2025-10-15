#!/usr/bin/env python3
"""
Comprehensive Alerting System
Advanced alerting with multiple channels and intelligent routing
"""

import os
import json
import time
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    severity: str
    channels: List[str]
    cooldown: int  # seconds
    enabled: bool = True

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    timestamp: str
    severity: str
    category: str
    service: str
    message: str
    metric: str
    value: float
    threshold: float
    rule_name: str
    channels: List[str]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class AlertChannel:
    """Alert channel configuration"""
    name: str
    type: str  # email, slack, webhook, sms
    config: Dict[str, Any]
    enabled: bool = True

class AlertingSystem:
    """Comprehensive alerting system with multiple channels"""
    
    def __init__(self, config_file: str = 'monitoring/alerting_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.alert_queue = queue.Queue()
        self.alert_history = []
        self.active_alerts = {}
        self.running = False
        self.alert_threads = []
        
        # Initialize channels
        self.channels = self.initialize_channels()
        
        # Initialize rules
        self.rules = self.initialize_rules()
        
        logger.info("Alerting system initialized")
    
    def load_config(self) -> Dict[str, Any]:
        """Load alerting configuration"""
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
            "channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "alerts@helpdesk-platform.com",
                    "to_emails": ["admin@helpdesk-platform.com", "devops@helpdesk-platform.com"]
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#alerts",
                    "username": "AlertBot"
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {"Content-Type": "application/json"}
                },
                "sms": {
                    "enabled": False,
                    "provider": "twilio",
                    "account_sid": "",
                    "auth_token": "",
                    "from_number": "",
                    "to_numbers": []
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
                    "channels": ["email", "slack", "sms"],
                    "cooldown": 60
                },
                {
                    "name": "High Error Rate",
                    "condition": "error_rate > 5",
                    "threshold": 5.0,
                    "severity": "critical",
                    "channels": ["email", "slack", "sms"],
                    "cooldown": 120
                },
                {
                    "name": "Slow Response Time",
                    "condition": "response_time > 1000",
                    "threshold": 1000.0,
                    "severity": "warning",
                    "channels": ["email", "slack"],
                    "cooldown": 600
                },
                {
                    "name": "Service Down",
                    "condition": "service_status == 'down'",
                    "threshold": 0,
                    "severity": "critical",
                    "channels": ["email", "slack", "sms"],
                    "cooldown": 30
                }
            ],
            "escalation": {
                "enabled": True,
                "levels": [
                    {"delay": 0, "channels": ["email"]},
                    {"delay": 300, "channels": ["slack"]},
                    {"delay": 900, "channels": ["sms"]}
                ]
            },
            "suppression": {
                "enabled": True,
                "maintenance_windows": [],
                "quiet_hours": {"start": "22:00", "end": "08:00"}
            }
        }
    
    def initialize_channels(self) -> Dict[str, AlertChannel]:
        """Initialize alert channels"""
        channels = {}
        
        for name, config in self.config['channels'].items():
            channels[name] = AlertChannel(
                name=name,
                type=name,
                config=config,
                enabled=config.get('enabled', True)
            )
        
        return channels
    
    def initialize_rules(self) -> List[AlertRule]:
        """Initialize alert rules"""
        rules = []
        
        for rule_config in self.config['rules']:
            rule = AlertRule(
                name=rule_config['name'],
                condition=rule_config['condition'],
                threshold=rule_config['threshold'],
                severity=rule_config['severity'],
                channels=rule_config['channels'],
                cooldown=rule_config['cooldown'],
                enabled=rule_config.get('enabled', True)
            )
            rules.append(rule)
        
        return rules
    
    def evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation
            # In production, you'd want a more robust expression evaluator
            if 'cpu_percent' in condition:
                return metrics.get('cpu_percent', 0) > float(condition.split('>')[1].strip())
            elif 'memory_percent' in condition:
                return metrics.get('memory_percent', 0) > float(condition.split('>')[1].strip())
            elif 'error_rate' in condition:
                return metrics.get('error_rate', 0) > float(condition.split('>')[1].strip())
            elif 'response_time' in condition:
                return metrics.get('response_time', 0) > float(condition.split('>')[1].strip())
            elif 'service_status' in condition:
                return metrics.get('service_status') == 'down'
            
            return False
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def create_alert(self, rule: AlertRule, metrics: Dict[str, Any]) -> Alert:
        """Create alert from rule and metrics"""
        alert_id = f"{rule.name}_{int(time.time())}"
        
        # Determine metric value
        metric_value = 0
        if 'cpu_percent' in rule.condition:
            metric_value = metrics.get('cpu_percent', 0)
        elif 'memory_percent' in rule.condition:
            metric_value = metrics.get('memory_percent', 0)
        elif 'error_rate' in rule.condition:
            metric_value = metrics.get('error_rate', 0)
        elif 'response_time' in rule.condition:
            metric_value = metrics.get('response_time', 0)
        
        return Alert(
            id=alert_id,
            timestamp=datetime.now().isoformat(),
            severity=rule.severity,
            category='performance' if 'cpu' in rule.condition or 'memory' in rule.condition else 'reliability',
            service=metrics.get('service', 'system'),
            message=f"{rule.name}: {metric_value}",
            metric=rule.condition.split()[0],
            value=metric_value,
            threshold=rule.threshold,
            rule_name=rule.name,
            channels=rule.channels
        )
    
    def should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent (cooldown, suppression)"""
        # Check cooldown
        rule = next((r for r in self.rules if r.name == alert.rule_name), None)
        if rule:
            last_alert = next(
                (a for a in self.alert_history 
                 if a.rule_name == alert.rule_name and a.service == alert.service),
                None
            )
            if last_alert:
                time_diff = datetime.now() - datetime.fromisoformat(last_alert.timestamp)
                if time_diff.total_seconds() < rule.cooldown:
                    return False
        
        # Check suppression
        if self.config['suppression']['enabled']:
            current_time = datetime.now().time()
            quiet_start = datetime.strptime(
                self.config['suppression']['quiet_hours']['start'], '%H:%M'
            ).time()
            quiet_end = datetime.strptime(
                self.config['suppression']['quiet_hours']['end'], '%H:%M'
            ).time()
            
            if quiet_start <= quiet_end:
                if quiet_start <= current_time <= quiet_end:
                    return False
            else:  # Overnight quiet hours
                if current_time >= quiet_start or current_time <= quiet_end:
                    return False
        
        return True
    
    def send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            channel = self.channels['email']
            if not channel.enabled:
                return
            
            config = channel.config
            
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.service} - {alert.message}"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body>
                <h2 style="color: {'red' if alert.severity == 'critical' else 'orange'}">
                    {alert.severity.upper()} Alert
                </h2>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr><td><strong>Time</strong></td><td>{alert.timestamp}</td></tr>
                    <tr><td><strong>Service</strong></td><td>{alert.service}</td></tr>
                    <tr><td><strong>Category</strong></td><td>{alert.category}</td></tr>
                    <tr><td><strong>Message</strong></td><td>{alert.message}</td></tr>
                    <tr><td><strong>Metric</strong></td><td>{alert.metric}</td></tr>
                    <tr><td><strong>Value</strong></td><td>{alert.value}</td></tr>
                    <tr><td><strong>Threshold</strong></td><td>{alert.threshold}</td></tr>
                    <tr><td><strong>Rule</strong></td><td>{alert.rule_name}</td></tr>
                </table>
                <p><strong>Action Required:</strong> Please investigate this issue immediately.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert.service}")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        try:
            channel = self.channels['slack']
            if not channel.enabled:
                return
            
            config = channel.config
            
            color = "danger" if alert.severity == "critical" else "warning"
            
            payload = {
                "channel": config['channel'],
                "username": config['username'],
                "text": f"🚨 *{alert.severity.upper()} Alert*",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {"title": "Service", "value": alert.service, "short": True},
                            {"title": "Category", "value": alert.category, "short": True},
                            {"title": "Message", "value": alert.message, "short": False},
                            {"title": "Metric", "value": f"{alert.metric}: {alert.value}", "short": True},
                            {"title": "Threshold", "value": str(alert.threshold), "short": True},
                            {"title": "Time", "value": alert.timestamp, "short": False}
                        ],
                        "footer": "Helpdesk Platform Monitoring",
                        "ts": int(time.time())
                    }
                ]
            }
            
            response = requests.post(config['webhook_url'], json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Slack alert sent for {alert.service}")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    def send_webhook_alert(self, alert: Alert):
        """Send webhook alert"""
        try:
            channel = self.channels['webhook']
            if not channel.enabled:
                return
            
            config = channel.config
            
            payload = {
                "alert": asdict(alert),
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                config['url'], 
                json=payload, 
                headers=config.get('headers', {}),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Webhook alert sent for {alert.service}")
            else:
                logger.error(f"Failed to send webhook alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
    
    def send_sms_alert(self, alert: Alert):
        """Send SMS alert"""
        try:
            channel = self.channels['sms']
            if not channel.enabled:
                return
            
            config = channel.config
            
            if config['provider'] == 'twilio':
                from twilio.rest import Client
                
                client = Client(config['account_sid'], config['auth_token'])
                
                message = f"{alert.severity.upper()}: {alert.service} - {alert.message}"
                
                for to_number in config['to_numbers']:
                    client.messages.create(
                        body=message,
                        from_=config['from_number'],
                        to=to_number
                    )
                
                logger.info(f"SMS alert sent for {alert.service}")
        except Exception as e:
            logger.error(f"Error sending SMS alert: {e}")
    
    def send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        for channel_name in alert.channels:
            try:
                if channel_name == 'email':
                    self.send_email_alert(alert)
                elif channel_name == 'slack':
                    self.send_slack_alert(alert)
                elif channel_name == 'webhook':
                    self.send_webhook_alert(alert)
                elif channel_name == 'sms':
                    self.send_sms_alert(alert)
            except Exception as e:
                logger.error(f"Error sending {channel_name} alert: {e}")
    
    def process_alerts(self):
        """Process alerts from queue"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1)
                
                if self.should_send_alert(alert):
                    self.send_alert(alert)
                    self.alert_history.append(alert)
                    self.active_alerts[alert.id] = alert
                    
                    logger.warning(f"Alert sent: {alert.message}")
                else:
                    logger.info(f"Alert suppressed: {alert.message}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
    
    def evaluate_metrics(self, metrics: Dict[str, Any]):
        """Evaluate metrics against alert rules"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self.evaluate_condition(rule.condition, metrics):
                alert = self.create_alert(rule, metrics)
                self.alert_queue.put(alert)
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert {alert_id} acknowledged")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            logger.info(f"Alert {alert_id} resolved")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert.timestamp) > cutoff_time
        ]
    
    def start_alerting(self):
        """Start alerting system"""
        logger.info("Starting alerting system")
        
        self.running = True
        
        # Start alert processing thread
        alert_thread = threading.Thread(target=self.process_alerts)
        alert_thread.daemon = True
        alert_thread.start()
        self.alert_threads.append(alert_thread)
        
        logger.info("Alerting system started")
    
    def stop_alerting(self):
        """Stop alerting system"""
        logger.info("Stopping alerting system")
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.alert_threads:
            thread.join(timeout=5)
        
        logger.info("Alerting system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get alerting system status"""
        return {
            'running': self.running,
            'channels': {name: channel.enabled for name, channel in self.channels.items()},
            'rules': len(self.rules),
            'active_alerts': len(self.get_active_alerts()),
            'queue_size': self.alert_queue.qsize(),
            'history_size': len(self.alert_history)
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Alerting System')
    parser.add_argument('--config', default='monitoring/alerting_config.json', help='Config file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--test', action='store_true', help='Send test alert')
    
    args = parser.parse_args()
    
    alerting = AlertingSystem(args.config)
    
    if args.status:
        status = alerting.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.test:
        # Send test alert
        test_metrics = {
            'cpu_percent': 85.0,
            'memory_percent': 45.0,
            'error_rate': 2.0,
            'response_time': 200.0,
            'service': 'test'
        }
        alerting.evaluate_metrics(test_metrics)
        print("Test alert sent")
        return
    
    try:
        if args.daemon:
            alerting.start_alerting()
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("Alerting system ready")
            
    except KeyboardInterrupt:
        logger.info("Shutting down alerting system")
        alerting.stop_alerting()
    except Exception as e:
        logger.error(f"Error running alerting system: {e}")

if __name__ == '__main__':
    main()
