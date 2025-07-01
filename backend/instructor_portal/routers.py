from rest_framework.routers import DefaultRouter
from .views import (
    InstructorProfileViewSet,
    InstructorDashboardViewSet,
    # Add other viewsets as needed
)

router = DefaultRouter()
# router.register(r'profile', InstructorProfileViewSet)
# router.register(r'dashboard', InstructorDashboardViewSet)
# Add other router registrations here
