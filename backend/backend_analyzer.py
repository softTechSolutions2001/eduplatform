#!/usr/bin/env python3

import os
import re
import ast
import json
import argparse
import sys
import importlib
import inspect
import contextlib
from pathlib import Path, PurePosixPath
import posixpath
from collections import defaultdict
from typing import Dict, List, Optional, Any, Set, Tuple
import logging
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

# Check if colorama is available
COLORAMA_LOADED = 'colorama' in sys.modules

# Helper function for JavaScript template literals in Python f-strings


def js_tpl(expr: str) -> str:
    """Returns ${expr} with safe escaping inside a Python f-string"""
    return f"${{{expr}}}"

# Django integration helpers


def discover_settings_module(backend_path='.'):
    """Attempt to discover Django settings module path"""
    # Try common locations and patterns
    settings_candidates = [
        # Direct settings.py file
        os.path.join(backend_path, 'settings.py'),

        # Project/settings.py pattern
        *[os.path.join(backend_path, d, 'settings.py')
          for d in os.listdir(backend_path)
          if os.path.isdir(os.path.join(backend_path, d)) and
          os.path.exists(os.path.join(backend_path, d, 'settings.py'))],

        # Project/config/settings.py pattern
        *[os.path.join(backend_path, d, 'config', 'settings.py')
          for d in os.listdir(backend_path)
          if os.path.isdir(os.path.join(backend_path, d)) and
          os.path.exists(os.path.join(backend_path, d, 'config', 'settings.py'))],

        # Project/project/settings.py pattern
        *[os.path.join(backend_path, d, d, 'settings.py')
          for d in os.listdir(backend_path)
          if os.path.isdir(os.path.join(backend_path, d)) and
          os.path.exists(os.path.join(backend_path, d, d, 'settings.py'))]
    ]

    # Try to find manage.py and extract the settings module
    manage_py_path = os.path.join(backend_path, 'manage.py')
    if os.path.exists(manage_py_path):
        try:
            with open(manage_py_path, 'r') as f:
                manage_content = f.read()
                settings_matches = re.findall(
                    r"os\.environ\.setdefault\(['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^'\"]+)['\"]", manage_content)
                if settings_matches:
                    return settings_matches[0]
        except Exception:
            pass

    # Filter to existing files
    settings_candidates = [p for p in settings_candidates if os.path.exists(p)]

    if not settings_candidates:
        return None

    # First candidate as default
    settings_path = settings_candidates[0]

    # Convert path to module notation
    module_path = os.path.relpath(settings_path, backend_path)
    module_path = module_path.replace(os.path.sep, '.').replace('.py', '')

    # If backend path is not in sys.path, prepare to add it in a context manager
    parent_dir = os.path.dirname(os.path.abspath(backend_path))
    backend_absolute = os.path.abspath(backend_path)

    return module_path, parent_dir, backend_absolute


@contextlib.contextmanager
def temp_sys_path(paths):
    """Context manager to temporarily modify sys.path"""
    original_sys_path = sys.path.copy()
    try:
        for path in paths:
            if path not in sys.path:
                sys.path.insert(0, path)
        yield
    finally:
        sys.path = original_sys_path


def setup_django_environment(backend_path='.'):
    """Set up Django environment if possible"""
    # Check if analyzer mode is enabled to prevent side effects
    analyzer_mode = os.environ.get('ANALYZER_MODE', '0') == '1'

    try:
        discovery_result = discover_settings_module(backend_path)
        if not discovery_result:
            return False, "Could not discover Django settings module"

        settings_module, parent_dir, backend_absolute = discovery_result

        # Set environment variable if not already set
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

        # Set analyzer mode to minimize side effects if requested
        if analyzer_mode:
            os.environ.setdefault('ANALYZER_MODE', '1')

        # Import Django and setup
        with temp_sys_path([parent_dir, backend_absolute]):
            import django
            # Try to import URL modules early to populate router registries
            try:
                # Find and import all urls.py files to populate router registries
                for root, dirs, files in os.walk(backend_absolute):
                    if 'urls.py' in files:
                        rel_path = os.path.relpath(root, backend_absolute)
                        if rel_path == '.':
                            module_path = 'urls'
                        else:
                            module_path = rel_path.replace(
                                os.path.sep, '.') + '.urls'

                        try:
                            importlib.import_module(module_path)
                        except ImportError:
                            # Silently continue if this module can't be imported directly
                            pass
            except Exception:
                # Failure to import URLs early is not critical
                pass

            # Now set up Django
            django.setup()
            return True, None
    except Exception as e:
        return False, f"Error setting up Django environment: {str(e)}"


def import_safely(module_path):
    """Safely import a module and return it or None"""
    try:
        return importlib.import_module(module_path)
    except (ImportError, ModuleNotFoundError):
        return None


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('backend_analyzer')

# AST compatibility helpers for Python 3.8+


