"""
Advanced threat detection and security hardening system.
"""

import json
import logging
import time
import hashlib
import hmac
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
import ipaddress

logger = logging.getLogger(__name__)


class AdvancedThreatDetector:
    """
    Advanced threat detection system with multiple detection engines.
    """
    
    def __init__(self):
        self.threat_patterns = {
            'sql_injection': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
                r"(\b(OR|AND)\s+\".*\"\s*=\s*\".*\")",
                r"(\b(OR|AND)\s+.*\s*LIKE\s+.*)",
                r"(\b(OR|AND)\s+.*\s*IN\s+.*)",
            ],
            'xss_attacks': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*=",
                r"onmouseover\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"\.\.%2f",
                r"\.\.%5c",
                r"\.\.%252f",
                r"\.\.%255c",
            ],
            'command_injection': [
                r"[;&|`$]",
                r"\b(cat|ls|dir|type|more|less|head|tail|grep|find|awk|sed|cut|sort|uniq|wc|ps|kill|chmod|chown|sudo|su)\b",
                r"\b(ping|nslookup|dig|traceroute|netstat|ifconfig|ipconfig|arp|route|iptables)\b",
                r"\b(wget|curl|nc|netcat|telnet|ssh|ftp|scp|rsync)\b",
            ],
            'ldap_injection': [
                r"[()=*!&|]",
                r"\b(OR|AND|NOT)\b",
                r"\b(cn|uid|mail|telephoneNumber|objectClass)\b",
            ],
            'no_sql_injection': [
                r"\$where",
                r"\$ne",
                r"\$gt",
                r"\$lt",
                r"\$regex",
                r"\$exists",
                r"\$in",
                r"\$nin",
                r"\$or",
                r"\$and",
            ]
        }
        
        self.threat_indicators = {
            'suspicious_ips': [],
            'malicious_user_agents': [],
            'attack_patterns': [],
            'anomalous_behavior': []
        }
        
        self.security_rules = {
            'max_request_size': 10 * 1024 * 1024,  # 10MB
            'max_parameters': 100,
            'max_header_size': 8192,  # 8KB
            'max_cookie_size': 4096,  # 4KB
            'rate_limit_window': 60,  # 1 minute
            'max_requests_per_minute': 100
        }
    
    def detect_threats(self, request) -> Dict[str, Any]:
        """
        Detect threats in incoming request.
        
        Args:
            request: HTTP request object
            
        Returns:
            Threat detection results
        """
        try:
            threat_result = {
                'threats_detected': [],
                'risk_level': 'low',
                'block_request': False,
                'security_headers': {},
                'timestamp': timezone.now().isoformat()
            }
            
            # Check for various threat types
            sql_injection = self._detect_sql_injection(request)
            xss_attacks = self._detect_xss_attacks(request)
            path_traversal = self._detect_path_traversal(request)
            command_injection = self._detect_command_injection(request)
            ldap_injection = self._detect_ldap_injection(request)
            no_sql_injection = self._detect_no_sql_injection(request)
            
            # Combine all threats
            all_threats = sql_injection + xss_attacks + path_traversal + command_injection + ldap_injection + no_sql_injection
            threat_result['threats_detected'] = all_threats
            
            # Determine risk level
            threat_result['risk_level'] = self._calculate_risk_level(all_threats)
            
            # Determine if request should be blocked
            threat_result['block_request'] = self._should_block_request(all_threats)
            
            # Generate security headers
            threat_result['security_headers'] = self._generate_security_headers(request, all_threats)
            
            # Log threats
            if all_threats:
                self._log_threats(request, all_threats)
            
            return threat_result
            
        except Exception as e:
            logger.error(f"Threat detection error: {e}")
            return {
                'threats_detected': [],
                'risk_level': 'low',
                'block_request': False,
                'error': str(e)
            }
    
    def _detect_sql_injection(self, request) -> List[Dict]:
        """Detect SQL injection attempts."""
        threats = []
        
        # Check request parameters
        for param_name, param_value in request.GET.items():
            if self._check_patterns(param_value, self.threat_patterns['sql_injection']):
                threats.append({
                    'type': 'sql_injection',
                    'parameter': param_name,
                    'value': param_value[:100],  # Truncate for logging
                    'severity': 'high',
                    'description': 'SQL injection pattern detected'
                })
        
        # Check POST data
        if hasattr(request, 'POST'):
            for param_name, param_value in request.POST.items():
                if self._check_patterns(str(param_value), self.threat_patterns['sql_injection']):
                    threats.append({
                        'type': 'sql_injection',
                        'parameter': param_name,
                        'value': str(param_value)[:100],
                        'severity': 'high',
                        'description': 'SQL injection pattern detected in POST data'
                    })
        
        return threats
    
    def _detect_xss_attacks(self, request) -> List[Dict]:
        """Detect XSS attack attempts."""
        threats = []
        
        # Check request parameters
        for param_name, param_value in request.GET.items():
            if self._check_patterns(param_value, self.threat_patterns['xss_attacks']):
                threats.append({
                    'type': 'xss_attack',
                    'parameter': param_name,
                    'value': param_value[:100],
                    'severity': 'high',
                    'description': 'XSS attack pattern detected'
                })
        
        return threats
    
    def _detect_path_traversal(self, request) -> List[Dict]:
        """Detect path traversal attempts."""
        threats = []
        
        # Check URL path
        if self._check_patterns(request.path, self.threat_patterns['path_traversal']):
            threats.append({
                'type': 'path_traversal',
                'parameter': 'path',
                'value': request.path,
                'severity': 'high',
                'description': 'Path traversal pattern detected'
            })
        
        return threats
    
    def _detect_command_injection(self, request) -> List[Dict]:
        """Detect command injection attempts."""
        threats = []
        
        # Check request parameters
        for param_name, param_value in request.GET.items():
            if self._check_patterns(param_value, self.threat_patterns['command_injection']):
                threats.append({
                    'type': 'command_injection',
                    'parameter': param_name,
                    'value': param_value[:100],
                    'severity': 'critical',
                    'description': 'Command injection pattern detected'
                })
        
        return threats
    
    def _detect_ldap_injection(self, request) -> List[Dict]:
        """Detect LDAP injection attempts."""
        threats = []
        
        # Check request parameters
        for param_name, param_value in request.GET.items():
            if self._check_patterns(param_value, self.threat_patterns['ldap_injection']):
                threats.append({
                    'type': 'ldap_injection',
                    'parameter': param_name,
                    'value': param_value[:100],
                    'severity': 'high',
                    'description': 'LDAP injection pattern detected'
                })
        
        return threats
    
    def _detect_no_sql_injection(self, request) -> List[Dict]:
        """Detect NoSQL injection attempts."""
        threats = []
        
        # Check request parameters
        for param_name, param_value in request.GET.items():
            if self._check_patterns(param_value, self.threat_patterns['no_sql_injection']):
                threats.append({
                    'type': 'no_sql_injection',
                    'parameter': param_name,
                    'value': param_value[:100],
                    'severity': 'high',
                    'description': 'NoSQL injection pattern detected'
                })
        
        return threats
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the patterns."""
        if not text:
            return False
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_risk_level(self, threats: List[Dict]) -> str:
        """Calculate overall risk level."""
        if not threats:
            return 'low'
        
        # Count threats by severity
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for threat in threats:
            severity = threat.get('severity', 'low')
            severity_counts[severity] += 1
        
        # Determine risk level
        if severity_counts['critical'] > 0:
            return 'critical'
        elif severity_counts['high'] > 2:
            return 'high'
        elif severity_counts['high'] > 0 or severity_counts['medium'] > 3:
            return 'medium'
        else:
            return 'low'
    
    def _should_block_request(self, threats: List[Dict]) -> bool:
        """Determine if request should be blocked."""
        if not threats:
            return False
        
        # Block if any critical threats
        for threat in threats:
            if threat.get('severity') == 'critical':
                return True
        
        # Block if too many high-severity threats
        high_severity_count = sum(1 for threat in threats if threat.get('severity') == 'high')
        if high_severity_count > 2:
            return True
        
        return False
    
    def _generate_security_headers(self, request, threats: List[Dict]) -> Dict[str, str]:
        """Generate security headers based on threats."""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        # Add additional headers based on threats
        if any(threat['type'] == 'xss_attack' for threat in threats):
            headers['Content-Security-Policy'] = "default-src 'self'"
        
        if any(threat['type'] == 'sql_injection' for threat in threats):
            headers['X-SQL-Injection-Protection'] = 'enabled'
        
        return headers
    
    def _log_threats(self, request, threats: List[Dict]):
        """Log detected threats."""
        for threat in threats:
            logger.warning(
                f"Threat detected: {threat['type']} - {threat['description']} "
                f"from IP: {request.META.get('REMOTE_ADDR')} "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )


class SecurityHardeningMiddleware:
    """
    Middleware for security hardening.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.threat_detector = AdvancedThreatDetector()
        self.security_analyzer = SecurityAnalyzer()
        self.rate_limiter = SecurityRateLimiter()
    
    def __call__(self, request):
        # Perform threat detection
        threat_result = self.threat_detector.detect_threats(request)
        
        # Block request if threats detected
        if threat_result['block_request']:
            return JsonResponse({
                'error': {
                    'code': 'SECURITY_THREAT_DETECTED',
                    'message': 'Request blocked due to security threats',
                    'details': threat_result['threats_detected'],
                    'timestamp': timezone.now().isoformat()
                },
                'meta': {
                    'timestamp': timezone.now().isoformat(),
                    'version': 'v1',
                    'request_id': str(uuid.uuid4()),
                }
            }, status=403)
        
        # Perform security analysis
        security_analysis = self.security_analyzer.analyze_request(request)
        
        # Apply rate limiting
        rate_limit_result = self.rate_limiter.check_rate_limit(request)
        if not rate_limit_result['allowed']:
            return JsonResponse({
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'details': rate_limit_result,
                    'timestamp': timezone.now().isoformat()
                },
                'meta': {
                    'timestamp': timezone.now().isoformat(),
                    'version': 'v1',
                    'request_id': str(uuid.uuid4()),
                }
            }, status=429)
        
        # Process request
        response = self.get_response(request)
        
        # Add security headers
        for header, value in threat_result['security_headers'].items():
            response[header] = value
        
        # Add security analysis headers
        response['X-Security-Analysis'] = json.dumps(security_analysis)
        
        return response


