#
# File Path: instructor_portal/serializers/course_management.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 13:35:44
# Date Revised: 2025-06-30 10:05:06
# Current Date and Time (UTC): 2025-06-30 10:05:06
# Current User's Login: cadsanthanamNew
# Author: softTechSolutions2001
# Last Modified By: cadsanthanamNew
# Last Modified: 2025-06-30 10:05:06 UTC
# User: cadsanthanamNew
# Version: 1.0.3
#
# Course management serializers for instructor_portal
# Split from original serializers.py maintaining exact code compatibility

import logging
from decimal import Decimal
from django.db import transaction, IntegrityError, models
from django.utils import timezone
from rest_framework import serializers

from courses.constants import (
    ACCESS_LEVEL_CHOICES, LESSON_TYPE_CHOICES, RESOURCE_TYPE_CHOICES,
    LEVEL_CHOICES, CREATION_METHODS, COMPLETION_STATUSES
)
from courses.models import (
    Course, Module, Lesson, Resource, Category,
    Enrollment, Review, CourseProgress, Progress as LessonProgress
)
from courses.validators import validate_video_url, validate_price_range
from courses.utils import clear_course_caches

from ..models import InstructorProfile, CourseInstructor
from .mixins import JsonFieldMixin
from .utils import safe_decimal_conversion, validate_file_path_security
from .profile import InstructorProfileSerializer

logger = logging.getLogger(__name__)

# Constants for validation
VALID_ACCESS_LEVELS = [choice[0] for choice in ACCESS_LEVEL_CHOICES]
VALID_LESSON_TYPES = [choice[0] for choice in LESSON_TYPE_CHOICES]
VALID_RESOURCE_TYPES = [choice[0] for choice in RESOURCE_TYPE_CHOICES]
VALID_LEVELS = [choice[0] for choice in LEVEL_CHOICES]
VALID_CREATION_METHODS = [choice[0] for choice in CREATION_METHODS]
VALID_COMPLETION_STATUSES = [choice[0] for choice in COMPLETION_STATUSES]

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

class InstructorResourceSerializer(serializers.ModelSerializer):
    """Serializer for instructor resources"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)
    upload_info = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'type', 'file', 'url', 'description', 'premium',
            'storage_key', 'uploaded', 'file_size', 'mime_type', 'created_date', 'updated_date', 'file_size_display', 'duration_display',
            'order', 'duration_minutes',
            'lesson_title', 'course_title', 'upload_info'
        ]
        read_only_fields = ['id', 'uploaded']

    def get_upload_info(self, obj):
        """Get upload information and status"""
        try:
            return {
                'has_file': bool(obj.file or obj.storage_key),
                'file_size_mb': round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0,
                'is_secure': validate_file_path_security(str(obj.file)) if obj.file else True,
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

            # Filter out None IDs to avoid NULL join warnings
            lesson_ids = list(filter(None, lesson_ids))

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

    # Re-added fields for backward compatibility
    creation_method = serializers.CharField(required=False)
    completion_status = serializers.CharField(required=False)
    completion_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, read_only=True)
    version = serializers.IntegerField(read_only=True)
    # FIXED: Remove queryset for read-only field
    parent_version = serializers.PrimaryKeyRelatedField(read_only=True)

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
            lesson_ids = list(filter(None, obj.modules.values_list('lessons__id', flat=True)))
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
            lesson_ids = list(filter(None, obj.modules.values_list('lessons__id', flat=True)))
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

    def validate_creation_method(self, value):
        """Validate creation method"""
        if value and value not in VALID_CREATION_METHODS:
            raise serializers.ValidationError(f"Invalid creation method. Must be one of: {', '.join(VALID_CREATION_METHODS)}")
        return value

    def validate_completion_status(self, value):
        """Validate completion status"""
        if value and value not in VALID_COMPLETION_STATUSES:
            raise serializers.ValidationError(f"Invalid completion status. Must be one of: {', '.join(VALID_COMPLETION_STATUSES)}")
        return value

    def validate_price(self, value):
        """Enhanced price validation with decimal conversion"""
        if value is not None:
            try:
                decimal_value = safe_decimal_conversion(value, raise_validation_error=True)
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
                # Updated to use analytics property
                if hasattr(request.instructor_profile, 'analytics'):
                    request.instructor_profile.analytics.update_analytics()

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

                try:
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
                except Exception as exc:
                    # Be consistent with module/lesson error handling by logging and raising
                    logger.error("Resource processing error: %s", exc)
                    raise serializers.ValidationError(f"Resource processing failed: {str(exc)}")

            # Delete orphaned resources
            resources_to_delete = existing_resource_ids - processed_resource_ids
            if resources_to_delete:
                Resource.objects.filter(id__in=resources_to_delete).delete()

        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as exc:
            # Log other errors but don't fail the entire operation
            logger.error("Resource processing error: %s", exc)
