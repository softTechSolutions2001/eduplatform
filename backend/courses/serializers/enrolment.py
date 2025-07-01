# Enrollment model serializers
#
# File Path: backend/courses/serializers/enrolment.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:18:15
# Date Revised: 2025-06-27 11:45:30
# Current Date and Time (UTC): 2025-06-27 11:45:30
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 11:45:30 UTC
# User: softTechSolutions2001
# Version: 3.1.0
#
# Enrollment-Related Serializers for Course Management System

import logging
from rest_framework import serializers
from django.db.models import Prefetch

from ..models import (
    Enrollment, Progress, Certificate, Lesson, Course  # Added Course to the imports
)

from .mixins import (
    ContextPropagationMixin, OptimizedQueryMixin
)
from .core import CourseSerializer, LessonSerializer

logger = logging.getLogger(__name__)


class EnrollmentSerializer(ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer):
    """
    Enhanced serializer for student course enrollments with optimization
    """
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),  # Directly specify the queryset here
        source='course',
        write_only=True
    )
    progress_summary = serializers.SerializerMethodField()

    # Remove the __init__ method that sets the queryset
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_id', 'status', 'completion_date',
            'last_accessed', 'total_time_spent', 'progress_percentage',
            'progress_summary', 'created_date', 'updated_date'
        ]
        read_only_fields = ['created_date', 'updated_date', 'last_accessed']

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize enrollment queries"""
        return queryset.select_related('course__category').prefetch_related(
            'course__courseinstructor_set__instructor',
            'progress'
        )

    def get_progress_summary(self, obj):
        """Get enrollment progress summary with optimization"""
        try:
            total_lessons = Lesson.objects.filter(module__course=obj.course).count()

            # Use prefetched progress if available
            if hasattr(obj, '_prefetched_objects_cache') and 'progress' in obj._prefetched_objects_cache:
                completed_lessons = sum(1 for p in obj._prefetched_objects_cache['progress'] if p.is_completed)
            else:
                completed_lessons = Progress.objects.filter(
                    enrollment=obj,
                    is_completed=True
                ).count()

            return {
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            }
        except Exception as e:
            logger.warning(f"Error getting progress summary for enrollment {obj.id}: {e}")
            return {'total_lessons': 0, 'completed_lessons': 0, 'percentage': 0}

    def get_course(self, obj):
        """Get course with proper context propagation"""
        try:
            context = self.get_serializer_context_for_nested()
            return CourseSerializer(obj.course, context=context).data
        except Exception as e:
            logger.warning(f"Error getting course for enrollment {obj.id}: {e}")
            return None


class ProgressSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for student lesson progress"""
    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),  # Fix: Provide a queryset directly here instead of None
        source='lesson',
        write_only=True
    )

    class Meta:
        model = Progress
        fields = [
            'id', 'lesson', 'lesson_id', 'is_completed', 'completed_date',
            'time_spent', 'progress_percentage', 'notes', 'last_accessed',
            'created_date', 'updated_date'
        ]
        read_only_fields = ['completed_date', 'last_accessed', 'created_date', 'updated_date']

    # Remove the __init__ method that sets the queryset since we're setting it directly in the field definition

    def get_lesson(self, obj):
        """Get lesson with proper context propagation"""
        try:
            context = self.get_serializer_context_for_nested()
            return LessonSerializer(obj.lesson, context=context).data
        except Exception as e:
            logger.warning(f"Error getting lesson for progress {obj.id}: {e}")
            return None


class CertificateSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for course completion certificates"""
    enrollment = EnrollmentSerializer(read_only=True)
    course = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id', 'enrollment', 'certificate_number', 'course', 'user',
            'verification_url', 'is_valid', 'verification_hash',
            'template_version', 'revocation_date', 'revocation_reason',
            'created_date', 'updated_date'
        ]
        read_only_fields = [
            'certificate_number', 'verification_hash', 'created_date', 'updated_date'
        ]

    def get_course(self, obj):
        """Get course information for certificate safely"""
        try:
            course = obj.enrollment.course
            from ..utils import format_duration
            return {
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'level': course.level,
                'duration_display': (course.duration_display
                                    if hasattr(course, 'duration_display')
                                    else format_duration(course.duration_minutes))
            }
        except Exception as e:
            logger.warning(f"Error getting course info for certificate {obj.id}: {e}")
            return None

    def get_user(self, obj):
        """Get user information for certificate safely"""
        try:
            user = obj.enrollment.user
            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'username': user.username
            }
        except Exception as e:
            logger.warning(f"Error getting user info for certificate {obj.id}: {e}")
            return {'id': None, 'full_name': 'Unknown'}

    def get_verification_url(self, obj):
        """Get certificate verification URL safely"""
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/certificates/verify/{obj.certificate_number}/')
            return f'/certificates/verify/{obj.certificate_number}/'
        except Exception as e:
            logger.warning(f"Error building verification URL for certificate {obj.id}: {e}")
            return f'/certificates/verify/{obj.certificate_number}/'

    def get_enrollment(self, obj):
        """Get enrollment with proper context propagation"""
        try:
            context = self.get_serializer_context_for_nested()
            return EnrollmentSerializer(obj.enrollment, context=context).data
        except Exception as e:
            logger.warning(f"Error getting enrollment for certificate {obj.id}: {e}")
            return None


class UserProgressStatsSerializer(serializers.Serializer):
    """
    Serializer for aggregated user progress statistics

    Provides a standardized format for the UserProgressStatsView
    that ensures consistent field names and data types for frontend consumption
    """
    totalCourses = serializers.IntegerField()
    coursesCompleted = serializers.IntegerField()
    coursesInProgress = serializers.IntegerField()
    totalLessons = serializers.IntegerField()
    completedLessons = serializers.IntegerField()
    completionPercentage = serializers.FloatField()
    hoursSpent = serializers.FloatField()
    totalTimeSpent = serializers.IntegerField()
    assessmentsCompleted = serializers.IntegerField()
    averageScore = serializers.FloatField()
    certificatesEarned = serializers.IntegerField()
    recentActivity = serializers.ListField(child=serializers.DictField(), default=[])
    generatedAt = serializers.DateTimeField()

    class Meta:
        fields = (
            'totalCourses', 'coursesCompleted', 'coursesInProgress',
            'totalLessons', 'completedLessons', 'completionPercentage',
            'hoursSpent', 'totalTimeSpent', 'assessmentsCompleted',
            'averageScore', 'certificatesEarned', 'recentActivity', 'generatedAt'
        )
