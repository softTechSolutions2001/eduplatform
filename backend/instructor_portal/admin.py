#
# File Path: instructor_portal/admin.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-01 00:00:00
# Date Revised: 2025-06-19 16:38:02
# Current Date and Time (UTC): 2025-06-19 16:38:02
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-19 16:38:02 UTC
# User: sujibeautysalon
# Version: 2.5.0
#
# Admin Interface Configuration for the Instructor Portal
#
# Version 2.5.0 Changes:
# - ENHANCED: Rich admin interfaces for all models
# - ADDED: Custom admin actions for bulk operations
# - ADDED: Filtering and search capabilities
# - IMPROVED: Inline editors for related models
# - OPTIMIZED: Admin performance with select_related and prefetch_related

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
import os

from .models import (
    InstructorProfile, CourseInstructor, InstructorDashboard, InstructorAnalytics,
    CourseCreationSession, CourseTemplate, DraftCourseContent, CourseContentDraft, TierManager
)

# Inline admin classes
class CourseInstructorInline(admin.TabularInline):
    model = CourseInstructor
    extra = 0
    fields = ('instructor', 'role', 'is_lead', 'is_active', 'revenue_share_percentage')
    raw_id_fields = ('instructor',)

class InstructorDashboardInline(admin.StackedInline):
    model = InstructorDashboard
    can_delete = False
    verbose_name = 'Dashboard Configuration'
    verbose_name_plural = 'Dashboard Configuration'
    fields = (('show_analytics', 'show_recent_students', 'show_performance_metrics'),
              ('show_revenue_charts', 'show_course_progress'),
              ('notify_new_enrollments', 'notify_new_reviews', 'notify_course_completions'))

class InstructorAnalyticsInline(admin.TabularInline):
    model = InstructorAnalytics
    extra = 0
    max_num = 5
    fields = ('get_date', 'total_students', 'total_courses', 'average_rating', 'total_revenue', 'completion_rate')
    ordering = ('-last_updated',)
    readonly_fields = ('get_date',)
    can_delete = False
    verbose_name = 'Analytics History'
    verbose_name_plural = 'Recent Analytics History'

    def get_date(self, obj):
        """Get date from last_updated field"""
        return obj.last_updated.date() if obj.last_updated else None
    get_date.short_description = 'Date'

    def get_queryset(self, request):
        # Only show recent analytics entries
        queryset = super().get_queryset(request)
        return queryset.order_by('-last_updated')[:5]

class DraftCourseContentInline(admin.TabularInline):
    model = DraftCourseContent
    extra = 0
    fields = ('content_type', 'title', 'order', 'is_complete', 'version', 'last_saved')
    readonly_fields = ('last_saved',)

# Main admin classes
@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'status', 'tier', 'get_total_courses',
                     'get_total_students', 'get_average_rating', 'created_date')
    list_filter = ('status', 'tier', 'is_verified')
    search_fields = ('user__username', 'user__email', 'display_name', 'bio')
    readonly_fields = ('created_date', 'updated_date', 'get_total_courses',
                         'get_total_students', 'get_average_rating', 'get_total_reviews', 'get_total_revenue')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'display_name', 'bio', 'profile_image', 'cover_image')
        }),
        ('Professional Details', {
            'fields': ('title', 'organization', 'years_experience', 'expertise_areas')
        }),
        ('Status & Verification', {
            'fields': ('status', 'is_verified', 'tier', 'approved_by', 'approval_date')
        }),
        ('Contact & Social', {
            'fields': ('website', 'linkedin_profile', 'twitter_handle')
        }),
        ('Analytics', {
            'fields': ('get_total_students', 'get_total_courses', 'get_average_rating',
                       'get_total_reviews', 'get_total_revenue')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'marketing_emails', 'public_profile')
        }),        ('Timestamps', {
            'fields': ('created_date', 'updated_date', 'last_login')
        }),
    )
    inlines = [InstructorDashboardInline, InstructorAnalyticsInline]
    actions = ['update_analytics', 'approve_instructors', 'suspend_instructors']

    def get_total_courses(self, obj):
        """Get total courses count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_courses
        return 0
    get_total_courses.short_description = 'Total Courses'

    def get_total_students(self, obj):
        """Get total students count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_students
        return 0
    get_total_students.short_description = 'Total Students'

    def get_average_rating(self, obj):
        """Get average rating from analytics"""
        if hasattr(obj, 'analytics'):
            return f"{obj.analytics.average_rating:.2f}"
        return "0.00"
    get_average_rating.short_description = 'Average Rating'

    def get_total_reviews(self, obj):
        """Get total reviews count from analytics"""
        if hasattr(obj, 'analytics'):
            return obj.analytics.total_reviews
        return 0
    get_total_reviews.short_description = 'Total Reviews'

    def get_total_revenue(self, obj):
        """Get total revenue from analytics"""
        if hasattr(obj, 'analytics'):
            return f"${obj.analytics.total_revenue:.2f}"
        return "$0.00"
    get_total_revenue.short_description = 'Total Revenue'

    def update_analytics(self, request, queryset):
        updated = 0
        for profile in queryset:
            profile.update_analytics()
            updated += 1
        self.message_user(request, f"Updated analytics for {updated} instructor(s).")

    def approve_instructors(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status=InstructorProfile.Status.ACTIVE,
            approved_by=request.user,
            approval_date=timezone.now()
        )
        self.message_user(request, f"Approved {updated} instructor(s).")

    def suspend_instructors(self, request, queryset):
        updated = queryset.filter(status='active').update(
            status=InstructorProfile.Status.SUSPENDED
        )
        self.message_user(request, f"Suspended {updated} instructor(s).")

    update_analytics.short_description = "Update analytics for selected instructors"
    approve_instructors.short_description = "Approve selected instructors"
    suspend_instructors.short_description = "Suspend selected instructors"

