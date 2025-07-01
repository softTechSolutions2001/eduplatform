#
# File Path: instructor_portal/serializers.py
# Folder Path: instructor_portal/


import json
import base64
import zlib
import logging
import hashlib
import os
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime, timedelta

from django.db import transaction, IntegrityError, models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from rest_framework import serializers

# Import from courses app
from courses.constants import (
    ACCESS_LEVEL_CHOICES, LESSON_TYPE_CHOICES, RESOURCE_TYPE_CHOICES,
    QUESTION_TYPE_CHOICES, LEVEL_CHOICES, CREATION_METHODS,
    COMPLETION_STATUSES
)

from courses.models import (
    Course, Module, Lesson, Resource, Category,
    Enrollment, Review, CourseProgress, Progress as LessonProgress
)

# Import instructor portal models
from .models import (
    InstructorProfile, CourseInstructor, InstructorDashboard, InstructorAnalytics,
    CourseCreationSession, CourseTemplate, DraftCourseContent, CourseContentDraft
)

# Import utilities and validators
from courses.validators import (
    validate_percentage, validate_duration_minutes, MinStrLenValidator,
    validate_video_url, validate_price_range
)

from courses.validation import validate_course_data, validate_lesson_data, sanitize_input
from courses.utils import clear_course_caches, generate_unique_slug

# Set up structured logging
logger = logging.getLogger(__name__)

# Constants from models/views
VALID_ACCESS_LEVELS = [choice[0] for choice in ACCESS_LEVEL_CHOICES]
VALID_LESSON_TYPES = [choice[0] for choice in LESSON_TYPE_CHOICES]
VALID_RESOURCE_TYPES = [choice[0] for choice in RESOURCE_TYPE_CHOICES]
VALID_LEVELS = [choice[0] for choice in LEVEL_CHOICES]
VALID_CREATION_METHODS = [choice[0] for choice in CREATION_METHODS]

MAX_BULK_OPERATION_SIZE = getattr(settings, 'MAX_BULK_OPERATION_SIZE', 100)
MAX_RESOURCE_FILE_SIZE = getattr(settings, 'MAX_RESOURCE_FILE_SIZE', 100 * 1024 * 1024)  # 100MB
MAX_THUMBNAIL_SIZE = getattr(settings, 'MAX_THUMBNAIL_SIZE', 5 * 1024 * 1024)  # 5MB
MAX_JSON_COMPRESSION_SIZE = getattr(settings, 'MAX_JSON_COMPRESSION_SIZE', 10 * 1024 * 1024)  # 10MB
PERMISSIONS_CACHE_TIMEOUT = getattr(settings, 'PERMISSIONS_CACHE_TIMEOUT', 180)  # 3 minutes

# =====================================
# UTILITY FUNCTIONS
# =====================================

def safe_decimal_conversion(value, default=Decimal('0.00')):
    """Safely convert value to Decimal for financial data"""
    try:
        if value is None:
            return default
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def validate_file_path_security(file_path: str) -> bool:
    """Enhanced file path security validation"""
    if not file_path or not isinstance(file_path, str):
        return False

    normalized_path = os.path.normpath(file_path)
    if '..' in normalized_path or normalized_path.startswith('/'):
        return False

    return True


def validate_instructor_tier_access(instructor_profile, required_tier, feature_name):
    """Validate if instructor tier has access to specific feature"""
    tier_hierarchy = {
        InstructorProfile.Tier.BRONZE: 1,
        InstructorProfile.Tier.SILVER: 2,
        InstructorProfile.Tier.GOLD: 3,
        InstructorProfile.Tier.PLATINUM: 4,
        InstructorProfile.Tier.DIAMOND: 5,
    }

    current_level = tier_hierarchy.get(instructor_profile.tier, 1)
    required_level = tier_hierarchy.get(required_tier, 1)

    if current_level < required_level:
        raise serializers.ValidationError(
            f"{feature_name} requires {required_tier} tier or higher. Current tier: {instructor_profile.tier}"
        )


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content for versioning"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


# =====================================
# MIXINS
# =====================================

