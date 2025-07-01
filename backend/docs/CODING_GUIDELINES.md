# Coding Guidelines for AI Development Assistance
## Education Platform with AI Course Builder

## CRITICAL RULES
1. **PRESERVE ALL FUNCTIONALITY** - Never remove or comment out working code
2. **ROOT CAUSE ANALYSIS FIRST** - Understand the problem before suggesting solutions
3. **EXPLAIN BEFORE IMPLEMENTING** - Always describe what you plan to change
4. **NO TEMPORARY FIXES** - Only provide production-ready solutions
5. **RESPECT DOMAIN BOUNDARIES** - Keep course, user, instructor, AI builder, and content logic separate
6. **LEGACY COMPATIBILITY** - Check compatibility audit files before making changes

## Project Structure

```
frontend/                     # React/Vite application
├── src/
│   ├── components/
│   │   ├── layouts/         # MainLayout, Header, Footer
│   │   ├── routes/          # ProtectedRoute, CourseContentRouteChecker
│   │   ├── common/          # Reusable UI components (50+ components)
│   │   ├── courses/         # Course-specific components
│   │   ├── instructor/      # Instructor-specific components
│   │   ├── subscription/    # Subscription and payment components
│   │   └── testimonials/    # Testimonial components
│   ├── pages/
│   │   ├── auth/           # Login, Register, ForgotPassword, etc.
│   │   ├── courses/        # CoursesListPage, CourseContentPage, etc.
│   │   ├── dashboard/      # Student, Instructor, Admin dashboards
│   │   ├── instructor/     # Course creation, editing, curriculum
│   │   ├── subscription/   # Pricing, checkout, success pages
│   │   └── user/           # Profile management
│   ├── services/
│   │   ├── domains/        # Domain-specific services (15+ services)
│   │   ├── instructor/     # Instructor-specific services
│   │   ├── http/           # HTTP client configuration
│   │   └── utils/          # Service utilities
│   ├── contexts/           # AuthContext, DirectionContext
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── aiCourseBuilder/    # AI-powered course generation
│   │   ├── components/     # AI builder UI components
│   │   ├── api/            # AI builder API client
│   │   ├── store/          # AI builder state management
│   │   ├── hooks/          # AI-specific hooks
│   │   ├── config/         # AI builder configuration
│   │   └── utils/          # AI builder utilities
│   └── courseBuilder/      # Manual course editor (TypeScript)
│       ├── components/     # Course builder UI components
│       ├── store/          # Redux course slice
│       ├── api/            # Course builder API
│       ├── hooks/          # Course builder hooks
│       ├── utils/          # Course builder utilities
│       └── pages/          # Builder interface pages
├── test/                   # Test files and configurations
├── scripts/                # Build and utility scripts
└── package.json

backend/                    # Django application
├── educore/                # Main Django configuration
│   ├── settings.py         # Main settings with db_settings separation
│   ├── urls.py             # Root URL configuration
│   ├── celery.py           # Celery configuration for async tasks
│   ├── asgi.py/wsgi.py     # Application entry points
│   └── utils/              # Core utilities
├── courses/                # Course management domain
│   ├── models/             # core.py, enrolment.py, analytics.py, misc.py
│   ├── serializers/        # Domain-specific serializers
│   ├── views/              # public.py, user.py, instructor.py, debug.py
│   ├── utils/              # Course-specific utilities
│   ├── legacy_shims/       # Legacy compatibility layer
│   ├── management/commands/ # Custom Django commands
│   └── migrations/         # Database migrations
├── users/                  # User management domain
│   ├── models.py           # User models with custom managers
│   ├── authentication.py   # Custom authentication backends
│   ├── permissions.py      # User-specific permissions
│   ├── pipeline.py         # Social auth pipeline
│   └── utils.py            # User utilities
├── instructor_portal/      # Instructor-specific features
│   ├── models/             # creation.py, dashboard.py, analytics.py, etc.
│   ├── serializers/        # Instructor-specific serializers
│   ├── views/              # creation_views.py, dashboard_views.py, etc.
│   ├── api/                # External API integrations
│   ├── tests/              # Comprehensive test suite
│   └── multiple URL configs # Various URL routing strategies
├── ai_course_builder/      # AI course generation
│   ├── models.py           # AI builder data models
│   ├── views.py            # AI generation endpoints
│   ├── tasks.py            # Celery async AI tasks
│   ├── serializers.py      # AI builder API serializers
│   └── migrations/         # AI builder migrations
├── content/                # Content management system
│   ├── models.py           # Content models (testimonials, etc.)
│   ├── views.py            # Content management views
│   ├── serializers.py      # Content API serializers
│   └── signals.py          # Content-related signals
├── templates/              # Django templates
│   ├── base.html           # Base template
│   ├── instructor/         # Instructor-specific templates
│   └── users/              # User-related email templates
├── config/                 # Configuration files
├── requirements.txt        # Main Python dependencies
├── requirements-celery.txt # Celery-specific dependencies
└── multiple analysis files # Compatibility and refactoring reports
```