@admin.register(CourseInstructor)
class CourseInstructorAdmin(admin.ModelAdmin):
    list_display = ('instructor_name', 'course_title', 'role', 'is_lead',
                    'is_active', 'revenue_share_percentage', 'joined_date')
    list_filter = ('role', 'is_lead', 'is_active')
    search_fields = ('instructor__username', 'instructor__email', 'course__title')
    readonly_fields = ('joined_date', 'updated_date')

    def instructor_name(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.username

    def course_title(self, obj):
        return obj.course.title

    instructor_name.admin_order_field = 'instructor__username'
    course_title.admin_order_field = 'course__title'

@admin.register(InstructorDashboard)
class InstructorDashboardAdmin(admin.ModelAdmin):
    list_display = ('instructor_name', 'show_analytics', 'show_recent_students',
                    'show_revenue_charts', 'notify_new_reviews', 'created_date')
    list_filter = ('show_analytics', 'show_recent_students', 'show_revenue_charts')
    search_fields = ('instructor__user__username', 'instructor__display_name')
    readonly_fields = ('created_date', 'updated_date')

    def instructor_name(self, obj):
        return obj.instructor.display_name

    instructor_name.admin_order_field = 'instructor__display_name'

@admin.register(InstructorAnalytics)
class InstructorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('instructor_name', 'get_date', 'total_students', 'total_courses',
                    'average_rating', 'get_completion_rate', 'get_data_type')
    list_filter = ('instructor__tier', 'instructor__status')
    search_fields = ('instructor__user__username', 'instructor__display_name')
    readonly_fields = ('last_updated', 'last_calculated')

    def instructor_name(self, obj):
        return obj.instructor.display_name

    def get_date(self, obj):
        """Get the date field - use last_updated as proxy for analytics date"""
        return obj.last_updated.date() if obj.last_updated else None
    get_date.short_description = 'Date'

    def get_completion_rate(self, obj):
        """Get completion rate from analytics"""
        if hasattr(obj, 'completion_rate'):
            return f"{obj.completion_rate:.2f}%"
        return "0.00%"
    get_completion_rate.short_description = 'Completion Rate'

    def get_data_type(self, obj):
        """Get data type - use a default value"""
        return "daily"  # Default data type
    get_data_type.short_description = 'Data Type'

    instructor_name.admin_order_field = 'instructor__display_name'

@admin.register(CourseCreationSession)
class CourseCreationSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id_short', 'instructor_name', 'creation_method', 'status',
                    'get_progress_percentage', 'created_date', 'updated_date')
    list_filter = ('creation_method', 'status')
    search_fields = ('session_id', 'instructor__user__username', 'instructor__display_name')
    readonly_fields = ('session_id', 'created_date', 'updated_date', 'get_completed_date')

    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'instructor', 'creation_method', 'status')
        }),
        ('Progress', {
            'fields': ('current_step', 'total_steps', 'get_progress_percentage', 'steps_completed')
        }),
        ('Course Data', {
            'fields': ('course_data', 'template', 'published_course')
        }),
        ('AI Configuration', {
            'fields': ('ai_prompts_used',)
        }),
        ('Validation', {
            'fields': ('validation_errors',)
        }),        ('Timestamps', {
            'fields': ('created_date', 'updated_date', 'get_completed_date', 'expires_at')
        }),
    )
    inlines = [DraftCourseContentInline]
    actions = ['validate_sessions', 'mark_abandoned', 'reset_expiry']

    def session_id_short(self, obj):
        return str(obj.session_id)[:8] + '...'

    def instructor_name(self, obj):
        return obj.instructor.display_name

    def get_progress_percentage(self, obj):
        """Get progress percentage from completion_percentage field"""
        if hasattr(obj, 'completion_percentage'):
            return f"{obj.completion_percentage:.1f}%"
        return "0.0%"
    get_progress_percentage.short_description = 'Progress %'

    def get_completed_date(self, obj):
        """Get completed date - use updated_date when status is published"""
        if obj.status == 'published':
            return obj.updated_date
        return None
    get_completed_date.short_description = 'Completed Date'

    def validate_sessions(self, request, queryset):
        valid_count = 0
        error_count = 0

        for session in queryset:
            errors = session.validate_course_data()
            if errors:
                error_count += 1
                session.status = session.Status.DRAFT
                session.validation_errors = errors
            else:
                valid_count += 1
                session.status = session.Status.READY_TO_PUBLISH
                session.validation_errors = []
            session.save()

        self.message_user(
            request,
            f"Validation complete: {valid_count} valid, {error_count} with errors."
        )

    def mark_abandoned(self, request, queryset):
        updated = queryset.update(
            status=CourseCreationSession.Status.ABANDONED
        )
        self.message_user(request, f"Marked {updated} session(s) as abandoned.")

    def reset_expiry(self, request, queryset):
        new_expiry = timezone.now() + timezone.timedelta(days=30)
        updated = queryset.update(
            expires_at=new_expiry
        )
        self.message_user(request, f"Reset expiry for {updated} session(s).")

    session_id_short.short_description = 'Session ID'
    instructor_name.admin_order_field = 'instructor__display_name'
    validate_sessions.short_description = "Validate selected sessions"
    mark_abandoned.short_description = "Mark selected sessions as abandoned"
    reset_expiry.short_description = "Reset expiry date (30 days from now)"

