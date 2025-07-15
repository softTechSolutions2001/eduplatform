# Miscellaneous serializers
#
# File Path: backend/courses/serializers/misc.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:20:35
# Date Revised: 2025-07-09 05:07:15
# Current Date and Time (UTC): 2025-07-09 05:07:15
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 05:07:15 UTC
# User: MohithaSanthanam2010
# Version: 3.1.0
#
# Miscellaneous Serializers for Course Management System
#
# Version 3.1.0 Changes:
# - FIXED 🔴: Set is_private default to False for lesson notes based on business requirements
# - ENHANCED: Better validation and security checks
# - ADDED: Proper business logic validation

import logging

from rest_framework import serializers

# Import only what's needed
from ..models import Lesson

logger = logging.getLogger(__name__)


class LessonNotesUploadSerializer(serializers.Serializer):
    """
    Serializer for bulk lesson notes uploads
    FIXED: Set appropriate default for is_private based on business requirements
    """

    lesson_id = serializers.IntegerField(required=True)
    notes = serializers.CharField(required=True)
    # FIXED: Default to False since business rules suggest students should be able to share notes
    is_private = serializers.BooleanField(default=False)
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    def validate_lesson_id(self, value):
        """Validate that the lesson exists and user has access"""
        try:
            lesson = Lesson.objects.select_related("module__course").get(id=value)

            # Additional security check - ensure lesson is from a published course
            if not lesson.module.course.is_published:
                raise serializers.ValidationError(
                    "Cannot add notes to lessons in unpublished courses"
                )

            return value
        except Lesson.DoesNotExist:
            raise serializers.ValidationError(f"Lesson with ID {value} not found")

    def validate_notes(self, value):
        """Validate notes content with security checks"""
        if not value or not value.strip():
            raise serializers.ValidationError("Notes content cannot be empty")

        # Basic content length validation
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Notes must be at least 5 characters long"
            )

        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError(
                "Notes content is too long (max 10,000 characters)"
            )

        # Basic XSS prevention
        dangerous_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
        ]
        content_lower = value.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                raise serializers.ValidationError(
                    "Notes contain potentially dangerous content"
                )

        return value.strip()

    def validate_tags(self, value):
        """Validate tags list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list")

        # Limit number of tags
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags allowed")

        # Validate individual tags
        cleaned_tags = []
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError("Each tag must be a string")

            tag = tag.strip().lower()
            if len(tag) < 2:
                continue  # Skip very short tags

            if len(tag) > 50:
                raise serializers.ValidationError(
                    "Tag cannot be longer than 50 characters"
                )

            # Basic tag format validation
            import re

            if not re.match(r"^[a-zA-Z0-9\s\-_]+$", tag):
                raise serializers.ValidationError(
                    f"Tag '{tag}' contains invalid characters"
                )

            if tag not in cleaned_tags:  # Avoid duplicates
                cleaned_tags.append(tag)

        return cleaned_tags


class BulkEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for bulk student enrollments with enhanced security
    """

    course_id = serializers.IntegerField(required=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        max_length=100,  # Limit bulk operations
    )
    send_notifications = serializers.BooleanField(default=True)
    enrollment_type = serializers.ChoiceField(
        choices=["regular", "premium", "trial"], default="regular", required=False
    )

    def validate_course_id(self, value):
        """Validate that the course exists and is available for enrollment"""
        from ..models import Course

        try:
            course = Course.objects.get(id=value)

            # Security check - only published courses can have bulk enrollments
            if not course.is_published:
                raise serializers.ValidationError(
                    "Cannot enroll users in unpublished courses"
                )

            # Additional business logic checks
            if course.is_draft:
                raise serializers.ValidationError(
                    "Cannot enroll users in draft courses"
                )

            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with ID {value} not found")

    def validate_user_ids(self, value):
        """Enhanced validation of user IDs with security checks"""
        if not value:
            raise serializers.ValidationError("No user IDs provided")

        # Remove duplicates while preserving order
        unique_ids = []
        seen = set()
        for user_id in value:
            if user_id not in seen:
                unique_ids.append(user_id)
                seen.add(user_id)

        # Validate user ID format
        for user_id in unique_ids:
            if not isinstance(user_id, int) or user_id <= 0:
                raise serializers.ValidationError(f"Invalid user ID: {user_id}")

        # Check if users exist (basic validation)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        existing_users = User.objects.filter(id__in=unique_ids, is_active=True)
        existing_ids = set(existing_users.values_list("id", flat=True))

        missing_ids = set(unique_ids) - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"The following user IDs were not found or are inactive: {sorted(missing_ids)}"
            )

        return unique_ids

    def validate(self, data):
        """Cross-field validation"""
        # Additional business logic validation can be added here
        course_id = data.get("course_id")
        user_ids = data.get("user_ids", [])
        enrollment_type = data.get("enrollment_type", "regular")

        # Check for existing enrollments to avoid duplicates
        if course_id and user_ids:
            from ..models import Enrollment

            existing_enrollments = Enrollment.objects.filter(
                course_id=course_id,
                user_id__in=user_ids,
                status__in=["active", "completed"],
            ).values_list("user_id", flat=True)

            if existing_enrollments:
                raise serializers.ValidationError(
                    f"Some users are already enrolled in this course: {list(existing_enrollments)}"
                )

        return data


