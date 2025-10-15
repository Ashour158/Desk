"""
Authentication serializers for helpdesk platform.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for API responses."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    is_agent = serializers.BooleanField(read_only=True)
    is_customer = serializers.BooleanField(read_only=True)
    is_technician = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "phone",
            "avatar",
            "timezone",
            "language",
            "is_verified",
            "last_active_at",
            "is_agent",
            "is_customer",
            "is_technician",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    organization_slug = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "full_name",
            "phone",
            "password",
            "password_confirm",
            "organization_slug",
            "timezone",
            "language",
        ]

    def validate(self, attrs):
        """Validate registration data."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists")
        return value

    def create(self, validated_data):
        """Create new user."""
        validated_data.pop("password_confirm")
        validated_data.pop("organization_slug", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data.get("username", validated_data["email"]),
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            phone=validated_data.get("phone", ""),
            timezone=validated_data.get("timezone", "UTC"),
            language=validated_data.get("language", "en"),
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "bio",
            "website",
            "location",
            "birth_date",
            "job_title",
            "department",
            "manager",
            "theme",
            "notifications_email",
            "notifications_browser",
            "notifications_mobile",
            "linkedin_url",
            "twitter_handle",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate password change data."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Password reset request serializer."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer."""

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate password reset data."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class TwoFactorSetupSerializer(serializers.Serializer):
    """Two-factor authentication setup serializer."""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate 2FA token."""
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Token must be 6 digits")
        return value


class TwoFactorVerifySerializer(serializers.Serializer):
    """Two-factor authentication verification serializer."""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate 2FA token."""
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Token must be 6 digits")
        return value


class TwoFactorDisableSerializer(serializers.Serializer):
    """Two-factor authentication disable serializer."""

    password = serializers.CharField(required=True)

    def validate_password(self, value):
        """Validate user password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect")
        return value
