#
# File Path: instructor_portal/serializers/dashboard.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 14:07:20
# Date Revised: 2025-06-27 06:16:38
# Current Date and Time (UTC): 2025-06-27 06:16:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:16:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Dashboard and analytics serializers for instructor_portal
# Split from original serializers.py maintaining exact code compatibility

import logging
from rest_framework import serializers
from ..models import InstructorProfile, InstructorDashboard

logger = logging.getLogger(__name__)

class InstructorDashboardSerializer(serializers.ModelSerializer):
    """Serializer for instructor dashboard configuration"""
    dashboard_data = serializers.SerializerMethodField()
    available_widgets = serializers.SerializerMethodField()

    class Meta:
        model = InstructorDashboard
        fields = [
            'id', 'show_analytics', 'show_recent_students', 'show_performance_metrics',
            'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
            'notify_new_reviews', 'notify_course_completions', 'widget_order',
            'custom_colors', 'dashboard_data', 'available_widgets', 'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date']

    def get_dashboard_data(self, obj):
        """Get dashboard data with error handling"""
        try:
            # This would call the model's get_dashboard_data method
            return {
                'recent_activity': obj.get_recent_activity(),
                'instructor': {
                    'name': obj.instructor.display_name,
                    'tier': obj.instructor.get_tier_display(),
                    'status': obj.instructor.get_status_display()
                },
                # Additional dashboard data would go here
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def get_available_widgets(self, obj):
        """Get available dashboard widgets based on tier"""
        instructor_tier = obj.instructor.tier

        base_widgets = [
            {'id': 'course_overview', 'name': 'Course Overview', 'tier': 'bronze'},
            {'id': 'recent_students', 'name': 'Recent Students', 'tier': 'bronze'},
            {'id': 'basic_analytics', 'name': 'Basic Analytics', 'tier': 'bronze'},
        ]

        advanced_widgets = [
            {'id': 'revenue_charts', 'name': 'Revenue Charts', 'tier': 'silver'},
            {'id': 'performance_metrics', 'name': 'Performance Metrics', 'tier': 'silver'},
            {'id': 'student_engagement', 'name': 'Student Engagement', 'tier': 'gold'},
            {'id': 'course_analytics', 'name': 'Advanced Course Analytics', 'tier': 'gold'},
            {'id': 'revenue_forecasting', 'name': 'Revenue Forecasting', 'tier': 'platinum'},
            {'id': 'custom_reports', 'name': 'Custom Reports', 'tier': 'platinum'},
        ]

        tier_hierarchy = {
            InstructorProfile.Tier.BRONZE: 1,
            InstructorProfile.Tier.SILVER: 2,
            InstructorProfile.Tier.GOLD: 3,
            InstructorProfile.Tier.PLATINUM: 4,
            InstructorProfile.Tier.DIAMOND: 5,
        }

        widget_tier_hierarchy = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4, 'diamond': 5}
        user_tier_level = tier_hierarchy.get(instructor_tier, 1)

        return [widget for widget in base_widgets + advanced_widgets
                if user_tier_level >= widget_tier_hierarchy.get(widget['tier'], 1)]

    def validate_widget_order(self, value):
        """Validate widget order configuration"""
        # Fix: Return empty list instead of None for consistency with frontend expectations
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Widget order must be a list")
        return value

    def validate_custom_colors(self, value):
        """Validate custom color configuration"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Custom colors must be a dictionary")
        return value
