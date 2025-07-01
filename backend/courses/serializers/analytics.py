# Analytics model serializers
#
# File Path: backend/courses/serializers/analytics.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:19:35
# Date Revised: 2025-06-26 10:19:35
# Current Date and Time (UTC): 2025-06-26 10:19:35
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 10:19:35 UTC
# User: softTechSolutions2001
# Version: 3.0.0
#
# Analytics-Related Serializers for Course Management System

import logging
from rest_framework import serializers
from django.db.models import Prefetch
from .core import LessonSerializer  # Import at module level
from ..models import (
    Assessment, Question, Answer, AssessmentAttempt,
    AttemptAnswer, Review, Note, Lesson
)

from .mixins import (
    ContextPropagationMixin, OptimizedQueryMixin
)


logger = logging.getLogger(__name__)

# =====================================
# OPTIMIZED ASSESSMENT SERIALIZERS
# =====================================

class AnswerSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """
    Enhanced answer serializer with proper access control and context
    """
    # Support both old and new field names for backward compatibility
    text = serializers.CharField(source='text_property', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'answer_text', 'text', 'is_correct', 'explanation', 'order',
            'created_date', 'updated_date'
        ]
        read_only_fields = ['created_date', 'updated_date', 'text']

    def _process_representation_safely(self, data, instance):
        """Control access to correct answer information safely"""
        request = self.context.get('request')        # Hide correct answers from students during active attempts
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user

            # Show correct answers only to instructors/admins or after submission
            is_instructor = user.is_staff or (hasattr(user, 'role') and user.role in ['administrator', 'instructor'])
            show_correct = self.context.get('show_correct_answers', False)

            if not is_instructor and not show_correct:
                data.pop('is_correct', None)
                data['is_restricted'] = True
            else:
                data['is_restricted'] = False

        return data

    def to_representation(self, instance):
        """Use the safe processing method"""
        data = super().to_representation(instance)
        return self._process_representation_safely(data, instance)

# Fix for QuestionSerializer - replace answers field with SerializerMethodField
class QuestionSerializer(ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer):
    """
    Enhanced question serializer with optimized nested loading
    """
    answers = serializers.SerializerMethodField()  # Changed from AnswerSerializer to SerializerMethodField
    # Support both old and new field names for backward compatibility
    text = serializers.CharField(source='text_property', read_only=True)
    feedback = serializers.CharField(source='feedback_property', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'text', 'question_type', 'order', 'points',
            'explanation', 'feedback', 'answers', 'created_date', 'updated_date'
        ]
        read_only_fields = ['created_date', 'updated_date', 'text', 'feedback']

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize question queries with answers"""
        return queryset.prefetch_related(
            Prefetch('answers', queryset=Answer.objects.order_by('order'))
        )

    def get_answers(self, obj):
        """Get answers with proper context propagation"""
        answers = obj.answers.all()
        context = self.get_serializer_context_for_nested()
        return AnswerSerializer(answers, many=True, context=context).data

class QuestionDetailSerializer(QuestionSerializer):
    """
    Detailed question serializer for instructors with complete information
    """
    answers = serializers.SerializerMethodField()

    def get_answers(self, obj):
        """Get complete answer information for authorized users"""
        answers = obj.answers.all().order_by('order')
        context = self.get_serializer_context_for_nested({'show_correct_answers': True})
        return AnswerSerializer(answers, many=True, context=context).data


class AssessmentSerializer(ContextPropagationMixin, OptimizedQueryMixin, serializers.ModelSerializer):
    """
    Enhanced assessment serializer with optimized loading
    """
    lesson = serializers.PrimaryKeyRelatedField(read_only=True)
    questions = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    # Support both old and new field names for backward compatibility
    time_limit_minutes = serializers.IntegerField(source='time_limit_minutes', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'lesson', 'title', 'description', 'time_limit', 'time_limit_minutes', 'passing_score',
            'max_attempts', 'randomize_questions', 'show_results',
            'questions', 'question_count', 'created_date', 'updated_date'
        ]
        read_only_fields = ['created_date', 'updated_date', 'time_limit_minutes']

    @classmethod
    def setup_eager_loading(cls, queryset):
        """Optimize assessment queries with questions and answers"""
        return queryset.prefetch_related(
            Prefetch('questions',
                    queryset=Question.objects.prefetch_related('answers').order_by('order'))
        )

    def get_question_count(self, obj):
        """Get total number of questions with caching"""
        if hasattr(obj, '_question_count'):
            return obj._question_count

        try:
            return obj.questions.count()
        except Exception:
            return 0

    def get_questions(self, obj):
        """Get questions with proper context propagation"""
        questions = obj.questions.all()
        context = self.get_serializer_context_for_nested()
        return QuestionSerializer(questions, many=True, context=context).data


class AssessmentAttemptSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for student assessment attempts"""
    assessment = AssessmentSerializer(read_only=True)
    detailed_results = serializers.SerializerMethodField()
    # Support both old and new field names for backward compatibility
    passed = serializers.BooleanField(source='passed', read_only=True)
    is_passed = serializers.BooleanField(source='is_passed', read_only=True)

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'assessment', 'start_time', 'end_time', 'score', 'passed', 'is_passed',
            'score_percentage', 'attempt_number', 'detailed_results',
            'ip_address', 'user_agent', 'created_date', 'updated_date'
        ]
        read_only_fields = [
            'start_time', 'end_time', 'score', 'passed', 'is_passed', 'score_percentage',
            'created_date', 'updated_date'
        ]

    def get_detailed_results(self, obj):
        """Get detailed assessment results with error handling"""
        try:
            return {
                'total_questions': obj.assessment.questions.count() if obj.assessment else 0,
                'correct_answers': obj.answers.filter(is_correct=True).count(),
                'time_taken': obj.time_taken
            }
        except Exception as e:
            logger.warning(f"Error getting detailed results for attempt {obj.id}: {e}")
            return {'total_questions': 0, 'correct_answers': 0, 'time_taken': 0}

    def get_assessment(self, obj):
        """Get assessment with proper context propagation"""
        if not obj.assessment:
            return None

        try:
            context = self.get_serializer_context_for_nested()
            return AssessmentSerializer(obj.assessment, context=context).data
        except Exception as e:
            logger.warning(f"Error getting assessment for attempt {obj.id}: {e}")
            return None


class AttemptAnswerSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for student answers in assessment attempts"""
    question = QuestionSerializer(read_only=True)
    # Support both old and new field names for backward compatibility
    answer = serializers.IntegerField(source='answer.id', read_only=True, allow_null=True)
    text_response = serializers.CharField(source='text_response', read_only=True, allow_null=True)

    class Meta:
        model = AttemptAnswer
        fields = [
            'id', 'question', 'selected_answer', 'answer', 'text_answer', 'text_response',
            'is_correct', 'points_earned', 'feedback', 'answered_at'
        ]
        read_only_fields = ['is_correct', 'points_earned', 'answered_at', 'answer', 'text_response']

    def get_question(self, obj):
        """Get question with proper context propagation"""
        try:
            context = self.get_serializer_context_for_nested()
            return QuestionSerializer(obj.question, context=context).data
        except Exception as e:
            logger.warning(f"Error getting question for attempt answer {obj.id}: {e}")
            return None


class ReviewSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for course reviews"""
    user = serializers.SerializerMethodField()
    helpful_votes = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'rating', 'title', 'content', 'helpful_count',
            'helpful_votes', 'is_verified_purchase', 'is_approved', 'moderation_notes',
            'created_date', 'updated_date'
        ]
        read_only_fields = ['helpful_count', 'is_verified_purchase', 'created_date', 'updated_date']

    def get_user(self, obj):
        """Get user information for review safely"""
        try:
            return {
                'id': obj.user.id,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'username': obj.user.username,
                'is_verified': (hasattr(obj.user, 'profile') and
                              getattr(obj.user.profile, 'is_verified', False))
            }
        except Exception as e:
            logger.warning(f"Error getting user info for review {obj.id}: {e}")
            return {'id': None, 'username': 'Anonymous'}

    def get_helpful_votes(self, obj):
        """Get helpful votes for current user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        # Implementation depends on your helpful votes model
        return None


class NoteSerializer(ContextPropagationMixin, serializers.ModelSerializer):
    """Enhanced serializer for student notes"""
    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),  # Directly specify the queryset here
        source='lesson',
        write_only=True
    )

    class Meta:
        model = Note
        fields = [
            'id', 'lesson', 'lesson_id', 'content', 'is_private', 'tags',
            'created_date', 'updated_date'
        ]
        read_only_fields = ['created_date', 'updated_date']

    def get_lesson(self, obj):
        """Get lesson with proper context propagation"""
        try:
            context = self.get_serializer_context_for_nested()
            return LessonSerializer(obj.lesson, context=context).data
        except Exception as e:
            logger.warning(f"Error getting lesson for note {obj.id}: {e}")
            return None
