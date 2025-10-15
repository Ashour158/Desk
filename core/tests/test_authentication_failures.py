"""
Comprehensive Authentication Failure Tests
Tests critical authentication failure scenarios including token expiration, invalid credentials, and security breaches.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.accounts.authentication import JWTAuthentication, MultiFactorAuthentication
from apps.security.models import SecurityPolicy, AuditLog
from apps.api.models import APIService
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class AuthenticationFailureTest(EnhancedTransactionTestCase):
    """Test authentication failure scenarios with comprehensive error handling."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.jwt_auth = JWTAuthentication()
        self.mfa_auth = MultiFactorAuthentication()
        
        # Create security policy
        self.security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="Test Security Policy",
            is_active=True,
            max_login_attempts=5,
            lockout_duration=30,  # 30 minutes
            password_expiry_days=90,
            session_timeout_minutes=60
        )
    
    def test_token_expiration_handling(self):
        """Test handling of expired JWT tokens."""
        # Create expired token
        expired_time = timezone.now() - timedelta(hours=1)
        token = AccessToken.for_user(self.user)
        token.set_exp(expired_time)
        expired_token = str(token)
        
        with patch('rest_framework_simplejwt.tokens.AccessToken') as mock_token:
            mock_token.side_effect = TokenError("Token has expired")
            
            with self.assertRaises(TokenError):
                self.jwt_auth.authenticate_credentials(expired_token)
    
    def test_invalid_token_format(self):
        """Test handling of invalid token format."""
        invalid_tokens = [
            "invalid.token.format",
            "not.a.jwt.token",
            "malformed-token",
            "",
            None
        ]
        
        for invalid_token in invalid_tokens:
            with self.assertRaises((TokenError, InvalidToken, TypeError)):
                self.jwt_auth.authenticate_credentials(invalid_token)
    
    def test_token_manipulation_detection(self):
        """Test detection of token manipulation."""
        # Create valid token
        valid_token = AccessToken.for_user(self.user)
        token_string = str(valid_token)
        
        # Manipulate token
        manipulated_token = token_string[:-5] + "XXXXX"
        
        with self.assertRaises(TokenError):
            self.jwt_auth.authenticate_credentials(manipulated_token)
    
    def test_invalid_credentials_handling(self):
        """Test handling of invalid credentials."""
        invalid_credentials = [
            {"email": "nonexistent@example.com", "password": "wrongpassword"},
            {"email": "test@example.com", "password": "wrongpassword"},
            {"email": "", "password": "testpass123"},
            {"email": "test@example.com", "password": ""},
            {"email": None, "password": "testpass123"},
            {"email": "test@example.com", "password": None}
        ]
        
        for credentials in invalid_credentials:
            with self.assertRaises(ValidationError):
                self.jwt_auth.authenticate_user(credentials)
    
    def test_account_lockout_after_max_attempts(self):
        """Test account lockout after maximum login attempts."""
        # Simulate multiple failed login attempts
        for attempt in range(self.security_policy.max_login_attempts + 1):
            with self.assertRaises(ValidationError):
                self.jwt_auth.authenticate_user({
                    "email": self.user.email,
                    "password": "wrongpassword"
                })
        
        # Check if account is locked
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked)
        self.assertIsNotNone(self.user.locked_until)
    
    def test_account_lockout_duration(self):
        """Test account lockout duration."""
        # Lock the account
        self.user.is_locked = True
        self.user.locked_until = timezone.now() + timedelta(minutes=self.security_policy.lockout_duration)
        self.user.save()
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        self.assertIn("Account is locked", str(context.exception))
    
    def test_password_expiry_handling(self):
        """Test handling of expired passwords."""
        # Set password as expired
        expired_date = timezone.now() - timedelta(days=self.security_policy.password_expiry_days + 1)
        self.user.password_changed_at = expired_date
        self.user.save()
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        self.assertIn("Password has expired", str(context.exception))
    
    def test_session_timeout_handling(self):
        """Test handling of session timeouts."""
        # Create token with expired session
        expired_time = timezone.now() - timedelta(minutes=self.security_policy.session_timeout_minutes + 1)
        token = AccessToken.for_user(self.user)
        token.set_exp(expired_time)
        expired_token = str(token)
        
        with self.assertRaises(TokenError):
            self.jwt_auth.authenticate_credentials(expired_token)
    
    def test_inactive_user_authentication(self):
        """Test authentication with inactive user."""
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        self.assertIn("Account is inactive", str(context.exception))
    
    def test_organization_suspended_authentication(self):
        """Test authentication with suspended organization."""
        # Suspend organization
        self.organization.is_active = False
        self.organization.save()
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        self.assertIn("Organization is suspended", str(context.exception))
    
    def test_mfa_failure_handling(self):
        """Test MFA failure handling."""
        # Enable MFA for user
        self.user.mfa_enabled = True
        self.user.save()
        
        # Test with invalid MFA code
        with self.assertRaises(ValidationError) as context:
            self.mfa_auth.verify_mfa_code(self.user, "invalid_code")
        
        self.assertIn("Invalid MFA code", str(context.exception))
    
    def test_mfa_code_expiry(self):
        """Test MFA code expiry handling."""
        # Enable MFA for user
        self.user.mfa_enabled = True
        self.user.save()
        
        # Create expired MFA code
        expired_time = timezone.now() - timedelta(minutes=5)  # MFA codes expire in 5 minutes
        with patch('apps.accounts.authentication.timezone.now') as mock_now:
            mock_now.return_value = expired_time
            
            with self.assertRaises(ValidationError) as context:
                self.mfa_auth.verify_mfa_code(self.user, "123456")
            
            self.assertIn("MFA code has expired", str(context.exception))
    
    def test_brute_force_attack_detection(self):
        """Test brute force attack detection."""
        # Simulate rapid failed login attempts
        for attempt in range(10):
            with self.assertRaises(ValidationError):
                self.jwt_auth.authenticate_user({
                    "email": self.user.email,
                    "password": "wrongpassword"
                })
        
        # Check if brute force attack is detected
        audit_logs = AuditLog.objects.filter(
            user=self.user,
            action="failed_login_attempt"
        )
        self.assertEqual(audit_logs.count(), 10)
    
    def test_suspicious_activity_detection(self):
        """Test suspicious activity detection."""
        # Simulate login from different location
        with patch('apps.accounts.authentication.get_client_ip') as mock_ip:
            mock_ip.return_value = "192.168.1.100"  # Different IP
            
            with self.assertRaises(ValidationError) as context:
                self.jwt_auth.authenticate_user({
                    "email": self.user.email,
                    "password": "testpass123"
                })
            
            self.assertIn("Suspicious activity detected", str(context.exception))
    
    def test_token_blacklist_handling(self):
        """Test handling of blacklisted tokens."""
        # Create token
        token = AccessToken.for_user(self.user)
        token_string = str(token)
        
        # Blacklist token
        with patch('rest_framework_simplejwt.tokens.BlacklistMixin.check_blacklist') as mock_blacklist:
            mock_blacklist.return_value = True  # Token is blacklisted
            
            with self.assertRaises(TokenError):
                self.jwt_auth.authenticate_credentials(token_string)
    
    def test_concurrent_session_limit(self):
        """Test concurrent session limit handling."""
        # Set session limit
        self.security_policy.max_concurrent_sessions = 2
        self.security_policy.save()
        
        # Create multiple sessions
        sessions = []
        for i in range(3):
            token = AccessToken.for_user(self.user)
            sessions.append(str(token))
        
        # Third session should be rejected
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_credentials(sessions[2])
        
        self.assertIn("Maximum concurrent sessions exceeded", str(context.exception))
    
    def test_api_key_authentication_failure(self):
        """Test API key authentication failure."""
        # Create API service
        api_service = APIService.objects.create(
            organization=self.organization,
            name="Test API Service",
            api_key="test-api-key",
            is_active=True
        )
        
        # Test with invalid API key
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_api_key("invalid-api-key")
        
        self.assertIn("Invalid API key", str(context.exception))
    
    def test_api_key_expiry_handling(self):
        """Test API key expiry handling."""
        # Create expired API service
        expired_date = timezone.now() - timedelta(days=1)
        api_service = APIService.objects.create(
            organization=self.organization,
            name="Expired API Service",
            api_key="expired-api-key",
            is_active=True,
            expires_at=expired_date
        )
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_api_key("expired-api-key")
        
        self.assertIn("API key has expired", str(context.exception))
    
    def test_api_key_rate_limiting(self):
        """Test API key rate limiting."""
        # Create API service with rate limit
        api_service = APIService.objects.create(
            organization=self.organization,
            name="Rate Limited API Service",
            api_key="rate-limited-api-key",
            is_active=True,
            rate_limit=10  # 10 requests per minute
        )
        
        # Exceed rate limit
        for i in range(11):
            with self.assertRaises(ValidationError) as context:
                self.jwt_auth.authenticate_api_key("rate-limited-api-key")
        
        self.assertIn("Rate limit exceeded", str(context.exception))
    
    def test_authentication_audit_logging(self):
        """Test authentication audit logging."""
        # Attempt authentication
        with self.assertRaises(ValidationError):
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "wrongpassword"
            })
        
        # Check audit log
        audit_log = AuditLog.objects.filter(
            user=self.user,
            action="failed_login_attempt"
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.details["reason"], "Invalid password")
    
    def test_security_policy_violation(self):
        """Test security policy violation handling."""
        # Create policy violation
        self.user.failed_login_attempts = self.security_policy.max_login_attempts + 1
        self.user.save()
        
        with self.assertRaises(ValidationError) as context:
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        self.assertIn("Security policy violated", str(context.exception))
    
    def test_authentication_error_recovery(self):
        """Test authentication error recovery."""
        # Lock account
        self.user.is_locked = True
        self.user.locked_until = timezone.now() + timedelta(minutes=30)
        self.user.save()
        
        # Attempt authentication
        with self.assertRaises(ValidationError):
            self.jwt_auth.authenticate_user({
                "email": self.user.email,
                "password": "testpass123"
            })
        
        # Unlock account
        self.user.is_locked = False
        self.user.locked_until = None
        self.user.save()
        
        # Should now authenticate successfully
        result = self.jwt_auth.authenticate_user({
            "email": self.user.email,
            "password": "testpass123"
        })
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, self.user.email)


