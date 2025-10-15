"""
Database query optimization helpers to prevent N+1 queries.

Provides utilities for efficiently fetching related objects using
select_related and prefetch_related.
"""

from django.db.models import Prefetch


def optimize_ticket_queryset(queryset):
    """
    Optimize ticket queryset with select_related and prefetch_related.
    
    Prevents N+1 queries when accessing related objects.
    
    Args:
        queryset: Ticket queryset to optimize
        
    Returns:
        Optimized queryset
        
    Example:
        >>> tickets = Ticket.objects.all()
        >>> optimized_tickets = optimize_ticket_queryset(tickets)
        >>> for ticket in optimized_tickets:
        ...     print(ticket.customer.name)  # No extra query!
    """
    return queryset.select_related(
        'customer',
        'assigned_agent',
        'organization',
        'created_by',
        'sla_policy'
    ).prefetch_related(
        'comments',
        'attachments',
        'history'
    )


def optimize_ticket_list_queryset(queryset):
    """
    Optimize ticket queryset for list views (minimal data).
    
    Only fetches fields needed for list display.
    
    Args:
        queryset: Ticket queryset to optimize
        
    Returns:
        Optimized queryset with minimal fields
    """
    return queryset.select_related(
        'customer',
        'assigned_agent',
        'organization'
    ).only(
        'id',
        'ticket_number',
        'subject',
        'status',
        'priority',
        'created_at',
        'updated_at',
        'customer__id',
        'customer__email',
        'customer__first_name',
        'customer__last_name',
        'assigned_agent__id',
        'assigned_agent__email',
        'assigned_agent__first_name',
        'assigned_agent__last_name',
        'organization__id',
        'organization__name'
    )


def optimize_ticket_detail_queryset(queryset):
    """
    Optimize ticket queryset for detail views (all related data).
    
    Args:
        queryset: Ticket queryset to optimize
        
    Returns:
        Optimized queryset with all related data
    """
    return queryset.select_related(
        'customer',
        'assigned_agent',
        'organization',
        'created_by',
        'sla_policy'
    ).prefetch_related(
        Prefetch('comments', queryset=None),  # Will use default ordering
        'attachments',
        'history',
        'tags'
    )


def optimize_user_queryset(queryset):
    """
    Optimize user queryset with related organization.
    
    Args:
        queryset: User queryset to optimize
        
    Returns:
        Optimized queryset
    """
    return queryset.select_related('organization')


def optimize_notification_queryset(queryset):
    """
    Optimize notification queryset with related objects.
    
    Args:
        queryset: Notification queryset to optimize
        
    Returns:
        Optimized queryset
    """
    return queryset.select_related(
        'user',
        'organization',
        'ticket'
    )


def get_tickets_with_stats(queryset):
    """
    Get tickets with computed statistics using efficient queries.
    
    Args:
        queryset: Ticket queryset
        
    Returns:
        Queryset with annotations
    """
    from django.db.models import Count, Avg, Q
    
    return queryset.annotate(
        comment_count=Count('comments'),
        attachment_count=Count('attachments'),
    )


def bulk_fetch_related(model_instances, *related_fields):
    """
    Bulk fetch related objects for a list of model instances.
    
    Useful when you have a list of objects fetched without select_related
    and need to avoid N+1 queries.
    
    Args:
        model_instances: List of model instances
        *related_fields: Field names to fetch
        
    Example:
        >>> tickets = list(Ticket.objects.all()[:10])
        >>> bulk_fetch_related(tickets, 'customer', 'assigned_agent')
    """
    if not model_instances:
        return
    
    model_class = model_instances[0].__class__
    ids = [obj.id for obj in model_instances]
    
    # Refetch with optimizations
    optimized = model_class.objects.filter(
        id__in=ids
    ).select_related(*related_fields)
    
    # Create lookup dict
    lookup = {obj.id: obj for obj in optimized}
    
    # Update instances
    for instance in model_instances:
        optimized_instance = lookup.get(instance.id)
        if optimized_instance:
            # Copy cached related objects
            for field in related_fields:
                if hasattr(optimized_instance, field):
                    setattr(instance, field, getattr(optimized_instance, field))


# Query optimization best practices
OPTIMIZATION_TIPS = """
Database Query Optimization Best Practices:

1. Use select_related() for ForeignKey and OneToOne relationships:
   - Reduces queries by performing SQL JOIN
   - Example: Ticket.objects.select_related('customer', 'organization')

2. Use prefetch_related() for ManyToMany and reverse ForeignKey:
   - Reduces queries by fetching in separate queries
   - Example: Ticket.objects.prefetch_related('comments', 'attachments')

3. Use only() to fetch specific fields:
   - Reduces data transferred from database
   - Example: Ticket.objects.only('id', 'subject', 'status')

4. Use defer() to exclude large fields:
   - Skip fields you don't need
   - Example: Ticket.objects.defer('description')

5. Use iterator() for large querysets:
   - Prevents loading all objects into memory
   - Example: for ticket in Ticket.objects.iterator(chunk_size=100):

6. Use values() or values_list() when you don't need model instances:
   - Much faster for simple data extraction
   - Example: Ticket.objects.values('id', 'subject')

7. Use exists() instead of count() when checking existence:
   - Example: if Ticket.objects.filter(status='open').exists():

8. Avoid queries in loops:
   - BAD: for ticket in tickets: print(ticket.customer.name)
   - GOOD: tickets = tickets.select_related('customer')

9. Use bulk operations:
   - bulk_create(), bulk_update() for multiple inserts/updates
   - Example: Ticket.objects.bulk_create([ticket1, ticket2, ticket3])

10. Monitor query performance:
    - Use django-debug-toolbar in development
    - Check slow query logs in production
"""