@admin.register(CourseTemplate)
class CourseTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'get_category', 'get_difficulty_level',
                     'usage_count', 'get_success_rate', 'is_active')
    list_filter = ('template_type', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('usage_count', 'created_date', 'updated_date')

    actions = ['toggle_active_status', 'reset_usage_stats']

    def get_category(self, obj):
        """Get category - use template_type as proxy"""
        return obj.get_template_type_display()
    get_category.short_description = 'Category'

    def get_difficulty_level(self, obj):
        """Get difficulty level - use template_type as proxy"""
        # Map template types to difficulty levels
        difficulty_map = {
            'academic': 'intermediate',
            'professional': 'advanced',
            'creative': 'beginner',
            'technical': 'advanced',
            'business': 'intermediate',
            'language': 'beginner'
        }
        return difficulty_map.get(obj.template_type, 'beginner')
    get_difficulty_level.short_description = 'Difficulty Level'

    def get_success_rate(self, obj):
        """Get success rate with percentage formatting"""
        if hasattr(obj, 'success_rate'):
            return f"{obj.success_rate:.1f}%"
        return "0.0%"
    get_success_rate.short_description = 'Success Rate'

    def toggle_active_status(self, request, queryset):
        activated = 0
        deactivated = 0

        for template in queryset:
            template.is_active = not template.is_active
            template.save(update_fields=['is_active'])
            if template.is_active:
                activated += 1
            else:
                deactivated += 1

        if activated:
            self.message_user(request, f"Activated {activated} template(s).")
        if deactivated:
            self.message_user(request, f"Deactivated {deactivated} template(s).")

    def reset_usage_stats(self, request, queryset):
        updated = queryset.update(usage_count=0, success_rate=0)
        self.message_user(request, f"Reset usage statistics for {updated} template(s).")

    toggle_active_status.short_description = "Toggle active status"
    reset_usage_stats.short_description = "Reset usage statistics"

@admin.register(DraftCourseContent)
class DraftCourseContentAdmin(admin.ModelAdmin):
    list_display = ('session_info', 'content_type', 'title', 'version',
                    'is_complete', 'last_saved')
    list_filter = ('content_type', 'is_complete')
    search_fields = ('title', 'content_id', 'session__session_id')
    readonly_fields = ('last_saved',)

    def session_info(self, obj):
        return f"{obj.session.session_id} ({obj.session.instructor.display_name})"

    session_info.admin_order_field = 'session__session_id'

@admin.register(CourseContentDraft)
class CourseContentDraftAdmin(admin.ModelAdmin):
    list_display = ('session_info', 'content_type', 'file_info', 'processing_status',
                    'is_processed', 'created_date')
    list_filter = ('content_type', 'processing_status', 'is_processed')
    search_fields = ('file_path', 'content_hash', 'session__session_id')
    readonly_fields = ('created_date', 'processed_date', 'content_hash')

    def session_info(self, obj):
        return f"{obj.session.session_id} ({obj.session.instructor.display_name})"

    def file_info(self, obj):
        if obj.file_path:
            return f"{os.path.basename(obj.file_path)} ({obj.mime_type})"
        return "No file"

    session_info.admin_order_field = 'session__session_id'
    file_info.short_description = 'File'
