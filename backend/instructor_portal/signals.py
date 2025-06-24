#
# File Path: instructor_portal/signals.py
# Folder Path: instructor_portal/
# Date Created: 2025-06-01 00:00:00
# Date Revised: 2025-06-19 16:38:02
# Current Date and Time (UTC): 2025-06-19 16:38:02
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-19 16:38:02 UTC
# User: sujibeautysalon
# Version: 2.0.0
#
# Signal Handlers for Instructor Portal
#
# Version 2.0.0 Changes:
# - ENHANCED: Moved signals to dedicated module
# - FIXED: Signal handler performance issues
# - ADDED: Signals for analytics and cache invalidation
# - IMPROVED: Error handling and logging
# - OPTIMIZED: Reduced redundant database queries

import logging
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings

from courses.models import Course, Module, Lesson, Resource
from .models import (
    InstructorProfile, CourseInstructor, InstructorDashboard, InstructorAnalytics,
    CourseCreationSession, CourseTemplate, DraftCourseContent, CourseContentDraft
)

logger = logging.getLogger(__name__)
User = get_user_model()

# =====================================
# USER & INSTRUCTOR PROFILE SIGNALS
# =====================================

@receiver(post_save, sender=User)
def create_instructor_profile_signal(sender, instance, created, **kwargs):
    """
    Signal handler to create instructor profile for eligible users
    - Optimized: Only run on create, not on update
    - Fixed: Better handling of group check to reduce queries
    """
    if not created:
        return

    try:
        # Check if user should have instructor profile based on groups or permissions
        # Use efficient filtering with exists() to check without loading full groups
        should_create = (
            instance.groups.filter(name='instructors').exists() or
            instance.user_permissions.filter(codename='add_course').exists() or
            getattr(settings, 'AUTO_CREATE_INSTRUCTOR_PROFILES', False)
        )

        if should_create and not hasattr(instance, 'instructor_profile'):
            # Create profile with full_name fallback if not available
            display_name = instance.get_full_name() if hasattr(instance, 'get_full_name') else instance.username

            InstructorProfile.objects.create(
                user=instance,
                display_name=display_name,
                status=InstructorProfile.Status.PENDING
            )
            logger.info(f"Created instructor profile for user {instance.username}")

    except Exception as e:
        logger.error(f"Error creating instructor profile for user {instance.id}: {e}")


@receiver(post_save, sender=InstructorProfile)
def handle_instructor_profile_change(sender, instance, created, **kwargs):
    """
    Handle instructor profile creation and changes
    - Created: Initialize related data
    - Updated: Clear caches and update analytics
    """
    try:
        # Clear cache to ensure permissions are refreshed
        cache.delete(f"instructor_profile:{instance.user.id}")
        cache.delete(f"instructor_profile_status:{instance.user.id}")

        # Create dashboard if not exists (for existing profiles)
        if not created:
            return

        # Initialize instructor setup
        InstructorDashboard.objects.get_or_create(
            instructor=instance,
            defaults={
                'show_analytics': True,
                'show_recent_students': True,
                'show_performance_metrics': True
            }
        )

        # Create initial analytics record
        InstructorAnalytics.objects.create(
            instructor=instance,
            date=timezone.now(),
            total_students=0,
            total_courses=0,
            average_rating=0,
            total_revenue=0,
            completion_rate=0
        )

    except Exception as e:
        logger.error(f"Error handling instructor profile change: {e}")


# =====================================
# COURSE INSTRUCTOR SIGNALS
# =====================================

@receiver(post_save, sender=CourseInstructor)
def handle_instructor_course_change(sender, instance, created, **kwargs):
    """
    Handle course instructor relationship changes
    - Clear permissions cache
    - Update instructor analytics
    - Handle lead instructor changes
    """
    try:
        # Clear permission cache for this user and course
        cache.delete(f"instructor_permission:{instance.instructor.id}:{instance.course.id}")

        # If this is a new lead instructor, ensure only one lead exists
        if created or instance.is_lead:
            # Get existing leads except this one
            other_leads = CourseInstructor.objects.filter(
                course=instance.course,
                is_lead=True,
                is_active=True
            ).exclude(pk=instance.pk)

            if instance.is_lead and other_leads.exists():
                # This is a new lead, demote others
                other_leads.update(is_lead=False)
                logger.info(f"Updated lead instructor for course {instance.course.id} to {instance.instructor.id}")

        # Update instructor analytics if needed
        try:
            if hasattr(instance.instructor, 'instructor_profile'):
                instance.instructor.instructor_profile.update_analytics()
        except:
            pass

    except Exception as e:
        logger.error(f"Error handling course instructor change: {e}")