def get_constant_value(node):
    """Extract value from ast.Constant (Python 3.8+) or legacy nodes"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.List):
        return [get_constant_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(get_constant_value(elt) for elt in node.elts)
    elif isinstance(node, ast.Dict):
        keys = [get_constant_value(k) for k in node.keys]
        values = [get_constant_value(v) for v in node.values]
        return dict(zip(keys, values))
    else:
        return str(type(node).__name__)


def is_model_subclass(node):
    """Check if a class is a subclass of models.Model or similar base classes"""
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == 'Model':
            return True
        elif isinstance(base, ast.Attribute):
            # Get full attribute chain
            attr_chain = []
            current = base
            while isinstance(current, ast.Attribute):
                attr_chain.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                attr_chain.insert(0, current.id)

            # Check if last part is 'Model'
            if attr_chain and attr_chain[-1] == 'Model':
                return True
            # Handle common model parent classes
            if base.attr in ['AbstractUser', 'AbstractBaseUser', 'Model']:
                return True
    return False


def is_serializer_subclass(node):
    """Check if a class is a subclass of a serializer"""
    for base in node.bases:
        if isinstance(base, ast.Name) and 'Serializer' in base.id:
            return True
        elif isinstance(base, ast.Attribute) and 'Serializer' in base.attr:
            return True
    return False


def get_import_module_name(node, default=None):
    """Extract module name from an import node"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        module_parts = []
        current = node
        while isinstance(current, ast.Attribute):
            module_parts.insert(0, current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            module_parts.insert(0, current.id)
        return '.'.join(module_parts)
    return default


class ModelField:
    """Represents a field in a Django model"""

    def __init__(self, name, field_type, options=None):
        self.name = name
        self.field_type = field_type
        self.options = options or {}

    def __str__(self):
        return f"{self.name}: {self.field_type}"

    def to_dict(self):
        return {
            "name": self.name,
            "field_type": self.field_type,
            "options": self.options
        }


class ModelInfo:
    """Information about a Django model"""

    def __init__(self, name, app_name, fields=None, relationships=None, meta=None):
        self.name = name
        self.app_name = app_name
        self.fields = fields or []
        self.relationships = relationships or []
        self.meta = meta or {}

    def __str__(self):
        return f"{self.app_name}.{self.name}"

    def to_dict(self):
        return {
            "name": self.name,
            "app_name": self.app_name,
            "fields": [f.to_dict() for f in self.fields],
            "relationships": self.relationships,
            "meta": self.meta
        }


class SerializerInfo:
    """Information about a Django REST Framework serializer"""

    def __init__(self, name, model=None, fields=None, meta=None, read_only_fields=None, write_only_fields=None, extra_kwargs=None):
        self.name = name
        self.model = model
        self.fields = fields or []
        self.meta = meta or {}
        self.read_only_fields = read_only_fields or []
        self.write_only_fields = write_only_fields or []
        self.extra_kwargs = extra_kwargs or {}

    def __str__(self):
        return f"{self.name} → {self.model}" if self.model else self.name

    def to_dict(self):
        return {
            "name": self.name,
            "model": self.model,
            "fields": self.fields,
            "meta": self.meta,
            "read_only_fields": self.read_only_fields,
            "write_only_fields": self.write_only_fields,
            "extra_kwargs": self.extra_kwargs
        }


class ViewInfo:
    """Information about a Django view or viewset"""

    def __init__(self, name, view_type, model=None, serializer=None, methods=None, permissions=None):
        self.name = name
        self.view_type = view_type  # APIView, ViewSet, ModelViewSet, etc.
        self.model = model
        self.serializer = serializer
        self.methods = methods or []
        self.permissions = permissions or []

    def __str__(self):
        return f"{self.name} ({self.view_type})"

    def to_dict(self):
        return {
            "name": self.name,
            "view_type": self.view_type,
            "model": self.model,
            "serializer": self.serializer,
            "methods": self.methods,
            "permissions": self.permissions
        }


class URLInfo:
    """Information about a Django URL pattern"""

    def __init__(self, pattern, view, name=None):
        self.pattern = pattern
        self.view = view
        self.name = name

    def __str__(self):
        return f"{self.pattern} → {self.view} ({self.name})" if self.name else f"{self.pattern} → {self.view}"

    def to_dict(self):
        return {
            "pattern": self.pattern,
            "view": self.view,
            "name": self.name
        }


class APIEndpoint:
    """Represents an API endpoint derived from URLs and views"""

    def __init__(self, path, method, view, name=None, model=None, serializer=None, permissions=None):
        self.path = path
        self.method = method
        self.view = view
        self.name = name
        self.model = model
        self.serializer = serializer
        self.permissions = permissions or []

    def __str__(self):
        return f"{self.method} {self.path} → {self.view}"

    def to_dict(self):
        return {
            "path": self.path,
            "method": self.method,
            "view": self.view,
            "name": self.name,
            "model": self.model,
            "serializer": self.serializer,
            "permissions": self.permissions
        }

    def get_endpoint_key(self):
        """Create a unique key for deduplication"""
        # Normalize the path to handle URL parameters consistently
        normalized_path = re.sub(r'<[^>]+>', '<param>', self.path)
        return (self.method, normalized_path)


class CompatibilityIssue:
    """Represents a compatibility issue between frontend and backend"""

    def __init__(self, issue_type, description, severity="warning", file=None, line=None):
        # naming, field_mismatch, serializer_model, etc.
        self.issue_type = issue_type
        self.description = description
        self.severity = severity  # info, warning, error
        self.file = file
        self.line = line

    def __str__(self):
        return f"[{self.severity.upper()}] {self.issue_type}: {self.description}"

    def to_dict(self):
        return {
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "file": self.file,
            "line": self.line
        }


class BackendAnalyzer:
    """Main analyzer class for Django backend"""

    def __init__(self, backend_path, verbose=False, exclude_apps=None, max_issues_to_show=100,
                 use_django_reflection=True, fail_on_error=False, output_openapi=False,
                 output_typescript=False, config_file=None):
        self.backend_path = os.path.abspath(backend_path)
        self.verbose = verbose
        self.exclude_apps = set(exclude_apps or [])
        self.max_issues_to_show = max_issues_to_show
        self.use_django_reflection = use_django_reflection
        self.fail_on_error = fail_on_error
        self.output_openapi = output_openapi
        self.output_typescript = output_typescript
        self.config_file = config_file

        # Setup logging
        self.logger = logger
        if verbose:
            self.logger.setLevel(logging.DEBUG)

        # Data structures to store analysis results
        self.apps = set()
        self.models = {}  # app_name.model_name -> ModelInfo
        self.serializers = {}  # app_name.serializer_name -> SerializerInfo
        self.views = {}  # app_name.view_name -> ViewInfo
        self.urls = {}  # app_name -> List[URLInfo]
        self.api_endpoints = []  # List of APIEndpoint objects
        self.issues = []  # List of CompatibilityIssue objects

        # Map to track relationships between different components
        self.model_to_serializers = defaultdict(list)
        self.serializer_to_views = defaultdict(list)
        self.view_to_urls = defaultdict(list)

        # Dictionary mapping viewset actions to HTTP methods
        self.viewset_action_map = {
            'list': 'GET',
            'retrieve': 'GET',
            'create': 'POST',
            'update': 'PUT',
            'partial_update': 'PATCH',
            'destroy': 'DELETE'
        }

        # Cache for file contents to avoid multiple reads
        self.file_cache = {}

        # Add a cache for authentication data
        self._auth_data_cache = None

        # Django integration state
        self.django_ready = False
        self.django_error = None

        # Try to set up Django if reflection is enabled
        if use_django_reflection:
            self.django_ready, self.django_error = setup_django_environment(
                self.backend_path)
            if self.django_ready:
                self.log(f"Django environment successfully initialized", "success")
                # Import Django-specific modules if available
                try:
                    import django
                    from django.apps import apps
                    from django.urls import get_resolver, URLPattern, URLResolver
                    self.django_apps = apps
                    self.django_urls = get_resolver()
                    self.django_version = django.get_version()

                    # Try to import DRF if available
                    try:
                        import rest_framework
                        self.drf_version = rest_framework.__version__

                        # Try to import router modules
                        try:
                            from rest_framework.routers import DefaultRouter, SimpleRouter
                            # Find all routers in the project
                            self.routers = self._discover_routers()
                        except ImportError:
                            self.routers = []
                    except ImportError:
                        self.drf_version = None
                        self.routers = []
                except ImportError as e:
                    self.log(
                        f"Error importing Django modules: {str(e)}", "error")
            else:
                self.log(
                    f"Django environment not initialized: {self.django_error}", "warning")
                self.log("Falling back to static file analysis", "info")

        # Read config file if provided
        self.config = {}
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.json'):
                        self.config = json.load(f)
                    elif config_file.endswith(('.toml', '.tml')):
                        import toml
                        self.config = toml.load(f)
                    elif config_file.endswith(('.yaml', '.yml')):
                        import yaml
                        self.config = yaml.safe_load(f)
                self.log(f"Loaded configuration from {config_file}", "info")
            except Exception as e:
                self.log(
                    f"Error loading config file {config_file}: {str(e)}", "error")

    def _discover_routers(self):
        """Discover DRF routers used in the project"""
        routers = []

        try:
            # Walk through modules in sys.modules to find routers
            from rest_framework.routers import BaseRouter

            for module_name, module in sys.modules.items():
                # Skip stdlib modules
                if not hasattr(module, '__file__') or not module.__file__:
                    continue

                # Skip modules not within our project path
                if not module.__file__.startswith(self.backend_path):
                    continue

                # Find router instances in the module
                for name, obj in inspect.getmembers(module):
                    if isinstance(obj, BaseRouter):
                        router_info = {
                            'router': obj,
                            'module': module_name,
                            'name': name
                        }
                        routers.append(router_info)
                        self.log(
                            f"Found router: {name} in {module_name}", "info")

            return routers
        except (ImportError, AttributeError):
            self.log("Could not discover DRF routers", "warning")
            return []

    def log(self, message, level="info"):
        """Log messages based on verbosity and level"""
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)

        if self.verbose:
            try:
                # Use colorama if available
                if COLORAMA_LOADED:
                    color = {
                        "info": Fore.BLUE,
                        "success": Fore.GREEN,
                        "warning": Fore.YELLOW,
                        "error": Fore.RED,
                        "debug": Fore.CYAN
                    }.get(level, Fore.WHITE)

                    print(
                        f"{color}[{level.upper()}] {message}{Style.RESET_ALL}")
                else:
                    print(f"[{level.upper()}] {message}")
            except Exception:
                # Fallback to plain output if something fails
                print(f"[{level.upper()}] {message}")

    def read_file(self, file_path):
        """Read file contents with caching"""
        if file_path in self.file_cache:
            return self.file_cache[file_path]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_cache[file_path] = content
                return content
        except Exception as e:
            self.log(f"Error reading file {file_path}: {str(e)}", "error")
            return ""

    def find_django_apps(self):
        """Find all Django apps in the backend directory"""
        self.log("Searching for Django apps...")

        # If Django is initialized, use apps registry
        if self.django_ready:
            try:
                # Use Django's app registry
                for app_config in self.django_apps.get_app_configs():
                    # Get the last part of the dotted path
                    app_name = app_config.name.split('.')[-1]
                    self.apps.add(app_name)
                    self.log(
                        f"Found Django app via registry: {app_name}", "success")

                # After finding all apps
                self.apps = {
                    app for app in self.apps if app not in self.exclude_apps}
                self.log(
                    f"Total Django apps found via registry: {len(self.apps)}")
                return self.apps
            except Exception as e:
                self.log(f"Error using Django app registry: {str(e)}", "error")
                self.log("Falling back to file system search", "warning")

        # Traditional file system search if Django reflection isn't available
        for root, dirs, files in os.walk(self.backend_path):
            # Look for apps.py which indicates a Django app
            if 'apps.py' in files:
                app_path = os.path.relpath(root, self.backend_path)
                app_name = os.path.basename(app_path)
                self.apps.add(app_name)
                self.log(f"Found Django app: {app_name}", "success")

        # After finding all apps
        self.apps = {app for app in self.apps if app not in self.exclude_apps}
        self.log(f"Total Django apps found: {len(self.apps)}")
        return self.apps

    def analyze_models(self):
        """Analyze models.py files in all Django apps"""
        self.log("Analyzing Django models...")

        # If Django is initialized, use model registry
        if self.django_ready:
            try:
                # Get all models from Django's registry
                for model in self.django_apps.get_models():
                    try:
                        app_name = model._meta.app_label
                        model_name = model.__name__

                        # Skip models in excluded apps
                        if app_name in self.exclude_apps:
                            continue

                        # Extract model information
                        model_info = self._extract_model_info_from_django(
                            model)
                        self.models[f"{app_name}.{model_name}"] = model_info
                        self.log(
                            f"  Found model via registry: {model_name} with {len(model_info.fields)} fields", "success")
                    except Exception as e:
                        self.log(
                            f"Error analyzing model {model.__name__}: {str(e)}", "error")

                self.log(
                    f"Total models found via registry: {len(self.models)}")
                return self.models
            except Exception as e:
                self.log(
                    f"Error using Django model registry: {str(e)}", "error")
                self.log("Falling back to file analysis", "warning")

        # Traditional file analysis if Django reflection isn't available
        for app_name in self.apps:
            models_path = os.path.join(
                self.backend_path, app_name, 'models.py')

            if not os.path.exists(models_path):
                models_dir = os.path.join(
                    self.backend_path, app_name, 'models')
                if os.path.isdir(models_dir) and os.path.exists(os.path.join(models_dir, '__init__.py')):
                    # Handle case where models are in a directory instead of a single file
                    self.log(f"Found models directory for app: {app_name}")
                    for model_file in os.listdir(models_dir):
                        if model_file.endswith('.py') and model_file != '__init__.py':
                            model_path = os.path.join(models_dir, model_file)
                            self._analyze_model_file(model_path, app_name)
                else:
                    self.log(
                        f"No models.py found for app: {app_name}", "warning")
                continue

            self._analyze_model_file(models_path, app_name)

        self.log(f"Total models found: {len(self.models)}")
        return self.models

    def _extract_model_info_from_django(self, model):
        """Extract model information using Django's model introspection APIs"""
        model_name = model.__name__
        app_name = model._meta.app_label
        fields = []
        relationships = []
        meta = {}

        # Get basic model metadata
        meta['verbose_name'] = str(model._meta.verbose_name)
        meta['verbose_name_plural'] = str(model._meta.verbose_name_plural)
        meta['db_table'] = model._meta.db_table
        meta['abstract'] = model._meta.abstract
        meta['app_label'] = model._meta.app_label
        meta['proxy'] = model._meta.proxy

        # Process all fields
        for field in model._meta.get_fields():
            try:
                field_name = field.name
                field_type = field.__class__.__name__
                options = {}

                # Extract common field options
                for option in ['null', 'blank', 'choices', 'default', 'help_text',
                               'primary_key', 'unique', 'verbose_name', 'editable']:
                    if hasattr(field, option):
                        value = getattr(field, option)
                        if value not in [None, False, ''] and not callable(value):
                            # Handle non-serializable objects
                            if option == 'default' and callable(value):
                                options[option] = 'callable'
                            else:
                                try:
                                    # Test JSON serialization
                                    json.dumps({option: value})
                                    options[option] = value
                                except (TypeError, OverflowError):
                                    options[option] = str(value)

                # Extract relationship information
                if hasattr(field, 'remote_field') and field.remote_field:
                    relation_type = field.__class__.__name__
                    if hasattr(field.remote_field, 'model') and field.remote_field.model:
                        related_model_name = field.remote_field.model.__name__
                        related_app_label = field.remote_field.model._meta.app_label
                        related_model = f"{related_app_label}.{related_model_name}"
                    else:
                        related_model = "Unknown"

                    if hasattr(field, 'remote_field') and hasattr(field.remote_field, 'related_name'):
                        related_name = field.remote_field.related_name
                    else:
                        related_name = None

                    relationships.append({
                        'field_name': field_name,
                        'relation_type': relation_type,
                        'related_model': related_model,
                        'related_name': related_name
                    })

                # Add the field to the list
                fields.append(ModelField(field_name, field_type, options))
            except Exception as e:
                self.log(
                    f"Error extracting field {field.name} from {model_name}: {str(e)}", "error")

        return ModelInfo(model_name, app_name, fields, relationships, meta)

    def _analyze_model_file(self, models_path, app_name):
        """Analyze a single model file"""
        self.log(f"Processing models in: {app_name}")

        try:
            file_content = self.read_file(models_path)

            # Parse the AST tree
            tree = ast.parse(file_content)

            # Find model classes (subclasses of models.Model)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a model class
                    if is_model_subclass(node):
                        model_name = node.name
                        model_info = self._extract_model_info(node, app_name)
                        self.models[f"{app_name}.{model_name}"] = model_info
                        self.log(
                            f"  Found model: {model_name} with {len(model_info.fields)} fields", "success")

        except Exception as e:
            self.log(
                f"Error analyzing models in {app_name}: {str(e)}", "error")

    def _extract_model_info(self, node, app_name):
        """Extract information from a model class node"""
        model_name = node.name
        fields = []
        relationships = []
        meta = {}

        for item in node.body:
            # Extract field definitions
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        field_type, options = self._extract_field_info(
                            item.value)

                        # Identify relationships
                        if field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                            try:
                                related_model = options.get('to', '')
                                if not related_model:
                                    # Try to extract from first arg
                                    if isinstance(item.value, ast.Call) and item.value.args:
                                        # For Python < 3.8
                                        if hasattr(item.value.args[0], 's'):
                                            related_model = item.value.args[0].s
                                        elif hasattr(item.value.args[0], 'id'):
                                            related_model = item.value.args[0].id
                                        else:
                                            related_model = get_constant_value(
                                                item.value.args[0])

                                relationships.append({
                                    'field_name': field_name,
                                    'relation_type': field_type,
                                    'related_model': related_model,
                                    'related_name': options.get('related_name', None)
                                })
                            except Exception as e:
                                self.log(
                                    f"Error parsing relationship {field_name}: {str(e)}", "error")

                        fields.append(ModelField(
                            field_name, field_type, options))

            # Extract Meta class information
            elif isinstance(item, ast.ClassDef) and item.name == 'Meta':
                for meta_item in item.body:
                    if isinstance(meta_item, ast.Assign) and isinstance(meta_item.targets[0], ast.Name):
                        meta_name = meta_item.targets[0].id
                        meta_value = self._extract_meta_value(meta_item.value)
                        meta[meta_name] = meta_value

        return ModelInfo(model_name, app_name, fields, relationships, meta)

    def _extract_field_info(self, node):
        """Extract field type and options from a field definition"""
        field_type = None
        options = {}

        if isinstance(node, ast.Call):
            # Get field type
            if isinstance(node.func, ast.Name):
                field_type = node.func.id
            elif isinstance(node.func, ast.Attribute):
                field_type = node.func.attr

            # Get field options
            for keyword in node.keywords:
                option_value = get_constant_value(keyword.value)
                options[keyword.arg] = option_value

            # For positional arguments (like ForeignKey('Model'))
            for i, arg in enumerate(node.args):
                if i == 0 and field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
                    # First arg for relationship fields is often the related model
                    try:
                        model_name = get_constant_value(arg)
                        if isinstance(model_name, str):
                            options['to'] = model_name
                        elif hasattr(arg, 'id'):  # For model references like User
                            options['to'] = arg.id
                    except:
                        pass

        return field_type or "Unknown", options

    def _extract_meta_value(self, node):
        """Extract meta value from a node using the get_constant_value helper"""
        return get_constant_value(node)

    def analyze_serializers(self):
        """Analyze serializers.py files in all Django apps"""
        self.log("Analyzing Django REST Framework serializers...")

        for app_name in self.apps:
            serializers_path = os.path.join(
                self.backend_path, app_name, 'serializers.py')

            if not os.path.exists(serializers_path):
                self.log(
                    f"No serializers.py found for app: {app_name}", "warning")
                continue

            self.log(f"Processing serializers in: {app_name}")

            try:
                file_content = self.read_file(serializers_path)

                # Parse the AST tree
                tree = ast.parse(file_content)

                # Find serializer classes (subclasses of serializers.*)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a serializer class
                        if is_serializer_subclass(node):
                            serializer_name = node.name
                            serializer_info = self._extract_serializer_info(
                                node, app_name)
                            self.serializers[f"{app_name}.{serializer_name}"] = serializer_info

                            # Update model to serializer mapping
                            if serializer_info.model:
                                self.model_to_serializers[serializer_info.model].append(
                                    f"{app_name}.{serializer_name}")

                            self.log(
                                f"  Found serializer: {serializer_name}", "success")

            except Exception as e:
                self.log(
                    f"Error analyzing serializers in {app_name}: {str(e)}", "error")

        self.log(f"Total serializers found: {len(self.serializers)}")
        return self.serializers

    def _extract_serializer_info(self, node, app_name):
        """Extract information from a serializer class node"""
        serializer_name = node.name
        fields = []
        meta = {}
        model = None
        read_only_fields = []
        write_only_fields = []
        extra_kwargs = {}

        for item in node.body:
            # Extract field definitions
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        fields.append(field_name)

            # Extract Meta class information
            elif isinstance(item, ast.ClassDef) and item.name == 'Meta':
                for meta_item in item.body:
                    if isinstance(meta_item, ast.Assign) and isinstance(meta_item.targets[0], ast.Name):
                        meta_name = meta_item.targets[0].id
                        meta_value = self._extract_meta_value(meta_item.value)
                        meta[meta_name] = meta_value

                        # Extract model information
                        if meta_name == 'model':
                            if isinstance(meta_item.value, ast.Name):
                                model = meta_item.value.id
                            elif isinstance(meta_item.value, ast.Attribute):
                                model = meta_item.value.attr

                        # Extract read-only fields
                        elif meta_name == 'read_only_fields':
                            if isinstance(meta_value, (list, tuple)):
                                read_only_fields = meta_value

                        # Extract extra_kwargs
                        elif meta_name == 'extra_kwargs':
                            if isinstance(meta_value, dict):
                                extra_kwargs = meta_value
                                # Check for write_only in extra_kwargs
                                for field_name, options in extra_kwargs.items():
                                    if isinstance(options, dict) and options.get('write_only', False):
                                        write_only_fields.append(field_name)

        return SerializerInfo(serializer_name, model, fields, meta, read_only_fields, write_only_fields, extra_kwargs)

    def analyze_views(self):
        """Analyze views.py files in all Django apps"""
        self.log("Analyzing Django views...")

        for app_name in self.apps:
            views_path = os.path.join(self.backend_path, app_name, 'views.py')

            if not os.path.exists(views_path):
                views_dir = os.path.join(self.backend_path, app_name, 'views')
                if os.path.isdir(views_dir) and os.path.exists(os.path.join(views_dir, '__init__.py')):
                    # Handle case where views are in a directory instead of a single file
                    self.log(f"Found views directory for app: {app_name}")
                    for view_file in os.listdir(views_dir):
                        if view_file.endswith('.py') and view_file != '__init__.py':
                            view_path = os.path.join(views_dir, view_file)
                            self._analyze_view_file(view_path, app_name)
                else:
                    self.log(
                        f"No views.py found for app: {app_name}", "warning")
                continue

            self._analyze_view_file(views_path, app_name)

        self.log(f"Total views found: {len(self.views)}")
        return self.views

    def _analyze_view_file(self, views_path, app_name):
        """Analyze a single view file"""
        self.log(f"Processing views in: {app_name}")

        try:
            file_content = self.read_file(views_path)

            # Parse the AST tree
            tree = ast.parse(file_content)

            # Find view classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    view_name = node.name
                    view_type, model, serializer = self._extract_view_type_and_model(
                        node)

                    if view_type:
                        methods, permissions = self._extract_view_methods_and_permissions(
                            node)
                        view_info = ViewInfo(
                            view_name, view_type, model, serializer, methods, permissions)
                        self.views[f"{app_name}.{view_name}"] = view_info

                        # Update serializer to view mapping
                        if serializer:
                            self.serializer_to_views[serializer].append(
                                f"{app_name}.{view_name}")

                        self.log(
                            f"  Found view: {view_name} ({view_type})", "success")

        except Exception as e:
            self.log(f"Error analyzing views in {app_name}: {str(e)}", "error")

    def _extract_view_type_and_model(self, node):
        """Extract view type and associated model from a view class node"""
        view_type = None
        model = None
        serializer = None

        # Check base classes to determine view type
        for base in node.bases:
            if isinstance(base, ast.Name):
                view_type = base.id
            elif isinstance(base, ast.Attribute):
                view_type = base.attr

        # Extract model and serializer from class variables
        for item in node.body:
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                var_name = item.targets[0].id

                if var_name == 'queryset' and isinstance(item.value, ast.Call):
                    # Extract model from queryset = Model.objects.all() or Model.objects.filter(...)
                    if isinstance(item.value.func, ast.Attribute) and item.value.func.attr in ['all', 'filter', 'exclude', 'get_queryset']:
                        if isinstance(item.value.func.value, ast.Attribute) and item.value.func.value.attr in ['objects', 'published', 'active']:
                            if isinstance(item.value.func.value.value, ast.Name):
                                model = item.value.func.value.value.id

                elif var_name == 'model' and isinstance(item.value, ast.Name):
                    # Extract model from model = ModelName
                    model = item.value.id

                elif var_name == 'serializer_class' and isinstance(item.value, ast.Name):
                    # Extract serializer from serializer_class = SerializerName
                    serializer = item.value.id

            # Check for get_serializer_class method
            elif isinstance(item, ast.FunctionDef) and item.name == 'get_serializer_class':
                # Try to extract serializer from return statement
                for sub_node in ast.walk(item):
                    if isinstance(sub_node, ast.Return) and isinstance(sub_node.value, ast.Name):
                        serializer = sub_node.value.id
                        break

        return view_type, model, serializer

    def _extract_view_methods_and_permissions(self, node):
        """Extract HTTP methods and permissions from a view class node"""
        methods = []
        permissions = []

        for item in node.body:
            # Extract methods defined in the class
            if isinstance(item, ast.FunctionDef):
                method_name = item.name.lower()
                if method_name in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    methods.append(method_name.upper())

            # Extract permissions from permission_classes
            if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name):
                var_name = item.targets[0].id

                if var_name == 'permission_classes':
                    if isinstance(item.value, ast.List):
                        for element in item.value.elts:
                            if isinstance(element, ast.Name):
                                permissions.append(element.id)
                            elif isinstance(element, ast.Attribute):
                                permissions.append(element.attr)

            # Extract permissions from get_permissions method
            elif isinstance(item, ast.FunctionDef) and item.name == 'get_permissions':
                for sub_node in ast.walk(item):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name) and sub_node.func.id.endswith('Permission'):
                            permissions.append(sub_node.func.id)
                        elif isinstance(sub_node.func, ast.Attribute) and sub_node.func.attr.endswith('Permission'):
                            permissions.append(sub_node.func.attr)

        # Check for @action decorators
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check for decorators
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'action':
                        # Extract HTTP methods from the decorator
                        methods_arg = None
                        for keyword in decorator.keywords:
                            if keyword.arg == 'methods':
                                methods_arg = keyword.value

                        if methods_arg and isinstance(methods_arg, ast.List):
                            for method_node in methods_arg.elts:
                                method_str = get_constant_value(method_node)
                                if isinstance(method_str, str):
                                    methods.append(method_str.upper())

        return methods, permissions

    def analyze_urls(self):
        """Analyze urls.py files in all Django apps and root URLs"""
        self.log("Analyzing Django URLs...")

        # If Django is initialized, use URLResolver
        if self.django_ready:
            try:
                from django.urls import URLPattern, URLResolver, get_resolver

                # Process the root URL resolver
                self.log("Processing URLs via Django URL resolver")
                url_patterns = self._process_url_patterns(
                    self.django_urls.url_patterns, prefix='')

                # Group by app
                for url_info in url_patterns:
                    app_name = self._extract_app_name_from_view(url_info.view)
                    if app_name not in self.urls:
                        self.urls[app_name] = []
                    self.urls[app_name].append(url_info)

                    # Update view to URL mapping
                    view_name = self._extract_view_name_from_reference(
                        url_info.view)
                    if view_name:
                        self.view_to_urls[view_name].append(url_info)

                # Process DRF routers if available
                if hasattr(self, 'routers') and self.routers:
                    self._process_drf_routers()

                total_urls = sum(len(urls) for urls in self.urls.values())
                self.log(
                    f"Total URL patterns found via resolver: {total_urls}")
                return self.urls
            except Exception as e:
                self.log(f"Error using Django URL resolver: {str(e)}", "error")
                self.log("Falling back to file analysis", "warning")

        # Traditional file analysis if Django reflection isn't available
        # First check for root URLs
        root_urls_path = self._find_root_urls_path()
        if root_urls_path:
            self.log(f"Processing root URLs: {root_urls_path}")
            self._process_urls_file(root_urls_path, "root")

        # Then check app-specific URLs
        for app_name in self.apps:
            urls_path = os.path.join(self.backend_path, app_name, 'urls.py')

            if not os.path.exists(urls_path):
                self.log(f"No urls.py found for app: {app_name}", "warning")
                continue

            self.log(f"Processing URLs in: {app_name}")
            self._process_urls_file(urls_path, app_name)

        # Count total URLs
        total_urls = sum(len(urls) for urls in self.urls.values())
        self.log(f"Total URL patterns found: {total_urls}")
        return self.urls

    def _process_url_patterns(self, url_patterns, prefix=''):
        """Process URL patterns using Django's URL resolver"""
        from django.urls import URLPattern, URLResolver

        results = []

        for pattern in url_patterns:
            if isinstance(pattern, URLPattern):
                # Extract pattern information
                pattern_str = prefix + \
                    self._format_pattern_for_url(pattern.pattern)
                view_str = self._get_view_string(pattern.callback)
                name = pattern.name

                url_info = URLInfo(pattern_str, view_str, name)
                results.append(url_info)
                self.log(
                    f"  Found URL pattern: {pattern_str} → {view_str}", "success")

            elif isinstance(pattern, URLResolver):
                # Process included URL patterns recursively
                new_prefix = prefix + \
                    self._format_pattern_for_url(pattern.pattern)
                nested_patterns = self._process_url_patterns(
                    pattern.url_patterns, new_prefix)
                results.extend(nested_patterns)

        return results

    def _format_pattern_for_url(self, pattern):
        """Format Django's URL pattern to string representation"""
        pattern_str = str(pattern)
        # Remove regex markers and non-capturing groups
        pattern_str = pattern_str.replace('^', '').replace('$', '')

        # Replace Django 2.0+ path converters with simpler placeholders
        pattern_str = re.sub(r'<(?:\w+:)?(\w+)>', r'<\1>', pattern_str)

        # If the pattern is empty, return /
        if not pattern_str:
            return '/'

        # Ensure pattern starts with /
        if not pattern_str.startswith('/'):
            pattern_str = '/' + pattern_str

        # Use posixpath to normalize the URL (avoid double slashes)
        return posixpath.normpath(pattern_str)

    def _get_view_string(self, view_func):
        """Get string representation of a view function or callable"""
        if hasattr(view_func, '__name__'):
            # Function-based view
            view_name = view_func.__name__
            if hasattr(view_func, '__module__'):
                return f"{view_func.__module__}.{view_name}"
            return view_name
        elif hasattr(view_func, '__class__'):
            # Class-based view
            view_class = view_func.__class__.__name__
            if hasattr(view_func, 'view_class'):
                # Likely a View.as_view() object
                view_class = view_func.view_class.__name__
            if hasattr(view_func, '__module__'):
                return f"{view_func.__module__}.{view_class}"
            return view_class
        else:
            # Fallback
            return str(view_func)

    def _extract_app_name_from_view(self, view_str):
        """Extract app name from a view string"""
        parts = view_str.split('.')
        if len(parts) > 1:
            # Try to find the app name in the module path
            for app in self.apps:
                if app in parts:
                    return app
            # Default to the first part of the module path
            return parts[0]
        return "unknown"

    def _process_drf_routers(self):
        """Process DRF routers to extract URL patterns"""
        if not hasattr(self, 'routers') or not self.routers:
            return

        self.log("Processing DRF routers")

        for router_info in self.routers:
            router = router_info['router']
            router_name = router_info['name']

            try:
                # Get registry entries (prefix, viewset, basename)
                for prefix, viewset, basename in router.registry:
                    self.log(
                        f"  Found router registration: {prefix} → {viewset.__name__}", "success")

                    # Create URLInfo for each action in the viewset
                    viewset_actions = self._get_viewset_actions(viewset)

                    for action, method in viewset_actions.items():
                        # Determine URL pattern based on action
                        if action == 'list':
                            pattern = f"/{prefix}/"
                        elif action == 'retrieve':
                            pattern = f"/{prefix}/<id>/"
                        elif action in ['update', 'partial_update', 'destroy']:
                            pattern = f"/{prefix}/<id>/"
                        elif action == 'create':
                            pattern = f"/{prefix}/"
                        else:
                            # Custom action - might be detail or list
                            detail = getattr(
                                getattr(viewset, action, None), 'detail', False)
                            pattern = f"/{prefix}/{'<id>/' if detail else ''}{action}/"

                        # Normalize the path
                        pattern = posixpath.normpath(pattern)

                        view_str = f"{viewset.__module__}.{viewset.__name__}.{action}"
                        name = f"{basename}-{action}" if basename else None

                        url_info = URLInfo(pattern, view_str, name)

                        # Associate with app
                        app_name = self._extract_app_name_from_view(view_str)
                        if app_name not in self.urls:
                            self.urls[app_name] = []
                        self.urls[app_name].append(url_info)

                        # Update view to URL mapping
                        self.view_to_urls[viewset.__name__].append(url_info)
            except Exception as e:
                self.log(
                    f"Error processing router {router_name}: {str(e)}", "error")

    def _get_viewset_actions(self, viewset):
        """Get actions for a viewset"""
        actions = {}

        # Standard actions
        for action, method in self.viewset_action_map.items():
            if hasattr(viewset, action):
                actions[action] = method

        # Custom actions using @action decorator
        for name, method in inspect.getmembers(viewset, predicate=inspect.isfunction):
            if hasattr(method, 'mapping'):
                # This is a custom action with defined HTTP methods
                for http_method, action_name in method.mapping.items():
                    # Use setdefault to avoid overwriting existing methods
                    actions.setdefault(name, http_method.upper())
            elif hasattr(method, 'detail'):
                # This is a custom action with default method (GET)
                actions.setdefault(name, 'GET')

        return actions

    def _find_root_urls_path(self):
        """Find the root urls.py file"""
        # Try to find the Django project's root directory
        # This is typically a directory with settings.py
        for root, dirs, files in os.walk(self.backend_path):
            if 'settings.py' in files:
                project_dir = os.path.basename(root)
                urls_path = os.path.join(root, 'urls.py')

                if os.path.exists(urls_path):
                    return urls_path

        return None

    def _process_urls_file(self, urls_path, app_name):
        """Process a urls.py file to extract URL patterns using AST"""
        try:
            file_content = self.read_file(urls_path)

            # Parse the AST tree
            tree = ast.parse(file_content)

            # Look for urlpatterns variable
            url_patterns = []
            includes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == 'urlpatterns':
                            if isinstance(node.value, ast.List):
                                for element in node.value.elts:
                                    url_info = self._extract_url_from_node(
                                        element)
                                    if url_info:
                                        url_patterns.append(url_info)

                                    # Check for include statements
                                    include_path = self._extract_include_from_node(
                                        element)
                                    if include_path:
                                        includes.append(include_path)

            # Process include statements
            for include_path in includes:
                self.log(f"  Found include: {include_path}", "info")
                self._process_included_urls(include_path, app_name)

            # Update the URL data structure
            if app_name not in self.urls:
                self.urls[app_name] = []

            self.urls[app_name].extend(url_patterns)

            # Update view to URL mapping
            for url_info in url_patterns:
                view_name = self._extract_view_name_from_reference(
                    url_info.view)
                if view_name:
                    self.view_to_urls[view_name].append(url_info)

        except Exception as e:
            self.log(f"Error analyzing URLs in {app_name}: {str(e)}", "error")

    def _extract_url_from_node(self, node):
        """Extract URL info from a path(), re_path(), or url() node"""
        if not isinstance(node, ast.Call):
            return None

        # Check if it's a path/re_path/url function
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name not in ['path', 're_path', 'url']:
            return None

        # Extract pattern, view, and name
        pattern = None
        view = None
        name = None

        # Get positional arguments
        if len(node.args) >= 2:
            # First arg is the pattern
            pattern = get_constant_value(node.args[0])

            # Second arg is the view
            view_arg = node.args[1]
            if isinstance(view_arg, ast.Name):
                view = view_arg.id
            elif isinstance(view_arg, ast.Attribute):
                view = get_import_module_name(view_arg)
            elif isinstance(view_arg, ast.Call):
                if isinstance(view_arg.func, ast.Attribute) and view_arg.func.attr == 'as_view':
                    view = get_import_module_name(view_arg.func.value)
                else:
                    view = get_import_module_name(view_arg.func)

        # Get keyword arguments
        for keyword in node.keywords:
            if keyword.arg == 'name':
                name = get_constant_value(keyword.value)

        if pattern and view:
            url_info = URLInfo(pattern, view, name)
            self.log(f"  Found URL pattern: {pattern} → {view}", "success")
            return url_info

        return None

    def _extract_include_from_node(self, node):
        """Extract include path from an include() call"""
        if not isinstance(node, ast.Call):
            return None

        # Check if it's an include function
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name != 'include':
            return None

        # Extract include path
        if node.args:
            include_path = get_constant_value(node.args[0])
            return include_path

        return None

    def _extract_view_name_from_reference(self, view_ref):
        """Extract the view name from a view reference in urls.py"""
        # Handle common patterns like 'views.ViewName.as_view()'
        if '.as_view' in view_ref:
            view_ref = view_ref.replace(
                '.as_view()', '').replace('.as_view', '')

        # Handle 'app_name.views.ViewName' pattern
        parts = view_ref.split('.')
        if len(parts) > 1:
            return parts[-1]

        return view_ref

    def identify_api_endpoints(self):
        """Identify API endpoints by combining URL, view, and serializer information"""
        self.log("Identifying API endpoints...")

        # Dictionary to store unique endpoints for deduplication
        unique_endpoints = {}

        for app_name, url_patterns in self.urls.items():
            for url_info in url_patterns:
                view_name = self._extract_view_name_from_reference(
                    url_info.view)

                # Try to find the matching view
                view_full_name = None
                for key in self.views.keys():
                    if key.endswith('.' + view_name):
                        view_full_name = key
                        break

                if view_full_name:
                    view_info = self.views[view_full_name]

                    # For ViewSet or ModelViewSet, create multiple endpoints
                    if 'ViewSet' in view_info.view_type:
                        for action, method in self.viewset_action_map.items():
                            # Construct appropriate path based on action
                            path = url_info.pattern
                            if action == 'list':
                                path = path.rstrip('/')
                            elif action == 'retrieve':
                                if not path.endswith('/'):
                                    path += '/'
                                path += '<id>/'
                            elif action in ['update', 'partial_update', 'destroy']:
                                if not path.endswith('/'):
                                    path += '/'
                                path += '<id>/'

                            # Normalize the path
                            path = posixpath.normpath(path)

                            endpoint = APIEndpoint(
                                path=path,
                                method=method,
                                view=view_info.name,
                                name=f"{url_info.name}_{action}" if url_info.name else None,
                                model=view_info.model,
                                serializer=view_info.serializer,
                                permissions=view_info.permissions
                            )

                            # Use endpoint key for deduplication
                            key = endpoint.get_endpoint_key()
                            if key not in unique_endpoints:
                                unique_endpoints[key] = endpoint
                                self.log(
                                    f"  Identified API endpoint: {method} {path}", "success")

                    # For regular views, use the methods defined in the view
                    else:
                        for method in (view_info.methods or ['GET']):
                            endpoint = APIEndpoint(
                                path=url_info.pattern,
                                method=method,
                                view=view_info.name,
                                name=url_info.name,
                                model=view_info.model,
                                serializer=view_info.serializer,
                                permissions=view_info.permissions
                            )

                            # Use endpoint key for deduplication
                            key = endpoint.get_endpoint_key()
                            if key not in unique_endpoints:
                                unique_endpoints[key] = endpoint
                                self.log(
                                    f"  Identified API endpoint: {method} {url_info.pattern}", "success")

                # If view not found but URL exists, add a placeholder
                # Only for function-based views or unknown views
                elif not view_full_name and not self._is_class_based_view(url_info.view):
                    endpoint = APIEndpoint(
                        path=url_info.pattern,
                        method="GET",  # Default method
                        view=url_info.view,
                        name=url_info.name
                    )

                    # Use endpoint key for deduplication
                    key = endpoint.get_endpoint_key()
                    if key not in unique_endpoints:
                        unique_endpoints[key] = endpoint
                        self.log(
                            f"  Identified API endpoint (function view): GET {url_info.pattern}", "info")

        # Set the deduplicated endpoints list
        self.api_endpoints = list(unique_endpoints.values())
        self.log(f"Total API endpoints identified: {len(self.api_endpoints)}")
        return self.api_endpoints

    def _is_class_based_view(self, view_ref):
        """Check if a view reference is likely to be a class-based view"""
        return '.as_view' in view_ref or any(view_ref.endswith(f".{v.name}") for v in self.views.values())

    def analyze_permissions(self):
        """Analyze permission classes"""
        self.log("Analyzing permission classes...")

        permission_files = []
        for app_name in self.apps:
            permissions_path = os.path.join(
                self.backend_path, app_name, 'permissions.py')

            if os.path.exists(permissions_path):
                permission_files.append((app_name, permissions_path))
                self.log(f"Found permissions.py in {app_name}")

        # If no specific permission files, look in views.py
        if not permission_files:
            self.log(
                "No dedicated permission files found, using permissions from views", "warning")

            # Collect unique permissions
            unique_permissions = set()
            for view_info in self.views.values():
                unique_permissions.update(view_info.permissions)

            self.log(
                f"Found {len(unique_permissions)} unique permission classes in views")

        return permission_files

    def detect_compatibility_issues(self):
        """Detect compatibility issues between models, serializers, views, and URLs"""
        self.log("Detecting compatibility issues...")

        # Check 1: Models referenced by serializers should exist
        for serializer_name, serializer_info in self.serializers.items():
            if serializer_info.model:
                # Build possible model references
                found = False
                for model_key in self.models.keys():
                    if model_key.endswith('.' + serializer_info.model) or serializer_info.model == model_key.split('.')[-1]:
                        found = True
                        break

                if not found:
                    self.issues.append(CompatibilityIssue(
                        issue_type="serializer_model_mismatch",
                        description=f"Serializer {serializer_name} references model {serializer_info.model} which was not found",
                        severity="error"
                    ))

        # Check 2: Serializers referenced by views should exist
        for view_name, view_info in self.views.items():
            if view_info.serializer:
                # Build possible serializer references
                found = False
                for serializer_key in self.serializers.keys():
                    if serializer_key.endswith('.' + view_info.serializer) or view_info.serializer == serializer_key.split('.')[-1]:
                        found = True
                        break

                if not found:
                    self.issues.append(CompatibilityIssue(
                        issue_type="view_serializer_mismatch",
                        description=f"View {view_name} references serializer {view_info.serializer} which was not found",
                        severity="error"
                    ))

        # Check 3: Views referenced by URLs should exist
        for app_name, url_list in self.urls.items():
            for url_info in url_list:
                view_name = self._extract_view_name_from_reference(
                    url_info.view)

                # Skip function views, this analysis focuses on class-based views
                if self._is_class_based_view(url_info.view):
                    # Build possible view references
                    found = False
                    for view_key in self.views.keys():
                        if view_key.endswith('.' + view_name) or view_name == view_key.split('.')[-1]:
                            found = True
                            break

                    if not found:
                        self.issues.append(CompatibilityIssue(
                            issue_type="url_view_mismatch",
                            description=f"URL {url_info.pattern} references view {view_name} which was not found",
                            severity="error"
                        ))

        # Check 4: Naming conventions
        for model_key, model_info in self.models.items():
            # Model names should be singular and PascalCase
            if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', model_info.name):
                self.issues.append(CompatibilityIssue(
                    issue_type="naming_convention",
                    description=f"Model {model_info.name} should use PascalCase (starting with uppercase, only letters, numbers, and underscores)",
                    severity="warning"
                ))

        for serializer_key, serializer_info in self.serializers.items():
            # Serializer names should end with 'Serializer'
            if not serializer_info.name.endswith('Serializer'):
                self.issues.append(CompatibilityIssue(
                    issue_type="naming_convention",
                    description=f"Serializer {serializer_info.name} should end with 'Serializer'",
                    severity="warning"
                ))

        # Check for model/serializer field mismatches
        for serializer_name, serializer_info in self.serializers.items():
            if serializer_info.model:
                # Find the corresponding model
                model_info = None
                for model_key, m_info in self.models.items():
                    if model_key.endswith('.' + serializer_info.model) or serializer_info.model == model_key.split('.')[-1]:
                        model_info = m_info
                        break

                if model_info:
                    # Check if all fields in serializer meta exist in model
                    model_field_names = set(
                        field.name for field in model_info.fields)
                    serializer_fields = serializer_info.meta.get('fields', [])

                    # Handle different types of fields
                    if serializer_fields == "__all__":
                        # No issues, using all fields
                        pass
                    elif isinstance(serializer_fields, list):
                        for field in serializer_fields:
                            if field not in model_field_names and field != 'id' and field != 'url':
                                self.issues.append(CompatibilityIssue(
                                    issue_type="field_mismatch",
                                    description=f"Serializer {serializer_info.name} references field '{field}' which does not exist in model {model_info.name}",
                                    severity="error"
                                ))

        # Check 5: Inconsistent permissions
        settings_data = self.analyze_settings()
        rest_framework = settings_data.get('REST_FRAMEWORK', {})
        global_permissions = []

        if isinstance(rest_framework, dict) and 'DEFAULT_PERMISSION_CLASSES' in rest_framework:
            global_permissions = rest_framework['DEFAULT_PERMISSION_CLASSES']

        # Group endpoints by base path
        endpoint_groups = defaultdict(list)
        for endpoint in self.api_endpoints:
            # Group by base path (remove parameters)
            base_path = re.sub(r'<[^>]+>', '<param>', endpoint.path)
            endpoint_groups[base_path].append(endpoint)

        for base_path, endpoints in endpoint_groups.items():
            # Check for inconsistent auth requirements within the same resource
            auth_required = [e for e in endpoints if e.permissions and any(
                'IsAuthenticated' in p for p in e.permissions)]
            not_auth_required = [e for e in endpoints if not e.permissions or not any(
                'IsAuthenticated' in p for p in e.permissions)]

            if auth_required and not_auth_required and not any('IsAuthenticated' in p for p in global_permissions):
                self.issues.append(CompatibilityIssue(
                    issue_type="inconsistent_auth",
                    description=f"Inconsistent authentication requirements for {base_path}",
                    severity="error"
                ))

        self.log(f"Found {len(self.issues)} compatibility issues")

        # Identify critical errors (any issue with severity="error")
        critical_errors = [
            issue for issue in self.issues if issue.severity == "error"]
        if critical_errors:
            self.log(f"Found {len(critical_errors)} critical errors", "error")

        return self.issues

    def analyze_settings(self):
        """Analyze Django settings.py for important configurations"""
        self.log("Analyzing Django settings...")

        settings_data = {}

        # Find settings.py
        settings_path = None
        for root, dirs, files in os.walk(self.backend_path):
            if 'settings.py' in files:
                settings_path = os.path.join(root, 'settings.py')
                break

        if not settings_path:
            self.log("settings.py not found", "error")
            return settings_data

        try:
            file_content = self.read_file(settings_path)

            # Parse the AST tree
            tree = ast.parse(file_content)

            # Extract important settings
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id

                    # Check for important settings
                    if var_name in [
                        'INSTALLED_APPS', 'REST_FRAMEWORK', 'DATABASES',
                        'MIDDLEWARE', 'CORS_ALLOWED_ORIGINS', 'CORS_ALLOW_ALL_ORIGINS',
                        'ALLOWED_HOSTS', 'DEBUG', 'STATIC_URL', 'MEDIA_URL',
                        'AUTHENTICATION_BACKENDS'
                    ]:
                        # Extract the value using our helper function
                        settings_data[var_name] = get_constant_value(
                            node.value)

            self.log(f"Found {len(settings_data)} important settings")

        except Exception as e:
            self.log(f"Error analyzing settings: {str(e)}", "error")

        return settings_data

    def analyze_authentication(self):
        """Analyze authentication mechanism in the project with caching"""
        if self._auth_data_cache is not None:
            return self._auth_data_cache

        self.log("Analyzing authentication mechanisms...")

        auth_data = {
            'mechanisms': set(),
            'user_model': None,
            'custom_auth': False
        }

        try:
            # Check settings for authentication backends
            settings_data = self.analyze_settings()
            backends = settings_data.get('AUTHENTICATION_BACKENDS', [])

            if backends and isinstance(backends, list):
                for backend in backends:
                    if isinstance(backend, str):
                        if 'django.contrib.auth' in backend:
                            auth_data['mechanisms'].add('django_auth')
                        if 'allauth' in backend:
                            auth_data['mechanisms'].add('allauth')
                        if 'knox' in backend:
                            auth_data['mechanisms'].add('knox')
                        if 'rest_framework.authentication' in backend:
                            auth_data['mechanisms'].add('drf_auth')
                        if 'dj_rest_auth' in backend:
                            auth_data['mechanisms'].add('dj_rest_auth')
                        if 'oauth2' in backend or 'oauth' in backend:
                            auth_data['mechanisms'].add('oauth')
                        if 'jwt' in backend.lower():
                            auth_data['mechanisms'].add('jwt')
                        if 'social' in backend:
                            auth_data['mechanisms'].add('social_auth')

            # Check if settings has REST_FRAMEWORK with authentication classes
            rest_framework = settings_data.get('REST_FRAMEWORK', {})
            if isinstance(rest_framework, dict) and 'DEFAULT_AUTHENTICATION_CLASSES' in rest_framework:
                auth_classes = rest_framework['DEFAULT_AUTHENTICATION_CLASSES']
                if isinstance(auth_classes, list):
                    for auth_class in auth_classes:
                        if isinstance(auth_class, str):
                            if 'TokenAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_token')
                            if 'SessionAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_session')
                            if 'BasicAuthentication' in auth_class:
                                auth_data['mechanisms'].add('drf_basic')
                            if 'JWTAuthentication' in auth_class or 'JWT' in auth_class:
                                auth_data['mechanisms'].add('jwt')
                            if 'KnoxAuthentication' in auth_class:
                                auth_data['mechanisms'].add('knox')

            # Check installed apps for authentication-related packages
            installed_apps = settings_data.get('INSTALLED_APPS', [])
            if isinstance(installed_apps, list):
                for app in installed_apps:
                    if isinstance(app, str):
                        if 'rest_framework.authtoken' in app:
                            auth_data['mechanisms'].add('drf_token')
                        if 'knox' in app:
                            auth_data['mechanisms'].add('knox')
                        if 'allauth' in app:
                            auth_data['mechanisms'].add('allauth')
                        if 'dj_rest_auth' in app:
                            auth_data['mechanisms'].add('dj_rest_auth')
                        if 'oauth2' in app or 'oauth' in app:
                            auth_data['mechanisms'].add('oauth')
                        if 'social' in app:
                            auth_data['mechanisms'].add('social_auth')
                        if 'jwt' in app.lower() or 'simplejwt' in app.lower() or 'rest_framework_simplejwt' in app:
                            auth_data['mechanisms'].add('jwt')

            # Find custom user models
            for app_name in self.apps:
                models_path = os.path.join(
                    self.backend_path, app_name, 'models.py')

                if os.path.exists(models_path):
                    try:
                        file_content = self.read_file(models_path)

                        # Look for AbstractUser or AbstractBaseUser
                        if 'AbstractUser' in file_content or 'AbstractBaseUser' in file_content:
                            # Parse the AST tree
                            tree = ast.parse(file_content)

                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    for base in node.bases:
                                        base_name = None
                                        if isinstance(base, ast.Name):
                                            base_name = base.id
                                        elif isinstance(base, ast.Attribute):
                                            base_name = base.attr

                                        if base_name in ['AbstractUser', 'AbstractBaseUser']:
                                            auth_data['user_model'] = f"{app_name}.{node.name}"
                                            auth_data['custom_auth'] = True
                                            break

                    except Exception as e:
                        self.log(
                            f"Error checking custom user model in {app_name}: {str(e)}", "error")

            # If no custom user model found, assume default
            if not auth_data['user_model']:
                auth_data['user_model'] = "django.contrib.auth.models.User"

            # Convert set to list for better serialization
            auth_data['mechanisms'] = list(auth_data['mechanisms'])

            self.log(
                f"Identified authentication mechanisms: {', '.join(auth_data['mechanisms'])}")
            if auth_data['custom_auth']:
                self.log(f"Found custom user model: {auth_data['user_model']}")

            # Cache the result only if successful
            self._auth_data_cache = auth_data
        except Exception as e:
            self.log(f"Error analyzing authentication: {str(e)}", "error")
            # Don't cache errors

        return auth_data

    def generate_er_diagram(self):
        """Generate entity-relationship diagram in text format"""
        self.log("Generating entity-relationship diagram...")

        er_lines = ["# Entity-Relationship Diagram", ""]
        app_models = {}

        # Group models by app
        for model_key, model_info in self.models.items():
            if model_info.app_name not in app_models:
                app_models[model_info.app_name] = []

            app_models[model_info.app_name].append(model_info)

        # Generate diagram for each app
        for app_name, models in app_models.items():
            er_lines.append(f"## App: {app_name}")
            er_lines.append("```")

            # Add each model
            for model_info in models:
                er_lines.append(f"[{model_info.name}]")

                # Add fields
                for field in model_info.fields:
                    field_str = f"  {field.name}: {field.field_type}"

                    # Add options if available
                    if field.options:
                        options_str = ", ".join(
                            f"{k}={v}" for k, v in field.options.items())
                        if options_str:
                            field_str += f" ({options_str})"

                    er_lines.append(field_str)

                er_lines.append("")

            # Add relationships
            er_lines.append("# Relationships")
            for model_info in models:
                for rel in model_info.relationships:
                    rel_type_symbol = {
                        'ForeignKey': '->',
                        'OneToOneField': '--',
                        'ManyToManyField': '<->'
                    }.get(rel['relation_type'], '->')

                    related_name = f" (as {rel['related_name']})" if rel['related_name'] else ""
                    er_lines.append(
                        f"[{model_info.name}] {rel_type_symbol} [{rel['related_model']}] : {rel['field_name']}{related_name}")

            er_lines.append("```")
            er_lines.append("")

        return "\n".join(er_lines)

    def analyze(self):
        """Run the full analysis"""
        self.log("Starting full backend analysis...")

        try:
            # Basic project analysis
            self.find_django_apps()
            self.analyze_models()
            self.analyze_serializers()
            self.analyze_views()
            self.analyze_urls()
            self.analyze_permissions()
            self.analyze_settings()

            # Identify API endpoints and analyze authentication
            self.identify_api_endpoints()
            auth_data = self.analyze_authentication()

            # Detect issues and generate ER diagram
            self.detect_compatibility_issues()
            er_diagram = self.generate_er_diagram()

            # Prepare final report data
            analysis_data = {
                'frontend_data': {
                    'api_endpoints': [endpoint.to_dict() for endpoint in self.api_endpoints],
                    'data_models': {model_name: model.to_dict() for model_name, model in self.models.items()},
                    'serializers': {serializer_name: serializer.to_dict() for serializer_name, serializer in self.serializers.items()},
                    'er_diagram': er_diagram,
                    'authentication': auth_data
                },
                'backend_compatibility': {
                    'issues': [issue.to_dict() for issue in self.issues],
                    'model_serializer_mapping': dict(self.model_to_serializers),
                    'serializer_view_mapping': dict(self.serializer_to_views),
                    'view_url_mapping': dict(self.view_to_urls)
                },
                'metadata': {
                    'script_version': '2.0',
                    'timestamp': self._get_current_date(),
                    'django_version': getattr(self, 'django_version', 'Unknown'),
                    'drf_version': getattr(self, 'drf_version', 'Unknown'),
                    'django_reflection_used': self.django_ready,
                    'excluded_apps': list(self.exclude_apps)
                }
            }

            self.log("Analysis completed successfully!", "success")
            return analysis_data

        except Exception as e:
            self.log(f"Error during analysis: {str(e)}", "error")
            import traceback
            self.log(traceback.format_exc(), "error")
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def generate_report(self, analysis_data, output_format='markdown'):
        """Generate a formatted report based on analysis data"""
        self.log(f"Generating {output_format} report...")

        if output_format == 'json':
            # Convert defaultdicts to regular dicts for JSON serialization
            for key, value in analysis_data.get('backend_compatibility', {}).items():
                if isinstance(value, defaultdict):
                    analysis_data['backend_compatibility'][key] = dict(value)

            # Add security matrix
            security_matrix = self.generate_security_matrix()
            analysis_data['security_matrix'] = security_matrix

            return json.dumps(analysis_data, indent=2)

        elif output_format == 'markdown':
            from datetime import datetime

            report_lines = [
                "# Django Backend Analysis Report",
                f"- Generated for: {os.path.basename(self.backend_path)}",
                f"- Date: {self._get_current_date()}",
                "",
                "## Table of Contents",
                "1. [Frontend Data](#frontend-data)",
                "   1. [API Endpoints](#api-endpoints)",
                "   2. [Data Models](#data-models)",
                "   3. [Serializers](#serializers)",
                "   4. [Entity-Relationship Diagram](#entity-relationship-diagram)",
                "   5. [Authentication](#authentication)",
                "   6. [Security Matrix](#security-matrix)",
                "2. [Backend Compatibility](#backend-compatibility)",
                "   1. [Issues](#issues)",
                "   2. [Component Mappings](#component-mappings)",
                "",
                "---",
                "",
                "<a id='frontend-data'></a>",
                "# FRONT END DATA",
                "",
                "<a id='api-endpoints'></a>",
                "## API Endpoints",
                "",
            ]

            # API Endpoints
            endpoints = analysis_data['frontend_data']['api_endpoints']
            if endpoints:
                report_lines.extend(self._format_api_endpoints(endpoints))
            else:
                report_lines.append("No API endpoints found.")

            report_lines.extend([
                "",
                "<a id='data-models'></a>",
                "## Data Models",
                ""
            ])

            # Data Models
            models = analysis_data['frontend_data']['data_models']
            if models:
                report_lines.extend(self._format_data_models(models))
            else:
                report_lines.append("No data models found.")

            report_lines.extend([
                "",
                "<a id='serializers'></a>",
                "## Serializers",
                ""
            ])

            # Serializers
            serializers = analysis_data['frontend_data']['serializers']
            if serializers:
                report_lines.extend(self._format_serializers(serializers))
            else:
                report_lines.append("No serializers found.")

            report_lines.extend([
                "",
                "<a id='entity-relationship-diagram'></a>",
                "## Entity-Relationship Diagram",
                ""
            ])

            # ER Diagram
            er_diagram = analysis_data['frontend_data']['er_diagram']
            if er_diagram:
                report_lines.append(er_diagram)
            else:
                report_lines.append(
                    "No entity-relationship diagram generated.")

            report_lines.extend([
                "",
                "<a id='authentication'></a>",
                "## Authentication",
                ""
            ])

            # Authentication
            auth_data = analysis_data['frontend_data']['authentication']
            if auth_data:
                report_lines.extend(self._format_authentication(auth_data))
            else:
                report_lines.append("No authentication information found.")

            # Security Matrix
            report_lines.extend([
                "",
                "<a id='security-matrix'></a>",
                "## Security Matrix",
                ""
            ])

            # Generate and add security matrix
            security_matrix = self.generate_security_matrix()
            if security_matrix:
                report_lines.extend(
                    self._format_security_matrix(security_matrix))
            else:
                report_lines.append("No security matrix generated.")

            report_lines.extend([
                "",
                "---",
                "",
                "<a id='backend-compatibility'></a>",
                "# BACKEND COMPATIBILITY",
                "",
                "<a id='issues'></a>",
                "## Issues",
                ""
            ])

            # Issues
            issues = analysis_data['backend_compatibility']['issues']
            if issues:
                report_lines.extend(self._format_issues(issues))
            else:
                report_lines.append("No compatibility issues found.")

            report_lines.extend([
                "",
                "<a id='component-mappings'></a>",
                "## Component Mappings",
                ""
            ])

            # Component Mappings
            mappings = {
                'Model to Serializers': analysis_data['backend_compatibility'].get('model_serializer_mapping', {}),
                'Serializer to Views': analysis_data['backend_compatibility'].get('serializer_view_mapping', {}),
                'View to URLs': analysis_data['backend_compatibility'].get('view_url_mapping', {})
            }

            report_lines.extend(self._format_component_mappings(mappings))

            # Add metadata at the end of the report
            report_lines.extend([
                "",
                "---",
                "",
                "## Metadata",
                "",
                f"- **Script Version**: 2.0",
                f"- **Analyzer Run Time**: {self._get_current_date()}",
            ])

            # Add Django and DRF versions if available
            if hasattr(self, 'django_version'):
                report_lines.append(
                    f"- **Django Version**: {self.django_version}")
            if hasattr(self, 'drf_version'):
                report_lines.append(f"- **DRF Version**: {self.drf_version}")

            # Add options used
            report_lines.extend([
                f"- **Used Django Reflection**: {self.django_ready}",
                f"- **Excluded Apps**: {', '.join(self.exclude_apps) if self.exclude_apps else 'None'}",
            ])

            return "\n".join(report_lines)

        else:
            self.log(f"Unsupported output format: {output_format}", "error")
            return "Unsupported output format. Please choose 'json' or 'markdown'."

    def _get_current_date(self):
        """Get current date in ISO format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _escape_markdown_table_cell(self, text):
        """Escape pipe characters in markdown table cells"""
        if not isinstance(text, str):
            text = str(text)
        return text.replace('|', '\\|').replace('\n', ' ')

    def _format_api_endpoints(self, endpoints):
        """Format API endpoints for markdown report"""
        lines = []

        # Group endpoints by base path
        endpoints_by_path = defaultdict(list)
        for endpoint in endpoints:
            base_path = endpoint['path'].split('<')[0].rstrip('/')
            endpoints_by_path[base_path].append(endpoint)

        for base_path, path_endpoints in endpoints_by_path.items():
            lines.append(
                f"### Path: `{self._escape_markdown_table_cell(base_path)}`")
            lines.append("")

            # Create table for endpoints
            table_headers = ["Method", "Full Path", "View",
                             "Serializer", "Model", "Permissions"]
            table_rows = []

            for endpoint in path_endpoints:
                row = [
                    self._escape_markdown_table_cell(endpoint['method']),
                    f"`{self._escape_markdown_table_cell(endpoint['path'])}`",
                    self._escape_markdown_table_cell(endpoint['view']),
                    self._escape_markdown_table_cell(
                        endpoint['serializer'] or '-'),
                    self._escape_markdown_table_cell(endpoint['model'] or '-'),
                    self._escape_markdown_table_cell(
                        ', '.join(endpoint['permissions']) if endpoint['permissions'] else '-')
                ]
                table_rows.append(row)

            # Add table
            lines.append("| " + " | ".join(table_headers) + " |")
            lines.append(
                "| " + " | ".join(["---" for _ in table_headers]) + " |")
            for row in table_rows:
                lines.append("| " + " | ".join(row) + " |")

            lines.append("")

        # Add general REST API conventions
        lines.extend([
            "### Common API Conventions",
            "",
            "- **GET /resource/**: List all resources",
            "- **POST /resource/**: Create a new resource",
            "- **GET /resource/{id}/**: Retrieve a specific resource",
            "- **PUT /resource/{id}/**: Update a specific resource (full update)",
            "- **PATCH /resource/{id}/**: Update a specific resource (partial update)",
            "- **DELETE /resource/{id}/**: Delete a specific resource",
            ""
        ])

        return lines

    def _format_data_models(self, models):
        """Format data models for markdown report"""
        lines = []

        # Group models by app
        models_by_app = defaultdict(list)
        for model_key, model_data in models.items():
            app_name = model_data['app_name']
            models_by_app[app_name].append(model_data)

        for app_name, app_models in models_by_app.items():
            lines.append(f"### App: {app_name}")
            lines.append("")

            for model in app_models:
                lines.append(f"#### {model['name']}")
                lines.append("")

                # Model metadata
                if model['meta']:
                    meta_items = []
                    for key, value in model['meta'].items():
                        meta_items.append(f"{key}: {value}")
                    if meta_items:
                        lines.append("**Meta Options:**")
                        for item in meta_items:
                            lines.append(f"- {item}")
                        lines.append("")

                # Fields table
                lines.append("**Fields:**")
                lines.append("")
                lines.append("| Field Name | Field Type | Options |")
                lines.append("| --- | --- | --- |")

                for field in model['fields']:
                    options_str = ", ".join(
                        f"{k}={v}" for k, v in field['options'].items()) if field['options'] else "-"
                    lines.append(
                        f"| {self._escape_markdown_table_cell(field['name'])} | {self._escape_markdown_table_cell(field['field_type'])} | {self._escape_markdown_table_cell(options_str)} |")

                lines.append("")

                # Relationships
                if model['relationships']:
                    lines.append("**Relationships:**")
                    lines.append("")
                    lines.append(
                        "| Field Name | Relation Type | Related Model | Related Name |")
                    lines.append("| --- | --- | --- | --- |")

                    for rel in model['relationships']:
                        related_name = rel['related_name'] or "-"
                        lines.append(
                            f"| {self._escape_markdown_table_cell(rel['field_name'])} | {self._escape_markdown_table_cell(rel['relation_type'])} | {self._escape_markdown_table_cell(rel['related_model'])} | {self._escape_markdown_table_cell(related_name)} |")

                    lines.append("")

                # Frontend usage notes
                lines.append("**Frontend Usage Notes:**")
                lines.append("")
                lines.append(
                    f"- Use the model name `{model['name']}` for component naming (e.g., `{model['name']}List`, `{model['name']}Detail`)")
                lines.append(
                    f"- Primary API endpoint will likely follow REST conventions for `{model['name'].lower()}`")

                # Check for special fields
                has_image = any(field['field_type'] ==
                                'ImageField' for field in model['fields'])
                has_file = any(field['field_type'] ==
                               'FileField' for field in model['fields'])
                has_date = any('Date' in field['field_type']
                               for field in model['fields'])

                if has_image:
                    lines.append(
                        "- Contains image fields - frontend should handle image uploads and display")
                if has_file:
                    lines.append(
                        "- Contains file fields - frontend should handle file uploads and downloads")
                if has_date:
                    lines.append(
                        "- Contains date/time fields - use appropriate date pickers and formatting")

                lines.append("")

        return lines

    def _format_serializers(self, serializers):
        """Format serializers for markdown report"""
        lines = []

        # Group serializers by app
        serializers_by_app = defaultdict(list)
        for serializer_key, serializer_data in serializers.items():
            app_name = serializer_key.split('.')[0]
            serializers_by_app[app_name].append(
                (serializer_key, serializer_data))

        for app_name, app_serializers in serializers_by_app.items():
            lines.append(f"### App: {app_name}")
            lines.append("")

            for serializer_key, serializer in app_serializers:
                lines.append(f"#### {serializer['name']}")
                lines.append("")

                # Basic info
                lines.append(f"**Model:** {serializer['model'] or 'None'}")
                lines.append("")

                # Fields
                if serializer['fields']:
                    lines.append("**Fields:**")
                    for field in serializer['fields']:
                        lines.append(f"- `{field}`")
                    lines.append("")

                # Meta options
                if serializer['meta']:
                    lines.append("**Meta Options:**")
                    for key, value in serializer['meta'].items():
                        lines.append(f"- `{key}`: {value}")
                    lines.append("")

                # Frontend usage notes
                lines.append("**Frontend Usage Notes:**")
                lines.append("")
                lines.append(
                    f"- This serializer is used for {serializer['model']} data representation")
                lines.append(
                    "- Fields listed above are directly accessible in API responses")

                # If no fields specified, note about __all__
                if not serializer['fields'] and serializer['meta'].get('fields') == "__all__":
                    lines.append("- Includes all fields from the model")

                lines.append("")

        return lines

    def _format_authentication(self, auth_data):
        """Format authentication details for markdown report"""
        lines = []

        lines.append("### Authentication Mechanisms")
        lines.append("")

        mechanisms = auth_data.get('mechanisms', [])
        if mechanisms:
            for mechanism in mechanisms:
                if mechanism == 'django_auth':
                    lines.append(
                        "- **Django Authentication**: Standard Django authentication system")
                elif mechanism == 'drf_auth':
                    lines.append(
                        "- **Django REST Framework Authentication**: DRF's built-in authentication")
                elif mechanism == 'drf_token':
                    lines.append(
                        "- **DRF Token Authentication**: Token-based authentication")
                    lines.append(
                        "  - Frontend should send the token in the `Authorization` header: `Token <token_value>`")
                elif mechanism == 'knox':
                    lines.append(
                        "- **Knox Token Authentication**: More secure token-based authentication")
                    lines.append(
                        "  - Frontend should send the token in the `Authorization` header: `Token <token_value>`")
                    lines.append(
                        "  - Tokens have expiry times and can be invalidated")
                elif mechanism == 'jwt':
                    lines.append(
                        "- **JWT Authentication**: JSON Web Token based authentication")
                    lines.append(
                        "  - Frontend should send the token in the `Authorization` header: `Bearer <token_value>`")
                    lines.append(
                        "  - Tokens are typically stored in localStorage or cookies")
                elif mechanism == 'oauth':
                    lines.append(
                        "- **OAuth Authentication**: OAuth-based authentication")
                    lines.append(
                        "  - Frontend will need to implement OAuth flow")
                elif mechanism == 'social_auth':
                    lines.append(
                        "- **Social Authentication**: Authentication via social providers")
                    lines.append(
                        "  - Frontend will need to implement social login buttons and flows")
                elif mechanism == 'allauth':
                    lines.append(
                        "- **Django Allauth**: Extended authentication supporting social accounts")
                elif mechanism == 'dj_rest_auth':
                    lines.append(
                        "- **dj-rest-auth**: Authentication endpoints for login, registration, password reset")
                    lines.append(
                        "  - Standard endpoints include: `/auth/login/`, `/auth/logout/`, `/auth/password/reset/`")
        else:
            lines.append("- No specific authentication mechanisms identified")

        lines.append("")

        # User model
        user_model = auth_data.get('user_model')
        if user_model:
            lines.append("### User Model")
            lines.append("")
            if auth_data.get('custom_auth'):
                lines.append(f"- **Custom User Model**: `{user_model}`")
                lines.append(
                    "  - Frontend should check for custom user fields when handling user data")
            else:
                lines.append(
                    f"- **Default Django User Model**: `{user_model}`")
                lines.append(
                    "  - Standard fields: username, email, password, first_name, last_name, is_active, is_staff, etc.")
            lines.append("")

        # Frontend integration notes
        lines.append("### Frontend Integration Notes")
        lines.append("")
        lines.append("1. **Authentication Flow**:")

        if any(m in mechanisms for m in ['drf_token', 'knox', 'jwt']):
            lines.extend([
                "   - User submits login credentials",
                "   - Backend returns a token",
                "   - Frontend stores the token (localStorage, httpOnly cookie, etc.)",
                "   - Frontend sends the token with each request in the Authorization header",
                ""
            ])
        else:
            lines.extend([
                "   - User submits login credentials",
                "   - Backend creates a session",
                "   - Frontend stores the session cookie",
                ""
            ])

        lines.append("2. **Authorization**:")
        lines.append(
            "   - Check permissions for each endpoint in the API Endpoints section above")
        lines.append(
            "   - Handle unauthorized access gracefully with appropriate UI feedback")
        lines.append("")

        lines.append("3. **Common Auth Endpoints**:")
        auth_endpoints = [
            ("POST", "/api/auth/login/", "Login with username/email and password"),
            ("POST", "/api/auth/logout/", "Logout and invalidate token/session"),
            ("POST", "/api/auth/register/", "Create a new user account"),
            ("POST", "/api/auth/password/reset/",
             "Request a password reset email"),
            ("POST", "/api/auth/password/reset/confirm/",
             "Confirm password reset with token")
        ]

        lines.append("| Method | Endpoint | Description |")
        lines.append("| --- | --- | --- |")
        for method, endpoint, desc in auth_endpoints:
            lines.append(f"| {method} | `{endpoint}` | {desc} |")

        lines.append("")

        return lines

    def _format_issues(self, issues):
        """Format compatibility issues for markdown report"""
        lines = []

        # Apply maximum issues limit
        if len(issues) > self.max_issues_to_show:
            lines.append(
                f"**Note:** Showing {self.max_issues_to_show} of {len(issues)} total issues.")
            lines.append("")
            issues = issues[:self.max_issues_to_show]

        # Group issues by severity
        issues_by_severity = defaultdict(list)
        for issue in issues:
            issues_by_severity[issue['severity']].append(issue)

        # Show errors first, then warnings, then info
        for severity in ['error', 'warning', 'info']:
            if severity in issues_by_severity:
                severity_issues = issues_by_severity[severity]

                lines.append(
                    f"### {severity.upper()} Issues ({len(severity_issues)})")
                lines.append("")

                # Group by issue type
                issues_by_type = defaultdict(list)
                for issue in severity_issues:
                    issues_by_type[issue['issue_type']].append(issue)

                for issue_type, type_issues in issues_by_type.items():
                    lines.append(
                        f"#### {issue_type.replace('_', ' ').title()} ({len(type_issues)})")
                    lines.append("")

                    for issue in type_issues:
                        file_info = f" in {issue['file']}" if issue['file'] else ""
                        lines.append(f"- {issue['description']}{file_info}")

                    # Add suggestions for fixing
                    if issue_type == 'serializer_model_mismatch':
                        lines.append("")
                        lines.append("**Suggestions:**")
                        lines.append(
                            "- Ensure the model is properly imported in the serializer file")
                        lines.append("- Check for typos in the model name")
                        lines.append(
                            "- Make sure the model exists in the project")

                    elif issue_type == 'view_serializer_mismatch':
                        lines.append("")
                        lines.append("**Suggestions:**")
                        lines.append(
                            "- Ensure the serializer is properly imported in the view file")
                        lines.append(
                            "- Check for typos in the serializer name")
                        lines.append(
                            "- Make sure the serializer exists in the project")

                    elif issue_type == 'url_view_mismatch':
                        lines.append("")
                        lines.append("**Suggestions:**")
                        lines.append(
                            "- Ensure the view is properly imported in the urls.py file")
                        lines.append("- Check for typos in the view name")
                        lines.append(
                            "- Make sure the view exists in the project")

                    elif issue_type == 'naming_convention':
                        lines.append("")
                        lines.append("**Suggestions:**")
                        lines.append(
                            "- Follow Django's naming conventions for better maintainability")
                        lines.append(
                            "- Use PascalCase for model and class names")
                        lines.append(
                            "- End serializer names with 'Serializer'")

                    elif issue_type == 'field_mismatch':
                        lines.append("")
                        lines.append("**Suggestions:**")
                        lines.append(
                            "- Update the serializer to only include fields that exist in the model")
                        lines.append(
                            "- Add missing fields to the model if they're needed")
                        lines.append("- Check for typos in field names")

                    lines.append("")

        return lines

    def _format_component_mappings(self, mappings):
        """Format component mappings for markdown report"""
        lines = []

        for mapping_name, mapping_data in mappings.items():
            lines.append(f"### {mapping_name}")
            lines.append("")

            if not mapping_data:
                lines.append("No mappings found.")
                lines.append("")
                continue

            for source, targets in mapping_data.items():
                if isinstance(targets, list) and targets:
                    lines.append(
                        f"- **{self._escape_markdown_table_cell(source)}** → {self._escape_markdown_table_cell(', '.join(str(t) for t in targets))}")

                elif isinstance(targets, str):
                    lines.append(
                        f"- **{self._escape_markdown_table_cell(source)}** → {self._escape_markdown_table_cell(targets)}")

            lines.append("")

        return lines

    def generate_code_samples(self):
        """Generate sample code for frontend integration"""
        self.log("Generating code samples...")

        # Check if we have sufficient data to generate code samples
        if not self.api_endpoints:
            self.log(
                "Insufficient data to generate code samples. No API endpoints found.", "warning")
            return {
                "api_client": "// No API endpoints found to generate client code.",
                "model_form": "// No model data found to generate form code.",
                "auth_utilities": "// No authentication data found to generate utilities."
            }

        code_samples = {}

        # React component for API data fetching
        code_samples['api_client'] = self._generate_react_api_client()

        # React component for model form
        if self.models:
            code_samples['model_form'] = self._generate_react_model_form()
        else:
            code_samples['model_form'] = "// No models found to generate form"

        # Authentication utilities
        auth_data = self.analyze_authentication()
        if auth_data and auth_data.get('mechanisms'):
            code_samples['auth_utilities'] = self._generate_auth_utilities(
                auth_data)
        else:
            code_samples['auth_utilities'] = "// No authentication mechanisms detected"

        return code_samples

    def _generate_react_api_client(self):
        """Generate a React API client based on discovered endpoints"""
        # Basic structure for an API client
        api_client = """
