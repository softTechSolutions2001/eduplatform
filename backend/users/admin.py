"""
File: backend/users/admin.py
Purpose: Enhanced Django admin interface for user models
Date Revised: 2025-07-15 00:00:00 UTC
Version: 2.1.0 - Security and Usability Enhancements

FIXES APPLIED:
- Added security measures and audit logging
- Enhanced search and filtering capabilities
- Improved performance with optimized queries
- Added bulk actions with safety checks
- Better user experience with custom admin actions
"""

import csv
from datetime import timedelta
from typing import Any, List, Optional

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    EmailVerification,
    LoginLog,
    PasswordReset,
    Profile,
    Subscription,
    UserSession,
)

User = get_user_model()


class ProfileInline(admin.StackedInline):
    """Enhanced inline admin for Profile model."""

    model = Profile
    can_delete = False
    verbose_name_plural = "Profile Information"
    fk_name = "user"

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("profile_picture", "bio", "date_of_birth", "phone_number")},
        ),
        (
            "Address",
            {
                "fields": ("address", "city", "state", "country", "postal_code"),
                "classes": ("collapse",),
            },
        ),
        (
            "Professional",
            {
                "fields": (
                    "expertise",
                    "teaching_experience",
                    "educational_background",
                    "interests",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Social Links",
            {
                "fields": ("website", "linkedin", "twitter", "github"),
                "classes": ("collapse",),
            },
        ),
        (
            "Preferences",
            {
                "fields": ("receive_email_notifications", "receive_marketing_emails"),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")


class CustomUserAdmin(UserAdmin):
    """Enhanced admin configuration for CustomUser model."""

    list_display = (
        "email",
        "username",
        "get_full_name",
        "role",
        "is_active",
        "is_email_verified",
        "get_subscription_tier",
        "failed_login_attempts",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "role",
        "is_email_verified",
        "date_joined",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)
    list_per_page = 50

    # Enhanced fieldsets
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Account status"), {"fields": ("is_active", "is_email_verified", "role")}),
        (
            _("Security information"),
            {
                "fields": ("failed_login_attempts", "ban_expires_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": ("is_staff", "is_superuser", "groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined"), "classes": ("collapse",)},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "role"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")
    inlines = (ProfileInline,)

    # Custom admin actions
    actions = [
        "verify_email",
        "unverify_email",
        "reset_failed_attempts",
        "export_users_csv",
        "activate_users",
        "deactivate_users",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimize queryset with related data."""
        return (
            super()
            .get_queryset(request)
            .select_related("profile", "subscription")
            .annotate(
                session_count=Count("sessions", filter=Q(sessions__is_active=True))
            )
        )

    def get_subscription_tier(self, obj: User) -> str:
        """Display user's subscription tier."""
        try:
            return obj.subscription.tier.title()
        except:
            return "No Subscription"

    get_subscription_tier.short_description = "Subscription"
    get_subscription_tier.admin_order_field = "subscription__tier"

    def verify_email(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Mark selected users' emails as verified."""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can verify emails")

        updated = queryset.update(is_email_verified=True)
        self.message_user(
            request, f"Successfully verified {updated} user(s) email addresses."
        )

    verify_email.short_description = "Mark selected users' emails as verified"

    def unverify_email(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Mark selected users' emails as unverified."""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can unverify emails")

        updated = queryset.update(is_email_verified=False)
        self.message_user(
            request, f"Successfully unverified {updated} user(s) email addresses."
        )

    unverify_email.short_description = "Mark selected users' emails as unverified"

    def reset_failed_attempts(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Reset failed login attempts for selected users."""
        updated = queryset.update(failed_login_attempts=0, ban_expires_at=None)
        self.message_user(
            request, f"Reset failed login attempts for {updated} user(s)."
        )

    reset_failed_attempts.short_description = "Reset failed login attempts"

    def export_users_csv(
        self, request: HttpRequest, queryset: QuerySet
    ) -> HttpResponse:
        """Export selected users to CSV."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Email",
                "Username",
                "First Name",
                "Last Name",
                "Role",
                "Is Active",
                "Email Verified",
                "Date Joined",
            ]
        )

        for user in queryset:
            writer.writerow(
                [
                    user.id,
                    user.email,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.role,
                    user.is_active,
                    user.is_email_verified,
                    user.date_joined,
                ]
            )

        return response

    export_users_csv.short_description = "Export selected users to CSV"

    def activate_users(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Activate selected users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} user(s).")

    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Deactivate selected users."""
        # Prevent deactivating superusers
        superuser_count = queryset.filter(is_superuser=True).count()
        if superuser_count > 0:
            self.message_user(
                request,
                f"Cannot deactivate {superuser_count} superuser(s).",
                level="ERROR",
            )
            queryset = queryset.filter(is_superuser=False)

        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} user(s).")

    deactivate_users.short_description = "Deactivate selected users"


class EmailVerificationAdmin(admin.ModelAdmin):
    """Enhanced admin for EmailVerification model."""

    list_display = (
        "user",
        "created_at",
        "expires_at",
        "is_used",
        "verified_at",
        "is_expired",
    )
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("token", "created_at", "verified_at")
    date_hierarchy = "created_at"

    def is_expired(self, obj: EmailVerification) -> bool:
        """Check if verification token is expired."""
        return not obj.is_valid()

    is_expired.boolean = True
    is_expired.short_description = "Expired"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")


class PasswordResetAdmin(admin.ModelAdmin):
    """Enhanced admin for PasswordReset model."""

    list_display = (
        "user",
        "created_at",
        "expires_at",
        "is_used",
        "used_at",
        "ip_address",
        "is_expired",
    )
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = ("token", "created_at", "used_at", "ip_address")
    date_hierarchy = "created_at"

    def is_expired(self, obj: PasswordReset) -> bool:
        """Check if reset token is expired."""
        return not obj.is_valid()

    is_expired.boolean = True
    is_expired.short_description = "Expired"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")


class LoginLogAdmin(admin.ModelAdmin):
    """Enhanced admin for LoginLog model."""

    list_display = ("user", "timestamp", "ip_address", "successful", "device_info")
    list_filter = ("successful", "timestamp")
    search_fields = ("user__email", "user__username", "ip_address", "user_agent")
    readonly_fields = ("user", "timestamp", "ip_address", "user_agent", "successful")
    date_hierarchy = "timestamp"
    list_per_page = 100

    def device_info(self, obj: LoginLog) -> str:
        """Extract device info from user agent."""
        user_agent = obj.user_agent.lower()
        if "mobile" in user_agent:
            return "Mobile"
        elif "tablet" in user_agent:
            return "Tablet"
        else:
            return "Desktop"

    device_info.short_description = "Device"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent manual creation of login logs."""
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Optional[LoginLog] = None
    ) -> bool:
        """Prevent modification of login logs."""
        return False


class UserSessionAdmin(admin.ModelAdmin):
    """Enhanced admin for UserSession model."""

    list_display = (
        "user",
        "ip_address",
        "device_type",
        "login_method",
        "created_at",
        "expires_at",
        "last_activity",
        "is_active",
        "session_status",
    )
    list_filter = ("is_active", "device_type", "login_method", "created_at")
    search_fields = ("user__email", "user__username", "ip_address", "location")
    readonly_fields = ("session_key", "created_at", "last_activity")
    actions = ["invalidate_sessions", "extend_sessions"]
    date_hierarchy = "created_at"

    def session_status(self, obj: UserSession) -> str:
        """Display session status with color coding."""
        if obj.is_valid():
            return format_html('<span style="color: green;">Active</span>')
        else:
            return format_html('<span style="color: red;">Expired</span>')

    session_status.short_description = "Status"

    def invalidate_sessions(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Admin action to invalidate selected sessions."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Invalidated {updated} session(s).")

    invalidate_sessions.short_description = "Invalidate selected sessions"

    def extend_sessions(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Admin action to extend session expiration."""
        new_expiry = timezone.now() + timedelta(days=7)
        updated = queryset.filter(is_active=True).update(expires_at=new_expiry)
        self.message_user(request, f"Extended {updated} active session(s) by 7 days.")

    extend_sessions.short_description = "Extend selected active sessions"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")


class SubscriptionAdmin(admin.ModelAdmin):
    """Enhanced admin for Subscription model."""

    list_display = (
        "user",
        "tier",
        "status",
        "start_date",
        "end_date",
        "is_active_display",
        "days_remaining_display",
        "is_auto_renew",
    )
    list_filter = ("tier", "status", "is_auto_renew", "start_date")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("start_date", "last_payment_date")
    actions = ["activate_subscriptions", "cancel_subscriptions"]

    def is_active_display(self, obj: Subscription) -> bool:
        """Display active status."""
        return obj.is_active

    is_active_display.boolean = True
    is_active_display.short_description = "Active"

    def days_remaining_display(self, obj: Subscription) -> str:
        """Display days remaining."""
        days = obj.days_remaining
        if days is None:
            return "Unlimited"
        elif days > 0:
            return f"{days} days"
        else:
            return "Expired"

    days_remaining_display.short_description = "Days Remaining"

    def activate_subscriptions(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Activate selected subscriptions."""
        updated = queryset.update(status="active")
        self.message_user(request, f"Activated {updated} subscription(s).")

    activate_subscriptions.short_description = "Activate selected subscriptions"

    def cancel_subscriptions(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Cancel selected subscriptions."""
        updated = queryset.update(status="cancelled", is_auto_renew=False)
        self.message_user(request, f"Cancelled {updated} subscription(s).")

    cancel_subscriptions.short_description = "Cancel selected subscriptions"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")


# Register models with enhanced admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)
admin.site.register(LoginLog, LoginLogAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

# Customize admin site
admin.site.site_header = "EduPlatform Administration"
admin.site.site_title = "EduPlatform Admin"
admin.site.index_title = "Welcome to EduPlatform Administration"
