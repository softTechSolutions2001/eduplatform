from rest_framework import serializers
from .models import Testimonial, PlatformStatistics, UserLearningStatistics, InstructorStatistics


class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer for the Testimonial model
    """
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'role', 'content',
                  'rating', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class PlatformStatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for platform-wide statistics
    """
    class Meta:
        model = PlatformStatistics
        fields = [
            'total_courses', 'total_students', 'total_instructors',
            'total_lessons_completed', 'total_certificates_issued',
            'last_updated'
        ]
        read_only_fields = ['last_updated']


class UserLearningStatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for user learning statistics
    """
    class Meta:
        model = UserLearningStatistics
        fields = [
            'courses_completed', 'hours_spent', 'average_score',
            'last_updated'
        ]
        read_only_fields = ['last_updated']


class InstructorStatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for instructor teaching statistics
    """
    class Meta:
        model = InstructorStatistics
        fields = [
            'courses_created', 'total_students', 'average_rating',
            'last_updated'
        ]
        read_only_fields = ['last_updated']
