from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import (
    Testimonial, PlatformStatistics,
    UserLearningStatistics, InstructorStatistics
)
from .serializers import (
    TestimonialSerializer, PlatformStatisticsSerializer,
    UserLearningStatisticsSerializer, InstructorStatisticsSerializer
)

# Create your views here.


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving testimonials
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Testimonial.objects.all()
        featured = self.request.query_params.get('featured', None)

        if featured is not None and featured.lower() == 'true':
            queryset = queryset.filter(featured=True)

        return queryset


class FeaturedTestimonialsView(generics.ListAPIView):
    """
    API endpoint to get featured testimonials
    """
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        limit = self.request.query_params.get('limit', 3)
        try:
            limit = int(limit)
        except ValueError:
            limit = 3

        return Testimonial.objects.filter(featured=True).order_by('-created_at')[:limit]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def platform_statistics(request):
    """
    Get platform-wide statistics
    """
    stats = PlatformStatistics.get_stats()
    # Optionally update the stats if they're outdated
    if request.query_params.get('refresh') == 'true':
        if request.user.is_staff:  # Only staff can refresh stats
            stats.update_stats()

    serializer = PlatformStatisticsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_learning_statistics(request):
    """
    Get learning statistics for the current user
    """
    stats, created = UserLearningStatistics.objects.get_or_create(
        user=request.user)
    serializer = UserLearningStatisticsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def instructor_statistics(request):
    """
    Get teaching statistics for the current user (instructor only)
    """
    if not hasattr(request.user, 'role') or request.user.role != 'instructor':
        return Response(
            {"detail": "You must be an instructor to view these statistics."},
            status=status.HTTP_403_FORBIDDEN
        )

    stats, created = InstructorStatistics.objects.get_or_create(
        user=request.user)
    serializer = InstructorStatisticsSerializer(stats)
    return Response(serializer.data)
