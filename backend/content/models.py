from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser


class Testimonial(models.Model):
    """
    Testimonials from users about the platform
    """
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    avatar = models.ImageField(
        upload_to='testimonials/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.role}"


class PlatformStatistics(models.Model):
    """
    Model for storing platform-wide statistics
    This is a singleton model (only one instance should exist)
    """
    total_courses = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    total_instructors = models.PositiveIntegerField(default=0)
    total_lessons_completed = models.PositiveIntegerField(default=0)
    total_certificates_issued = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Platform Statistics'
        verbose_name_plural = 'Platform Statistics'

    def __str__(self):
        return f"Platform Stats (Updated: {self.last_updated.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def get_stats(cls):
        """
        Get or create the singleton statistics instance
        """
        stats, created = cls.objects.get_or_create(pk=1)
        return stats

    def update_stats(self):
        """
        Update the statistics based on current data in the database
        """
        from courses.models import Course, Enrollment
        from users.models import CustomUser

        self.total_courses = Course.objects.count()
        self.total_students = CustomUser.objects.filter(role='student').count()
        self.total_instructors = CustomUser.objects.filter(
            role='instructor').count()
        # We can add more statistics calculations here as needed
        self.save()
        return self


class UserLearningStatistics(models.Model):
    """
    Model for storing learning statistics for individual users
    """
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='learning_stats')
    courses_completed = models.PositiveIntegerField(default=0)
    hours_spent = models.PositiveIntegerField(default=0)  # stored in minutes
    average_score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Learning Statistics'
        verbose_name_plural = 'User Learning Statistics'

    def __str__(self):
        return f"Learning Stats for {self.user.username}"


class InstructorStatistics(models.Model):
    """
    Model for storing teaching statistics for instructors
    """
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='instructor_stats')
    courses_created = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Instructor Statistics'
        verbose_name_plural = 'Instructor Statistics'

    def __str__(self):
        return f"Teaching Stats for {self.user.username}"