## Technology Stack

**Frontend**:
- React 18+, Vite, TypeScript (course builder), JavaScript (AI builder)
- Tailwind CSS, Custom CSS modules
- Cypress (E2E testing), Vitest (unit testing)

**Backend**:
- Django 4.2+, Django REST Framework, PostgreSQL
- Celery + Redis (async tasks), Custom authentication
- Custom management commands, Legacy compatibility layers

**Key Features**:
- AI course generation with async processing
- Manual course builder with drag-and-drop
- Multi-role authentication (Students, Instructors, Admins)
- Subscription and payment processing
- Content management system
- Analytics and progress tracking
- Certificate generation
- Forum and social features

## Domain Architecture

### Core Domains
1. **Courses** - Course content, structure, enrollment, and analytics
2. **Users** - Authentication, profiles, permissions, and social auth
3. **Instructor Portal** - Course creation, management, analytics, and collaboration
4. **AI Course Builder** - AI-powered course generation with async processing
5. **Course Builder** - Manual TypeScript-based course editing
6. **Content** - CMS for testimonials, blog posts, and static content

### Key Business Rules
- **Course Creation**: Dual paths - AI-assisted vs Manual builder
- **User Roles**: Students, Instructors, Admins with role-based permissions
- **Enrollment & Progress**: Comprehensive tracking with analytics
- **Subscription Model**: Tiered access with payment processing
- **Content Management**: Instructor-created content with moderation

## Common Commands

```bash
# Backend (always activate virtual environment first)
source venv/Scripts/activate        # Windows
# source venv/bin/activate          # Linux/Mac

python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py test

# Custom management commands
python manage.py add_sample_data
python manage.py setup_test_data
python manage.py list_endpoints
python manage.py delete_all_courses

# Celery (for AI tasks and async processing)
# Use provided batch files or:
celery -A educore worker --loglevel=info

# Frontend
npm run dev
npm run build
npm run preview
npm run lint
npm run type-check

# Testing
npm run test              # Vitest unit tests
npx cypress open         # E2E tests
```

## Critical Integration Points

### AI Course Builder
- **Async Processing**: Uses Celery tasks for AI generation
- **State Management**: Custom store with workflow validation
- **API Integration**: Dedicated API client with mock responses
- **Error Handling**: Comprehensive error boundaries and validation

### Course Builder (Manual)
- **TypeScript**: Fully typed with custom schemas
- **Drag & Drop**: Custom DnD implementation with virtualization
- **Auto-save**: Debounced auto-save with dirty state tracking
- **Network Debugging**: Built-in network debugging tools

### Authentication & Authorization
- **Multi-backend**: Custom authentication with social auth pipeline
- **Role-based Access**: Student/Instructor/Admin role separation
- **Session Management**: Custom session handling with security features
- **Protected Routes**: Route guards with role-based access control

### Content Management
- **CMS Integration**: Separate content domain for static content
- **Testimonials**: Dynamic testimonial management
- **Blog System**: Blog post management with categories
- **Media Handling**: File upload and media management

## Legacy Compatibility

