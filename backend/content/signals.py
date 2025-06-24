from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from courses.models import Course, Enrollment, Lesson
from users.models import CustomUser
from .models import PlatformStatistics, UserLearningStatistics, InstructorStatistics


@receiver([post_save, post_delete], sender=Course)
@receiver([post_save, post_delete], sender=CustomUser)
def update_platform_statistics(sender, **kwargs):
    """
    Update platform statistics when courses or users are added/changed/deleted
    """
    try:
        # Don't update too frequently - this could be optimized with a cache or task queue
        stats = PlatformStatistics.get_stats()
        stats.update_stats()
    except Exception as e:
        # Just log the error but don't break the save operation
        print(f"Error updating platform statistics: {e}")


@receiver(post_save, sender=CustomUser)
def create_user_statistics(sender, instance, created, **kwargs):
    """
    Create statistics objects for new users
    """
    if created:
        if hasattr(instance, 'role') and instance.role == 'instructor':
            InstructorStatistics.objects.create(user=instance)
        else:
            UserLearningStatistics.objects.create(user=instance)


@receiver(post_save, sender=Course)
def update_instructor_statistics(sender, instance, **kwargs):
    """
    Update instructor statistics when a course is added or changed
    """
    if not hasattr(instance, 'instructor'):
        return

    try:
        instructor = instance.instructor
        stats, created = InstructorStatistics.objects.get_or_create(
            user=instructor)

        # Count courses created by this instructor
        stats.courses_created = Course.objects.filter(
            instructor=instructor).count()

        # Count total enrolled students across all instructor's courses
        stats.total_students = Enrollment.objects.filter(
            course__instructor=instructor
        ).values('user').distinct().count()

        # Calculate average course rating
        stats.average_rating = Course.objects.filter(
            instructor=instructor
        ).aggregate(Avg('rating'))['rating__avg'] or 0.0

        stats.save()
    except Exception as e:
        # Just log the error but don't break the save operation
        print(f"Error updating instructor statistics: {e}")


@receiver(post_save, sender=Enrollment)
def update_learning_statistics(sender, instance, **kwargs):
    """
    Update user learning statistics when enrollment status changes
    """
    if not hasattr(instance, 'user'):
        return

    try:
        user = instance.user
        stats, created = UserLearningStatistics.objects.get_or_create(
            user=user)

        # Count completed courses
        stats.courses_completed = Enrollment.objects.filter(
            user=user,
            status='completed'
        ).count()

        # TODO: Calculate other statistics like hours spent and average score
        # This would depend on your specific data model

        stats.save()
    except Exception as e:
        # Just log the error but don't break the save operation
        print(f"Error updating user learning statistics: {e}")
