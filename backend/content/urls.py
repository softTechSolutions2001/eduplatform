"""
File: backend/content/urls.py
Purpose: URL routing configuration for content-related APIs

This file defines URL patterns for:
1. Testimonials 
2. Platform statistics
3. User learning statistics
4. Instructor teaching statistics
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'testimonials', views.TestimonialViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('testimonials/featured/', views.FeaturedTestimonialsView.as_view(),
         name='featured-testimonials'),
    path('statistics/platform/', views.platform_statistics,
         name='platform-statistics'),
    path('statistics/user/learning/', views.user_learning_statistics,
         name='user-learning-statistics'),
    path('statistics/instructor/', views.instructor_statistics,
         name='instructor-statistics'),
]
