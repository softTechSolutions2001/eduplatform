"""
Views for AI Course Builder functionality.

This module defines viewsets and API endpoints for interacting with
the AI course builder features, including draft management and
AI-assisted course generation operations.

Classes:
- AICourseBuilderHealthView: Simple health check endpoint
- AICourseBuilderDraftViewSet: Main viewset for draft management
"""

from celery.result import AsyncResult
from courses.models import Assessment, Course, Lesson, Module, Question
from courses.serializers import CourseSerializer
from courses.serializers.utils import HealthCheckSerializer
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from instructor_portal.models import CourseInstructor
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AICourseBuilderDraft
from .serializers import AICourseBuilderDraftSerializer
from .tasks import (
    generate_assessments_task,
    generate_course_outline_task,
    generate_lesson_content_task,
    generate_module_content_task,
)


class AICourseBuilderHealthView(APIView):
    """
    Simple health check endpoint for AI course builder services.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HealthCheckSerializer  # Add this line

    def get(self, request):
        """
        Returns a simple status check to verify the API is operational.
        """
        return Response(
            {
                "status": "ok",
                "message": "AI Course Builder API is operational",
                "timestamp": timezone.now().isoformat(),
            }
        )


class AICourseBuilderDraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI Course Builder drafts.

    This viewset provides endpoints for creating, retrieving, updating,
    and finalizing course drafts created with the AI course builder.

    Actions:
    - initialize: Create a new draft
    - partial_update: Save changes to a draft
    - finalize: Create a published course from the draft
    - outline: Generate a course outline (async)
    - module: Generate content for a specific module (async)
    - lesson: Generate content for a specific lesson (async)
    - assessments: Generate assessments for the course (async)
    - task_status: Check the status of an async task
    """

    serializer_class = AICourseBuilderDraftSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"  # Changed from "pk" to "id" for consistency
    lookup_value_regex = r"\d+"  # Ensure it's treated as an integer

    def get_queryset(self):
        """
        Filter drafts to only include those belonging to the current user.
        """
        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return AICourseBuilderDraft.objects.none()

        return AICourseBuilderDraft.objects.filter(instructor=user).order_by(
            "-updated_at"
        )

    @action(detail=False, methods=["post"])
    def initialize(self, request):
        """
        Create a new AI course builder draft.

        Returns:
            Response with the new draft ID and status
        """
        # Create a new draft owned by the current user
        draft = AICourseBuilderDraft.objects.create(
            instructor=request.user, status="DRAFT"
        )

        serializer = self.get_serializer(draft)
        return Response(
            {
                "status": "success",
                "message": "New course draft initialized",
                "draftId": draft.id,
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Update a draft with new data (handles autosave and manual saves).

        This method is called for PATCH requests and supports partial updates
        to any fields in the draft.

        Returns:
            Response with the updated draft data
        """
        instance = self.get_object()

        # Only allow the owner to update their draft
        if instance.instructor != request.user:
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to update this draft",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update the draft with the provided data
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Draft updated successfully",
                "data": serializer.data,
            }
        )

    @action(detail=True, methods=["post"])
    def outline(self, request, id=None):
        """
        Generate a course outline based on basic course information.

        This method uses a Celery task to handle the long-running AI operation.
        It immediately returns a task ID and status, which the client can use
        to poll for the completed result.

        Returns:
            Response with the task ID for the outline generation task
        """
        draft = self.get_object()

        # Get basic course info from the request or draft
        course_info = request.data.get("courseInfo", {})
        if not course_info:
            # If no course info provided, use data from the draft
            course_info = {
                "title": draft.title,
                "description": draft.description,
                "objectives": draft.course_objectives,
                "target_audience": draft.target_audience,
                "difficulty_level": draft.difficulty_level,
            }

        # Enqueue a Celery task for outline generation
        task = generate_course_outline_task.delay(draft.id, course_info)

        # Store the task ID in the draft's metadata
        if not draft.generation_metadata:
            draft.generation_metadata = {}

        draft.generation_metadata["outline_task_id"] = task.id
        draft.save(update_fields=["generation_metadata"])

        return Response(
            {
                "status": "pending",
                "message": "Course outline generation started",
                "taskId": task.id,
                "pollUrl": f"/api/instructor/ai-course-builder/{draft.id}/task-status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def module(self, request, id=None):
        """
        Generate detailed content for a specific module.

        Uses a Celery task to generate module content asynchronously.

        Request Parameters:
            moduleIndex (int): Index of the module to generate content for

        Returns:
            Response with task info for the module generation
        """
        draft = self.get_object()
        module_index = request.data.get("moduleIndex")

        if module_index is None:
            return Response(
                {"status": "error", "message": "Module index is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Convert to integer if it's a string
            module_index = int(module_index)
        except ValueError:
            return Response(
                {"status": "error", "message": "Module index must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the module exists in the outline
        if (
            not draft.has_outline
            or not draft.outline.get("modules")
            or module_index >= len(draft.outline["modules"])
        ):
            return Response(
                {
                    "status": "error",
                    "message": "Invalid module index or outline not generated",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue a Celery task for module content generation
        task = generate_module_content_task.delay(draft.id, module_index)

        # Store the task ID in the draft's metadata
        if not draft.generation_metadata:
            draft.generation_metadata = {}

        if "module_tasks" not in draft.generation_metadata:
            draft.generation_metadata["module_tasks"] = {}

        draft.generation_metadata["module_tasks"][str(module_index)] = task.id
        draft.save(update_fields=["generation_metadata"])

        # Get the module title for better UX
        module_title = draft.outline["modules"][module_index].get(
            "title", f"Module {module_index + 1}"
        )

        return Response(
            {
                "status": "pending",
                "message": f"Generation started for module: {module_title}",
                "taskId": task.id,
                "moduleIndex": module_index,
                "pollUrl": f"/api/instructor/ai-course-builder/{draft.id}/task-status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def lesson(self, request, id=None):
        """
        Generate detailed content for a specific lesson within a module.

        Uses a Celery task to generate lesson content asynchronously.

        Request Parameters:
            moduleIndex (int): Index of the parent module
            lessonIndex (int): Index of the lesson to generate content for

        Returns:
            Response with task info for the lesson generation
        """
        draft = self.get_object()
        module_index = request.data.get("moduleIndex")
        lesson_index = request.data.get("lessonIndex")

        if module_index is None or lesson_index is None:
            return Response(
                {
                    "status": "error",
                    "message": "Module index and lesson index are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Convert to integers if they're strings
            module_index = int(module_index)
            lesson_index = int(lesson_index)
        except ValueError:
            return Response(
                {
                    "status": "error",
                    "message": "Module and lesson indices must be integers",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the indices
        try:
            module = draft.outline["modules"][module_index]
            lesson_info = module["lessons"][lesson_index]
        except (KeyError, IndexError):
            return Response(
                {"status": "error", "message": "Invalid module or lesson index"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue a Celery task for lesson content generation
        task = generate_lesson_content_task.delay(draft.id, module_index, lesson_index)

        # Store the task ID in the draft's metadata
        if not draft.generation_metadata:
            draft.generation_metadata = {}

        if "lesson_tasks" not in draft.generation_metadata:
            draft.generation_metadata["lesson_tasks"] = {}

        lesson_key = f"{module_index}-{lesson_index}"
        draft.generation_metadata["lesson_tasks"][lesson_key] = task.id
        draft.save(update_fields=["generation_metadata"])

        # Get the lesson title for better UX
        lesson_title = lesson_info.get("title", f"Lesson {lesson_index + 1}")

        return Response(
            {
                "status": "pending",
                "message": f"Generation started for lesson: {lesson_title}",
                "taskId": task.id,
                "moduleIndex": module_index,
                "lessonIndex": lesson_index,
                "pollUrl": f"/api/instructor/ai-course-builder/{draft.id}/task-status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def assessments(self, request, id=None):
        """
        Generate assessments (quizzes) for the course.

        Uses a Celery task to generate assessments asynchronously.

        Returns:
            Response with task info for the assessments generation
        """
        draft = self.get_object()

        # Ensure the draft has modules and lessons
        if not draft.has_outline or not draft.has_modules or not draft.has_lessons:
            return Response(
                {
                    "status": "error",
                    "message": "Cannot generate assessments: draft must have outline, modules, and lessons",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue a Celery task for assessments generation
        task = generate_assessments_task.delay(draft.id)

        # Store the task ID in the draft's metadata
        if not draft.generation_metadata:
            draft.generation_metadata = {}

        draft.generation_metadata["assessments_task_id"] = task.id
        draft.save(update_fields=["generation_metadata"])

        return Response(
            {
                "status": "pending",
                "message": "Assessment generation started",
                "taskId": task.id,
                "pollUrl": f"/api/instructor/ai-course-builder/{draft.id}/task-status/{task.id}/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    # File: ai_course_builder/views.py
    @action(detail=True, methods=["get"], url_path=r"task-status/(?P<task_id>[^/.]+)")
    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, location=OpenApiParameter.PATH),
            OpenApiParameter(
                "task_id", OpenApiTypes.STR, location=OpenApiParameter.PATH
            ),
        ],
        responses={200: AICourseBuilderDraftSerializer},
    )
    def task_status(self, request, id=None, task_id=None):
        """
        Check the status of an asynchronous task.

        This endpoint allows the frontend to poll for the status of
        long-running tasks like outline or content generation.
        """
        draft = self.get_object()

        # Verify the task ID exists in this draft's metadata
        # This prevents accessing tasks that belong to other drafts
        if not draft.generation_metadata:
            return Response(
                {"status": "error", "message": "No tasks found for this draft"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check all possible task locations in metadata
        task_locations = [
            draft.generation_metadata.get("outline_task_id"),
            draft.generation_metadata.get("assessments_task_id"),
        ]

        # Check module tasks
        module_tasks = draft.generation_metadata.get("module_tasks", {})
        if module_tasks:
            task_locations.extend(module_tasks.values())

        # Check lesson tasks
        lesson_tasks = draft.generation_metadata.get("lesson_tasks", {})
        if lesson_tasks:
            task_locations.extend(lesson_tasks.values())

        # If task_id not in our known tasks, reject access
        if task_id not in task_locations:
            return Response(
                {
                    "status": "error",
                    "message": "Task ID is not associated with this draft",
                    "draftId": draft.id,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check the task status via AsyncResult
        task_result = AsyncResult(task_id)

        # Return the appropriate response based on task state
        if task_result.ready():
            if task_result.successful():
                result = task_result.result
                return Response(
                    {"status": "success", "state": "COMPLETED", "result": result}
                )
            else:
                # Task failed
                error = (
                    str(task_result.result) if task_result.result else "Unknown error"
                )
                return Response(
                    {
                        "status": "error",
                        "state": "FAILED",
                        "message": f"Task failed: {error}",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            # Task is still running
            progress = {}
            if hasattr(task_result, "info") and task_result.info:
                if (
                    isinstance(task_result.info, dict)
                    and "progress" in task_result.info
                ):
                    progress = task_result.info.get("progress", {})

            return Response(
                {"status": "pending", "state": task_result.state, "progress": progress}
            )

    @action(detail=True, methods=["post"])
    def finalize(self, request, id=None):
        """
        Finalize a draft by creating a published course from it.

        This method transfers all the content from the draft to
        create a new Course instance with its related objects.

        Returns:
            Response with the newly created course ID and URL
        """
        draft = self.get_object()

        # Validate the draft has all required components
        if not all(
            [
                draft.title,
                draft.description,
                draft.has_outline,
                draft.has_modules,
                draft.has_lessons,
            ]
        ):
            return Response(
                {
                    "status": "error",
                    "message": "Draft is incomplete and cannot be finalized",
                    "missing_components": {
                        "title": not bool(draft.title),
                        "description": not bool(draft.description),
                        "outline": not draft.has_outline,
                        "modules": not draft.has_modules,
                        "lessons": not draft.has_lessons,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Use a transaction to ensure all-or-nothing creation
            with transaction.atomic():
                # Create the course
                course = Course.objects.create(
                    title=draft.title,
                    description=draft.description,
                    price=draft.price or 0.00,
                    duration_minutes=draft.duration_minutes or 0,
                    level=draft.difficulty_level or "all_levels",
                    is_published=True,
                )

                # Add the instructor
                CourseInstructor.objects.create(
                    course=course, instructor=draft.instructor, is_lead=True
                )

                # Create modules and lessons
                for i, module_data in enumerate(draft.outline.get("modules", [])):
                    module = Module.objects.create(
                        course=course,
                        title=module_data.get("title", f"Module {i+1}"),
                        description=module_data.get("description", ""),
                        order=i + 1,
                    )

                    # Create lessons for this module
                    for j, lesson_info in enumerate(module_data.get("lessons", [])):
                        # Get detailed lesson content if available
                        lesson_key = f"{i}-{j}"
                        lesson_content = draft.content.get("lessons", {}).get(
                            lesson_key, {"content": ""}
                        )

                        lesson = Lesson.objects.create(
                            module=module,
                            title=lesson_info.get("title", f"Lesson {j+1}"),
                            content=lesson_content.get("content", ""),
                            type=lesson_info.get("type", "reading"),
                            order=j + 1,
                        )

                        # Create assessment if this module has one in the draft
                        if draft.has_assessments and draft.assessments.get("quizzes"):
                            for quiz in draft.assessments["quizzes"]:
                                if quiz.get("moduleIndex") == i:
                                    assessment = Assessment.objects.create(
                                        lesson=lesson,
                                        title=quiz.get(
                                            "title", f"Quiz for {lesson.title}"
                                        ),
                                        passing_score=70,
                                    )

                                    # Create questions for this assessment
                                    for q_idx, q_data in enumerate(
                                        quiz.get("questions", [])
                                    ):
                                        Question.objects.create(
                                            assessment=assessment,
                                            question_text=q_data.get(
                                                "question", f"Question {q_idx+1}"
                                            ),
                                            question_type="multiple_choice",
                                            order=q_idx + 1,
                                        )

                # Update the draft status
                draft.status = "PUBLISHED"
                draft.save()

                # Return the new course details
                course_data = CourseSerializer(course).data

                return Response(
                    {
                        "status": "success",
                        "message": "Course published successfully",
                        "courseId": course.id,
                        "course": course_data,
                    }
                )

        except ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to create course",
                    "errors": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
