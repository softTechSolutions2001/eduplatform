# Django Runtime Validation Stack - Step by Step Guide

This guide helps you build a comprehensive testing pipeline that catches bugs across all layers of your Django application before they reach production.

## Phase 1: Foundation Setup (Start Here)

### Step 1: Install Required Packages
```bash
pip install pytest-django model-bakery drf-spectacular
```

### Step 2: Create pytest.ini in your project root
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = your_project.settings
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db --nomigrations
```

### Step 3: Basic Django System Check
Add this to your CI/CD pipeline:
```bash
python manage.py check --deploy
```
This catches:
- Field name conflicts
- Foreign key target errors
- Settings configuration issues

### Step 4: Model Factory Smoke Test
Create `tests/test_model_factories.py`:
```python
import pytest
from django.apps import apps
from model_bakery import baker

@pytest.mark.django_db
@pytest.mark.parametrize('model', apps.get_models())
def test_model_can_be_created(model):
    """Test that every model can be instantiated without errors"""
    instance = baker.make(model)
    assert model.objects.filter(pk=instance.pk).exists()
```

**Why this matters**: Catches missing default values, required fields, and database constraints.

## Phase 2: API Layer Validation

### Step 5: DRF Spectacular Setup
Add to your `settings.py`:
```python
INSTALLED_APPS = [
    # ... your apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ... your existing config
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### Step 6: Generate OpenAPI Schema
```bash
python manage.py spectacular --color --file schema.yml
```
**If this fails**: You have broken serializers, missing viewsets, or incorrect URL patterns.

### Step 7: Serializer Round-Trip Testing
Create `tests/test_serializers.py`:
```python
import pytest
from rest_framework.test import APIRequestFactory
from model_bakery import baker
from your_app.models import Course, Lesson  # Replace with your models
from your_app.serializers import CourseSerializer, LessonSerializer

SERIALIZER_MAP = {
    Course: CourseSerializer,
    Lesson: LessonSerializer,
    # Add all your model-serializer pairs
}

@pytest.mark.django_db
@pytest.mark.parametrize("model,serializer_cls", SERIALIZER_MAP.items())
def test_serializer_round_trip(model, serializer_cls):
    """Test that serializers can serialize and deserialize data correctly"""
    # Create a model instance
    obj = baker.make(model)

    # Serialize to dict
    serializer = serializer_cls(obj)
    data = serializer.data

    # Deserialize back
    new_serializer = serializer_cls(data=data)
    assert new_serializer.is_valid(), f"Serializer errors: {new_serializer.errors}"
```

**Why this matters**: Catches missing fields, wrong `read_only` flags, and type mismatches.

## Phase 3: URL and View Validation

### Step 8: Endpoint Smoke Testing
Create `tests/test_endpoints.py`:
```python
import pytest
from rest_framework.test import APIClient
from django.urls import get_resolver
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_user(api_client):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return user

@pytest.mark.django_db
def test_endpoints_dont_crash(api_client):
    """Test that all endpoints return valid HTTP status codes"""
    # Get all URL patterns
    resolver = get_resolver()

    test_urls = [
        '/api/courses/',
        '/api/lessons/',
        # Add your main endpoints here
    ]

    for url in test_urls:
        response = api_client.get(url)
        assert response.status_code in (200, 401, 403, 405), f"URL {url} returned {response.status_code}"
```

## Phase 4: Business Logic Integration Tests

### Step 9: Cross-App Integration Testing
Create `tests/test_integration.py`:
```python
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from your_app.models import Course, Enrollment  # Replace with your models

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(api_client):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return user

@pytest.fixture
def course():
    return Course.objects.create(
        title='Test Course',
        description='A test course',
        # Add required fields
    )

@pytest.mark.django_db
def test_course_enrollment_flow(api_client, user, course):
    """Test the complete enrollment process"""
    # Step 1: Enroll user in course
    response = api_client.post(f'/api/courses/{course.id}/enroll/')
    assert response.status_code == 201

    # Step 2: Verify enrollment was created
    assert Enrollment.objects.filter(user=user, course=course).exists()

    # Step 3: Verify user can access course content
    response = api_client.get(f'/api/courses/{course.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_lesson_progress_tracking(api_client, user, course):
    """Test lesson completion tracking"""
    # Create lesson
    lesson = course.lessons.create(
        title='Test Lesson',
        content='Test content'
    )

    # Mark lesson as completed
    response = api_client.post(f'/api/lessons/{lesson.id}/complete/')
    assert response.status_code == 200

    # Verify progress was recorded
    # Add your progress model checks here
```

## Phase 5: Migration Safety

### Step 10: Migration Validation
```bash
# Install migration linter
pip install django-migration-linter

# Check for destructive migrations
migration-linter --project-path .
```

### Step 11: Test with Full Migration History
Add to your test suite:
```bash
pytest --migrations
```

## Phase 6: Production Health Checks

### Step 12: Health Check Endpoints
Create `your_app/views/health.py`:
```python
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    """Basic health check endpoint"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

Add to your `urls.py`:
```python
from django.urls import path
from your_app.views.health import health_check

urlpatterns = [
    # ... your existing URLs
    path('health/', health_check, name='health-check'),
]
```

## Phase 7: CI/CD Integration

### Step 13: GitHub Actions Setup
Create `.github/workflows/test.yml`:
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run Django checks
        run: python manage.py check --deploy
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db

      - name: Run migrations
        run: python manage.py migrate --noinput
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db

      - name: Run tests
        run: pytest -v
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db

      - name: Generate OpenAPI schema
        run: python manage.py spectacular --file schema.yml
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
```

## Quick Start Checklist

**Week 1: Foundation**
- [ ] Install pytest-django, model-bakery
- [ ] Create model factory test
- [ ] Add Django system checks to CI

**Week 2: API Layer**
- [ ] Set up DRF Spectacular
- [ ] Create serializer round-trip tests
- [ ] Add endpoint smoke tests

**Week 3: Integration**
- [ ] Write 3 key business flow tests
- [ ] Add health check endpoints
- [ ] Set up CI/CD pipeline

**Week 4: Production Ready**
- [ ] Add migration linting
- [ ] Set up monitoring/alerting
- [ ] Document the testing strategy

## What Each Layer Catches

| Layer                     | What It Finds                                        |
| ------------------------- | ---------------------------------------------------- |
| **Model Factory Tests**   | Missing defaults, constraint violations, FK issues   |
| **Serializer Round-Trip** | Field mismatches, read-only errors, type issues      |
| **Endpoint Smoke Tests**  | URL routing problems, permission errors, 500 crashes |
| **Integration Tests**     | Business logic bugs, cross-app communication issues  |
| **Migration Linting**     | Data loss risks, deployment failures                 |
| **Health Checks**         | Database connectivity, service dependencies          |

## Common Issues and Solutions

**Problem**: Tests are too slow
**Solution**: Use `--reuse-db` and `--nomigrations` flags

**Problem**: Model factory fails with IntegrityError
**Solution**: Check for missing default values or unique constraints

**Problem**: Serializer round-trip fails
**Solution**: Check for missing fields or incorrect `read_only` settings

**Problem**: Integration tests are flaky
**Solution**: Use database transactions and proper test isolation

Start with Phase 1 and gradually add more layers. Each phase builds on the previous one and catches different types of bugs!
