"""
Network Security Implementation with WAF and DDoS Protection.
"""

import time
import hashlib
import ipaddress
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class DDoSProtection:
    """
    Distributed Denial of Service (DDoS) protection system.
    """
    
    def __init__(self):
        self.rate_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
        }
        self.blocked_ips = set()
        self.suspicious_ips = set()
        
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self.blocked_ips
    
    def is_ip_suspicious(self, ip: str) -> bool:
        """Check if IP is suspicious."""
        return ip in self.suspicious_ips
    
    def check_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """Check rate limits for IP."""
        current_time = int(time.time())
        
        # Check per-minute limit
        minute_key = f"ddos_minute_{ip}_{current_time // 60}"
        minute_count = cache.get(minute_key, 0)
        if minute_count >= self.rate_limits['requests_per_minute']:
            self.suspicious_ips.add(ip)
            return False, "Rate limit exceeded: too many requests per minute"
        
        # Check per-hour limit
        hour_key = f"ddos_hour_{ip}_{current_time // 3600}"
        hour_count = cache.get(hour_key, 0)
        if hour_count >= self.rate_limits['requests_per_hour']:
            self.suspicious_ips.add(ip)
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Check per-day limit
        day_key = f"ddos_day_{ip}_{current_time // 86400}"
        day_count = cache.get(day_key, 0)
        if day_count >= self.rate_limits['requests_per_day']:
            self.blocked_ips.add(ip)
            return False, "Rate limit exceeded: too many requests per day"
        
        # Increment counters
        cache.set(minute_key, minute_count + 1, timeout=60)
        cache.set(hour_key, hour_count + 1, timeout=3600)
        cache.set(day_key, day_count + 1, timeout=86400)
        
        return True, "OK"
    
    def block_ip(self, ip: str, duration: int = 3600) -> None:
        """Block IP for specified duration."""
        self.blocked_ips.add(ip)
        cache.set(f"blocked_ip_{ip}", True, timeout=duration)
        logger.warning(f"IP {ip} blocked for {duration} seconds")
    
    def unblock_ip(self, ip: str) -> None:
        """Unblock IP."""
        self.blocked_ips.discard(ip)
        cache.delete(f"blocked_ip_{ip}")
        logger.info(f"IP {ip} unblocked")


