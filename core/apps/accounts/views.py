"""
Authentication views for helpdesk platform.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice

from .serializers import UserSerializer, UserRegistrationSerializer
from .models import UserProfile
from apps.organizations.models import Organization

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration view."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Create new user account."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get organization from request or create default
            organization_slug = request.data.get("organization_slug")
            if organization_slug:
                try:
                    organization = Organization.objects.get(slug=organization_slug)
                except Organization.DoesNotExist:
                    return Response(
                        {"error": "Organization not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # Create default organization for new users
                organization = Organization.objects.create(
                    name=f"{request.data.get('full_name', 'User')}'s Organization",
                    slug=f"org-{request.data.get('email', '').split('@')[0]}",
                    subscription_tier="free",
                )

            # Create user
            user = serializer.save(organization=organization)

            # Send welcome email
            self.send_welcome_email(user)

            return Response(
                {
                    "message": "User created successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_welcome_email(self, user):
        """Send welcome email to new user."""
        subject = "Welcome to Helpdesk Platform"
        message = f"""
        Hello {user.full_name or user.email},
        
        Welcome to our helpdesk platform! Your account has been created successfully.
        
        You can now:
        - Submit support tickets
        - Access our knowledge base
        - Track your requests
        
        If you have any questions, please don't hesitate to contact us.
        
        Best regards,
        The Support Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile management view."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get current user."""
        return self.request.user


class ChangePasswordView(APIView):
    """Change user password view."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Change user password."""
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Old password and new password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"})


class PasswordResetView(APIView):
    """Password reset request view."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Send password reset email."""
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        subject = "Password Reset Request"
        message = f"""
        Hello {user.full_name or user.email},
        
        You requested a password reset for your account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The Support Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent"})


class PasswordResetConfirmView(APIView):
    """Password reset confirmation view."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Confirm password reset."""
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not uid or not token or not new_password:
            return Response(
                {"error": "UID, token, and new password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successfully"})


class TwoFactorSetupView(APIView):
    """Two-factor authentication setup view."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get 2FA setup information."""
        user = request.user

        # Create TOTP device if it doesn't exist
        device, created = TOTPDevice.objects.get_or_create(user=user, name="default")

        if created:
            device.save()

        # Generate QR code data
        qr_data = device.config_url

        return Response(
            {
                "secret": device.key,
                "qr_code": qr_data,
                "backup_codes": [],  # Would generate backup codes in production
            }
        )

    def post(self, request):
        """Verify 2FA setup."""
        user = request.user
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            device = TOTPDevice.objects.get(user=user, name="default")
            if device.verify_token(token):
                user.two_factor_enabled = True
                user.save()
                return Response({"message": "2FA enabled successfully"})
            else:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
        except TOTPDevice.DoesNotExist:
            return Response(
                {"error": "2FA device not found"}, status=status.HTTP_404_NOT_FOUND
            )


class TwoFactorVerifyView(APIView):
    """Two-factor authentication verification view."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Verify 2FA token."""
        user = request.user
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            device = TOTPDevice.objects.get(user=user, name="default")
            if device.verify_token(token):
                return Response({"message": "2FA verified successfully"})
            else:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
        except TOTPDevice.DoesNotExist:
            return Response(
                {"error": "2FA not enabled"}, status=status.HTTP_404_NOT_FOUND
            )


class TwoFactorDisableView(APIView):
    """Disable two-factor authentication view."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Disable 2FA."""
        user = request.user
        password = request.data.get("password")

        if not password:
            return Response(
                {"error": "Password required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Delete TOTP device
        TOTPDevice.objects.filter(user=user).delete()
        user.two_factor_enabled = False
        user.save()

        return Response({"message": "2FA disabled successfully"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """Verify JWT token."""
    return Response({"valid": True, "user": UserSerializer(request.user).data})