class JsonFieldMixin:
    """Mixin for handling JSON field validation and coercion"""

    def _coerce_json(self, value: Any) -> Any:
        """Coerce string to JSON with error handling"""
        if isinstance(value, str):
            try:
                if len(value.encode('utf-8')) > MAX_JSON_COMPRESSION_SIZE:
                    raise serializers.ValidationError(
                        f"JSON data too large. Maximum size: {MAX_JSON_COMPRESSION_SIZE // (1024*1024)}MB"
                    )
                return json.loads(value)
            except json.JSONDecodeError as exc:
                logger.error("JSON coercion failed: %s", exc)
                raise serializers.ValidationError(f"Invalid JSON format: {exc}")

        return value

    def _inflate_modules_if_needed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress and convert modules_json_gz to modules_json if present"""
        gz_key = 'modules_json_gz'
        if gz_key in data:
            try:
                compressed_data = data[gz_key]
                try:
                    raw = base64.b64decode(compressed_data)
                except Exception as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Invalid base64 encoding: {exc}'}
                    )

                try:
                    json_bytes = zlib.decompress(raw, wbits=-15)
                except Exception as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Decompression failed: {exc}'}
                    )

                if len(json_bytes) > MAX_JSON_COMPRESSION_SIZE:
                    raise serializers.ValidationError(
                        {'modules_json_gz': 'Decompressed data too large'}
                    )

                try:
                    json_str = json_bytes.decode('utf-8')
                    data['modules_json'] = json_str
                    logger.info("Successfully decompressed modules_json_gz (%d bytes -> %d bytes)",
                              len(compressed_data), len(json_str))
                except UnicodeDecodeError as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Invalid UTF-8 encoding: {exc}'}
                    )
            except serializers.ValidationError:
                raise
            except Exception as exc:
                logger.error("Unexpected error in modules decompression: %s", exc)
                raise serializers.ValidationError(
                    {'modules_json_gz': f'Decompression failed: {exc}'}
                )

        return data

    def validate_json_list(self, value: Any, field_name: str, max_items: int = None) -> List:
        """Validate JSON field as list with security and limits"""
        if value is None:
            return []

        value = self._coerce_json(value)

        if not isinstance(value, list):
            raise serializers.ValidationError(f"{field_name} must be a list.")

        if max_items and len(value) > max_items:
            raise serializers.ValidationError(f"{field_name} cannot have more than {max_items} items.")

        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise serializers.ValidationError(f"{field_name}[{i}] must be a string.")

        return value


# =====================================
# INSTRUCTOR PROFILE SERIALIZERS
# =====================================

class InstructorProfileSerializer(serializers.ModelSerializer):
    """Serializer for instructor profile management"""
    expertise_areas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    expertise_areas_display = serializers.StringRelatedField(
        source='expertise_areas',
        many=True,
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    performance_metrics = serializers.SerializerMethodField()
    tier_benefits = serializers.SerializerMethodField()
    next_tier_requirements = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = [
            'id', 'display_name', 'bio', 'title', 'organization', 'years_experience',
            'website', 'linkedin_profile', 'twitter_handle', 'profile_image', 'cover_image',
            'status', 'status_display', 'is_verified', 'tier', 'tier_display',
            'total_students', 'total_courses', 'average_rating', 'total_reviews', 'total_revenue',
            'email_notifications', 'marketing_emails', 'public_profile',
            'expertise_areas', 'expertise_areas_display', 'performance_metrics',
            'tier_benefits', 'next_tier_requirements',
            'created_date', 'updated_date', 'last_login'
        ]
        read_only_fields = [
            'id', 'status', 'is_verified', 'tier', 'total_students', 'total_courses',
            'average_rating', 'total_reviews', 'total_revenue', 'created_date', 'updated_date'
        ]

    def get_performance_metrics(self, obj):
        """Get comprehensive performance metrics"""
        try:
            return obj.get_performance_metrics()
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

    def get_tier_benefits(self, obj):
        """Get benefits for current tier"""
        tier_benefits = {
            InstructorProfile.Tier.BRONZE: {
                'max_courses': 3,
                'max_file_size_mb': 10,
                'analytics_history_days': 30,
                'features': ['Basic analytics', 'Course creation', 'Student management']
            },
            InstructorProfile.Tier.SILVER: {
                'max_courses': 10,
                'max_file_size_mb': 50,
                'analytics_history_days': 90,
                'features': ['Advanced analytics', 'Course cloning', 'Revenue reports', 'Bulk operations']
            },
            InstructorProfile.Tier.GOLD: {
                'max_courses': 25,
                'max_file_size_mb': 100,
                'analytics_history_days': 180,
                'features': ['Premium analytics', 'AI course builder', 'Advanced imports', 'Co-instructor support']
            },
            InstructorProfile.Tier.PLATINUM: {
                'max_courses': 100,
                'max_file_size_mb': 500,
                'analytics_history_days': 365,
                'features': ['Enterprise analytics', 'Custom templates', 'API access', 'Priority support']
            },
            InstructorProfile.Tier.DIAMOND: {
                'max_courses': 1000,
                'max_file_size_mb': 1024,
                'analytics_history_days': 730,
                'features': ['Complete feature access', 'White-label options', 'Dedicated support', 'Beta features']
            }
        }
        return tier_benefits.get(obj.tier, tier_benefits[InstructorProfile.Tier.BRONZE])

    def get_next_tier_requirements(self, obj):
        """Get requirements for next tier"""
        tier_order = [
            InstructorProfile.Tier.BRONZE,
            InstructorProfile.Tier.SILVER,
            InstructorProfile.Tier.GOLD,
            InstructorProfile.Tier.PLATINUM,
            InstructorProfile.Tier.DIAMOND
        ]

        current_index = tier_order.index(obj.tier)
        if current_index >= len(tier_order) - 1:
            return None

        next_tier = tier_order[current_index + 1]
        requirements = {
            InstructorProfile.Tier.SILVER: {
                'min_students': 50,
                'min_courses': 2,
                'min_rating': 3.5,
                'min_reviews': 10
            },
            InstructorProfile.Tier.GOLD: {
                'min_students': 100,
                'min_courses': 5,
                'min_rating': 4.0,
                'min_reviews': 25
            },
            InstructorProfile.Tier.PLATINUM: {
                'min_students': 500,
                'min_courses': 10,
                'min_rating': 4.5,
                'min_reviews': 100
            },
            InstructorProfile.Tier.DIAMOND: {
                'min_students': 1000,
                'min_courses': 20,
                'min_rating': 4.5,
                'min_reviews': 200
            }
        }

        req = requirements.get(next_tier, {})
        progress = {
            'next_tier': next_tier,
            'requirements': req,
            'current_progress': {
                'students': obj.total_students,
                'courses': obj.total_courses,
                'rating': float(obj.average_rating),
                'reviews': obj.total_reviews
            }
        }
        return progress

    def validate_bio(self, value):
        """Validate instructor bio with tier requirements"""
        if value and len(value) < 50:
            if self.instance and self.instance.status == InstructorProfile.Status.ACTIVE:
                raise serializers.ValidationError("Active instructors must have a bio of at least 50 characters")
        return value

    def validate_years_experience(self, value):
        """Validate years of experience"""
        if value is not None and (value < 0 or value > 50):
            raise serializers.ValidationError("Years of experience must be between 0 and 50")
        return value

    def validate(self, data):
        """Enhanced validation for instructor profile"""
        # Active instructors need proper bio
        if data.get('status') == InstructorProfile.Status.ACTIVE:
            bio = data.get('bio', getattr(self.instance, 'bio', ''))
            if len(bio) < 100:
                raise serializers.ValidationError(
                    {'bio': 'Active instructors need detailed bio (100+ characters)'}
                )

            # Check for profile image
            profile_image = data.get('profile_image', getattr(self.instance, 'profile_image', None))
            if not profile_image:
                raise serializers.ValidationError(
                    {'profile_image': 'Active instructors must upload profile image'}
                )

        return data

    def save(self, **kwargs):
        """Override save to update analytics"""
        instance = super().save(**kwargs)
        # Update analytics on save, matching the model's behavior
        instance.update_analytics()
        return instance


class CourseInstructorSerializer(serializers.ModelSerializer):
    """Serializer for course instructor relationships"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    instructor_email = serializers.CharField(source='instructor.email', read_only=True)
    instructor_profile = InstructorProfileSerializer(source='instructor.instructor_profile', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CourseInstructor
        fields = [
            'id', 'course', 'instructor', 'role', 'role_display', 'is_active', 'is_lead',
            'can_edit_content', 'can_manage_students', 'can_view_analytics',
            'revenue_share_percentage', 'instructor_name', 'instructor_email', 'instructor_profile',
            'course_title', 'course_slug', 'joined_date', 'updated_date'
        ]
        read_only_fields = ['id', 'joined_date', 'updated_date']

    def validate_revenue_share_percentage(self, value):
        """Validate revenue share percentage"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Revenue share must be between 0 and 100 percent")
        return value

    def validate(self, data):
        """Validate course instructor relationships"""
        course = data.get('course')
        instructor = data.get('instructor')
        is_lead = data.get('is_lead', False)

        # Check if instructor already exists for this course
        if self.instance is None:
            existing = CourseInstructor.objects.filter(
                course=course, instructor=instructor, is_active=True
            ).exists()
            if existing:
                raise serializers.ValidationError("This instructor is already associated with this course")

        # Only one lead instructor per course
        if is_lead:
            existing_leads = CourseInstructor.objects.filter(
                course=course, is_lead=True, is_active=True
            )
            if self.instance:
                existing_leads = existing_leads.exclude(pk=self.instance.pk)

            if existing_leads.exists():
                raise serializers.ValidationError("Course can only have one lead instructor")

        # Validate instructor has profile
        try:
            if hasattr(instructor, 'instructor_profile'):
                instructor_profile = instructor.instructor_profile
                if instructor_profile.status != InstructorProfile.Status.ACTIVE:
                    raise serializers.ValidationError(
                        "Only active instructors can be added to courses"
                    )
        except (AttributeError, InstructorProfile.DoesNotExist):
            raise serializers.ValidationError(
                "User must have an active instructor profile"
            )

        return data


class InstructorDashboardSerializer(serializers.ModelSerializer):
    """Serializer for instructor dashboard configuration"""
    dashboard_data = serializers.SerializerMethodField()
    available_widgets = serializers.SerializerMethodField()

    class Meta:
        model = InstructorDashboard
        fields = [
            'id', 'show_analytics', 'show_recent_students', 'show_performance_metrics',
            'show_revenue_charts', 'show_course_progress', 'notify_new_enrollments',
            'notify_new_reviews', 'notify_course_completions', 'widget_order',
            'custom_colors', 'dashboard_data', 'available_widgets', 'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date']

    def get_dashboard_data(self, obj):
        """Get dashboard data with error handling"""
        try:
            # This would call the model's get_dashboard_data method
            return {
                'recent_activity': obj.get_recent_activity(),
                'instructor': {
                    'name': obj.instructor.display_name,
                    'tier': obj.instructor.get_tier_display(),
                    'status': obj.instructor.get_status_display()
                },
                # Additional dashboard data would go here
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def get_available_widgets(self, obj):
        """Get available dashboard widgets based on tier"""
        instructor_tier = obj.instructor.tier

        base_widgets = [
            {'id': 'course_overview', 'name': 'Course Overview', 'tier': 'bronze'},
            {'id': 'recent_students', 'name': 'Recent Students', 'tier': 'bronze'},
            {'id': 'basic_analytics', 'name': 'Basic Analytics', 'tier': 'bronze'},
        ]

        advanced_widgets = [
            {'id': 'revenue_charts', 'name': 'Revenue Charts', 'tier': 'silver'},
            {'id': 'performance_metrics', 'name': 'Performance Metrics', 'tier': 'silver'},
            {'id': 'student_engagement', 'name': 'Student Engagement', 'tier': 'gold'},
            {'id': 'course_analytics', 'name': 'Advanced Course Analytics', 'tier': 'gold'},
            {'id': 'revenue_forecasting', 'name': 'Revenue Forecasting', 'tier': 'platinum'},
            {'id': 'custom_reports', 'name': 'Custom Reports', 'tier': 'platinum'},
        ]

        tier_hierarchy = {
            InstructorProfile.Tier.BRONZE: 1,
            InstructorProfile.Tier.SILVER: 2,
            InstructorProfile.Tier.GOLD: 3,
            InstructorProfile.Tier.PLATINUM: 4,
            InstructorProfile.Tier.DIAMOND: 5,
        }

        widget_tier_hierarchy = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4, 'diamond': 5}
        user_tier_level = tier_hierarchy.get(instructor_tier, 1)

        return [widget for widget in base_widgets + advanced_widgets
                if user_tier_level >= widget_tier_hierarchy.get(widget['tier'], 1)]

    def validate_widget_order(self, value):
        """Validate widget order configuration"""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Widget order must be a list")
        return value

    def validate_custom_colors(self, value):
        """Validate custom color configuration"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Custom colors must be a dictionary")
        return value


