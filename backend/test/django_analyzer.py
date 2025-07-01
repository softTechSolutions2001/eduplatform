#!/usr/bin/env python3

# fmt: off
# isort: off


#!/usr/bin/env python3
"""
Integrated Django Backend Analyzer

This script analyzes a Django project using both static code analysis and runtime
introspection to generate a comprehensive report of:
- Models and their relationships
- Fields and their types, constraints
- API endpoints/URLs
- View functions/methods and their permissions
- Serializers with field definitions
- Authentication mechanisms

The output is suitable for frontend developers to build a complete frontend
without needing access to the backend codebase.

Usage:
  1. Run from outside the Django project:
     python django_analyzer.py /path/to/django/project
     
  2. Or run within the Django environment:
     cd /path/to/django/project
     python django_analyzer.py --runtime
"""

import os
import sys
import ast
import json
import re
import inspect
import importlib
import importlib.util
from pathlib import Path
from collections import defaultdict

# Configuration
OUTPUT_FORMATS = ['json', 'markdown']

class DjangoAnalyzer:
    """Main analyzer class that orchestrates the analysis of a Django project."""

    def __init__(self, project_path=None, output_format='markdown', use_runtime=False, settings_module=None):
        """
        Initialize the analyzer with the project path and output format.

        Args:
            project_path (str): Path to the Django project (required for static analysis)
            output_format (str): Output format (json or markdown)
            use_runtime (bool): Whether to use runtime introspection
            settings_module (str): Django settings module for runtime analysis
        """
        self.project_path = Path(project_path) if project_path else None
        self.output_format = output_format
        self.use_runtime = use_runtime
        self.settings_module = settings_module

        if not use_runtime and (not self.project_path or not self.project_path.exists()):
            raise ValueError(f"Project path does not exist: {project_path}")

        if output_format not in OUTPUT_FORMATS:
            raise ValueError(f"Output format must be one of {OUTPUT_FORMATS}")

        self.results = {
            'models': [],
            'views': [],
            'urls': [],
            'serializers': [],
            'forms': [],
            'api_endpoints': [],
            'auth': {},
        }

        # Django runtime objects (when using runtime analysis)
        self.django_apps = None
        self.django_initialized = False

    def analyze(self):
        """Main method to analyze the Django project."""
        print(f"Analyzing Django project{' at: ' + str(self.project_path) if self.project_path else ''}")

        # Try runtime analysis if requested
        if self.use_runtime:
            try:
                self._setup_django()
                self.django_initialized = True
                print("Django runtime environment initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Django runtime environment: {e}")
                if not self.project_path:
                    raise ValueError("Cannot fall back to static analysis: project_path not provided")
                print("Falling back to static analysis")

        # Perform static analysis if we're not using runtime or runtime initialization failed
        if not self.django_initialized:
            # Find all Django apps in the project
            apps = self._discover_apps()
            print(f"Discovered apps through static analysis: {[app.name for app in apps]}")

            for app_path in apps:
                app_name = app_path.name
                print(f"\nAnalyzing app: {app_name}")

                # Analyze models
                self._analyze_models_static(app_path, app_name)

                # Analyze views
                self._analyze_views_static(app_path, app_name)

                # Analyze URLs
                self._analyze_urls_static(app_path, app_name)

                # Analyze serializers
                self._analyze_serializers_static(app_path, app_name)

                # Analyze forms
                self._analyze_forms_static(app_path, app_name)
        else:
            # Use runtime analysis
            print("Using Django runtime introspection")

            # Analyze models using Django's model registry
            self._analyze_models_runtime()

            # Analyze serializers through app configs
            for app_config in self.django_apps.get_app_configs():
                # Analyze serializers
                self._analyze_serializers_runtime(app_config)

                # Analyze views and permissions
                self._analyze_views_runtime(app_config)

            # Analyze URLs using Django's URL resolver
            self._analyze_urls_runtime()

        # Post-process to connect related information
        self._post_process()

        return self.results

    def _setup_django(self):
        """Set up Django runtime environment."""
        import django

        if self.settings_module:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", self.settings_module)
        elif "DJANGO_SETTINGS_MODULE" not in os.environ:
            # Try to find settings module
            if self.project_path:
                for item in self.project_path.glob("**/settings.py"):
                    module_path = str(item.relative_to(self.project_path)).replace("/", ".").replace("\\", ".").replace(".py", "")
                    os.environ.setdefault("DJANGO_SETTINGS_MODULE", module_path)
                    break

            # If we still don't have settings, try a common pattern
            if "DJANGO_SETTINGS_MODULE" not in os.environ:
                project_name = self.project_path.name if self.project_path else None
                if project_name:
                    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")

        # Initialize Django
        django.setup()

        # Import Django apps registry
        from django.apps import apps
        self.django_apps = apps

    def _discover_apps(self):
        """Discover all Django apps in the project using static analysis."""
        apps = []

        # Look for directories that contain typical Django app files
        for path in self.project_path.glob("**/"):
            if path.is_dir() and not str(path).startswith('.'):
                if any((path / file).exists() for file in ['models.py', 'views.py', 'urls.py', 'apps.py']):
                    apps.append(path)

        return apps

    def _analyze_models_static(self, app_path, app_name):
        """Analyze models.py file to extract model definitions and relationships using static analysis."""
        models_file = app_path / 'models.py'
        if not models_file.exists():
            return

        print(f"  Analyzing models in {app_name} (static)...")

        try:
            with open(models_file, 'r') as file:
                content = file.read()

            tree = ast.parse(content)
            model_visitor = ModelVisitor(app_name)
            model_visitor.visit(tree)

            self.results['models'].extend(model_visitor.models)

        except Exception as e:
            print(f"Error analyzing models in {app_name}: {str(e)}")

    def _analyze_models_runtime(self):
        """Analyze models using Django's model registry."""
        print("Analyzing Django models (runtime)...")

        for model in self.django_apps.get_models():
            meta = model._meta
            app_name = meta.app_label
            model_name = meta.object_name

            print(f"  Processing model: {app_name}.{model_name}")

            model_info = {
                'name': model_name,
                'app_name': app_name,
                'fields': [],
                'relationships': [],
                'methods': []
            }

            # Extract docstring if available
            model_info['docstring'] = model.__doc__ or ''

            # Process fields
            for field in meta.get_fields():
                field_info = {
                    'name': field.name,
                    'type': field.get_internal_type()
                }

                # Is it a relationship?
                if field.is_relation:
                    rel_info = {
                        'name': field.name,
                        'type': field_info['type'],
                        'is_relationship': True,
                        'related_model': field.related_model._meta.object_name
                    }

                    # Get related name
                    if hasattr(field, 'remote_field') and hasattr(field.remote_field, 'related_name'):
                        rel_info['related_name'] = field.remote_field.related_name or f"{model_name.lower()}_set"

                    # Check for through model on M2M
                    if field_info['type'] == 'ManyToManyField' and hasattr(field, 'remote_field') and hasattr(field.remote_field, 'through'):
                        through = field.remote_field.through
                        if through and through._meta.auto_created is False:
                            rel_info['through'] = through._meta.object_name

                    model_info['relationships'].append(rel_info)
                else:
                    # Regular field attributes
                    field_info['required'] = not field.blank and not field.null

                    if field.has_default():
                        default_value = field.default
                        if callable(default_value):
                            field_info['default'] = f"<function: {default_value.__name__}>"
                        else:
                            field_info['default'] = str(default_value)

                    if hasattr(field, 'choices') and field.choices:
                        field_info['choices'] = [choice[1] for choice in field.choices]

                    if field.help_text:
                        field_info['help_text'] = str(field.help_text)

                    model_info['fields'].append(field_info)

            # Extract methods (excluding private and Django's built-ins)
            for name in dir(model):
                if not name.startswith('_') or name in ['__str__', '__repr__']:
                    attr = getattr(model, name)
                    if callable(attr) and not isinstance(attr, type):
                        try:
                            method_info = {
                                'name': name,
                                'args': inspect.getfullargspec(attr).args,
                                'docstring': attr.__doc__ or ''
                            }
                            # Remove 'self' from args
                            if 'self' in method_info['args']:
                                method_info['args'].remove('self')

                            model_info['methods'].append(method_info)
                        except (TypeError, ValueError):
                            # Skip if not inspectable
                            pass

            self.results['models'].append(model_info)

    def _analyze_views_static(self, app_path, app_name):
        """Analyze views.py and viewsets to extract view functions, methods, and API endpoints using static analysis."""
        views_file = app_path / 'views.py'
        viewsets_file = app_path / 'viewsets.py'  # Some projects separate viewsets
        api_views_file = app_path / 'api.py'      # Some projects use api.py

        view_files = [f for f in [views_file, viewsets_file, api_views_file] if f.exists()]

        if not view_files:
            return

        print(f"  Analyzing views in {app_name} (static)...")

        for view_file in view_files:
            try:
                with open(view_file, 'r') as file:
                    content = file.read()

                tree = ast.parse(content)
                view_visitor = ViewVisitor(app_name, view_file.name)
                view_visitor.visit(tree)

                self.results['views'].extend(view_visitor.views)

            except Exception as e:
                print(f"Error analyzing {view_file.name} in {app_name}: {str(e)}")

    def _analyze_views_runtime(self, app_config):
        """Analyze views and extract permission/throttle settings using runtime analysis."""
        app_name = app_config.name
        import_path = f"{app_name}.views"

        print(f"  Analyzing views in {app_name} (runtime)...")

        try:
            # Import the views module
            views_module = importlib.import_module(import_path)
            source = inspect.getsource(views_module)

            # Parse with AST for static analysis of permissions and throttles
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this is a view class
                    view_base_classes = [
                        'View', 'APIView', 'GenericAPIView', 'ViewSet', 'ModelViewSet', 
                        'ReadOnlyModelViewSet', 'CreateView', 'ListView', 'DetailView',
                        'UpdateView', 'DeleteView'
                    ]

                    is_view = False
                    for base in node.bases:
                        base_name = None
                        if isinstance(base, ast.Name):
                            base_name = base.id
                        elif isinstance(base, ast.Attribute):
                            base_name = base.attr

                        if base_name and base_name in view_base_classes:
                            is_view = True
                            break

                    if is_view:
                        view_info = {
                            'name': node.name,
                            'app_name': app_config.label,
                            'type': 'Class-based',
                            'class_methods': []
                        }

                        # Extract docstring
                        if ast.get_docstring(node):
                            view_info['docstring'] = ast.get_docstring(node)

                        # Extract permission_classes
                        permission_classes = []
                        throttle_classes = []
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        if target.id == 'permission_classes':
                                            if isinstance(item.value, ast.List) or isinstance(item.value, ast.Tuple):
                                                permission_classes = [ast.unparse(el).strip() for el in item.value.elts]
                                        elif target.id == 'throttle_classes':
                                            if isinstance(item.value, ast.List) or isinstance(item.value, ast.Tuple):
                                                throttle_classes = [ast.unparse(el).strip() for el in item.value.elts]
                                        elif target.id == 'serializer_class':
                                            if isinstance(item.value, ast.Name):
                                                view_info['serializer_class'] = item.value.id

                            # Extract methods
                            elif isinstance(item, ast.FunctionDef):
                                view_info['class_methods'].append(item.name)

                                # Check for custom permission or throttle methods
                                if item.name in ('get_permissions', 'get_throttles'):
                                    view_info[f"{item.name}_impl"] = ast.get_source_segment(source, item)

                        if permission_classes:
                            view_info['permission_classes'] = permission_classes

                        if throttle_classes:
                            view_info['throttle_classes'] = throttle_classes

                        # Extract runtime information from actual class if possible
                        try:
                            view_class = getattr(views_module, node.name)

                            # Extract serializer class
                            if hasattr(view_class, 'serializer_class'):
                                serializer_class = view_class.serializer_class
                                if serializer_class:
                                    view_info['serializer_class'] = serializer_class.__name__

                            # Extract queryset model
                            if hasattr(view_class, 'queryset') and view_class.queryset is not None:
                                model = view_class.queryset.model
                                view_info['model'] = model._meta.object_name
                        except (AttributeError, TypeError):
                            pass

                        self.results['views'].append(view_info)

                elif isinstance(node, ast.FunctionDef):
                    # Check if this is likely a view function
                    is_view = False
                    for arg in node.args.args:
                        if arg.arg == 'request':
                            is_view = True
                            break

                    if is_view:
                        view_info = {
                            'name': node.name,
                            'app_name': app_config.label,
                            'type': 'Function-based'
                        }

                        # Extract docstring
                        if ast.get_docstring(node):
                            view_info['docstring'] = ast.get_docstring(node)

                        self.results['views'].append(view_info)

        except (ImportError, OSError) as e:
            print(f"Error analyzing views in {app_name} (runtime): {str(e)}")

    def _analyze_urls_static(self, app_path, app_name):
        """Analyze urls.py to extract URL patterns and API endpoints using static analysis."""
        urls_file = app_path / 'urls.py'
        if not urls_file.exists():
            return

        print(f"  Analyzing URLs in {app_name} (static)...")

        try:
            with open(urls_file, 'r') as file:
                content = file.read()

            url_visitor = URLVisitor(app_name)
            tree = ast.parse(content)
            url_visitor.visit(tree)

            # Extract API endpoints from DRF router registrations
            api_endpoints = self._extract_drf_router_endpoints(content, app_name)

            self.results['urls'].extend(url_visitor.urls)
            self.results['api_endpoints'].extend(api_endpoints)

        except Exception as e:
            print(f"Error analyzing URLs in {app_name}: {str(e)}")

    def _analyze_urls_runtime(self):
        """Analyze URLs using Django's URL resolver."""
        print("Analyzing Django URLs (runtime)...")

        try:
            from django.urls import get_resolver

            resolver = get_resolver()
            patterns = self._flatten_urlpatterns(resolver.url_patterns)

            for pattern, callback, pattern_name in patterns:
                url_info = {
                    'path': pattern,
                    'name': pattern_name or ''
                }

                # Extract view information
                if hasattr(callback, '__name__'):
                    url_info['view_name'] = callback.__name__
                elif hasattr(callback, '__class__'):
                    url_info['view_name'] = callback.__class__.__name__

                # Determine HTTP methods
                methods = []
                if hasattr(callback, 'actions'):  # ViewSet as_view({..})
                    methods = list(callback.actions.keys())
                    url_info['http_methods'] = [m.upper() for m in methods]
                elif hasattr(callback, 'view_class'):
                    view_class = callback.view_class
                    for m in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options'):
                        if hasattr(view_class, m):
                            methods.append(m.upper())
                    url_info['http_methods'] = methods

                self.results['urls'].append(url_info)

        except (ImportError, AttributeError) as e:
            print(f"Error analyzing URLs (runtime): {str(e)}")

    def _flatten_urlpatterns(self, urlpatterns, prefix=""):
        """Recursively collect (pattern, callback, name) tuples from URL patterns."""
        from django.urls import URLPattern, URLResolver

        items = []
        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern):
                pattern_str = prefix + str(pattern.pattern)
                callback = pattern.callback
                name = pattern.name
                items.append((pattern_str, callback, name))
            elif isinstance(pattern, URLResolver):
                new_prefix = prefix + str(pattern.pattern)
                items.extend(self._flatten_urlpatterns(pattern.url_patterns, new_prefix))
        return items

    def _extract_drf_router_endpoints(self, content, app_name):
        """Extract API endpoints from DRF router registrations."""
        endpoints = []

        # Look for router.register patterns
        router_pattern = r"router\.register\(['\"]([^'\"]+)['\"],\s*(\w+)"
        matches = re.findall(router_pattern, content)

        for url_prefix, viewset in matches:
            endpoints.append({
                'app_name': app_name,
                'url_prefix': url_prefix,
                'viewset': viewset,
                'http_methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],  # Default DRF methods
                'is_viewset': True
            })

        return endpoints

    def _analyze_serializers_static(self, app_path, app_name):
        """Analyze serializers.py to extract serializer definitions using static analysis."""
        serializers_file = app_path / 'serializers.py'
        if not serializers_file.exists():
            return

        print(f"  Analyzing serializers in {app_name} (static)...")

        try:
            with open(serializers_file, 'r') as file:
                content = file.read()

            tree = ast.parse(content)
            serializer_visitor = SerializerVisitor(app_name)
            serializer_visitor.visit(tree)

            self.results['serializers'].extend(serializer_visitor.serializers)

        except Exception as e:
            print(f"Error analyzing serializers in {app_name}: {str(e)}")

    def _analyze_serializers_runtime(self, app_config):
        """Analyze serializers using AST parser with runtime module import."""
        app_name = app_config.name
        import_path = f"{app_name}.serializers"

        print(f"  Analyzing serializers in {app_name} (runtime)...")

        try:
            # Import the serializers module
            serializers_module = importlib.import_module(import_path)
            source = inspect.getsource(serializers_module)

            # Parse with AST
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this is a serializer class
                    serializer_base_classes = [
                        'Serializer', 'ModelSerializer', 'HyperlinkedModelSerializer',
                        'ListSerializer', 'BaseSerializer'
                    ]

                    is_serializer = False
                    for base in node.bases:
                        base_name = None
                        if isinstance(base, ast.Name):
                            base_name = base.id
                        elif isinstance(base, ast.Attribute):
                            base_name = base.attr

                        if base_name and base_name in serializer_base_classes:
                            is_serializer = True
                            break

                    if is_serializer:
                        serializer_info = {
                            'name': node.name,
                            'app_name': app_config.label,
                            'fields': []
                        }

                        # Try to get actual serializer class for additional info
                        serializer_class = None
                        try:
                            serializer_class = getattr(serializers_module, node.name)
                        except AttributeError:
                            pass

                        # Extract fields information
                        meta = None
                        for item in node.body:
                            # Look for Meta class for model info
                            if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                                for meta_item in item.body:
                                    if isinstance(meta_item, ast.Assign):
                                        for target in meta_item.targets:
                                            if isinstance(target, ast.Name):
                                                if target.id == 'model':
                                                    if isinstance(meta_item.value, ast.Name):
                                                        serializer_info['model'] = meta_item.value.id
                                                elif target.id == 'fields':
                                                    if isinstance(meta_item.value, ast.Str) and meta_item.value.s == '__all__':
                                                        serializer_info['fields'] = ['__all__']
                                                    elif isinstance(meta_item.value, ast.List) or isinstance(meta_item.value, ast.Tuple):
                                                        fields = []
                                                        for elt in meta_item.value.elts:
                                                            if isinstance(elt, ast.Str):
                                                                fields.append(elt.s)
                                                        serializer_info['fields'] = fields

                            # Look for field declarations
                            elif isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        field_name = target.id

                                        # Skip Meta class
                                        if field_name == 'Meta':
                                            continue

                                        # Try to detect if this is a field
                                        if isinstance(item.value, ast.Call):
                                            field_type = None
                                            if isinstance(item.value.func, ast.Name):
                                                field_type = item.value.func.id
                                            elif isinstance(item.value.func, ast.Attribute):
                                                field_type = item.value.func.attr

                                            if field_type and field_type.endswith('Field'):
                                                field_info = {
                                                    'name': field_name,
                                                    'type': field_type
                                                }

                                                # Extract field options
                                                for keyword in item.value.keywords:
                                                    if keyword.arg in ('required', 'read_only', 'write_only'):
                                                        try:
                                                            field_info[keyword.arg] = ast.literal_eval(keyword.value)
                                                        except (ValueError, SyntaxError):
                                                            field_info[keyword.arg] = str(ast.unparse(keyword.value))
                                                    elif keyword.arg == 'default':
                                                        try:
                                                            field_info['default'] = ast.literal_eval(keyword.value)
                                                        except (ValueError, SyntaxError):
                                                            field_info['default'] = str(ast.unparse(keyword.value))
                                                    elif keyword.arg == 'choices':
                                                        try:
                                                            field_info['choices'] = ast.literal_eval(keyword.value)
                                                        except (ValueError, SyntaxError):
                                                            field_info['choices'] = str(ast.unparse(keyword.value))

                                                serializer_info['fields'].append(field_info)

                        # If we have a real serializer class, get field info from there
                        if serializer_class:
                            try:
                                # Try to instantiate the serializer to get field definitions
                                instance = serializer_class()
                                if hasattr(instance, 'fields'):
                                    # Replace static fields analysis with runtime fields if available
                                    detailed_fields = []
                                    for name, field in instance.fields.items():
                                        field_info = {
                                            'name': name,
                                            'type': field.__class__.__name__,
                                            'required': getattr(field, 'required', None),
                                            'read_only': getattr(field, 'read_only', None),
                                            'write_only': getattr(field, 'write_only', None),
                                            'allow_null': getattr(field, 'allow_null', None)
                                        }

                                        # Get default value if any
                                        if hasattr(field, 'default') and field.default != serializers.empty:
                                            if callable(field.default):
                                                field_info['default'] = f"<function: {field.default.__name__}>"
                                            else:
                                                field_info['default'] = field.default

                                        # Get choices if any
                                        if hasattr(field, 'choices') and field.choices:
                                            field_info['choices'] = dict(field.choices)

                                        # Get validators if any
                                        if hasattr(field, 'validators') and field.validators:
                                            field_info['validators'] = [v.__class__.__name__ for v in field.validators]

                                        detailed_fields.append(field_info)

                                    if detailed_fields:
                                        serializer_info['fields'] = detailed_fields
                            except Exception:
                                # If instantiation fails, keep the static analysis results
                                pass

                        self.results['serializers'].append(serializer_info)

        except (ImportError, OSError) as e:
            print(f"Error analyzing serializers in {app_name} (runtime): {str(e)}")

    def _analyze_forms_static(self, app_path, app_name):
        """Analyze forms.py to extract form definitions."""
        forms_file = app_path / 'forms.py'
        if not forms_file.exists():
            return

        print(f"  Analyzing forms in {app_name}...")

        try:
            with open(forms_file, 'r') as file:
                content = file.read()

            tree = ast.parse(content)
            form_visitor = FormVisitor(app_name)
            form_visitor.visit(tree)

            self.results['forms'].extend(form_visitor.forms)

        except Exception as e:
            print(f"Error analyzing forms in {app_name}: {str(e)}")

    def _post_process(self):
        """Post-process the results to connect related information."""
        # Link views to URLs
        for url in self.results['urls']:
            for view in self.results['views']:
                if url.get('view_name') == view.get('name'):
                    url['view'] = view

        # Link serializers to views
        for view in self.results['views']:
            for serializer in self.results['serializers']:
                if serializer.get('name') == view.get('serializer_class'):
                    if 'serializers' not in view:
                        view['serializers'] = []
                    view['serializers'].append(serializer)

        # Link models to serializers
        for serializer in self.results['serializers']:
            for model in self.results['models']:
                if model.get('name') == serializer.get('model'):
                    serializer['model_detail'] = model

        # Generate comprehensive API endpoints info
        self._generate_api_endpoints()

        # Analyze authentication mechanisms
        self._analyze_authentication()

    def _generate_api_endpoints(self):
        """Generate comprehensive API endpoints information."""
        api_endpoints = []

        # Combine URL patterns and viewsets to create comprehensive API endpoints
        for url in self.results['urls']:
            endpoint = {
                'path': url.get('path', ''),
                'name': url.get('name', ''),
                'methods': []
            }

            # If HTTP methods are already defined (from runtime analysis)
            if 'http_methods' in url:
                for method in url['http_methods']:
                    endpoint['methods'].append({
                        'http_method': method,
                        'view_method': method.lower()
                    })
            # If this URL is linked to a view
            elif 'view' in url:
                view = url['view']
                if 'class_methods' in view:
                    # For class-based views, map HTTP methods
                    http_methods = {
                        'get': 'GET',
                        'post': 'POST',
                        'put': 'PUT',
                        'patch': 'PATCH',
                        'delete': 'DELETE',
                    }

                    for method in view['class_methods']:
                        if method.lower() in http_methods:
                            endpoint['methods'].append({
                                'http_method': http_methods[method.lower()],
                                'view_method': method
                            })
                else:
                    # For function-based views, assume it handles GET by default
                    endpoint['methods'].append({
                        'http_method': 'GET',
                        'view_method': view.get('name', '')
                    })

                # Link serializers
                if 'serializers' in view:
                    endpoint['serializers'] = view['serializers']

            api_endpoints.append(endpoint)

        # Also include endpoints from DRF routers
        for endpoint in self.results['api_endpoints']:
            if 'is_viewset' in endpoint and endpoint['is_viewset']:
                # For viewsets, find the corresponding view
                for view in self.results['views']:
                    if view.get('name') == endpoint.get('viewset'):
                        # Create standard REST endpoints
                        base_path = endpoint.get('url_prefix', '')

                        # List/Create endpoint
                        list_endpoint = {
                            'path': f"/{base_path}/",
                            'name': f"{view.get('name')}_list",
                            'methods': [
                                {'http_method': 'GET', 'view_method': 'list'},
                                {'http_method': 'POST', 'view_method': 'create'}
                            ],
                        }

                        # Detail endpoint
                        detail_endpoint = {
                            'path': f"/{base_path}/{{id}}/",
                            'name': f"{view.get('name')}_detail",
                            'methods': [
                                {'http_method': 'GET', 'view_method': 'retrieve'},
                                {'http_method': 'PUT', 'view_method': 'update'},
                                {'http_method': 'PATCH', 'view_method': 'partial_update'},
                                {'http_method': 'DELETE', 'view_method': 'destroy'}
                            ],
                        }

                        # Add serializers
                        if 'serializers' in view:
                            list_endpoint['serializers'] = view['serializers']
                            detail_endpoint['serializers'] = view['serializers']

                        api_endpoints.extend([list_endpoint, detail_endpoint])

        # Replace the existing api_endpoints with the comprehensive list
        self.results['api_endpoints'] = api_endpoints

    def _analyze_authentication(self):
        """Analyze authentication mechanisms used in the project."""
        auth_info = {
            'authentication_classes': [],
            'permission_classes': [],
            'token_auth': False,
            'jwt_auth': False,
            'oauth': False,
            'session_auth': False
        }

        # Look for auth related imports and classes in views
        auth_keywords = [
            'TokenAuthentication', 'JWTAuthentication', 'SessionAuthentication',
            'BasicAuthentication', 'OAuth2Authentication', 'IsAuthenticated',
            'IsAdminUser', 'AllowAny', 'IsAuthenticatedOrReadOnly'
        ]

        for view in self.results['views']:
            # Check imports if available from static analysis
            if 'imports' in view:
                for imp in view['imports']:
                    if any(keyword in imp for keyword in auth_keywords):
                        parts = imp.split('.')
                        auth_class = parts[-1]

                        if 'Authentication' in auth_class:
                            auth_info['authentication_classes'].append(auth_class)

                            if 'Token' in auth_class:
                                auth_info['token_auth'] = True
                            if 'JWT' in auth_class:
                                auth_info['jwt_auth'] = True
                            if 'Session' in auth_class:
                                auth_info['session_auth'] = True
                            if 'OAuth' in auth_class:
                                auth_info['oauth'] = True

                        if any(perm in auth_class for perm in ['IsAuthenticated', 'IsAdminUser', 'AllowAny']):
                            auth_info['permission_classes'].append(auth_class)

            # Check permission classes from runtime analysis
            if 'permission_classes' in view:
                for perm_class in view['permission_classes']:
                    auth_info['permission_classes'].append(perm_class)

                    # Detect auth type from permission classes
                    if 'IsAuthenticated' in perm_class:
                        # Assume some kind of authentication is required
                        if not any([auth_info['token_auth'], auth_info['jwt_auth'], auth_info['session_auth'], auth_info['oauth']]):
                            auth_info['session_auth'] = True

        # Check Django settings for AUTH_USER_MODEL if using runtime analysis
        if self.django_initialized:
            try:
                from django.conf import settings

                # Check for JWT settings
                if hasattr(settings, 'REST_FRAMEWORK'):
                    auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
                    for auth_class in auth_classes:
                        if isinstance(auth_class, str):
                            auth_info['authentication_classes'].append(auth_class.split('.')[-1])

                            if 'JWT' in auth_class:
                                auth_info['jwt_auth'] = True
                            elif 'Token' in auth_class:
                                auth_info['token_auth'] = True
                            elif 'Session' in auth_class:
                                auth_info['session_auth'] = True
                            elif 'OAuth' in auth_class:
                                auth_info['oauth'] = True

                    # Check for permission classes
                    perm_classes = settings.REST_FRAMEWORK.get('DEFAULT_PERMISSION_CLASSES', [])
                    for perm_class in perm_classes:
                        if isinstance(perm_class, str):
                            auth_info['permission_classes'].append(perm_class.split('.')[-1])

                # Check for installed apps related to auth
                if hasattr(settings, 'INSTALLED_APPS'):
                    if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
                        auth_info['token_auth'] = True
                    if any('oauth' in app.lower() for app in settings.INSTALLED_APPS):
                        auth_info['oauth'] = True
                    if any('jwt' in app.lower() for app in settings.INSTALLED_APPS):
                        auth_info['jwt_auth'] = True
            except Exception as e:
                print(f"Error analyzing authentication settings: {str(e)}")

        # Remove duplicates
        auth_info['authentication_classes'] = list(set(auth_info['authentication_classes']))
        auth_info['permission_classes'] = list(set(auth_info['permission_classes']))

        self.results['auth'] = auth_info

    def generate_report(self):
        """Generate the final report in the specified format."""
        if self.output_format == 'json':
            return self._generate_json_report()
        elif self.output_format == 'markdown':
            return self._generate_markdown_report()

    def _generate_json_report(self):
        """Generate a JSON report."""
        return json.dumps(self.results, indent=2)

    def _generate_markdown_report(self):
        """Generate a Markdown report."""
        markdown = "# Django Backend Analysis Report\n\n"
        markdown += f"_Generated on {self._get_current_date()}_\n\n"

        # Add Table of Contents
        markdown += "## Table of Contents\n\n"
        markdown += "1. [Models](#models)\n"
        markdown += "2. [API Endpoints](#api-endpoints)\n"
        markdown += "3. [Views](#views)\n"
        markdown += "4. [Serializers](#serializers)\n"
        markdown += "5. [Forms](#forms)\n"
        markdown += "6. [Authentication](#authentication)\n\n"

        # Models Section
        markdown += "## Models\n\n"
        for model in self.results['models']:
            markdown += f"### {model['name']}\n\n"
            markdown += f"**App:** {model['app_name']}\n\n"

            if model.get('docstring'):
                markdown += f"**Description:** {model['docstring']}\n\n"

            if model['fields']:
                markdown += "**Fields:**\n\n"
                markdown += "| Name | Type | Required | Default | Choices | Help Text |\n"
                markdown += "|------|------|----------|---------|---------|----------|\n"

                for field in model['fields']:
                    required = "Yes" if field.get('required', False) else "No"
                    default = field.get('default', '')
                    choices = ', '.join([str(c) for c in field.get('choices', [])])
                    help_text = field.get('help_text', '')

                    markdown += f"| {field['name']} | {field['type']} | {required} | {default} | {choices} | {help_text} |\n"

                markdown += "\n"

            if model.get('relationships'):
                markdown += "**Relationships:**\n\n"
                markdown += "| Relationship Type | Related Model | Related Name | Through |\n"
                markdown += "|-------------------|--------------|--------------|--------|\n"

                for rel in model['relationships']:
                    rel_type = rel.get('type', '')
                    related = rel.get('related_model', '')
                    related_name = rel.get('related_name', '')
                    through = rel.get('through', '')

                    markdown += f"| {rel_type} | {related} | {related_name} | {through} |\n"

                markdown += "\n"

            if model.get('methods'):
                markdown += "**Methods:**\n\n"
                for method in model['methods']:
                    markdown += f"- `{method['name']}({', '.join(method.get('args', []))})`: {method.get('docstring', '')}\n"

                markdown += "\n"

        # API Endpoints Section
        markdown += "## API Endpoints\n\n"
        markdown += "| Path | HTTP Methods | View/Viewset | Serializer | Model |\n"
        markdown += "|------|-------------|-------------|------------|-------|\n"

        for endpoint in self.results['api_endpoints']:
            path = endpoint.get('path', '')
            methods = ', '.join([m['http_method'] for m in endpoint.get('methods', [])])
            view = endpoint.get('name', '')

            # Get serializer info
            serializer = ""
            model = ""
            if 'serializers' in endpoint:
                for s in endpoint['serializers']:
                    serializer += f"{s['name']}, "
                    if 'model_detail' in s:
                        model += f"{s['model_detail']['name']}, "

            # Remove trailing commas
            serializer = serializer.rstrip(', ')
            model = model.rstrip(', ')

            markdown += f"| {path} | {methods} | {view} | {serializer} | {model} |\n"

        markdown += "\n"

        # Views Section
        markdown += "## Views\n\n"
        for view in self.results['views']:
            markdown += f"### {view['name']}\n\n"
            markdown += f"**Type:** {view.get('type', 'Function-based')}\n"
            markdown += f"**App:** {view['app_name']}\n\n"

            if view.get('docstring'):
                markdown += f"**Description:** {view['docstring']}\n\n"

            if view.get('permission_classes'):
                markdown += "**Permission Classes:**\n\n"
                for perm in view['permission_classes']:
                    markdown += f"- {perm}\n"
                markdown += "\n"

            if view.get('throttle_classes'):
                markdown += "**Throttle Classes:**\n\n"
                for throttle in view['throttle_classes']:
                    markdown += f"- {throttle}\n"
                markdown += "\n"

            if view.get('class_methods'):
                markdown += "**Methods:**\n\n"
                for method in view['class_methods']:
                    markdown += f"- `{method}`\n"
                markdown += "\n"

            if view.get('get_permissions_impl'):
                markdown += "**Custom get_permissions Method:**\n\n"
                markdown += "```python\n" + view['get_permissions_impl'] + "\n```\n\n"

            if view.get('get_throttles_impl'):
                markdown += "**Custom get_throttles Method:**\n\n"
                markdown += "```python\n" + view['get_throttles_impl'] + "\n```\n\n"

            if 'serializers' in view:
                markdown += "**Serializers:**\n\n"
                for serializer in view['serializers']:
                    markdown += f"- {serializer['name']}\n"
                markdown += "\n"

        # Serializers Section
        markdown += "## Serializers\n\n"
        for serializer in self.results['serializers']:
            markdown += f"### {serializer['name']}\n\n"
            markdown += f"**App:** {serializer['app_name']}\n"

            if serializer.get('model'):
                markdown += f"**Model:** {serializer['model']}\n\n"

            if serializer.get('fields'):
                markdown += "**Fields:**\n\n"

                if isinstance(serializer['fields'][0], dict):
                    # Detailed field information
                    markdown += "| Name | Type | Required | Read Only | Write Only | Default | Choices | Validators |\n"
                    markdown += "|------|------|----------|-----------|------------|---------|---------|------------|\n"

                    for field in serializer['fields']:
                        name = field.get('name', '')
                        field_type = field.get('type', '')
                        required = "Yes" if field.get('required') else "No"
                        read_only = "Yes" if field.get('read_only') else "No"
                        write_only = "Yes" if field.get('write_only') else "No"
                        default = field.get('default', '')
                        choices = str(field.get('choices', ''))
                        validators = ', '.join(field.get('validators', []))

                        markdown += f"| {name} | {field_type} | {required} | {read_only} | {write_only} | {default} | {choices} | {validators} |\n"
                else:
                    # Simple field list
                    for field in serializer['fields']:
                        markdown += f"- {field}\n"

                markdown += "\n"

        # Forms Section
        if self.results['forms']:
            markdown += "## Forms\n\n"
            for form in self.results['forms']:
                markdown += f"### {form['name']}\n\n"
                markdown += f"**App:** {form['app_name']}\n\n"

                if form.get('fields'):
                    markdown += "**Fields:**\n\n"
                    for field in form['fields']:
                        markdown += f"- {field}\n"
                    markdown += "\n"

        # Authentication Section
        markdown += "## Authentication\n\n"
        auth = self.results['auth']

        markdown += "**Authentication Classes:**\n\n"
        for auth_class in auth['authentication_classes']:
            markdown += f"- {auth_class}\n"
        markdown += "\n"

        markdown += "**Permission Classes:**\n\n"
        for perm_class in auth['permission_classes']:
            markdown += f"- {perm_class}\n"
        markdown += "\n"

        markdown += "**Authentication Types:**\n\n"
        if auth['token_auth']:
            markdown += "- Token Authentication\n"
        if auth['jwt_auth']:
            markdown += "- JWT Authentication\n"
        if auth['session_auth']:
            markdown += "- Session Authentication\n"
        if auth['oauth']:
            markdown += "- OAuth Authentication\n"

        return markdown

    def _get_current_date(self):
        """Get the current date and time in a formatted string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_report(self, output_file=None):
        """Save the report to a file."""
        if not output_file:
            output_file = f"django_backend_report.{self.output_format}"

        report = self.generate_report()

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"\nReport saved to {output_file}")
        return output_file


class ModelVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Django models."""

    def __init__(self, app_name):
        self.app_name = app_name
        self.models = []
        self.current_model = None

    def visit_ClassDef(self, node):
        """Visit classes to find models."""
        # Check if this class inherits from models.Model
        is_model = False
        for base in node.bases:
            if isinstance(base, ast.Attribute) and base.attr == 'Model':
                is_model = True
            elif isinstance(base, ast.Name) and base.id == 'Model':
                is_model = True

        if is_model:
            self.current_model = {
                'name': node.name,
                'app_name': self.app_name,
                'fields': [],
                'relationships': [],
                'methods': [],
            }

            # Extract docstring if available
            if ast.get_docstring(node):
                self.current_model['docstring'] = ast.get_docstring(node)

            # Visit all class body nodes
            for item in node.body:
                self.visit(item)

            self.models.append(self.current_model)
            self.current_model = None
        else:
            # This might be a model form or other Django class
            self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit assignments to find model fields."""
        if not self.current_model:
            return

        # Only process assignments that might be model fields
        for target in node.targets:
            if isinstance(target, ast.Name):
                field_name = target.id

                # Skip common non-field attributes
                if field_name in ['Meta', 'objects', 'DoesNotExist', 'MultipleObjectsReturned']:
                    continue

                # Try to detect if this is a field
                if isinstance(node.value, ast.Call):
                    field_info = self._extract_field_info(field_name, node.value)
                    if field_info:
                        if field_info.get('is_relationship'):
                            self.current_model['relationships'].append(field_info)
                        else:
                            self.current_model['fields'].append(field_info)

    def visit_FunctionDef(self, node):
        """Visit function definitions to find model methods."""
        if not self.current_model:
            return

        # Skip private methods and common Django methods
        if node.name.startswith('_') and node.name not in ['__str__', '__repr__']:
            return

        method_info = {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args if arg.arg != 'self'],
        }

        # Extract docstring if available
        if ast.get_docstring(node):
            method_info['docstring'] = ast.get_docstring(node)

        self.current_model['methods'].append(method_info)

    def _extract_field_info(self, name, node):
        """Extract field information from an assignment node."""
        if not hasattr(node, 'func'):
            return None

        # Get field type
        field_type = None
        if isinstance(node.func, ast.Name):
            field_type = node.func.id
        elif isinstance(node.func, ast.Attribute):
            field_type = node.func.attr

        # If we couldn't determine the field type, skip
        if not field_type:
            return None

        # Check if this is a relationship field
        relationship_fields = [
            'ForeignKey', 'OneToOneField', 'ManyToManyField'
        ]

        is_relationship = field_type in relationship_fields

        field_info = {
            'name': name,
            'type': field_type
        }

        if is_relationship:
            field_info['is_relationship'] = True
            field_info['type'] = field_type

            # Get related model
            if node.args:
                related_model = None
                if isinstance(node.args[0], ast.Str):
                    related_model = node.args[0].s
                elif isinstance(node.args[0], ast.Name):
                    related_model = node.args[0].id

                if related_model:
                    field_info['related_model'] = related_model

            # Extract relationship options from keywords
            for keyword in node.keywords:
                if keyword.arg == 'related_name':
                    if isinstance(keyword.value, ast.Str):
                        field_info['related_name'] = keyword.value.s
                elif keyword.arg == 'through':
                    if isinstance(keyword.value, ast.Str):
                        field_info['through'] = keyword.value.s
                    elif isinstance(keyword.value, ast.Name):
                        field_info['through'] = keyword.value.id
        else:
            # Extract field options from keywords
            field_info['required'] = True  # Default to required
            for keyword in node.keywords:
                if keyword.arg == 'null' and isinstance(keyword.value, ast.NameConstant):
                    field_info['required'] = not keyword.value.value
                elif keyword.arg == 'blank' and isinstance(keyword.value, ast.NameConstant):
                    if keyword.value.value:
                        field_info['required'] = False
                elif keyword.arg == 'default':
                    if isinstance(keyword.value, ast.Str):
                        field_info['default'] = keyword.value.s
                    elif isinstance(keyword.value, ast.Num):
                        field_info['default'] = keyword.value.n
                    elif isinstance(keyword.value, ast.NameConstant):
                        field_info['default'] = str(keyword.value.value)
                    elif isinstance(keyword.value, ast.Call):
                        if hasattr(keyword.value.func, 'id'):
                            field_info['default'] = f"{keyword.value.func.id}()"
                elif keyword.arg == 'choices':
                    field_info['choices'] = []

                    # Try to extract choices from various formats
                    if isinstance(keyword.value, ast.Name):
                        field_info['choices'].append(f"From variable: {keyword.value.id}")
                    elif isinstance(keyword.value, ast.List) or isinstance(keyword.value, ast.Tuple):
                        for elt in keyword.value.elts:
                            if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                                choice_value = None
                                choice_display = None

                                if isinstance(elt.elts[0], ast.Str):
                                    choice_value = elt.elts[0].s
                                elif isinstance(elt.elts[0], ast.Num):
                                    choice_value = str(elt.elts[0].n)

                                if isinstance(elt.elts[1], ast.Str):
                                    choice_display = elt.elts[1].s

                                if choice_value and choice_display:
                                    field_info['choices'].append(f"{choice_value}: {choice_display}")
                elif keyword.arg == 'help_text' and isinstance(keyword.value, ast.Str):
                    field_info['help_text'] = keyword.value.s

        return field_info


class ViewVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Django views."""

    def __init__(self, app_name, file_name):
        self.app_name = app_name
        self.file_name = file_name
        self.views = []
        self.imports = []
        self.current_view = None

    def visit_Import(self, node):
        """Visit import statements."""
        for name in node.names:
            self.imports.append(name.name)

    def visit_ImportFrom(self, node):
        """Visit from import statements."""
        module = node.module or ''
        for name in node.names:
            self.imports.append(f"{module}.{name.name}")

    def visit_ClassDef(self, node):
        """Visit class definitions to find views."""
        # Check if this is a view class
        view_base_classes = [
            'View', 'APIView', 'GenericAPIView', 'ViewSet', 'ModelViewSet', 
            'ReadOnlyModelViewSet', 'CreateView', 'ListView', 'DetailView',
            'UpdateView', 'DeleteView'
        ]

        is_view = False
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name and base_name in view_base_classes:
                is_view = True
                break

        if is_view:
            self.current_view = {
                'name': node.name,
                'app_name': self.app_name,
                'file': self.file_name,
                'type': 'Class-based',
                'imports': self.imports,
                'class_methods': [],
                'permission_classes': [],
                'throttle_classes': []
            }

            # Extract docstring if available
            if ast.get_docstring(node):
                self.current_view['docstring'] = ast.get_docstring(node)

            # Visit all class body nodes
            for item in node.body:
                # Extract methods
                if isinstance(item, ast.FunctionDef):
                    self.current_view['class_methods'].append(item.name)

                    # Check for custom permission or throttle methods
                    if item.name in ('get_permissions', 'get_throttles'):
                        # We don't have source in static analysis
                        self.current_view[f"{item.name}_custom"] = True

                # Look for attributes like serializer_class, permission_classes
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == 'serializer_class':
                                if isinstance(item.value, ast.Name):
                                    self.current_view['serializer_class'] = item.value.id
                            elif target.id == 'permission_classes':
                                if isinstance(item.value, ast.List) or isinstance(item.value, ast.Tuple):
                                    for el in item.value.elts:
                                        if isinstance(el, ast.Name):
                                            self.current_view['permission_classes'].append(el.id)
                                        elif isinstance(el, ast.Attribute):
                                            self.current_view['permission_classes'].append(el.attr)
                            elif target.id == 'throttle_classes':
                                if isinstance(item.value, ast.List) or isinstance(item.value, ast.Tuple):
                                    for el in item.value.elts:
                                        if isinstance(el, ast.Name):
                                            self.current_view['throttle_classes'].append(el.id)
                                        elif isinstance(el, ast.Attribute):
                                            self.current_view['throttle_classes'].append(el.attr)

            self.views.append(self.current_view)
            self.current_view = None
        else:
            # This might be a helper class
            self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions to find function-based views."""
        if self.current_view:  # We're inside a class
            return

        # Heuristic: if function has request parameter, likely a view
        is_view = False
        for arg in node.args.args:
            if arg.arg == 'request':
                is_view = True
                break

        if is_view:
            view_info = {
                'name': node.name,
                'app_name': self.app_name,
                'file': self.file_name,
                'type': 'Function-based',
                'imports': self.imports
            }

            # Extract docstring if available
            if ast.get_docstring(node):
                view_info['docstring'] = ast.get_docstring(node)

            self.views.append(view_info)


class URLVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Django URL patterns."""

    def __init__(self, app_name):
        self.app_name = app_name
        self.urls = []
        self.imports = []
        self.in_urlpatterns = False

    def visit_Import(self, node):
        """Visit import statements."""
        for name in node.names:
            self.imports.append(name.name)

    def visit_ImportFrom(self, node):
        """Visit from import statements."""
        module = node.module or ''
        for name in node.names:
            self.imports.append(f"{module}.{name.name}")

    def visit_Assign(self, node):
        """Visit assignments to find urlpatterns."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'urlpatterns':
                self.in_urlpatterns = True
                self.visit(node.value)
                self.in_urlpatterns = False

    def visit_Call(self, node):
        """Visit function calls within urlpatterns."""
        if not self.in_urlpatterns:
            return

        # Look for path() or url() functions
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in ['path', 'url', 're_path']:
            url_info = {
                'app_name': self.app_name
            }

            # Extract path pattern
            if node.args and isinstance(node.args[0], ast.Str):
                url_info['path'] = node.args[0].s

            # Extract view function or class
            if len(node.args) > 1:
                view_arg = node.args[1]

                # Direct reference to a view
                if isinstance(view_arg, ast.Name):
                    url_info['view_name'] = view_arg.id

                # as_view() call
                elif isinstance(view_arg, ast.Call) and isinstance(view_arg.func, ast.Attribute):
                    if view_arg.func.attr == 'as_view':
                        url_info['view_name'] = view_arg.func.value.id

                # include() call
                elif isinstance(view_arg, ast.Call) and isinstance(view_arg.func, ast.Name):
                    if view_arg.func.id == 'include':
                        url_info['include'] = True
                        if node.args[1].args and isinstance(node.args[1].args[0], ast.Str):
                            url_info['include_path'] = node.args[1].args[0].s

            # Extract URL name if available
            for keyword in node.keywords:
                if keyword.arg == 'name' and isinstance(keyword.value, ast.Str):
                    url_info['name'] = keyword.value.s

            self.urls.append(url_info)

        self.generic_visit(node)


class SerializerVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Django REST Framework serializers."""

    def __init__(self, app_name):
        self.app_name = app_name
        self.serializers = []
        self.current_serializer = None

    def visit_ClassDef(self, node):
        """Visit classes to find serializers."""
        # Check if this is a serializer class
        serializer_base_classes = [
            'Serializer', 'ModelSerializer', 'HyperlinkedModelSerializer',
            'ListSerializer', 'BaseSerializer'
        ]

        is_serializer = False
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name and base_name in serializer_base_classes:
                is_serializer = True
                break

        if is_serializer:
            self.current_serializer = {
                'name': node.name,
                'app_name': self.app_name,
                'fields': []
            }

            # Visit all class body nodes
            for item in node.body:
                self.visit(item)

            # If no fields were found explicitly, check for Meta class
            if not self.current_serializer['fields'] and 'meta_fields' in self.current_serializer:
                self.current_serializer['fields'] = self.current_serializer.pop('meta_fields')

            self.serializers.append(self.current_serializer)
            self.current_serializer = None
        else:
            # This might be a Meta inner class
            if node.name == 'Meta' and self.current_serializer:
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                # Extract model
                                if target.id == 'model':
                                    if isinstance(item.value, ast.Name):
                                        self.current_serializer['model'] = item.value.id

                                # Extract fields
                                elif target.id == 'fields':
                                    fields = []

                                    # '__all__'
                                    if isinstance(item.value, ast.Str) and item.value.s == '__all__':
                                        fields = ['__all__']

                                    # List or tuple of fields
                                    elif isinstance(item.value, (ast.List, ast.Tuple)):
                                        for elt in item.value.elts:
                                            if isinstance(elt, ast.Str):
                                                fields.append(elt.s)

                                    self.current_serializer['meta_fields'] = fields

    def visit_Assign(self, node):
        """Visit assignments to find serializer fields."""
        if not self.current_serializer:
            return

        # Only process assignments that might be serializer fields
        for target in node.targets:
            if isinstance(target, ast.Name):
                field_name = target.id

                # Skip Meta class
                if field_name == 'Meta':
                    continue

                # Try to detect if this is a field
                if isinstance(node.value, ast.Call):
                    field_type = None
                    if isinstance(node.value.func, ast.Name):
                        field_type = node.value.func.id
                    elif isinstance(node.value.func, ast.Attribute):
                        field_type = node.value.func.attr

                    if field_type and field_type.endswith('Field'):
                        field_info = {
                            'name': field_name,
                            'type': field_type
                        }

                        # Extract field options
                        for keyword in node.value.keywords:
                            if keyword.arg in ('required', 'read_only', 'write_only'):
                                try:
                                    if hasattr(ast, 'NameConstant'):  # Python < 3.8
                                        if isinstance(keyword.value, ast.NameConstant):
                                            field_info[keyword.arg] = keyword.value.value
                                    else:  # Python >= 3.8
                                        if isinstance(keyword.value, ast.Constant):
                                            field_info[keyword.arg] = keyword.value.value
                                except (ValueError, AttributeError):
                                    pass
                            elif keyword.arg == 'default':
                                try:
                                    if hasattr(ast, 'NameConstant'):  # Python < 3.8
                                        if isinstance(keyword.value, ast.NameConstant):
                                            field_info['default'] = keyword.value.value
                                        elif isinstance(keyword.value, ast.Str):
                                            field_info['default'] = keyword.value.s
                                        elif isinstance(keyword.value, ast.Num):
                                            field_info['default'] = keyword.value.n
                                    else:  # Python >= 3.8
                                        if isinstance(keyword.value, ast.Constant):
                                            field_info['default'] = keyword.value.value
                                except (ValueError, AttributeError):
                                    pass

                        self.current_serializer['fields'].append(field_info)


class FormVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Django forms."""

    def __init__(self, app_name):
        self.app_name = app_name
        self.forms = []
        self.current_form = None

    def visit_ClassDef(self, node):
        """Visit classes to find forms."""
        # Check if this is a form class
        form_base_classes = ['Form', 'ModelForm']

        is_form = False
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name and base_name in form_base_classes:
                is_form = True
                break

        if is_form:
            self.current_form = {
                'name': node.name,
                'app_name': self.app_name,
                'fields': []
            }

            # Visit all class body nodes
            for item in node.body:
                self.visit(item)

            # If no fields were found explicitly, check for Meta class
            if not self.current_form['fields'] and 'meta_fields' in self.current_form:
                self.current_form['fields'] = self.current_form.pop('meta_fields')

            self.forms.append(self.current_form)
            self.current_form = None
        else:
            # This might be a Meta inner class
            if node.name == 'Meta' and self.current_form:
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                # Extract model
                                if target.id == 'model':
                                    if isinstance(item.value, ast.Name):
                                        self.current_form['model'] = item.value.id

                                # Extract fields
                                elif target.id == 'fields':
                                    fields = []

                                    # '__all__'
                                    if isinstance(item.value, ast.Str) and item.value.s == '__all__':
                                        fields = ['__all__']

                                    # List or tuple of fields
                                    elif isinstance(item.value, (ast.List, ast.Tuple)):
                                        for elt in item.value.elts:
                                            if isinstance(elt, ast.Str):
                                                fields.append(elt.s)

                                    self.current_form['meta_fields'] = fields

    def visit_Assign(self, node):
        """Visit assignments to find form fields."""
        if not self.current_form:
            return

        # Only process assignments that might be form fields
        for target in node.targets:
            if isinstance(target, ast.Name):
                field_name = target.id

                # Skip Meta class
                if field_name == 'Meta':
                    continue

                # Try to detect if this is a field
                if isinstance(node.value, ast.Call):
                    field_type = None
                    if isinstance(node.value.func, ast.Name):
                        field_type = node.value.func.id
                    elif isinstance(node.value.func, ast.Attribute):
                        field_type = node.value.func.attr

                    if field_type and field_type.endswith('Field'):
                        self.current_form['fields'].append(f"{field_name} ({field_type})")


def main():
    """Main function to run the Django analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze a Django project and generate a comprehensive report.')
    parser.add_argument('project_path', nargs='?', help='Path to the Django project (required for static analysis)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--runtime', action='store_true', help='Use Django runtime introspection')
    parser.add_argument('--settings', help='Django settings module for runtime analysis')

    args = parser.parse_args()

    try:
        # Use runtime analysis if explicitly requested or if running within a Django project
        use_runtime = args.runtime or (not args.project_path and 'DJANGO_SETTINGS_MODULE' in os.environ)

        # Validate project path if not using runtime
        if not use_runtime and not args.project_path:
            parser.error("project_path is required when not using runtime analysis")

        analyzer = DjangoAnalyzer(
            project_path=args.project_path,
            output_format=args.format,
            use_runtime=use_runtime,
            settings_module=args.settings
        )

        analyzer.analyze()
        analyzer.save_report(args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())