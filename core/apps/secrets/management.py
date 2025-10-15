"""
Secrets Management System
Supports AWS Secrets Manager, HashiCorp Vault, and environment variables
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SecretsManager:
    """Base secrets manager class"""
    
    def __init__(self):
        self.backend = getattr(settings, 'SECRET_BACKEND', 'environment')
        self.cache_ttl = getattr(settings, 'SECRET_CACHE_TTL', 300)  # 5 minutes
        
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get a secret value"""
        raise NotImplementedError
        
    def set_secret(self, key: str, value: Any) -> bool:
        """Set a secret value"""
        raise NotImplementedError
        
    def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        raise NotImplementedError


class EnvironmentSecretsManager(SecretsManager):
    """Environment variables secrets manager"""
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret from environment variables"""
        return os.environ.get(key, default)
    
    def set_secret(self, key: str, value: Any) -> bool:
        """Set secret in environment variables"""
        os.environ[key] = str(value)
        return True
    
    def delete_secret(self, key: str) -> bool:
        """Delete secret from environment variables"""
        if key in os.environ:
            del os.environ[key]
            return True
        return False


class AWSSecretsManager(SecretsManager):
    """AWS Secrets Manager implementation"""
    
    def __init__(self):
        super().__init__()
        self.region = getattr(settings, 'AWS_SECRETS_REGION', 'us-east-1')
        self.prefix = getattr(settings, 'AWS_SECRETS_PREFIX', 'helpdesk')
        
        try:
            import boto3
            self.client = boto3.client('secretsmanager', region_name=self.region)
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS Secrets Manager: {e}")
            raise
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret from AWS Secrets Manager"""
        cache_key = f"secret_{key}"
        
        # Check cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        try:
            secret_name = f"{self.prefix}/{key}"
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Parse JSON if possible
            try:
                value = json.loads(response['SecretString'])
            except (json.JSONDecodeError, KeyError):
                value = response.get('SecretString', default)
            
            # Cache the result
            cache.set(cache_key, value, self.cache_ttl)
            
            return value
            
        except self.client.exceptions.ResourceNotFoundException:
            logger.warning(f"Secret {key} not found in AWS Secrets Manager")
            return default
        except Exception as e:
            logger.error(f"Error retrieving secret {key} from AWS Secrets Manager: {e}")
            return default
    
    def set_secret(self, key: str, value: Any) -> bool:
        """Set secret in AWS Secrets Manager"""
        try:
            secret_name = f"{self.prefix}/{key}"
            secret_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            
            try:
                # Try to update existing secret
                self.client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_value
                )
            except self.client.exceptions.ResourceNotFoundException:
                # Create new secret
                self.client.create_secret(
                    Name=secret_name,
                    SecretString=secret_value,
                    Description=f"Secret for {key}"
                )
            
            # Clear cache
            cache_key = f"secret_{key}"
            cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting secret {key} in AWS Secrets Manager: {e}")
            return False
    
    def delete_secret(self, key: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            secret_name = f"{self.prefix}/{key}"
            self.client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
            
            # Clear cache
            cache_key = f"secret_{key}"
            cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting secret {key} from AWS Secrets Manager: {e}")
            return False


class VaultSecretsManager(SecretsManager):
    """HashiCorp Vault implementation"""
    
    def __init__(self):
        super().__init__()
        self.vault_url = getattr(settings, 'VAULT_URL', 'http://localhost:8200')
        self.vault_token = getattr(settings, 'VAULT_TOKEN', '')
        self.vault_path = getattr(settings, 'VAULT_PATH', 'secret/helpdesk')
        
        try:
            import hvac
            self.client = hvac.Client(url=self.vault_url, token=self.vault_token)
            
            # Test connection
            if not self.client.is_authenticated():
                logger.error("Vault authentication failed")
                raise Exception("Vault authentication failed")
                
        except ImportError:
            logger.error("hvac not installed. Install with: pip install hvac")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            raise
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret from Vault"""
        cache_key = f"vault_secret_{key}"
        
        # Check cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        try:
            secret_path = f"{self.vault_path}/{key}"
            response = self.client.secrets.kv.v2.read_secret_version(path=secret_path)
            
            value = response['data']['data'].get(key, default)
            
            # Cache the result
            cache.set(cache_key, value, self.cache_ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"Error retrieving secret {key} from Vault: {e}")
            return default
    
    def set_secret(self, key: str, value: Any) -> bool:
        """Set secret in Vault"""
        try:
            secret_path = f"{self.vault_path}/{key}"
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret={key: value}
            )
            
            # Clear cache
            cache_key = f"vault_secret_{key}"
            cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting secret {key} in Vault: {e}")
            return False
    
    def delete_secret(self, key: str) -> bool:
        """Delete secret from Vault"""
        try:
            secret_path = f"{self.vault_path}/{key}"
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=secret_path)
            
            # Clear cache
            cache_key = f"vault_secret_{key}"
            cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting secret {key} from Vault: {e}")
            return False


class SecretsManagerFactory:
    """Factory for creating secrets managers"""
    
    @staticmethod
    def create_manager(backend: str = None) -> SecretsManager:
        """Create a secrets manager instance"""
        if backend is None:
            backend = getattr(settings, 'SECRET_BACKEND', 'environment')
        
        if backend == 'environment':
            return EnvironmentSecretsManager()
        elif backend == 'aws':
            return AWSSecretsManager()
        elif backend == 'vault':
            return VaultSecretsManager()
        else:
            raise ValueError(f"Unknown secrets backend: {backend}")


# Global secrets manager instance
secrets_manager = SecretsManagerFactory.create_manager()


def get_secret(key: str, default: Any = None) -> Any:
    """Get a secret value"""
    return secrets_manager.get_secret(key, default)


def set_secret(key: str, value: Any) -> bool:
    """Set a secret value"""
    return secrets_manager.set_secret(key, value)


def delete_secret(key: str) -> bool:
    """Delete a secret"""
    return secrets_manager.delete_secret(key)


# Django settings integration
def configure_secrets():
    """Configure Django settings with secrets"""
    try:
        # Database secrets
        db_password = get_secret('DB_PASSWORD')
        if db_password:
            settings.DATABASES['default']['PASSWORD'] = db_password
        
        # Redis secrets
        redis_password = get_secret('REDIS_PASSWORD')
        if redis_password:
            redis_url = settings.CACHES['default']['LOCATION']
            if 'redis://' in redis_url:
                settings.CACHES['default']['LOCATION'] = f"redis://:{redis_password}@{redis_url.split('@')[-1]}"
        
        # Email secrets
        email_password = get_secret('EMAIL_HOST_PASSWORD')
        if email_password:
            settings.EMAIL_HOST_PASSWORD = email_password
        
        # Third-party service secrets
        openai_key = get_secret('OPENAI_API_KEY')
        if openai_key:
            settings.OPENAI_API_KEY = openai_key
        
        twilio_sid = get_secret('TWILIO_ACCOUNT_SID')
        if twilio_sid:
            settings.TWILIO_ACCOUNT_SID = twilio_sid
        
        twilio_token = get_secret('TWILIO_AUTH_TOKEN')
        if twilio_token:
            settings.TWILIO_AUTH_TOKEN = twilio_token
        
        sendgrid_key = get_secret('SENDGRID_API_KEY')
        if sendgrid_key:
            settings.SENDGRID_API_KEY = sendgrid_key
        
        aws_access_key = get_secret('AWS_ACCESS_KEY_ID')
        if aws_access_key:
            settings.AWS_ACCESS_KEY_ID = aws_access_key
        
        aws_secret_key = get_secret('AWS_SECRET_ACCESS_KEY')
        if aws_secret_key:
            settings.AWS_SECRET_ACCESS_KEY = aws_secret_key
        
        sentry_dsn = get_secret('SENTRY_DSN')
        if sentry_dsn:
            settings.SENTRY_DSN = sentry_dsn
        
        logger.info("Secrets configured successfully")
        
    except Exception as e:
        logger.error(f"Error configuring secrets: {e}")
        raise
