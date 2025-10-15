"""
Comprehensive Security Monitoring and Alerting System.
"""

import time
import json
import smtplib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class SecurityMonitor:
    """
    Comprehensive security monitoring system.
    """
    
    def __init__(self):
        self.alert_channels = {
            'email': self._send_email_alert,
            'slack': self._send_slack_alert,
            'webhook': self._send_webhook_alert,
        }
        self.monitoring_rules = self._load_monitoring_rules()
    
    def _load_monitoring_rules(self) -> Dict[str, Any]:
        """Load monitoring rules from settings."""
        return {
            'failed_login_threshold': getattr(settings, 'SECURITY_FAILED_LOGIN_THRESHOLD', 5),
            'suspicious_activity_threshold': getattr(settings, 'SECURITY_SUSPICIOUS_ACTIVITY_THRESHOLD', 10),
            'data_breach_threshold': getattr(settings, 'SECURITY_DATA_BREACH_THRESHOLD', 1),
            'privilege_escalation_threshold': getattr(settings, 'SECURITY_PRIVILEGE_ESCALATION_THRESHOLD', 1),
            'unusual_access_pattern_threshold': getattr(settings, 'SECURITY_UNUSUAL_ACCESS_THRESHOLD', 3),
        }
    
    def monitor_failed_logins(self, ip: str, username: str, timestamp: float) -> None:
        """Monitor failed login attempts."""
        key = f"failed_logins_{ip}_{username}"
        failed_attempts = cache.get(key, [])
        failed_attempts.append(timestamp)
        
        # Keep only last hour
        current_time = time.time()
        failed_attempts = [t for t in failed_attempts if current_time - t < 3600]
        cache.set(key, failed_attempts, timeout=3600)
        
        threshold = self.monitoring_rules['failed_login_threshold']
        if len(failed_attempts) >= threshold:
            self._trigger_alert('failed_logins', {
                'ip': ip,
                'username': username,
                'attempts': len(failed_attempts),
                'timeframe': '1 hour'
            })
    
    def monitor_suspicious_activity(self, ip: str, activity_type: str, details: Dict) -> None:
        """Monitor suspicious activities."""
        key = f"suspicious_activity_{ip}"
        activities = cache.get(key, [])
        activities.append({
            'timestamp': time.time(),
            'type': activity_type,
            'details': details
        })
        
        # Keep only last hour
        current_time = time.time()
        activities = [a for a in activities if current_time - a['timestamp'] < 3600]
        cache.set(key, activities, timeout=3600)
        
        threshold = self.monitoring_rules['suspicious_activity_threshold']
        if len(activities) >= threshold:
            self._trigger_alert('suspicious_activity', {
                'ip': ip,
                'activities': len(activities),
                'types': list(set(a['type'] for a in activities)),
                'timeframe': '1 hour'
            })
    
    def monitor_data_access(self, user_id: int, resource: str, action: str, ip: str) -> None:
        """Monitor data access patterns."""
        key = f"data_access_{user_id}"
        access_log = cache.get(key, [])
        access_log.append({
            'timestamp': time.time(),
            'resource': resource,
            'action': action,
            'ip': ip
        })
        
        # Keep only last 24 hours
        current_time = time.time()
        access_log = [a for a in access_log if current_time - a['timestamp'] < 86400]
        cache.set(key, access_log, timeout=86400)
        
        # Check for unusual access patterns
        self._check_unusual_access_patterns(user_id, access_log)
    
    def _check_unusual_access_patterns(self, user_id: int, access_log: List[Dict]) -> None:
        """Check for unusual access patterns."""
        if len(access_log) < 10:  # Need minimum data
            return
        
        # Check for access from multiple IPs
        unique_ips = set(a['ip'] for a in access_log)
        if len(unique_ips) > 3:  # More than 3 different IPs
            self._trigger_alert('unusual_access_pattern', {
                'user_id': user_id,
                'pattern': 'multiple_ips',
                'ip_count': len(unique_ips),
                'ips': list(unique_ips)
            })
        
        # Check for access outside business hours
        business_hours = self._get_business_hours()
        outside_hours = [a for a in access_log if not self._is_business_hours(a['timestamp'])]
        if len(outside_hours) > len(access_log) * 0.5:  # More than 50% outside business hours
            self._trigger_alert('unusual_access_pattern', {
                'user_id': user_id,
                'pattern': 'outside_business_hours',
                'percentage': len(outside_hours) / len(access_log) * 100
            })
    
    def _get_business_hours(self) -> Dict[str, int]:
        """Get business hours configuration."""
        return {
            'start_hour': getattr(settings, 'BUSINESS_HOURS_START', 9),
            'end_hour': getattr(settings, 'BUSINESS_HOURS_END', 17),
            'timezone': getattr(settings, 'BUSINESS_TIMEZONE', 'UTC')
        }
    
    def _is_business_hours(self, timestamp: float) -> bool:
        """Check if timestamp is within business hours."""
        dt = datetime.fromtimestamp(timestamp)
        business_hours = self._get_business_hours()
        hour = dt.hour
        return business_hours['start_hour'] <= hour <= business_hours['end_hour']
    
    def monitor_privilege_escalation(self, user_id: int, old_role: str, new_role: str) -> None:
        """Monitor privilege escalation attempts."""
        self._trigger_alert('privilege_escalation', {
            'user_id': user_id,
            'old_role': old_role,
            'new_role': new_role,
            'timestamp': time.time()
        })
    
    def monitor_data_breach(self, resource: str, data_type: str, severity: str) -> None:
        """Monitor potential data breaches."""
        self._trigger_alert('data_breach', {
            'resource': resource,
            'data_type': data_type,
            'severity': severity,
            'timestamp': time.time()
        })
    
    def _trigger_alert(self, alert_type: str, data: Dict) -> None:
        """Trigger security alert."""
        alert = {
            'id': f"{alert_type}_{int(time.time())}",
            'type': alert_type,
            'timestamp': time.time(),
            'data': data,
            'severity': self._get_alert_severity(alert_type),
            'status': 'active'
        }
        
        # Store alert
        cache.set(f"security_alert_{alert['id']}", alert, timeout=86400)  # 24 hours
        
        # Log alert
        logger.critical(f"SECURITY ALERT: {alert}")
        
        # Send notifications
        self._send_notifications(alert)
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level."""
        severity_map = {
            'failed_logins': 'medium',
            'suspicious_activity': 'high',
            'unusual_access_pattern': 'medium',
            'privilege_escalation': 'high',
            'data_breach': 'critical'
        }
        return severity_map.get(alert_type, 'low')
    
    def _send_notifications(self, alert: Dict) -> None:
        """Send notifications through configured channels."""
        channels = getattr(settings, 'SECURITY_ALERT_CHANNELS', ['email'])
        
        for channel in channels:
            if channel in self.alert_channels:
                try:
                    self.alert_channels[channel](alert)
                except Exception as e:
                    logger.error(f"Failed to send alert via {channel}: {e}")
    
    def _send_email_alert(self, alert: Dict) -> None:
        """Send email alert."""
        subject = f"Security Alert: {alert['type'].replace('_', ' ').title()}"
        message = self._format_alert_message(alert)
        
        recipients = getattr(settings, 'SECURITY_ALERT_EMAILS', [])
        if recipients:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False
            )
    
    def _send_slack_alert(self, alert: Dict) -> None:
        """Send Slack alert."""
        webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
        if not webhook_url:
            return
        
        import requests
        
        payload = {
            'text': f"🚨 Security Alert: {alert['type'].replace('_', ' ').title()}",
            'attachments': [{
                'color': 'danger' if alert['severity'] == 'critical' else 'warning',
                'fields': [
                    {'title': 'Type', 'value': alert['type'], 'short': True},
                    {'title': 'Severity', 'value': alert['severity'], 'short': True},
                    {'title': 'Timestamp', 'value': datetime.fromtimestamp(alert['timestamp']).isoformat(), 'short': True},
                    {'title': 'Details', 'value': json.dumps(alert['data'], indent=2), 'short': False}
                ]
            }]
        }
        
        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_webhook_alert(self, alert: Dict) -> None:
        """Send webhook alert."""
        webhook_url = getattr(settings, 'SECURITY_WEBHOOK_URL', None)
        if not webhook_url:
            return
        
        import requests
        
        try:
            requests.post(webhook_url, json=alert, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _format_alert_message(self, alert: Dict) -> str:
        """Format alert message for email."""
        message = f"""
