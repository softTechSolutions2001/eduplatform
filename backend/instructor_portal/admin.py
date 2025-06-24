#
# File Path: instructor_portal/admin.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-20 17:17:29
# Date Revised: 2025-06-20 17:17:29
# Current Date and Time (UTC): 2025-06-20 17:17:29
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-20 17:17:29 UTC
# User: sujibeautysalon
# Version: 1.0.0 - Fixed Field References

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    InstructorProfile, CourseInstructor, InstructorDashboard,
    InstructorAnalytics, InstructorAnalyticsHistory,
    CourseCreationSession, CourseTemplate, DraftCourseContent,
    CourseContentDraft, InstructorNotification, InstructorSession
)

# =====================================
# CORRECTED ADMIN CONFIGURATIONS
# =====================================

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    """Fixed admin for InstructorProfile - no more field reference errors"""

    list_display = [
        'user', 'display_name', 'tier', 'status', 'is_verified',
        'get_total_courses', 'get_total_students', 'created_date'
    ]
    list_filter = ['tier', 'status', 'is_verified', 'created_date']
    search_fields = ['user__username', 'display_name', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user', 'created_date', 'updated_date', 'last_login']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'display_name', 'bio', 'title', 'organization')
        }),
        ('Professional Details', {
            'fields': ('expertise_areas', 'years_experience', 'website', 'linkedin_profile', 'twitter_handle')
        }),
        ('Media', {
            'fields': ('profile_image', 'cover_image')
        }),
        ('Status & Tier', {
            'fields': ('status', 'tier', 'is_verified', 'approved_by', 'approval_date')
        }),
        ('Settings', {
            'fields': ('email_notifications', 'marketing_emails', 'public_profile')
        }),
        ('System Information', {
            'fields': ('created_date', 'updated_date', 'last_login'),
            'classes': ('collapse',)
        })
    )

    # Custom methods for calculated fields
    def get_total_courses(self, obj):
        """Get total courses for this instructor"""
        try:
            return obj.analytics.total_courses if hasattr(obj, 'analytics') else 0
        except:
            return 0
    get_total_courses.short_description = 'Total Courses'
    get_total_courses.admin_order_field = 'analytics__total_courses'

    def get_total_students(self, obj):
        """Get total students for this instructor"""
        try:
            return obj.analytics.total_students if hasattr(obj, 'analytics') else 0
        except:
            return 0
    get_total_students.short_description = 'Total Students'
    get_total_students.admin_order_field = 'analytics__total_students'


@admin.register(InstructorAnalytics)
class InstructorAnalyticsAdmin(admin.ModelAdmin):
    """Fixed admin for InstructorAnalytics - correct field names"""

    list_display = [
        'instructor', 'total_students', 'total_courses', 'average_rating',
        'total_revenue', 'get_last_updated'
    ]
    list_filter = ['last_updated', 'last_calculated']
    readonly_fields = ['last_updated', 'last_calculated']
    search_fields = ['instructor__display_name', 'instructor__user__username']

    fieldsets = (
        ('Analytics Data', {
            'fields': ('instructor', 'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue')
        }),
        ('Performance Metrics', {
            'fields': ('completion_rate', 'student_satisfaction_rate', 'monthly_revenue')
        }),
        ('System Information', {
            'fields': ('last_updated', 'last_calculated'),
            'classes': ('collapse',)
        })
    )

    def get_last_updated(self, obj):
        """Format last updated time"""
        return obj.last_updated.strftime('%Y-%m-%d %H:%M:%S') if obj.last_updated else 'Never'
    get_last_updated.short_description = 'Last Updated'
    get_last_updated.admin_order_field = 'last_updated'


@admin.register(InstructorAnalyticsHistory)
class InstructorAnalyticsHistoryAdmin(admin.ModelAdmin):
    """Fixed admin for InstructorAnalyticsHistory - correct field names"""

    list_display = [
        'instructor', 'date', 'total_students', 'total_courses',
        'average_rating', 'data_type'
    ]
    list_filter = ['date', 'data_type']
    readonly_fields = ['date']
    search_fields = ['instructor__display_name']

    date_hierarchy = 'date'

    fieldsets = (
        ('Snapshot Information', {
            'fields': ('instructor', 'date', 'data_type')
        }),
        ('Metrics Snapshot', {
            'fields': ('total_students', 'total_courses', 'average_rating', 'total_revenue', 'completion_rate')
        }),
        ('Additional Data', {
            'fields': ('additional_data',),
            'classes': ('collapse',)
        })
    )


