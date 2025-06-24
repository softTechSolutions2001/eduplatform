"""
Celery tasks for AI Course Builder functionality.

This module defines asynchronous tasks for handling long-running AI operations
such as course outline, module, and lesson generation. Using Celery allows
these operations to run in the background without blocking the main thread.

Functions:
- generate_course_outline_task: Creates a course outline based on course info
- generate_module_content_task: Creates detailed content for a course module
- generate_lesson_content_task: Creates content for a specific lesson
- generate_assessments_task: Creates quiz questions for a course
"""

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, Retry
from celery.signals import task_failure, task_success, task_revoked
import logging
import time
import traceback
import json
from django.conf import settings
from django.db import transaction
from .models import AICourseBuilderDraft

logger = logging.getLogger(__name__)

# Task status tracking
class TaskStatus:
    """Helper class for updating task progress during execution."""

    @staticmethod
    def update_progress(task, percent, message=""):
        """
        Update the current task's progress.

        Args:
            task: The Celery task instance
            percent (int): Current progress percentage (0-100)
            message (str): Optional status message
        """
        if hasattr(task, 'update_state'):
            task.update_state(
                state='PROGRESS',
                meta={
                    'progress': {
                        'percent': percent,
                        'message': message
                    }
                }
            )
            logger.info(f"Task {task.request.id}: {percent}% - {message}")

# Error handling for tasks
@task_failure.connect
def log_failed_task(sender=None, task_id=None, exception=None, **kwargs):
    """Log information about failed Celery tasks."""
    logger.error(f"Task {task_id} failed: {exception}")

    # Try to update the draft with error information
    try:
        # Extract draft_id from task args if possible
        args = kwargs.get('args', [])
        if args and isinstance(args[0], int):
            draft_id = args[0]
            draft = AICourseBuilderDraft.objects.filter(id=draft_id).first()

            if draft and draft.generation_metadata:
                # Add error info to metadata
                task_errors = draft.generation_metadata.get('task_errors', {})
                task_errors[task_id] = {
                    'error': str(exception),
                    'traceback': traceback.format_exc(),
                    'timestamp': time.time()
                }
                draft.generation_metadata['task_errors'] = task_errors
                draft.save(update_fields=['generation_metadata'])
    except Exception as e:
        logger.error(f"Error logging task failure metadata: {e}")


@shared_task(
    bind=True,
    name='ai_course_builder.generate_course_outline',
    soft_time_limit=300,  # 5 minutes
    time_limit=360,       # 6 minutes
    max_retries=2,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    acks_late=True
)
def generate_course_outline_task(self, draft_id, course_info=None):
    """
    Generate a course outline with modules and lesson structure.

    This task communicates with an AI service to create a comprehensive
    course outline based on the provided course information.

    Args:
        draft_id (int): ID of the AICourseBuilderDraft
        course_info (dict, optional): Course information to base the outline on

    Returns:
        dict: The generated outline data
    """
    try:
        # Get the draft object
        draft = AICourseBuilderDraft.objects.get(id=draft_id)

        # Update progress
        TaskStatus.update_progress(self, 10, "Preparing course information")

        # In a production implementation, this would call an AI service
        # For demonstration, we'll simulate an AI response with a delay
        TaskStatus.update_progress(self, 30, "Connecting to AI service")
        time.sleep(1)  # Simulate connection

        TaskStatus.update_progress(self, 50, "Generating course structure")
        time.sleep(1)  # Simulate processing

        TaskStatus.update_progress(self, 70, "Creating modules and lessons")
        time.sleep(1)  # Simulate more processing

        # Generate a placeholder outline (replace with actual AI integration)
        outline_data = {
            "modules": [
                {
                    "title": f"Module 1: Introduction to {draft.title}",
                    "description": "This module introduces the fundamental concepts of the course.",
                    "lessons": [
                        {"title": "Getting Started", "type": "video"},
                        {"title": "Core Concepts", "type": "reading"},
                        {"title": "Practical Application", "type": "interactive"}
                    ]
                },
                {
                    "title": "Module 2: Intermediate Topics",
                    "description": "Building on the fundamentals, this module explores more advanced topics.",
                    "lessons": [
                        {"title": "Advanced Techniques", "type": "video"},
                        {"title": "Case Studies", "type": "reading"},
                        {"title": "Hands-on Exercise", "type": "lab"}
                    ]
                }
            ]
        }        # Final progress update
        TaskStatus.update_progress(self, 90, "Finalizing course outline")

        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Update the draft with the outline data
            draft.outline = outline_data
            draft.has_outline = True
            draft.save()

            # Update metadata with successful completion
            if not draft.generation_metadata:
                draft.generation_metadata = {}

            draft.generation_metadata['outline_completed'] = True
            draft.generation_metadata['outline_completed_at'] = time.time()
            draft.save(update_fields=['generation_metadata'])

        TaskStatus.update_progress(self, 100, "Course outline completed")

        return {
            "status": "success",
            "draft_id": draft_id,
            "outline": outline_data
        }

    except AICourseBuilderDraft.DoesNotExist:
        error_msg = f"Draft with ID {draft_id} not found"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    except SoftTimeLimitExceeded:
        error_msg = f"Time limit exceeded generating outline for draft {draft_id}"
        logger.error(error_msg)
        # Record the error in the draft metadata
        try:
            draft = AICourseBuilderDraft.objects.get(id=draft_id)
            if not draft.generation_metadata:
                draft.generation_metadata = {}
            draft.generation_metadata['outline_error'] = error_msg
            draft.save(update_fields=['generation_metadata'])
        except Exception:
            pass
        self.retry(countdown=60)  # Retry after 1 minute
    except Exception as e:
        error_msg = f"Error generating course outline for draft {draft_id}: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)  # Log full traceback
        return {
            "status": "error",
            "message": str(e)
        }