Security Alert Details:
=====================

Type: {alert['type'].replace('_', ' ').title()}
Severity: {alert['severity'].upper()}
Timestamp: {datetime.fromtimestamp(alert['timestamp']).isoformat()}

Data:
{json.dumps(alert['data'], indent=2)}

Please investigate this security event immediately.

Best regards,
Security Monitoring System
        """
        return message.strip()


class SecurityDashboard:
    """
    Security dashboard for real-time monitoring.
    """
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get current security metrics."""
        current_time = time.time()
        
        # Get failed logins in last hour
        failed_logins = self._get_failed_logins_count(current_time - 3600)
        
        # Get suspicious activities in last hour
        suspicious_activities = self._get_suspicious_activities_count(current_time - 3600)
        
        # Get blocked IPs
        blocked_ips = self._get_blocked_ips_count()
        
        # Get active alerts
        active_alerts = self._get_active_alerts_count()
        
        return {
            'failed_logins_last_hour': failed_logins,
            'suspicious_activities_last_hour': suspicious_activities,
            'blocked_ips': blocked_ips,
            'active_alerts': active_alerts,
            'timestamp': current_time
        }
    
    def _get_failed_logins_count(self, since: float) -> int:
        """Get count of failed logins since timestamp."""
        # This would query the actual failed login logs
        # For now, return a mock value
        return 0
    
    def _get_suspicious_activities_count(self, since: float) -> int:
        """Get count of suspicious activities since timestamp."""
        # This would query the actual suspicious activity logs
        # For now, return a mock value
        return 0
    
    def _get_blocked_ips_count(self) -> int:
        """Get count of blocked IPs."""
        # This would query the actual blocked IPs
        # For now, return a mock value
        return 0
    
    def _get_active_alerts_count(self) -> int:
        """Get count of active alerts."""
        # This would query the actual active alerts
        # For now, return a mock value
        return 0
    
    def get_security_events(self, limit: int = 100) -> List[Dict]:
        """Get recent security events."""
        # This would query the actual security events
        # For now, return mock data
        return []


# Global instances
security_monitor = SecurityMonitor()
security_dashboard = SecurityDashboard()
