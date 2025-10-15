"""
Advanced search utilities with full-text search capabilities.
"""

from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)


class AdvancedSearchManager:
    """
    Advanced search manager with full-text search capabilities.
    """
    
    @staticmethod
    def search_tickets(query, organization_id=None, limit=50, offset=0):
        """
        Search tickets using full-text search.
        """
        from apps.tickets.models import Ticket
        
        # Create search vector for subject and description
        search_vector = SearchVector('subject', 'description', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset
        queryset = Ticket.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query
        ).order_by('-rank')
        
        # Filter by organization if provided
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def search_ticket_comments(query, organization_id=None, limit=50, offset=0):
        """
        Search ticket comments using full-text search.
        """
        from apps.tickets.models import TicketComment
        
        # Create search vector for content
        search_vector = SearchVector('content', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset with ticket organization filter
        queryset = TicketComment.objects.select_related('ticket').annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query
        ).order_by('-rank')
        
        # Filter by organization if provided
        if organization_id:
            queryset = queryset.filter(ticket__organization_id=organization_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def search_canned_responses(query, organization_id=None, limit=50, offset=0):
        """
        Search canned responses using full-text search.
        """
        from apps.tickets.models import CannedResponse
        
        # Create search vector for name, subject, and content
        search_vector = SearchVector('name', 'subject', 'content', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset
        queryset = CannedResponse.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query,
            is_active=True
        ).order_by('-rank', '-usage_count')
        
        # Filter by organization if provided
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def search_users(query, organization_id=None, limit=50, offset=0):
        """
        Search users using full-text search.
        """
        from apps.accounts.models import User
        
        # Create search vector for name and email
        search_vector = SearchVector('first_name', 'last_name', 'email', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset
        queryset = User.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query
        ).order_by('-rank')
        
        # Filter by organization if provided
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def search_organizations(query, limit=50, offset=0):
        """
        Search organizations using full-text search.
        """
        from apps.organizations.models import Organization
        
        # Create search vector for name
        search_vector = SearchVector('name', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset
        queryset = Organization.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query,
            is_active=True
        ).order_by('-rank')
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def search_ticket_attachments(query, organization_id=None, limit=50, offset=0):
        """
        Search ticket attachments using full-text search.
        """
        from apps.tickets.models import TicketAttachment
        
        # Create search vector for file name
        search_vector = SearchVector('file_name', config='english')
        search_query = SearchQuery(query, config='english')
        
        # Base queryset with ticket organization filter
        queryset = TicketAttachment.objects.select_related('ticket').annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query
        ).order_by('-rank')
        
        # Filter by organization if provided
        if organization_id:
            queryset = queryset.filter(ticket__organization_id=organization_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page = paginator.get_page(offset // limit + 1)
        
        return {
            'results': page.object_list,
            'total_count': paginator.count,
            'page_number': page.number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        }
    
    @staticmethod
    def global_search(query, organization_id=None, limit=50, offset=0):
        """
        Perform global search across all searchable models.
        """
        results = {
            'tickets': [],
            'comments': [],
            'canned_responses': [],
            'users': [],
            'organizations': [],
            'attachments': []
        }
        
        # Search tickets
        ticket_results = AdvancedSearchManager.search_tickets(
            query, organization_id, limit//6, offset
        )
        results['tickets'] = ticket_results
        
        # Search comments
        comment_results = AdvancedSearchManager.search_ticket_comments(
            query, organization_id, limit//6, offset
        )
        results['comments'] = comment_results
        
        # Search canned responses
        canned_results = AdvancedSearchManager.search_canned_responses(
            query, organization_id, limit//6, offset
        )
        results['canned_responses'] = canned_results
        
        # Search users
        user_results = AdvancedSearchManager.search_users(
            query, organization_id, limit//6, offset
        )
        results['users'] = user_results
        
        # Search organizations (only if no organization filter)
        if not organization_id:
            org_results = AdvancedSearchManager.search_organizations(
                query, limit//6, offset
            )
            results['organizations'] = org_results
        
        # Search attachments
        attachment_results = AdvancedSearchManager.search_ticket_attachments(
            query, organization_id, limit//6, offset
        )
        results['attachments'] = attachment_results
        
        return results
    
    @staticmethod
    def get_search_suggestions(query, organization_id=None, limit=10):
        """
        Get search suggestions based on query.
        """
        suggestions = []
        
        # Get ticket subjects that match
        from apps.tickets.models import Ticket
        ticket_suggestions = Ticket.objects.filter(
            subject__icontains=query
        ).values_list('subject', flat=True)[:limit//2]
        
        suggestions.extend(ticket_suggestions)
        
        # Get canned response names that match
        from apps.tickets.models import CannedResponse
        canned_suggestions = CannedResponse.objects.filter(
            name__icontains=query,
            is_active=True
        ).values_list('name', flat=True)[:limit//2]
        
        suggestions.extend(canned_suggestions)
        
        return list(set(suggestions))[:limit]
    
    @staticmethod
    def get_search_analytics(organization_id=None, days=30):
        """
        Get search analytics for the specified period.
        """
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        from apps.tickets.models import Ticket, TicketComment
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Search frequency by query terms
        # This would require a search log table in a real implementation
        # For now, we'll return basic analytics
        
        analytics = {
            'total_searches': 0,  # Would come from search log
            'popular_queries': [],  # Would come from search log
            'search_success_rate': 0,  # Would come from search log
            'most_searched_tickets': [],
            'most_searched_comments': []
        }
        
        # Get most searched tickets (by view count or similar metric)
        if organization_id:
            popular_tickets = Ticket.objects.filter(
                organization_id=organization_id,
                created_at__gte=start_date
            ).order_by('-created_at')[:10]
        else:
            popular_tickets = Ticket.objects.filter(
                created_at__gte=start_date
            ).order_by('-created_at')[:10]
        
        analytics['most_searched_tickets'] = [
            {
                'id': ticket.id,
                'subject': ticket.subject,
                'created_at': ticket.created_at,
                'status': ticket.status
            }
            for ticket in popular_tickets
        ]
        
        return analytics


class SearchOptimizer:
    """
    Search optimization utilities.
    """
    
    @staticmethod
    def optimize_search_indexes():
        """
        Optimize search indexes for better performance.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Update search index statistics
            cursor.execute("""
                UPDATE pg_stat_user_indexes 
                SET idx_scan = idx_scan + 1 
                WHERE indexname LIKE '%fulltext%';
            """)
            
            # Analyze search indexes
            cursor.execute("""
                ANALYZE tickets_ticket;
                ANALYZE tickets_ticketcomment;
                ANALYZE tickets_cannedresponse;
                ANALYZE accounts_user;
                ANALYZE organizations_organization;
            """)
            
            logger.info("Search indexes optimized")
    
    @staticmethod
    def get_search_performance_stats():
        """
        Get search performance statistics.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes 
                WHERE indexname LIKE '%fulltext%'
                ORDER BY idx_scan DESC;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def rebuild_search_indexes():
        """
        Rebuild search indexes for optimal performance.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Rebuild full-text search indexes
            cursor.execute("""
                REINDEX INDEX CONCURRENTLY idx_tickets_fulltext_subject_description;
                REINDEX INDEX CONCURRENTLY idx_ticket_comments_fulltext_content;
                REINDEX INDEX CONCURRENTLY idx_canned_responses_fulltext_name_subject_content;
                REINDEX INDEX CONCURRENTLY idx_users_fulltext_name_email;
                REINDEX INDEX CONCURRENTLY idx_organizations_fulltext_name;
            """)
            
            logger.info("Search indexes rebuilt")


# Export utilities
__all__ = [
    'AdvancedSearchManager',
    'SearchOptimizer'
]