class SecurityAnalyzer:
    """
    Security analysis system.
    """
    
    def analyze_request(self, request) -> Dict[str, Any]:
        """Analyze request for security issues."""
        analysis = {
            'request_size': len(request.body) if hasattr(request, 'body') else 0,
            'parameter_count': len(request.GET) + len(request.POST) if hasattr(request, 'POST') else len(request.GET),
            'header_count': len(request.META),
            'user_agent_analysis': self._analyze_user_agent(request),
            'ip_analysis': self._analyze_ip(request),
            'timestamp': timezone.now().isoformat()
        }
        
        return analysis
    
    def _analyze_user_agent(self, request) -> Dict[str, Any]:
        """Analyze user agent for suspicious patterns."""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return {
            'user_agent': user_agent,
            'is_suspicious': self._is_suspicious_user_agent(user_agent),
            'length': len(user_agent),
            'contains_script': '<script' in user_agent.lower()
        }
    
    def _analyze_ip(self, request) -> Dict[str, Any]:
        """Analyze IP address for security issues."""
        ip = request.META.get('REMOTE_ADDR', '')
        
        return {
            'ip': ip,
            'is_private': self._is_private_ip(ip),
            'is_suspicious': self._is_suspicious_ip(ip)
        }
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious."""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'scanner', 'hack', 'exploit'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP is suspicious."""
        # This would implement actual IP reputation checking
        return False


