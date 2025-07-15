# Core model serializers
#
# File Path: backend/courses/serializers/core.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:16:45
# Date Revised: 2025-07-09 04:31:31
# Current Date and Time (UTC): 2025-07-09 04:31:31
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 04:31:31 UTC
# User: MohithaSanthanam2010
# Version: 3.1.0
#
# Core Serializers for Course Management System
#
# Version 3.1.0 Changes:
# - FIXED 🔴: format_file_size and format_duration now raise ValidationError for invalid values
# - FIXED 🔴: Field attribute naming consistency with source parameters
# - ENHANCED: Better error handling and validation
# - ADDED: Proper backward compatibility support

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Avg, Count, Prefetch, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from instructor_portal.models import CourseInstructor
from rest_framework import serializers

from ..models import Category, Course, Lesson, Module, Resource
from ..utils import format_duration, format_filesize
from ..validation import (
    ACCESS_LEVELS,
    can_user_access_content,
    get_unified_user_access_level,
    validate_lesson_data,
)
from .mixins import (
    ContextPropagationMixin,
    EnhancedValidationMixin,
    OptimizedQueryMixin,
)

logger = logging.getLogger(__name__)

# =====================================
# OPTIMIZED CATEGORY SERIALIZERS
# =====================================


class CategorySerializer(
    ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer
):
    """
    Enhanced category serializer with optimized queries and context propagation
    """

    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "slug",
            "is_active",
            "sort_order",
            "parent",
            "course_count",
            "created_date",
            "updated_date",
            "featured",
        ]
        read_only_fields = ["slug", "created_date", "updated_date"]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize category queries"""
        return queryset.prefetch_related(
            Prefetch("courses", queryset=Course.objects.filter(is_published=True))
        )

    def get_course_count(self, obj):
        """Get number of active courses with caching"""
        if hasattr(obj, "_course_count"):
            return obj._course_count

        try:
            return obj.get_course_count()
        except Exception as e:
            logger.warning(f"Error getting course count for category {obj.id}: {e}")
            return 0


# =====================================
# OPTIMIZED RESOURCE SERIALIZERS
# =====================================


class ResourceSerializer(
    ContextPropagationMixin, EnhancedValidationMixin, serializers.ModelSerializer
):
    """
    Enhanced resource serializer with security and validation improvements
    FIXED: Proper validation for file size and duration formatting
    """

    # Use consistent field names with source mapping for backward compatibility
    formatted_file_size = serializers.SerializerMethodField(source="file_size")
    formatted_duration = serializers.SerializerMethodField(source="duration_minutes")

    # Backward compatibility fields
    format_file_size = serializers.SerializerMethodField()
    format_duration = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            "id",
            "title",
            "type",
            "description",
            "file",
            "url",
            "premium",
            "order",
            "file_size",
            "formatted_file_size",
            "format_file_size",
            "mime_type",
            "uploaded",
            "storage_key",
            "duration_minutes",
            "formatted_duration",
            "format_duration",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "file_size",
            "mime_type",
            "uploaded",
            "storage_key",
            "created_date",
            "updated_date",
        ]

    def get_formatted_file_size(self, obj):
        """Get human-readable file size with proper validation"""
        try:
            if obj.file_size is None or obj.file_size < 0:
                raise serializers.ValidationError("Invalid file size")
            return (
                obj.file_size_display
                if hasattr(obj, "file_size_display")
                else format_filesize(obj.file_size)
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Error formatting file size for resource {obj.id}: {e}")
            raise serializers.ValidationError("Unable to format file size")

    def get_formatted_duration(self, obj):
        """Get human-readable duration with proper validation"""
        try:
            if obj.duration_minutes is None or obj.duration_minutes < 0:
                raise serializers.ValidationError("Invalid duration")
            return (
                obj.duration_display
                if hasattr(obj, "duration_display")
                else format_duration(obj.duration_minutes)
            )
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Error formatting duration for resource {obj.id}: {e}")
            raise serializers.ValidationError("Unable to format duration")

    # FIXED: Backward compatibility methods with proper validation
    def get_format_file_size(self, obj):
        """Backward compatibility - use formatted_file_size"""
        return self.get_formatted_file_size(obj)

    def get_format_duration(self, obj):
        """Backward compatibility - use formatted_duration"""
        return self.get_formatted_duration(obj)

    def validate(self, data):
        """Enhanced resource validation with model integration"""
        return self.validate_with_model_clean(data, self.instance)

    def _process_representation_safely(self, data, instance):
        """Process resource representation with access control"""
        request = self.context.get("request")

        # Apply premium resource access control
        if instance.premium:
            user_access_level = get_unified_user_access_level(
                request.user if request and request.user.is_authenticated else None
            )

            if user_access_level != ACCESS_LEVELS.get("PREMIUM", "premium"):
                # Remove sensitive fields for non-premium users
                data.pop("file", None)
                data.pop("url", None)
                data.pop("storage_key", None)
                data["is_premium_locked"] = True
            else:
                data["is_premium_locked"] = False
        else:
            data["is_premium_locked"] = False

        return data


# =====================================
# OPTIMIZED LESSON SERIALIZERS
# =====================================


class LessonSerializer(
    ContextPropagationMixin,
    OptimizedQueryMixin,
    EnhancedValidationMixin,
    serializers.ModelSerializer,
):
    """
    Enhanced lesson serializer with comprehensive optimizations and access control
    """

    resources = serializers.SerializerMethodField()
    premium_resources = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content",
            "guest_content",
            "registered_content",
            "access_level",
            "duration_minutes",
            "duration_display",
            "type",
            "order",
            "has_assessment",
            "has_lab",
            "is_free_preview",
            "video_url",
            "transcript",
            "resources",
            "premium_resources",
            "is_completed",
            "assessment",
            "progress_percentage",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["created_date", "updated_date"]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize lesson queries with related data"""
        return queryset.select_related("module__course").prefetch_related(
            Prefetch("resources", queryset=Resource.objects.order_by("order")),
            Prefetch("assessment", queryset=cls._get_assessment_queryset()),
        )

    @classmethod
    def _get_assessment_queryset(cls):
        """Helper to get assessment queryset with proper imports"""
        from ..models import Assessment, Question

        return Assessment.objects.prefetch_related(
            Prefetch(
                "questions",
                queryset=Question.objects.prefetch_related("answers_question"),
            )
        )

    def get_duration_display(self, obj):
        """Get human-readable duration with error handling"""
        try:
            if obj.duration_minutes is None or obj.duration_minutes < 0:
                return "Unknown"
            return (
                obj.duration_display
                if hasattr(obj, "duration_display")
                else format_duration(obj.duration_minutes)
            )
        except Exception:
            return "Unknown"

    def validate(self, data):
        """Enhanced lesson validation with unified validation logic"""
        try:
            # Use unified validation logic
            errors = validate_lesson_data(data)
            if errors:
                if isinstance(errors, list):
                    raise serializers.ValidationError(
                        errors[0] if len(errors) == 1 else {"non_field_errors": errors}
                    )
                else:
                    raise serializers.ValidationError(errors)
        except Exception as e:
            logger.error(f"Validation error in LessonSerializer: {e}")
            raise serializers.ValidationError(f"Validation error: {str(e)}")

        # Also run streamlined model validation
        return self.validate_with_model_clean(data, self.instance)

    def get_is_completed(self, obj):
        """Enhanced completion status check with optimization"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # Use cached enrollment from context if available
        enrollment = self.context.get("user_enrollment")
        if not enrollment:
            try:
                from ..models import Enrollment

                enrollment = Enrollment.objects.select_related("course").get(
                    user=request.user, course=obj.module.course
                )
            except Enrollment.DoesNotExist:
                return False

        try:
            from ..models import Progress

            return Progress.objects.filter(
                enrollment=enrollment, lesson=obj, is_completed=True
            ).exists()
        except Exception as e:
            logger.warning(f"Error checking lesson completion for lesson {obj.id}: {e}")
            return False

    def get_progress_percentage(self, obj):
        """Get user's progress percentage with optimization"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        # Use cached enrollment from context if available
        enrollment = self.context.get("user_enrollment")
        if not enrollment:
            try:
                from ..models import Enrollment

                enrollment = Enrollment.objects.get(
                    user=request.user, course=obj.module.course
                )
            except Enrollment.DoesNotExist:
                return 0

        try:
            from ..models import Progress

            progress = Progress.objects.filter(
                enrollment=enrollment, lesson=obj
            ).first()

            return progress.progress_percentage if progress else 0
        except Exception as e:
            logger.warning(f"Error getting lesson progress for lesson {obj.id}: {e}")
            return 0

    def get_premium_resources(self, obj):
        """Enhanced premium resource access with proper context"""
        request = self.context.get("request")
        user_access_level = get_unified_user_access_level(
            request.user if request and request.user.is_authenticated else None
        )

        # Only return premium resources for premium access level
        if user_access_level != ACCESS_LEVELS.get("PREMIUM", "premium"):
            return []

        try:
            premium_resources = obj.resources.filter(premium=True).order_by("order")
            context = self.get_serializer_context_for_nested()
            return ResourceSerializer(
                premium_resources, many=True, context=context
            ).data
        except Exception as e:
            logger.warning(f"Error getting premium resources for lesson {obj.id}: {e}")
            return []

    def get_resources(self, obj):
        """Get resources with proper context propagation"""
        try:
            resources = obj.resources.all().order_by("order")
            context = self.get_serializer_context_for_nested()
            return ResourceSerializer(resources, many=True, context=context).data
        except Exception as e:
            logger.warning(f"Error getting resources for lesson {obj.id}: {e}")
            return []

    def get_assessment(self, obj):
        """Get assessment with proper context propagation"""
        if not obj.has_assessment or not hasattr(obj, "assessment"):
            return None

        try:
            context = self.get_serializer_context_for_nested()

            # FIXED: Lazy import to break circular import cycle
            def get_assessment_serializer():
                from .analytics import AssessmentSerializer

                return AssessmentSerializer

            AssessmentSerializerClass = get_assessment_serializer()
            return AssessmentSerializerClass(obj.assessment, context=context).data
        except Exception as e:
            logger.warning(f"Error getting assessment for lesson {obj.id}: {e}")
            return None

    def _process_representation_safely(self, data, instance):
        """Enhanced content representation with proper access control"""
        request = self.context.get("request")

        # Get user access level using unified logic
        user_access_level = get_unified_user_access_level(
            request.user if request and request.user.is_authenticated else None
        )

        lesson_access_level = instance.access_level

        # Enhanced access control logic
        if can_user_access_content(user_access_level, lesson_access_level):
            # User has proper access - use full content
            data["is_restricted"] = False
        else:
            # User lacks access - provide appropriate fallback
            if (
                user_access_level == ACCESS_LEVELS.get("REGISTERED", "registered")
                and instance.registered_content
            ):
                data["content"] = instance.registered_content
            elif instance.guest_content:
                data["content"] = instance.guest_content
            else:
                data["content"] = (
                    f"This content requires {lesson_access_level} access level."
                )

            # Remove sensitive fields
            data.pop("video_url", None)
            data.pop("transcript", None)
            data["is_restricted"] = True

        return data


