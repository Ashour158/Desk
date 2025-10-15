"""
Advanced Secret Management System for Enterprise Security.
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Enterprise-grade secret management system.
    Supports multiple backends: environment, AWS Secrets Manager, Azure Key Vault, HashiCorp Vault.
    """
    
    def __init__(self):
        self.backend = os.environ.get('SECRET_BACKEND', 'environment')
        self.master_key = self._get_master_key()
        self.cipher_suite = Fernet(self.master_key)
        
    def _get_master_key(self) -> bytes:
        """Get or generate master encryption key."""
        master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
        if not master_key:
            # Generate key from SECRET_KEY
            password = settings.SECRET_KEY.encode()
            salt = b'helpdesk_salt_2024'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            master_key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            master_key = master_key.encode()
        return master_key
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret from configured backend."""
        try:
            if self.backend == 'environment':
                return self._get_from_environment(key, default)
            elif self.backend == 'aws':
                return self._get_from_aws_secrets_manager(key, default)
            elif self.backend == 'azure':
                return self._get_from_azure_key_vault(key, default)
            elif self.backend == 'vault':
                return self._get_from_vault(key, default)
            else:
                logger.warning(f"Unknown secret backend: {self.backend}")
                return default
        except Exception as e:
            logger.error(f"Error getting secret {key}: {e}")
            return default
    
    def _get_from_environment(self, key: str, default: Any) -> Any:
        """Get secret from environment variables."""
        return os.environ.get(key, default)
    
    def _get_from_aws_secrets_manager(self, key: str, default: Any) -> Any:
        """Get secret from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            client = boto3.client('secretsmanager', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            response = client.get_secret_value(SecretId=key)
            return response['SecretString']
        except ImportError:
            logger.error("boto3 not installed for AWS Secrets Manager")
            return default
        except ClientError as e:
            logger.error(f"AWS Secrets Manager error: {e}")
            return default
    
    def _get_from_azure_key_vault(self, key: str, default: Any) -> Any:
        """Get secret from Azure Key Vault."""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=os.environ.get('AZURE_VAULT_URL'),
                credential=credential
            )
            secret = client.get_secret(key)
            return secret.value
        except ImportError:
            logger.error("azure-keyvault-secrets not installed")
            return default
        except Exception as e:
            logger.error(f"Azure Key Vault error: {e}")
            return default
    
    def _get_from_vault(self, key: str, default: Any) -> Any:
        """Get secret from HashiCorp Vault."""
        try:
            import hvac
            
            client = hvac.Client(
                url=os.environ.get('VAULT_URL', 'http://localhost:8200'),
                token=os.environ.get('VAULT_TOKEN')
            )
            response = client.secrets.kv.v2.read_secret_version(path=key)
            return response['data']['data']['value']
        except ImportError:
            logger.error("hvac not installed for HashiCorp Vault")
            return default
        except Exception as e:
            logger.error(f"HashiCorp Vault error: {e}")
            return default
    
    def encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value."""
        try:
            encrypted_value = self.cipher_suite.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_value).decode()
        except Exception as e:
            logger.error(f"Error encrypting secret: {e}")
            return value
    
    def decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt a secret value."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_value = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_value.decode()
        except Exception as e:
            logger.error(f"Error decrypting secret: {e}")
            return encrypted_value
    
    def rotate_secret(self, key: str) -> bool:
        """Rotate a secret key."""
        try:
            # Generate new secret
            new_secret = self._generate_secret()
            
            # Store new secret
            if self.backend == 'environment':
                os.environ[key] = new_secret
            elif self.backend == 'aws':
                self._update_aws_secret(key, new_secret)
            elif self.backend == 'azure':
                self._update_azure_secret(key, new_secret)
            elif self.backend == 'vault':
                self._update_vault_secret(key, new_secret)
            
            logger.info(f"Secret {key} rotated successfully")
            return True
        except Exception as e:
            logger.error(f"Error rotating secret {key}: {e}")
            return False
    
    def _generate_secret(self, length: int = 32) -> str:
        """Generate a cryptographically secure random secret."""
        import secrets
        return secrets.token_urlsafe(length)
    
    def _update_aws_secret(self, key: str, value: str) -> None:
        """Update secret in AWS Secrets Manager."""
        import boto3
        client = boto3.client('secretsmanager')
        client.update_secret(SecretId=key, SecretString=value)
    
    def _update_azure_secret(self, key: str, value: str) -> None:
        """Update secret in Azure Key Vault."""
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        
        credential = DefaultAzureCredential()
        client = SecretClient(
            vault_url=os.environ.get('AZURE_VAULT_URL'),
            credential=credential
        )
        client.set_secret(key, value)
    
    def _update_vault_secret(self, key: str, value: str) -> None:
        """Update secret in HashiCorp Vault."""
        import hvac
        
        client = hvac.Client(
            url=os.environ.get('VAULT_URL', 'http://localhost:8200'),
            token=os.environ.get('VAULT_TOKEN')
        )
        client.secrets.kv.v2.create_or_update_secret(path=key, secret={'value': value})
    
    def audit_secret_access(self, key: str, user: str, action: str) -> None:
        """Audit secret access for compliance."""
        audit_log = {
            'timestamp': str(timezone.now()),
            'key': key,
            'user': user,
            'action': action,
            'backend': self.backend
        }
        
        # Log to security audit log
        logger.info(f"Secret access audit: {audit_log}")
        
        # Store in cache for real-time monitoring
        cache_key = f"secret_audit_{key}_{user}"
        cache.set(cache_key, audit_log, timeout=3600)  # 1 hour


# Global secret manager instance
secret_manager = SecretManager()


class SecretField:
    """
    Django model field for encrypted secrets.
    """
    
    def __init__(self, *args, **kwargs):
        self.encrypted = kwargs.pop('encrypted', True)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when reading from database."""
        if value is None:
            return value
        if self.encrypted:
            return secret_manager.decrypt_secret(value)
        return value
    
    def to_python(self, value):
        """Convert value to Python object."""
        if value is None:
            return value
        if self.encrypted:
            return secret_manager.decrypt_secret(value)
        return value
    
    def get_prep_value(self, value):
        """Encrypt value before storing in database."""
        if value is None:
            return value
        if self.encrypted:
            return secret_manager.encrypt_secret(value)
        return value


class SecretValidator:
    """
    Validator for secret strength and compliance.
    """
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        score = 0
        issues = []
        
        if len(password) >= 8:
            score += 1
        else:
            issues.append("Password must be at least 8 characters long")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            issues.append("Password must contain uppercase letters")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            issues.append("Password must contain lowercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            issues.append("Password must contain numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            issues.append("Password must contain special characters")
        
        return {
            'score': score,
            'max_score': 5,
            'strength': 'weak' if score < 3 else 'medium' if score < 5 else 'strong',
            'issues': issues
        }
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format."""
        # API keys should be base64-like strings
        try:
            base64.b64decode(api_key, validate=True)
            return True
        except:
            return False
