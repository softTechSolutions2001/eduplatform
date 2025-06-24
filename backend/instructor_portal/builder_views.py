# File Path: backend/instructor_portal/builder_views.py
# Date Created: 2025-06-24 08:50:00
# Current Date and Time (UTC): 2025-06-24 08:49:22
# Author: saiacupunctureFolllow
# Version: 1.0.0

from typing import Any
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.permissions import IsCourseInstructor
from instructor_portal.models import CourseCreationSession, DraftCourseContent, InstructorProfile
from instructor_portal.serializers import CourseCreationSessionSerializer, DraftCoursePublishSerializer
from instructor_portal.views import require_instructor_profile, audit_log

import logging
logger = logging.getLogger(__name__)

class DragDropBuilderViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    End-points required by the React DnD course-builder.

    • POST   /instructor/dnd/sessions/start/      → start()
    • GET    /instructor/dnd/sessions/{session_id}/     → retrieve()   (built-in)
    • POST   /instructor/dnd/sessions/{session_id}/publish/ → publish()
    """

    queryset = CourseCreationSession.objects.select_related("instructor")
    serializer_class = CourseCreationSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "session_id"
    resource_name = 'course_creation_session'

    @require_instructor_profile
    @action(detail=False, methods=["post"])
    def start(self, request, *args: Any, **kwargs: Any) -> Response:  # POST
        """Start a new drag-and-drop course builder session"""
        instructor_profile = request.instructor_profile

        try:
            # Validate tier requirements (Silver tier or higher for advanced editing)
            if instructor_profile.tier not in [
                InstructorProfile.Tier.SILVER,
                InstructorProfile.Tier.GOLD,
                InstructorProfile.Tier.PLATINUM,
                InstructorProfile.Tier.DIAMOND
            ]:
                return Response(
                    {"detail": "Drag & Drop Builder requires Silver tier or higher"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check course limit
            from instructor_portal.models import TierManager
            if not TierManager.check_courses_limit(
                instructor_profile.tier,
                instructor_profile.total_courses
            ):
                tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
                max_courses = tier_limits.get('max_courses', 3)

                return Response(
                    {
                        'detail': f'Course limit reached for your tier',
                        'current_count': instructor_profile.total_courses,
                        'max_courses': max_courses
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            with transaction.atomic():
                session = CourseCreationSession.objects.create(
                    session_id=uuid4(),
                    instructor=instructor_profile,
                    creation_method=CourseCreationSession.CreationMethod.DRAG_DROP,
                    total_steps=3,
                    status=CourseCreationSession.Status.IN_PROGRESS,
                    course_data={},  # Initialize empty course data
                    started_at=timezone.now(),
                    expires_at=timezone.now() + timezone.timedelta(days=30)
                )

                audit_log(
                    request.user,
                    'dnd_session_started',
                    'course_creation_session',
                    session.id,
                    {'session_id': str(session.session_id)},
                    success=True,
                    request=request
                )

                return Response(
                    {"session_id": session.session_id},
                    status=status.HTTP_201_CREATED,
                )

        except serializers.ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating DnD session: {e}", exc_info=True)
            audit_log(
                request.user,
                'dnd_session_failed',
                'course_creation_session',
                None,
                {'error': str(e)},
                success=False,
                request=request
            )
            return Response(
                {'detail': 'Failed to create course creation session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(
        detail=True,
        methods=["post"],
        url_path="publish",
        permission_classes=[IsAuthenticated, IsCourseInstructor],
    )
    def publish(self, request, session_id: str, *args: Any, **kwargs: Any) -> Response:
        """Publish course from drag-and-drop session"""
        try:
            session = self.get_object()

            # Validate ownership
            if session.instructor.user != request.user:
                audit_log(
                    request.user,
                    'unauthorized_publish_attempt',
                    'course_creation_session',
                    session.id,
                    {'session_id': str(session.session_id)},
                    success=False,
                    request=request
                )
                return Response(
                    {"detail": "You do not have permission to publish this session"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Validate that session is ready for publishing
            if session.status == CourseCreationSession.Status.DRAFT:
                # Auto-validate if needed
                errors = session.validate_course_data()
                if errors:
                    return Response(
                        {
                            'detail': 'Session is not ready for publishing',
                            'errors': errors[:5],  # Limit to first 5 errors
                            'error_count': len(errors)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update status if validation passes
                session.status = CourseCreationSession.Status.READY_TO_PUBLISH
                session.save(update_fields=['status'])

            elif session.status != CourseCreationSession.Status.READY_TO_PUBLISH:
                return Response(
                    {"detail": f"Draft not ready for publishing. Current status: {session.get_status_display()}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = DraftCoursePublishSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                # Convert session to published course
                course = session.publish_course()

                if not course:
                    return Response(
                        {'detail': 'Course publishing failed. See validation errors for details.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update publish settings based on serializer data
                if serializer.validated_data.get('is_published', True):
                    course.is_published = True
                    course.completion_status = 'published'
                    course.published_date = timezone.now()
                    course.save(update_fields=['is_published', 'completion_status', 'published_date'])

                # Update session status
                session.status = CourseCreationSession.Status.PUBLISHED
                session.published_course = course
                session.save(update_fields=["status", "published_course"])

                # Update instructor analytics
                session.instructor.update_analytics()

                audit_log(
                    request.user,
                    'dnd_session_published',
                    'course',
                    course.id,
                    {
                        'session_id': str(session.session_id),
                        'creation_method': session.creation_method
                    },
                    success=True,
                    request=request
                )

            return Response(
                {"course_id": course.id, "slug": course.slug},
                status=status.HTTP_201_CREATED,
            )

        except serializers.ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error publishing DnD session: {e}", exc_info=True)
            audit_log(
                request.user,
                'dnd_session_publish_failed',
                'course_creation_session',
                session.id if 'session' in locals() else None,
                {'error': str(e)},
                success=False,
                request=request
            )
            return Response(
                {'detail': 'Course publishing failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
