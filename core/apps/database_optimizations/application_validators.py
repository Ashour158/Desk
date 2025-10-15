"""
Application-level validation for data integrity.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.tickets.models import Ticket, TicketComment, TicketAttachment
from apps.accounts.models import User
import re
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class DataIntegrityValidator:
    """
    Comprehensive data integrity validation utilities.
    """
    
    @staticmethod
    def validate_ticket_data(ticket_data):
        """
        Validate ticket data for integrity.
        """
        errors = []
        
        # Validate subject
        if not ticket_data.get('subject') or ticket_data['subject'].strip() == '':
            errors.append('Ticket subject is required and cannot be empty')
        
        # Validate description
        if not ticket_data.get('description') or ticket_data['description'].strip() == '':
            errors.append('Ticket description is required and cannot be empty')
        
        # Validate status
        valid_statuses = ['new', 'open', 'pending', 'resolved', 'closed', 'cancelled']
        if ticket_data.get('status') and ticket_data['status'] not in valid_statuses:
            errors.append(f'Invalid ticket status: {ticket_data["status"]}. Must be one of: {valid_statuses}')
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if ticket_data.get('priority') and ticket_data['priority'] not in valid_priorities:
            errors.append(f'Invalid ticket priority: {ticket_data["priority"]}. Must be one of: {valid_priorities}')
        
        # Validate channel
        valid_channels = ['email', 'web', 'phone', 'chat', 'social', 'api']
        if ticket_data.get('channel') and ticket_data['channel'] not in valid_channels:
            errors.append(f'Invalid ticket channel: {ticket_data["channel"]}. Must be one of: {valid_channels}')
        
        # Validate satisfaction score
        if ticket_data.get('customer_satisfaction_score') is not None:
            score = ticket_data['customer_satisfaction_score']
            if not isinstance(score, int) or score < 1 or score > 5:
                errors.append(f'Invalid satisfaction score: {score}. Must be an integer between 1 and 5')
        
        # Validate customer exists and is a customer
        if ticket_data.get('customer_id'):
            try:
                customer = User.objects.get(id=ticket_data['customer_id'])
                if customer.role != 'customer':
                    errors.append(f'User {customer.email} is not a customer (role: {customer.role})')
            except User.DoesNotExist:
                errors.append(f'Customer with ID {ticket_data["customer_id"]} does not exist')
        
        # Validate assigned agent exists and is an agent
        if ticket_data.get('assigned_agent_id'):
            try:
                agent = User.objects.get(id=ticket_data['assigned_agent_id'])
                if agent.role not in ['admin', 'manager', 'agent']:
                    errors.append(f'User {agent.email} is not an agent (role: {agent.role})')
            except User.DoesNotExist:
                errors.append(f'Agent with ID {ticket_data["assigned_agent_id"]} does not exist')
        
        # Validate organization exists
        if ticket_data.get('organization_id'):
            try:
                Organization.objects.get(id=ticket_data['organization_id'])
            except Organization.DoesNotExist:
                errors.append(f'Organization with ID {ticket_data["organization_id"]} does not exist')
        
        # Validate timestamp consistency
        if ticket_data.get('created_at') and ticket_data.get('updated_at'):
            if ticket_data['updated_at'] < ticket_data['created_at']:
                errors.append('Updated timestamp cannot be before created timestamp')
        
        if ticket_data.get('resolved_at') and ticket_data.get('created_at'):
            if ticket_data['resolved_at'] < ticket_data['created_at']:
                errors.append('Resolved timestamp cannot be before created timestamp')
        
        if ticket_data.get('first_response_at') and ticket_data.get('created_at'):
            if ticket_data['first_response_at'] < ticket_data['created_at']:
                errors.append('First response timestamp cannot be before created timestamp')
        
        if ticket_data.get('closed_at') and ticket_data.get('created_at'):
            if ticket_data['closed_at'] < ticket_data['created_at']:
                errors.append('Closed timestamp cannot be before created timestamp')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_comment_data(comment_data):
        """
        Validate ticket comment data for integrity.
        """
        errors = []
        
        # Validate content
        if not comment_data.get('content') or comment_data['content'].strip() == '':
            errors.append('Comment content is required and cannot be empty')
        
        # Validate comment type
        valid_types = ['public', 'internal', 'system']
        if comment_data.get('comment_type') and comment_data['comment_type'] not in valid_types:
            errors.append(f'Invalid comment type: {comment_data["comment_type"]}. Must be one of: {valid_types}')
        
        # Validate ticket exists
        if comment_data.get('ticket_id'):
            try:
                Ticket.objects.get(id=comment_data['ticket_id'])
            except Ticket.DoesNotExist:
                errors.append(f'Ticket with ID {comment_data["ticket_id"]} does not exist')
        
        # Validate author exists
        if comment_data.get('author_id'):
            try:
                User.objects.get(id=comment_data['author_id'])
            except User.DoesNotExist:
                errors.append(f'Author with ID {comment_data["author_id"]} does not exist')
        
        # Validate timestamp consistency
        if comment_data.get('created_at') and comment_data.get('updated_at'):
            if comment_data['updated_at'] < comment_data['created_at']:
                errors.append('Updated timestamp cannot be before created timestamp')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_attachment_data(attachment_data):
        """
        Validate ticket attachment data for integrity.
        """
        errors = []
        
        # Validate file name
        if not attachment_data.get('file_name') or attachment_data['file_name'].strip() == '':
            errors.append('File name is required and cannot be empty')
        
        # Validate file path
        if not attachment_data.get('file_path') or attachment_data['file_path'].strip() == '':
            errors.append('File path is required and cannot be empty')
        
        # Validate file size
        if attachment_data.get('file_size') is not None:
            if not isinstance(attachment_data['file_size'], int) or attachment_data['file_size'] <= 0:
                errors.append(f'Invalid file size: {attachment_data["file_size"]}. Must be a positive integer')
        
        # Validate download count
        if attachment_data.get('download_count') is not None:
            if not isinstance(attachment_data['download_count'], int) or attachment_data['download_count'] < 0:
                errors.append(f'Invalid download count: {attachment_data["download_count"]}. Must be a non-negative integer')
        
        # Validate ticket exists
        if attachment_data.get('ticket_id'):
            try:
                Ticket.objects.get(id=attachment_data['ticket_id'])
            except Ticket.DoesNotExist:
                errors.append(f'Ticket with ID {attachment_data["ticket_id"]} does not exist')
        
        # Validate comment exists (if provided)
        if attachment_data.get('comment_id'):
            try:
                TicketComment.objects.get(id=attachment_data['comment_id'])
            except TicketComment.DoesNotExist:
                errors.append(f'Comment with ID {attachment_data["comment_id"]} does not exist')
        
        # Validate uploaded by exists
        if attachment_data.get('uploaded_by_id'):
            try:
                User.objects.get(id=attachment_data['uploaded_by_id'])
            except User.DoesNotExist:
                errors.append(f'User with ID {attachment_data["uploaded_by_id"]} does not exist')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_user_data(user_data):
        """
        Validate user data for integrity.
        """
        errors = []
        
        # Validate email
        if not user_data.get('email') or user_data['email'].strip() == '':
            errors.append('Email is required and cannot be empty')
        else:
            email = user_data['email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append(f'Invalid email format: {email}')
        
        # Validate role
        valid_roles = ['admin', 'manager', 'agent', 'customer']
        if user_data.get('role') and user_data['role'] not in valid_roles:
            errors.append(f'Invalid user role: {user_data["role"]}. Must be one of: {valid_roles}')
        
        # Validate customer tier
        valid_tiers = ['basic', 'premium', 'enterprise']
        if user_data.get('customer_tier') and user_data['customer_tier'] not in valid_tiers:
            errors.append(f'Invalid customer tier: {user_data["customer_tier"]}. Must be one of: {valid_tiers}')
        
        # Validate availability status
        valid_statuses = ['available', 'busy', 'away', 'offline']
        if user_data.get('availability_status') and user_data['availability_status'] not in valid_statuses:
            errors.append(f'Invalid availability status: {user_data["availability_status"]}. Must be one of: {valid_statuses}')
        
        # Validate max concurrent tickets
        if user_data.get('max_concurrent_tickets') is not None:
            if not isinstance(user_data['max_concurrent_tickets'], int) or user_data['max_concurrent_tickets'] <= 0:
                errors.append(f'Invalid max concurrent tickets: {user_data["max_concurrent_tickets"]}. Must be a positive integer')
        
        # Validate organization exists
        if user_data.get('organization_id'):
            try:
                Organization.objects.get(id=user_data['organization_id'])
            except Organization.DoesNotExist:
                errors.append(f'Organization with ID {user_data["organization_id"]} does not exist')
        
        # Validate timestamp consistency
        if user_data.get('date_joined') and user_data.get('last_active_at'):
            if user_data['last_active_at'] < user_data['date_joined']:
                errors.append('Last active timestamp cannot be before date joined')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_organization_data(organization_data):
        """
        Validate organization data for integrity.
        """
        errors = []
        
        # Validate name
        if not organization_data.get('name') or organization_data['name'].strip() == '':
            errors.append('Organization name is required and cannot be empty')
        
        # Validate slug
        if not organization_data.get('slug') or organization_data['slug'].strip() == '':
            errors.append('Organization slug is required and cannot be empty')
        else:
            slug = organization_data['slug']
            if not re.match(r'^[a-z0-9-]+$', slug):
                errors.append(f'Invalid slug format: {slug}. Must contain only lowercase letters, numbers, and hyphens')
        
        # Validate domain
        if organization_data.get('domain'):
            domain = organization_data['domain']
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
                errors.append(f'Invalid domain format: {domain}')
        
        # Validate timestamp consistency
        if organization_data.get('created_at') and organization_data.get('updated_at'):
            if organization_data['updated_at'] < organization_data['created_at']:
                errors.append('Updated timestamp cannot be before created timestamp')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_session_data(session_data):
        """
        Validate user session data for integrity.
        """
        errors = []
        
        # Validate session key
        if not session_data.get('session_key') or session_data['session_key'].strip() == '':
            errors.append('Session key is required and cannot be empty')
        
        # Validate user exists
        if session_data.get('user_id'):
            try:
                User.objects.get(id=session_data['user_id'])
            except User.DoesNotExist:
                errors.append(f'User with ID {session_data["user_id"]} does not exist')
        
        # Validate timestamp consistency
        if session_data.get('created_at') and session_data.get('last_activity'):
            if session_data['last_activity'] < session_data['created_at']:
                errors.append('Last activity timestamp cannot be before created timestamp')
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_permission_data(permission_data):
        """
        Validate user permission data for integrity.
        """
        errors = []
        
        # Validate permission name
        if not permission_data.get('permission') or permission_data['permission'].strip() == '':
            errors.append('Permission name is required and cannot be empty')
        
        # Validate user exists
        if permission_data.get('user_id'):
            try:
                User.objects.get(id=permission_data['user_id'])
            except User.DoesNotExist:
                errors.append(f'User with ID {permission_data["user_id"]} does not exist')
        
        # Validate granted by exists
        if permission_data.get('granted_by_id'):
            try:
                User.objects.get(id=permission_data['granted_by_id'])
            except User.DoesNotExist:
                errors.append(f'Granted by user with ID {permission_data["granted_by_id"]} does not exist')
        
        # Validate expiration date
        if permission_data.get('expires_at') and permission_data.get('granted_at'):
            if permission_data['expires_at'] < permission_data['granted_at']:
                errors.append('Expiration date cannot be before granted date')
        
        if errors:
            raise ValidationError(errors)
        
        return True


class ModelValidationMixin:
    """
    Mixin to add data integrity validation to Django models.
    """
    
    def clean(self):
        """
        Override clean method to add data integrity validation.
        """
        super().clean()
        
        # Get the appropriate validator based on model type
        if isinstance(self, Ticket):
            DataIntegrityValidator.validate_ticket_data(self.__dict__)
        elif isinstance(self, TicketComment):
            DataIntegrityValidator.validate_comment_data(self.__dict__)
        elif isinstance(self, TicketAttachment):
            DataIntegrityValidator.validate_attachment_data(self.__dict__)
        elif isinstance(self, User):
            DataIntegrityValidator.validate_user_data(self.__dict__)
        elif isinstance(self, Organization):
            DataIntegrityValidator.validate_organization_data(self.__dict__)
    
    def save(self, *args, **kwargs):
        """
        Override save method to ensure validation runs.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class DataIntegrityMonitor:
    """
    Monitor for data integrity issues in real-time.
    """
    
    @staticmethod
    def check_orphaned_records():
        """
        Check for orphaned records across all tables.
        """
        issues = []
        
        # Check for orphaned tickets
        orphaned_tickets = Ticket.objects.filter(
            organization__isnull=True
        ).count()
        if orphaned_tickets > 0:
            issues.append(f'{orphaned_tickets} orphaned tickets found')
        
        # Check for orphaned comments
        orphaned_comments = TicketComment.objects.filter(
            ticket__isnull=True
        ).count()
        if orphaned_comments > 0:
            issues.append(f'{orphaned_comments} orphaned comments found')
        
        # Check for orphaned attachments
        orphaned_attachments = TicketAttachment.objects.filter(
            ticket__isnull=True
        ).count()
        if orphaned_attachments > 0:
            issues.append(f'{orphaned_attachments} orphaned attachments found')
        
        return issues
    
    @staticmethod
    def check_duplicate_records():
        """
        Check for duplicate records across all tables.
        """
        issues = []
        
        # Check for duplicate ticket numbers
        duplicate_tickets = Ticket.objects.values('ticket_number').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        if duplicate_tickets.exists():
            issues.append(f'{duplicate_tickets.count()} duplicate ticket numbers found')
        
        # Check for duplicate session keys
        duplicate_sessions = User.objects.filter(
            sessions__isnull=False
        ).values('sessions__session_key').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        if duplicate_sessions.exists():
            issues.append(f'{duplicate_sessions.count()} duplicate session keys found')
        
        return issues
    
    @staticmethod
    def check_null_values():
        """
        Check for NULL values in required fields.
        """
        issues = []
        
        # Check for NULL ticket subjects
        null_subjects = Ticket.objects.filter(
            models.Q(subject__isnull=True) | models.Q(subject='')
        ).count()
        if null_subjects > 0:
            issues.append(f'{null_subjects} tickets with NULL subjects found')
        
        # Check for NULL user emails
        null_emails = User.objects.filter(
            models.Q(email__isnull=True) | models.Q(email='')
        ).count()
        if null_emails > 0:
            issues.append(f'{null_emails} users with NULL emails found')
        
        return issues
    
    @staticmethod
    def check_invalid_enum_values():
        """
        Check for invalid enum values.
        """
        issues = []
        
        # Check for invalid ticket statuses
        invalid_statuses = Ticket.objects.exclude(
            status__in=['new', 'open', 'pending', 'resolved', 'closed', 'cancelled']
        ).count()
        if invalid_statuses > 0:
            issues.append(f'{invalid_statuses} tickets with invalid statuses found')
        
        # Check for invalid user roles
        invalid_roles = User.objects.exclude(
            role__in=['admin', 'manager', 'agent', 'customer']
        ).count()
        if invalid_roles > 0:
            issues.append(f'{invalid_roles} users with invalid roles found')
        
        return issues
    
    @staticmethod
    def check_timestamp_consistency():
        """
        Check for timestamp consistency issues.
        """
        issues = []
        
        # Check for tickets with updated_at before created_at
        inconsistent_tickets = Ticket.objects.filter(
            updated_at__lt=models.F('created_at')
        ).count()
        if inconsistent_tickets > 0:
            issues.append(f'{inconsistent_tickets} tickets with inconsistent timestamps found')
        
        return issues
    
    @staticmethod
    def run_comprehensive_check():
        """
        Run comprehensive data integrity check.
        """
        all_issues = []
        
        all_issues.extend(DataIntegrityMonitor.check_orphaned_records())
        all_issues.extend(DataIntegrityMonitor.check_duplicate_records())
        all_issues.extend(DataIntegrityMonitor.check_null_values())
        all_issues.extend(DataIntegrityMonitor.check_invalid_enum_values())
        all_issues.extend(DataIntegrityMonitor.check_timestamp_consistency())
        
        if all_issues:
            logger.warning(f'Data integrity issues found: {all_issues}')
        else:
            logger.info('No data integrity issues found')
        
        return all_issues


# Export utilities
__all__ = [
    'DataIntegrityValidator',
    'ModelValidationMixin',
    'DataIntegrityMonitor'
]
