"""
Models for AI Course Builder functionality.

This module defines models for storing and managing AI-generated course drafts
before they are published as regular courses.

Classes:
- AICourseBuilderDraft: Stores draft data for AI-generated courses
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AICourseBuilderDraft(models.Model):
    """
    Model for storing AI course builder draft data.

    This model stores the state of an AI-generated course draft throughout the
    creation process. It holds all data necessary for the frontend wizard and
    eventual course publication.

    Fields:
        instructor: ForeignKey to User model, the course creator
        created_at: DateTime when draft was initialized
        updated_at: DateTime when draft was last updated
        status: Current status of the draft (DRAFT/READY/PUBLISHED)
        title: Draft course title
        description: Draft course description
        course_objectives: JSON field containing learning objectives
        target_audience: JSON field containing target audience information
        difficulty_level: String representing the difficulty level
        duration_minutes: Integer for course duration in minutes
        price: Decimal representing the course price
        outline: JSON field containing the course outline (modules structure)
        content: JSON field containing full course content
        assessments: JSON field containing quiz/assessment data
    """

    # Status choices
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('READY', 'Ready for Publishing'),
        ('PUBLISHED', 'Published')
    )

    # Difficulty level choices - matching Course model
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels'),
    )

    # Basic fields
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_course_drafts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    # Course information fields
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    course_objectives = models.JSONField(default=list, blank=True, null=True)
    target_audience = models.JSONField(default=list, blank=True, null=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='all_levels',
        null=True,
        blank=True    )
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # AI-generated content
    outline = models.JSONField(default=dict, blank=True, null=True)
    content = models.JSONField(default=dict, blank=True, null=True)
    assessments = models.JSONField(default=dict, blank=True, null=True)

    # Metadata and flags
    has_outline = models.BooleanField(default=False)
    has_modules = models.BooleanField(default=False)
    has_lessons = models.BooleanField(default=False)
    has_assessments = models.BooleanField(default=False)
    generation_metadata = models.JSONField(default=dict, blank=True, null=True)

    @property
    def duration_display(self):
        """Return human-readable duration in hours and minutes format."""
        if not self.duration_minutes:
            return "N/A"
        hours, minutes = divmod(self.duration_minutes, 60)
        parts = []
        if hours:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        return " ".join(parts) if parts else "N/A"

    def __str__(self):
        return f"Draft: {self.title or 'Untitled'} ({self.id})"

    class Meta:
        verbose_name = 'AI Course Builder Draft'
        verbose_name_plural = 'AI Course Builder Drafts'
        ordering = ['-updated_at']
