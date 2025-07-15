"""
File: backend/users/signals.py
Purpose: Django signals for automatic model management
Date Created: 2025-07-15 00:00:00 UTC
Version: 1.0.0 - Extracted from models to avoid circular imports

HANDLES:
- Automatic Profile creation on User creation
- Cache invalidation on user updates
- Subscription creation for new users
- Security logging for model changes
- Cleanup tasks for deleted users
"""

import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Profile, Subscription, UserSession

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create Profile and Subscription when a new User is created.
    FIXED: Moved from manager to avoid circular imports.
    """
    if created:
        try:
            # Create profile if it doesn't exist
            profile, profile_created = Profile.objects.get_or_create(
                user=instance,
                defaults={
                    "bio": "",
                    "receive_email_notifications": True,
                    "receive_marketing_emails": False,
                },
            )

            if profile_created:
                logger.info(f"Profile created for user {instance.id}")

            # Create subscription if it doesn't exist
            subscription, sub_created = Subscription.objects.get_or_create(
                user=instance,
                defaults={
                    "tier": "registered",
                    "status": "active",
                },
            )

            if sub_created:
                logger.info(f"Subscription created for user {instance.id}")

        except Exception as e:
            logger.error(
                f"Error creating profile/subscription for user {instance.id}: {str(e)}"
            )


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """
    Invalidate cached user permissions when user is updated.
    ADDED: Cache management for user updates.
    """
    try:
        # Clear permission cache
        permission_types = [
            "is_admin",
            "is_instructor",
            "is_student",
            "is_email_verified",
        ]
        for perm_type in permission_types:
            cache_key = f"permission:{perm_type}:{instance.id}"
            cache.delete(cache_key)

        # Clear user-specific cache
        user_cache_key = f"user:{instance.id}"
        cache.delete(user_cache_key)

        logger.debug(f"Cache cleared for user {instance.id}")

    except Exception as e:
        logger.error(f"Error clearing cache for user {instance.id}: {str(e)}")


@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    """
    Log important user field changes for security auditing.
    ADDED: Security audit trail for user modifications.
    """
    if instance.pk:  # Only for existing users
        try:
            original = User.objects.get(pk=instance.pk)

            # Track important field changes
            important_fields = [
                "is_active",
                "is_email_verified",
                "role",
                "is_staff",
                "is_superuser",
                "email",
            ]

            changes = []
            for field in important_fields:
                old_value = getattr(original, field)
                new_value = getattr(instance, field)

                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")

            if changes:
                logger.info(f"User {instance.id} changes: {', '.join(changes)}")

        except User.DoesNotExist:
            # User is being created, not updated
            pass
        except Exception as e:
            logger.error(f"Error logging changes for user {instance.id}: {str(e)}")


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up related data when a user is deleted.
    ADDED: Proper cleanup to prevent orphaned data.
    """
    try:
        # Invalidate all user sessions
        UserSession.objects.filter(user=instance).update(is_active=False)

        # Clear cache
        permission_types = [
            "is_admin",
            "is_instructor",
            "is_student",
            "is_email_verified",
        ]
        for perm_type in permission_types:
            cache_key = f"permission:{perm_type}:{instance.id}"
            cache.delete(cache_key)

        user_cache_key = f"user:{instance.id}"
        cache.delete(user_cache_key)

        logger.info(f"Cleaned up data for deleted user {instance.id}")

    except Exception as e:
        logger.error(f"Error cleaning up data for user {instance.id}: {str(e)}")


@receiver(post_save, sender=Profile)
def log_profile_changes(sender, instance, created, **kwargs):
    """
    Log profile creation and updates.
    ADDED: Audit trail for profile modifications.
    """
    try:
        if created:
            logger.info(f"Profile created for user {instance.user.id}")
        else:
            logger.debug(f"Profile updated for user {instance.user.id}")

    except Exception as e:
        logger.error(f"Error logging profile changes: {str(e)}")


@receiver(post_save, sender=Subscription)
def log_subscription_changes(sender, instance, created, **kwargs):
    """
    Log subscription changes for business intelligence.
    ADDED: Business analytics for subscription management.
    """
    try:
        if created:
            logger.info(
                f"Subscription created: user {instance.user.id}, tier {instance.tier}"
            )
        else:
            logger.info(
                f"Subscription updated: user {instance.user.id}, tier {instance.tier}, status {instance.status}"
            )

    except Exception as e:
        logger.error(f"Error logging subscription changes: {str(e)}")


@receiver(post_save, sender=UserSession)
def log_session_activity(sender, instance, created, **kwargs):
    """
    Log session creation for security monitoring.
    ADDED: Security monitoring for session management.
    """
    try:
        if created:
            logger.info(
                f"Session created for user {instance.user.id} from {instance.ip_address}"
            )
        elif not instance.is_active:
            logger.info(f"Session invalidated for user {instance.user.id}")

    except Exception as e:
        logger.error(f"Error logging session activity: {str(e)}")


# Custom signal for password changes
from django.dispatch import Signal

password_changed = Signal()


@receiver(password_changed)
def handle_password_change(sender, user, **kwargs):
    """
    Handle password change events.
    ADDED: Custom signal for password change handling.
    """
    try:
        # Invalidate all user sessions except current one
        current_session_key = kwargs.get("current_session_key")

        sessions_to_invalidate = UserSession.objects.filter(user=user, is_active=True)

        if current_session_key:
            sessions_to_invalidate = sessions_to_invalidate.exclude(
                session_key=current_session_key
            )

        invalidated_count = sessions_to_invalidate.update(is_active=False)

        logger.info(
            f"Password changed for user {user.id}, invalidated {invalidated_count} sessions"
        )

    except Exception as e:
        logger.error(f"Error handling password change for user {user.id}: {str(e)}")


# Utility function to emit password change signal
def emit_password_changed_signal(user, current_session_key=None):
    """
    Utility function to emit password changed signal.
    Use this in views when password is changed.
    """
    password_changed.send(
        sender=user.__class__, user=user, current_session_key=current_session_key
    )
