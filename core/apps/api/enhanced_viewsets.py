"""
Enhanced ViewSets with comprehensive validation, security, and standardized responses.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max, Min
from django.contrib.auth import get_user_model
import logging

from .enhanced_pagination import EnhancedPageNumberPagination, AdvancedPaginationViewSet
from .file_upload_security import FileUploadViewMixin, get_file_upload_config
from .standardized_responses import APIResponseMixin, error_manager
from .enhanced_validation import EnhancedValidationMixin, validation_manager
from apps.organizations.models import Organization
from apps.tickets.models import Ticket, TicketComment
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class BaseEnhancedViewSet(APIResponseMixin, AdvancedPaginationViewSet, FileUploadViewMixin):
    """
    Base ViewSet with enhanced features for all API endpoints.
    """
    
    pagination_class = EnhancedPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get queryset with organization filtering and optimization.
        """
        queryset = super().get_queryset()
        
        # Apply organization filtering
        if hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Perform create with enhanced validation and organization assignment.
        """
        # Add organization and user context
        if hasattr(serializer.Meta.model, 'organization'):
            serializer.save(
                organization=self.request.user.organization,
                created_by=self.request.user
            )
        else:
            serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """
        Perform update with enhanced validation.
        """
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """
        Perform soft delete if supported, otherwise hard delete.
        """
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            instance.save()
        else:
            instance.delete()
    
    def list(self, request, *args, **kwargs):
        """
        Enhanced list method with caching and optimization.
        """
        # Generate cache key
        cache_key = f"{self.__class__.__name__}_list_{request.user.organization.id}_{request.GET.urlencode()}"
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get queryset with filtering
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data
        
        # Cache response for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)
    
    def create(self, request, *args, **kwargs):
        """
        Enhanced create method with validation and error handling.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                # Perform additional validation
                validation_result = self._validate_instance(serializer.validated_data)
                if not validation_result['is_valid']:
                    return self.validation_error(validation_result['errors'])
                
                # Save with transaction
                with transaction.atomic():
                    instance = serializer.save()
                    self.perform_create(serializer)
                
                return self.success_response(
                    data=serializer.data,
                    message=f"{self.__class__.__name__.replace('ViewSet', '')} created successfully",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return self.validation_error(serializer.errors)
                
        except ValidationError as e:
            return self.validation_error(str(e))
        except Exception as e:
            logger.error(f"Create error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to create resource")
    
    def update(self, request, *args, **kwargs):
        """
        Enhanced update method with validation and error handling.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            
            if serializer.is_valid():
                # Perform additional validation
                validation_result = self._validate_instance(serializer.validated_data, instance)
                if not validation_result['is_valid']:
                    return self.validation_error(validation_result['errors'])
                
                # Save with transaction
                with transaction.atomic():
                    serializer.save()
                    self.perform_update(serializer)
                
                return self.success_response(
                    data=serializer.data,
                    message=f"{self.__class__.__name__.replace('ViewSet', '')} updated successfully"
                )
            else:
                return self.validation_error(serializer.errors)
                
        except ValidationError as e:
            return self.validation_error(str(e))
        except Exception as e:
            logger.error(f"Update error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to update resource")
    
    def destroy(self, request, *args, **kwargs):
        """
        Enhanced destroy method with soft delete support.
        """
        try:
            instance = self.get_object()
            
            # Check permissions
            if not self._can_delete(instance):
                return self.insufficient_permissions("You don't have permission to delete this resource")
            
            # Perform soft delete
            with transaction.atomic():
                self.perform_destroy(instance)
            
            return self.success_response(
                message=f"{self.__class__.__name__.replace('ViewSet', '')} deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            logger.error(f"Delete error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to delete resource")
    
    def _validate_instance(self, data, instance=None):
        """
        Validate instance data using enhanced validation.
        """
        try:
            # Create temporary instance for validation
            if instance:
                temp_instance = instance
                for key, value in data.items():
                    setattr(temp_instance, key, value)
            else:
                temp_instance = self.get_serializer().Meta.model(**data)
            
            # Perform validation
            validation_result = validation_manager.validate_model_instance(temp_instance)
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {'is_valid': False, 'errors': [str(e)]}
    
    def _can_delete(self, instance):
        """
        Check if user can delete the instance.
        """
        # Add custom permission logic here
        return True
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics for the model.
        """
        try:
            queryset = self.get_queryset()
            
            # Calculate basic statistics
            stats = {
                'total_count': queryset.count(),
                'active_count': queryset.filter(is_active=True).count() if hasattr(queryset.model, 'is_active') else queryset.count(),
                'created_today': queryset.filter(created_at__date=timezone.now().date()).count(),
                'created_this_week': queryset.filter(created_at__week=timezone.now().isocalendar()[1]).count(),
                'created_this_month': queryset.filter(created_at__month=timezone.now().month).count(),
            }
            
            # Add model-specific statistics
            if hasattr(queryset.model, 'status'):
                stats['status_distribution'] = dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count'))
            
            if hasattr(queryset.model, 'priority'):
                stats['priority_distribution'] = dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count'))
            
            return self.success_response(data=stats)
            
        except Exception as e:
            logger.error(f"Statistics error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to get statistics")
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create multiple instances.
        """
        try:
            data = request.data
            if not isinstance(data, list):
                return self.validation_error("Data must be a list of objects")
            
            created_instances = []
            errors = []
            
            with transaction.atomic():
                for i, item_data in enumerate(data):
                    try:
                        serializer = self.get_serializer(data=item_data)
                        if serializer.is_valid():
                            instance = serializer.save()
                            self.perform_create(serializer)
                            created_instances.append(serializer.data)
                        else:
                            errors.append({
                                'index': i,
                                'errors': serializer.errors
                            })
                    except Exception as e:
                        errors.append({
                            'index': i,
                            'errors': [str(e)]
                        })
            
            return self.success_response(
                data={
                    'created_count': len(created_instances),
                    'error_count': len(errors),
                    'created_instances': created_instances,
                    'errors': errors
                },
                message=f"Bulk create completed: {len(created_instances)} created, {len(errors)} errors"
            )
            
        except Exception as e:
            logger.error(f"Bulk create error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to perform bulk create")
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update multiple instances.
        """
        try:
            data = request.data
            if not isinstance(data, list):
                return self.validation_error("Data must be a list of objects with 'id' field")
            
            updated_instances = []
            errors = []
            
            with transaction.atomic():
                for i, item_data in enumerate(data):
                    try:
                        if 'id' not in item_data:
                            errors.append({
                                'index': i,
                                'errors': ['ID field is required for bulk update']
                            })
                            continue
                        
                        instance = self.get_queryset().get(id=item_data['id'])
                        serializer = self.get_serializer(instance, data=item_data, partial=True)
                        
                        if serializer.is_valid():
                            serializer.save()
                            self.perform_update(serializer)
                            updated_instances.append(serializer.data)
                        else:
                            errors.append({
                                'index': i,
                                'id': item_data['id'],
                                'errors': serializer.errors
                            })
                    except Exception as e:
                        errors.append({
                            'index': i,
                            'id': item_data.get('id'),
                            'errors': [str(e)]
                        })
            
            return self.success_response(
                data={
                    'updated_count': len(updated_instances),
                    'error_count': len(errors),
                    'updated_instances': updated_instances,
                    'errors': errors
                },
                message=f"Bulk update completed: {len(updated_instances)} updated, {len(errors)} errors"
            )
            
        except Exception as e:
            logger.error(f"Bulk update error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to perform bulk update")
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Bulk delete multiple instances.
        """
        try:
            ids = request.data.get('ids', [])
            if not isinstance(ids, list):
                return self.validation_error("IDs must be a list")
            
            deleted_count = 0
            errors = []
            
            with transaction.atomic():
                for id_value in ids:
                    try:
                        instance = self.get_queryset().get(id=id_value)
                        if self._can_delete(instance):
                            self.perform_destroy(instance)
                            deleted_count += 1
                        else:
                            errors.append({
                                'id': id_value,
                                'error': 'Permission denied'
                            })
                    except Exception as e:
                        errors.append({
                            'id': id_value,
                            'error': str(e)
                        })
            
            return self.success_response(
                data={
                    'deleted_count': deleted_count,
                    'error_count': len(errors),
                    'errors': errors
                },
                message=f"Bulk delete completed: {deleted_count} deleted, {len(errors)} errors"
            )
            
        except Exception as e:
            logger.error(f"Bulk delete error in {self.__class__.__name__}: {e}")
            return self.internal_server_error("Failed to perform bulk delete")


class EnhancedTicketViewSet(BaseEnhancedViewSet):
    """
    Enhanced Ticket ViewSet with comprehensive validation and features.
    """
    
    queryset = Ticket.objects.all()
    serializer_class = None  # Will be set in the actual implementation
    
    def get_queryset(self):
        """
        Get tickets with organization filtering and optimization.
        """
        queryset = super().get_queryset()
        
        # Apply organization filtering
        if hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        # Apply role-based filtering
        if self.request.user.role == 'customer':
            queryset = queryset.filter(customer=self.request.user)
        
        return queryset.select_related(
            'organization', 'customer', 'assigned_agent', 'created_by'
        ).prefetch_related('comments', 'attachments', 'tags')
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign ticket to an agent.
        """
        try:
            ticket = self.get_object()
            agent_id = request.data.get('agent_id')
            
            if not agent_id:
                return self.validation_error({'agent_id': 'Agent ID is required'})
            
            # Validate agent exists and belongs to organization
            agent = User.objects.filter(
                id=agent_id,
                organization=ticket.organization,
                role__in=['agent', 'manager', 'admin']
            ).first()
            
            if not agent:
                return self.resource_not_found('Agent')
            
            ticket.assigned_agent = agent
            ticket.status = 'open'
            ticket.save()
            
            return self.success_response(
                data=self.get_serializer(ticket).data,
                message="Ticket assigned successfully"
            )
            
        except Exception as e:
            logger.error(f"Ticket assignment error: {e}")
            return self.internal_server_error("Failed to assign ticket")
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close a ticket.
        """
        try:
            ticket = self.get_object()
            resolution = request.data.get('resolution', '')
            
            ticket.status = 'closed'
            ticket.resolution = resolution
            ticket.closed_at = timezone.now()
            ticket.save()
            
            return self.success_response(
                data=self.get_serializer(ticket).data,
                message="Ticket closed successfully"
            )
            
        except Exception as e:
            logger.error(f"Ticket close error: {e}")
            return self.internal_server_error("Failed to close ticket")
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add a comment to a ticket.
        """
        try:
            ticket = self.get_object()
            content = request.data.get('content')
            is_internal = request.data.get('is_internal', False)
            
            if not content:
                return self.validation_error({'content': 'Comment content is required'})
            
            comment = TicketComment.objects.create(
                ticket=ticket,
                author=request.user,
                content=content,
                is_internal=is_internal
            )
            
            return self.success_response(
                data={
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.full_name,
                    'is_internal': comment.is_internal,
                    'created_at': comment.created_at.isoformat()
                },
                message="Comment added successfully"
            )
            
        except Exception as e:
            logger.error(f"Add comment error: {e}")
            return self.internal_server_error("Failed to add comment")


class EnhancedUserViewSet(BaseEnhancedViewSet):
    """
    Enhanced User ViewSet with comprehensive validation and features.
    """
    
    queryset = User.objects.all()
    serializer_class = None  # Will be set in the actual implementation
    
    def get_queryset(self):
        """
        Get users with organization filtering.
        """
        queryset = super().get_queryset()
        
        # Apply organization filtering
        if hasattr(self.request.user, 'organization'):
            queryset = queryset.filter(organization=self.request.user.organization)
        
        return queryset.select_related('organization')
    
    @action(detail=False, methods=['get'])
    def agents(self, request):
        """
        Get all agents in the organization.
        """
        try:
            agents = self.get_queryset().filter(role__in=['agent', 'manager', 'admin'])
            serializer = self.get_serializer(agents, many=True)
            
            return self.success_response(data=serializer.data)
            
        except Exception as e:
            logger.error(f"Get agents error: {e}")
            return self.internal_server_error("Failed to get agents")
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """
        Get all customers in the organization.
        """
        try:
            customers = self.get_queryset().filter(role='customer')
            serializer = self.get_serializer(customers, many=True)
            
            return self.success_response(data=serializer.data)
            
        except Exception as e:
            logger.error(f"Get customers error: {e}")
            return self.internal_server_error("Failed to get customers")


class EnhancedOrganizationViewSet(BaseEnhancedViewSet):
    """
    Enhanced Organization ViewSet with comprehensive validation and features.
    """
    
    queryset = Organization.objects.all()
    serializer_class = None  # Will be set in the actual implementation
    
    def get_queryset(self):
        """
        Get organizations with proper filtering.
        """
        queryset = super().get_queryset()
        
        # Admin users can see all organizations
        if self.request.user.role == 'admin':
            return queryset
        
        # Other users can only see their organization
        if hasattr(self.request.user, 'organization'):
            return queryset.filter(id=self.request.user.organization.id)
        
        return queryset.none()
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get all users in the organization.
        """
        try:
            organization = self.get_object()
            users = User.objects.filter(organization=organization)
            serializer = self.get_serializer(users, many=True)
            
            return self.success_response(data=serializer.data)
            
        except Exception as e:
            logger.error(f"Get organization users error: {e}")
            return self.internal_server_error("Failed to get organization users")
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get organization statistics.
        """
        try:
            organization = self.get_object()
            
            # Optimized single query for all statistics
            from django.db.models import Count, Q
            
            # Get user statistics in single query
            user_stats = User.objects.filter(organization=organization).aggregate(
                total_users=Count('id'),
                active_users=Count('id', filter=Q(is_active=True))
            )
            
            # Get ticket statistics in single query
            ticket_stats = Ticket.objects.filter(organization=organization).aggregate(
                total_tickets=Count('id'),
                open_tickets=Count('id', filter=Q(status='open')),
                resolved_tickets=Count('id', filter=Q(status='resolved'))
            )
            
            stats = {
                **user_stats,
                **ticket_stats
            }
            
            return self.success_response(data=stats)
            
        except Exception as e:
            logger.error(f"Get organization statistics error: {e}")
            return self.internal_server_error("Failed to get organization statistics")
