"""
File: backend/courses/urls.py
Folder Path: backend/courses/
Date Created: 2025-06-01 00:00:00
Date Revised: 2025-06-26 09:25:45
Current User: softTechSolutions2001
Last Modified By: softTechSolutions2001
Version: 7.3.3
"""

import logging
from django.urls import path, include, re_path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import inspect

from . import views

# =====================================
# LOGGING CONFIGURATION
# =====================================

logger = logging.getLogger(__name__)

# =====================================
# SECURITY & PERFORMANCE CONFIGURATION
# =====================================

# Consolidated rate limiting classes
class APIThrottle(UserRateThrottle):
    scope = 'api'

class SensitiveAPIThrottle(UserRateThrottle):
    scope = 'sensitive_api'

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'public': 300,      # 5 minutes for public content
    'course': 600,      # 10 minutes for course details
    'user': 60,         # 1 minute for user-specific data
    'analytics': 900,   # 15 minutes for analytics
    'health': 30,       # 30 seconds for health checks
}

# Improved secure_endpoint decorator that correctly handles both function-based and class-based views
def secure_endpoint(cache_timeout=None, require_auth=False, sensitive=False):
    """Enhanced security decorator with proper handling for both function and class-based views"""
    def decorator(view_func_or_class):
        # For class-based views, we need to apply method_decorator with the method name
        if inspect.isclass(view_func_or_class):
            # For class-based views, decorate the dispatch method
            result = view_func_or_class

            if require_auth:
                result = method_decorator(login_required, name='dispatch')(result)

            # Use appropriate throttle class
            throttle_class = SensitiveAPIThrottle if sensitive else APIThrottle

            # Apply DRF throttle classes to the dispatch method
            from rest_framework.decorators import throttle_classes
            result = method_decorator(
                throttle_classes((throttle_class, AnonRateThrottle)),
                name='dispatch'
            )(result)

            # Apply cache decorators if configured
            if cache_timeout:
                result = method_decorator(cache_page(cache_timeout), name='dispatch')(result)
                result = method_decorator(
                    vary_on_headers('Authorization', 'Accept-Language'),
                    name='dispatch'
                )(result)

            return result
        else:
            # For function-based views, decorate directly
            result = view_func_or_class

            if require_auth:
                result = login_required(result)

            # Use appropriate throttle class
            throttle_class = SensitiveAPIThrottle if sensitive else APIThrottle

            # Apply DRF throttle classes
            from rest_framework.decorators import throttle_classes
            result = throttle_classes((throttle_class, AnonRateThrottle))(result)

            # Apply cache decorators if configured
            if cache_timeout:
                result = cache_page(cache_timeout)(result)
                result = vary_on_headers('Authorization', 'Accept-Language')(result)

            return result

    return decorator

# =====================================
# ROUTER CONFIGURATION
# =====================================

router = DefaultRouter()

# Register ViewSets with logging
def register_viewset(prefix, viewset, basename=None):
    try:
        router.register(prefix, viewset, basename)
        logger.info(f"Registered ViewSet: {prefix} -> {viewset.__name__}")
    except Exception as e:
        logger.error(f"Failed to register ViewSet {prefix}: {e}")
        raise

# Register all ViewSets with backward compatibility fixes
register_viewset(r'categories', views.CategoryViewSet, basename='category')
register_viewset(r'courses', views.CourseViewSet, basename='course')
register_viewset(r'modules', views.ModuleViewSet, basename='module')  # FIXED: Use backward compatibility alias
register_viewset(r'lessons', views.LessonViewSet, basename='lesson')
register_viewset(r'enrollments', views.EnrollmentViewSet, basename='enrollment')
register_viewset(r'progress', views.ProgressViewSet, basename='progress')
register_viewset(r'reviews', views.ReviewViewSet, basename='review')
register_viewset(r'notes', views.NoteViewSet, basename='note')
register_viewset(r'certificates', views.CertificateViewSet, basename='certificate')

# =====================================
# APP CONFIGURATION
# =====================================

app_name = 'courses'

# =====================================
# STREAMLINED URL PATTERNS
# =====================================