@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    """Admin for CourseInstructor relationships"""

    list_display = [
        'course', 'instructor', 'role', 'is_active', 'is_lead',
        'revenue_share_percentage', 'joined_date'
    ]
    list_filter = ['role', 'is_active', 'is_lead', 'joined_date']
    search_fields = ['course__title', 'instructor__username', 'instructor__first_name', 'instructor__last_name']

    fieldsets = (
        ('Relationship', {
            'fields': ('course', 'instructor', 'role')
        }),
        ('Status & Permissions', {
            'fields': ('is_active', 'is_lead', 'can_edit_content', 'can_manage_students', 'can_view_analytics')
        }),
        ('Financial', {
            'fields': ('revenue_share_percentage',)
        }),
        ('Timestamps', {
            'fields': ('joined_date', 'updated_date'),
            'classes': ('collapse',)
        })
    )


@admin.register(InstructorDashboard)
class InstructorDashboardAdmin(admin.ModelAdmin):
    """Admin for InstructorDashboard configuration"""

    list_display = [
        'instructor', 'show_analytics', 'show_recent_students',
        'show_performance_metrics', 'updated_date'
    ]
    list_filter = ['show_analytics', 'show_recent_students', 'show_performance_metrics']
    search_fields = ['instructor__display_name']

    fieldsets = (
        ('Display Preferences', {
            'fields': ('instructor', 'show_analytics', 'show_recent_students', 'show_performance_metrics', 'show_revenue_charts', 'show_course_progress')
        }),
        ('Notification Preferences', {
            'fields': ('notify_new_enrollments', 'notify_new_reviews', 'notify_course_completions')
        }),
        ('Layout Configuration', {
            'fields': ('widget_order', 'custom_colors'),
            'classes': ('collapse',)
        })
    )


@admin.register(CourseCreationSession)
class CourseCreationSessionAdmin(admin.ModelAdmin):
    """Admin for CourseCreationSession"""

    list_display = [
        'session_id', 'instructor', 'creation_method', 'status',
        'progress_percentage', 'current_step', 'updated_date'
    ]
    list_filter = ['creation_method', 'status', 'created_date', 'updated_date']
    readonly_fields = ['session_id', 'created_date', 'updated_date', 'completed_date']
    search_fields = ['instructor__display_name', 'session_id']

    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'instructor', 'creation_method', 'status')
        }),
        ('Progress', {
            'fields': ('current_step', 'total_steps', 'progress_percentage', 'completed_steps')
        }),
        ('Content Data', {
            'fields': ('course_data', 'auto_save_data'),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('validation_errors', 'quality_score'),
            'classes': ('collapse',)
        }),
        ('AI Features', {
            'fields': ('ai_prompt', 'ai_suggestions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date', 'completed_date', 'expires_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CourseTemplate)
class CourseTemplateAdmin(admin.ModelAdmin):
    """Admin for CourseTemplate"""

    list_display = [
        'name', 'template_type', 'category', 'difficulty_level',
        'usage_count', 'success_rate', 'is_active'
    ]
    list_filter = ['template_type', 'difficulty_level', 'is_active', 'category']
    search_fields = ['name', 'description']

    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'template_type', 'category', 'difficulty_level')
        }),
        ('Template Data', {
            'fields': ('template_data', 'estimated_duration'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'success_rate')
        }),
        ('Management', {
            'fields': ('is_active', 'created_by')
        })
    )