class WebApplicationFirewall:
    """
    Web Application Firewall (WAF) implementation.
    """
    
    def __init__(self):
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
            r"(\bUNION\s+SELECT\b)",
            r"(\bDROP\s+TABLE\b)",
            r"(\bUNION\s+ALL\s+SELECT\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
        ]
        
        self.command_injection_patterns = [
            r"[;&|`$]",
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat)\b",
            r"\b(rm|del|mkdir|rmdir|copy|move)\b",
            r"\b(ping|nslookup|traceroute|telnet)\b",
        ]
    
    def scan_request(self, request: HttpRequest) -> Tuple[bool, str, str]:
        """Scan request for malicious patterns."""
        import re
        
        # Get request data
        path = request.path
        query_params = request.GET.dict()
        post_data = request.POST.dict()
        headers = dict(request.headers)
        
        # Check SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False, "SQL_INJECTION", f"SQL injection attempt detected in path: {path}"
            
            for key, value in query_params.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "SQL_INJECTION", f"SQL injection attempt detected in parameter {key}: {value}"
            
            for key, value in post_data.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "SQL_INJECTION", f"SQL injection attempt detected in POST data {key}: {value}"
        
        # Check XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False, "XSS", f"XSS attempt detected in path: {path}"
            
            for key, value in query_params.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "XSS", f"XSS attempt detected in parameter {key}: {value}"
            
            for key, value in post_data.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "XSS", f"XSS attempt detected in POST data {key}: {value}"
        
        # Check path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False, "PATH_TRAVERSAL", f"Path traversal attempt detected: {path}"
        
        # Check command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False, "COMMAND_INJECTION", f"Command injection attempt detected in path: {path}"
            
            for key, value in query_params.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "COMMAND_INJECTION", f"Command injection attempt detected in parameter {key}: {value}"
            
            for key, value in post_data.items():
                if re.search(pattern, str(value), re.IGNORECASE):
                    return False, "COMMAND_INJECTION", f"Command injection attempt detected in POST data {key}: {value}"
        
        return True, "SAFE", "Request appears safe"
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_whitelisted_ip(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        whitelist = getattr(settings, 'SECURITY_WHITELIST_IPS', [])
        return ip in whitelist
    
    def is_blacklisted_ip(self, ip: str) -> bool:
        """Check if IP is blacklisted."""
        blacklist = getattr(settings, 'SECURITY_BLACKLIST_IPS', [])
        return ip in blacklist


class SecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.ddos_protection = DDoSProtection()
        self.waf = WebApplicationFirewall()
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process incoming request for security checks."""
        try:
            # Get client IP
            client_ip = self.waf.get_client_ip(request)
            
            # Check if IP is blacklisted
            if self.waf.is_blacklisted_ip(client_ip):
                logger.warning(f"Blacklisted IP {client_ip} attempted access")
                return HttpResponse("Access Denied", status=403)
            
            # Skip security checks for whitelisted IPs
            if self.waf.is_whitelisted_ip(client_ip):
                return None
            
            # Check if IP is blocked
            if self.ddos_protection.is_ip_blocked(client_ip):
                logger.warning(f"Blocked IP {client_ip} attempted access")
                return HttpResponse("Access Denied", status=403)
            
            # Check rate limits
            rate_ok, rate_message = self.ddos_protection.check_rate_limit(client_ip)
            if not rate_ok:
                logger.warning(f"Rate limit exceeded for IP {client_ip}: {rate_message}")
                return HttpResponse("Rate Limit Exceeded", status=429)
            
            # WAF scanning
            is_safe, threat_type, threat_message = self.waf.scan_request(request)
            if not is_safe:
                logger.warning(f"WAF blocked request from {client_ip}: {threat_type} - {threat_message}")
                
                # Block IP for malicious requests
                if threat_type in ['SQL_INJECTION', 'COMMAND_INJECTION']:
                    self.ddos_protection.block_ip(client_ip, duration=3600)
                
                return HttpResponse("Request Blocked", status=403)
            
            return None
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers to response."""
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response['Content-Security-Policy'] = csp
        
        return response


class IPGeolocationFilter:
    """
    IP geolocation-based filtering.
    """
    
    def __init__(self):
        self.blocked_countries = getattr(settings, 'SECURITY_BLOCKED_COUNTRIES', [])
        self.allowed_countries = getattr(settings, 'SECURITY_ALLOWED_COUNTRIES', [])
    
    def get_country_from_ip(self, ip: str) -> Optional[str]:
        """Get country from IP address."""
        try:
            # In production, use a proper geolocation service
            # For now, return None (no filtering)
            return None
        except Exception as e:
            logger.error(f"Error getting country for IP {ip}: {e}")
            return None
    
    def is_country_allowed(self, ip: str) -> bool:
        """Check if country is allowed."""
        country = self.get_country_from_ip(ip)
        if not country:
            return True  # Allow if country cannot be determined
        
        if self.allowed_countries and country not in self.allowed_countries:
            return False
        
        if self.blocked_countries and country in self.blocked_countries:
            return False
        
        return True


class SecurityMonitoring:
    """
    Security monitoring and alerting system.
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'failed_logins': 5,
            'suspicious_requests': 10,
            'blocked_ips': 3,
        }
    
    def log_security_event(self, event_type: str, ip: str, details: Dict) -> None:
        """Log security event."""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'ip': ip,
            'details': details,
        }
        
        # Store in cache for real-time monitoring
        cache_key = f"security_event_{event_type}_{ip}"
        cache.set(cache_key, event, timeout=3600)
        
        # Log to file
        logger.warning(f"Security event: {event}")
        
        # Check if alert should be sent
        self._check_alert_thresholds(event_type, ip)
    
    def _check_alert_thresholds(self, event_type: str, ip: str) -> None:
        """Check if alert thresholds are exceeded."""
        threshold = self.alert_thresholds.get(event_type, 0)
        if threshold == 0:
            return
        
        # Count events in last hour
        events = cache.get(f"security_events_{event_type}_{ip}", [])
        events = [e for e in events if time.time() - e['timestamp'] < 3600]
        
        if len(events) >= threshold:
            self._send_alert(event_type, ip, len(events))
    
    def _send_alert(self, event_type: str, ip: str, count: int) -> None:
        """Send security alert."""
        alert = {
            'timestamp': time.time(),
            'event_type': event_type,
            'ip': ip,
            'count': count,
            'message': f"Security alert: {count} {event_type} events from {ip} in the last hour"
        }
        
        logger.critical(f"SECURITY ALERT: {alert}")
        
        # In production, send to monitoring system
        # self._send_to_monitoring_system(alert)