class CourseFeedbackSerializer(serializers.Serializer):
    """
    Serializer for course feedback collection with enhanced validation
    """

    course_id = serializers.IntegerField(required=True)
    feedback_type = serializers.ChoiceField(
        choices=[
            "content",
            "technical",
            "pricing",
            "instructor",
            "platform",
            "general",
        ],
        required=True,
    )
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    comments = serializers.CharField(required=True, max_length=5000)  # Increased limit
    include_user_info = serializers.BooleanField(default=True)
    anonymous_feedback = serializers.BooleanField(default=False)

    # Additional fields for better feedback categorization
    urgency = serializers.ChoiceField(
        choices=["low", "medium", "high", "critical"], default="medium", required=False
    )
    category_tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        max_length=5,
    )

    def validate_course_id(self, value):
        """Validate that the course exists and user has access to provide feedback"""
        from ..models import Course

        try:
            course = Course.objects.get(id=value)

            # Users can only provide feedback for published courses
            if not course.is_published:
                raise serializers.ValidationError(
                    "Cannot provide feedback for unpublished courses"
                )

            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with ID {value} not found")

    def validate_comments(self, value):
        """Enhanced validation for comments with content filtering"""
        if not value or not value.strip():
            raise serializers.ValidationError("Comments cannot be empty")

        content = value.strip()

        # Minimum content length
        if len(content) < 10:
            raise serializers.ValidationError(
                "Comments must be at least 10 characters long"
            )

        # Basic profanity/spam detection (implement based on your requirements)
        spam_patterns = [
            "click here",
            "visit our website",
            "buy now",
            "100% guaranteed",
        ]
        content_lower = content.lower()

        for pattern in spam_patterns:
            if pattern in content_lower:
                raise serializers.ValidationError(
                    "Comments appear to contain spam content"
                )

        # Basic XSS prevention
        dangerous_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
        ]
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                raise serializers.ValidationError(
                    "Comments contain potentially dangerous content"
                )

        return content

    def validate_category_tags(self, value):
        """Validate feedback category tags"""
        if not isinstance(value, list):
            return []

        cleaned_tags = []
        valid_tags = [
            "video-quality",
            "audio-quality",
            "content-accuracy",
            "difficulty-level",
            "instructor-clarity",
            "course-structure",
            "assignments",
            "quizzes",
            "resources",
            "support",
            "platform-bug",
            "mobile-app",
            "desktop-app",
        ]

        for tag in value:
            if isinstance(tag, str) and tag.strip().lower() in valid_tags:
                cleaned_tag = tag.strip().lower()
                if cleaned_tag not in cleaned_tags:
                    cleaned_tags.append(cleaned_tag)

        return cleaned_tags

    def validate(self, data):
        """Cross-field validation for feedback"""
        rating = data.get("rating")
        comments = data.get("comments", "")
        feedback_type = data.get("feedback_type")

        # For low ratings, ensure detailed comments
        if rating <= 2 and len(comments.strip()) < 50:
            raise serializers.ValidationError(
                "For ratings of 2 or below, please provide detailed comments (at least 50 characters)"
            )

        # For technical feedback, suggest including more details
        if feedback_type == "technical" and len(comments.strip()) < 30:
            raise serializers.ValidationError(
                "Technical feedback should include detailed information (at least 30 characters)"
            )

        return data


class CourseCompletionCertificateRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting course completion certificates
    """

    course_id = serializers.IntegerField(required=True)
    request_reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )
    delivery_method = serializers.ChoiceField(
        choices=["email", "download", "postal"], default="email"
    )
    postal_address = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )

    def validate_course_id(self, value):
        """Validate course exists and user is eligible for certificate"""
        from ..models import Course, Enrollment

        try:
            course = Course.objects.get(id=value)

            # Check if course offers certificates
            if not course.has_certificate:
                raise serializers.ValidationError(
                    "This course does not offer completion certificates"
                )

            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with ID {value} not found")

    def validate(self, data):
        """Validate certificate request eligibility"""
        course_id = data.get("course_id")
        delivery_method = data.get("delivery_method")
        postal_address = data.get("postal_address", "").strip()

        # For postal delivery, address is required
        if delivery_method == "postal" and not postal_address:
            raise serializers.ValidationError(
                "Postal address is required for postal delivery method"
            )

        # Validate user's enrollment and completion status
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            from ..models import Enrollment

            try:
                enrollment = Enrollment.objects.get(
                    user=request.user, course_id=course_id
                )

                if enrollment.status != "completed":
                    raise serializers.ValidationError(
                        "You must complete the course before requesting a certificate"
                    )

                # Check if certificate already exists
                from ..models import Certificate

                existing_cert = Certificate.objects.filter(
                    enrollment=enrollment, is_valid=True
                ).first()

                if existing_cert:
                    raise serializers.ValidationError(
                        f"You already have a valid certificate (#{existing_cert.certificate_number})"
                    )

            except Enrollment.DoesNotExist:
                raise serializers.ValidationError(
                    "You must be enrolled in this course to request a certificate"
                )

        return data