@shared_task(
    bind=True,
    name='ai_course_builder.generate_module_content',
    soft_time_limit=180,  # 3 minutes
    time_limit=240,       # 4 minutes
    max_retries=2
)
def generate_module_content_task(self, draft_id, module_index):
    """
    Generate detailed content for a specific module.

    Args:
        draft_id (int): ID of the AICourseBuilderDraft
        module_index (int): Index of the module to generate content for

    Returns:
        dict: The generated module content
    """
    try:
        # Get the draft object
        draft = AICourseBuilderDraft.objects.get(id=draft_id)

        # Ensure the module exists in the outline
        if not draft.has_outline or not draft.outline.get('modules') or \
           module_index >= len(draft.outline['modules']):
            return {
                "status": "error",
                "message": "Invalid module index or outline not generated"
            }

        # In a production implementation, this would call an AI service
        # For demonstration, simulate an AI response with a delay
        time.sleep(2)  # Simulate AI processing time

        # Generate placeholder content for the module
        module_data = draft.outline['modules'][module_index]
        module_data['content'] = f"Detailed content for module: {module_data['title']}"

        # Add additional information
        module_data['learning_outcomes'] = [
            "Understand the core concepts presented in this module",
            "Apply the techniques in practical scenarios",
            "Analyze and evaluate different approaches"
        ]

        # Update the content in the draft
        if 'content' not in draft.content:
            draft.content['content'] = {}
        draft.content['content'][str(module_index)] = module_data

        # Update the has_modules flag if this is the first module
        if not draft.has_modules:
            draft.has_modules = True

        draft.save()

        return {
            "status": "success",
            "draft_id": draft_id,
            "module": module_data,
            "moduleIndex": module_index
        }

    except AICourseBuilderDraft.DoesNotExist:
        logger.error(f"Draft with ID {draft_id} not found")
        return {
            "status": "error",
            "message": f"Draft with ID {draft_id} not found"
        }
    except SoftTimeLimitExceeded:
        logger.error(f"Time limit exceeded generating module {module_index} for draft {draft_id}")
        self.retry(countdown=30)  # Retry after 30 seconds
    except Exception as e:
        logger.error(f"Error generating module content for draft {draft_id}, module {module_index}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@shared_task(
    bind=True,
    name='ai_course_builder.generate_lesson_content',
    soft_time_limit=120,  # 2 minutes
    time_limit=180,       # 3 minutes
    max_retries=2
)
def generate_lesson_content_task(self, draft_id, module_index, lesson_index):
    """
    Generate detailed content for a specific lesson within a module.

    Args:
        draft_id (int): ID of the AICourseBuilderDraft
        module_index (int): Index of the parent module
        lesson_index (int): Index of the lesson to generate content for

    Returns:
        dict: The generated lesson content
    """
    try:
        # Get the draft object
        draft = AICourseBuilderDraft.objects.get(id=draft_id)

        # Validate the indices
        try:
            module = draft.outline['modules'][module_index]
            lesson_info = module['lessons'][lesson_index]
        except (KeyError, IndexError):
            return {
                "status": "error",
                "message": "Invalid module or lesson index"
            }

        # In a production implementation, this would call an AI service
        # For demonstration, simulate an AI response with a delay
        time.sleep(1.5)  # Simulate AI processing time        # Generate placeholder content for the lesson
        lesson_data = {
            **lesson_info,
            'content': f"<h2>Welcome to {lesson_info['title']}</h2><p>This comprehensive lesson covers all essential aspects of the topic, providing detailed explanations and examples to enhance understanding.</p><h3>Key Concepts</h3><p>The main ideas you will learn in this lesson include fundamental principles, practical applications, and advanced techniques.</p><h4>Practical Application</h4><p>Through hands-on exercises, you will apply these concepts in real-world scenarios.</p>",
            'duration_minutes': 15,
            'learning_objectives': [
                "Understand the core principles discussed in this lesson",
                "Apply the knowledge in practical situations"
            ]
        }

        # Update the content in the draft
        if 'lessons' not in draft.content:
            draft.content['lessons'] = {}

        lesson_key = f"{module_index}-{lesson_index}"
        draft.content['lessons'][lesson_key] = lesson_data

        # Update the has_lessons flag if this is the first lesson
        if not draft.has_lessons:
            draft.has_lessons = True

        draft.save()

        return {
            "status": "success",
            "draft_id": draft_id,
            "lesson": lesson_data,
            "moduleIndex": module_index,
            "lessonIndex": lesson_index
        }

    except AICourseBuilderDraft.DoesNotExist:
        logger.error(f"Draft with ID {draft_id} not found")
        return {
            "status": "error",
            "message": f"Draft with ID {draft_id} not found"
        }
    except SoftTimeLimitExceeded:
        logger.error(f"Time limit exceeded generating lesson for draft {draft_id}, module {module_index}, lesson {lesson_index}")
        self.retry(countdown=30)  # Retry after 30 seconds
    except Exception as e:
        logger.error(f"Error generating lesson content for draft {draft_id}, module {module_index}, lesson {lesson_index}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@shared_task(
    bind=True,
    name='ai_course_builder.generate_assessments',
    soft_time_limit=240,  # 4 minutes
    time_limit=300,       # 5 minutes
    max_retries=2
)
def generate_assessments_task(self, draft_id):
    """
    Generate assessments (quizzes) for the course.

    Args:
        draft_id (int): ID of the AICourseBuilderDraft

    Returns:
        dict: The generated assessment data
    """
    try:
        # Get the draft object
        draft = AICourseBuilderDraft.objects.get(id=draft_id)

        # In a production implementation, this would call an AI service
        # For demonstration, simulate an AI response with a delay
        time.sleep(2.5)  # Simulate AI processing time

        # Generate placeholder assessments based on the course modules
        assessments_data = {"quizzes": []}

        # Create a quiz for each module
        for i, module in enumerate(draft.outline.get('modules', [])):
            quiz = {
                'title': f"Assessment: {module.get('title', f'Module {i+1}')}",
                'moduleIndex': i,
                'description': f"Test your knowledge of {module.get('title', f'Module {i+1}')}",
                'questions': []
            }

            # Add 3-5 questions per module
            num_questions = min(len(module.get('lessons', [])) + 2, 5)
            for j in range(num_questions):
                quiz['questions'].append({
                    'question': f"Question {j+1} about {module.get('title', 'this module')}?",
                    'options': [
                        {'text': 'Option A', 'is_correct': j % 4 == 0},
                        {'text': 'Option B', 'is_correct': j % 4 == 1},
                        {'text': 'Option C', 'is_correct': j % 4 == 2},
                        {'text': 'Option D', 'is_correct': j % 4 == 3}
                    ]
                })

            assessments_data['quizzes'].append(quiz)

        # Update the draft with the assessments data
        draft.assessments = assessments_data
        draft.has_assessments = True
        draft.save()

        return {
            "status": "success",
            "draft_id": draft_id,
            "assessments": assessments_data
        }

    except AICourseBuilderDraft.DoesNotExist:
        logger.error(f"Draft with ID {draft_id} not found")
        return {
            "status": "error",
            "message": f"Draft with ID {draft_id} not found"
        }
    except SoftTimeLimitExceeded:
        logger.error(f"Time limit exceeded generating assessments for draft {draft_id}")
        self.retry(countdown=60)  # Retry after 1 minute
    except Exception as e:
        logger.error(f"Error generating assessments for draft {draft_id}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
