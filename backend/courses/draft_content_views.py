# File Path: backend/courses/draft_content_views.py
# Date Created: 2025-06-24 08:50:00
# Current Date and Time (UTC): 2025-06-24 08:49:22
# Author: saiacupunctureFolllow
# Version: 1.0.0

import logging
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from instructor_portal.models import DraftCourseContent, CourseCreationSession
from instructor_portal.serializers import DraftCourseContentSerializer
from instructor_portal.views import audit_log

logger = logging.getLogger(__name__)

class DraftCourseContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for draft course content management
    """
    serializer_class = DraftCourseContentSerializer
    permission_classes = [IsAuthenticated]
    queryset = DraftCourseContent.objects.all()

    def get_queryset(self):
        """Get draft content with proper filtering"""
        queryset = super().get_queryset()

        # Filter by session
        session_id = self.request.query_params.get('session_id')
        if session_id:
            queryset = queryset.filter(session__session_id=session_id)

        # Only return user's own content
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(
                session__instructor__user=self.request.user
            )

        return queryset.order_by('order')

    def perform_create(self, serializer):
        """Add security validation before creating content"""
        session = serializer.validated_data.get('session')

        # Verify user owns this session
        if session and session.instructor.user != self.request.user:
            raise serializers.ValidationError("You don't have permission to add content to this session")

        super().perform_create(serializer)

        audit_log(
            self.request.user,
            'draft_content_created',
            'draft_content',
            serializer.instance.id,
            {
                'content_type': serializer.instance.content_type,
                'session_id': str(session.session_id) if session else None
            },
            success=True,
            request=self.request
        )

    @action(detail=False, methods=["patch"], url_path="reorder")
    def bulk_reorder(self, request, *args, **kwargs):
        """
        Reorder multiple draft content blocks at once.

        Payload:
        {
          "items": [
            {"id": 17, "order": 1},
            {"id": 42, "order": 2},
            ...
          ]
        }
        """
        items = request.data.get("items", [])
        if not items or not isinstance(items, list):
            return Response(
                {"detail": "items[] list required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limit the number of items for security
        max_items = getattr(settings, 'MAX_BULK_OPERATION_SIZE', 100)
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

                if not self.request.user.is_staff and not self.request.user.is_superuser:
                    queryset = queryset.filter(
                        session__instructor__user=self.request.user
                    )

                # Use select_for_update to prevent race conditions
                rows = queryset.select_for_update(of=("self",))

                if rows.count() != len(draft_ids):
                    audit_log(
                        self.request.user,
                        'bulk_reorder_failed',
                        'draft_content',
                        None,
                        {'error': 'Some IDs not found or permission denied'},
                        success=False,
                        request=request
                    )
                    return Response(
                        {"detail": "Some draft-block IDs not found or you don't have permission."},
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
                    'bulk_reorder_completed',
                    'draft_content',
                    None,
                    {'item_count': len(items), 'sessions_updated': len(sessions)},
                    success=True,
                    request=request
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error in bulk_reorder: {e}", exc_info=True)
            audit_log(
                self.request.user,
                'bulk_reorder_error',
                'draft_content',
                None,
                {'error': str(e)},
                success=False,
                request=request
            )
            return Response(
                {"detail": "An error occurred during reordering."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
