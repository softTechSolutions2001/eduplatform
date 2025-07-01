# File Path: instructor_portal/models/course_link.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:01:07
# Date Revised: 2025-06-27 03:27:18
# Author: softTechSolutions2001
# Version: 1.0.1
#
# CourseInstructor model - Course collaboration and instructor relationships
# Split from original models.py maintaining exact code compatibility

import logging
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()


class CourseInstructor(models.Model):
    """
    Instructor-course relationship model with role-based permissions
    ENHANCED: Better permission management and validation
    """

    class Role(models.TextChoices):
        PRIMARY = 'primary', _('Primary Instructor')
        CO_INSTRUCTOR = 'co_instructor', _('Co-Instructor')
        ASSISTANT = 'assistant', _('Teaching Assistant')
        GUEST = 'guest', _('Guest Instructor')

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        verbose_name=_('Course')
    )

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Instructor')
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.PRIMARY,
        verbose_name=_('Role')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    is_lead = models.BooleanField(
        default=False,
        verbose_name=_('Is Lead Instructor')
    )

    # Permissions
    can_edit_content = models.BooleanField(default=True)
    can_manage_students = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=True)

    # Revenue sharing
    revenue_share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )

    # Timestamps
    joined_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course Instructor')
        verbose_name_plural = _('Course Instructors')
        unique_together = [['course', 'instructor']]
        ordering = ['course', '-is_lead', 'joined_date']
        indexes = [
            models.Index(fields=['course', 'is_active']),
            models.Index(fields=['instructor', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(revenue_share_percentage__gte=0) & Q(revenue_share_percentage__lte=100),
                name='valid_revenue_share_percentage'
            ),
        ]

    def __str__(self):
        return f"{self.instructor.get_full_name()} - {self.course.title} ({self.get_role_display()})"

    def clean(self):
        """Validate course instructor relationships"""
        super().clean()

        # Only one lead instructor per course
        if self.is_lead:
            existing_leads = CourseInstructor.objects.filter(
                course=self.course,
                is_lead=True,
                is_active=True
            ).exclude(pk=self.pk)

            if existing_leads.exists():
                raise ValidationError(_('Course can only have one lead instructor'))

    def save(self, *args, **kwargs):
        """Enhanced save with cache management"""
        is_new = self.pk is None
        # FIX: Only check permission fields if not a new record
        permission_changed = not is_new and self._permission_fields_changed()

        super().save(*args, **kwargs)

        # Clear permission caches
        cache.delete(f"instructor_permission:{self.instructor.id}:{self.course.id}")

        # Update analytics if needed
        if is_new or permission_changed:
            try:
                instructor_profile = self.instructor.instructor_profile
                # Use async update to avoid blocking the save operation
                from django.db import transaction
                transaction.on_commit(
                    lambda: instructor_profile.analytics.update_analytics()
                )
            except (AttributeError, Exception):
                pass

    def _permission_fields_changed(self) -> bool:
        """Check if permission fields have changed"""
        try:
            # FIX: Short-circuit when pk is None to avoid unnecessary db query
            if self.pk is None:
                return True

            old_obj = CourseInstructor.objects.get(pk=self.pk)
            permission_fields = ['can_edit_content', 'can_manage_students', 'can_view_analytics', 'is_active']
            return any(getattr(self, field) != getattr(old_obj, field) for field in permission_fields)
        except CourseInstructor.DoesNotExist:
            return True
