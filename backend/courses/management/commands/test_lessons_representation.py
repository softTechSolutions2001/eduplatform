# tests/test_lessons_representation.py
import pytest
from rest_framework.test import APIRequestFactory

from courses.models import Category, Course, Module, Lesson
from courses.serializers import LessonSerializer
from users.models import CustomUser


class _FakeSubscription:               # minimal stub that the helper accepts
    def __init__(self, tier, active=True):
        self.tier = tier
        self._active = active

    def is_active(self):
        return self._active


@pytest.fixture
def lesson(db):
    """
    Re-usable Lesson fixture with all three content flavours filled-in.
    The lesson itself is set to `registered` access-level so:
      • guests receive `guest_content`
      • registered receive `registered_content`
      • premium receive full `content`
    """
    cat = Category.objects.create(name="General")
    course = Course.objects.create(
        title="Demo", description="x", category=cat
    )
    module = Module.objects.create(course=course, title="M1")
    return Lesson.objects.create(
        module=module,
        title="L1",
        access_level="registered",
        content="FULL PREMIUM CONTENT",
        registered_content="REGISTERED CONTENT",
        guest_content="GUEST PREVIEW",
    )


@pytest.fixture
def factory():
    return APIRequestFactory()


def _serialize(lesson, user, factory):
    """Helper that instantiates the serializer with proper `request` context."""
    request = factory.get("/fake-url")
    request.user = user
    return LessonSerializer(lesson, context={"request": request}).data


@pytest.mark.django_db
def test_guest_user_gets_guest_content(lesson, factory):
    data = _serialize(lesson, user=AnonymousUser(), factory=factory)
    assert data["content"] == "GUEST PREVIEW"
    assert data["is_restricted"] is True


@pytest.mark.django_db
def test_registered_user_gets_registered_content(lesson, factory):
    user = CustomUser.objects.create_user(
        email="reg@example.com", username="reg", password="x"
    )
    user.subscription = _FakeSubscription("registered")  # satisfy helper
    data = _serialize(lesson, user, factory)
    assert data["content"] == "REGISTERED CONTENT"
    assert data["is_restricted"] is False


@pytest.mark.django_db
def test_premium_user_gets_full_content(lesson, factory):
    user = CustomUser.objects.create_user(
        email="prem@example.com", username="prem", password="x"
    )
    user.subscription = _FakeSubscription("premium")
    data = _serialize(lesson, user, factory)
    assert data["content"] == "FULL PREMIUM CONTENT"
    assert data["is_restricted"] is False
