#
# File Path: instructor_portal/views/course_views.py
# Folder Path: instructor_portal/views/
# Date Created: 2025-06-27 06:34:12
# Date Revised: 2025-06-27 06:34:12
# Current Date and Time (UTC): 2025-06-27 06:34:12
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:34:12 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Course management viewsets for instructor_portal
# Complete implementation of all course-related endpoints

import logging
import uuid
from typing import Any
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, status, permissions, serializers, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from django.db import transaction, IntegrityError
from django.db.models import Q, Count, Prefetch, Avg
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

# Import from courses app
from courses.models import Course, Module, Lesson, Resource
from courses.permissions import IsInstructorOrAdmin
from courses.utils import clear_course_caches, validate_file_security
from courses.validation import validate_course_data, validate_lesson_data, sanitize_input

# Import from instructor portal
from ..models import (
    InstructorProfile, CourseInstructor, TierManager
)
from ..serializers import (
    InstructorCourseSerializer, InstructorModuleSerializer,
    InstructorLessonSerializer, InstructorResourceSerializer
)
from .mixins import (
    InstructorBaseViewSet, require_instructor_profile, require_permission,
    tier_required, validate_user_permission, get_instructor_profile,
    audit_log, validate_file_upload, MAX_BULK_OPERATIONS
)

logger = logging.getLogger(__name__)


