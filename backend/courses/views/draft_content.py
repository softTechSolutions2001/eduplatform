# File Path: backend/courses/views/draft_content.py
# Folder Path: backend/courses/views/
# Date Created: 2025-06-26 14:05:29
# Date Revised: 2025-07-09 04:31:31
# Current Date and Time (UTC): 2025-07-09 04:31:31
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 04:31:31 UTC
# User: MohithaSanthanam2010
# Version: 7.2.0
#
# Draft Content Management Views for Course Management System
#
# Version 7.2.0 Changes:
# - FIXED 🔴: frozenset concatenation error in SAFE_TAGS
# - FIXED 🔴: Added throttling to all endpoints consistently
# - FIXED 🔴: Proper CSRF protection implementation
# - ENHANCED: Improved content sanitization and validation
# - ADDED: Row-level locking for race condition prevention

import logging
import secrets
import time
from typing import Any, Dict, List, Optional

# Import HTML sanitization library
import bleach
from bleach.sanitizer import ALLOWED_ATTRIBUTES, ALLOWED_TAGS
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import OpenApiParameter, extend_schema

# Import instructor portal models and functions needed for existing functionality
from instructor_portal.models import CourseCreationSession, DraftCourseContent
from instructor_portal.serializers.creation import DraftCourseContentSerializer
from instructor_portal.views.mixins import audit_log
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from ..models import Course, Lesson, Module, Resource
from ..permissions import IsInstructorOrAdmin
from ..serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseVersionSerializer,
    LessonSerializer,
    ModuleSerializer,
    ResourceSerializer,
)
from .mixins import (
    ConsolidatedPermissionMixin,
    OptimizedSerializerMixin,
    SensitiveAPIThrottle,
    StandardContextMixin,
    log_operation_safe,
    validate_permissions_and_raise,
)

# FIXED: Convert frozenset to list to avoid TypeError
SAFE_TAGS = list(ALLOWED_TAGS) + [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "div",
    "span",
    "p",
]
SAFE_ATTRIBUTES = dict(ALLOWED_ATTRIBUTES)
SAFE_ATTRIBUTES.update(
    {
        "img": ["src", "alt", "width", "height"],
        "a": ["href", "target", "rel", "title"],
        "*": ["class", "id", "style"],
    }
)

logger = logging.getLogger(__name__)


