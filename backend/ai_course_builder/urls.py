"""
URL patterns for AI Course Builder functionality.

This module defines URL patterns that expose the AI course builder
API endpoints to the frontend application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AICourseBuilderDraftViewSet, AICourseBuilderHealthView

# Create a router for viewsets
router = DefaultRouter()
router.register(
    r'instructor/ai-course-builder',
    AICourseBuilderDraftViewSet,
    basename='ai-course-builder'
)

# Additional URL patterns for non-viewset views
urlpatterns = [
    path('api/instructor/ai-course-builder/health/', AICourseBuilderHealthView.as_view(), name='ai-course-builder-health'),
    path('api/', include(router.urls)),
]
