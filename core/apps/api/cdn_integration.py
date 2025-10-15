"""
CDN integration and advanced caching system for performance optimization.
"""

import json
import logging
import time
import hashlib
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, List, Any, Optional, Tuple
import requests
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CDNManager:
    """
    CDN management system for content delivery optimization.
    """
    
    def __init__(self):
        self.cdn_config = {
            'aws_cloudfront': {
                'enabled': True,
                'distribution_id': getattr(settings, 'AWS_CLOUDFRONT_DISTRIBUTION_ID', None),
                'domain': getattr(settings, 'AWS_CLOUDFRONT_DOMAIN', None),
                'region': getattr(settings, 'AWS_REGION', 'us-east-1')
            },
            'aws_s3': {
                'enabled': True,
                'bucket_name': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
                'region': getattr(settings, 'AWS_REGION', 'us-east-1')
            },
            'cache_headers': {
                'static_assets': 'max-age=31536000',  # 1 year
                'api_responses': 'max-age=300',  # 5 minutes
                'user_content': 'max-age=3600',  # 1 hour
                'dynamic_content': 'max-age=60'  # 1 minute
            }
        }
        
        self.s3_client = None
        self.cloudfront_client = None
        self._initialize_aws_clients()
    
    def _initialize_aws_clients(self):
        """Initialize AWS clients for CDN operations."""
        try:
            if self.cdn_config['aws_s3']['enabled']:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.cdn_config['aws_s3']['region'],
                    aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                    aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
                )
            
            if self.cdn_config['aws_cloudfront']['enabled']:
                self.cloudfront_client = boto3.client(
                    'cloudfront',
                    region_name=self.cdn_config['aws_cloudfront']['region'],
                    aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                    aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
                )
        except Exception as e:
            logger.error(f"AWS client initialization error: {e}")
    
    def upload_to_cdn(self, file_path: str, content: bytes, content_type: str = 'application/octet-stream') -> Dict[str, Any]:
        """
        Upload content to CDN.
        
        Args:
            file_path: Path for the file in CDN
            content: File content
            content_type: MIME type of the content
            
        Returns:
            Upload result with CDN URL
        """
        try:
            if not self.s3_client:
                return {'success': False, 'error': 'S3 client not initialized'}
            
            # Upload to S3
            s3_key = f"cdn/{file_path}"
            self.s3_client.put_object(
                Bucket=self.cdn_config['aws_s3']['bucket_name'],
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                CacheControl=self._get_cache_control(content_type)
            )
            
            # Generate CDN URL
            cdn_url = self._generate_cdn_url(s3_key)
            
            return {
                'success': True,
                'cdn_url': cdn_url,
                's3_key': s3_key,
                'content_type': content_type,
                'cache_control': self._get_cache_control(content_type)
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"CDN upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def invalidate_cdn_cache(self, paths: List[str]) -> Dict[str, Any]:
        """
        Invalidate CDN cache for specific paths.
        
        Args:
            paths: List of paths to invalidate
            
        Returns:
            Invalidation result
        """
        try:
            if not self.cloudfront_client:
                return {'success': False, 'error': 'CloudFront client not initialized'}
            
            # Create invalidation batch
            invalidation_batch = {
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': f"invalidation-{int(time.time())}"
            }
            
            # Create invalidation
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.cdn_config['aws_cloudfront']['distribution_id'],
                InvalidationBatch=invalidation_batch
            )
            
            return {
                'success': True,
                'invalidation_id': response['Invalidation']['Id'],
                'status': response['Invalidation']['Status'],
                'paths': paths
            }
            
        except ClientError as e:
            logger.error(f"CloudFront invalidation error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"CDN invalidation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_cache_control(self, content_type: str) -> str:
        """Get cache control header based on content type."""
        if content_type.startswith('image/'):
            return self.cdn_config['cache_headers']['static_assets']
        elif content_type.startswith('text/css') or content_type.startswith('application/javascript'):
            return self.cdn_config['cache_headers']['static_assets']
        elif content_type.startswith('application/json'):
            return self.cdn_config['cache_headers']['api_responses']
        else:
            return self.cdn_config['cache_headers']['dynamic_content']
    
    def _generate_cdn_url(self, s3_key: str) -> str:
        """Generate CDN URL for S3 key."""
        if self.cdn_config['aws_cloudfront']['domain']:
            return f"https://{self.cdn_config['aws_cloudfront']['domain']}/{s3_key}"
        else:
            return f"https://{self.cdn_config['aws_s3']['bucket_name']}.s3.{self.cdn_config['aws_s3']['region']}.amazonaws.com/{s3_key}"


class AdvancedCachingSystem:
    """
    Advanced caching system with intelligent cache management.
    """
    
    def __init__(self):
        self.cache_configs = {
            'tickets': {
                'ttl': 300,  # 5 minutes
                'max_size': 1000,
                'cache_strategy': 'write_through',
                'invalidation_rules': ['user_update', 'status_change']
            },
            'users': {
                'ttl': 600,  # 10 minutes
                'max_size': 500,
                'cache_strategy': 'write_around',
                'invalidation_rules': ['profile_update', 'role_change']
            },
            'organizations': {
                'ttl': 1800,  # 30 minutes
                'max_size': 100,
                'cache_strategy': 'write_behind',
                'invalidation_rules': ['settings_update', 'user_added']
            },
            'knowledge_base': {
                'ttl': 900,  # 15 minutes
                'max_size': 200,
                'cache_strategy': 'write_through',
                'invalidation_rules': ['content_update', 'category_change']
            },
            'field_service': {
                'ttl': 600,  # 10 minutes
                'max_size': 300,
                'cache_strategy': 'write_around',
                'invalidation_rules': ['status_change', 'assignment_change']
            }
        }
        
        self.cache_stats = {}
        self.cache_invalidation_queue = []
        self.cache_warming_queue = []
    
    def get_cached_data(self, cache_key: str, model_name: str, 
                       fetch_func: callable, *args, **kwargs) -> Any:
        """
        Get cached data with intelligent cache management.
        
        Args:
            cache_key: Unique cache key
            model_name: Name of the model for cache configuration
            fetch_func: Function to fetch data if not cached
            *args: Arguments for fetch function
            **kwargs: Keyword arguments for fetch function
            
        Returns:
            Cached or fetched data
        """
        try:
            # Check cache first
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                self._update_cache_stats(cache_key, 'hit')
                return cached_data
            
            # Fetch data if not cached
            data = fetch_func(*args, **kwargs)
            
            # Cache the data based on strategy
            cache_config = self.cache_configs.get(model_name, {'ttl': 300, 'max_size': 1000})
            self._cache_data(cache_key, data, cache_config)
            
            self._update_cache_stats(cache_key, 'miss')
            return data
            
        except Exception as e:
            logger.error(f"Cache error: {e}")
            # Fallback to direct fetch
            return fetch_func(*args, **kwargs)
    
    def _cache_data(self, cache_key: str, data: Any, cache_config: Dict):
        """Cache data based on strategy."""
        try:
            # Apply cache strategy
            strategy = cache_config.get('cache_strategy', 'write_through')
            
            if strategy == 'write_through':
                # Cache immediately
                cache.set(cache_key, data, cache_config['ttl'])
            elif strategy == 'write_around':
                # Cache after successful write
                cache.set(cache_key, data, cache_config['ttl'])
            elif strategy == 'write_behind':
                # Queue for background caching
                self.cache_warming_queue.append({
                    'cache_key': cache_key,
                    'data': data,
                    'ttl': cache_config['ttl']
                })
            
        except Exception as e:
            logger.error(f"Cache data error: {e}")
    
    def invalidate_cache(self, pattern: str, model_name: str = None):
        """
        Invalidate cache based on pattern.
        
        Args:
            pattern: Cache key pattern to invalidate
            model_name: Optional model name for targeted invalidation
        """
        try:
            # Add to invalidation queue
            self.cache_invalidation_queue.append({
                'pattern': pattern,
                'model_name': model_name,
                'timestamp': timezone.now().isoformat()
            })
            
            # Process invalidation
            self._process_cache_invalidation(pattern, model_name)
            
            logger.info(f"Cache invalidated for pattern: {pattern}")
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def _process_cache_invalidation(self, pattern: str, model_name: str = None):
        """Process cache invalidation."""
        try:
            # This would implement actual cache invalidation logic
            # For now, we'll use a simple approach
            cache.delete_many([pattern])
            
        except Exception as e:
            logger.error(f"Cache invalidation processing error: {e}")
    
    def warm_cache(self, model_name: str, limit: int = 100):
        """
        Warm cache with frequently accessed data.
        
        Args:
            model_name: Name of the model to warm
            limit: Maximum number of items to warm
        """
        try:
            # Get cache configuration
            cache_config = self.cache_configs.get(model_name)
            if not cache_config:
                return
            
            # This would implement actual cache warming logic
            # For now, we'll use a simple approach
            logger.info(f"Cache warming initiated for {model_name}")
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
    
    def _update_cache_stats(self, cache_key: str, hit_type: str):
        """Update cache statistics."""
        if cache_key not in self.cache_stats:
            self.cache_stats[cache_key] = {'hits': 0, 'misses': 0}
        
        if hit_type == 'hit':
            self.cache_stats[cache_key]['hits'] += 1
        else:
            self.cache_stats[cache_key]['misses'] += 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(stats['hits'] for stats in self.cache_stats.values())
        total_misses = sum(stats['misses'] for stats in self.cache_stats.values())
        total_requests = total_hits + total_misses
        
        return {
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'hit_rate': total_hits / total_requests if total_requests > 0 else 0,
            'cache_stats': self.cache_stats,
            'invalidation_queue_size': len(self.cache_invalidation_queue),
            'warming_queue_size': len(self.cache_warming_queue)
        }


class PerformanceOptimizer:
    """
    Performance optimization system.
    """
    
    def __init__(self):
        self.cdn_manager = CDNManager()
        self.caching_system = AdvancedCachingSystem()
        self.performance_metrics = {}
        self.optimization_rules = {
            'image_optimization': self._optimize_images,
            'css_optimization': self._optimize_css,
            'javascript_optimization': self._optimize_javascript,
            'api_response_optimization': self._optimize_api_responses
        }
    
    def optimize_content(self, content: bytes, content_type: str, 
                        optimization_type: str = 'auto') -> Dict[str, Any]:
        """
        Optimize content for performance.
        
        Args:
            content: Content to optimize
            content_type: MIME type of content
            optimization_type: Type of optimization to apply
            
        Returns:
            Optimization result
        """
        try:
            # Determine optimization type
            if optimization_type == 'auto':
                optimization_type = self._determine_optimization_type(content_type)
            
            # Apply optimization
            if optimization_type in self.optimization_rules:
                optimized_content = self.optimization_rules[optimization_type](content)
            else:
                optimized_content = content
            
            # Calculate optimization metrics
            original_size = len(content)
            optimized_size = len(optimized_content)
            compression_ratio = (original_size - optimized_size) / original_size if original_size > 0 else 0
            
            return {
                'success': True,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': compression_ratio,
                'optimization_type': optimization_type,
                'content': optimized_content
            }
            
        except Exception as e:
            logger.error(f"Content optimization error: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': content
            }
    
    def _determine_optimization_type(self, content_type: str) -> str:
        """Determine optimization type based on content type."""
        if content_type.startswith('image/'):
            return 'image_optimization'
        elif content_type == 'text/css':
            return 'css_optimization'
        elif content_type == 'application/javascript':
            return 'javascript_optimization'
        elif content_type == 'application/json':
            return 'api_response_optimization'
        else:
            return 'api_response_optimization'
    
    def _optimize_images(self, content: bytes) -> bytes:
        """Optimize image content."""
        # This would implement actual image optimization
        # For now, we'll return the original content
        return content
    
    def _optimize_css(self, content: bytes) -> bytes:
        """Optimize CSS content."""
        # This would implement actual CSS optimization
        # For now, we'll return the original content
        return content
    
    def _optimize_javascript(self, content: bytes) -> bytes:
        """Optimize JavaScript content."""
        # This would implement actual JavaScript optimization
        # For now, we'll return the original content
        return content
    
    def _optimize_api_responses(self, content: bytes) -> bytes:
        """Optimize API response content."""
        try:
            # Parse JSON and optimize
            data = json.loads(content.decode('utf-8'))
            
            # Remove unnecessary fields
            optimized_data = self._remove_unnecessary_fields(data)
            
            # Compress JSON
            optimized_content = json.dumps(optimized_data, separators=(',', ':')).encode('utf-8')
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"API response optimization error: {e}")
            return content
    
    def _remove_unnecessary_fields(self, data: Dict) -> Dict:
        """Remove unnecessary fields from data."""
        # This would implement actual field removal logic
        # For now, we'll return the original data
        return data


