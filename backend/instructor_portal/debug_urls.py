"""
Debug URL patterns for instructor portal.
These URLs don't go through the API prefix and are for direct template rendering.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('instructor/debug/courses/', views.debug_courses, name='debug-courses-direct'),
]