### Critical Compatibility Files
- `COMPATIBILITY_AUDIT_FINAL_REPORT.md` - System-wide compatibility audit
- `courses/COMPATIBILITY_AUDIT_FINAL_REPORT.md` - Course-specific audit
- `SERIALIZERS_COMPATIBILITY_AUDIT_FINAL.md` - Serializer compatibility
- `courses/legacy_shims/` - Legacy compatibility layer

### Refactoring Guidelines
- **Check compatibility audits** before making changes
- **Use legacy shims** when breaking changes are necessary
- **Maintain API contracts** documented in compatibility reports
- **Test with existing data** using setup commands

## When Working on Issues:

### Before Making Changes
1. **Identify the domain** - Which app/module does this belong to?
2. **Check compatibility audits** - Review relevant audit files
3. **Review related code** - Look at models, serializers, views, and components
4. **Consider user roles** - How does this impact different user types?
5. **Check legacy shims** - Are there compatibility layers involved?

### Domain-Specific Considerations
- **Courses**: Changes may affect enrollment, analytics, and instructor portal
- **AI Builder**: Consider async task implications and error handling
- **Course Builder**: Maintain TypeScript types and DnD functionality
- **Users**: Authentication changes affect the entire platform
- **Content**: CMS changes may affect public-facing content
- **Instructor Portal**: Changes affect instructor workflows and analytics

## Red Flags to Avoid

### Backend Critical Areas
- **Authentication pipeline** - Breaking social auth or custom backends
- **Celery tasks** - Removing error handling or breaking async workflows
- **Legacy shims** - Modifying without understanding compatibility impact
- **Database migrations** - Making non-reversible schema changes
- **API contracts** - Breaking existing frontend integrations
- **Permission systems** - Bypassing role-based access controls

### Frontend Critical Areas
- **AI Builder state** - Breaking workflow validation or state management
- **Course Builder DnD** - Disrupting drag-and-drop functionality
- **Authentication context** - Breaking auth state management
- **TypeScript types** - Introducing type inconsistencies
- **Route protection** - Bypassing role-based route guards
- **Component exports** - Breaking component import/export patterns

### Cross-Domain Concerns
- **Service layer consistency** - Maintaining API service patterns
- **Error boundary placement** - Removing error handling components
- **Test coverage** - Breaking existing test suites
- **Build processes** - Modifying Vite/Django configurations without testing

## File Organization Patterns

### Backend Conventions
- **Models**: Domain-specific organization (`core.py`, `analytics.py`, etc.)
- **Views**: Role-based separation (`public.py`, `user.py`, `instructor.py`)
- **Serializers**: Mirror model organization with mixins
- **URLs**: Multiple URL configuration strategies for different needs

### Frontend Conventions
- **Components**: Organized by domain and reusability
- **Services**: Domain-driven with TypeScript interfaces
- **Pages**: Route-based organization with role separation
- **Types**: Comprehensive TypeScript definitions
- **Utils**: Shared utilities with specific domain helpers

## Testing Priorities

### Critical Test Areas
1. **Authentication flows** - Login, registration, role switching
2. **Course creation** - Both AI and manual workflows
3. **Enrollment & progress** - Student learning journeys
4. **AI generation** - Error handling and async processing
5. **Payment processing** - Subscription and checkout flows
6. **API compatibility** - Backend/frontend integration
7. **Role-based access** - Permission and authorization systems

### Test Commands
```bash
# Backend tests
python manage.py test
python manage.py test instructor_portal.tests.test_creation

# Frontend tests
npm run test                    # Unit tests
npx cypress run                # E2E tests
npm run test:ai-builder        # AI builder specific tests
```

## Development Workflow

### Starting Development
1. **Backend**: Activate venv, start Django server, start Celery worker
2. **Frontend**: Install dependencies, start Vite dev server
3. **Database**: Ensure PostgreSQL is running, run migrations
4. **Sample Data**: Use management commands to set up test data

### Before Committing
1. **Run tests** - Both backend and frontend test suites
2. **Check linting** - ESLint, Prettier, Black, isort
3. **Review compatibility** - Check if changes affect legacy systems
4. **Update documentation** - Maintain README and analysis files
