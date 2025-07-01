#
# File Path: instructor_portal/serializers/settings.py
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
# Settings serializers for instructor_portal
# Created to handle missing InstructorSettingsSerializer functionality

import logging
from rest_framework import serializers
from ..models import InstructorProfile, InstructorDashboard

logger = logging.getLogger(__name__)


class InstructorSettingsSerializer(serializers.ModelSerializer):
    """Serializer for instructor settings and preferences"""

    # Dashboard settings (nested)
    dashboard_settings = serializers.SerializerMethodField()

    # Notification preferences
    notification_preferences = serializers.SerializerMethodField()

    # Privacy settings
    privacy_settings = serializers.SerializerMethodField()

    # Account settings
    account_settings = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = [
            'id', 'email_notifications', 'marketing_emails', 'public_profile',
            'dashboard_settings', 'notification_preferences', 'privacy_settings', 'account_settings'
        ]
        read_only_fields = ['id']

    def get_dashboard_settings(self, obj):
        """Get dashboard configuration settings"""
        try:
            dashboard = InstructorDashboard.objects.get(instructor=obj)
            return {
                'show_analytics': dashboard.show_analytics,
                'show_recent_students': dashboard.show_recent_students,
                'show_performance_metrics': dashboard.show_performance_metrics,
                'show_revenue_charts': dashboard.show_revenue_charts,
                'show_course_progress': dashboard.show_course_progress,
                'widget_order': dashboard.widget_order or [],
                'custom_colors': dashboard.custom_colors or {}
            }
        except InstructorDashboard.DoesNotExist:
            return {
                'show_analytics': True,
                'show_recent_students': True,
                'show_performance_metrics': True,
                'show_revenue_charts': True,
                'show_course_progress': True,
                'widget_order': [],
                'custom_colors': {}
            }
        except Exception as e:
            logger.error(f"Error getting dashboard settings: {e}")
            return {}

    def get_notification_preferences(self, obj):
        """Get notification preferences"""
        try:
            dashboard = InstructorDashboard.objects.get(instructor=obj)
            return {
                'email_notifications': obj.email_notifications,
                'marketing_emails': obj.marketing_emails,
                'new_enrollments': dashboard.notify_new_enrollments,
                'new_reviews': dashboard.notify_new_reviews,
                'course_completions': dashboard.notify_course_completions,
                'system_updates': True,  # Default
                'security_alerts': True,  # Default
                'payment_notifications': True,  # Default
                'digest_frequency': 'daily',  # Default
                'instant_notifications': True,  # Default
                'quiet_hours': {
                    'enabled': False,
                    'start_time': '22:00',
                    'end_time': '08:00'
                }
            }
        except InstructorDashboard.DoesNotExist:
            return {
                'email_notifications': obj.email_notifications,
                'marketing_emails': obj.marketing_emails,
                'new_enrollments': True,
                'new_reviews': True,
                'course_completions': True,
                'system_updates': True,
                'security_alerts': True,
                'payment_notifications': True,
                'digest_frequency': 'daily',
                'instant_notifications': True,
                'quiet_hours': {
                    'enabled': False,
                    'start_time': '22:00',
                    'end_time': '08:00'
                }
            }
        except Exception as e:
            logger.error(f"Error getting notification preferences: {e}")
            return {}

    def get_privacy_settings(self, obj):
        """Get privacy settings"""
        try:
            return {
                'public_profile': obj.public_profile,
                'show_email_in_profile': False,  # Default private
                'allow_contact_from_students': True,
                'show_revenue_publicly': False,  # Always private
                'show_student_count': obj.public_profile,
                'show_course_count': obj.public_profile,
                'show_ratings': obj.public_profile,
                'searchable_profile': obj.public_profile
            }
        except Exception as e:
            logger.error(f"Error getting privacy settings: {e}")
            return {}

    def get_account_settings(self, obj):
        """Get account-level settings"""
        try:
            return {
                'timezone': getattr(obj, 'timezone', 'UTC'),
                'language': getattr(obj, 'language', 'en'),
                'date_format': getattr(obj, 'date_format', 'YYYY-MM-DD'),
                'currency': getattr(obj, 'currency', 'USD'),
                'two_factor_enabled': False,  # Would come from User model
                'session_timeout': 3600,  # Default 1 hour
                'auto_logout_enabled': True
            }
        except Exception as e:
            logger.error(f"Error getting account settings: {e}")
            return {}

    def update(self, instance, validated_data):
        """Update instructor settings with proper validation"""
        try:
            # Update profile-level settings
            profile_fields = ['email_notifications', 'marketing_emails', 'public_profile']
            updated_fields = []

            for field in profile_fields:
                if field in validated_data:
                    setattr(instance, field, validated_data[field])
                    updated_fields.append(field)

            if updated_fields:
                instance.save(update_fields=updated_fields)

            # Handle dashboard settings updates if provided in context
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                self._update_dashboard_settings(instance, request.data.get('dashboard_settings', {}))
                self._update_notification_settings(instance, request.data.get('notification_preferences', {}))

            return instance

        except Exception as e:
            logger.error(f"Error updating instructor settings: {e}")
            raise serializers.ValidationError(f"Settings update failed: {str(e)}")

    def _update_dashboard_settings(self, instructor_profile, dashboard_data):
        """Update dashboard configuration"""
        try:
            if not dashboard_data:
                return

            dashboard, created = InstructorDashboard.objects.get_or_create(
                instructor=instructor_profile,
                defaults={
                    'show_analytics': True,
                    'show_recent_students': True,
                    'show_performance_metrics': True,
                    'show_revenue_charts': True,
                    'show_course_progress': True
                }
            )

            dashboard_fields = [
                'show_analytics', 'show_recent_students', 'show_performance_metrics',
                'show_revenue_charts', 'show_course_progress', 'widget_order', 'custom_colors'
            ]

            updated_fields = []
            for field in dashboard_fields:
                if field in dashboard_data:
                    setattr(dashboard, field, dashboard_data[field])
                    updated_fields.append(field)

            if updated_fields:
                dashboard.save(update_fields=updated_fields)

        except Exception as e:
            logger.error(f"Error updating dashboard settings: {e}")

    def _update_notification_settings(self, instructor_profile, notification_data):
        """Update notification preferences"""
        try:
            if not notification_data:
                return

            dashboard, created = InstructorDashboard.objects.get_or_create(
                instructor=instructor_profile,
                defaults={'notify_new_enrollments': True}
            )

            notification_fields = ['notify_new_enrollments', 'notify_new_reviews', 'notify_course_completions']
            updated_fields = []

            for field in notification_fields:
                if field in notification_data:
                    setattr(dashboard, field, notification_data[field])
                    updated_fields.append(field)

            if updated_fields:
                dashboard.save(update_fields=updated_fields)

        except Exception as e:
            logger.error(f"Error updating notification settings: {e}")

    def validate_email_notifications(self, value):
        """Validate email notifications setting"""
        if not isinstance(value, bool):
            raise serializers.ValidationError("Email notifications must be a boolean value")
        return value

    def validate_marketing_emails(self, value):
        """Validate marketing emails setting"""
        if not isinstance(value, bool):
            raise serializers.ValidationError("Marketing emails must be a boolean value")
        return value

    def validate_public_profile(self, value):
        """Validate public profile setting"""
        if not isinstance(value, bool):
            raise serializers.ValidationError("Public profile must be a boolean value")
        return value
