"""
Serializers for AI Course Builder functionality.

This module defines serializers for the AI course builder models,
handling the conversion between Python objects and JSON formats.

Classes:
- AICourseBuilderDraftSerializer: Serializes AICourseBuilderDraft model
"""

from rest_framework import serializers
from .models import AICourseBuilderDraft


class AICourseBuilderDraftSerializer(serializers.ModelSerializer):
    """
    Serializer for the AICourseBuilderDraft model.

    This serializer handles the conversion of AICourseBuilderDraft instances
    to and from JSON, handling all fields required for the AI course builder
    workflow.
    """

    class Meta:
        model = AICourseBuilderDraft
        fields = [
            'id', 'instructor', 'created_at', 'updated_at', 'status',
            'title', 'description', 'course_objectives', 'target_audience',
            'difficulty_level', 'duration_minutes', 'price',
            'outline', 'content', 'assessments',
            'has_outline', 'has_modules', 'has_lessons', 'has_assessments',
            'generation_metadata'
        ]
        read_only_fields = ['id', 'instructor', 'created_at', 'updated_at']
