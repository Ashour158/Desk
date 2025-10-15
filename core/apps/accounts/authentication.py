"""
Advanced authentication system with JWT, OAuth2, and SSO support.
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import requests
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class MultiTenantJWTAuthentication(JWTAuthentication):
    """JWT authentication with multi-tenant support."""

    def get_user(self, validated_token):
        """Get user with organization context."""
        try:
            user_id = validated_token.get("user_id")
            organization_id = validated_token.get("organization_id")

            # Enhanced validation
            if not user_id:
                raise InvalidToken("Token contains no user ID")
            
            if not isinstance(user_id, (int, str)):
                raise InvalidToken("Invalid user ID format")

            # Validate user exists and is active
            user = User.objects.select_related('organization').get(
                id=user_id, 
                is_active=True
            )

            # Validate organization access
            if organization_id:
                if not user.organization or str(user.organization.id) != str(organization_id):
                    raise InvalidToken("User not authorized for this organization")
                user.current_organization_id = organization_id

            # Log successful authentication
            logger.info(f"User {user.email} authenticated successfully")
            return user
            
        except User.DoesNotExist:
            logger.warning(f"Authentication failed: User {user_id} not found")
            raise InvalidToken("User not found")
        except ValueError as e:
            logger.warning(f"Authentication failed: Invalid user ID format - {e}")
            raise InvalidToken("Invalid user ID format")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise InvalidToken("Authentication failed")


class OAuth2Authentication(authentication.BaseAuthentication):
    """OAuth2 authentication for third-party integrations."""

    def authenticate(self, request):
        """Authenticate using OAuth2 token."""
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # Verify OAuth2 token with provider
            user_info = self.verify_oauth2_token(token)
            if not user_info:
                return None

            # Get or create user
            user = self.get_or_create_user(user_info)
            return (user, token)

        except Exception as e:
            logger.error(f"OAuth2 authentication error: {e}")
            return None

    def verify_oauth2_token(self, token):
        """Verify OAuth2 token with provider."""
        try:
            # Verify with Google OAuth2
            response = requests.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token}",
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()

            # Verify with Microsoft OAuth2
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            logger.error(f"OAuth2 token verification error: {e}")
            return None

    def get_or_create_user(self, user_info):
        """Get or create user from OAuth2 user info."""
        email = user_info.get("email") or user_info.get("mail")
        if not email:
            raise exceptions.AuthenticationFailed("No email in OAuth2 response")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                full_name=user_info.get("name") or user_info.get("displayName", ""),
                is_active=True,
            )

        return user


class SSOAuthentication(authentication.BaseAuthentication):
    """SSO authentication for enterprise integrations."""

    def authenticate(self, request):
        """Authenticate using SSO."""
        sso_token = request.META.get("HTTP_X_SSO_TOKEN")
        if not sso_token:
            return None

        try:
            # Verify SSO token
            user_info = self.verify_sso_token(sso_token)
            if not user_info:
                return None

            # Get or create user
            user = self.get_or_create_sso_user(user_info)
            return (user, sso_token)

        except Exception as e:
            logger.error(f"SSO authentication error: {e}")
            return None

    def verify_sso_token(self, token):
        """Verify SSO token with identity provider."""
        try:
            # Decode JWT token
            decoded = jwt.decode(
                token,
                settings.SSO_PUBLIC_KEY,
                algorithms=["RS256"],
                options={"verify_exp": True},
            )

            return decoded

        except jwt.ExpiredSignatureError:
            logger.error("SSO token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid SSO token: {e}")
            return None

    def get_or_create_sso_user(self, user_info):
        """Get or create user from SSO user info."""
        email = user_info.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("No email in SSO response")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email, full_name=user_info.get("name", ""), is_active=True
            )

        return user


class APIKeyAuthentication(authentication.BaseAuthentication):
    """API key authentication for programmatic access."""

    def authenticate(self, request):
        """Authenticate using API key."""
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return None

        try:
            # Verify API key
            user = self.verify_api_key(api_key)
            if not user:
                return None

            return (user, api_key)

        except Exception as e:
            logger.error(f"API key authentication error: {e}")
            return None

    def verify_api_key(self, api_key):
        """Verify API key and return user."""
        try:
            # Decode API key
            decoded = jwt.decode(
                api_key,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )

            user_id = decoded.get("user_id")
            if not user_id:
                return None

            user = User.objects.get(id=user_id, is_active=True)
            return user

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None


class MultiFactorAuthentication:
    """Multi-factor authentication support."""

    @staticmethod
    def generate_totp_secret(user):
        """Generate TOTP secret for user."""
        import pyotp

        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save()

        return secret

    @staticmethod
    def verify_totp_code(user, code):
        """Verify TOTP code."""
        import pyotp

        if not user.totp_secret:
            return False

        totp = pyotp.TOTP(user.totp_secret)
        return totp.verify(code)

    @staticmethod
    def send_sms_code(user, phone_number):
        """Send SMS verification code."""
        import random
        import string

        # Generate 6-digit code
        code = "".join(random.choices(string.digits, k=6))

        # Store code in user session (in production, use Redis)
        user.sms_verification_code = code
        user.sms_verification_expires = datetime.now() + timedelta(minutes=5)
        user.save()

        # Send SMS (in production, use Twilio or similar)
        logger.info(f"SMS code for {phone_number}: {code}")

        return True

    @staticmethod
    def verify_sms_code(user, code):
        """Verify SMS code."""
        if not user.sms_verification_code:
            return False

        if datetime.now() > user.sms_verification_expires:
            return False

        if user.sms_verification_code == code:
            user.sms_verification_code = None
            user.sms_verification_expires = None
            user.save()
            return True

        return False


class TokenGenerator:
    """Token generation utilities."""

    @staticmethod
    def generate_jwt_token(user, organization=None):
        """Generate JWT token for user."""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "organization_id": organization.id if organization else None,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    @staticmethod
    def generate_api_key(user):
        """Generate API key for user."""
        payload = {
            "user_id": user.id,
            "type": "api_key",
            "exp": datetime.utcnow() + timedelta(days=365),
            "iat": datetime.utcnow(),
        }

        api_key = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return api_key

    @staticmethod
    def generate_refresh_token(user):
        """Generate refresh token."""
        refresh = RefreshToken.for_user(user)
        return str(refresh)


class PasswordPolicy:
    """Password policy enforcement."""

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SYMBOLS = True
    MAX_AGE_DAYS = 90

    @classmethod
    def validate_password(cls, password):
        """Validate password against policy."""
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")

        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if cls.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        if cls.REQUIRE_SYMBOLS and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            errors.append("Password must contain at least one special character")

        return errors

    @classmethod
    def is_password_expired(cls, user):
        """Check if user's password is expired."""
        if not user.password_changed_at:
            return True

        age = datetime.now() - user.password_changed_at
        return age.days > cls.MAX_AGE_DAYS


class SessionManagement:
    """Session management utilities."""

    @staticmethod
    def create_session(user, request):
        """Create user session."""
        session = {
            "user_id": user.id,
            "email": user.email,
            "organization_id": getattr(user, "current_organization_id", None),
            "ip_address": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
        }

        return session

    @staticmethod
    def update_session_activity(session):
        """Update session activity timestamp."""
        session["last_activity"] = datetime.now()
        return session

    @staticmethod
    def is_session_expired(session, max_idle_minutes=30):
        """Check if session is expired."""
        if not session.get("last_activity"):
            return True

        idle_time = datetime.now() - session["last_activity"]
        return idle_time.total_seconds() > (max_idle_minutes * 60)

    @staticmethod
    def invalidate_session(session):
        """Invalidate user session."""
        session["invalidated"] = True
        return session