@receiver(post_delete, sender=CourseInstructor)
def handle_instructor_course_delete(sender, instance, **kwargs):
    """
    Handle course instructor relationship deletion
    - Clear permissions cache
    - Auto-assign lead if needed
    - Update instructor analytics
    """
    try:
        # Clear permission cache
        cache.delete(f"instructor_permission:{instance.instructor.id}:{instance.course.id}")

        # If this was the lead instructor, assign a new lead if possible
        if instance.is_lead:
            # Find another active instructor
            other_instructor = CourseInstructor.objects.filter(
                course=instance.course,
                is_active=True
            ).first()

            if other_instructor:
                other_instructor.is_lead = True
                other_instructor.save(update_fields=['is_lead'])
                logger.info(f"Auto-assigned new lead instructor for course {instance.course.id}: {other_instructor.instructor.id}")

        # Update instructor analytics
        try:
            if hasattr(instance.instructor, 'instructor_profile'):
                instance.instructor.instructor_profile.update_analytics()
        except:
            pass

    except Exception as e:
        logger.error(f"Error handling course instructor deletion: {e}")


# =====================================
# COURSE CREATION SESSION SIGNALS
# =====================================

@receiver(post_save, sender=CourseCreationSession)
def handle_session_status_change(sender, instance, **kwargs):
    """
    Handle course creation session status changes
    - Update instructor analytics when published
    - Handle template usage stats
    """
    try:
        # Update template usage stats if using a template
        if instance.template_used and instance.status == CourseCreationSession.Status.PUBLISHED:
            try:
                template = CourseTemplate.objects.filter(name=instance.template_used).first()
                if template:
                    template.update_success_rate()
            except Exception as e:
                logger.error(f"Error updating template stats: {e}")

        # Update instructor analytics when published
        if instance.status == CourseCreationSession.Status.PUBLISHED:
            try:
                instance.instructor.update_analytics()
            except Exception as e:
                logger.error(f"Error updating instructor analytics: {e}")

    except Exception as e:
        logger.error(f"Error handling course creation session change: {e}")


# =====================================
# COURSE CHANGE SIGNALS
# =====================================

@receiver(post_save, sender=Course)
def handle_course_update(sender, instance, created, **kwargs):
    """
    Handle course changes to update instructor analytics
    """
    try:
        # Update analytics for all instructors of this course
        instructors = CourseInstructor.objects.filter(
            course=instance,
            is_active=True
        ).select_related('instructor__instructor_profile')

        for course_instructor in instructors:
            try:
                if hasattr(course_instructor.instructor, 'instructor_profile'):
                    course_instructor.instructor.instructor_profile.update_analytics()
            except Exception as e:
                logger.error(f"Error updating analytics for instructor {course_instructor.instructor.id}: {e}")

        # Clear course cache
        from courses.utils import clear_course_caches
        clear_course_caches(instance.id)

    except Exception as e:
        logger.error(f"Error handling course update: {e}")


@receiver(post_delete, sender=Course)
def handle_course_delete(sender, instance, **kwargs):
    """
    Handle course deletion to update instructor analytics
    """
    try:
        # Get instructors before relationships are gone
        instructor_ids = list(CourseInstructor.objects.filter(
            course=instance
        ).values_list('instructor_id', flat=True))

        # Update analytics for all affected instructors
        for instructor_id in instructor_ids:
            try:
                user = User.objects.get(id=instructor_id)
                if hasattr(user, 'instructor_profile'):
                    user.instructor_profile.update_analytics()
            except Exception as e:
                logger.error(f"Error updating analytics for instructor {instructor_id}: {e}")

        # Clear course-related caches
        cache_keys = [
            f"course:{instance.id}",
            f"course_modules:{instance.id}",
            f"course_instructors:{instance.id}"
        ]
        cache.delete_many(cache_keys)

    except Exception as e:
        logger.error(f"Error handling course deletion: {e}")


# =====================================
# MODULE & LESSON SIGNALS
# =====================================

