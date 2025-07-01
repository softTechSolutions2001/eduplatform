#
# File Path: instructor_portal/serializers/analytics.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-28 00:00:00
# Date Revised: 2025-06-28 00:00:00
# Current Date and Time (UTC): 2025-06-28 00:00:00
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-28 00:00:00 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Analytics serializers for instructor_portal
# Created to handle missing InstructorAnalyticsSerializer functionality

import logging
from rest_framework import serializers
from ..models import InstructorAnalytics

logger = logging.getLogger(__name__)


class InstructorAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for instructor analytics data"""

    # Read-only computed fields
    instructor_name = serializers.CharField(source='instructor.display_name', read_only=True)
    last_updated_display = serializers.SerializerMethodField()
    performance_metrics = serializers.SerializerMethodField()

    class Meta:
        model = InstructorAnalytics
        fields = [
            'id', 'instructor', 'instructor_name',
            'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue',
            'completion_rate', 'student_satisfaction_rate', 'monthly_revenue',
            'last_updated', 'last_updated_display', 'last_calculated',
            'performance_metrics'
        ]
        read_only_fields = [
            'id', 'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue',
            'completion_rate', 'student_satisfaction_rate', 'monthly_revenue',
            'last_updated', 'last_calculated'
        ]

    def get_last_updated_display(self, obj):
        """Get human-readable last updated time"""
        try:
            from django.utils import timezone
            from django.utils.timesince import timesince

            if obj.last_updated:
                return f"{timesince(obj.last_updated)} ago"
            return "Never"
        except Exception as e:
            logger.warning(f"Error formatting last updated display: {e}")
            return "Unknown"

    def get_performance_metrics(self, obj):
        """Get comprehensive performance metrics"""
        try:
            return {
                'total_students': obj.total_students,
                'total_courses': obj.total_courses,
                'average_rating': float(obj.average_rating) if obj.average_rating else 0.0,
                'total_reviews': obj.total_reviews,
                'total_revenue': float(obj.total_revenue) if obj.total_revenue else 0.0,
                'completion_rate': float(obj.completion_rate) if obj.completion_rate else 0.0,
                'student_satisfaction_rate': float(obj.student_satisfaction_rate) if obj.student_satisfaction_rate else 0.0,
                'monthly_revenue': float(obj.monthly_revenue) if obj.monthly_revenue else 0.0,
                'performance_grade': self._calculate_performance_grade(obj),
                'trends': self._get_analytics_trends(obj)
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'total_students': 0,
                'total_courses': 0,
                'average_rating': 0.0,
                'total_reviews': 0,
                'total_revenue': 0.0,
                'completion_rate': 0.0,
                'student_satisfaction_rate': 0.0,
                'monthly_revenue': 0.0,
                'performance_grade': 'N/A',
                'trends': {}
            }

    def _calculate_performance_grade(self, obj):
        """Calculate overall performance grade"""
        try:
            # Simple grading based on key metrics
            rating_score = float(obj.average_rating) if obj.average_rating else 0
            completion_score = float(obj.completion_rate) if obj.completion_rate else 0
            satisfaction_score = float(obj.student_satisfaction_rate) if obj.student_satisfaction_rate else 0

            # Weighted average: rating 40%, completion 30%, satisfaction 30%
            overall_score = (rating_score * 20) + (completion_score * 0.3) + (satisfaction_score * 0.3)

            if overall_score >= 90:
                return 'A+'
            elif overall_score >= 80:
                return 'A'
            elif overall_score >= 70:
                return 'B'
            elif overall_score >= 60:
                return 'C'
            else:
                return 'D'
        except Exception:
            return 'N/A'

    def _get_analytics_trends(self, obj):
        """Get trend indicators for analytics"""
        try:
            # This would typically compare with previous period data
            # For now, return placeholder trends
            return {
                'students_trend': 'stable',
                'revenue_trend': 'stable',
                'rating_trend': 'stable',
                'completion_trend': 'stable'
            }
        except Exception:
            return {}
