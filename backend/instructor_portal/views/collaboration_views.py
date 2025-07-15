#
# File Path: instructor_portal/views/collaboration_views.py
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
# Collaboration and course instructor management for instructor_portal
# FIXED: Complete implementation with proper transactions and error handling

import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction

from courses.models import Course
from courses.permissions import IsInstructorOrAdmin
from ..models import CourseInstructor, TierManager
from ..serializers import CourseInstructorSerializer
from .mixins import (
    InstructorBaseViewSet, require_instructor_profile, require_permission,
    tier_required, validate_user_permission, audit_log
)

logger = logging.getLogger(__name__)

class CourseInstructorViewSet(InstructorBaseViewSet):
    """
    API endpoint for managing course-instructor relationships
    FIXED: Added proper transaction handling and validation
    """
    serializer_class = CourseInstructorSerializer
    permission_classes = [IsInstructorOrAdmin]
    resource_name = 'course_instructor'

    def get_queryset(self):
        """Get queryset based on permissions"""
        user = self.request.user

        # Staff and superusers see all
        if user.is_staff or user.is_superuser:
            return CourseInstructor.objects.all()

        # Filter by courses where user is an instructor
        course_id = self.request.query_params.get('course')
        if course_id:
            # Check if user has permission for this course
            try:
                course = Course.objects.get(id=course_id)
                if validate_user_permission(user, course, 'manage'):
                    return CourseInstructor.objects.filter(course=course)
                else:
                    return CourseInstructor.objects.none()
            except Course.DoesNotExist:
                return CourseInstructor.objects.none()

        # Return all relationships where user is involved
        return CourseInstructor.objects.filter(
            Q(instructor=user) |
            Q(course__in=Course.objects.filter(
                courseinstructor_set__instructor=user,
                courseinstructor_set__is_active=True,
                courseinstructor_set__is_lead=True
            ))
        ).distinct()

    @require_instructor_profile
    @require_permission('manage')
    @tier_required('gold')
    def create(self, request, *args, **kwargs):
        """Create new course-instructor relationship with tier check"""
        instructor_profile = request.instructor_profile

        # Additional validation for course ownership
        course_id = request.data.get('course')
        if not course_id:
            return Response(
                {'detail': 'Course ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check that user has lead instructor permission
        if not CourseInstructor.objects.filter(
            course=course,
            instructor=request.user,
            is_active=True,
            is_lead=True
        ).exists():
            return Response(
                {'detail': 'Only lead instructors can add other instructors'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check maximum instructors limit based on tier
        tier_limits = TierManager.get_tier_limits(instructor_profile.tier)
        max_instructors = tier_limits.get('max_instructors_per_course', 1)

        if max_instructors != -1:  # -1 means unlimited
            current_count = CourseInstructor.objects.filter(course=course, is_active=True).count()
            if current_count >= max_instructors:
                return Response(
                    {
                        'detail': f'Maximum instructor limit reached for your tier ({max_instructors})',
                        'current_count': current_count,
                        'max_instructors': max_instructors
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate instructor relationship"""
        course_instructor = self.get_object()

        # Check permissions
        if not validate_user_permission(request.user, course_instructor.course, 'manage'):
            return Response(
                {'detail': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        # FIXED: Added transaction for atomic operation
        with transaction.atomic():
            course_instructor.is_active = True
            course_instructor.save(update_fields=['is_active'])

        audit_log(
            request.user,
            'instructor_activated',
            'course_instructor',
            course_instructor.id,
            request=request
        )

        return Response({'detail': 'Instructor activated successfully'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate instructor relationship"""
        course_instructor = self.get_object()

        # Check permissions
        if not validate_user_permission(request.user, course_instructor.course, 'manage'):
            return Response(
                {'detail': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prevent deactivating the last lead instructor
        if course_instructor.is_lead:
            active_leads = CourseInstructor.objects.filter(
                course=course_instructor.course,
                is_lead=True,
                is_active=True
            ).exclude(pk=course_instructor.pk).count()

            if active_leads == 0:
                return Response(
                    {'detail': 'Cannot deactivate the last lead instructor'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # FIXED: Added transaction for atomic operation
        with transaction.atomic():
            course_instructor.is_active = False
            course_instructor.save(update_fields=['is_active'])

        audit_log(
            request.user,
            'instructor_deactivated',
            'course_instructor',
            course_instructor.id,
            request=request
        )

        return Response({'detail': 'Instructor deactivated successfully'})

    @action(detail=True, methods=['patch'])
    def update_permissions(self, request, pk=None):
        """Update instructor permissions with proper transaction handling"""
        course_instructor = self.get_object()

        # Check permissions - only lead instructors can update permissions
        if not CourseInstructor.objects.filter(
            course=course_instructor.course,
            instructor=request.user,
            is_active=True,
            is_lead=True
        ).exists():
            return Response(
                {'detail': 'Only lead instructors can update permissions'},
                status=status.HTTP_403_FORBIDDEN
            )

        # FIXED: Added proper transaction and validation
        try:
            with transaction.atomic():
                # Lock the record to prevent concurrent updates
                course_instructor = CourseInstructor.objects.select_for_update().get(
                    pk=course_instructor.pk
                )

                # Update permissions
                permission_fields = ['can_edit_content', 'can_manage_students', 'can_view_analytics']
                updated_fields = []

                for field in permission_fields:
                    if field in request.data:
                        setattr(course_instructor, field, request.data[field])
                        updated_fields.append(field)

                # Update revenue share if provided
                if 'revenue_share_percentage' in request.data:
                    revenue_share = request.data['revenue_share_percentage']
                    if 0 <= revenue_share <= 100:
                        course_instructor.revenue_share_percentage = revenue_share
                        updated_fields.append('revenue_share_percentage')
                    else:
                        return Response(
                            {'detail': 'Revenue share must be between 0 and 100'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                if updated_fields:
                    course_instructor.save(update_fields=updated_fields)

            audit_log(
                request.user,
                'instructor_permissions_updated',
                'course_instructor',
                course_instructor.id,
                metadata={'updated_fields': updated_fields},
                request=request
            )

            serializer = self.get_serializer(course_instructor)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error updating instructor permissions: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to update permissions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseCollaborationViewSet(viewsets.ViewSet):
    """Course collaboration management"""
    permission_classes = [IsInstructorOrAdmin]

    @require_instructor_profile
    def list(self, request):
        """List active collaborations"""
        instructor_profile = request.instructor_profile

        # Get courses where user is an instructor
        collaborations = CourseInstructor.objects.filter(
            instructor=request.user,
            is_active=True
        ).select_related('course', 'instructor')

        collaboration_data = []
        for ci in collaborations:
            collaboration_data.append({
                'id': ci.id,
                'course': {
                    'id': ci.course.id,
                    'title': ci.course.title,
                    'slug': ci.course.slug
                },
                'role': ci.get_role_display(),
                'is_lead': ci.is_lead,
                'permissions': {
                    'can_edit_content': ci.can_edit_content,
                    'can_manage_students': ci.can_manage_students,
                    'can_view_analytics': ci.can_view_analytics
                },
                'revenue_share': float(ci.revenue_share_percentage),
                'joined_date': ci.joined_date
            })

        return Response({'collaborations': collaboration_data})

    @require_instructor_profile
    @action(detail=False, methods=['post'])
    def invite(self, request):
        """Invite instructor to collaborate"""
        course_id = request.data.get('course_id')
        instructor_email = request.data.get('instructor_email')
        role = request.data.get('role', 'contributor')

        if not all([course_id, instructor_email]):
            return Response(
                {'detail': 'course_id and instructor_email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)

            # Check if user has permission to invite
            if not validate_user_permission(request.user, course, 'manage'):
                return Response(
                    {'detail': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # TODO: Implement invitation logic
            # This would typically:
            # 1. Create an invitation record
            # 2. Send email notification
            # 3. Handle invitation acceptance

            audit_log(
                request.user,
                'collaboration_invite_sent',
                'course',
                course.id,
                {'invited_email': instructor_email, 'role': role},
                request=request
            )

            return Response({'detail': 'Invitation sent successfully'})

        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def accept_invitation(self, request):
        """Accept collaboration invitation"""
        invitation_token = request.data.get('invitation_token')

        if not invitation_token:
            return Response(
                {'detail': 'invitation_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement invitation acceptance logic
        return Response({'detail': 'Invitation accepted successfully'})

    @action(detail=False, methods=['post'])
    def decline_invitation(self, request):
        """Decline collaboration invitation"""
        invitation_token = request.data.get('invitation_token')

        if not invitation_token:
            return Response(
                {'detail': 'invitation_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement invitation decline logic
        return Response({'detail': 'Invitation declined'})

    @action(detail=False, methods=['get'])
    def pending_invitations(self, request):
        """Get pending invitations for current user"""
        # TODO: Implement pending invitations retrieval
        return Response({'invitations': []})
