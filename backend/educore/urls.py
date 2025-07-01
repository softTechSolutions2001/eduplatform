"""
File: backend/educore/urls.py
Folder Path: backend/educore/
Date Created: 2025-06-01 00:00:00
Date Revised: 2025-06-26 06:49:21
Current User: softTechSolutions2001
Last Modified By: softTechSolutions2001
Last Modified: 2025-06-26 06:49:21 UTC
Version: 1.2.0

URL configuration for educore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import db_status, db_stats, test_static, test_admin_static
from instructor_portal.views import debug_courses


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # API endpoints - organized in priority order
    # Core API endpoints (courses first to ensure proper slug lookups)
    path('api/', include('courses.urls')),

    # User authentication endpoints using JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App-specific API endpoints (no version prefixes)
    path('api/user/', include('users.urls')),
    path('api/instructor/', include('instructor_portal.urls')),

    # Content API endpoints (may shadow paths in courses.urls)
    path('api/', include('content.urls')),

    # System endpoints
    path('api/system/db-status/', db_status, name='db-status'),
    path('api/system/db-stats/', db_stats, name='db-stats'),

    # Include AI course builder URLs (non-API)
    path('', include('ai_course_builder.urls')),

    # Django REST browsable API authentication
    path('api-auth/', include('rest_framework.urls')),

    # Debug and test endpoints
    path('test-static/', test_static, name='test-static'),
    path('test-admin-static/', test_admin_static, name='test-admin-static'),
    path('instructor/debug/courses/', debug_courses, name='debug-courses-direct'),
    path('instructor/debug/courses/simple/', debug_courses, {'template': 'simple'}, name='debug-courses-simple'),
    path('api/debug/courses/', debug_courses, name='api-debug-courses'),
]

# Add debug toolbar URLs
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
