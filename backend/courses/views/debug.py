#
# File Path: backend/courses/views/debug.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 17:16:34
# Date Revised: 2025-06-26 17:16:34
# Current Date and Time (UTC): 2025-06-26 17:16:34
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 17:16:34 UTC
# User: softTechSolutions2001
# Version: 7.0.0
#
# Debug and monitoring views for development use only

import logging
from django.conf import settings
from django.core.cache import cache
from django.urls import get_resolver
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class CacheStatsView(APIView):
    """
    Cache statistics view for debugging (development only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: {'description': 'Cache statistics'}}
    )
    def get(self, request):
        """Get cache statistics and performance metrics"""
        try:
            if not settings.DEBUG:
                return Response(
                    {'error': 'Cache stats only available in debug mode'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Basic cache information
            cache_stats = {
                'cache_backend': str(cache),
                'cache_location': getattr(cache, '_cache', {}).get('_servers', 'Unknown'),
                'default_timeout': getattr(settings, 'CACHE_TIMEOUT', 300),
                'timestamp': timezone.now().isoformat()
            }

            # Test cache functionality
            test_key = f"cache_test_{timezone.now().timestamp()}"
            test_value = {'test': True, 'timestamp': timezone.now().isoformat()}

            try:
                cache.set(test_key, test_value, 60)
                retrieved_value = cache.get(test_key)
                cache_working = retrieved_value == test_value
                cache.delete(test_key)
            except Exception as e:
                cache_working = False
                logger.warning(f"Cache test failed: {e}")

            cache_stats['cache_working'] = cache_working

            # Sample cache keys (if Redis/Memcached supports key listing)
            try:
                # This is implementation-specific and may not work with all cache backends
                sample_keys = []
                if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_stats'):
                    stats = cache._cache.get_stats()
                    cache_stats['backend_stats'] = stats
            except Exception:
                cache_stats['backend_stats'] = 'Not available for this cache backend'

            # Common cache key patterns
            cache_stats['common_cache_patterns'] = [
                'featured_content:*',
                'cert_verification:*',
                'course_analytics:*',
                'user_progress:*'
            ]

            return Response(cache_stats)

        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return Response(
                {'error': 'An error occurred while retrieving cache statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class URLPatternsView(APIView):
    """
    URL patterns overview for debugging (development only)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: {'description': 'URL patterns information'}}
    )
    def get(self, request):
        """Get overview of URL patterns and routes"""
        try:
            if not settings.DEBUG:
                return Response(
                    {'error': 'URL patterns view only available in debug mode'},
                    status=status.HTTP_403_FORBIDDEN
                )

            resolver = get_resolver(settings.ROOT_URLCONF)

            # Get URL patterns for courses app
            courses_patterns = []

            def extract_patterns(url_patterns, prefix=''):
                patterns = []
                for pattern in url_patterns:
                    if hasattr(pattern, 'url_patterns'):
                        # Include patterns (nested URLconf)
                        patterns.extend(extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern)))
                    else:
                        # Regular pattern
                        patterns.append({
                            'pattern': prefix + str(pattern.pattern),
                            'name': getattr(pattern, 'name', None),
                            'callback': str(pattern.callback) if hasattr(pattern, 'callback') else None
                        })
                return patterns

            # Extract patterns from the main resolver
            all_patterns = extract_patterns(resolver.url_patterns)

            # Filter courses-related patterns
            courses_patterns = [
                pattern for pattern in all_patterns
                if (pattern['name'] and 'course' in pattern['name'].lower()) or
                   ('courses' in pattern['pattern'])
            ]

            # Router-generated patterns
            from .. import urls as courses_urls
            router_patterns = []
            if hasattr(courses_urls, 'router'):
                for prefix, viewset, basename in courses_urls.router.registry:
                    router_patterns.append({
                        'prefix': prefix,
                        'viewset': str(viewset),
                        'basename': basename
                    })

            url_info = {
                'total_patterns': len(all_patterns),
                'courses_patterns_count': len(courses_patterns),
                'router_patterns_count': len(router_patterns),
                'courses_patterns': courses_patterns[:20],  # Limit to first 20
                'router_patterns': router_patterns,
                'debug_patterns': [
                    pattern for pattern in all_patterns
                    if pattern['name'] and 'debug' in pattern['name'].lower()
                ],
                'timestamp': timezone.now().isoformat()
            }

            return Response(url_info)

        except Exception as e:
            logger.error(f"URL patterns error: {e}")
            return Response(
                {'error': 'An error occurred while retrieving URL patterns'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