// api.js - Auto-generated API client
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized (e.g., redirect to login)
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Set auth token - used by auth.js
const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    localStorage.removeItem('auth_token');
    delete api.defaults.headers.common['Authorization'];
  }
};

// API endpoints
const apiClient = {
  // Auth endpoints
  login: (data) => api.post('/api/auth/login/', data),
  logout: () => api.post('/api/auth/logout/'),
  register: (data) => api.post('/api/auth/register/', data),
  me: () => api.get('/api/auth/user/'),
  requestPasswordReset: (data) => api.post('/api/auth/password/reset/', data),
  
  // Set auth token helper
  setAuthToken,
"""

        # Group endpoints by model
        endpoints_by_model = defaultdict(list)
        for endpoint in self.api_endpoints:
            if endpoint.model:
                endpoints_by_model[endpoint.model].append(endpoint)
            else:
                endpoints_by_model['other'].append(endpoint)

        # Generate API methods for each model
        for model, endpoints in endpoints_by_model.items():
            if model != 'other':
                # Add comment for model
                api_client += f"\n  // {model} endpoints\n"

                # Find common endpoints for this model
                list_endpoint = next(
                    (e for e in endpoints if e.method == 'GET' and '<id>' not in e.path), None)
                detail_endpoint = next(
                    (e for e in endpoints if e.method == 'GET' and '<id>' in e.path), None)
                create_endpoint = next(
                    (e for e in endpoints if e.method == 'POST' and '<id>' not in e.path), None)
                update_endpoint = next((e for e in endpoints if e.method in [
                                       'PUT', 'PATCH'] and '<id>' in e.path), None)
                delete_endpoint = next(
                    (e for e in endpoints if e.method == 'DELETE' and '<id>' in e.path), None)

                # Generate methods
                if list_endpoint:
                    api_client += f"  get{model}List: (params = {{}}) => api.get('{list_endpoint.path}', {{ params }}),\n"

                if detail_endpoint:
                    path = detail_endpoint.path.replace('<id>', js_tpl('id'))
                    api_client += f"  get{model}: (id) => api.get(`{path}`),\n"

                if create_endpoint:
                    api_client += f"  create{model}: (data) => api.post('{create_endpoint.path}', data),\n"

                if update_endpoint:
                    method = update_endpoint.method.lower()
                    path = update_endpoint.path.replace(
                        '<id>', js_tpl('encodeURIComponent(id)'))
                    api_client += f"  update{model}: (id, data) => api.{method}(`{path}`, data),\n"

                if delete_endpoint:
                    path = delete_endpoint.path.replace(
                        '<id>', js_tpl('encodeURIComponent(id)'))
                    api_client += f"  delete{model}: (id) => api.delete(`{path}`),\n"

        # Add other endpoints
        if 'other' in endpoints_by_model and endpoints_by_model['other']:
            api_client += "\n  // Other endpoints\n"
            for endpoint in endpoints_by_model['other']:
                # Generate a reasonable method name
                name_parts = []
                if endpoint.name:
                    name_parts = endpoint.name.split('_')
                else:
                    # Try to derive a name from the path
                    path_parts = endpoint.path.strip('/').split('/')
                    name_parts = [p for p in path_parts if not (
                        p.startswith('<') and p.endswith('>'))]

                if not name_parts:
                    name_parts = ['api']

                method_name = endpoint.method.lower() + ''.join(p.capitalize()
                                                                for p in name_parts)

                # Handle path parameters
                path = endpoint.path
                if '<' in path and '>' in path:
                    # Replace <param> with ${param}
                    import re
                    params = re.findall(r'<([^>]+)>', path)
                    param_list = ', '.join(params)
                    for param in params:
                        path = path.replace(f'<{param}>', js_tpl(param))

                    if endpoint.method.lower() in ['get', 'delete']:
                        api_client += f"  {method_name}: ({param_list}) => api.{endpoint.method.lower()}(`{path}`),\n"
                    else:
                        api_client += f"  {method_name}: ({param_list}, data) => api.{endpoint.method.lower()}(`{path}`, data),\n"
                else:
                    if endpoint.method.lower() in ['get', 'delete']:
                        api_client += f"  {method_name}: (params = {{}}) => api.{endpoint.method.lower()}('{path}', {{ params }}),\n"
                    else:
                        api_client += f"  {method_name}: (data) => api.{endpoint.method.lower()}('{path}', data),\n"

        # Close the apiClient object and export
        api_client += """};