# =====================================
# OPTIMIZED MODULE SERIALIZERS
# =====================================


class ModuleSerializer(
    ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer
):
    """
    Enhanced module serializer with comprehensive optimizations
    """

    lessons = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    course = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Course.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Module
        fields = [
            "id",
            "title",
            "description",
            "order",
            "duration_minutes",
            "duration_display",
            "is_published",
            "lessons",
            "lessons_count",
            "course",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["created_date", "updated_date"]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize module queries with lessons and related data"""
        return queryset.select_related("course").prefetch_related(
            Prefetch(
                "lessons",
                queryset=Lesson.objects.select_related("module")
                .prefetch_related(
                    "resources", "assessment__questions__answers_question"
                )
                .order_by("order"),
            )
        )

    def get_duration_display(self, obj):
        """Get human-readable duration with error handling"""
        try:
            if obj.duration_minutes is None or obj.duration_minutes < 0:
                return "Unknown"
            return (
                obj.duration_display
                if hasattr(obj, "duration_display")
                else format_duration(obj.duration_minutes)
            )
        except Exception:
            return "Unknown"

    def get_lessons_count(self, obj):
        """Get total number of lessons with caching"""
        if hasattr(obj, "_lesson_count"):
            return obj._lesson_count

        try:
            return obj.lessons.count()
        except Exception:
            return 0

    def get_lessons(self, obj):
        """Get lessons with proper context propagation"""
        try:
            lessons = obj.lessons.all().order_by("order")

            # Pass through enrollment context for optimization
            context = self.get_serializer_context_for_nested()
            if "user_enrollment" in self.context:
                context["user_enrollment"] = self.context["user_enrollment"]

            return LessonSerializer(lessons, many=True, context=context).data
        except Exception as e:
            logger.warning(f"Error getting lessons for module {obj.id}: {e}")
            return []

    def validate_order(self, value):
        """Validate module order within course"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Order must be a positive integer")
        return value