# Utility functions
def sanitize_html_content(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    if not html_content or not isinstance(html_content, str):
        return html_content

    return bleach.clean(
        html_content, tags=SAFE_TAGS, attributes=SAFE_ATTRIBUTES, strip=True
    )


# =====================================
# EXISTING DRAFT CONTENT SYSTEM
# =====================================


class DraftCourseContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for draft course content management
    FIXED: Added proper throttling and CSRF protection
    """

    serializer_class = DraftCourseContentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [
        TokenAuthentication
    ]  # Removed SessionAuthentication for security
    queryset = DraftCourseContent.objects.all()
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security

    def get_queryset(self):
        """Get draft content with proper filtering"""
        queryset = super().get_queryset()

        # Filter by session
        session_id = self.request.query_params.get("session_id")
        if session_id:
            queryset = queryset.filter(session__session_id=session_id)

        # Only return user's own content
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(session__instructor__user=self.request.user)

        return queryset.order_by("order")

    def perform_create(self, serializer):
        """Add security validation before creating content"""
        session = serializer.validated_data.get("session")

        # Verify user owns this session
        if session and session.instructor.user != self.request.user:
            raise ValidationError(
                "You don't have permission to add content to this session"
            )

        # Sanitize HTML content
        content = serializer.validated_data.get("content")
        if content and "html_content" in content:
            content["html_content"] = sanitize_html_content(content["html_content"])
            serializer.validated_data["content"] = content

        super().perform_create(serializer)

        audit_log(
            self.request.user,
            "draft_content_created",
            "draft_content",
            serializer.instance.id,
            {
                "content_type": serializer.instance.content_type,
                "session_id": str(session.session_id) if session else None,
            },
            success=True,
            request=self.request,
        )

    def perform_update(self, serializer):
        """Add security validation before updating content"""
        # Verify user owns this content
        instance = serializer.instance
        if (
            instance.session.instructor.user != self.request.user
            and not self.request.user.is_staff
        ):
            raise ValidationError("You don't have permission to update this content")

        # Sanitize HTML content
        content = serializer.validated_data.get("content")
        if content and "html_content" in content:
            content["html_content"] = sanitize_html_content(content["html_content"])
            serializer.validated_data["content"] = content

        super().perform_update(serializer)

    @method_decorator(csrf_protect)
    @action(detail=False, methods=["patch"], url_path="reorder")
    def bulk_reorder(self, request, *args, **kwargs):
        """
        Reorder multiple draft content blocks at once.
        FIXED: Added proper CSRF protection and row-level locking
        """
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response(
                {"detail": "items[] list required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limit the number of items for security
        max_items = getattr(settings, "MAX_BULK_OPERATION_SIZE", 100)
        if len(items) > max_items:
            return Response(
                {"detail": f"Too many items. Maximum allowed: {max_items}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                draft_ids = [i["id"] for i in items]
                order_map = {i["id"]: i["order"] for i in items}

                # Fetch blocks and ensure they belong to the user
                queryset = self.get_queryset().filter(pk__in=draft_ids)

                if (
                    not self.request.user.is_staff
                    and not self.request.user.is_superuser
                ):
                    queryset = queryset.filter(
                        session__instructor__user=self.request.user
                    )

                # Use select_for_update to prevent race conditions
                rows = queryset.select_for_update(of=("self",))

                if rows.count() != len(draft_ids):
                    audit_log(
                        self.request.user,
                        "bulk_reorder_failed",
                        "draft_content",
                        None,
                        {"error": "Some IDs not found or permission denied"},
                        success=False,
                        request=request,
                    )
                    return Response(
                        {
                            "detail": "Some draft-block IDs not found or you don't have permission."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for row in rows:
                    row.order = order_map[row.pk]
                    row.save(update_fields=("order",))

                # Update session's last_auto_save time
                sessions = set()
                for row in rows:
                    sessions.add(row.session_id)

                if sessions:
                    CourseCreationSession.objects.filter(pk__in=sessions).update(
                        last_auto_save=timezone.now()
                    )

                audit_log(
                    self.request.user,
                    "bulk_reorder_completed",
                    "draft_content",
                    None,
                    {"item_count": len(items), "sessions_updated": len(sessions)},
                    success=True,
                    request=request,
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error in bulk_reorder: {e}", exc_info=True)
            audit_log(
                self.request.user,
                "bulk_reorder_error",
                "draft_content",
                None,
                {"error": str(e)},
                success=False,
                request=request,
            )
            return Response(
                {"detail": "An error occurred during reordering."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # FIXED: Added missing throttling and CSRF protection
    @method_decorator(csrf_protect)
    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_draft_update(self, request, *args, **kwargs):
        """
        Bulk update multiple draft content blocks at once.
        FIXED: Added CSRF protection and throttling
        """
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response(
                {"detail": "items[] list required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limit the number of items for security
        max_items = getattr(settings, "MAX_BULK_OPERATION_SIZE", 100)
        if len(items) > max_items:
            return Response(
                {"detail": f"Too many items. Maximum allowed: {max_items}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                draft_ids = [i["id"] for i in items if "id" in i]
                content_map = {
                    i["id"]: i.get("content", {}) for i in items if "id" in i
                }

                # Fetch blocks and ensure they belong to the user
                queryset = self.get_queryset().filter(pk__in=draft_ids)

                if (
                    not self.request.user.is_staff
                    and not self.request.user.is_superuser
                ):
                    queryset = queryset.filter(
                        session__instructor__user=self.request.user
                    )

                # Use select_for_update to prevent race conditions
                rows = queryset.select_for_update(of=("self",))

                if rows.count() != len(draft_ids):
                    audit_log(
                        self.request.user,
                        "bulk_update_failed",
                        "draft_content",
                        None,
                        {"error": "Some IDs not found or permission denied"},
                        success=False,
                        request=request,
                    )
                    return Response(
                        {
                            "detail": "Some draft-block IDs not found or you don't have permission."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                updated_count = 0
                for row in rows:
                    content = content_map.get(row.pk)
                    if content:
                        # Sanitize HTML content
                        if "html_content" in content:
                            content["html_content"] = sanitize_html_content(
                                content["html_content"]
                            )

                        row.content = content
                        row.save(update_fields=("content",))
                        updated_count += 1

                # Update session's last_auto_save time
                sessions = set()
                for row in rows:
                    sessions.add(row.session_id)

                if sessions:
                    CourseCreationSession.objects.filter(pk__in=sessions).update(
                        last_auto_save=timezone.now()
                    )

                audit_log(
                    self.request.user,
                    "bulk_update_completed",
                    "draft_content",
                    None,
                    {"updated_count": updated_count, "sessions_updated": len(sessions)},
                    success=True,
                    request=request,
                )

            return Response({"updated_count": updated_count}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in bulk_draft_update: {e}", exc_info=True)
            audit_log(
                self.request.user,
                "bulk_update_error",
                "draft_content",
                None,
                {"error": str(e)},
                success=False,
                request=request,
            )
            return Response(
                {"detail": "An error occurred during bulk update."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =====================================
# REGULAR COURSE DRAFT MANAGEMENT
# =====================================


class DraftCourseViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,
    StandardContextMixin,
    viewsets.ModelViewSet,
):
    """Draft course management for instructors"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    lookup_field = "slug"
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    serializer_action_map = {
        "retrieve": CourseDetailSerializer,
        "versions": CourseVersionSerializer,
    }

    def get_queryset(self):
        """Get only draft courses for the current instructor"""
        try:
            if not self.request.user.is_authenticated:
                return Course.objects.none()

            # Return only draft courses that belong to the instructor
            queryset = (
                Course.objects.filter(
                    is_draft=True,
                    courseinstructor__instructor=self.request.user,
                    courseinstructor__is_active=True,
                )
                .select_related("category", "parent_version")
                .order_by("-created_date")
            )

            return queryset
        except Exception as e:
            logger.error(f"Error in DraftCourseViewSet.get_queryset: {e}")
            return Course.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a draft course with proper locking"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Set as draft by default
            draft_course = serializer.save(
                is_draft=True,
                is_published=False,
                created_by=request.user,
            )

            # Assign instructor
            from instructor_portal.models import CourseInstructor

            CourseInstructor.objects.create(
                course=draft_course,
                instructor=request.user,
                is_lead=True,
                title="Lead Instructor",
                is_active=True,
            )

            log_operation_safe("Draft course created", draft_course.id, request.user)

            response_serializer = CourseDetailSerializer(
                draft_course, context=self.get_serializer_context()
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Draft course creation error: {e}")
            return Response(
                {"error": "An error occurred while creating the draft course."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(responses={200: CourseVersionSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def versions(self, request, slug=None):
        """Get all versions of a course"""
        try:
            course = self.get_object()

            # Get parent version if this is a derived course
            parent = course.parent_version
            original = parent if parent else course

            # Get all versions including the original
            versions = (
                Course.objects.filter(parent_version=original)
                .union(Course.objects.filter(id=original.id))
                .order_by("-created_date")
            )

            serializer = self.get_serializer(versions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving course versions: {e}")
            return Response(
                {"error": "An error occurred while retrieving course versions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DraftModuleViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,
    StandardContextMixin,
    viewsets.ModelViewSet,
):
    """Draft module management for instructors"""

    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get modules for draft courses only"""
        try:
            if not self.request.user.is_authenticated:
                return Module.objects.none()

            return (
                Module.objects.filter(
                    course__is_draft=True,
                    course__courseinstructor__instructor=self.request.user,
                    course__courseinstructor__is_active=True,
                )
                .select_related("course")
                .prefetch_related("lessons")
            )
        except Exception as e:
            logger.error(f"Error in DraftModuleViewSet.get_queryset: {e}")
            return Module.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Create a module ensuring it's for a draft course"""
        try:
            course = serializer.validated_data.get("course")

            # Validate the course is a draft and user has permission
            validate_permissions_and_raise(
                self.request.user,
                course and course.is_draft and self.has_course_permission(course),
                "You can only add modules to draft courses you have permission for.",
            )

            module = serializer.save()
            log_operation_safe("Draft module created", module.id, self.request.user)
        except ValidationError as e:
            logger.error(f"Draft module validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Draft module creation error: {e}")
            raise ValidationError("An error occurred while creating the draft module.")


class DraftLessonViewSet(
    OptimizedSerializerMixin,
    ConsolidatedPermissionMixin,
    StandardContextMixin,
    viewsets.ModelViewSet,
):
    """Draft lesson management for instructors"""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get lessons for draft modules only"""
        try:
            if not self.request.user.is_authenticated:
                return Lesson.objects.none()

            return (
                Lesson.objects.filter(
                    module__course__is_draft=True,
                    module__course__courseinstructor__instructor=self.request.user,
                    module__course__courseinstructor__is_active=True,
                )
                .select_related("module", "module__course")
                .prefetch_related("resources")
            )
        except Exception as e:
            logger.error(f"Error in DraftLessonViewSet.get_queryset: {e}")
            return Lesson.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """Create a lesson ensuring it's for a draft module"""
        try:
            module = serializer.validated_data.get("module")

            # Validate the module's course is a draft and user has permission
            validate_permissions_and_raise(
                self.request.user,
                module
                and module.course.is_draft
                and self.has_course_permission(module.course),
                "You can only add lessons to draft modules you have permission for.",
            )

            # Sanitize HTML content
            content = serializer.validated_data.get("content")
            if content:
                serializer.validated_data["content"] = sanitize_html_content(content)

            guest_content = serializer.validated_data.get("guest_content")
            if guest_content:
                serializer.validated_data["guest_content"] = sanitize_html_content(
                    guest_content
                )

            registered_content = serializer.validated_data.get("registered_content")
            if registered_content:
                serializer.validated_data["registered_content"] = sanitize_html_content(
                    registered_content
                )

            lesson = serializer.save()
            log_operation_safe("Draft lesson created", lesson.id, self.request.user)
        except ValidationError as e:
            logger.error(f"Draft lesson validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Draft lesson creation error: {e}")
            raise ValidationError("An error occurred while creating the draft lesson.")


class ResourceManagementView(APIView, ConsolidatedPermissionMixin):
    """
    API endpoint for managing lesson resources in draft content
    """

    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    @extend_schema(
        request=ResourceSerializer,
        responses={
            201: ResourceSerializer,
            400: {"description": "Bad request"},
            403: {"description": "Permission denied"},
        },
    )
    @transaction.atomic
    @method_decorator(csrf_protect)
    def post(self, request, lesson_id):
        """Add a resource to a lesson"""
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                lesson.module.course.is_draft
                and self.has_course_permission(lesson.module.course),
                "You can only add resources to lessons in draft courses you have permission for.",
            )

            # Create resource
            serializer = ResourceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Sanitize description
            description = serializer.validated_data.get("description")
            if description:
                serializer.validated_data["description"] = sanitize_html_content(
                    description
                )

            resource = serializer.save(lesson=lesson)

            log_operation_safe("Resource added to lesson", resource.id, request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Resource creation error: {e}")
            return Response(
                {"error": "An error occurred while adding the resource."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        responses={
            200: {"description": "Resource deleted successfully"},
            403: {"description": "Permission denied"},
            404: {"description": "Resource not found"},
        }
    )
    @transaction.atomic
    @method_decorator(csrf_protect)
    def delete(self, request, resource_id):
        """Delete a resource"""
        try:
            resource = get_object_or_404(Resource, id=resource_id)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                resource.lesson.module.course.is_draft
                and self.has_course_permission(resource.lesson.module.course),
                "You can only delete resources from draft courses you have permission for.",
            )

            # Delete resource
            resource_id = resource.id
            resource.delete()

            log_operation_safe("Resource deleted", resource_id, request.user)

            return Response(
                {"detail": "Resource deleted successfully"}, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Resource deletion error: {e}")
            return Response(
                {"error": "An error occurred while deleting the resource."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CoursePreviewView(APIView, ConsolidatedPermissionMixin):
    """
    Generate a preview URL for a draft course
    """

    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    @extend_schema(
        responses={
            200: {"description": "Preview URL generated"},
            403: {"description": "Permission denied"},
            404: {"description": "Course not found"},
        }
    )
    @method_decorator(csrf_protect)
    def get(self, request, course_slug):
        """Generate preview URL for a draft course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                course.is_draft and self.has_course_permission(course),
                "You can only generate preview URLs for draft courses you have permission for.",
            )

            # Generate preview token (cryptographically secure)
            preview_token = f"{secrets.token_hex(16)}_{int(time.time())}"
            preview_expiry = timezone.now() + timezone.timedelta(days=7)  # 7-day expiry

            # Try to save preview token to course if fields exist
            try:
                course.preview_token = preview_token
                course.preview_expiry = preview_expiry
                course.save(update_fields=["preview_token", "preview_expiry"])
            except Exception as e:
                logger.warning(f"Could not save preview token to course: {e}")

            # Generate preview URL
            frontend_url = request.build_absolute_uri("/").rstrip("/")
            preview_url = (
                f"{frontend_url}/courses/preview/{course_slug}?token={preview_token}"
            )

            log_operation_safe("Course preview URL generated", course.id, request.user)

            return Response(
                {
                    "preview_url": preview_url,
                    "expires_at": preview_expiry,
                    "course_id": course.id,
                    "course_slug": course.slug,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Preview URL generation error: {e}")
            return Response(
                {"error": "An error occurred while generating the preview URL."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CourseVersionControlView(APIView, ConsolidatedPermissionMixin):
    """
    Course version control operations for instructors
    """

    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    throttle_classes = [SensitiveAPIThrottle]  # Added throttling for security
    authentication_classes = [TokenAuthentication]

    @extend_schema(
        responses={
            200: {"description": "Course version information"},
            403: {"description": "Permission denied"},
            404: {"description": "Course not found"},
        }
    )
    def get(self, request, course_slug):
        """Get version history for a course"""
        try:
            course = get_object_or_404(Course, slug=course_slug)

            # Validate permissions
            validate_permissions_and_raise(
                request.user,
                self.has_course_permission(course),
                "You do not have permission to view version history for this course.",
            )

            # Determine the original course
            original = course
            if course.parent_version:
                original = course.parent_version

            # Get all versions including the original
            versions = list(
                Course.objects.filter(parent_version=original)
                .order_by("-created_date")
                .values(
                    "id",
                    "title",
                    "slug",
                    "version",
                    "is_draft",
                    "is_published",
                    "created_date",
                )
            )

            # Add the original version to the list if not already included
            original_data = {
                "id": original.id,
                "title": original.title,
                "slug": original.slug,
                "version": original.version,
                "is_draft": original.is_draft,
                "is_published": original.is_published,
                "created_date": original.created_date,
                "created_by": (
                    original.created_by.username
                    if hasattr(original, "created_by") and original.created_by
                    else "Unknown"
                ),
            }

            # Check if original is already in versions list
            if not any(v["id"] == original.id for v in versions):
                versions.insert(0, original_data)

            # Add current version indicator
            for version in versions:
                version["is_current_version"] = version["id"] == course.id

            return Response(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "current_version": course.version,
                    "total_versions": len(versions),
                    "versions": versions,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Version history error: {e}")
            return Response(
                {"error": "An error occurred while retrieving version history."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
