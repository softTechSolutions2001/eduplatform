from django.db import models
from django.utils.translation import gettext_lazy as _


class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", _("Beginner")
    INTERMEDIATE = "intermediate", _("Intermediate")
    ADVANCED = "advanced", _("Advanced")
    ALL_LEVELS = "all_levels", _("All Levels")


class AccessLevel(models.TextChoices):
    GUEST = "guest", _("Guest")
    REGISTERED = "registered", _("Registered")
    PREMIUM = "premium", _("Premium")
    ENTERPRISE = "enterprise", _("Enterprise")


class CompletionStatus(models.TextChoices):
    NOT_STARTED = "not_started", _("Not Started")
    IN_PROGRESS = "in_progress", _("In Progress")
    PARTIALLY_COMPLETE = "partially_complete", _("Partially Complete")
    COMPLETE = "complete", _("Complete")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")
    SUSPENDED = "suspended", _("Suspended")


class EnrollmentStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    COMPLETED = "completed", _("Completed")
    DROPPED = "dropped", _("Dropped")
    SUSPENDED = "suspended", _("Suspended")
    UNENROLLED = "unenrolled", _("Unenrolled")
    EXPIRED = "expired", _("Expired")
    PENDING = "pending", _("Pending")
