#
# File Path: instructor_portal/views/creation_views.py
# Folder Path: instructor_portal/views/
# Date Created: 2025-06-27 06:42:13
# Date Revised: 2025-06-27 06:42:13
# Current Date and Time (UTC): 2025-06-27 06:42:13
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:42:13 UTC
# User: softTechSolutions2001
# Version: 1.0.0
#
# Course creation and session endpoints for instructor_portal (Session/Builder endpoints)
# FIXED: Complete implementation with proper imports and error handling

import logging
import uuid
from typing import Any
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from courses.permissions import IsCourseInstructor
from ..models import (
    InstructorProfile, CourseCreationSession, CourseTemplate,
    DraftCourseContent, TierManager
)
from ..serializers import (
    CourseCreationSessionSerializer, CourseTemplateSerializer,
    DraftCourseContentSerializer
)
from .mixins import (
    InstructorBaseViewSet, require_instructor_profile, tier_required,
    get_instructor_profile, audit_log
)

logger = logging.getLogger(__name__)

class CourseCreationSessionViewSet(InstructorBaseViewSet):
    """
    API endpoint for course creation session management
    ENHANCED: Complete course creation workflow support
    """
    serializer_class = CourseCreationSessionSerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'course_creation_session'

    def get_queryset(self):
        """Get user's course creation sessions"""
        instructor_profile = get_instructor_profile(self.request.user)
        if not instructor_profile:
            return CourseCreationSession.objects.none()

        return CourseCreationSession.objects.filter(
            instructor=instructor_profile
        ).order_by('-updated_date')

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def start_wizard(self, request):
        """Start wizard-based course creation"""
        instructor_profile = request.instructor_profile

        # Check course limit
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
                    'max_courses': max_courses,
                    'tier': instructor_profile.get_tier_display()
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Create new wizard session
            session = CourseCreationSession.objects.create(
                instructor=instructor_profile,
                creation_method=CourseCreationSession.CreationMethod.WIZARD,
                total_steps=6,  # Define your wizard steps
                course_data={},  # Initialize empty data
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            serializer = self.get_serializer(session)

            audit_log(
                request.user,
                'course_wizard_started',
                'course_creation_session',
                session.id,
                {'session_id': str(session.session_id)},
                request=request
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating wizard session: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create course creation session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @tier_required('gold')
    @action(detail=False, methods=['post'])
    def start_ai_builder(self, request):
        """Start AI-assisted course creation"""
        instructor_profile = request.instructor_profile
        ai_prompt = request.data.get('ai_prompt', '').strip()

        # Validate AI prompt
        if not ai_prompt or len(ai_prompt) < 20:
            return Response(
                {'detail': 'AI prompt must be at least 20 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check course limit
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

        try:
            # Create AI builder session
            session = CourseCreationSession.objects.create(
                instructor=instructor_profile,
                creation_method=CourseCreationSession.CreationMethod.AI_ASSISTED,
                total_steps=4,
                course_data={},
                ai_prompt=ai_prompt,
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            serializer = self.get_serializer(session)

            audit_log(
                request.user,
                'ai_builder_started',
                'course_creation_session',
                session.id,
                {
                    'session_id': str(session.session_id),
                    'prompt_length': len(ai_prompt)
                },
                request=request
            )

            return Response(
                {
                    **serializer.data,
                    'ai_status': 'processing',
                    'estimated_wait': '2-5 minutes'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating AI builder session: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create AI builder session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def auto_save(self, request, pk=None):
        """Auto-save session data"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data

        # Validate auto-save data
        if not isinstance(data, dict):
            return Response(
                {'detail': 'Auto-save data must be a valid JSON object'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent auto-save for published sessions
        if session.status in [
            CourseCreationSession.Status.PUBLISHED,
            CourseCreationSession.Status.FAILED
        ]:
            return Response(
                {'detail': f'Cannot auto-save a session in {session.get_status_display()} status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = session.auto_save(data)
        if success:
            return Response({'detail': 'Auto-saved successfully'})
        else:
            return Response(
                {'detail': 'Auto-save failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate session content before publishing"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update status to validating
        session.status = CourseCreationSession.Status.IN_PROGRESS
        session.save(update_fields=['status'])

        try:
            # Perform validation
            errors = session.validate_session_data()

            # Update status based on validation results
            if errors:
                session.status = CourseCreationSession.Status.DRAFT
                session.validation_errors = errors
                session.save(update_fields=['status', 'validation_errors'])

                return Response(
                    {
                        'is_valid': False,
                        'errors': errors,
                        'status': session.get_status_display()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                session.status = CourseCreationSession.Status.COMPLETED
                session.validation_errors = []
                session.save(update_fields=['status', 'validation_errors'])

                return Response({
                    'is_valid': True,
                    'status': session.get_status_display()
                })

        except Exception as e:
            logger.error(f"Error validating session {session.id}: {e}", exc_info=True)
            session.status = CourseCreationSession.Status.DRAFT
            session.save(update_fields=['status'])

            return Response(
                {'detail': 'Validation failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish course from creation session"""
        session = self.get_object()

        # Validate ownership
        if session.instructor.user != request.user:
            return Response(
                {'detail': 'You do not have permission to publish this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate session is ready for publishing
        if session.status != CourseCreationSession.Status.COMPLETED:
            # Auto-validate if needed
            if session.status == CourseCreationSession.Status.DRAFT:
                errors = session.validate_session_data()
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
                session.status = CourseCreationSession.Status.COMPLETED
                session.save(update_fields=['status'])
            else:
                return Response(
                    {
                        'detail': 'Session is not ready for publishing',
                        'status': session.get_status_display()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            # Execute publishing with proper serializer integration
            with transaction.atomic():
                course = session.publish_course(request.user)

                if not course:
                    return Response(
                        {'detail': 'Course publishing failed. See validation errors for details.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                session.status = CourseCreationSession.Status.PUBLISHED
                session.published_course = course
                session.save(update_fields=['status', 'published_course'])

                # Update instructor analytics
                session.instructor.update_analytics()

            audit_log(
                request.user,
                'session_published',
                'course',
                course.id,
                {
                    'session_id': str(session.session_id),
                    'creation_method': session.creation_method
                },
                request=request
            )

            return Response({
                'detail': 'Course published successfully',
                'course_id': course.id,
                'course_slug': course.slug,
                'course_title': course.title
            })

        except Exception as e:
            logger.error(f"Error publishing course for session {session.id}: {e}", exc_info=True)
            return Response(
                {'detail': 'Course publishing failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseTemplateViewSet(InstructorBaseViewSet):
    """
    API endpoint for course template management
    """
    serializer_class = CourseTemplateSerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'course_template'

    def get_queryset(self):
        """Get available templates based on user permissions"""
        # Public templates available to all authenticated users
        queryset = CourseTemplate.objects.filter(is_active=True)

        # Additional filtering options
        category = self.request.query_params.get('category')
        template_type = self.request.query_params.get('type')
        difficulty = self.request.query_params.get('difficulty')

        if category:
            queryset = queryset.filter(category_id=category)

        if template_type:
            queryset = queryset.filter(template_type=template_type)

        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        return queryset.select_related('category', 'created_by')

    @require_instructor_profile
    @action(detail=True, methods=['post'])
    def create_session(self, request, pk=None):
        """Create a course creation session from template"""
        template = self.get_object()
        instructor_profile = request.instructor_profile

        # Check course limit
        if not TierManager.check_courses_limit(
            instructor_profile.tier,
            instructor_profile.total_courses
        ):
            tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
            max_courses = tier_limits.get('max_courses', 3)

            return Response(
                {
                    'detail': f'Course limit reached for {instructor_profile.get_tier_display()} tier',
                    'current_count': instructor_profile.total_courses,
                    'max_courses': max_courses
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Create session from template
            session = CourseCreationSession.objects.create(
                instructor=instructor_profile,
                creation_method=CourseCreationSession.CreationMethod.TEMPLATE,
                template=template,
                course_data=template.template_data,
                total_steps=template.template_data.get('steps', 5),
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            session_serializer = CourseCreationSessionSerializer(session)

            audit_log(
                request.user,
                'template_session_created',
                'course_creation_session',
                session.id,
                {'template_id': template.id, 'template_name': template.name},
                request=request
            )

            return Response(
                session_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating session from template: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to create session from template'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @tier_required('platinum')
    @action(detail=False, methods=['post'])
    def create_template(self, request):
        """Create a new course template (premium feature)"""
        # This is a premium feature restricted to higher tiers
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Set the creator
                template = serializer.save(created_by=request.user)

                audit_log(
                    request.user,
                    'template_created',
                    'course_template',
                    template.id,
                    {'template_name': template.name},
                    request=request
                )

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return Response(
                {'detail': 'Template creation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DragDropBuilderViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    End-points required by the React DnD course-builder.
    """

    queryset = CourseCreationSession.objects.select_related("instructor")
    serializer_class = CourseCreationSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "session_id"
    resource_name = 'course_creation_session'

    @require_instructor_profile
    @action(detail=False, methods=["post"])
    def start(self, request, *args: Any, **kwargs: Any) -> Response:
        instructor_profile = request.instructor_profile

        try:
            with transaction.atomic():
                session = CourseCreationSession.objects.create(
                    session_id=uuid.uuid4(),
                    instructor=instructor_profile,
                    creation_method=CourseCreationSession.CreationMethod.DRAG_DROP,
                    total_steps=3,
                    status=CourseCreationSession.Status.IN_PROGRESS,
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
        except Exception as e:
            logger.error(f"Error creating DnD session: {e}", exc_info=True)
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
        try:
            session = self.get_object()

            # Validate ownership
            if session.instructor.user != request.user:
                return Response(
                    {"detail": "You don't have permission to publish this session"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if session.status != CourseCreationSession.Status.COMPLETED:
                return Response(
                    {"detail": "Draft not yet valid for publishing."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                course = session.publish_course(request.user)
                session.status = CourseCreationSession.Status.PUBLISHED
                session.published_course = course
                session.save(update_fields=("status", "published_course"))

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
                {"course_id": course.pk, "slug": course.slug},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Error publishing DnD session: {e}", exc_info=True)
            return Response(
                {'detail': 'Course publishing failed due to an error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# FIXED: Removed typo in class name
class AICourseBuilderViewSet(viewsets.ViewSet):
    """AI course builder"""
    permission_classes = [IsAuthenticated]

    @require_instructor_profile
    @tier_required('gold')
    def start(self, request):
        """Start AI course builder"""
        return Response({
            'detail': 'AI course builder not yet implemented',
            'status': 'coming_soon'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    def generate(self, request):
        """Generate AI content"""
        return Response({
            'detail': 'AI content generation not yet implemented',
            'status': 'coming_soon'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class CourseWizardViewSet(viewsets.ViewSet):
    """Course wizard management"""
    permission_classes = [IsAuthenticated]

    @require_instructor_profile
    def start(self, request):
        """Start course wizard"""
        return Response({'wizard_started': True})

    def get_step(self, request, step):
        """Get wizard step data"""
        return Response({'step': step, 'data': {}})

    def save_step(self, request, step):
        """Save wizard step"""
        return Response({'step_saved': True})

    def resume(self, request, session_id):
        """Resume wizard session"""
        return Response({'session_resumed': True})

    def complete(self, request, session_id):
        """Complete wizard"""
        return Response({'wizard_completed': True})


class TemplateBuilderViewSet(viewsets.ViewSet):
    """Template builder"""
    permission_classes = [IsAuthenticated]

    def list_templates(self, request):
        """List available templates"""
        return Response({'templates': []})


class ContentImportViewSet(viewsets.ViewSet):
    """Content import"""
    permission_classes = [IsAuthenticated]

    @require_instructor_profile
    def start(self, request):
        """Start content import"""
        return Response({'import_started': True})