export default apiClient;
"""

        return api_client

    def _generate_react_model_form(self):
        """Generate a React form component for a model"""
        # Select a model to generate a form for
        model_info = None
        model_name = None

        # Try to find a suitable model
        for model_key, info in self.models.items():
            # Skip abstract or through models
            if info.meta.get('abstract') or 'through' in model_key.lower():
                continue
            model_info = info
            model_name = info.name
            break

        if not model_info:
            return "// No suitable models found for form generation"

        form_component = f"""
// {model_name}Form.js - Auto-generated form component
import React, {{ useState, useEffect }} from 'react';
import apiClient from './api';

const {model_name}Form = ({{ {model_name.lower()}Id, onSubmit, onCancel }}) => {{
  const [formData, setFormData] = useState({{}});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileUploads, setFileUploads] = useState({{}});
  
  // Fetch data if editing existing {model_name}
  useEffect(() => {{
    if ({model_name.lower()}Id) {{
      setLoading(true);
      apiClient.get{model_name}({model_name.lower()}Id)
        .then(response => {{
          setFormData(response.data);
          setLoading(false);
        }})
        .catch(err => {{
          setError(`Error fetching {model_name}: ${{err.message}}`);
          setLoading(false);
        }});
    }}
  }}, [{model_name.lower()}Id]);
  
  // Handle form input changes
  const handleChange = (e) => {{
    const {{ name, value, type, checked }} = e.target;
    setFormData(prev => ({{
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }}));
  }};
  
  // Handle file input changes
  const handleFileChange = (e) => {{
    const {{ name, files }} = e.target;
    if (files.length > 0) {{
      setFileUploads(prev => ({{
        ...prev,
        [name]: files[0]
      }}));
    }}
  }};
  
  // Handle form submission
  const handleSubmit = (e) => {{
    e.preventDefault();
    setLoading(true);
    
    // Check if we have any file uploads
    const hasFileUploads = Object.keys(fileUploads).length > 0;
    
    if (hasFileUploads) {{
      // Create FormData for file uploads
      const formDataObj = new FormData();
      
      // Add regular form fields
      Object.keys(formData).forEach(key => {{
        formDataObj.append(key, formData[key]);
      }});
      
      // Add file uploads
      Object.keys(fileUploads).forEach(key => {{
        formDataObj.append(key, fileUploads[key]);
      }});
      
      // Send request with FormData
      const savePromise = {model_name.lower()}Id
        ? apiClient.update{model_name}({model_name.lower()}Id, formDataObj)
        : apiClient.create{model_name}(formDataObj);
      
      savePromise
        .then(response => {{
          setLoading(false);
          if (onSubmit) onSubmit(response.data);
        }})
        .catch(err => {{
          setError(`Error saving {model_name}: ${{err.message}}`);
          setLoading(false);
        }});
    }} else {{
      // Regular JSON request without files
      const savePromise = {model_name.lower()}Id
        ? apiClient.update{model_name}({model_name.lower()}Id, formData)
        : apiClient.create{model_name}(formData);
      
      savePromise
        .then(response => {{
          setLoading(false);
          if (onSubmit) onSubmit(response.data);
        }})
        .catch(err => {{
          setError(`Error saving {model_name}: ${{err.message}}`);
          setLoading(false);
        }});
    }}
  }};
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="form-container">
      <h2>{{ ({model_name.lower()}Id ? 'Edit' : 'Create') }} {model_name}</h2>
      
      {{ error && <div className="error-message">{{ error }}</div> }}
      
      <form onSubmit={{ handleSubmit }}>
"""

        # Generate form fields based on model fields
        for field in model_info.fields:
            field_name = field.name
            field_type = field.field_type.lower()

            # Skip automatic fields
            if field_name in ['id']:
                continue

            # Skip readonly fields
            if field.options.get('editable', True) is False:
                continue

            # Determine if field is required
            is_required = not field.options.get('blank', False)

            # Generate appropriate form control based on field type
            if field_type in ['charfield', 'emailfield', 'slugfield', 'urlfield']:
                # Map field types to appropriate HTML input types
                input_type = None
                if field_type == 'charfield' or field_type == 'slugfield':
                    input_type = 'text'
                elif field_type == 'emailfield':
                    input_type = 'email'
                elif field_type == 'urlfield':
                    input_type = 'url'

                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()}</label>
          <input
            type="{input_type}"
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
          />
        </div>
"""
            elif field_type == 'textfield':
                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()}</label>
          <textarea
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
            rows="4"
          ></textarea>
        </div>
