"""
File: backend/users/admin.py
Purpose: Configure Django admin interface for user models in EduPlatform.

This file contains:
- Admin classes for CustomUser model
- Admin classes for Profile model
- Admin classes for authentication-related models (EmailVerification, PasswordReset, LoginLog)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import (
    Profile, EmailVerification, PasswordReset,
    LoginLog, UserSession
)

User = get_user_model()


class ProfileInline(admin.StackedInline):
    """
    Inline admin for Profile model.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'role',
                    'is_active', 'is_email_verified', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser',
                   'role', 'is_email_verified')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Account status'), {
         'fields': ('is_active', 'is_email_verified', 'role')}),
        (_('Security information'), {
         'fields': ('failed_login_attempts', 'temporary_ban_until')}),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')
    inlines = (ProfileInline,)


class EmailVerificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmailVerification model.
    """
    list_display = ('user', 'created_at', 'expires_at',
                    'is_used', 'verified_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('token', 'created_at', 'verified_at')


class PasswordResetAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordReset model.
    """
    list_display = ('user', 'created_at', 'expires_at',
                    'is_used', 'ip_address')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'ip_address')
    readonly_fields = ('token', 'created_at', 'used_at', 'ip_address')


class LoginLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for LoginLog model.
    """
    list_display = ('user', 'timestamp', 'ip_address', 'successful')
    list_filter = ('successful', 'timestamp')
    search_fields = ('user__email', 'user__username',
                     'ip_address', 'user_agent')
    readonly_fields = ('user', 'timestamp', 'ip_address',
                       'user_agent', 'successful')


class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserSession model.
    """
    list_display = ('user', 'ip_address', 'device_type',
                    'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'device_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'ip_address', 'location')
    readonly_fields = ('session_key', 'created_at', 'last_activity')
    actions = ['invalidate_sessions']

    def invalidate_sessions(self, request, queryset):
        """
        Admin action to invalidate selected sessions.
        """
        queryset.update(is_active=False)
    invalidate_sessions.short_description = "Invalidate selected sessions"


# Register models to admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)
admin.site.register(LoginLog, LoginLogAdmin)
admin.site.register(UserSession, UserSessionAdmin)