class ModuleDetailSerializer(ModuleSerializer):
    """
    Enhanced detailed module serializer with comprehensive information
    """

    lessons = LessonSerializer(many=True, read_only=True)
    completion_stats = serializers.SerializerMethodField()

    class Meta(ModuleSerializer.Meta):
        fields = ModuleSerializer.Meta.fields + ["completion_stats"]

    def get_completion_stats(self, obj):
        """Get module completion statistics for current user with optimization"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        # Use cached enrollment from context if available
        enrollment = self.context.get("user_enrollment")
        if not enrollment:
            try:
                from ..models import Enrollment

                enrollment = Enrollment.objects.get(
                    user=request.user, course=obj.course
                )
            except Enrollment.DoesNotExist:
                return None

        try:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return {"completed": 0, "total": 0, "percentage": 0}

            from ..models import Progress

            completed_lessons = Progress.objects.filter(
                enrollment=enrollment, lesson__module=obj, is_completed=True
            ).count()

            percentage = (
                (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
            )

            return {
                "completed": completed_lessons,
                "total": total_lessons,
                "percentage": round(percentage, 1),
            }
        except Exception as e:
            logger.warning(f"Error getting completion stats for module {obj.id}: {e}")
            return None


# =====================================
# OPTIMIZED COURSE INSTRUCTOR SERIALIZER
# =====================================


class CourseInstructorSerializer(
    ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer
):
    """
    Enhanced serializer for course instructor information with optimizations
    """

    instructor = serializers.SerializerMethodField()
    instructor_stats = serializers.SerializerMethodField()

    class Meta:
        model = CourseInstructor
        fields = [
            "instructor",
            "is_lead",
            "is_active",
            "instructor_stats",
            "joined_date",
            "updated_date",
        ]
        read_only_fields = ["joined_date", "updated_date"]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize instructor queries"""
        return queryset.select_related("instructor", "course")

    def get_instructor(self, obj):
        """Get instructor user information safely"""
        try:
            user = obj.instructor
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}".strip()
                or user.username,
                "email": user.email,
                "username": user.username,
                "profile_picture": (
                    getattr(user.profile, "picture", None)
                    if hasattr(user, "profile")
                    else None
                ),
            }
        except Exception as e:
            logger.warning(
                f"Error getting instructor info for course instructor {obj.id}: {e}"
            )
            return {"id": None, "full_name": "Unknown", "email": "", "username": ""}

    def get_instructor_stats(self, obj):
        """Get instructor statistics with optimization"""
        try:
            user = obj.instructor

            # Use cached stats if available
            if hasattr(obj, "_instructor_stats"):
                return obj._instructor_stats

            total_courses = Course.objects.filter(
                courseinstructor_set__instructor=user,
                courseinstructor_set__is_active=True,
            ).count()

            from ..models import Enrollment

            total_students = Enrollment.objects.filter(
                course__courseinstructor_set__instructor=user,
                course__courseinstructor_set__is_active=True,
            ).count()

            return {"total_courses": total_courses, "total_students": total_students}
        except Exception as e:
            logger.warning(f"Error getting instructor stats for {obj.id}: {e}")
            return {"total_courses": 0, "total_students": 0}