class SecurityRateLimiter:
    """
    Security-focused rate limiter.
    """
    
    def __init__(self):
        self.rate_limits = {
            'general': {'requests': 100, 'window': 60},
            'authentication': {'requests': 10, 'window': 60},
            'file_upload': {'requests': 20, 'window': 60},
            'api_calls': {'requests': 1000, 'window': 3600}
        }
    
    def check_rate_limit(self, request) -> Dict[str, Any]:
        """Check rate limit for request."""
        # Determine limit type based on request
        limit_type = self._get_limit_type(request)
        
        if not limit_type:
            return {'allowed': True}
        
        # Get rate limit configuration
        rate_config = self.rate_limits.get(limit_type)
        if not rate_config:
            return {'allowed': True}
        
        # Create cache key
        cache_key = f"security_rate_limit:{limit_type}:{request.META.get('REMOTE_ADDR')}"
        
        # Check current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= rate_config['requests']:
            return {
                'allowed': False,
                'current_count': current_count,
                'limit': rate_config['requests'],
                'window': rate_config['window']
            }
        
        # Increment counter
        cache.set(cache_key, current_count + 1, rate_config['window'])
        
        return {
            'allowed': True,
            'current_count': current_count + 1,
            'limit': rate_config['requests'],
            'window': rate_config['window']
        }
    
    def _get_limit_type(self, request) -> Optional[str]:
        """Get rate limit type for request."""
        path = request.path
        
        if '/api/v1/users/' in path:
            return 'authentication'
        elif '/api/v1/upload/' in path:
            return 'file_upload'
        elif '/api/v1/' in path:
            return 'api_calls'
        else:
            return 'general'


# Global instances
threat_detector = AdvancedThreatDetector()
security_analyzer = SecurityAnalyzer()
security_rate_limiter = SecurityRateLimiter()