# =====================================
# COURSE CREATION SERIALIZERS
# =====================================

class CourseCreationSessionSerializer(serializers.ModelSerializer):
    """Serializer for course creation session management"""
    instructor_name = serializers.CharField(source='instructor.display_name', read_only=True)
    instructor_tier = serializers.CharField(source='instructor.tier', read_only=True)
    creation_method_display = serializers.CharField(source='get_creation_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    validation_status = serializers.SerializerMethodField()
    step_configuration = serializers.SerializerMethodField()
    resume_data = serializers.SerializerMethodField()

    class Meta:
        model = CourseCreationSession
        fields = [
            'id', 'session_id', 'instructor', 'instructor_name', 'instructor_tier',
            'creation_method', 'creation_method_display', 'status', 'status_display',
            'course_data', 'current_step', 'total_steps', 'completed_steps', 'progress_percentage',
            'last_auto_save', 'auto_save_data', 'validation_errors', 'quality_score',
            'ai_prompt', 'ai_suggestions', 'template_used', 'draft_course', 'published_course',
            'validation_status', 'step_configuration', 'resume_data',
            'created_date', 'updated_date', 'expires_at'
        ]
        read_only_fields = [
            'id', 'session_id', 'progress_percentage', 'last_auto_save', 'validation_errors',
            'published_course', 'created_date', 'updated_date'
        ]

    def get_validation_status(self, obj):
        """Get current validation status"""
        try:
            errors = obj.validate_course_data()
            return {
                'is_valid': len(errors) == 0,
                'error_count': len(errors),
                'errors': errors[:5],  # Limit to first 5 errors
                'completeness_score': self._calculate_completeness_score(obj)
            }
        except Exception as e:
            logger.error(f"Error getting validation status: {e}")
            return {'is_valid': False, 'error_count': 1, 'errors': ['Validation check failed']}

    def get_step_configuration(self, obj):
        """Get step configuration based on creation method"""
        step_configs = {
            CourseCreationSession.CreationMethod.WIZARD: {
                'steps': [
                    {'number': 1, 'name': 'Basic Information', 'required_fields': ['title', 'description', 'category']},
                    {'number': 2, 'name': 'Course Structure', 'required_fields': ['modules']},
                    {'number': 3, 'name': 'Content Creation', 'required_fields': ['lessons']},
                    {'number': 4, 'name': 'Resources & Materials', 'required_fields': []},
                    {'number': 5, 'name': 'Pricing & Publishing', 'required_fields': ['price']},
                    {'number': 6, 'name': 'Review & Publish', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.AI_BUILDER: {
                'steps': [
                    {'number': 1, 'name': 'AI Prompt', 'required_fields': ['ai_prompt']},
                    {'number': 2, 'name': 'Generated Content Review', 'required_fields': []},
                    {'number': 3, 'name': 'Content Refinement', 'required_fields': []},
                    {'number': 4, 'name': 'Finalization', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.DRAG_DROP: {
                'steps': [
                    {'number': 1, 'name': 'Course Setup', 'required_fields': ['title', 'description']},
                    {'number': 2, 'name': 'Content Assembly', 'required_fields': []},
                    {'number': 3, 'name': 'Organization', 'required_fields': []},
                    {'number': 4, 'name': 'Publishing Setup', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.TEMPLATE: {
                'steps': [
                    {'number': 1, 'name': 'Template Selection', 'required_fields': ['template_used']},
                    {'number': 2, 'name': 'Customization', 'required_fields': []},
                    {'number': 3, 'name': 'Content Population', 'required_fields': []},
                    {'number': 4, 'name': 'Review & Publish', 'required_fields': []}
                ]
            }
        }
        return step_configs.get(obj.creation_method, {'steps': []})

    def get_resume_data(self, obj):
        """Get data needed to resume course creation"""
        try:
            course_data = obj.course_data
            return {
                'current_step': obj.current_step,
                'total_steps': obj.total_steps,
                'completed_steps': obj.completed_steps,
                'progress_percentage': float(obj.progress_percentage),
                'has_title': bool(course_data.get('title')),
                'has_category': bool(course_data.get('category_id')),
                'modules_count': len(course_data.get('modules', [])),
                'creation_method': obj.creation_method,
                'status': obj.status
            }
        except Exception as e:
            logger.error(f"Error getting resume data: {e}")
            return {}

    def _calculate_completeness_score(self, obj):
        """Calculate course completeness percentage"""
        try:
            course_data = obj.course_data
            total_checks = 0
            completed_checks = 0

            # Basic information checks
            basic_fields = ['title', 'description', 'category_id']
            for field in basic_fields:
                total_checks += 1
                if course_data.get(field):
                    completed_checks += 1

            # Module and lesson checks
            modules = course_data.get('modules', [])
            if modules:
                total_checks += 1
                completed_checks += 1

                for module in modules:
                    total_checks += 2  # title and lessons
                    if module.get('title'):
                        completed_checks += 1

                    lessons = module.get('lessons', [])
                    if lessons:
                        completed_checks += 1

                        for lesson in lessons:
                            total_checks += 2  # title and content
                            if lesson.get('title'):
                                completed_checks += 1
                            if lesson.get('content') or lesson.get('video_url'):
                                completed_checks += 1

            # Additional fields
            additional_fields = ['price', 'level', 'learning_objectives']
            for field in additional_fields:
                total_checks += 1
                if course_data.get(field):
                    completed_checks += 1

            return (completed_checks / total_checks * 100) if total_checks > 0 else 0

        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0

    def validate_creation_method(self, value):
        """Validate creation method with tier restrictions"""
        if value not in [choice[0] for choice in CourseCreationSession.CreationMethod.choices]:
            raise serializers.ValidationError("Invalid creation method")

        # AI Builder requires Gold tier or higher
        if value == CourseCreationSession.CreationMethod.AI_BUILDER:
            request = self.context.get('request')
            if request and hasattr(request, 'instructor_profile'):
                validate_instructor_tier_access(
                    request.instructor_profile,
                    InstructorProfile.Tier.GOLD,
                    "AI Course Builder"
                )

        return value

    def validate_ai_prompt(self, value):
        """Validate AI prompt with length limits"""
        if value:
            if len(value) < 20:
                raise serializers.ValidationError("AI prompt must be at least 20 characters")
            if len(value) > 2000:
                raise serializers.ValidationError("AI prompt cannot exceed 2000 characters")
        return value

    @transaction.atomic
    def publish_course(self):
        """
        Convert session data to published course
        Matches the implementation in CourseCreationSession.publish_course model method
        """
        # Call the model's publish_course method directly
        instance = self.instance

        if not instance:
            raise serializers.ValidationError("Must save session before publishing")

        if instance.status != CourseCreationSession.Status.READY_TO_PUBLISH:
            instance.status = CourseCreationSession.Status.VALIDATING
            instance.save(update_fields=['status'])

            # Validate first
            errors = instance.validate_course_data()
            if errors:
                instance.status = CourseCreationSession.Status.FAILED
                instance.validation_errors = errors
                instance.save(update_fields=['status', 'validation_errors'])
                return None

            instance.status = CourseCreationSession.Status.READY_TO_PUBLISH
            instance.save(update_fields=['status'])

        # Now call the model's publish_course method
        try:
            return instance.publish_course()
        except Exception as e:
            logger.error(f"Error publishing course: {e}")
            instance.status = CourseCreationSession.Status.FAILED
            instance.save(update_fields=['status'])
            raise serializers.ValidationError(f"Course publishing failed: {str(e)}")


class CourseTemplateSerializer(serializers.ModelSerializer):
    """Serializer for course template management"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    usage_analytics = serializers.SerializerMethodField()
    preview_data = serializers.SerializerMethodField()

    class Meta:
        model = CourseTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_display',
            'category', 'category_name', 'template_data', 'estimated_duration',
            'difficulty_level', 'usage_count', 'success_rate', 'is_active',
            'created_by', 'created_by_name', 'usage_analytics', 'preview_data',
            'created_date', 'updated_date'
        ]
        read_only_fields = [
            'id', 'usage_count', 'success_rate', 'created_by', 'created_date', 'updated_date'
        ]

    def get_usage_analytics(self, obj):
        """Get template usage analytics"""
        try:
            thirty_days_ago = timezone.now() - timedelta(days=30)

            recent_sessions = CourseCreationSession.objects.filter(
                template_used=obj.name,
                created_date__gte=thirty_days_ago
            )

            total_recent = recent_sessions.count()
            successful_recent = recent_sessions.filter(
                status=CourseCreationSession.Status.PUBLISHED
            ).count()

            return {
                'total_usage': obj.usage_count,
                'recent_usage_30_days': total_recent,
                'recent_success_rate': (successful_recent / total_recent * 100) if total_recent > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {}

    def get_preview_data(self, obj):
        """Get template preview data"""
        try:
            template_data = obj.template_data
            preview = {
                'structure_overview': {
                    'modules_count': len(template_data.get('modules', [])),
                    'estimated_lessons': sum(
                        len(module.get('lessons', []))
                        for module in template_data.get('modules', [])
                    ),
                    'content_types': list(set(
                        lesson.get('type', 'text')
                        for module in template_data.get('modules', [])
                        for lesson in module.get('lessons', [])
                    ))
                },
                'sample_modules': [
                    {
                        'title': module.get('title', ''),
                        'lesson_count': len(module.get('lessons', []))
                    }
                    for module in template_data.get('modules', [])[:3]
                ]
            }
            return preview
        except Exception as e:
            logger.error(f"Error getting preview data: {e}")
            return {}

    def validate_template_data(self, value):
        """Validate template data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Template data must be a dictionary")

        required_keys = ['metadata', 'modules']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Template data must include '{key}' section")

        modules = value.get('modules', [])
        if not isinstance(modules, list):
            raise serializers.ValidationError("Modules must be a list")

        for i, module in enumerate(modules):
            if not isinstance(module, dict):
                raise serializers.ValidationError(f"Module {i+1} must be an object")

            if 'title' not in module:
                raise serializers.ValidationError(f"Module {i+1} must have a title")

            lessons = module.get('lessons', [])
            if not isinstance(lessons, list):
                raise serializers.ValidationError(f"Module {i+1} lessons must be a list")

        return value

    def create_session_from_template(self, instructor):
        """Create a course creation session using this template"""
        try:
            session = CourseCreationSession.objects.create(
                instructor=instructor,
                creation_method=CourseCreationSession.CreationMethod.TEMPLATE,
                template_used=self.instance.name,
                course_data=self.instance.template_data.copy(),
                total_steps=4,  # Template-based creation has 4 steps
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            # Update template usage statistics (using F() to avoid race conditions)
            with transaction.atomic():
                CourseTemplate.objects.filter(id=self.instance.id).update(
                    usage_count=models.F('usage_count') + 1
                )
                self.instance.refresh_from_db(fields=['usage_count'])

            return session
        except Exception as e:
            logger.error(f"Error creating session from template: {e}")
            raise serializers.ValidationError(f"Failed to create session from template: {str(e)}")


class DraftCourseContentSerializer(serializers.ModelSerializer):
    """Serializer for draft course content management"""
    session_info = serializers.CharField(source='session.session_id', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    content_hash = serializers.SerializerMethodField()
    version_history = serializers.SerializerMethodField()

    class Meta:
        model = DraftCourseContent
        fields = [
            'id', 'session', 'session_info', 'content_type', 'content_type_display',
            'content_id', 'version', 'content_data', 'title', 'order', 'is_complete',
            'validation_errors', 'auto_save_version', 'content_hash', 'version_history',
            'last_saved'
        ]
        read_only_fields = ['id', 'auto_save_version', 'last_saved']

    def get_content_hash(self, obj):
        """Generate hash of content for change detection"""
        try:
            content_str = json.dumps(obj.content_data, sort_keys=True)
            return calculate_content_hash(content_str)
        except Exception:
            return ''

    def get_version_history(self, obj):
        """Get version history for this content"""
        try:
            versions = DraftCourseContent.objects.filter(
                session=obj.session,
                content_type=obj.content_type,
                content_id=obj.content_id
            ).order_by('-version')[:5]

            return [
                {
                    'version': v.version,
                    'created': v.last_saved,
                    'changes_summary': self._get_changes_summary(obj, v) if v.version < obj.version else None
                }
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return []

    def _get_changes_summary(self, current, previous):
        """Generate summary of changes between versions"""
        try:
            changes = []

            if current.title != previous.title:
                changes.append('Title changed')

            if current.content_data != previous.content_data:
                changes.append('Content modified')

            if current.order != previous.order:
                changes.append('Order changed')

            return ', '.join(changes) if changes else 'Minor updates'
        except Exception:
            return 'Changes detected'

    def validate_content_data(self, value):
        """Validate content data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Content data must be a dictionary")
        return value

    def validate_order(self, value):
        """Validate display order"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Order must be positive")
        return value

    def validate_version(self, value):
        """Validate version number"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Version must be positive")
        return value


class CourseContentDraftSerializer(serializers.ModelSerializer):
    """Serializer for course content draft with file handling"""
    session_info = serializers.CharField(source='session.session_id', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    processing_status_display = serializers.CharField(source='get_processing_status_display', read_only=True)
    file_info = serializers.SerializerMethodField()

    class Meta:
        model = CourseContentDraft
        fields = [
            'id', 'session', 'session_info', 'content_type', 'content_type_display',
            'file_path', 'content_hash', 'version', 'is_processed', 'processing_status',
            'processing_status_display', 'file_size', 'mime_type', 'file_info',
            'created_date', 'processed_date'
        ]
        read_only_fields = [
            'id', 'content_hash', 'is_processed', 'processing_status', 'file_size',
            'created_date', 'processed_date'
        ]

    def get_file_info(self, obj):
        """Get file information and metadata"""
        try:
            if obj.file_path:
                return {
                    'filename': os.path.basename(obj.file_path),
                    'extension': os.path.splitext(obj.file_path)[1].lower(),
                    'size_mb': round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0,
                    'mime_type': obj.mime_type,
                    'is_secure': validate_file_path_security(obj.file_path)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    def validate_file_path(self, value):
        """Validate file path security"""
        if value and not validate_file_path_security(value):
            raise serializers.ValidationError("Invalid file path for security reasons")
        return value


# =====================================
# COURSE CONTENT SERIALIZERS
# =====================================

class InstructorResourceSerializer(serializers.ModelSerializer):
    """Serializer for instructor resources"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)
    upload_info = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'type', 'file', 'url', 'description', 'premium',
            'storage_key', 'uploaded', 'file_size', 'mime_type', 'order', 'duration_minutes',
            'lesson_title', 'course_title', 'upload_info'
        ]
        read_only_fields = ['id', 'uploaded']

    def get_upload_info(self, obj):
        """Get upload information and status"""
        try:
            return {
                'has_file': bool(obj.file or obj.storage_key),
                'file_size_mb': round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0,
                'is_secure': validate_file_path_security(obj.file),
                'upload_date': obj.uploaded
            }
        except Exception:
            return {}

    def validate_type(self, value):
        """Validate resource type"""
        if value not in VALID_RESOURCE_TYPES:
            raise serializers.ValidationError(f"Invalid resource type. Must be one of: {', '.join(VALID_RESOURCE_TYPES)}")
        return value

    def validate_title(self, value):
        """Enhanced resource title validation"""
        if not value or not value.strip():
            raise serializers.ValidationError("Resource title is required.")

        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Resource title must be at least 3 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Resource title must be less than 200 characters.")

        return value

    def validate(self, data):
        """Cross-field validation"""
        resource_type = data.get('type')
        file_data = data.get('file')
        url_data = data.get('url')
        storage_key = data.get('storage_key')

        if resource_type in ['document', 'video', 'audio', 'image'] and not any([file_data, url_data, storage_key]):
            raise serializers.ValidationError("Either file, URL, or storage_key must be provided for this resource type.")

        if resource_type == 'link' and not url_data:
            raise serializers.ValidationError("URL is required for external link resources.")

        # Enhanced video URL validation
        if resource_type == 'video' and url_data:
            try:
                validate_video_url(url_data)
            except Exception as exc:
                raise serializers.ValidationError(f"Invalid video URL: {exc}")

        return data


class InstructorLessonSerializer(serializers.ModelSerializer):
    """Serializer for instructor lessons"""
    resources = InstructorResourceSerializer(many=True, read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    progress_analytics = serializers.SerializerMethodField()
    content_analytics = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'guest_content', 'registered_content',
            'access_level', 'duration_minutes', 'type', 'order',
            'has_assessment', 'has_lab', 'is_free_preview', 'video_url',
            'transcript', 'resources', 'module_title', 'course_title',
            'progress_analytics', 'content_analytics'
        ]
        read_only_fields = ['id']

    def get_progress_analytics(self, obj):
        """Get lesson progress analytics"""
        try:
            progress_data = LessonProgress.objects.filter(lesson=obj).aggregate(
                total_students=models.Count('user', distinct=True),
                completed_students=models.Count(
                    'user', filter=models.Q(completed=True), distinct=True
                ),
                avg_time_spent=models.Avg('time_spent'),
                total_views=models.Sum('views_count')
            )

            completion_rate = 0
            if progress_data['total_students'] and progress_data['total_students'] > 0:
                completion_rate = (progress_data['completed_students'] / progress_data['total_students'] * 100)

            return {
                'total_students': progress_data['total_students'] or 0,
                'completed_students': progress_data['completed_students'] or 0,
                'completion_rate': round(completion_rate, 2),
                'avg_time_spent_minutes': round((progress_data['avg_time_spent'] or 0) / 60, 2),
                'total_views': progress_data['total_views'] or 0
            }
        except Exception as e:
            logger.error(f"Error getting lesson progress analytics: {e}")
            return {}

    def get_content_analytics(self, obj):
        """Get content quality analytics"""
        try:
            content_length = len(obj.content or '')
            video_present = bool(obj.video_url)
            resources_count = obj.resources.count()

            quality_score = 0
            quality_factors = []

            # Content length scoring
            if content_length > 500:
                quality_score += 25
                quality_factors.append('Adequate content length')
            elif content_length > 200:
                quality_score += 15
                quality_factors.append('Basic content length')

            # Video content scoring
            if video_present:
                quality_score += 30
                quality_factors.append('Video content included')

            # Resources scoring
            if resources_count >= 3:
                quality_score += 25
                quality_factors.append('Rich resource collection')
            elif resources_count >= 1:
                quality_score += 15
                quality_factors.append('Has supporting resources')

            # Assessment scoring
            if obj.has_assessment:
                quality_score += 20
                quality_factors.append('Includes assessment')

            return {
                'quality_score': min(quality_score, 100),
                'quality_factors': quality_factors,
                'content_stats': {
                    'content_length': content_length,
                    'has_video': video_present,
                    'resources_count': resources_count,
                    'has_assessment': obj.has_assessment
                }
            }
        except Exception as e:
            logger.error(f"Error getting content analytics: {e}")
            return {}

    def validate_access_level(self, value):
        """Validate access level"""
        if value not in VALID_ACCESS_LEVELS:
            raise serializers.ValidationError(f"Invalid access level. Must be one of: {', '.join(VALID_ACCESS_LEVELS)}")
        return value

    def validate_type(self, value):
        """Validate lesson type"""
        if value not in VALID_LESSON_TYPES:
            raise serializers.ValidationError(f"Invalid lesson type. Must be one of: {', '.join(VALID_LESSON_TYPES)}")
        return value

    def validate_title(self, value):
        """Enhanced lesson title validation"""
        if not value or not value.strip():
            raise serializers.ValidationError("Lesson title is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Lesson title must be at least 3 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Lesson title must be less than 200 characters.")

        return value

    def validate(self, data):
        """Validate based on access level"""
        access_level = data.get('access_level', 'registered')
        content = data.get('content', '')
        guest_content = data.get('guest_content', '')
        registered_content = data.get('registered_content', '')

        # Ensure at least one content field is provided
        if not any([content, guest_content, registered_content]):
            raise serializers.ValidationError("At least one content field must be provided.")

        # Enhanced validation based on access level
        if access_level == 'guest':
            if not guest_content and not content:
                raise serializers.ValidationError(
                    "Guest content or full content is required for guest access level lessons."
                )

        if access_level == 'registered':
            if not (registered_content or content):
                raise serializers.ValidationError(
                    "Registered content or full content must be provided for registered access level lessons."
                )

        if access_level == 'premium':
            if not content:
                raise serializers.ValidationError(
                    "Full content is required for premium access level lessons."
                )

        return data


class InstructorModuleSerializer(serializers.ModelSerializer):
    """Serializer for instructor modules"""
    lessons_count = serializers.SerializerMethodField()
    lessons = InstructorLessonSerializer(many=True, read_only=True, required=False)
    course_title = serializers.CharField(source='course.title', read_only=True)
    completion_analytics = serializers.SerializerMethodField()
    content_summary = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'duration_minutes',
            'is_published', 'lessons_count', 'lessons', 'course_title',
            'completion_analytics', 'content_summary'
        ]
        read_only_fields = ['id']

    def get_lessons_count(self, obj):
        """Get the count of lessons with optimization"""
        if hasattr(obj, '_lessons_count'):
            return obj._lessons_count
        return obj.lessons.count()

    def get_completion_analytics(self, obj):
        """Get module completion analytics"""
        try:
            # Get progress data for all lessons
            lesson_ids = obj.lessons.values_list('id', flat=True)

            if not lesson_ids:
                return {
                    'total_students': 0,
                    'completed_students': 0,
                    'completion_rate': 0,
                    'avg_time_spent_minutes': 0
                }

            # Aggregate lesson progress data
            progress_data = LessonProgress.objects.filter(
                lesson__in=lesson_ids
            ).aggregate(
                total_students=models.Count('user', distinct=True),
                avg_time_spent=models.Avg('time_spent')
            )

            # Count students who completed all lessons in module
            completed_students = LessonProgress.objects.filter(
                lesson__in=lesson_ids,
                completed=True
            ).values('user').annotate(
                completed_lessons=models.Count('lesson')
            ).filter(
                completed_lessons=len(lesson_ids)
            ).count()

            completion_rate = 0
            if progress_data['total_students'] and progress_data['total_students'] > 0:
                completion_rate = (completed_students / progress_data['total_students'] * 100)

            return {
                'total_students': progress_data['total_students'] or 0,
                'completed_students': completed_students,
                'completion_rate': round(completion_rate, 2),
                'avg_time_spent_minutes': round((progress_data['avg_time_spent'] or 0) / 60, 2)
            }
        except Exception as e:
            logger.error(f"Error getting module completion analytics: {e}")
            return {
                'completion_rate': 0
            }

    def get_content_summary(self, obj):
        """Get module content summary and quality metrics"""
        try:
            lessons = obj.lessons.all()

            summary = {
                'total_lessons': lessons.count(),
                'video_lessons': lessons.filter(video_url__isnull=False).exclude(video_url='').count(),
                'assessment_lessons': lessons.filter(has_assessment=True).count(),
                'lab_lessons': lessons.filter(has_lab=True).count(),
                'free_preview_lessons': lessons.filter(is_free_preview=True).count(),
                'total_resources': sum(lesson.resources.count() for lesson in lessons),
                'estimated_duration': sum(lesson.duration_minutes or 0 for lesson in lessons)
            }

            return summary
        except Exception as e:
            logger.error(f"Error getting content summary: {e}")
            return {}

    def validate_title(self, value):
        """Enhanced module title validation"""
        if not value or not value.strip():
            raise serializers.ValidationError("Module title is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Module title must be at least 3 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Module title must be less than 200 characters.")

        return value

class DraftCoursePublishSerializer(serializers.Serializer):
    """
    Serializer for publishing draft courses
    Controls publish settings and validation
    """
    is_published = serializers.BooleanField(default=True)
    publish_now = serializers.BooleanField(default=True)
    publish_date = serializers.DateTimeField(required=False, allow_null=True)
    notify_students = serializers.BooleanField(default=False)

    def validate(self, data):
        """Validate publish settings consistency"""
        publish_now = data.get('publish_now', True)
        publish_date = data.get('publish_date')

        if not publish_now and not publish_date:
            raise serializers.ValidationError(
                "Either publish now must be true or a publish date must be provided"
            )

        if publish_now and publish_date:
            # Ignore publish_date if publishing now
            data['publish_date'] = None

        return data

class InstructorCourseSerializer(serializers.ModelSerializer, JsonFieldMixin):
    """Serializer for instructor courses"""
    modules_count = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    modules_json = serializers.CharField(write_only=True, required=False)
    modules_json_gz = serializers.CharField(write_only=True, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructors = serializers.SerializerMethodField()
    instructor_role = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    course_analytics = serializers.SerializerMethodField()

    # Analytics fields matching views.py required fields
    enrolled_students_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    revenue_analytics = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'subtitle', 'slug', 'description', 'short_description', 'category',
            'category_id', 'category_name', 'thumbnail', 'price', 'discount_price', 'discount_ends',
            'level', 'duration_minutes', 'has_certificate', 'is_published', 'is_draft',
            'creation_method', 'completion_status', 'completion_percentage', 'version', 'parent_version',
            'modules_count', 'modules', 'requirements', 'skills', 'learning_objectives', 'target_audience',
            'modules_json', 'modules_json_gz', 'instructors', 'instructor_role', 'can_edit',
            'enrolled_students_count', 'avg_rating', 'total_reviews', 'course_analytics', 'revenue_analytics',
            'created_date', 'updated_date', 'published_date'
        ]
        read_only_fields = [
            'id', 'slug', 'version', 'parent_version', 'enrolled_students_count', 'avg_rating',
            'total_reviews', 'created_date', 'updated_date', 'published_date'
        ]

    def get_modules_count(self, obj):
        """Get the count of modules"""
        if hasattr(obj, '_modules_count'):
            return obj._modules_count
        return obj.modules.count()

    def get_modules(self, obj):
        """Get modules with proper serialization"""
        try:
            modules = obj.modules.prefetch_related('lessons__resources').order_by('order')
            return InstructorModuleSerializer(modules, many=True, context=self.context).data
        except Exception as e:
            logger.error(f"Error serializing modules: {e}")
            return []

    def get_instructors(self, obj):
        """Get list of instructors with CourseInstructor relationship data"""
        try:
            instructors = []
            for course_instructor in obj.courseinstructor_set.select_related('instructor').filter(is_active=True):
                instructor_data = {
                    'id': course_instructor.instructor.id,
                    'name': f"{course_instructor.instructor.first_name} {course_instructor.instructor.last_name}".strip(),
                    'email': course_instructor.instructor.email,
                    'role': course_instructor.get_role_display(),
                    'is_lead': course_instructor.is_lead,
                    'can_edit_content': course_instructor.can_edit_content,
                    'can_manage_students': course_instructor.can_manage_students,
                    'can_view_analytics': course_instructor.can_view_analytics,
                    'revenue_share': float(course_instructor.revenue_share_percentage),
                    'joined_date': course_instructor.joined_date
                }
                # Fallback for name if empty
                if not instructor_data['name']:
                    instructor_data['name'] = course_instructor.instructor.username
                instructors.append(instructor_data)
            return instructors
        except Exception as exc:
            logger.warning("Error getting instructors for course %s: %s", getattr(obj, 'id', 'unknown'), exc)
            return []

    def get_instructor_role(self, obj):
        """Get current user's role for this course"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        try:
            course_instructor = obj.courseinstructor_set.filter(
                instructor=request.user,
                is_active=True
            ).first()
            return {
                'role': course_instructor.get_role_display(),
                'permissions': {
                    'can_edit_content': course_instructor.can_edit_content,
                    'can_manage_students': course_instructor.can_manage_students,
                    'can_view_analytics': course_instructor.can_view_analytics,
                    'is_lead': course_instructor.is_lead
                }
            } if course_instructor else None
        except Exception:
            return None

    def get_can_edit(self, obj):
        """Check if current user can edit this course"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        try:
            course_instructor = obj.courseinstructor_set.filter(
                instructor=request.user,
                is_active=True
            ).first()
            return course_instructor.can_edit_content if course_instructor else False
        except Exception:
            return False

    def get_course_analytics(self, obj):
        """Get comprehensive course analytics"""
        try:
            # Basic enrollment analytics
            enrollments = Enrollment.objects.filter(course=obj)

            analytics = {
                'enrollment_stats': {
                    'total_enrolled': enrollments.count(),
                    'active_students': enrollments.filter(status='active').count(),
                    'completed_students': enrollments.filter(status='completed').count(),
                    'dropped_students': enrollments.filter(status='dropped').count()
                },
                'completion_analytics': {
                    'completion_rate': self._calculate_completion_rate(obj),
                    'avg_progress_percentage': self._calculate_avg_progress(obj)
                },
                'engagement_metrics': {
                    'total_lesson_views': self._calculate_total_views(obj),
                    'most_popular_lessons': self._get_popular_lessons(obj)
                },
                'review_analytics': {
                    'total_reviews': obj.reviews.count() if hasattr(obj, 'reviews') else 0,
                    'avg_rating': float(obj.avg_rating) if hasattr(obj, 'avg_rating') and obj.avg_rating else 0.0,
                    'rating_distribution': self._get_rating_distribution(obj)
                }
            }

            return analytics
        except Exception as e:
            logger.error(f"Error getting course analytics: {e}")
            return {}

    def get_revenue_analytics(self, obj):
        """Get course revenue analytics"""
        try:
            # This would integrate with your payment system
            enrollments = Enrollment.objects.filter(course=obj, status__in=['active', 'completed'])

            total_revenue = enrollments.count() * float(obj.price or 0)

            # Get monthly revenue breakdown
            monthly_data = []
            for i in range(6):  # Last 6 months
                month_start = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
                month_end = month_start + timezone.timedelta(days=30)

                monthly_enrollments = enrollments.filter(
                    created_date__range=[month_start, month_end]
                ).count()

                monthly_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'enrollments': monthly_enrollments,
                    'revenue': monthly_enrollments * float(obj.price or 0)
                })

            return {
                'total_revenue': total_revenue,
                'avg_revenue_per_student': float(obj.price or 0),
                'monthly_breakdown': monthly_data,
                'revenue_trend': self._calculate_revenue_trend(obj)
            }
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return {}

    def _calculate_completion_rate(self, obj):
        """Calculate course completion rate"""
        try:
            total_enrolled = Enrollment.objects.filter(course=obj).count()
            if total_enrolled == 0:
                return 0

            completed = Enrollment.objects.filter(course=obj, status='completed').count()
            return round((completed / total_enrolled) * 100, 2)
        except Exception:
            return 0

    def _calculate_avg_progress(self, obj):
        """Calculate average progress percentage"""
        try:
            progress_data = CourseProgress.objects.filter(course=obj).aggregate(
                avg_progress=models.Avg('progress_percentage')
            )
            return round(progress_data['avg_progress'] or 0, 2)
        except Exception:
            return 0

    def _calculate_total_views(self, obj):
        """Calculate total lesson views for course"""
        try:
            lesson_ids = obj.modules.values_list('lessons__id', flat=True)
            total_views = LessonProgress.objects.filter(
                lesson__in=lesson_ids
            ).aggregate(
                total=models.Sum('views_count')
            )
            return total_views['total'] or 0
        except Exception:
            return 0

    def _get_popular_lessons(self, obj):
        """Get most popular lessons by views"""
        try:
            lesson_ids = obj.modules.values_list('lessons__id', flat=True)
            popular_lessons = LessonProgress.objects.filter(
                lesson__in=lesson_ids
            ).values(
                'lesson__title'
            ).annotate(
                total_views=models.Sum('views_count')
            ).order_by('-total_views')[:5]

            return [
                {
                    'title': lesson['lesson__title'],
                    'views': lesson['total_views']
                }
                for lesson in popular_lessons
            ]
        except Exception:
            return []

    def _get_rating_distribution(self, obj):
        """Get rating distribution breakdown"""
        try:
            if hasattr(obj, 'reviews'):
                distribution = obj.reviews.values('rating').annotate(
                    count=models.Count('rating')
                ).order_by('rating')

                return {
                    str(item['rating']): item['count']
                    for item in distribution
                }
            return {}
        except Exception:
            return {}

    def _calculate_revenue_trend(self, obj):
        """Calculate revenue trend percentage"""
        try:
            current_month = timezone.now().replace(day=1)
            last_month = current_month - timezone.timedelta(days=30)

            current_enrollments = Enrollment.objects.filter(
                course=obj,
                created_date__gte=current_month,
                status__in=['active', 'completed']
            ).count()

            last_enrollments = Enrollment.objects.filter(
                course=obj,
                created_date__range=[last_month, current_month],
                status__in=['active', 'completed']
            ).count()

            if last_enrollments > 0:
                trend = ((current_enrollments - last_enrollments) / last_enrollments) * 100
                return round(trend, 2)

            return 0
        except Exception:
            return 0

    def validate_level(self, value):
        """Validate course level"""
        if value not in VALID_LEVELS:
            raise serializers.ValidationError(f"Invalid level. Must be one of: {', '.join(VALID_LEVELS)}")
        return value

    def validate_price(self, value):
        """Enhanced price validation with decimal conversion"""
        if value is not None:
            try:
                decimal_value = safe_decimal_conversion(value)
                validate_price_range(float(decimal_value))
                return decimal_value
            except Exception as exc:
                raise serializers.ValidationError(f"Invalid price: {exc}")
        return value

    def validate_title(self, value):
        """Enhanced course title validation"""
        if not value or not value.strip():
            raise serializers.ValidationError("Course title is required.")

        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError("Course title must be at least 5 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Course title must be less than 200 characters.")

        return value

    def validate_description(self, value):
        """Enhanced course description validation"""
        if not value or not value.strip():
            raise serializers.ValidationError("Course description is required.")

        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError("Course description must be at least 10 characters.")
        if len(value) > 5000:
            raise serializers.ValidationError("Course description must be less than 5000 characters.")

        return value

    def validate_requirements(self, value):
        """Enhanced requirements validation using mixin"""
        return self.validate_json_list(value, "Requirements", max_items=20)

    def validate_skills(self, value):
        """Enhanced skills validation using mixin"""
        return self.validate_json_list(value, "Skills", max_items=15)

    def validate_learning_objectives(self, value):
        """Enhanced learning objectives validation using mixin"""
        return self.validate_json_list(value, "Learning objectives", max_items=15)

    def validate_target_audience(self, value):
        """Enhanced target audience validation using mixin"""
        return self.validate_json_list(value, "Target audience", max_items=10)

    @transaction.atomic
    def create(self, validated_data):
        """Create course with instructor relationship and module creation"""
        try:
            # Extract modules data
            modules_data = None
            if 'modules_json' in validated_data:
                modules_data = self._coerce_json(validated_data.pop('modules_json'))
            elif 'modules_json_gz' in validated_data:
                validated_data = self._inflate_modules_if_needed(validated_data)
                modules_data = self._coerce_json(validated_data.pop('modules_json', '[]'))

            validated_data.pop('modules_json_gz', None)

            # Handle JSON fields with safe coercion
            for field in ['requirements', 'skills', 'learning_objectives', 'target_audience']:
                if field in validated_data and isinstance(validated_data[field], str):
                    validated_data[field] = self._coerce_json(validated_data[field])

            # Create course
            course = super().create(validated_data)

            # Create instructor relationship
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                CourseInstructor.objects.create(
                    course=course,
                    instructor=request.user,
                    role=CourseInstructor.Role.PRIMARY,
                    is_lead=True,
                    is_active=True,
                    can_edit_content=True,
                    can_manage_students=True,
                    can_view_analytics=True,
                    revenue_share_percentage=Decimal('100.00')
                )

            # Process modules if provided
            if modules_data:
                self._bulk_create_modules(course, modules_data)

            # Update instructor analytics
            if request and hasattr(request, 'instructor_profile'):
                request.instructor_profile.update_analytics()

            return course

        except IntegrityError as exc:
            logger.error("Course creation integrity error: %s", exc)
            raise serializers.ValidationError("Course creation failed due to data conflict")
        except Exception as exc:
            logger.error("Error in course creation: %s", exc)
            raise serializers.ValidationError(f"Course creation failed: {str(exc)}")

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update course with module handling"""
        try:
            # Extract modules data
            modules_data = None
            if 'modules_json' in validated_data:
                modules_data = self._coerce_json(validated_data.pop('modules_json'))
            elif 'modules_json_gz' in validated_data:
                validated_data = self._inflate_modules_if_needed(validated_data)
                modules_data = self._coerce_json(validated_data.pop('modules_json', '[]'))

            validated_data.pop('modules_json_gz', None)

            # Handle JSON fields with safe coercion
            for field in ['requirements', 'skills', 'learning_objectives', 'target_audience']:
                if field in validated_data and isinstance(validated_data[field], str):
                    validated_data[field] = self._coerce_json(validated_data[field])

            # Update the course
            course = super().update(instance, validated_data)

            # Process modules if provided
            if modules_data:
                self._update_modules_with_diff(course, modules_data)

            # Clear course caches
            clear_course_caches(course.id)

            return course

        except IntegrityError as exc:
            logger.error("Course update integrity error: %s", exc)
            raise serializers.ValidationError("Course update failed due to data conflict")
        except Exception as exc:
            logger.error("Error in course update: %s", exc)
            raise serializers.ValidationError(f"Course update failed: {str(exc)}")

    def _bulk_create_modules(self, course, modules_list):
        """Create modules and lessons in bulk"""
        try:
            if not isinstance(modules_list, list):
                return

            for order, module_data in enumerate(modules_list, start=1):
                lessons_data = module_data.pop('lessons', [])

                module_data_clean = {k: v for k, v in module_data.items() if k != 'id'}
                module = Module.objects.create(
                    course=course,
                    order=order,
                    **module_data_clean
                )

                # Create lessons
                for lesson_order, lesson_data in enumerate(lessons_data, start=1):
                    resources_data = lesson_data.pop('resources', [])

                    lesson_data_clean = {k: v for k, v in lesson_data.items() if k != 'id'}
                    lesson = Lesson.objects.create(
                        module=module,
                        order=lesson_order,
                        **lesson_data_clean
                    )

                    # Create resources
                    for resource_data in resources_data:
                        resource_data_clean = {k: v for k, v in resource_data.items() if k != 'id'}
                        Resource.objects.create(
                            lesson=lesson,
                            **resource_data_clean
                        )

        except Exception as exc:
            logger.error("Module bulk creation error: %s", exc)
            raise serializers.ValidationError(f"Module creation failed: {str(exc)}")

    def _update_modules_with_diff(self, course, modules_list):
        """Update modules using differential approach"""
        try:
            if not isinstance(modules_list, list):
                return

            existing_module_ids = set(course.modules.values_list('id', flat=True))
            processed_module_ids = set()

            # Process all modules in the list
            for order, module_data in enumerate(modules_list, start=1):
                module_id = module_data.get('id')
                lessons_data = module_data.pop('lessons', [])

                if module_id and not str(module_id).startswith('temp_'):
                    # Update existing module
                    try:
                        module = Module.objects.get(id=module_id, course=course)
                        for attr, value in module_data.items():
                            if attr != 'id':
                                setattr(module, attr, value)
                        module.order = order
                        module.save()
                        processed_module_ids.add(module_id)
                    except Module.DoesNotExist:
                        # Create if doesn't exist
                        module_data_clean = {k: v for k, v in module_data.items() if k != 'id'}
                        module = Module.objects.create(
                            course=course,
                            order=order,
                            **module_data_clean
                        )
                else:
                    # Create new module
                    module_data_clean = {k: v for k, v in module_data.items() if k != 'id'}
                    module = Module.objects.create(
                        course=course,
                        order=order,
                        **module_data_clean
                    )

                # Process lessons for this module
                self._process_lessons_with_diff(module, lessons_data)

            # Delete orphaned modules
            modules_to_delete = existing_module_ids - processed_module_ids
            if modules_to_delete:
                Module.objects.filter(id__in=modules_to_delete).delete()

        except Exception as exc:
            logger.error("Module update error: %s", exc)
            raise serializers.ValidationError(f"Module update failed: {str(exc)}")

    def _process_lessons_with_diff(self, module, lessons_data):
        """Process lessons using differential approach"""
        try:
            if not isinstance(lessons_data, list):
                return

            existing_lesson_ids = set(module.lessons.values_list('id', flat=True))
            processed_lesson_ids = set()

            # Process all lessons in the list
            for order, lesson_data in enumerate(lessons_data, start=1):
                lesson_id = lesson_data.get('id')
                resources_data = lesson_data.pop('resources', [])

                if lesson_id and not str(lesson_id).startswith('temp_'):
                    # Update existing lesson
                    try:
                        lesson = Lesson.objects.get(id=lesson_id, module=module)
                        for attr, value in lesson_data.items():
                            if attr != 'id':
                                setattr(lesson, attr, value)
                        lesson.order = order
                        lesson.save()
                        processed_lesson_ids.add(lesson_id)
                    except Lesson.DoesNotExist:
                        # Create if doesn't exist
                        lesson_data_clean = {k: v for k, v in lesson_data.items() if k != 'id'}
                        lesson = Lesson.objects.create(
                            module=module,
                            order=order,
                            **lesson_data_clean
                        )
                else:
                    # Create new lesson
                    lesson_data_clean = {k: v for k, v in lesson_data.items() if k != 'id'}
                    lesson = Lesson.objects.create(
                        module=module,
                        order=order,
                        **lesson_data_clean
                    )

                # Process resources for this lesson
                self._process_resources_with_diff(lesson, resources_data)

            # Delete orphaned lessons
            lessons_to_delete = existing_lesson_ids - processed_lesson_ids
            if lessons_to_delete:
                Lesson.objects.filter(id__in=lessons_to_delete).delete()

        except Exception as exc:
            logger.error("Lesson processing error: %s", exc)
            raise serializers.ValidationError(f"Lesson processing failed: {str(exc)}")

    def _process_resources_with_diff(self, lesson, resources_data):
        """Process resources using differential approach"""
        try:
            if not isinstance(resources_data, list):
                return

            existing_resource_ids = set(lesson.resources.values_list('id', flat=True))
            processed_resource_ids = set()

            # Process all resources in the list
            for resource_data in resources_data:
                resource_id = resource_data.get('id')

                if resource_id and not str(resource_id).startswith('temp_'):
                    # Update existing resource
                    try:
                        resource = Resource.objects.get(id=resource_id, lesson=lesson)
                        for attr, value in resource_data.items():
                            if attr != 'id':
                                setattr(resource, attr, value)
                        resource.save()
                        processed_resource_ids.add(resource_id)
                    except Resource.DoesNotExist:
                        # Create if doesn't exist
                        resource_data_clean = {k: v for k, v in resource_data.items() if k != 'id'}
                        Resource.objects.create(
                            lesson=lesson,
                            **resource_data_clean
                        )
                else:
                    # Create new resource
                    resource_data_clean = {k: v for k, v in resource_data.items() if k != 'id'}
                    Resource.objects.create(
                        lesson=lesson,
                        **resource_data_clean
                    )

            # Delete orphaned resources
            resources_to_delete = existing_resource_ids - processed_resource_ids
            if resources_to_delete:
                Resource.objects.filter(id__in=resources_to_delete).delete()

        except Exception as exc:
            logger.error("Resource processing error: %s", exc)
            # Don't throw exception for resource failures - log and continue
            pass


# Export serializers for import in views
__all__ = [
    'InstructorProfileSerializer',
    'CourseInstructorSerializer',
    'InstructorDashboardSerializer',
    'InstructorCourseSerializer',
    'InstructorModuleSerializer',
    'InstructorLessonSerializer',
    'InstructorResourceSerializer',
    'CourseCreationSessionSerializer',
    'CourseTemplateSerializer',
    'DraftCourseContentSerializer',
    'CourseContentDraftSerializer',
    'DraftCoursePublishSerializer',
]

logger.info("Instructor Portal Serializers loaded successfully")
