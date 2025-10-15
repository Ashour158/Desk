"""
Organization models for multi-tenancy.
"""

from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt


class Organization(models.Model):
    """Multi-tenant organization."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    domain = models.CharField(max_length=255, blank=True)
    subscription_tier = models.CharField(max_length=50, default="basic")
    settings = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Encrypted fields
    api_key = encrypt(models.CharField(max_length=255, blank=True))
    smtp_password = encrypt(models.CharField(max_length=255, blank=True))

    def __str__(self):
        return self.name


class Department(models.Model):
    """Department within organization."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Customer(models.Model):
    """Extended customer profile."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    company = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.organization.name})"