"""
            elif field_type in ['integerfield', 'positiveintegerfield', 'positivesmallintegerfield']:
                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()}</label>
          <input
            type="number"
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
          />
        </div>
"""
            elif field_type == 'booleanfield':
                form_component += f"""
        <div className="form-group checkbox">
          <label htmlFor="{field_name}">
            <input
              type="checkbox"
              id="{field_name}"
              name="{field_name}"
              checked={{ Boolean(formData.{field_name}) }}
              onChange={{ handleChange }}
            />
            {field_name.replace('_', ' ').title()}
          </label>
        </div>
"""
            elif field_type in ['datefield', 'datetimefield']:
                # Pre-compute input type
                input_type = 'datetime-local' if field_type == 'datetimefield' else 'date'
                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()}</label>
          <input
            type="{input_type}"
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
          />
        </div>
"""
            elif field_type in ['foreignkey', 'onetoonefield', 'manytomanyfield']:
                related_model = "Related Model"
                for rel in model_info.relationships:
                    if rel['field_name'] == field_name:
                        related_model = rel['related_model']
                        break

                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                # Different handling for ManyToMany vs ForeignKey
                if field_type == 'manytomanyfield':
                    form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()} ({related_model})</label>
          {{/* For ManyToMany fields, you'll need a multi-select or checkbox list */}}
          <select
            id="{field_name}"
            name="{field_name}"
            multiple
            value={{ formData.{field_name} || [] }}
            onChange={{ (e) => {{
              // Handle multiple select 
              const values = Array.from(e.target.selectedOptions).map(option => option.value);
              setFormData(prev => ({{
                ...prev,
                {field_name}: values
              }}));
            }} }}
            {required_attr}
          >
            {{/* Options would be loaded dynamically */}}
            <option value="">-- Select Options --</option>
            {{/* TODO: Fetch {related_model} options via API and map them here */}}
            {{/* 
              Example loading code:
              
              const [{related_model.split('.')[-1].toLowerCase()}s, set{related_model.split('.')[-1]}s] = useState([]);
              
              useEffect(() => {{
                apiClient.get{related_model.split('.')[-1]}List()
                  .then(response => {{
                    set{related_model.split('.')[-1]}s(response.data);
                  }})
                  .catch(error => console.error('Error loading options:', error));
              }}, []);
              
              // Then in your JSX:
              {{
                {related_model.split('.')[-1].toLowerCase()}s.map(item => (
                  <option key={{item.id}} value={{item.id}}>{{item.name}}</option>
                ))
              }}
            */}}
          </select>
        </div>
"""
                else:
                    form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()} ({related_model})</label>
          <select
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
          >
            <option value="">Select {related_model.split('.')[-1]}</option>
            {{/* TODO: Fetch {related_model} options via API and map them here */}}
            {{/* 
              Example loading code:
              
              const [{related_model.split('.')[-1].toLowerCase()}s, set{related_model.split('.')[-1]}s] = useState([]);
              
              useEffect(() => {{
                apiClient.get{related_model.split('.')[-1]}List()
                  .then(response => {{
                    set{related_model.split('.')[-1]}s(response.data);
                  }})
                  .catch(error => console.error('Error loading options:', error));
              }}, []);
              
              // Then in your JSX:
              {{
                {related_model.split('.')[-1].toLowerCase()}s.map(item => (
                  <option key={{item.id}} value={{item.id}}>{{item.name}}</option>
                ))
              }}
            */}}
          </select>
        </div>
