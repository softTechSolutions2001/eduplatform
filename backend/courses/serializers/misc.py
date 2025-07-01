# Miscellaneous serializers
#
# File Path: backend/courses/serializers/misc.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:20:35
# Date Revised: 2025-06-26 10:20:35
# Current Date and Time (UTC): 2025-06-26 10:20:35
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 10:20:35 UTC
# User: softTechSolutions2001
# Version: 3.0.0
#
# Miscellaneous Serializers for Course Management System

import logging
from rest_framework import serializers

# Import only what's needed
from ..models import Lesson

logger = logging.getLogger(__name__)


class LessonNotesUploadSerializer(serializers.Serializer):
    """
    Serializer for bulk lesson notes uploads
    """
    lesson_id = serializers.IntegerField(required=True)
    notes = serializers.CharField(required=True)
    is_private = serializers.BooleanField(default=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    def validate_lesson_id(self, value):
        """Validate that the lesson exists"""
        try:
            lesson = Lesson.objects.get(id=value)
            return value
        except Lesson.DoesNotExist:
            raise serializers.ValidationError(f"Lesson with ID {value} not found")

    def validate_notes(self, value):
        """Validate notes content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Notes content cannot be empty")
        return value.strip()


class BulkEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for bulk student enrollments
    """
    course_id = serializers.IntegerField(required=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    send_notifications = serializers.BooleanField(default=True)

    def validate_course_id(self, value):
        """Validate that the course exists"""
        from ..models import Course
        try:
            course = Course.objects.get(id=value)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with ID {value} not found")

    def validate_user_ids(self, value):
        """Basic validation of user IDs"""
        if not value:
            raise serializers.ValidationError("No user IDs provided")
        return value


class CourseFeedbackSerializer(serializers.Serializer):
    """
    Serializer for course feedback collection
    """
    course_id = serializers.IntegerField(required=True)
    feedback_type = serializers.ChoiceField(
        choices=['content', 'technical', 'pricing', 'general'],
        required=True
    )
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    comments = serializers.CharField(required=True, max_length=2000)
    include_user_info = serializers.BooleanField(default=True)

    def validate_course_id(self, value):
        """Validate that the course exists"""
        from ..models import Course
        try:
            course = Course.objects.get(id=value)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with ID {value} not found")

    def validate_comments(self, value):
        """Validate comments content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Comments cannot be empty")
        return value.strip()