@receiver(post_save, sender=Module)
def handle_module_update(sender, instance, created, **kwargs):
    """
    Handle module changes to update course completion percentage
    and invalidate caches
    """
    try:
        # Update course completion percentage
        course = instance.course
        if course:
            # If course has completion_percentage field
            if hasattr(course, 'completion_percentage'):
                try:
                    # Recalculate completion percentage based on module completion
                    modules = Module.objects.filter(course=course)
                    if modules.exists():
                        module_count = modules.count()
                        completed_modules = sum(1 for m in modules if getattr(m, 'is_complete', False))
                        completion_pct = (completed_modules / module_count) * 100 if module_count > 0 else 0

                        # Update course completion
                        Course.objects.filter(id=course.id).update(
                            completion_percentage=completion_pct
                        )
                except Exception as e:
                    logger.error(f"Error updating course completion: {e}")

            # Clear module and course caches
            cache_keys = [
                f"course:{course.id}",
                f"course_modules:{course.id}",
                f"module:{instance.id}"
            ]
            cache.delete_many(cache_keys)

    except Exception as e:
        logger.error(f"Error handling module update: {e}")


@receiver(post_save, sender=Lesson)
def handle_lesson_update(sender, instance, created, **kwargs):
    """
    Handle lesson changes to update module statistics
    and invalidate caches
    """
    try:
        # Update module duration if needed
        module = instance.module
        if module:
            # Recalculate module duration based on lessons
            try:
                lessons = Lesson.objects.filter(module=module)
                total_duration = sum(lesson.duration_minutes or 0 for lesson in lessons)

                # Update module duration
                Module.objects.filter(id=module.id).update(
                    duration_minutes=total_duration
                )

                # Clear caches
                cache_keys = [
                    f"module:{module.id}",
                    f"module_lessons:{module.id}",
                    f"lesson:{instance.id}"
                ]
                cache.delete_many(cache_keys)

            except Exception as e:
                logger.error(f"Error updating module duration: {e}")

    except Exception as e:
        logger.error(f"Error handling lesson update: {e}")


# =====================================
# ANALYTICS SIGNALS
# =====================================

@receiver(post_save, sender=InstructorAnalytics)
def handle_analytics_update(sender, instance, created, **kwargs):
    """
    Handle instructor analytics updates to refresh dashboard data
    """
    try:
        if created:
            # Update cache for dashboard data
            cache_keys = [
                f"instructor_analytics:{instance.instructor.id}",
                f"instructor_dashboard:{instance.instructor.id}"
            ]
            cache.delete_many(cache_keys)

            # Check for tier upgrade eligibility
            if instance.instructor.tier != InstructorProfile.Tier.DIAMOND:
                instance.instructor.update_tier()

    except Exception as e:
        logger.error(f"Error handling analytics update: {e}")


# =====================================
# MAINTENANCE SIGNALS
# =====================================

@receiver(post_save, sender=CourseContentDraft)
def process_content_draft(sender, instance, created, **kwargs):
    """
    Process newly uploaded content drafts
    """
    try:
        # Only process newly created unprocessed files
        if created and instance.file_path and not instance.is_processed:
            instance.processing_status = 'processing'
            instance.save(update_fields=['processing_status'])

            try:
                # Queue for processing (would typically use celery or similar)
                from .tasks import process_content_draft_task
                if hasattr(process_content_draft_task, 'delay'):
                    # Using Celery
                    process_content_draft_task.delay(instance.id)
                else:
                    # Direct processing (fallback)
                    success = instance.process_file()
                    if not success:
                        logger.warning(f"Failed to process file for content draft {instance.id}")
            except ImportError:
                # Process directly if task import fails
                instance.process_file()

    except Exception as e:
        logger.error(f"Error handling content draft creation: {e}")
        # Update status to failed
        try:
            instance.processing_status = 'failed'
            instance.save(update_fields=['processing_status'])
        except:
            pass


@receiver(post_delete, sender=CourseContentDraft)
def cleanup_orphaned_file(sender, instance, **kwargs):
    """
    Clean up files when content draft is deleted
    """
    try:
        # Delete the physical file if it exists
        if instance.file_path:
            from django.core.files.storage import default_storage
            try:
                if default_storage.exists(instance.file_path):
                    default_storage.delete(instance.file_path)
                    logger.info(f"Deleted orphaned file: {instance.file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {instance.file_path}: {e}")

    except Exception as e:
        logger.error(f"Error cleaning up orphaned file: {e}")


# Register all signals
logger.debug("Instructor portal signals registered successfully")