class CDNIntegrationMiddleware:
    """
    Middleware for CDN integration.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cdn_manager = CDNManager()
        self.caching_system = AdvancedCachingSystem()
        self.performance_optimizer = PerformanceOptimizer()
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Add CDN headers
        response = self._add_cdn_headers(response, request)
        
        # Optimize content if needed
        if self._should_optimize_content(request):
            response = self._optimize_response_content(response)
        
        return response
    
    def _add_cdn_headers(self, response: HttpResponse, request) -> HttpResponse:
        """Add CDN-related headers."""
        # Add cache control headers
        if hasattr(response, 'data') and isinstance(response.data, dict):
            # API response
            response['Cache-Control'] = 'max-age=300, public'
            response['CDN-Cache-Control'] = 'max-age=300'
        else:
            # Static content
            response['Cache-Control'] = 'max-age=31536000, public'
            response['CDN-Cache-Control'] = 'max-age=31536000'
        
        # Add CDN headers
        response['X-CDN-Enabled'] = 'true'
        response['X-CDN-Domain'] = self.cdn_manager.cdn_config['aws_cloudfront']['domain']
        
        return response
    
    def _should_optimize_content(self, request) -> bool:
        """Determine if content should be optimized."""
        # Optimize API responses
        if '/api/v1/' in request.path:
            return True
        
        # Optimize static content
        if request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
            return True
        
        return False
    
    def _optimize_response_content(self, response: HttpResponse) -> HttpResponse:
        """Optimize response content."""
        try:
            if hasattr(response, 'content'):
                # Get content type
                content_type = response.get('Content-Type', 'application/octet-stream')
                
                # Optimize content
                optimization_result = self.performance_optimizer.optimize_content(
                    response.content, content_type
                )
                
                if optimization_result['success']:
                    response.content = optimization_result['content']
                    response['X-Optimization-Applied'] = 'true'
                    response['X-Compression-Ratio'] = str(optimization_result['compression_ratio'])
            
            return response
            
        except Exception as e:
            logger.error(f"Response optimization error: {e}")
            return response


# Global instances
cdn_manager = CDNManager()
advanced_caching_system = AdvancedCachingSystem()
performance_optimizer = PerformanceOptimizer()
