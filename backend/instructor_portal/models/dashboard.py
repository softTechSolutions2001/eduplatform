#
# File Path: instructor_portal/models/dashboard.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:01:07
# Date Revised: 2025-06-26 13:01:07
# Current Date and Time (UTC): 2025-06-26 13:01:07
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 13:01:07 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# InstructorDashboard model - Dashboard configuration and preferences
# Split from original models.py maintaining exact code compatibility

import logging
from typing import Dict, List, Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from .utils import get_enrollment_model, get_review_model

logger = logging.getLogger(__name__)


class InstructorDashboard(models.Model):
    """
    Instructor dashboard configuration and preferences
    ENHANCED: Improved widget management and performance
    """

    instructor = models.OneToOneField(
        'InstructorProfile',
        on_delete=models.CASCADE,
        related_name='dashboard',
        verbose_name=_('Instructor')
    )

    # Display Preferences
    show_analytics = models.BooleanField(default=True)
    show_recent_students = models.BooleanField(default=True)
    show_performance_metrics = models.BooleanField(default=True)
    show_revenue_charts = models.BooleanField(default=True)
    show_course_progress = models.BooleanField(default=True)

    # Notification Preferences
    notify_new_enrollments = models.BooleanField(default=True)
    notify_new_reviews = models.BooleanField(default=True)
    notify_course_completions = models.BooleanField(default=True)

    # Layout Configuration
    widget_order = models.JSONField(default=list, blank=True)
    custom_colors = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Instructor Dashboard')
        verbose_name_plural = _('Instructor Dashboards')

    def __str__(self):
        return f"Dashboard - {self.instructor.display_name}"

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data with caching"""
        cache_key = f"instructor_dashboard:{self.instructor.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            data = {
                'recent_activity': self.get_recent_activity(),
                'instructor': {
                    'name': self.instructor.display_name,
                    'tier': self.instructor.get_tier_display(),
                    'status': self.instructor.get_status_display()
                },
                'widgets': self.get_enabled_widgets(),
                'notifications': {
                    'new_enrollments': self.notify_new_enrollments,
                    'new_reviews': self.notify_new_reviews,
                    'course_completions': self.notify_course_completions
                }
            }

            # Cache for 15 minutes
            cache.set(cache_key, data, timeout=900)
            return data

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'error': 'Failed to load dashboard data'}

    def get_enabled_widgets(self) -> List[Dict[str, Any]]:
        """Get enabled widgets in configured order"""
        available_widgets = [
            {'id': 'course_overview', 'name': 'Course Overview', 'enabled': True},
            {'id': 'recent_students', 'name': 'Recent Students', 'enabled': self.show_recent_students},
            {'id': 'analytics', 'name': 'Analytics', 'enabled': self.show_analytics},
            {'id': 'performance_metrics', 'name': 'Performance Metrics', 'enabled': self.show_performance_metrics},
            {'id': 'revenue_charts', 'name': 'Revenue Charts', 'enabled': self.show_revenue_charts},
            {'id': 'course_progress', 'name': 'Course Progress', 'enabled': self.show_course_progress}
        ]

        # Apply custom ordering if configured
        if self.widget_order:
            widget_lookup = {w['id']: w for w in available_widgets}
            ordered_widgets = []

            # Add widgets in custom order
            for widget_id in self.widget_order:
                if widget_id in widget_lookup and widget_lookup[widget_id]['enabled']:
                    ordered_widgets.append(widget_lookup[widget_id])

            # Add any remaining enabled widgets
            for widget in available_widgets:
                if widget['enabled'] and widget['id'] not in self.widget_order:
                    ordered_widgets.append(widget)

            return ordered_widgets
        else:
            return [w for w in available_widgets if w['enabled']]

    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent activity with optimized queries"""
        try:
            activities = []
            cutoff_date = timezone.now() - timezone.timedelta(days=7)

            # Get models
            Enrollment = get_enrollment_model()
            Review = get_review_model()

            # Recent enrollments - limit and optimize
            recent_enrollments = Enrollment.objects.filter(
                course__in=self.instructor.instructed_courses,
                created_date__gte=cutoff_date
            ).select_related('user', 'course').order_by('-created_date')[:15]

            for enrollment in recent_enrollments:
                activities.append({
                    'type': 'enrollment',
                    'message': f"{enrollment.user.get_full_name() or enrollment.user.username} enrolled in {enrollment.course.title}",
                    'date': enrollment.created_date,
                    'course_id': enrollment.course.id,
                })

            # Recent reviews - limit and optimize
            recent_reviews = Review.objects.filter(
                course__in=self.instructor.instructed_courses,
                created_date__gte=cutoff_date
            ).select_related('user', 'course').order_by('-created_date')[:15]

            for review in recent_reviews:
                activities.append({
                    'type': 'review',
                    'message': f"{review.user.get_full_name() or review.user.username} reviewed {review.course.title} ({review.rating}★)",
                    'date': review.created_date,
                    'course_id': review.course.id,
                    'rating': review.rating,
                })

            # Sort by date and return top 10
            activities.sort(key=lambda x: x['date'], reverse=True)
            return activities[:10]

        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
