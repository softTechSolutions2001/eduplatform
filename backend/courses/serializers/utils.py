# Utility serializers for API documentation and consistent response patterns
#
# File Path: backend/courses/serializers/utils.py
# Folder Path: backend/courses/serializers/
from django.utils import timezone
from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Simple serializer for health check endpoints"""

    status = serializers.CharField()
    message = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()
    components = serializers.DictField(required=False)
    statistics = serializers.DictField(required=False)


class EmptySerializer(serializers.Serializer):
    """Empty serializer for views without response data"""

    pass


class StatusResponseSerializer(serializers.Serializer):
    """Simple status response serializer"""

    status = serializers.CharField()
    message = serializers.CharField(required=False)


class ProgressStatsSerializer(serializers.Serializer):
    """Serializer for user progress statistics"""

    totalCourses = serializers.IntegerField()
    coursesCompleted = serializers.IntegerField()
    coursesInProgress = serializers.IntegerField()
    totalLessons = serializers.IntegerField()
    completedLessons = serializers.IntegerField()
    completionPercentage = serializers.FloatField()
    hoursSpent = serializers.FloatField()
    totalTimeSpent = serializers.IntegerField()
    assessmentsCompleted = serializers.IntegerField()
    averageScore = serializers.FloatField()
    certificatesEarned = serializers.IntegerField()
    recentActivity = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    generatedAt = serializers.DateTimeField()


class VersionInfoSerializer(serializers.Serializer):
    """Serializer for API version information"""

    api_version = serializers.CharField()
    django_version = serializers.CharField()
    drf_version = serializers.CharField()
    release_date = serializers.CharField()
    last_updated = serializers.CharField()
    features = serializers.DictField()
    endpoints = serializers.DictField()
    supported_formats = serializers.ListField(child=serializers.CharField())
    rate_limiting = serializers.DictField()
    caching = serializers.DictField()
    documentation = serializers.DictField()