"""
            elif field_type in ['filefield', 'imagefield']:
                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()}</label>
          <input
            type="file"
            id="{field_name}"
            name="{field_name}"
            onChange={{ handleFileChange }}
            {required_attr}
          />
          {{ formData.{field_name} && (
            <div className="file-preview">
              {f'<img src={{formData.{field_name}}} alt="{field_name}" width="100" />' if field_type == 'imagefield' else f'<span>Current file: {{formData.{field_name}}}</span>'}
            </div>
          )}}
        </div>
"""
            else:
                # Default to text input for other field types
                # Pre-compute required attribute
                required_attr = 'required={true}' if is_required else ''

                form_component += f"""
        <div className="form-group">
          <label htmlFor="{field_name}">{field_name.replace('_', ' ').title()} ({field_type})</label>
          <input
            type="text"
            id="{field_name}"
            name="{field_name}"
            value={{ formData.{field_name} || '' }}
            onChange={{ handleChange }}
            {required_attr}
          />
        </div>
"""

        # Form submission buttons
        form_component += """
        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={ loading }>
            { loading ? 'Saving...' : 'Save' }
          </button>
          { onCancel && (
            <button type="button" className="btn btn-secondary" onClick={ onCancel }>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default """ + model_name + "Form;\n"

        return form_component

    def _generate_auth_utilities(self, auth_data=None):
        """Generate authentication utilities based on detected authentication mechanism"""
        # Use passed auth_data or get it if not provided
        if auth_data is None:
            auth_data = self.analyze_authentication()

        mechanisms = auth_data.get('mechanisms', [])
        is_token_based = any(m in mechanisms for m in [
                             'drf_token', 'knox', 'jwt'])
        is_jwt = 'jwt' in mechanisms

        auth_utilities = """
// auth.js - Authentication utilities
import apiClient from './api';

// Storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';
"""

        if is_token_based:
            token_prefix = 'Bearer ' if is_jwt else 'Token '

            auth_utilities += f"""
// Login user and store token
export const login = async (username, password) => {{
  try {{
    const response = await apiClient.login({{ username, password }});
    
    // Extract token from response based on API format
    const token = response.data.{'token' if not is_jwt else 'access'};
    
    if (token) {{
      // Store token
      localStorage.setItem(TOKEN_KEY, token);
      
      // Store user info
      const user = response.data.user || {{
        username,
        // Add other user fields available from response
      }};
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      
      // Set token in API client
      apiClient.setAuthToken(token);
      
      return user;
    }}
    throw new Error('Token not found in response');
  }} catch (error) {{
    console.error('Login error:', error);
    throw error;
  }}
}};

// Logout user
export const logout = async () => {{
  try {{
    // Call logout endpoint if available
    if (isAuthenticated()) {{
      await apiClient.logout();
    }}
  }} catch (error) {{
    console.error('Logout error:', error);
  }} finally {{
    // Always clear local storage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    
    // Remove token from API client
    apiClient.setAuthToken(null);
  }}
}};

// Check if user is authenticated
export const isAuthenticated = () => {{
  const token = localStorage.getItem(TOKEN_KEY);
  return !!token;
}};

// Get current user
export const getCurrentUser = () => {{
  try {{
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  }} catch (error) {{
    console.error('Error getting current user:', error);
    return null;
  }}
}};

// Get auth header
export const getAuthHeader = () => {{
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? {{ Authorization: `{token_prefix}${token}` }} : {{}};
}};

// Register new user
export const register = async (userData) => {{
  try {{
    const response = await apiClient.register(userData);
    return response.data;
  }} catch (error) {{
    console.error('Registration error:', error);
    throw error;
  }}
}};

// Password reset request
export const requestPasswordReset = async (email) => {{
  try {{
    const response = await apiClient.requestPasswordReset({{ email }});
    return response.data;
  }} catch (error) {{
    console.error('Password reset request error:', error);
    throw error;
  }}
}};
"""
        else:
            # Session-based authentication
            auth_utilities += """
// Session-based login
export const login = async (username, password) => {
  try {
    const response = await apiClient.login({ username, password });
    
    // Store user info
    const user = response.data.user || { username };
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    
    return user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// Logout user
export const logout = async () => {
  try {
    await apiClient.logout();
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem(USER_KEY);
  }
};

// Check if user is authenticated
export const isAuthenticated = async () => {
  try {
    // With session auth, we need to check with the server
    const response = await apiClient.me();
    return !!response.data;
  } catch (error) {
    return false;
  }
};

// Get current user
export const getCurrentUser = async () => {
  try {
    // Try to get from local storage first
    const cachedUser = localStorage.getItem(USER_KEY);
    
    if (cachedUser) {
      return JSON.parse(cachedUser);
    }
    
    // Otherwise fetch from API
    const response = await apiClient.me();
    const user = response.data;
    
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    
    return user;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
};

// Register new user
export const register = async (userData) => {
  try {
    const response = await apiClient.register(userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

// Password reset request
export const requestPasswordReset = async (email) => {
  try {
    const response = await apiClient.requestPasswordReset({ email });
    return response.data;
  } catch (error) {
    console.error('Password reset request error:', error);
    throw error;
  }
};
"""

        # Add React auth context
        auth_utilities += """
// React authentication context
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Check authentication status on mount
    const checkAuth = async () => {
      try {
        if (isAuthenticated()) {
          const userData = getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);
  
  const authContextValue = {
    user,
    isAuthenticated: !!user,
    login: async (username, password) => {
      const userData = await login(username, password);
      setUser(userData);
      return userData;
    },
    logout: async () => {
      await logout();
      setUser(null);
    },
    register: async (userData) => {
      const result = await register(userData);
      return result;
    },
    loading
  };
  
  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
"""

        return auth_utilities

    def _process_included_urls(self, include_path, app_name):
        """Process URLs from an included module"""
        try:
            # Convert dotted path to filesystem path
            module_path = include_path.replace('.', '/') + '.py'
            if not module_path.startswith('/'):
                module_path = os.path.join(self.backend_path, module_path)

            if os.path.exists(module_path):
                self._process_urls_file(module_path, app_name)
            else:
                self.log(
                    f"Could not find included URLs module: {include_path}", "warning")
        except Exception as e:
            self.log(
                f"Error processing included URLs {include_path}: {str(e)}", "error")

    # Then modify _extract_include_from_node to call this method

    def generate_openapi_schema(self):
        """Generate OpenAPI schema using DRF's schema generators if available"""
        self.log("Attempting to generate OpenAPI schema...")

        if not self.django_ready:
            self.log(
                "Django environment not initialized, cannot generate OpenAPI schema", "error")
            return None

        schema = None

        # Try different schema generators

        # 1. Try drf-spectacular if available
        try:
            from drf_spectacular.generators import SchemaGenerator as SpectacularGenerator
            from drf_spectacular.settings import spectacular_settings

            self.log("Using drf-spectacular for schema generation", "success")
            generator = SpectacularGenerator()
            schema = generator.get_schema(request=None, public=True)
            return schema
        except ImportError:
            self.log("drf-spectacular not available", "info")

        # 2. Try drf-yasg if available
        try:
            from drf_yasg.generators import OpenAPISchemaGenerator
            from drf_yasg.views import get_schema_view
            from drf_yasg import openapi

            self.log("Using drf-yasg for schema generation", "success")
            schema_view = get_schema_view(
                openapi.Info(
                    title="API Documentation",
                    default_version='v1',
                    description="Auto-generated API documentation",
                ),
                public=True,
            )
            generator = OpenAPISchemaGenerator()
            schema = generator.get_schema(request=None, public=True)
            return schema
        except ImportError:
            self.log("drf-yasg not available", "info")

        # 3. Generate a basic schema ourselves
        if not schema and self.api_endpoints:
            self.log(
                "Generating basic OpenAPI schema from collected endpoints", "info")
            schema = self._generate_basic_openapi_schema()
            return schema

        self.log("Could not generate OpenAPI schema", "warning")
        return None

    def _generate_basic_openapi_schema(self):
        """Generate a basic OpenAPI schema from collected endpoints"""
        # Basic OpenAPI 3.0 structure
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Documentation",
                "version": "1.0.0",
                "description": "Auto-generated API documentation"
            },
            "servers": [
                {
                    "url": "/",
                    "description": "API Server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": self._generate_component_schemas(),
                "securitySchemes": self._generate_security_schemes()
            }
        }

        # Add paths based on api_endpoints
        for endpoint in self.api_endpoints:
            path = endpoint.path
            method = endpoint.method.lower()

            # Ensure path exists in schema
            if path not in schema["paths"]:
                schema["paths"][path] = {}

            # Add operation for this method
            schema["paths"][path][method] = self._generate_operation_object(
                endpoint)

        return schema

    def _generate_component_schemas(self):
        """Generate OpenAPI component schemas from models"""
        schemas = {}

        for model_name, model_info in self.models.items():
            # Skip abstract models
            if model_info.meta.get('abstract', False):
                continue

            simple_name = model_info.name

            properties = {}
            required = []

            for field in model_info.fields:
                field_schema = self._field_to_openapi_schema(field)
                properties[field.name] = field_schema

                # Check if field is required
                if not field.options.get('null', False) and not field.options.get('blank', False):
                    required.append(field.name)

            # Add schema
            schemas[simple_name] = {
                "type": "object",
                "properties": properties
            }

            if required:
                schemas[simple_name]["required"] = required

        return schemas

    def _field_to_openapi_schema(self, field):
        """Convert a Django model field to OpenAPI schema"""
        # Map Django field types to OpenAPI types
        field_type = field.field_type.lower()

        if 'char' in field_type or 'text' in field_type or 'slug' in field_type or 'url' in field_type or 'email' in field_type:
            schema = {"type": "string"}
            if 'max_length' in field.options:
                schema["maxLength"] = field.options['max_length']
        elif 'int' in field_type:
            schema = {"type": "integer"}
        elif 'float' in field_type or 'decimal' in field_type:
            schema = {"type": "number"}
        elif 'bool' in field_type:
            schema = {"type": "boolean"}
        elif 'date' in field_type and 'time' in field_type:
            schema = {"type": "string", "format": "date-time"}
        elif 'date' in field_type:
            schema = {"type": "string", "format": "date"}
        elif 'time' in field_type:
            schema = {"type": "string", "format": "time"}
        elif 'file' in field_type or 'image' in field_type:
            schema = {"type": "string", "format": "binary"}
        elif 'json' in field_type:
            schema = {"type": "object"}
        elif 'foreign' in field_type or 'onetoonefield' in field_type:
            schema = {"type": "integer"}  # Represents the ID
        elif 'manytomany' in field_type:
            schema = {
                "type": "array",
                "items": {"type": "integer"}
            }
        else:
            schema = {"type": "string"}

        # Add description from help_text
        if 'help_text' in field.options:
            schema["description"] = field.options['help_text']

        # Add enum from choices
        if 'choices' in field.options:
            choices = field.options['choices']
            if isinstance(choices, (list, tuple)):
                try:
                    enum_values = [choice[0] for choice in choices]
                    schema["enum"] = enum_values
                except (IndexError, TypeError):
                    pass

        return schema

    def _generate_operation_object(self, endpoint):
        """Generate OpenAPI operation object for an endpoint"""
        operation = {
            "summary": f"{endpoint.method} {endpoint.path}",
            "description": f"Endpoint for {endpoint.view}",
            "responses": {
                "200": {
                    "description": "Successful response"
                },
                "400": {
                    "description": "Bad request"
                },
                "401": {
                    "description": "Unauthorized"
                },
                "403": {
                    "description": "Forbidden"
                },
                "404": {
                    "description": "Not found"
                }
            }
        }

        # Add tags based on app/model
        if endpoint.model:
            operation["tags"] = [endpoint.model.split('.')[-1]]
        else:
            app_name = self._extract_app_name_from_view(endpoint.view)
            operation["tags"] = [app_name]

        # Add security requirements if authenticated
        if endpoint.permissions and any(p for p in endpoint.permissions if 'IsAuthenticated' in p):
            operation["security"] = [{"BearerAuth": []}]

        # Add request body for POST, PUT, PATCH
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and endpoint.serializer:
            operation["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{endpoint.serializer.split('.')[-1].replace('Serializer', '')}"
                        }
                    }
                },
                "required": True
            }

        # Add path parameters
        path_params = []
        for part in endpoint.path.split('/'):
            if part.startswith('<') and part.endswith('>'):
                param_name = part[1:-1]
                path_params.append({
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                })

        if path_params:
            operation["parameters"] = path_params

        return operation

    def _generate_security_schemes(self):
        """Generate security schemes based on authentication methods"""
        security_schemes = {}

        # Check authentication mechanisms
        auth_data = self.analyze_authentication()
        mechanisms = auth_data.get('mechanisms', [])

        if 'jwt' in mechanisms:
            security_schemes["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        elif any(m in mechanisms for m in ['drf_token', 'knox']):
            security_schemes["TokenAuth"] = {
                "type": "http",
                "scheme": "bearer"
            }
        elif 'oauth' in mechanisms:
            security_schemes["OAuth2"] = {
                "type": "oauth2",
                "flows": {
                    "implicit": {
                        "authorizationUrl": "/api/oauth/authorize",
                        "tokenUrl": "/api/oauth/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access"
                        }
                    }
                }
            }
        else:
            # Default to basic auth
            security_schemes["BasicAuth"] = {
                "type": "http",
                "scheme": "basic"
            }

        return security_schemes

    def generate_typescript_interfaces(self):
        """Generate TypeScript interfaces from models and serializers"""
        self.log("Generating TypeScript interfaces...")

        typescript_code = """// Generated TypeScript interfaces
// Generated on: ${new Date().toISOString()}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  success: boolean;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// Error Types
export interface ApiError {
  status: number;
  message: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

"""

        # Add models
        model_interfaces = []
        for model_key, model_info in self.models.items():
            # Skip abstract models
            if model_info.meta.get('abstract', False):
                continue

            model_interfaces.append(self._generate_model_interface(model_info))

        # Sort model interfaces alphabetically for better organization
        model_interfaces.sort()
        typescript_code += "\n// Model Interfaces\n" + \
            "\n\n".join(model_interfaces) + "\n\n"

        # Add serializers if they have different fields than models
        serializer_interfaces = []
        for serializer_key, serializer_info in self.serializers.items():
            model_name = serializer_info.model
            if model_name:
                serializer_name = serializer_info.name

                if serializer_name.endswith('Serializer'):
                    # Remove 'Serializer' suffix
                    interface_name = serializer_name[:-10]
                else:
                    interface_name = serializer_name

                # Only generate if it's a specialized serializer (not just a model wrapper)
                if serializer_info.meta.get('fields') != '__all__' or serializer_info.meta.get('exclude'):
                    serializer_interfaces.append(
                        self._generate_serializer_interface(serializer_info, interface_name))

        if serializer_interfaces:
            typescript_code += "\n// Serializer Interfaces\n" + \
                "\n\n".join(serializer_interfaces) + "\n\n"

        # Add React Query hooks
        typescript_code += self._generate_react_query_hooks()

        return typescript_code

    def generate_sample_config(self, output_file="backend_analyzer_config.json"):
        """Generate a sample configuration file"""
        self.log(f"Generating sample configuration file: {output_file}")

        example_config = {
            "analysis": {
                "exclude_apps": ["admin", "auth", "contenttypes", "sessions"],
                "max_issues_to_show": 100
            },
            "output": {
                "include_code_samples": True,
                "output_format": "markdown",
                "output_file": "backend_analysis_report.md"
            },
            "django": {
                "use_reflection": True,
                "analyzer_mode": True
            },
            "openapi": {
                "enabled": True,
                "output_file": "openapi_schema.json"
            },
            "typescript": {
                "enabled": True,
                "output_file": "api_types.ts"
            }
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, indent=2)
            self.log(
                f"Sample configuration file generated: {output_file}", "success")
            return True
        except Exception as e:
            self.log(
                f"Error generating sample configuration file: {str(e)}", "error")
            return False

    def _generate_model_interface(self, model_info):
        """Generate TypeScript interface for a Django model"""
        interface_name = model_info.name
        fields = []

        # Always include id field since it's fundamental for most operations
        fields.append("id: number")

        for field in model_info.fields:
            field_name = field.name
            field_type = field.field_type.lower()

            # Skip automatic primary keys that we've already added
            if field_name == 'id':
                continue

            # Don't skip created/updated fields as they're often useful
            # but mark them as readonly
            readonly = ""
            if field_name in ['created_at', 'updated_at', 'created', 'modified']:
                readonly = "readonly "

            # Determine if field is required
            is_optional = field.options.get(
                'blank', False) or field.options.get('null', False)
            optional_marker = "?" if is_optional else ""

            # Generate appropriate TypeScript type
            if field_type in ['charfield', 'emailfield', 'slugfield', 'urlfield', 'textfield']:
                # Map field types to appropriate TypeScript types
                ts_type = 'string'
            elif field_type in ['integerfield', 'positiveintegerfield', 'positivesmallintegerfield', 'autofield']:
                ts_type = 'number'
            elif field_type == 'booleanfield':
                ts_type = 'boolean'
            elif field_type in ['datefield']:
                ts_type = 'string /* YYYY-MM-DD */'
            elif field_type in ['datetimefield', 'timezonefield']:
                ts_type = 'string /* ISO-8601 date string */'
            elif field_type == 'jsonfield':
                ts_type = 'Record<string, any>'
            elif field_type in ['foreignkey', 'onetoonefield']:
                ts_type = 'number'  # Foreign key ID
            elif field_type == 'manytomanyfield':
                ts_type = 'number[]'  # Array of IDs
            elif field_type in ['filefield', 'imagefield']:
                ts_type = 'string'  # URL to the file
            else:
                ts_type = 'any'

            # Add field to interface
            fields.append(
                f"{readonly}{field_name}{optional_marker}: {ts_type}")

        # Generate interface
        fields_str = ';\n  '.join(fields)
        return f"export interface {interface_name} {{\n  {fields_str};\n}}"

    def _generate_serializer_interface(self, serializer_info, interface_name):
        """Generate TypeScript interface for a Django serializer"""
        fields = []

        for field in serializer_info.fields:
            field_name = field
            field_type = 'string'

            # Add field to interface
            fields.append(f"{field_name}: {field_type}")

        # Generate interface
        fields_str = '; '.join(fields)
        return f"export interface {interface_name}Serializer {{\n  {fields_str}\n}}\n\n"

    def _generate_react_query_hooks(self):
        """Generate React Query hooks for data fetching"""
        return """
// React Query hooks
import { useQuery, useMutation, QueryClient } from 'react-query';

// API client for making requests
import apiClient from './api';

// Authentication context
import { useAuth } from './auth';

// Create a client
const queryClient = new QueryClient();

/**
 * Custom hook factories for API endpoints
 * Replace ModelName with actual model names in your project
 * 
 * Usage example:
 * 
 * const { data, isLoading, error } = useModelList();
 * const { mutate: createModel } = useModelCreate();
 */

// Generic list hook factory
export const createListHook = (endpoint, key) => (params = {}) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery(
    [key, params],
    () => apiClient[endpoint](params),
    {
      enabled: isAuthenticated,
      select: (response) => response.data,
    }
  );
};

// Generic detail hook factory
export const createDetailHook = (endpoint, key) => (id, params = {}) => {
  const { isAuthenticated } = useAuth();
  
  return useQuery(
    [key, id, params],
    () => apiClient[endpoint](id, params),
    {
      enabled: isAuthenticated && !!id,
      select: (response) => response.data,
    }
  );
};

// Generic create hook factory
export const createCreateHook = (endpoint, listKey) => () => {
  return useMutation(
    (data) => apiClient[endpoint](data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(listKey);
      }
    }
  );
};

// Generic update hook factory
export const createUpdateHook = (endpoint, listKey, detailKey) => () => {
  return useMutation(
    ({ id, data }) => apiClient[endpoint](id, data),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(listKey);
        queryClient.invalidateQueries([detailKey, variables.id]);
      }
    }
  );
};

// Generic delete hook factory
export const createDeleteHook = (endpoint, listKey) => () => {
  return useMutation(
    (id) => apiClient[endpoint](id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(listKey);
      }
    }
  );
};

/**
 * Example Hooks
 * Uncomment and customize these for your models
 */

/*
// User hooks
export const useUserList = createListHook('getUserList', 'users');
export const useUserDetail = createDetailHook('getUser', 'user');
export const useUserCreate = createCreateHook('createUser', 'users');
export const useUserUpdate = createUpdateHook('updateUser', 'users', 'user');
export const useUserDelete = createDeleteHook('deleteUser', 'users');

// Post hooks
export const usePostList = createListHook('getPostList', 'posts');
export const usePostDetail = createDetailHook('getPost', 'post');
export const usePostCreate = createCreateHook('createPost', 'posts');
export const usePostUpdate = createUpdateHook('updatePost', 'posts', 'post');
export const usePostDelete = createDeleteHook('deletePost', 'posts');
*/
"""

    def generate_security_matrix(self):
        """Generate a security matrix showing which endpoints require which permissions"""
        self.log("Generating security matrix...")

        # Initialize matrix data structure
        matrix = {
            'endpoints': [],
            'permissions': set(),
            'auth_required': [],
            'public': []
        }

        # Get authentication data
        auth_data = self.analyze_authentication()
        auth_mechanisms = auth_data.get('mechanisms', [])

        # Process endpoints
        for endpoint in self.api_endpoints:
            endpoint_info = {
                'path': endpoint.path,
                'method': endpoint.method,
                'view': endpoint.view,
                'permissions': endpoint.permissions,
                'requires_auth': False,
                'permission_matrix': {}
            }

            # Check if authentication is required
            requires_auth = False

            # Add all permissions to the set
            for perm in endpoint.permissions:
                matrix['permissions'].add(perm)
                endpoint_info['permission_matrix'][perm] = True

                # Check if this permission requires authentication
                if 'IsAuthenticated' in perm or 'TokenHasScope' in perm or 'IsAdminUser' in perm:
                    requires_auth = True

            # Update requires_auth flag
            endpoint_info['requires_auth'] = requires_auth

            # Add to the appropriate list
            matrix['endpoints'].append(endpoint_info)
            if requires_auth:
                matrix['auth_required'].append(endpoint_info)
            else:
                matrix['public'].append(endpoint_info)

        # Find endpoints that require authentication but no auth mechanism is configured
        if not auth_mechanisms and matrix['auth_required']:
            self.log(
                f"Warning: {len(matrix['auth_required'])} endpoints require authentication, but no authentication mechanism is configured", "warning")
            for endpoint in matrix['auth_required']:
                self.log(
                    f"  {endpoint['method']} {endpoint['path']} requires authentication", "warning")

        # Create a warnings list for issues
        matrix['warnings'] = []

        # Check for inconsistent permission usage
        endpoint_groups = defaultdict(list)
        for endpoint in matrix['endpoints']:
            # Group by base path (remove parameters)
            base_path = re.sub(r'<[^>]+>', '<param>', endpoint['path'])
            endpoint_groups[base_path].append(endpoint)

        for base_path, endpoints in endpoint_groups.items():
            # Check for inconsistent auth requirements within the same resource
            auth_required = [e for e in endpoints if e['requires_auth']]
            not_auth_required = [
                e for e in endpoints if not e['requires_auth']]

            if auth_required and not_auth_required:
                matrix['warnings'].append({
                    'type': 'inconsistent_auth',
                    'message': f"Inconsistent authentication requirements for {base_path}",
                    'details': {
                        'auth_required': [f"{e['method']} {e['path']}" for e in auth_required],
                        'not_auth_required': [f"{e['method']} {e['path']}" for e in not_auth_required]
                    }
                })

        # Convert permissions set to list
        matrix['permissions'] = list(matrix['permissions'])

        return matrix

    def _format_security_matrix(self, matrix):
        """Format security matrix for markdown report"""
        lines = []

        # Add overview
        lines.append("## API Security Matrix")
        lines.append("")
        lines.append(f"- Total endpoints: {len(matrix['endpoints'])}")
        lines.append(f"- Protected endpoints: {len(matrix['auth_required'])}")
        lines.append(f"- Public endpoints: {len(matrix['public'])}")
        lines.append(
            f"- Unique permission classes: {len(matrix['permissions'])}")
        lines.append("")

        # Add warnings
        if matrix['warnings']:
            lines.append("### Security Warnings")
            lines.append("")
            for warning in matrix['warnings']:
                lines.append(f"- **{warning['type']}**: {warning['message']}")
                if 'details' in warning:
                    for key, values in warning['details'].items():
                        lines.append(f"  - {key}: {', '.join(values)}")
            lines.append("")

        # Add permission classes table
        lines.append("### Permission Classes")
        lines.append("")
        lines.append(
            "| Permission Class | Endpoints Using | Authentication Required |")
        lines.append("| --- | --- | --- |")

        for perm in matrix['permissions']:
            # Count endpoints using this permission
            count = sum(1 for e in matrix['endpoints']
                        if perm in e['permissions'])
            # Check if this permission requires authentication
            auth_required = "Yes" if any(keyword in perm for keyword in [
                                         'IsAuthenticated', 'TokenHasScope', 'IsAdminUser']) else "No"
            lines.append(f"| {perm} | {count} | {auth_required} |")

        lines.append("")

        # Add protected endpoints table
        if matrix['auth_required']:
            lines.append("### Protected Endpoints")
            lines.append("")
            lines.append("| Method | Path | Permissions |")
            lines.append("| --- | --- | --- |")

            for endpoint in matrix['auth_required']:
                perms = ', '.join(
                    endpoint['permissions']) if endpoint['permissions'] else 'Default'
                lines.append(
                    f"| {endpoint['method']} | {endpoint['path']} | {perms} |")

            lines.append("")

        # Add public endpoints table
        if matrix['public']:
            lines.append("### Public Endpoints")
            lines.append("")
            lines.append("| Method | Path | Permissions |")
            lines.append("| --- | --- | --- |")

            for endpoint in matrix['public']:
                perms = ', '.join(
                    endpoint['permissions']) if endpoint['permissions'] else 'None'
                lines.append(
                    f"| {endpoint['method']} | {endpoint['path']} | {perms} |")

            lines.append("")

        return lines