urlpatterns = [
    # =====================================
    # CORE API ENDPOINTS
    # =====================================

    # Health check - FIXED: Apply require_http_methods directly to the view
    path(
        'health/',
        secure_endpoint(cache_timeout=CACHE_TIMEOUTS['health'])(
            require_http_methods(["GET"])(views.APIHealthCheckView.as_view())
        ),
        name='api-health-check'
    ),

    # Main API endpoints (all router-generated URLs)
    path('', include(router.urls)),

    # =====================================
    # USER & ANALYTICS ENDPOINTS
    # =====================================

    # User progress statistics - using new SecureAPIView pattern
    path(
        'user/progress/stats/',
        require_http_methods(["GET"])(views.UserProgressStatsView.as_view()),
        name='user-progress-stats'
    ),

    # Legacy alias for user progress stats (maintaining backward compatibility)
    path(
        'user/progress-stats/',
        require_http_methods(["GET"])(views.UserProgressStatsView.as_view()),
        name='user-progress-stats-legacy'
    ),

    # =====================================
    # ENHANCED FUNCTIONALITY ENDPOINTS
    # =====================================

    # Course enrollment (allow both GET and POST for backward compatibility)
    path(
        'courses/<slug:course_slug>/enrollment/',
        require_http_methods(["GET", "POST"])(
            secure_endpoint(
                require_auth=True,
                sensitive=True
            )(views.CourseEnrollmentView).as_view()
        ),
        name='course-enrollment'
    ),

    # Course progress tracking
    path(
        'courses/<slug:course_slug>/progress/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['user'],
                require_auth=True
            )(views.CourseProgressView).as_view()
        ),
        name='course-progress'
    ),

    # =====================================
    # SEARCH & DISCOVERY
    # =====================================

    # Unified search (handles all search functionality)
    path(
        'search/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['public']
            )(views.UnifiedSearchView).as_view()
        ),
        name='search'
    ),

    # Featured content - FIXED: Correct ordering of decorators
    path(
        'featured/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['public']
            )(views.FeaturedContentView).as_view()
        ),
        name='featured'
    ),

    # =====================================
    # CERTIFICATE VERIFICATION
    # =====================================

    # Certificate verification (public endpoint) - using path converter instead of regex
    path(
        'certificates/verify/<slug:certificate_number>/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['public']
            )(views.CertificateVerificationView).as_view()
        ),
        name='verify-certificate'
    ),

    # =====================================
    # INSTRUCTOR TOOLS
    # =====================================

    # Instructor dashboard
    path(
        'instructor/dashboard/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['user'],
                require_auth=True
            )(views.InstructorDashboardView).as_view()
        ),
        name='instructor-dashboard'
    ),

    # Course analytics for instructors
    path(
        'instructor/courses/<slug:course_slug>/analytics/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['analytics'],
                require_auth=True
            )(views.CourseAnalyticsView).as_view()
        ),
        name='course-analytics'
    ),

    # =====================================
    # API METADATA
    # =====================================

    # API version information
    path(
        'version/',
        require_http_methods(["GET"])(
            secure_endpoint(
                cache_timeout=CACHE_TIMEOUTS['public']
            )(views.APIVersionView).as_view()
        ),
        name='api-version'
    ),
]

# =====================================
# DEVELOPMENT ENDPOINTS
# =====================================

if settings.DEBUG:
    urlpatterns += [
        path('debug/cache-stats/', views.CacheStatsView.as_view(), name='debug-cache-stats'),
        path('debug/url-patterns/', views.URLPatternsView.as_view(), name='debug-url-patterns'),
    ]

# =====================================
# COMPREHENSIVE API DOCUMENTATION
# =====================================
"""
STREAMLINED URL PATTERNS:

CORE VIEWSET ENDPOINTS (Router-Generated):
- /categories/                              - Category management
- /courses/                                 - Course management
- /modules/                                 - Module management
- /lessons/                                 - Lesson management
- /enrollments/                             - Enrollment management
- /progress/                                - Progress tracking
- /reviews/                                 - Review management
- /notes/                                   - Note management
- /certificates/                            - Certificate management

ENHANCED FUNCTIONALITY:
- GET/POST  /courses/{slug}/enrollment/     - Course enrollment/unenrollment
- GET       /courses/{slug}/progress/       - Course progress tracking
- GET       /user/progress/stats/           - User progress statistics
- GET       /user/progress-stats/           - User progress statistics (legacy)
- GET       /search/                        - Unified search
- GET       /featured/                      - Featured content
- GET       /certificates/verify/{number}/  - Certificate verification
- GET       /instructor/dashboard/          - Instructor dashboard
- GET       /instructor/courses/{slug}/analytics/ - Course analytics

UTILITY ENDPOINTS:
- GET       /health/                        - API health check
- GET       /version/                       - API version info
"""

# Log successful initialization
logger.info(f"Backward compatible security-optimized URLs configuration loaded - v7.3.3")
logger.info(f"Total URL patterns: {len(urlpatterns)}")

# Export for testing
__all__ = ['urlpatterns', 'app_name', 'router', 'secure_endpoint', 'CACHE_TIMEOUTS']