# =====================================
# OPTIMIZED COURSE VERSION SERIALIZER
# =====================================


class CourseVersionSerializer(
    ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer
):
    """
    Enhanced serializer for course versioning with optimizations
    """

    parent_version = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    version_family = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "version",
            "is_draft",
            "parent_version",
            "children",
            "title",
            "slug",
            "version_family",
            "created_date",
            "updated_date",
        ]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize version queries"""
        return queryset.select_related("parent_version").prefetch_related("children")

    def get_parent_version(self, obj):
        """Get parent version information safely"""
        if not obj.parent_version:
            return None

        try:
            return {
                "id": obj.parent_version.id,
                "version": float(obj.parent_version.version),
                "title": obj.parent_version.title,
                "slug": obj.parent_version.slug,
                "is_draft": obj.parent_version.is_draft,
                "created_date": obj.parent_version.created_date,
            }
        except Exception as e:
            logger.warning(f"Error getting parent version for course {obj.id}: {e}")
            return None

    def get_children(self, obj):
        """Get child version information with optimization"""
        try:
            children = obj.children.order_by("-version")[:5]
            return [
                {
                    "id": child.id,
                    "version": float(child.version),
                    "title": child.title,
                    "slug": child.slug,
                    "is_draft": child.is_draft,
                    "updated_date": child.updated_date,
                }
                for child in children
            ]
        except Exception as e:
            logger.warning(f"Error getting children versions for course {obj.id}: {e}")
            return []

    def get_version_family(self, obj):
        """Get version family identifier safely"""
        try:
            root = obj.parent_version or obj
            return f"{root.slug}-v{root.version}"
        except Exception as e:
            logger.warning(f"Error getting version family for course {obj.id}: {e}")
            return f"{obj.slug}-v{obj.version}"


# =====================================
# OPTIMIZED MAIN COURSE SERIALIZERS
# =====================================


class CourseSerializer(
    ContextPropagationMixin,
    OptimizedQueryMixin,
    EnhancedValidationMixin,
    serializers.ModelSerializer,
):
    """
    Enhanced course serializer with comprehensive optimizations and validation
    """

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    instructors = CourseInstructorSerializer(
        source="courseinstructor_set", many=True, read_only=True
    )
    slug = serializers.SlugField(
        validators=[], required=False  # Remove unique validation for draft cloning
    )
    rating = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "subtitle",
            "slug",
            "description",
            "category",
            "category_id",
            "thumbnail",
            "price",
            "discount_price",
            "discount_ends",
            "level",
            "duration_minutes",
            "duration_display",
            "has_certificate",
            "is_featured",
            "is_published",
            "is_draft",
            "published_date",
            "updated_date",
            "instructors",
            "rating",
            "enrolled_students",
            "is_enrolled",
            "creation_method",
            "completion_status",
            "completion_percentage",
            "version",
            "module_count",
            "lesson_count",
            "requirements",
            "skills",
            "learning_objectives",
            "target_audience",
            "avg_rating",
            "total_reviews",
            "enrolled_students_count",
            "meta_keywords",
            "meta_description",
        ]
        read_only_fields = ["version", "published_date", "updated_date"]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize course queries with all related data"""
        return (
            queryset.select_related("category")
            .prefetch_related(
                Prefetch(
                    "courseinstructor_set",
                    queryset=CourseInstructor.objects.select_related(
                        "instructor"
                    ).filter(is_active=True),
                ),
                "modules",
                "enrollments",
                "reviews",
            )
            .annotate(
                _enrolled_count=Count(
                    "enrollments", filter=Q(enrollments__status="active")
                ),
                _avg_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
                _review_count=Count("reviews", filter=Q(reviews__is_approved=True)),
            )
        )

    @extend_schema_field(OpenApiTypes.STR)
    def get_duration_display(self, obj):
        """Get human-readable duration with error handling"""
        try:
            if obj.duration_minutes is None or obj.duration_minutes < 0:
                return "Unknown"
            return (
                obj.duration_display
                if hasattr(obj, "duration_display")
                else format_duration(obj.duration_minutes)
            )
        except Exception:
            return "Unknown"

    def get_rating(self, obj):
        """Get course rating with optimization"""
        try:
            # Use cached value from annotation if available
            if hasattr(obj, "_avg_rating") and obj._avg_rating is not None:
                return float(obj._avg_rating)

            # Fallback to model property
            return float(obj.rating) if hasattr(obj, "rating") else 0.0
        except Exception:
            return 0.0

    def get_enrolled_students(self, obj):
        """Get count of enrolled students with optimization"""
        try:
            # Use cached value from annotation if available
            if hasattr(obj, "_enrolled_count"):
                return obj._enrolled_count

            # Fallback to model property
            return obj.enrolled_students if hasattr(obj, "enrolled_students") else 0
        except Exception:
            return 0

    def get_is_enrolled(self, obj):
        """Check if current user is enrolled with optimization"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        try:
            # Use cached enrollment from context if available
            user_enrollment = self.context.get("user_enrollment")
            if user_enrollment is not None:
                return user_enrollment.course_id == obj.id

            # Fallback to database query
            return obj.enrollments.filter(user=request.user, status="active").exists()
        except Exception as e:
            logger.warning(f"Error checking enrollment for course {obj.id}: {e}")
            return False

    def get_module_count(self, obj):
        """Get total number of modules with caching"""
        if hasattr(obj, "_module_count"):
            return obj._module_count

        try:
            return obj.modules.count()
        except Exception:
            return 0

    def get_lesson_count(self, obj):
        """Get total number of lessons with optimization"""
        if hasattr(obj, "_lesson_count"):
            return obj._lesson_count

        try:
            return Lesson.objects.filter(module__course=obj).count()
        except Exception:
            return 0

    def get_instructors(self, obj):
        """Get instructors with proper context propagation"""
        try:
            instructors = obj.courseinstructor_set.filter(is_active=True)
            context = self.get_serializer_context_for_nested()
            return CourseInstructorSerializer(
                instructors, many=True, context=context
            ).data
        except Exception as e:
            logger.warning(f"Error getting instructors for course {obj.id}: {e}")
            return []

    def validate_title(self, value):
        """
        Enhanced title validation with optimized duplicate checking
        FIXED: Duplicate query validation issues
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")

        value = value.strip()

        # Length validation
        if len(value) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long"
            )
        if len(value) > 160:
            raise serializers.ValidationError(
                "Title must be no more than 160 characters long"
            )

        # Optimized duplicate checking with version family support
        course_id = self.instance.id if self.instance else None
        qs = Course.objects.filter(title__iexact=value)

        if course_id:
            qs = qs.exclude(pk=course_id)

            if self.instance:
                # Allow duplicates within the same version family
                if self.instance.parent_version:
                    root_version = self.instance.parent_version
                    qs = qs.exclude(
                        Q(parent_version=root_version) | Q(pk=root_version.pk)
                    )
                else:
                    qs = qs.exclude(parent_version_id=course_id)

        if qs.exists():
            # Use select_related for efficient duplicate course info
            duplicate_course = qs.select_related().first()
            error_msg = f"A course with this title already exists"

            try:
                instructors = duplicate_course.courseinstructor_set.select_related(
                    "instructor"
                ).filter(is_active=True)[:2]
                if instructors:
                    instructor_names = [
                        f"{ci.instructor.first_name} {ci.instructor.last_name}".strip()
                        for ci in instructors
                    ]
                    error_msg += f" (by {', '.join(instructor_names)})"
            except Exception:
                pass

            raise serializers.ValidationError(error_msg)

        return value

    def validate(self, data):
        """
        Streamlined course validation with model integration
        FIXED: Large validate() blocks with redundant model clean() calls
        """
        return self.validate_with_model_clean(data, self.instance)