def main():
    """Main function to run the analyzer"""
    try:
        parser = argparse.ArgumentParser(
            description="Analyze Django backend for frontend integration")
        parser.add_argument('--backend_path', type=str, default='.',
                            help='Path to the Django backend directory')
        parser.add_argument('--output_file', type=str, default='backend_analysis_report.md',
                            help='Output file path')
        parser.add_argument('--output_format', type=str, default='markdown', choices=['markdown', 'json'],
                            help='Output format (markdown or json)')
        parser.add_argument('--verbose', action='store_true',
                            help='Enable verbose output')
        parser.add_argument('--include_code_samples', action='store_true',
                            help='Include sample code in the report')
        parser.add_argument('--exclude_apps', type=str, nargs='+', default=[],
                            help='List of app names to exclude from analysis')
        parser.add_argument('--max_issues_to_show', type=int, default=100,
                            help='Maximum number of issues to include in the report')

        # Django reflection flags (mutually exclusive)
        reflection_group = parser.add_mutually_exclusive_group()
        reflection_group.add_argument('--use_django_reflection', action='store_true',
                                      help='Use Django introspection APIs (runs Django project)')
        reflection_group.add_argument('--no_django_reflection', action='store_false', dest='use_django_reflection',
                                      help='Disable Django introspection (use static analysis only)')
        parser.set_defaults(use_django_reflection=True)

        parser.add_argument('--fail_on_error', action='store_true',
                            help='Exit with error code if critical issues are found')
        parser.add_argument('--output_openapi', action='store_true',
                            help='Generate OpenAPI schema and save to file')
        parser.add_argument('--openapi_file', type=str, default='openapi_schema.json',
                            help='Output file path for OpenAPI schema')
        parser.add_argument('--output_typescript', action='store_true',
                            help='Generate TypeScript interfaces and React Query hooks')
        parser.add_argument('--typescript_file', type=str, default='api_types.ts',
                            help='Output file path for TypeScript interfaces')
        parser.add_argument('--config_file', type=str,
                            help='Path to configuration file (JSON, TOML, or YAML)')
        parser.add_argument('--generate_config', action='store_true',
                            help='Generate a sample configuration file')
        parser.add_argument('--config_output', type=str, default='backend_analyzer_config.json',
                            help='Output path for the sample configuration file')

        args = parser.parse_args()

        # If just generating config, do that and exit
        if args.generate_config:
            analyzer = BackendAnalyzer(backend_path='.', verbose=args.verbose)
            analyzer.generate_sample_config(args.config_output)
            print(f"Sample configuration generated: {args.config_output}")
            return

        logger.info(f"Analyzing Django backend at: {args.backend_path}")
        analyzer = BackendAnalyzer(
            backend_path=args.backend_path,
            verbose=args.verbose,
            exclude_apps=args.exclude_apps,
            max_issues_to_show=args.max_issues_to_show,
            use_django_reflection=args.use_django_reflection,
            fail_on_error=args.fail_on_error,
            output_openapi=args.output_openapi,
            output_typescript=args.output_typescript,
            config_file=args.config_file
        )

        # Run the analysis
        analysis_data = analyzer.analyze()

        # Check for critical errors
        critical_errors = [i for i in analysis_data.get('backend_compatibility', {}).get('issues', [])
                           if i.get('severity') == 'error']

        if args.include_code_samples:
            code_samples = analyzer.generate_code_samples()
            analysis_data['code_samples'] = code_samples

        # Generate the report
        report = analyzer.generate_report(analysis_data, args.output_format)

        # Save the report
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report generated: {args.output_file}")

        # Generate OpenAPI schema if requested
        if args.output_openapi:
            schema = analyzer.generate_openapi_schema()
            if schema:
                with open(args.openapi_file, 'w') as f:
                    json.dump(schema, f, indent=2)
                print(f"OpenAPI schema generated: {args.openapi_file}")
            else:
                print("Could not generate OpenAPI schema")

        # Generate TypeScript interfaces if requested
        if args.output_typescript:
            typescript = analyzer.generate_typescript_interfaces()
            if typescript:
                with open(args.typescript_file, 'w') as f:
                    f.write(typescript)
                print(
                    f"TypeScript interfaces generated: {args.typescript_file}")
            else:
                print("Could not generate TypeScript interfaces")

        # Exit with error code if critical errors found and fail_on_error is set
        if args.fail_on_error and critical_errors:
            print(f"Critical errors found: {len(critical_errors)}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