@admin.register(DraftCourseContent)
class DraftCourseContentAdmin(admin.ModelAdmin):
    """Admin for DraftCourseContent"""

    list_display = [
        'session', 'content_type', 'title', 'version',
        'is_complete', 'ai_generated', 'last_saved'
    ]
    list_filter = ['content_type', 'is_complete', 'ai_generated', 'last_saved']
    search_fields = ['title', 'session__session_id']

    fieldsets = (
        ('Content Information', {
            'fields': ('session', 'content_type', 'content_id', 'title', 'version', 'order')
        }),
        ('Content Data', {
            'fields': ('content_data',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_complete', 'validation_errors')
        }),
        ('AI Generation', {
            'fields': ('ai_generated', 'ai_prompt'),
            'classes': ('collapse',)
        }),
        ('Auto-save', {
            'fields': ('auto_save_version', 'last_saved'),
            'classes': ('collapse',)
        })
    )


@admin.register(CourseContentDraft)
class CourseContentDraftAdmin(admin.ModelAdmin):
    """Admin for CourseContentDraft"""

    list_display = [
        'session', 'content_type', 'original_filename', 'file_size',
        'processing_status', 'is_processed', 'created_date'
    ]
    list_filter = ['content_type', 'processing_status', 'is_processed', 'created_date']
    readonly_fields = ['content_hash', 'file_size', 'mime_type', 'created_date', 'processed_date']

    fieldsets = (
        ('Content Information', {
            'fields': ('session', 'content_type', 'version')
        }),
        ('File Information', {
            'fields': ('file_path', 'original_filename', 'file_size', 'mime_type', 'content_hash')
        }),
        ('Processing', {
            'fields': ('processing_status', 'is_processed', 'processing_error', 'processed_date')
        }),
        ('Metadata', {
            'fields': ('processing_metadata',),
            'classes': ('collapse',)
        })
    )


@admin.register(InstructorNotification)
class InstructorNotificationAdmin(admin.ModelAdmin):
    """Admin for InstructorNotification"""

    list_display = [
        'instructor', 'notification_type', 'title', 'priority',
        'is_read', 'email_sent', 'created_date'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'email_sent', 'created_date']
    search_fields = ['instructor__display_name', 'title', 'message']
    readonly_fields = ['created_date', 'read_at', 'dismissed_at', 'email_sent_at']

    fieldsets = (
        ('Notification', {
            'fields': ('instructor', 'notification_type', 'priority', 'title', 'message')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_dismissed', 'dismissed_at')
        }),
        ('Email', {
            'fields': ('email_sent', 'email_sent_at')
        }),
        ('Metadata', {
            'fields': ('metadata', 'expires_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(InstructorSession)
class InstructorSessionAdmin(admin.ModelAdmin):
    """Admin for InstructorSession"""

    list_display = [
        'instructor', 'ip_address', 'device_type', 'login_time',
        'last_activity', 'is_active', 'is_suspicious'
    ]
    list_filter = ['device_type', 'is_active', 'is_suspicious', 'login_time']
    readonly_fields = ['session_key', 'login_time', 'last_activity', 'logout_time']
    search_fields = ['instructor__display_name', 'ip_address']

    fieldsets = (
        ('Session Information', {
            'fields': ('instructor', 'session_key', 'ip_address', 'location')
        }),
        ('Device Information', {
            'fields': ('user_agent', 'device_type')
        }),
        ('Timing', {
            'fields': ('login_time', 'last_activity', 'logout_time', 'is_active')
        }),
        ('Security', {
            'fields': ('is_suspicious', 'security_notes')
        })
    )

# =====================================
# ADMIN CUSTOMIZATIONS
# =====================================

# Customize admin site header
admin.site.site_header = 'Instructor Portal Administration'
admin.site.site_title = 'Instructor Portal Admin'
admin.site.index_title = 'Welcome to Instructor Portal Administration'

# Register additional admin actions
@admin.action(description='Update analytics for selected instructors')
def update_instructor_analytics(modeladmin, request, queryset):
    """Admin action to update analytics for selected instructors"""
    updated_count = 0
    for instructor in queryset:
        try:
            if hasattr(instructor, 'analytics'):
                instructor.analytics.update_analytics(force=True)
                updated_count += 1
        except Exception as e:
            pass

    modeladmin.message_user(request, f'Updated analytics for {updated_count} instructors.')

# Add the action to InstructorProfileAdmin
InstructorProfileAdmin.actions = [update_instructor_analytics]

@admin.action(description='Mark selected notifications as read')
def mark_notifications_read(modeladmin, request, queryset):
    """Admin action to mark notifications as read"""
    updated_count = 0
    for notification in queryset:
        if notification.mark_as_read():
            updated_count += 1

    modeladmin.message_user(request, f'Marked {updated_count} notifications as read.')

# Add the action to InstructorNotificationAdmin
InstructorNotificationAdmin.actions = [mark_notifications_read]
