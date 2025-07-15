#
# File Path: instructor_portal/serializers/creation.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 14:07:20
# Date Revised: 2025-06-27 06:16:38
# Current Date and Time (UTC): 2025-06-27 06:16:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:16:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Creation and session serializers for instructor_portal
# Split from original serializers.py maintaining exact code compatibility

import json
import logging
import os
from datetime import timedelta
from rest_framework import serializers
from django.db import transaction, models
from django.utils import timezone

from ..models import (
    InstructorProfile, CourseCreationSession, CourseTemplate,
    DraftCourseContent, CourseContentDraft
)
from courses.models import Category  # Import Category from courses
from .mixins import JsonFieldMixin
from .utils import validate_instructor_tier_access, calculate_content_hash, validate_file_path_security

logger = logging.getLogger(__name__)

class CourseCreationSessionSerializer(serializers.ModelSerializer):
    """Serializer for course creation session management"""
    instructor_name = serializers.CharField(source='instructor.display_name', read_only=True)
    instructor_tier = serializers.CharField(source='instructor.tier', read_only=True)
    creation_method_display = serializers.CharField(source='get_creation_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    validation_status = serializers.SerializerMethodField()
    step_configuration = serializers.SerializerMethodField()
    resume_data = serializers.SerializerMethodField()

    # Backward compatibility fields
    completed_steps = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    last_auto_save = serializers.SerializerMethodField()
    auto_save_data = serializers.SerializerMethodField()
    draft_course = serializers.SerializerMethodField()
    quality_score = serializers.SerializerMethodField()
    ai_prompt = serializers.SerializerMethodField()
    ai_suggestions = serializers.SerializerMethodField()

    class Meta:
        model = CourseCreationSession
        fields = [
            'id', 'session_id', 'instructor', 'instructor_name', 'instructor_tier',
            'creation_method', 'creation_method_display', 'status', 'status_display',
            'course_data', 'current_step', 'total_steps', 'steps_completed', 'completion_percentage',
            'last_auto_save', 'auto_save_data', 'validation_errors', 'quality_score',
            'ai_prompt', 'ai_suggestions', 'template_used', 'draft_course', 'published_course',
            'validation_status', 'step_configuration', 'resume_data',
            'created_date', 'updated_date', 'expires_at',
            # Include backward compatibility fields explicitly
            'completed_steps', 'progress_percentage',
            'ai_prompts_used',  # New field from the model
        ]
        read_only_fields = [
            'id', 'session_id', 'progress_percentage', 'completion_percentage',
            'last_auto_save', 'validation_errors', 'published_course',
            'created_date', 'updated_date'
        ]

    # Backward compatibility getters
    def get_completed_steps(self, obj):
        """Backward compatibility getter for completed_steps"""
        return obj.steps_completed

    def get_progress_percentage(self, obj):
        """Backward compatibility getter for progress_percentage"""
        return obj.completion_percentage

    def get_last_auto_save(self, obj):
        """Backward compatibility getter for last_auto_save"""
        return obj.updated_date

    def get_auto_save_data(self, obj):
        """Backward compatibility getter for auto_save_data"""
        return obj.course_data

    def get_draft_course(self, obj):
        """Backward compatibility getter for draft_course"""
        # This would link to any associated draft course
        return None

    def get_quality_score(self, obj):
        """Backward compatibility getter for quality_score"""
        # Calculate quality score from validation status if possible
        try:
            return self._calculate_completeness_score(obj)
        except Exception:
            return 0

    def get_ai_prompt(self, obj):
        """Backward compatibility getter for ai_prompt"""
        if obj.ai_prompts_used and len(obj.ai_prompts_used) > 0:
            return obj.ai_prompts_used[0]
        return ""

    def get_ai_suggestions(self, obj):
        """Backward compatibility getter for ai_suggestions"""
        # Return empty list as this is not stored in the same way anymore
        return []

    def get_validation_status(self, obj):
        """Get current validation status"""
        try:
            errors = obj.validate_session_data()
            return {
                'is_valid': len(errors) == 0,
                'error_count': len(errors),
                'errors': errors[:5],  # Limit to first 5 errors
                'completeness_score': self._calculate_completeness_score(obj)
            }
        except Exception as e:
            logger.error(f"Error getting validation status: {e}")
            return {'is_valid': False, 'error_count': 1, 'errors': ['Validation check failed']}

    def get_step_configuration(self, obj):
        """Get step configuration based on creation method"""
        step_configs = {
            CourseCreationSession.CreationMethod.WIZARD: {
                'steps': [
                    {'number': 1, 'name': 'Basic Information', 'required_fields': ['title', 'description', 'category']},
                    {'number': 2, 'name': 'Course Structure', 'required_fields': ['modules']},
                    {'number': 3, 'name': 'Content Creation', 'required_fields': ['lessons']},
                    {'number': 4, 'name': 'Resources & Materials', 'required_fields': []},
                    {'number': 5, 'name': 'Pricing & Publishing', 'required_fields': ['price']},
                    {'number': 6, 'name': 'Review & Publish', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.AI_ASSISTED: {
                'steps': [
                    {'number': 1, 'name': 'AI Prompt', 'required_fields': ['ai_prompt']},
                    {'number': 2, 'name': 'Generated Content Review', 'required_fields': []},
                    {'number': 3, 'name': 'Content Refinement', 'required_fields': []},
                    {'number': 4, 'name': 'Finalization', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.TEMPLATE: {
                'steps': [
                    {'number': 1, 'name': 'Template Selection', 'required_fields': ['template_used']},
                    {'number': 2, 'name': 'Customization', 'required_fields': []},
                    {'number': 3, 'name': 'Content Population', 'required_fields': []},
                    {'number': 4, 'name': 'Review & Publish', 'required_fields': []}
                ]
            },
            CourseCreationSession.CreationMethod.BULK_IMPORT: {
                'steps': [
                    {'number': 1, 'name': 'Course Setup', 'required_fields': ['title', 'description']},
                    {'number': 2, 'name': 'Content Assembly', 'required_fields': []},
                    {'number': 3, 'name': 'Organization', 'required_fields': []},
                    {'number': 4, 'name': 'Publishing Setup', 'required_fields': []}
                ]
            }
        }
        # For backward compatibility, support the old AI_BUILDER name
        step_configs[CourseCreationSession.CreationMethod.AI_BUILDER] = step_configs[CourseCreationSession.CreationMethod.AI_ASSISTED]

        return step_configs.get(obj.creation_method, {'steps': []})

    def get_resume_data(self, obj):
        """Get data needed to resume course creation"""
        try:
            course_data = obj.course_data
            return {
                'current_step': obj.current_step,
                'total_steps': obj.total_steps,
                'completed_steps': obj.steps_completed,
                'completion_percentage': float(obj.completion_percentage),
                'has_title': bool(course_data.get('title')),
                'has_category': bool(course_data.get('category_id')),
                'modules_count': len(course_data.get('modules', [])),
                'creation_method': obj.creation_method,
                'status': obj.status
            }
        except Exception as e:
            logger.error(f"Error getting resume data: {e}")
            return {}

    def _calculate_completeness_score(self, obj):
        """Calculate course completeness percentage"""
        try:
            course_data = obj.course_data
            total_checks = 0
            completed_checks = 0

            # Basic information checks
            basic_fields = ['title', 'description', 'category_id']
            for field in basic_fields:
                total_checks += 1
                if course_data.get(field):
                    completed_checks += 1

            # Module and lesson checks
            modules = course_data.get('modules', [])
            if modules:
                total_checks += 1
                completed_checks += 1

                for module in modules:
                    total_checks += 2  # title and lessons
                    if module.get('title'):
                        completed_checks += 1

                    lessons = module.get('lessons', [])
                    if lessons:
                        completed_checks += 1

                        for lesson in lessons:
                            total_checks += 2  # title and content
                            if lesson.get('title'):
                                completed_checks += 1
                            if lesson.get('content') or lesson.get('video_url'):
                                completed_checks += 1

            # Additional fields
            additional_fields = ['price', 'level', 'learning_objectives']
            for field in additional_fields:
                total_checks += 1
                if course_data.get(field):
                    completed_checks += 1

            return (completed_checks / total_checks * 100) if total_checks > 0 else 0

        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0

    def validate_creation_method(self, value):
        """Validate creation method with tier restrictions"""
        if value not in [choice[0] for choice in CourseCreationSession.CreationMethod.choices]:
            raise serializers.ValidationError("Invalid creation method")

        # AI Assisted requires Gold tier or higher
        if value == CourseCreationSession.CreationMethod.AI_ASSISTED:
            request = self.context.get('request')
            if request and hasattr(request, 'instructor_profile'):
                validate_instructor_tier_access(
                    request.instructor_profile,
                    InstructorProfile.Tier.GOLD,
                    "AI-Assisted Course Creation"  # Updated message for clarity
                )

        return value

    @transaction.atomic
    def publish_course(self):
        """
        Convert session data to published course
        Maintains backward compatibility with both status flows
        """
        # Call the model's publish_course method directly
        instance = self.instance

        if not instance:
            raise serializers.ValidationError("Must save session before publishing")

        # Handle both new status flow (COMPLETED) and old status flow (READY_TO_PUBLISH)
        if instance.status not in [CourseCreationSession.Status.COMPLETED,
                                   CourseCreationSession.Status.READY_TO_PUBLISH]:
            # Set transitional status for backward compatibility
            old_status = instance.status
            instance.status = CourseCreationSession.Status.IN_PROGRESS
            instance.save(update_fields=['status'])

            # Validate first
            errors = instance.validate_session_data()
            if errors:
                instance.status = CourseCreationSession.Status.FAILED
                instance.validation_errors = errors
                instance.save(update_fields=['status', 'validation_errors'])
                return None

            # Support both new and old status flows for broader compatibility
            if old_status == CourseCreationSession.Status.VALIDATING:
                # Old status flow
                instance.status = CourseCreationSession.Status.READY_TO_PUBLISH
            else:
                # New status flow
                instance.status = CourseCreationSession.Status.COMPLETED

            instance.save(update_fields=['status'])

        # Now call the model's publish_course method
        try:
            return instance.publish_course()
        except Exception as e:
            logger.error(f"Error publishing course: {e}")
            instance.status = CourseCreationSession.Status.FAILED
            instance.save(update_fields=['status'])
            raise serializers.ValidationError(f"Course publishing failed: {str(e)}")

class CourseTemplateSerializer(serializers.ModelSerializer):
    """Serializer for course template management"""
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    usage_analytics = serializers.SerializerMethodField()
    preview_data = serializers.SerializerMethodField()

    # Add backward compatibility fields
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    estimated_duration = serializers.IntegerField(required=False)
    difficulty_level = serializers.CharField(required=False)

    class Meta:
        model = CourseTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_display',
            'template_data', 'is_active', 'is_premium', 'required_tier',
            'usage_count', 'success_rate', 'created_by', 'created_by_name',
            'tags', 'usage_analytics', 'preview_data',
            'created_date', 'updated_date',
            # Backward compatibility fields
            'category', 'category_name', 'estimated_duration', 'difficulty_level'
        ]
        read_only_fields = [
            'id', 'usage_count', 'success_rate', 'created_by', 'created_date', 'updated_date'
        ]

    def get_usage_analytics(self, obj):
        """Get template usage analytics"""
        try:
            thirty_days_ago = timezone.now() - timedelta(days=30)

            recent_sessions = CourseCreationSession.objects.filter(
                template_used=obj.name,
                created_date__gte=thirty_days_ago
            )

            total_recent = recent_sessions.count()
            # Support both Status.PUBLISHED and Status.COMPLETED for broader compatibility
            successful_recent = recent_sessions.filter(
                status__in=[CourseCreationSession.Status.PUBLISHED, CourseCreationSession.Status.COMPLETED]
            ).count()

            return {
                'total_usage': obj.usage_count,
                'recent_usage_30_days': total_recent,
                'recent_success_rate': (successful_recent / total_recent * 100) if total_recent > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {}

    def get_preview_data(self, obj):
        """Get template preview data"""
        try:
            template_data = obj.template_data
            preview = {
                'structure_overview': {
                    'modules_count': len(template_data.get('modules', [])),
                    'estimated_lessons': sum(
                        len(module.get('lessons', []))
                        for module in template_data.get('modules', [])
                    ),
                    'content_types': list(set(
                        lesson.get('type', 'text')
                        for module in template_data.get('modules', [])
                        for lesson in module.get('lessons', [])
                    ))
                },
                'sample_modules': [
                    {
                        'title': module.get('title', ''),
                        'lesson_count': len(module.get('lessons', []))
                    }
                    for module in template_data.get('modules', [])[:3]
                ]
            }
            return preview
        except Exception as e:
            logger.error(f"Error getting preview data: {e}")
            return {}

    def validate_template_data(self, value):
        """Validate template data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Template data must be a dictionary")

        required_keys = ['metadata', 'modules']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Template data must include '{key}' section")

        modules = value.get('modules', [])
        if not isinstance(modules, list):
            raise serializers.ValidationError("Modules must be a list")

        for i, module in enumerate(modules):
            if not isinstance(module, dict):
                raise serializers.ValidationError(f"Module {i+1} must be an object")

            if 'title' not in module:
                raise serializers.ValidationError(f"Module {i+1} must have a title")

            lessons = module.get('lessons', [])
            if not isinstance(lessons, list):
                raise serializers.ValidationError(f"Module {i+1} lessons must be a list")

        return value

    def create_session_from_template(self, instructor):
        """Create a course creation session using this template"""
        try:
            session = CourseCreationSession.objects.create(
                instructor=instructor,
                creation_method=CourseCreationSession.CreationMethod.TEMPLATE,
                template_used=self.instance.name,
                course_data=self.instance.template_data.copy(),
                total_steps=4,  # Template-based creation has 4 steps
                expires_at=timezone.now() + timezone.timedelta(days=30)
            )

            # Update template usage statistics (using F() to avoid race conditions)
            with transaction.atomic():
                CourseTemplate.objects.filter(id=self.instance.id).update(
                    usage_count=models.F('usage_count') + 1
                )
                self.instance.refresh_from_db(fields=['usage_count'])

            return session
        except Exception as e:
            logger.error(f"Error creating session from template: {e}")
            raise serializers.ValidationError(f"Failed to create session from template: {str(e)}")

class DraftCourseContentSerializer(serializers.ModelSerializer):
    """Serializer for draft course content management"""
    session_info = serializers.CharField(source='session.session_id', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    content_hash = serializers.SerializerMethodField()
    version_history = serializers.SerializerMethodField()

    class Meta:
        model = DraftCourseContent
        fields = [
            'id', 'session', 'session_info', 'content_type', 'content_type_display',
            'content_id', 'version', 'content_data', 'title', 'order', 'is_complete',
            'validation_errors', 'auto_save_version', 'content_hash', 'version_history',
            'ai_generated', 'ai_prompt', 'last_saved'
        ]
        read_only_fields = ['id', 'auto_save_version', 'last_saved']

    def get_content_hash(self, obj):
        """Generate hash of content for change detection"""
        try:
            content_str = json.dumps(obj.content_data, sort_keys=True)
            return calculate_content_hash(content_str)
        except Exception:
            return ''

    def get_version_history(self, obj):
        """Get version history for this content"""
        try:
            versions = DraftCourseContent.objects.filter(
                session=obj.session,
                content_type=obj.content_type,
                content_id=obj.content_id
            ).order_by('-version')[:5]

            return [
                {
                    'version': v.version,
                    'created': v.last_saved,
                    'changes_summary': self._get_changes_summary(obj, v) if v.version < obj.version else None
                }
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return []

    def _get_changes_summary(self, current, previous):
        """Generate summary of changes between versions"""
        try:
            changes = []

            if current.title != previous.title:
                changes.append('Title changed')

            if current.content_data != previous.content_data:
                changes.append('Content modified')

            if current.order != previous.order:
                changes.append('Order changed')

            return ', '.join(changes) if changes else 'Minor updates'
        except Exception:
            return 'Changes detected'

    def validate_content_data(self, value):
        """Validate content data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Content data must be a dictionary")
        return value

    def validate_order(self, value):
        """Validate display order"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Order must be positive")
        return value

    def validate_version(self, value):
        """Validate version number"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Version must be positive")
        return value

class CourseContentDraftSerializer(serializers.ModelSerializer):
    """Serializer for course content draft with file handling"""
    session_info = serializers.CharField(source='session.session_id', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    processing_status_display = serializers.CharField(source='get_processing_status_display', read_only=True)
    file_info = serializers.SerializerMethodField()

    class Meta:
        model = CourseContentDraft
        fields = [
            'id', 'session', 'session_info', 'content_type', 'content_type_display',
            'file_path', 'content_hash', 'version', 'is_processed', 'processing_status',
            'processing_status_display', 'processing_error', 'file_size', 'mime_type',
            'original_filename', 'processing_metadata', 'file_info',
            'created_date', 'processed_date'
        ]
        read_only_fields = [
            'id', 'content_hash', 'is_processed', 'processing_status', 'file_size',
            'mime_type', 'original_filename', 'processing_metadata', 'created_date', 'processed_date'
        ]

    def get_file_info(self, obj):
        """Get file information and metadata"""
        try:
            if obj.file_path:
                # Ensure we always convert file_path to string
                file_path_str = str(obj.file_path)
                return {
                    'filename': os.path.basename(file_path_str),
                    'extension': os.path.splitext(file_path_str)[1].lower(),
                    'size_mb': round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0,
                    'mime_type': obj.mime_type,
                    'is_secure': validate_file_path_security(file_path_str)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    def validate_file_path(self, value):
        """Validate file path security"""
        # Convert to string if necessary
        if value:
            value_str = str(value)
            if not validate_file_path_security(value_str):
                raise serializers.ValidationError("Invalid file path for security reasons")
        return value

class DraftCoursePublishSerializer(serializers.Serializer):
    """
    Serializer for publishing draft courses
    Controls publish settings and validation
    """
    is_published = serializers.BooleanField(default=True)
    publish_now = serializers.BooleanField(default=True)
    publish_date = serializers.DateTimeField(required=False, allow_null=True)
    notify_students = serializers.BooleanField(default=False)

    def validate(self, data):
        """Validate publish settings consistency"""
        publish_now = data.get('publish_now', True)
        publish_date = data.get('publish_date')

        if not publish_now and not publish_date:
            raise serializers.ValidationError(
                "Either publish now must be true or a publish date must be provided"
            )

        if publish_now and publish_date:
            # Ignore publish_date if publishing now
            data['publish_date'] = None

        return data