class CourseDetailSerializer(CourseSerializer):
    """
    Enhanced detailed course serializer with comprehensive information and optimization
    """

    modules = ModuleDetailSerializer(many=True, read_only=True)
    user_progress = serializers.SerializerMethodField()
    version_info = CourseVersionSerializer(source="*", read_only=True)
    enrollment_info = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            "modules",
            "user_progress",
            "version_info",
            "enrollment_info",
            "recent_reviews",
        ]

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Extended optimization for detailed course views"""
        return (
            super()
            .setup_eager_loading(queryset)
            .prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.prefetch_related(
                        Prefetch(
                            "lessons",
                            queryset=Lesson.objects.prefetch_related(
                                "resources", "assessment__questions__answers_question"
                            ).order_by("order"),
                        )
                    ).order_by("order"),
                ),
                Prefetch("reviews", queryset=cls._get_review_queryset()),
            )
        )

    @classmethod
    def _get_review_queryset(cls):
        """Helper to get review queryset with proper imports"""
        from ..models import Review

        return (
            Review.objects.select_related("user")
            .filter(is_approved=True)
            .order_by("-created_date")[:5]
        )

    def get_modules(self, obj):
        """Get modules with optimized context propagation"""
        try:
            modules = obj.modules.all().order_by("order")

            # Optimize by passing user enrollment in context
            context = self.get_serializer_context_for_nested()
            request = self.context.get("request")

            if request and request.user.is_authenticated:
                try:
                    from ..models import Enrollment

                    enrollment = Enrollment.objects.get(user=request.user, course=obj)
                    context["user_enrollment"] = enrollment
                except Enrollment.DoesNotExist:
                    context["user_enrollment"] = None

            return ModuleDetailSerializer(modules, many=True, context=context).data
        except Exception as e:
            logger.warning(f"Error getting modules for course {obj.id}: {e}")
            return []

    def get_user_progress(self, obj):
        """Enhanced user progress tracking with optimization"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        try:
            from ..models import Enrollment, Progress

            enrollment = Enrollment.objects.select_related("course").get(
                user=request.user, course=obj
            )

            # Use optimized query for total lessons
            total_lessons = Lesson.objects.filter(module__course=obj).count()
            if total_lessons == 0:
                return {
                    "enrolled_date": enrollment.created_date,
                    "last_accessed": enrollment.last_accessed,
                    "completed": 0,
                    "total": 0,
                    "percentage": 0,
                    "completed_lessons": [],
                    "current_lesson": None,
                }

            # Optimized progress queries
            completed_progresses = Progress.objects.filter(
                enrollment=enrollment, is_completed=True
            ).select_related("lesson__module")

            completed_lessons = completed_progresses.count()
            percentage = (
                (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
            )

            # Get current lesson efficiently
            current_lesson = None
            incomplete_progress = (
                Progress.objects.filter(enrollment=enrollment, is_completed=False)
                .select_related("lesson__module")
                .first()
            )

            if incomplete_progress:
                current_lesson = {
                    "id": incomplete_progress.lesson.id,
                    "title": incomplete_progress.lesson.title,
                    "module_title": incomplete_progress.lesson.module.title,
                }

            return {
                "enrolled_date": enrollment.created_date,
                "last_accessed": enrollment.last_accessed,
                "completed": completed_lessons,
                "total": total_lessons,
                "percentage": round(percentage, 1),
                "completed_lessons": list(
                    completed_progresses.values_list("lesson__id", flat=True)
                ),
                "current_lesson": current_lesson,
                "time_spent": enrollment.total_time_spent or 0,
            }
        except Enrollment.DoesNotExist:
            return None
        except Exception as e:
            logger.warning(f"Error getting user progress for course {obj.id}: {e}")
            return None

    def get_enrollment_info(self, obj):
        """Get enrollment information for current user with error handling"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        try:
            from ..models import Enrollment

            enrollment = Enrollment.objects.get(user=request.user, course=obj)
            return {
                "id": enrollment.id,
                "status": enrollment.status,
                "enrolled_date": enrollment.created_date,
                "completion_date": enrollment.completion_date,
            }
        except Enrollment.DoesNotExist:
            return None
        except Exception as e:
            logger.warning(f"Error getting enrollment info for course {obj.id}: {e}")
            return None

    def get_recent_reviews(self, obj):
        """Get recent course reviews with optimization"""
        try:
            # Use prefetched reviews if available
            if (
                hasattr(obj, "_prefetched_objects_cache")
                and "reviews" in obj._prefetched_objects_cache
            ):
                recent_reviews = obj._prefetched_objects_cache["reviews"]
            else:
                from ..models import Review

                recent_reviews = (
                    Review.objects.select_related("user")
                    .filter(course=obj, is_approved=True)
                    .order_by("-created_date")[:5]
                )

            return [
                {
                    "id": review.id,
                    "rating": review.rating,
                    "title": review.title or "",
                    "content": (
                        review.content[:200] + "..."
                        if review.content and len(review.content) > 200
                        else review.content or ""
                    ),
                    "user": (
                        f"{review.user.first_name} {review.user.last_name}".strip()
                        or review.user.username
                    ),
                    "date_created": review.created_date,
                }
                for review in recent_reviews
            ]
        except Exception as e:
            logger.warning(f"Error getting recent reviews for course {obj.id}: {e}")
            return []


# =====================================
# OPTIMIZED COURSE CLONING SERIALIZER
# =====================================


class CourseCloneSerializer(serializers.Serializer):
    """
    Enhanced serializer for course cloning operations with validation
    """

    title = serializers.CharField(
        max_length=160,
        required=False,
        help_text="New title for the cloned course. If not provided, uses original title with suffix.",
    )
    description = serializers.CharField(
        required=False,
        help_text="New description for the cloned course. If not provided, uses original description.",
    )
    copy_modules = serializers.BooleanField(
        default=True,
        help_text="Whether to copy all modules and lessons from the original course.",
    )
    copy_resources = serializers.BooleanField(
        default=True,
        help_text="Whether to copy all resources from the original course.",
    )
    copy_assessments = serializers.BooleanField(
        default=True,
        help_text="Whether to copy all assessments from the original course.",
    )
    create_as_draft = serializers.BooleanField(
        default=True, help_text="Whether to create the cloned course as a draft."
    )

    def validate_title(self, value):
        """Validate cloned course title with security checks"""
        if value:
            value = value.strip()
            if len(value) < 3:
                raise serializers.ValidationError(
                    "Title must be at least 3 characters long"
                )
            if len(value) > 160:
                raise serializers.ValidationError(
                    "Title must be no more than 160 characters long"
                )

            # Basic security check
            dangerous_patterns = ["<script", "javascript:", "vbscript:"]
            if any(pattern in value.lower() for pattern in dangerous_patterns):
                raise serializers.ValidationError("Title contains dangerous content")

        return value