class MultiFactorAuthenticationFailureTest(EnhancedTransactionTestCase):
    """Test MFA failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.mfa_auth = MultiFactorAuthentication()
    
    def test_mfa_code_generation_failure(self):
        """Test MFA code generation failure."""
        with patch('apps.accounts.authentication.pyotp.TOTP') as mock_totp:
            mock_totp.side_effect = Exception("TOTP generation failed")
            
            with self.assertRaises(Exception):
                self.mfa_auth.generate_mfa_code(self.user)
    
    def test_mfa_code_verification_failure(self):
        """Test MFA code verification failure."""
        # Enable MFA
        self.user.mfa_enabled = True
        self.user.save()
        
        # Test with invalid code
        with self.assertRaises(ValidationError) as context:
            self.mfa_auth.verify_mfa_code(self.user, "000000")
        
        self.assertIn("Invalid MFA code", str(context.exception))
    
    def test_mfa_backup_code_failure(self):
        """Test MFA backup code failure."""
        # Enable MFA with backup codes
        self.user.mfa_enabled = True
        self.user.mfa_backup_codes = ["123456", "789012"]
        self.user.save()
        
        # Test with invalid backup code
        with self.assertRaises(ValidationError) as context:
            self.mfa_auth.verify_backup_code(self.user, "invalid_code")
        
        self.assertIn("Invalid backup code", str(context.exception))
    
    def test_mfa_device_lost_handling(self):
        """Test MFA device lost handling."""
        # Enable MFA
        self.user.mfa_enabled = True
        self.user.save()
        
        # Simulate device lost scenario
        with self.assertRaises(ValidationError) as context:
            self.mfa_auth.handle_lost_device(self.user)
        
        self.assertIn("Device recovery required", str(context.exception))


class SecurityPolicyFailureTest(EnhancedTransactionTestCase):
    """Test security policy failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
    
    def test_password_policy_violation(self):
        """Test password policy violation."""
        # Create strict password policy
        security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="Strict Password Policy",
            is_active=True,
            password_min_length=12,
            password_require_uppercase=True,
            password_require_lowercase=True,
            password_require_numbers=True,
            password_require_symbols=True
        )
        
        # Test weak password
        weak_passwords = [
            "password",  # Too short, no uppercase, no numbers, no symbols
            "PASSWORD",  # No lowercase, no numbers, no symbols
            "Password",  # No numbers, no symbols
            "Password1",  # No symbols
            "Password!",  # No numbers
        ]
        
        for password in weak_passwords:
            with self.assertRaises(ValidationError) as context:
                self.user.set_password(password)
            
            self.assertIn("Password does not meet policy requirements", str(context.exception))
    
    def test_account_lockout_policy(self):
        """Test account lockout policy."""
        # Create lockout policy
        security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="Lockout Policy",
            is_active=True,
            max_login_attempts=3,
            lockout_duration=15  # 15 minutes
        )
        
        # Simulate failed attempts
        for attempt in range(4):
            with self.assertRaises(ValidationError):
                self.user.authenticate("wrongpassword")
        
        # Check if account is locked
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked)
        self.assertIsNotNone(self.user.locked_until)
    
    def test_session_timeout_policy(self):
        """Test session timeout policy."""
        # Create session timeout policy
        security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="Session Timeout Policy",
            is_active=True,
            session_timeout_minutes=30
        )
        
        # Create session
        session = self.user.create_session()
        
        # Simulate timeout
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now() + timedelta(minutes=31)
            
            with self.assertRaises(ValidationError) as context:
                session.validate()
            
            self.assertIn("Session has expired", str(context.exception))
    
    def test_ip_whitelist_policy(self):
        """Test IP whitelist policy."""
        # Create IP whitelist policy
        security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="IP Whitelist Policy",
            is_active=True,
            allowed_ips=["192.168.1.0/24", "10.0.0.0/8"]
        )
        
        # Test from allowed IP
        with patch('apps.accounts.authentication.get_client_ip') as mock_ip:
            mock_ip.return_value = "192.168.1.100"
            
            # Should succeed
            result = self.user.authenticate("testpass123")
            self.assertIsNotNone(result)
        
        # Test from blocked IP
        with patch('apps.accounts.authentication.get_client_ip') as mock_ip:
            mock_ip.return_value = "203.0.113.1"
            
            with self.assertRaises(ValidationError) as context:
                self.user.authenticate("testpass123")
            
            self.assertIn("IP address not allowed", str(context.exception))


# Export test classes
__all__ = [
    'AuthenticationFailureTest',
    'MultiFactorAuthenticationFailureTest',
    'SecurityPolicyFailureTest'
]