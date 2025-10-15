"""
Enhanced pagination with page size limits and metadata.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.utils import timezone
import uuid


class EnhancedPageNumberPagination(PageNumberPagination):
    """
    Enhanced pagination with page size limits and comprehensive metadata.
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size limit
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with enhanced metadata.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'pagination': {
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        })
    
    def get_page_size(self, request):
        """
        Get page size with validation and limits.
        """
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size is not None:
                try:
                    page_size = int(page_size)
                    if page_size > 0:
                        return min(page_size, self.max_page_size)
                except (ValueError, TypeError):
                    pass
        return self.page_size
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate queryset with enhanced validation.
        """
        page_size = self.get_page_size(request)
        if page_size is None:
            return None
        
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        
        try:
            self.page = paginator.page(page_number)
        except Exception as e:
            # Handle invalid page numbers
            if page_number > paginator.num_pages:
                self.page = paginator.page(paginator.num_pages)
            elif page_number < 1:
                self.page = paginator.page(1)
            else:
                raise e
        
        if self.page.paginator.count > 0:
            self.request = request
        return list(self.page)


class StandardizedOrderingMixin:
    """
    Mixin to provide standardized ordering across all list endpoints.
    """
    
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at']  # Default ordering
    
    def get_ordering(self, request, queryset, view):
        """
        Get ordering with validation and standardization.
        """
        ordering = request.query_params.get('ordering')
        if ordering:
            # Validate ordering fields
            allowed_fields = getattr(view, 'ordering_fields', self.ordering_fields)
            ordering_fields = [field.lstrip('-') for field in ordering.split(',')]
            
            for field in ordering_fields:
                if field not in allowed_fields:
                    # Remove invalid fields
                    ordering = ','.join([
                        o for o in ordering.split(',') 
                        if o.lstrip('-') in allowed_fields
                    ])
                    break
            
            if ordering:
                return [field.strip() for field in ordering.split(',')]
        
        return getattr(view, 'ordering', self.ordering)


class PaginationMetadataMixin:
    """
    Mixin to add pagination metadata to responses.
    """
    
    def get_pagination_metadata(self, paginator, page):
        """
        Get comprehensive pagination metadata.
        """
        return {
            'pagination': {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'page_size': page.paginator.per_page,
                'total_count': paginator.count,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
                'start_index': page.start_index(),
                'end_index': page.end_index(),
                'page_range': list(paginator.page_range),
                'is_first_page': page.number == 1,
                'is_last_page': page.number == paginator.num_pages,
            }
        }


class AdvancedPaginationViewSet:
    """
    Advanced pagination for ViewSets with enhanced features.
    """
    
    pagination_class = EnhancedPageNumberPagination
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset with ordering applied.
        """
        queryset = super().get_queryset()
        
        # Apply ordering
        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering_fields = getattr(self, 'ordering_fields', [])
            valid_ordering = []
            
            for field in ordering.split(','):
                field = field.strip()
                if field.lstrip('-') in ordering_fields:
                    valid_ordering.append(field)
            
            if valid_ordering:
                queryset = queryset.order_by(*valid_ordering)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Enhanced list method with pagination metadata.
        """
        queryset = self.get_queryset()
        
        # Apply filtering
        queryset = self.filter_queryset(queryset)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Pagination configuration for different endpoint types
PAGINATION_CONFIGS = {
    'tickets': {
        'page_size': 20,
        'max_page_size': 50,
        'ordering_fields': ['created_at', 'updated_at', 'priority', 'status'],
        'default_ordering': ['-created_at']
    },
    'users': {
        'page_size': 25,
        'max_page_size': 100,
        'ordering_fields': ['created_at', 'updated_at', 'last_name', 'email'],
        'default_ordering': ['last_name', 'first_name']
    },
    'organizations': {
        'page_size': 15,
        'max_page_size': 50,
        'ordering_fields': ['created_at', 'updated_at', 'name'],
        'default_ordering': ['name']
    },
    'knowledge_base': {
        'page_size': 30,
        'max_page_size': 100,
        'ordering_fields': ['created_at', 'updated_at', 'title', 'views'],
        'default_ordering': ['-created_at']
    },
    'field_service': {
        'page_size': 20,
        'max_page_size': 50,
        'ordering_fields': ['created_at', 'updated_at', 'scheduled_date', 'priority'],
        'default_ordering': ['-scheduled_date']
    }
}


def get_pagination_config(endpoint_type):
    """
    Get pagination configuration for specific endpoint type.
    """
    return PAGINATION_CONFIGS.get(endpoint_type, {
        'page_size': 20,
        'max_page_size': 100,
        'ordering_fields': ['created_at', 'updated_at'],
        'default_ordering': ['-created_at']
    })


class ConfigurablePagination(EnhancedPageNumberPagination):
    """
    Configurable pagination based on endpoint type.
    """
    
    def __init__(self, endpoint_type=None, **kwargs):
        super().__init__(**kwargs)
        if endpoint_type:
            config = get_pagination_config(endpoint_type)
            self.page_size = config['page_size']
            self.max_page_size = config['max_page_size']
            self.ordering_fields = config['ordering_fields']
            self.default_ordering = config['default_ordering']
