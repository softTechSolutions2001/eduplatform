# Save this as: backend/management/commands/extract_business_logic.py
# Create directories if they don't exist:
# backend/management/
# backend/management/commands/
# backend/management/__init__.py
# backend/management/commands/__init__.py


# python manage.py extract_business_logic

import inspect
import json
import os
from pathlib import Path, PurePosixPath

import django
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection, models
from django.urls import get_resolver


class Command(BaseCommand):
    help = "Extract comprehensive business logic from Django project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="business_logic_analysis",
            help="Output file path (default: business_logic_analysis)",
        )
        parser.add_argument(
            "--format",
            choices=["json", "markdown", "both"],
            default="both",
            help="Output format (default: both)",
        )
        parser.add_argument(
            "--endpoint-limit",
            type=int,
            default=50,
            help="Maximum number of endpoints to show in markdown (default: 50)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting business logic extraction..."))

        # Cache models for performance
        self.all_models = apps.get_models()

        # Purely read-only; no DB transaction needed
        analysis = {
            "project_info": self.get_project_info(),
            "apps_analysis": self.analyze_apps(),
            "models_analysis": self.analyze_models(),
            "views_analysis": self.analyze_views(),
            "urls_analysis": self.analyze_urls(),
            "permissions_analysis": self.analyze_permissions(),
            "business_workflows": self.identify_workflows(),
            "user_roles": self.analyze_user_roles(),
            "integrations": self.identify_integrations(),
            "database_schema": self.analyze_database_schema(),
        }

        # Safe suffix handling
        output_path = Path(options["output"])
        if output_path.suffix:
            base = output_path.with_suffix("")
        else:
            base = output_path

        # Save outputs
        if options["format"] in ["json", "both"]:
            json_path = base.with_suffix(".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, default=str)
            self.stdout.write(f"JSON analysis saved to: {json_path}")

        if options["format"] in ["markdown", "both"]:
            md_path = base.with_suffix(".md")
            self.save_markdown_report(analysis, md_path, options["endpoint_limit"])
            self.stdout.write(f"Markdown report saved to: {md_path}")

        self.stdout.write(self.style.SUCCESS("Business logic extraction completed!"))

    def get_project_info(self):
        """Get basic project information"""
        return {
            "project_name": Path(settings.BASE_DIR).name,
            "django_version": django.get_version(),
            "database_engine": settings.DATABASES["default"]["ENGINE"],
            "database_name": settings.DATABASES["default"].get("NAME", "Unknown"),
            "installed_apps": list(settings.INSTALLED_APPS),
            "middleware": list(settings.MIDDLEWARE),
            "debug_mode": settings.DEBUG,
            "time_zone": settings.TIME_ZONE,
            "language_code": settings.LANGUAGE_CODE,
            "allowed_hosts": list(settings.ALLOWED_HOSTS),
        }

    def analyze_apps(self):
        """Analyze Django apps structure"""
        apps_info = {}

        for app_config in apps.get_app_configs():
            if app_config.name.startswith("django."):
                continue

            # Materialize the generator only once
            models_list = list(app_config.get_models())
            app_info = {
                "name": app_config.name,
                "label": app_config.label,
                "path": str(PurePosixPath(app_config.path)),
                "models_count": len(models_list),
                "models": [m.__name__ for m in models_list],
            }
            apps_info[app_config.label] = app_info

        return apps_info

    def analyze_models(self):
        """Comprehensive model analysis"""
        models_info = {}

        for model in self.all_models:
            # Skip proxy models to avoid double counting
            if model._meta.proxy:
                continue

            if not model._meta.app_label.startswith("django."):
                model_info = {
                    "app": model._meta.app_label,
                    "table_name": model._meta.db_table,
                    "fields": {},
                    "relationships": {},
                    "methods": [],
                    "managers": [],
                    "meta_options": {},
                    "permissions": [],
                }

                # Analyze fields
                for field in model._meta.get_fields():
                    field_info = {
                        "type": field.__class__.__name__,
                        "null": getattr(field, "null", False),
                        "blank": getattr(field, "blank", False),
                        "unique": getattr(field, "unique", False),
                        "db_index": getattr(field, "db_index", False),
                    }

                    # Add default value
                    if (
                        hasattr(field, "default")
                        and field.default is not models.NOT_PROVIDED
                    ):
                        if callable(field.default):
                            field_info["default"] = (
                                f"callable: {field.default.__name__}"
                            )
                        else:
                            field_info["default"] = str(field.default)

                    # Add relationship info
                    if hasattr(field, "related_model") and field.related_model:
                        field_info["related_model"] = field.related_model.__name__
                        field_info["relationship_type"] = field.__class__.__name__

                    # Add choices if available - handle lazy translations
                    if hasattr(field, "choices") and field.choices:
                        field_info["choices"] = [
                            tuple(str(c) for c in choice) for choice in field.choices
                        ]

                    # Add validators
                    if hasattr(field, "validators") and field.validators:
                        field_info["validators"] = [
                            v.__class__.__name__ for v in field.validators
                        ]

                    model_info["fields"][field.name] = field_info

                    # Populate relationships section
                    if "related_model" in field_info:
                        model_info["relationships"][field.name] = {
                            "to": field_info["related_model"],
                            "type": field_info["relationship_type"],
                        }

                # Analyze methods (improved filtering)
                for method_name in dir(model):
                    if not method_name.startswith("_"):
                        method = getattr(model, method_name)
                        if inspect.isfunction(method) or inspect.ismethod(method):
                            try:
                                sig = inspect.signature(method)
                                doc = inspect.getdoc(method)
                                model_info["methods"].append(
                                    {
                                        "name": method_name,
                                        "signature": str(sig),
                                        "docstring": (
                                            doc[:100] + "..."
                                            if doc and len(doc) > 100
                                            else doc
                                        ),
                                    }
                                )
                            except Exception:
                                model_info["methods"].append({"name": method_name})

                # Enhanced Meta options
                meta = model._meta
                model_info["meta_options"] = {
                    "verbose_name": str(meta.verbose_name),
                    "verbose_name_plural": str(meta.verbose_name_plural),
                    "ordering": list(meta.ordering) if meta.ordering else [],
                    "unique_together": (
                        list(meta.unique_together) if meta.unique_together else []
                    ),
                    "permissions": list(meta.permissions) if meta.permissions else [],
                    "db_table": meta.db_table,
                    "managed": meta.managed,
                    "indexes": (
                        [str(i.name) for i in meta.indexes] if meta.indexes else []
                    ),
                    "constraints": (
                        [str(c.name) for c in meta.constraints]
                        if meta.constraints
                        else []
                    ),
                }

                # Add database constraints from introspection
                try:
                    with connection.cursor() as cursor:
                        constraints = connection.introspection.get_constraints(
                            cursor, model._meta.db_table
                        )
                        model_info["database_constraints"] = {
                            name: {
                                "columns": constraint["columns"],
                                "primary_key": constraint["primary_key"],
                                "unique": constraint["unique"],
                                "foreign_key": constraint["foreign_key"],
                                "check": constraint["check"],
                                "index": constraint["index"],
                            }
                            for name, constraint in constraints.items()
                        }
                except Exception as e:
                    model_info["database_constraints"] = {"error": str(e)}

                models_info[f"{model._meta.app_label}.{model.__name__}"] = model_info

        return models_info

    def analyze_views(self):
        """Analyze views from URL patterns"""
        views_info = {}

        try:
            resolver = get_resolver()
            url_patterns = self.extract_url_patterns(resolver.url_patterns)

            for pattern_info in url_patterns:
                view_name = pattern_info.get("view_name", "Unknown")
                if view_name not in views_info:
                    views_info[view_name] = {
                        "urls": [],
                        "methods": set(),
                        "type": pattern_info.get("type", "Unknown"),
                    }

                views_info[view_name]["methods"].update(pattern_info.get("methods", []))
                views_info[view_name]["urls"].append(
                    {
                        "pattern": pattern_info["pattern"],
                        "name": pattern_info.get("name", "unnamed"),
                        "methods": pattern_info.get("methods", []),
                    }
                )

            # Convert methods sets to sorted lists for JSON serialization
            for data in views_info.values():
                data["methods"] = sorted(data["methods"])

        except Exception as e:
            views_info["error"] = str(e)

        return views_info

    def extract_url_patterns(self, patterns, prefix=""):
        """Recursively extract URL patterns"""
        url_list = []

        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                # Include patterns from included URLconfs
                url_list.extend(
                    self.extract_url_patterns(
                        pattern.url_patterns, prefix + str(pattern.pattern)
                    )
                )
            else:
                pattern_info = {
                    "pattern": prefix + str(pattern.pattern),
                    "name": getattr(pattern, "name", None),
                    "view_name": self.get_view_name(pattern),
                    "methods": self.get_view_methods(pattern),
                    "type": self.get_view_type(pattern),
                }
                url_list.append(pattern_info)

        return url_list

    def get_view_name(self, pattern):
        """Get view name from URL pattern"""
        try:
            if hasattr(pattern, "callback"):
                callback = pattern.callback
                if hasattr(callback, "__name__"):
                    return callback.__name__
                elif hasattr(callback, "view_class"):
                    return callback.view_class.__name__
                else:
                    return str(callback)
            return "Unknown"
        except Exception:
            return "Unknown"

    def get_view_methods(self, pattern):
        """Get HTTP methods for view"""
        try:
            if hasattr(pattern, "callback"):
                callback = pattern.callback

                # For DRF ViewSets
                if hasattr(callback, "actions"):
                    return [m.upper() for m in callback.actions.keys()]

                # For regular views
                if hasattr(callback, "view_class"):
                    view_class = callback.view_class
                    if hasattr(view_class, "http_method_names"):
                        return [
                            m.upper()
                            for m in view_class.http_method_names
                            if m != "options"
                        ]

                # For function-based views
                if hasattr(callback, "http_method_names"):
                    return [
                        m.upper() for m in callback.http_method_names if m != "options"
                    ]

            return []
        except Exception:
            return []

    def get_view_type(self, pattern):
        """Get view type"""
        try:
            if hasattr(pattern, "callback"):
                callback = pattern.callback

                # Import DRF classes if available
                try:
                    from rest_framework.views import APIView
                    from rest_framework.viewsets import ViewSetMixin

                    if hasattr(callback, "view_class"):
                        view_class = callback.view_class
                        if issubclass(view_class, ViewSetMixin):
                            return "ViewSet"
                        elif issubclass(view_class, APIView):
                            return "APIView"
                        else:
                            return "ClassBasedView"
                    elif inspect.isfunction(callback):
                        return "FunctionView"
                    else:
                        return "ClassBasedView"
                except ImportError:
                    # DRF not installed
                    if hasattr(callback, "view_class"):
                        return "ClassBasedView"
                    elif inspect.isfunction(callback):
                        return "FunctionView"
                    else:
                        return "Unknown"

            return "Unknown"
        except Exception:
            return "Unknown"

    def analyze_urls(self):
        """Analyze URL patterns and endpoints"""
        try:
            resolver = get_resolver()
            patterns = self.extract_url_patterns(resolver.url_patterns)

            # Group by namespaces
            namespaces = {}
            for pattern in patterns:
                name = pattern.get("name", "")
                if ":" in name:
                    namespace = name.split(":")[0]
                    if namespace not in namespaces:
                        namespaces[namespace] = []
                    namespaces[namespace].append(pattern)

            return {
                "total_endpoints": len(patterns),
                "endpoints": patterns,
                "namespaces": list(namespaces.keys()),
                "endpoints_by_namespace": namespaces,
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_permissions(self):
        """Analyze permissions system - optimized"""
        permissions_info = {
            "user_model": get_user_model().__name__,
            "model_permissions": {},
        }

        # Optimized query with select_related
        perms = Permission.objects.select_related("content_type").order_by(
            "content_type__app_label"
        )

        for perm in perms:
            ct = perm.content_type
            if not ct.app_label.startswith("django."):
                model_key = f"{ct.app_label}.{ct.model}"
                if model_key not in permissions_info["model_permissions"]:
                    permissions_info["model_permissions"][model_key] = []

                permissions_info["model_permissions"][model_key].append(
                    {"codename": perm.codename, "name": str(perm.name)}
                )

        return permissions_info

    def identify_workflows(self):
        """Identify business workflows based on models and apps"""
        workflows = []

        app_labels = [
            app.label
            for app in apps.get_app_configs()
            if not app.name.startswith("django.")
        ]

        for app_label in app_labels:
            try:
                # Materialize the generator to avoid multiple iterations
                models_list = list(apps.get_app_config(app_label).get_models())
                app_models = [model.__name__.lower() for model in models_list]

                workflow_mappings = [
                    ("course", "Course Management"),
                    ("instructor", "Instructor Portal"),
                    ("user", "User Management"),
                    ("ai", "AI-Powered Features"),
                    ("content", "Content Management"),
                    ("payment", "Payment Processing"),
                    ("notification", "Notification System"),
                    ("analytics", "Analytics & Reporting"),
                    ("auth", "Authentication & Authorization"),
                ]

                for keyword, workflow_name in workflow_mappings:
                    if keyword in app_label.lower() or any(
                        keyword in model for model in app_models
                    ):
                        workflows.append(
                            {
                                "name": workflow_name,
                                "app": app_label,
                                "models": app_models,
                                "model_count": len(app_models),
                            }
                        )
                        break
            except Exception:
                continue

        return workflows

    def analyze_user_roles(self):
        """Analyze user roles and permissions"""
        User = get_user_model()

        roles_info = {
            "user_model_name": User.__name__,
            "user_model_fields": [f.name for f in User._meta.get_fields()],
            "user_model_methods": [
                m
                for m in dir(User)
                if not m.startswith("_") and callable(getattr(User, m))
            ],
            "groups_enabled": "django.contrib.auth" in settings.INSTALLED_APPS,
            "custom_user_model": User.__name__ != "User",
            "user_model_table": User._meta.db_table,
        }

        # Analyze user-related fields
        user_fields = {}
        for field in User._meta.get_fields():
            if not field.name.startswith("_"):
                user_fields[field.name] = {
                    "type": field.__class__.__name__,
                    "null": getattr(field, "null", False),
                    "blank": getattr(field, "blank", False),
                }

        roles_info["user_fields_detail"] = user_fields

        return roles_info

    def identify_integrations(self):
        """Identify third-party integrations"""
        integrations = []
        seen = set()

        # Check installed apps for third-party packages
        third_party_mappings = {
            "rest_framework": "Django REST Framework",
            "corsheaders": "CORS Headers",
            "celery": "Celery Task Queue",
            "redis": "Redis Cache",
            "stripe": "Stripe Payment",
            "paypal": "PayPal Payment",
            "oauth": "OAuth Authentication",
            "social": "Social Authentication",
            "allauth": "Django AllAuth",
            "crispy_forms": "Crispy Forms",
            "storages": "Django Storages",
            "whitenoise": "WhiteNoise Static Files",
            "debug_toolbar": "Debug Toolbar",
            "extensions": "Django Extensions",
            "compressor": "Django Compressor",
            "channels": "Django Channels",
            "graphene": "GraphQL",
        }

        for app in settings.INSTALLED_APPS:
            for tp_app, description in third_party_mappings.items():
                if tp_app in app.lower() and description not in seen:
                    integrations.append(
                        {"name": description, "app": app, "type": "Django App"}
                    )
                    seen.add(description)

        return integrations

    def analyze_database_schema(self):
        """Analyze database schema relationships"""
        schema_info = {
            "total_tables": 0,
            "relationships": [],
            "indexes": [],
            "constraints": [],
        }

        for model in self.all_models:
            if model._meta.proxy:
                continue

            if not model._meta.app_label.startswith("django."):
                schema_info["total_tables"] += 1

                # Analyze relationships
                for field in model._meta.get_fields():
                    if hasattr(field, "related_model") and field.related_model:
                        # Fixed on_delete handling
                        on_delete = getattr(field, "on_delete", None)
                        schema_info["relationships"].append(
                            {
                                "from_model": f"{model._meta.app_label}.{model.__name__}",
                                "to_model": f"{field.related_model._meta.app_label}.{field.related_model.__name__}",
                                "field": field.name,
                                "type": field.__class__.__name__,
                                "on_delete": (
                                    on_delete.__name__ if callable(on_delete) else None
                                ),
                            }
                        )

                # Analyze indexes with safe field serialization
                for index in model._meta.indexes:
                    schema_info["indexes"].append(
                        {
                            "model": f"{model._meta.app_label}.{model.__name__}",
                            "name": index.name,
                            "fields": [str(f) for f in getattr(index, "fields", [])],
                            "unique": getattr(index, "unique", False),
                        }
                    )

                # Analyze constraints
                for constraint in model._meta.constraints:
                    schema_info["constraints"].append(
                        {
                            "model": f"{model._meta.app_label}.{model.__name__}",
                            "name": constraint.name,
                            "type": constraint.__class__.__name__,
                            "fields": getattr(constraint, "fields", []),
                        }
                    )

        return schema_info

    def save_markdown_report(self, analysis, output_path, endpoint_limit):
        """Save analysis as markdown report"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Django Project Business Logic Analysis\n\n")
            f.write(f"Generated on: {django.utils.timezone.now()}\n\n")

            # Project Info
            f.write("## Project Information\n")
            for key, value in analysis["project_info"].items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {str(value)}\n")
            f.write("\n")

            # Apps Analysis
            f.write("## Applications\n")
            for app_name, app_info in analysis["apps_analysis"].items():
                f.write(f"### {app_name}\n")
                f.write(f"- **Path**: {app_info['path']}\n")
                f.write(f"- **Models Count**: {app_info['models_count']}\n")
                f.write(f"- **Models**: {', '.join(app_info['models'])}\n\n")

            # Business Workflows
            f.write("## Business Workflows\n")
            for workflow in analysis["business_workflows"]:
                f.write(f"### {workflow['name']}\n")
                f.write(f"- **App**: {workflow['app']}\n")
                f.write(f"- **Model Count**: {workflow['model_count']}\n")
                f.write(f"- **Models**: {', '.join(workflow['models'])}\n\n")

            # Models Analysis (summary)
            f.write("## Models Summary\n")
            for model_name, model_info in analysis["models_analysis"].items():
                f.write(f"### {model_name}\n")
                f.write(f"- **App**: {model_info['app']}\n")
                f.write(f"- **Table**: {model_info['table_name']}\n")
                f.write(f"- **Fields**: {len(model_info['fields'])}\n")
                f.write(f"- **Methods**: {len(model_info['methods'])}\n")
                f.write(
                    f"- **Relationships**: {len([f for f in model_info['fields'].values() if 'related_model' in f])}\n\n"
                )

            # Database Schema
            f.write("## Database Schema\n")
            schema = analysis["database_schema"]
            f.write(f"- **Total Tables**: {schema['total_tables']}\n")
            f.write(f"- **Total Relationships**: {len(schema['relationships'])}\n")
            f.write(f"- **Total Indexes**: {len(schema['indexes'])}\n")
            f.write(f"- **Total Constraints**: {len(schema['constraints'])}\n\n")

            # URLs grouped by namespace for better readability
            f.write("## API Endpoints\n")
            if "endpoints" in analysis["urls_analysis"]:
                endpoints = analysis["urls_analysis"]["endpoints"][:endpoint_limit]

                # Group by namespace instead of view name
                namespaces = analysis["urls_analysis"].get("endpoints_by_namespace", {})

                for namespace, ns_endpoints in namespaces.items():
                    f.write(f"### {namespace}\n")
                    for endpoint in ns_endpoints[:endpoint_limit]:
                        methods = ", ".join(endpoint.get("methods", []))
                        f.write(
                            f"- `{endpoint['pattern']}` [{methods}] -> {endpoint['view_name']}\n"
                        )
                    f.write("\n")

                # Handle endpoints without namespace
                unnamed_endpoints = [
                    ep for ep in endpoints if not ep.get("name", "").count(":")
                ]
                if unnamed_endpoints:
                    f.write("### Other Endpoints\n")
                    for endpoint in unnamed_endpoints[:endpoint_limit]:
                        methods = ", ".join(endpoint.get("methods", []))
                        f.write(
                            f"- `{endpoint['pattern']}` [{methods}] -> {endpoint['view_name']}\n"
                        )
                    f.write("\n")

                f.write(
                    f"**Total Endpoints**: {analysis['urls_analysis']['total_endpoints']}\n"
                )
                if analysis["urls_analysis"]["total_endpoints"] > endpoint_limit:
                    f.write(f"*(Showing first {endpoint_limit} endpoints)*\n")
                f.write("\n")

            # Integrations
            f.write("## Third-Party Integrations\n")
            for integration in analysis["integrations"]:
                f.write(f"- **{integration['name']}**: {integration['app']}\n")
            f.write("\n")

            # User Model
            f.write("## User Management\n")
            user_info = analysis["user_roles"]
            f.write(f"- **User Model**: {user_info['user_model_name']}\n")
            f.write(f"- **Custom User Model**: {user_info['custom_user_model']}\n")
            f.write(f"- **Groups Enabled**: {user_info['groups_enabled']}\n")
            f.write(f"- **User Fields**: {len(user_info['user_model_fields'])}\n")
            f.write(f"- **User Methods**: {len(user_info['user_model_methods'])}\n\n")

            f.write("---\n")
            f.write(
                "*This report was generated automatically by the Django Business Logic Extractor*\n"
            )