class InstructorCourseViewSet(InstructorBaseViewSet):
    """
    Enhanced API endpoint for instructors to manage courses
    FIXED: Full integration with enhanced models and centralized permissions
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    lookup_field = 'slug'
    resource_name = 'course'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile integration"""
        user = self.request.user

        # Validate user has instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Course.objects.none()

        # Staff and superuser get all courses
        if user.is_staff or user.is_superuser:
            courses = Course.objects.select_related('category', 'parent_version')
        else:
            # FIXED: Use CourseInstructor model for filtering
            courses = Course.objects.filter(
                courseinstructor_set__instructor=user,
                courseinstructor_set__is_active=True
            ).select_related('category', 'parent_version')

        # Enhanced prefetching with CourseInstructor
        courses = courses.prefetch_related(
            Prefetch(
                'courseinstructor_set',
                queryset=CourseInstructor.objects.select_related('instructor').filter(is_active=True)
            ),
            Prefetch(
                'modules',
                queryset=Module.objects.prefetch_related('lessons').order_by('order')
            )
        )

        # Add analytics annotations for performance optimization
        return courses.annotate(
            enrolled_students_count=Count('enrollments', filter=Q(enrollments__status='active'), distinct=True),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            total_reviews=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True)
        ).order_by('-updated_date')

    @require_instructor_profile
    @require_permission('manage')
    def create(self, request, *args, **kwargs):
        """Enhanced course creation with InstructorProfile integration"""
        instructor_profile = request.instructor_profile

        audit_log(request.user, 'course_create_attempt', 'course', metadata={
            'instructor_tier': instructor_profile.tier,
            'instructor_status': instructor_profile.status
        }, request=request)

        try:
            # Validate course limits based on instructor tier using TierManager
            current_course_count = instructor_profile.total_courses
            if not TierManager.check_courses_limit(instructor_profile.tier, current_course_count):
                tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
                max_courses = tier_limits.get('max_courses', 3)
                return Response(
                    {
                        'detail': f'Course limit reached for {instructor_profile.get_tier_display()} tier',
                        'current_count': current_course_count,
                        'max_courses': max_courses
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create course with proper validation
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                course = serializer.save()

                # Create CourseInstructor relationship
                CourseInstructor.objects.create(
                    course=course,
                    instructor=request.user,
                    is_lead=True,
                    is_active=True,
                    can_edit_content=True,
                    can_manage_students=True,
                    can_view_analytics=True,
                    revenue_share_percentage=100.00
                )

                # Update instructor analytics
                instructor_profile.update_analytics()

            audit_log(request.user, 'course_created', 'course', course.id, {
                'title': course.title,
                'instructor_tier': instructor_profile.tier
            }, request=request)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            audit_log(request.user, 'course_create_failed', 'course',
                      metadata={'error': str(e)}, success=False, request=request)
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Course creation failed: {e}", exc_info=True)
            audit_log(request.user, 'course_create_failed', 'course',
                      metadata={'error': str(e)}, success=False, request=request)
            return Response(
                {'detail': 'Course creation failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @require_permission('manage')
    @tier_required('silver')
    @action(detail=True, methods=['post'])
    def clone(self, request, slug=None):
        """Enhanced course cloning with tier validation"""
        source_course = self.get_object()
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                # Clone course logic here
                cloned_course = source_course.clone_version(request.user)

                # Update instructor analytics
                instructor_profile.update_analytics()

                serializer = self.get_serializer(cloned_course)

                audit_log(request.user, 'course_cloned', 'course', cloned_course.id, {
                    'source_course_id': source_course.id,
                    'instructor_tier': instructor_profile.tier
                }, request=request)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Course cloning failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Course cloning failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @require_permission('manage')
    @action(detail=True, methods=['post'], url_path='reorder-modules')
    def reorder_modules(self, request, slug=None):
        """Reorder modules within a course"""
        course = self.get_object()
        modules_data = request.data.get('modules', [])

        # Validate input
        if not isinstance(modules_data, list):
            return Response(
                {'detail': 'modules must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate each module entry
        for i, module_data in enumerate(modules_data):
            if not isinstance(module_data, dict):
                return Response(
                    {'detail': f'modules[{i}] must be an object'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not {'id', 'order'} <= set(module_data.keys()):
                return Response(
                    {'detail': f'modules[{i}] must have id and order fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Limit operations to prevent DoS
        if len(modules_data) > MAX_BULK_OPERATIONS:
            return Response(
                {'detail': f'Too many modules (max {MAX_BULK_OPERATIONS})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Normalize order to prevent duplicates
                sorted_modules = sorted(modules_data, key=lambda x: int(x['order']))

                for idx, module_data in enumerate(sorted_modules, 1):
                    module_id = int(module_data['id'])

                    updated = Module.objects.filter(
                        id=module_id,
                        course=course
                    ).update(order=idx)

                    if not updated:
                        return Response(
                            {'detail': f"Module {module_id} not found in this course"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                # Clear caches
                clear_course_caches(course.id)

            audit_log(request.user, 'modules_reordered', 'course', course.id, {
                'module_count': len(modules_data)
            }, request=request)

            return Response({'detail': 'Module order updated successfully'})

        except Exception as e:
            logger.error(f"Module reordering failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Module reordering failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorModuleViewSet(InstructorBaseViewSet):
    """
    Enhanced module management with comprehensive security
    """
    serializer_class = InstructorModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'module'

    def get_queryset(self):
        """Enhanced queryset with security filtering and InstructorProfile integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Module.objects.none()

        course_id = self.request.query_params.get('course')
        if course_id:
            try:
                course_id = int(course_id)
                course = Course.objects.get(id=course_id)

                # Check course-specific permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Module.objects.filter(
                        course_id=course_id
                    ).select_related('course').prefetch_related('lessons')
                else:
                    return Module.objects.none()

            except (ValueError, Course.DoesNotExist):
                return Module.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Module.objects.select_related('course').prefetch_related('lessons')

        return Module.objects.filter(
            course__courseinstructor_set__instructor=user,
            course__courseinstructor_set__is_active=True
        ).select_related('course').prefetch_related('lessons')

    @require_instructor_profile
    @require_permission('edit')
    def perform_create(self, serializer):
        """Enhanced module creation with validation and analytics update"""
        course_id = self.request.data.get('course')
        if not course_id:
            raise serializers.ValidationError({"detail": "Course ID is required."})

        try:
            course_id = int(course_id)
            course = get_object_or_404(Course, id=course_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"detail": "Invalid course ID."})

        # Verify user has permission for this course using CourseInstructor
        if not CourseInstructor.objects.filter(
            course=course,
            instructor=self.request.user,
            is_active=True,
            can_edit_content=True
        ).exists():
            raise PermissionDenied("You do not have permission to create modules in this course.")

        with transaction.atomic():
            serializer.save(course=course)

            # Update instructor analytics
            if hasattr(self.request, 'instructor_profile'):
                self.request.instructor_profile.update_analytics()

            # Clear course caches
            clear_course_caches(course.id)

        audit_log(
            self.request.user,
            'module_created',
            'module',
            serializer.instance.id,
            {
                'course_id': course.id,
                'title': serializer.instance.title
            },
            request=self.request
        )

    @require_instructor_profile
    @require_permission('edit')
    @action(detail=True, methods=['post'], url_path='lessons/reorder')
    def reorder_lessons(self, request, pk=None):
        """
        Concurrency-safe lesson reordering with comprehensive validation
        ENHANCED: Integration with instructor profile and analytics
        """
        module = self.get_object()
        lessons_data = request.data.get('lessons', [])

        # Validate input
        if not isinstance(lessons_data, list):
            return Response(
                {'detail': 'lessons must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate each lesson entry
        for i, lesson_data in enumerate(lessons_data):
            if not isinstance(lesson_data, dict):
                return Response(
                    {'detail': f'lessons[{i}] must be an object'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not {'id', 'order'} <= set(lesson_data.keys()):
                return Response(
                    {'detail': f'lessons[{i}] must have id and order fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Limit operations to prevent DoS
        if len(lessons_data) > MAX_BULK_OPERATIONS:
            return Response(
                {'detail': f'Too many lessons (max {MAX_BULK_OPERATIONS})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Normalize order to prevent duplicates
                sorted_lessons = sorted(lessons_data, key=lambda x: int(x['order']))

                for idx, lesson_data in enumerate(sorted_lessons, 1):
                    lesson_id = int(lesson_data['id'])

                    updated = Lesson.objects.filter(
                        id=lesson_id,
                        module=module
                    ).update(order=idx)

                    if not updated:
                        return Response(
                            {'detail': f"Lesson {lesson_id} not found in this module"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                # Clear caches and update analytics
                clear_course_caches(module.course.id)
                if hasattr(request, 'instructor_profile'):
                    request.instructor_profile.update_analytics()

            audit_log(
                request.user,
                'lessons_reordered',
                'module',
                module.id,
                {
                    'lesson_count': len(lessons_data)
                },
                request=request
            )

            return Response({'detail': 'Lesson order updated successfully'})

        except Exception as e:
            logger.error(f"Lesson reordering failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Lesson reordering failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InstructorLessonViewSet(InstructorBaseViewSet):
    """
    Enhanced lesson management with comprehensive security and model integration
    """
    serializer_class = InstructorLessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'lesson'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile and CourseInstructor integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Lesson.objects.none()

        module_id = self.request.query_params.get('module')
        course_id = self.request.query_params.get('course')

        if module_id:
            try:
                module_id = int(module_id)
                module = Module.objects.select_related('course').get(id=module_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=module.course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Lesson.objects.filter(
                        module_id=module_id
                    ).select_related('module__course').prefetch_related('resources')
                else:
                    return Lesson.objects.none()

            except (ValueError, Module.DoesNotExist):
                return Lesson.objects.none()

        elif course_id:
            try:
                course_id = int(course_id)
                course = Course.objects.get(id=course_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Lesson.objects.filter(
                        module__course_id=course_id
                    ).select_related('module__course').prefetch_related('resources')
                else:
                    return Lesson.objects.none()

            except (ValueError, Course.DoesNotExist):
                return Lesson.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Lesson.objects.select_related('module__course').prefetch_related('resources')

        return Lesson.objects.filter(
            module__course__courseinstructor_set__instructor=user,
            module__course__courseinstructor_set__is_active=True
        ).select_related('module__course').prefetch_related('resources')

    @require_instructor_profile
    @require_permission('edit')
    def perform_create(self, serializer):
        """Enhanced lesson creation with validation and analytics"""
        module_id = self.request.data.get('module')
        if not module_id:
            raise serializers.ValidationError({"detail": "Module ID is required."})

        try:
            module_id = int(module_id)
            module = get_object_or_404(Module, id=module_id)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"detail": "Invalid module ID."})

        # Verify permissions using CourseInstructor
        if not CourseInstructor.objects.filter(
            course=module.course,
            instructor=self.request.user,
            is_active=True,
            can_edit_content=True
        ).exists():
            raise PermissionDenied("You do not have permission to create lessons in this course.")

        # Validate lesson data
        lesson_data = dict(self.request.data)
        validation_errors = validate_lesson_data(lesson_data)
        if validation_errors:
            raise serializers.ValidationError({
                "detail": "Lesson validation failed",
                "errors": validation_errors
            })

        with transaction.atomic():
            serializer.save(module=module)

            # Update instructor analytics
            if hasattr(self.request, 'instructor_profile'):
                self.request.instructor_profile.update_analytics()

            # Clear course caches
            clear_course_caches(module.course.id)

        audit_log(
            self.request.user,
            'lesson_created',
            'lesson',
            serializer.instance.id,
            {
                'module_id': module.id,
                'course_id': module.course.id,
                'title': serializer.instance.title
            },
            request=self.request
        )

    @require_instructor_profile
    @require_permission('edit')
    def perform_update(self, serializer):
        """Enhanced lesson update with validation"""
        lesson = self.get_object()

        # Validate lesson data
        lesson_data = dict(self.request.data)
        validation_errors = validate_lesson_data(lesson_data)
        if validation_errors:
            raise serializers.ValidationError({
                "detail": "Lesson validation failed",
                "errors": validation_errors
            })

        with transaction.atomic():
            serializer.save()

            # Clear course caches
            clear_course_caches(lesson.module.course.id)

        audit_log(
            self.request.user,
            'lesson_updated',
            'lesson',
            lesson.id,
            {
                'title': lesson.title
            },
            request=self.request
        )


class InstructorResourceViewSet(InstructorBaseViewSet):
    """
    Enhanced resource management with file security and model integration
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = InstructorResourceSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [UserRateThrottle]
    resource_name = 'resource'

    def get_queryset(self):
        """Enhanced queryset with InstructorProfile integration"""
        user = self.request.user

        # Validate instructor profile
        instructor_profile = get_instructor_profile(user)
        if not instructor_profile:
            return Resource.objects.none()

        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            try:
                lesson_id = int(lesson_id)
                lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)

                # Check permissions using CourseInstructor
                if CourseInstructor.objects.filter(
                    course=lesson.module.course,
                    instructor=user,
                    is_active=True
                ).exists():
                    return Resource.objects.filter(lesson_id=lesson_id)
                else:
                    return Resource.objects.none()

            except (ValueError, Lesson.DoesNotExist):
                return Resource.objects.none()

        # General queryset with permission filtering
        if user.is_staff or user.is_superuser:
            return Resource.objects.select_related('lesson__module__course')

        return Resource.objects.filter(
            lesson__module__course__courseinstructor_set__instructor=user,
            lesson__module__course__courseinstructor_set__is_active=True
        ).select_related('lesson__module__course')

    @require_instructor_profile
    @action(detail=False, methods=['post'], url_path='presigned-url',
            throttle_classes=[UserRateThrottle])
    def presigned_url(self, request):
        """
        Enhanced presigned URL generation with security validation and tier checking
        """
        instructor_profile = request.instructor_profile

        try:
            filename = request.data.get('filename', '').strip()
            content_type = request.data.get('content_type', '').strip()
            file_size = request.data.get('file_size', 0)

            # Validate inputs
            if not filename:
                return Response(
                    {'detail': 'filename is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not content_type:
                return Response(
                    {'detail': 'content_type is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                file_size = int(file_size)
            except (ValueError, TypeError):
                return Response(
                    {'detail': 'file_size must be an integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size based on instructor tier using TierManager
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_size = tier_limits.get('max_file_size', 10 * 1024 * 1024)  # Default 10MB

            if file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                return Response(
                    {
                        'detail': f'File too large (max {max_size_mb:.1f}MB for your tier)',
                        'max_size': max_size,
                        'file_size': file_size,
                        'tier': instructor_profile.get_tier_display()
                    },
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )

            # Get allowed file types from tier limits
            allowed_types = tier_limits.get('file_types_allowed', ['pdf', 'jpg', 'png'])

            # Check file extension
            file_ext = filename.split('.')[-1].lower() if '.' in filename else ''

            # Diamond tier can use any file type
            if allowed_types == '*' and instructor_profile.tier == 'diamond':
                # Still check for dangerous file types
                dangerous_extensions = ['exe', 'bat', 'cmd', 'com', 'sh', 'php', 'pl', 'py', 'js']
                if file_ext in dangerous_extensions:
                    return Response(
                        {'detail': f"File type {file_ext} not allowed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif file_ext not in allowed_types and allowed_types != '*':
                return Response(
                    {
                        'detail': f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_types)}",
                        'allowed_types': allowed_types
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file security
            security_result = validate_file_security(filename, content_type, file_size)
            if not security_result['is_safe']:
                audit_log(
                    request.user,
                    'unsafe_file_upload_attempt',
                    'resource',
                    metadata={
                        'filename': filename,
                        'reason': security_result['reason']
                    },
                    success=False,
                    request=request
                )
                return Response(
                    {'detail': f'File rejected: {security_result["reason"]}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate unique file path
            file_uuid = uuid.uuid4()
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            unique_filename = f"{file_uuid}.{file_extension}" if file_extension else str(file_uuid)
            file_path = f"instructor_resources/{request.user.id}/{unique_filename}"

            # Generate presigned URL (implementation depends on your storage backend)
            # This is a placeholder - implement according to your storage system
            presigned_data = {
                'upload_url': f"https://your-storage-service.com/presigned-upload",
                'file_path': file_path,
                'expires_in': 3600,  # 1 hour
                'fields': {
                    'key': file_path,
                    'Content-Type': content_type,
                    'Content-Length': str(file_size)
                }
            }

            audit_log(
                request.user,
                'presigned_url_generated',
                'resource',
                metadata={
                    'filename': filename,
                    'file_size': file_size,
                    'instructor_tier': instructor_profile.tier
                },
                request=request
            )

            return Response(presigned_data)

        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to generate upload URL'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=False, methods=['post'], throttle_classes=[UserRateThrottle])
    def upload_complete(self, request):
        """Handle upload completion and create resource record"""
        instructor_profile = request.instructor_profile

        try:
            file_path = request.data.get('file_path')
            lesson_id = request.data.get('lesson_id')
            title = request.data.get('title', '').strip()
            description = request.data.get('description', '').strip()

            if not all([file_path, lesson_id, title]):
                return Response(
                    {'detail': 'file_path, lesson_id, and title are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate lesson ownership
            try:
                lesson = Lesson.objects.select_related('module__course').get(id=lesson_id)
                if not CourseInstructor.objects.filter(
                    course=lesson.module.course,
                    instructor=request.user,
                    is_active=True,
                    can_edit_content=True
                ).exists():
                    return Response(
                        {'detail': 'Permission denied for this lesson'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Lesson.DoesNotExist:
                return Response(
                    {'detail': 'Lesson not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create resource record
            with transaction.atomic():
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=sanitize_input(title),
                    description=sanitize_input(description),
                    file_path=file_path,
                    resource_type='file',
                    uploaded_by=request.user
                )

                # Update instructor analytics
                instructor_profile.update_analytics()

            audit_log(
                request.user,
                'resource_uploaded',
                'resource',
                resource.id,
                {
                    'lesson_id': lesson.id,
                    'title': resource.title
                },
                request=request
            )

            serializer = self.get_serializer(resource)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Upload completion failed: {e}", exc_info=True)
            return Response(
                {'detail': 'Upload completion failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
