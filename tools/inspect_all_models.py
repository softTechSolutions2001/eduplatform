# fmt: off
# isort: skip_file

r"""
File: production_inspect_django.py

Purpose: Production-ready Django inspection tool with comprehensive edge-case handling
         and enterprise features for CI/CD integration.

This production version addresses:
- All edge cases from the previous review
- Circular import protection
- Performance timing
- CI-friendly exit codes
- Modular architecture
- Comprehensive error handling

Created by: Enhanced based on Professor Santhanam's original work
Production version: 2025-06-20
"""

import os
import sys
import inspect
import importlib
import importlib.util
import datetime
import json
import csv
import time
import logging
import re
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('django_inspection.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class InspectionConfig:
    """Configuration for the inspection tool"""
    output_file: str = "production_inspection_report.txt"
    json_output_file: str = "inspection_data.json"
    csv_output_file: str = "inspection_summary.csv"
    html_output_file: str = "inspection_report.html"
    apps_to_inspect: List[str] = None
    detailed_view: bool = True
    export_json: bool = True
    export_csv: bool = True
    export_html: bool = True
    check_security: bool = True
    analyze_performance: bool = True
    max_lines_per_section: int = 1000
    exit_on_issues: bool = False
    issue_threshold: int = 10
    timing_enabled: bool = True

@dataclass
class TimingData:
    """Performance timing data"""
    phase: str
    duration: float
    start_time: float
    end_time: float

class ProductionInspector:
    """Production-ready Django inspection tool"""

    def __init__(self, config: InspectionConfig):
        self.config = config
        self.report = []
        self.issues = []
        self.security_issues = []
        self.timings = []
        self.inspection_data = {
            'timestamp': None,
            'django_version': None,
            'drf_available': False,
            'models': {},
            'views': {},
            'serializers': {},
            'urls': [],
            'consistency_issues': [],
            'security_issues': [],
            'performance_notes': [],
            'timings': [],
            'summary': {}
        }

        # Setup Django environment
        self._setup_django()

        # Import Django components after setup
        self._import_django_components()

    def _setup_django(self):
        """Setup Django environment with error handling"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)

            if not os.environ.get('DJANGO_SETTINGS_MODULE'):
                # Try to detect settings module
                possible_settings = [
                    'settings',
                    'config.settings',
                    'core.settings',
                    'educore.settings'
                ]

                for setting in possible_settings:
                    if importlib.util.find_spec(setting):
                        os.environ.setdefault('DJANGO_SETTINGS_MODULE', setting)
                        break
                else:
                    raise ValueError("Could not detect Django settings module")

            import django
            django.setup()

            self.inspection_data['django_version'] = django.get_version()
            logger.info(f"Django {django.get_version()} initialized successfully")

        except Exception as e:
            logger.error(f"Failed to setup Django: {e}")
            raise

    def _import_django_components(self):
        """Import Django components with error handling"""
        try:
            from django.apps import apps
            from django.urls import get_resolver
            from django.conf import settings
            from django.db import models

            self.apps = apps
            self.get_resolver = get_resolver
            self.settings = settings
            self.models = models

            # Try to import DRF components
            try:
                from rest_framework import serializers, viewsets, permissions, routers
                from rest_framework.decorators import api_view
                from rest_framework.settings import api_settings

                self.serializers = serializers
                self.viewsets = viewsets
                self.permissions = permissions
                self.routers = routers
                self.api_view = api_view
                self.api_settings = api_settings
                self.drf_available = True
                self.inspection_data['drf_available'] = True

                logger.info("Django REST Framework detected")

            except ImportError:
                self.drf_available = False
                logger.warning("Django REST Framework not available")

        except Exception as e:
            logger.error(f"Failed to import Django components: {e}")
            raise

    @contextmanager
    def _time_phase(self, phase_name: str):
        """Context manager for timing inspection phases"""
        if not self.config.timing_enabled:
            yield
            return

        start_time = time.time()
        logger.info(f"Starting {phase_name}...")

        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time

            timing = TimingData(
                phase=phase_name,
                duration=duration,
                start_time=start_time,
                end_time=end_time
            )

            self.timings.append(timing)
            self.inspection_data['timings'].append(asdict(timing))
            logger.info(f"Completed {phase_name} in {duration:.2f}s")

    def _safe_import_module(self, module_name: str) -> Optional[Any]:
        """Safely import a module with circular import protection"""
        try:
            # Check if module exists first
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return None

            return importlib.import_module(module_name)

        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            logger.debug(f"Could not import {module_name}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error importing {module_name}: {e}")
            return None

    def _is_function_based_view(self, obj) -> bool:
        """Enhanced detection of function-based views"""
        if not inspect.isfunction(obj):
            return False

        # Check for DRF decorators
        if hasattr(obj, 'cls') or hasattr(obj, 'actions'):
            return True

        # Check function signature for request parameter
        try:
            sig = inspect.signature(obj)
            params = list(sig.parameters.keys())
            if params and 'request' in params[:2]:  # request in first 2 params
                return True
        except (ValueError, TypeError):
            pass

        # Check for Django view decorators
        if hasattr(obj, '__wrapped__'):
            return self._is_function_based_view(obj.__wrapped__)

        return False

    def _get_default_permissions(self) -> List[str]:
        """Get default permission classes from settings"""
        if not self.drf_available:
            return []

        try:
            return [p.__name__ for p in self.api_settings.DEFAULT_PERMISSION_CLASSES]
        except (AttributeError, TypeError):
            return []

    def _normalize_url_pattern(self, pattern) -> str:
        """Normalize URL pattern for better readability"""
        pattern_str = str(pattern.pattern)

        # Handle regex patterns
        if hasattr(pattern.pattern, 'regex'):
            # For re_path patterns, try to get a cleaner representation
            if hasattr(pattern.pattern, 'describe') and callable(pattern.pattern.describe):
                try:
                    return pattern.pattern.describe()
                except:
                    pass
            return pattern.pattern.regex.pattern

        return pattern_str

    def inspect_models(self) -> Tuple[List[str], Dict[str, List[str]], Dict[str, Dict]]:
        """Enhanced model inspection"""
        with self._time_phase("Model Inspection"):
            models_report = []
            model_field_registry = {}
            model_metadata = {}

            apps_to_check = self.config.apps_to_inspect or []
            installed_apps = [
                app_config for app_config in self.apps.get_app_configs()
                if not apps_to_check or app_config.name.split('.')[-1] in apps_to_check
            ]

            for app_config in installed_apps:
                app_name = app_config.name.split('.')[-1]

                try:
                    app_models = app_config.get_models()
                    if not app_models:
                        continue

                    models_report.append(f"\nApp: {app_name}")
                    models_report.append("-" * 40)

                    for model in app_models:
                        model_name = model.__name__
                        model_key = f"{app_name}.{model_name}"

                        # Enhanced model metadata
                        model_info = {
                            'name': model_name,
                            'app': app_name,
                            'is_proxy': model._meta.proxy,
                            'is_managed': model._meta.managed,
                            'abstract': model._meta.abstract,
                            'db_table': model._meta.db_table,
                            'fields': [],
                            'many_to_many': [],
                            'relationships': [],
                            'indexes': [],
                            'constraints': []
                        }

                        models_report.append(f"\n  Model: {model_name}")

                        # Add metadata info
                        metadata_info = []
                        if model._meta.proxy:
                            metadata_info.append("PROXY")
                        if not model._meta.managed:
                            metadata_info.append("UNMANAGED")
                        if model._meta.abstract:
                            metadata_info.append("ABSTRACT")

                        if metadata_info:
                            models_report.append(f"    Type: {', '.join(metadata_info)}")

                        # Get all fields
                        all_fields = model._meta.get_fields()
                        model_field_registry[model_key] = []

                        for field in all_fields:
                            field_type = type(field).__name__
                            field_info = f"    - {field.name}: {field_type}"

                            field_data = {
                                'name': field.name,
                                'type': field_type,
                                'related_model': None,
                                'properties': {}
                            }

                            # Add related model info
                            if hasattr(field, 'related_model') and field.related_model:
                                related_model_name = field.related_model.__name__
                                field_info += f" -> {related_model_name}"
                                field_data['related_model'] = related_model_name
                                model_info['relationships'].append({
                                    'field': field.name,
                                    'type': field_type,
                                    'target': related_model_name
                                })

                            # Enhanced field properties
                            if self.config.detailed_view:
                                extra_info = []
                                properties = {}

                                for attr in ['null', 'blank', 'unique', 'db_index', 'primary_key']:
                                    if hasattr(field, attr):
                                        value = getattr(field, attr)
                                        if value:  # Only show True values
                                            extra_info.append(f"{attr}={value}")
                                            properties[attr] = value

                                for attr in ['max_length', 'default']:
                                    if hasattr(field, attr):
                                        value = getattr(field, attr)
                                        if value is not None:
                                            extra_info.append(f"{attr}={value}")
                                            properties[attr] = value

                                if hasattr(field, 'choices') and field.choices:
                                    choices = [choice[0] for choice in field.choices]
                                    extra_info.append(f"choices={choices}")
                                    properties['choices'] = choices

                                if extra_info:
                                    field_info += f" ({', '.join(extra_info)})"

                                field_data['properties'] = properties

                            models_report.append(field_info)
                            model_field_registry[model_key].append(field.name)
                            model_info['fields'].append(field_data)

                        # Many-to-many fields
                        m2m_fields = model._meta.many_to_many
                        if m2m_fields:
                            models_report.append("    Many-to-Many Fields:")
                            for m2m_field in m2m_fields:
                                m2m_info = f"      - {m2m_field.name}: M2M -> {m2m_field.related_model.__name__}"
                                through_model = None

                                if hasattr(m2m_field, 'through') and not m2m_field.through._meta.auto_created:
                                    through_model = m2m_field.through.__name__
                                    m2m_info += f" (through: {through_model})"

                                models_report.append(m2m_info)

                                model_info['many_to_many'].append({
                                    'name': m2m_field.name,
                                    'target': m2m_field.related_model.__name__,
                                    'through': through_model
                                })

                        # Database indexes and constraints
                        if hasattr(model._meta, 'indexes') and model._meta.indexes:
                            for index in model._meta.indexes:
                                model_info['indexes'].append({
                                    'name': getattr(index, 'name', 'unnamed'),
                                    'fields': getattr(index, 'fields', [])
                                })

                        if hasattr(model._meta, 'constraints') and model._meta.constraints:
                            for constraint in model._meta.constraints:
                                model_info['constraints'].append({
                                    'name': getattr(constraint, 'name', 'unnamed'),
                                    'type': type(constraint).__name__
                                })

                        model_metadata[model_key] = model_info
                        self.inspection_data['models'][model_key] = model_info

                except Exception as e:
                    logger.error(f"Error inspecting models in app {app_name}: {e}")
                    models_report.append(f"    Error: {str(e)}")

            return models_report, model_field_registry, model_metadata

    def inspect_views(self) -> Tuple[List[str], Dict, Dict]:
        """Enhanced view inspection with better detection"""
        with self._time_phase("View Inspection"):
            views_report = []
            view_registry = defaultdict(list)
            view_metadata = {}

            apps_to_check = self.config.apps_to_inspect or []
            installed_apps = [
                app_config for app_config in self.apps.get_app_configs()
                if not apps_to_check or app_config.name.split('.')[-1] in apps_to_check
            ]

            for app_config in installed_apps:
                app_name = app_config.name.split('.')[-1]
                views_module_name = f"{app_config.name}.views"

                views_module = self._safe_import_module(views_module_name)
                if not views_module:
                    continue

                views_report.append(f"\nApp: {app_name}")
                views_report.append("-" * 40)

                try:
                    for name, obj in inspect.getmembers(views_module):
                        view_info = {
                            'name': name,
                            'app': app_name,
                            'type': None,
                            'http_methods': [],
                            'model': None,
                            'serializer': None,
                            'permissions': [],
                            'authentication': [],
                            'throttle_classes': []
                        }

                        # Class-based views
                        if inspect.isclass(obj) and hasattr(obj, 'as_view'):
                            views_report.append(f"\n  View: {name}")
                            view_info['type'] = 'class_based'

                            # Enhanced viewset detection
                            if self.drf_available:
                                try:
                                    if issubclass(obj, self.viewsets.ViewSet):
                                        view_info['type'] = 'viewset'
                                        views_report.append(f"    Type: ViewSet")

                                        # ViewSet actions
                                        actions = []
                                        for action in ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']:
                                            if hasattr(obj, action):
                                                actions.append(action)
                                        if actions:
                                            views_report.append(f"    Actions: {', '.join(actions)}")
                                            view_info['http_methods'] = actions
                                except TypeError:
                                    # obj is not a class or issubclass failed
                                    pass

                            # HTTP methods for regular CBVs
                            for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                                if hasattr(obj, method):
                                    view_info['http_methods'].append(method.upper())

                            if view_info['http_methods']:
                                views_report.append(f"    - HTTP Methods: {', '.join(view_info['http_methods'])}")

                            # Model information
                            if hasattr(obj, 'model') and obj.model:
                                model_name = obj.model.__name__
                                views_report.append(f"    - Model: {model_name}")
                                view_info['model'] = model_name
                                view_registry[app_name].append((name, model_name))

                            if hasattr(obj, 'queryset') and obj.queryset is not None:
                                try:
                                    queryset_model = obj.queryset.model.__name__
                                    views_report.append(f"    - Queryset Model: {queryset_model}")
                                    view_info['model'] = queryset_model
                                    view_registry[app_name].append((name, queryset_model))
                                except AttributeError:
                                    pass

                            # Serializer information
                            if hasattr(obj, 'serializer_class') and obj.serializer_class:
                                serializer_name = obj.serializer_class.__name__
                                views_report.append(f"    - Serializer: {serializer_name}")
                                view_info['serializer'] = serializer_name

                            # Enhanced security information
                            if self.config.check_security and self.drf_available:
                                if hasattr(obj, 'permission_classes') and obj.permission_classes:
                                    perms = [p.__name__ for p in obj.permission_classes]
                                    views_report.append(f"    - Permissions: {', '.join(perms)}")
                                    view_info['permissions'] = perms

                                if hasattr(obj, 'authentication_classes') and obj.authentication_classes:
                                    auths = [a.__name__ for a in obj.authentication_classes]
                                    views_report.append(f"    - Authentication: {', '.join(auths)}")
                                    view_info['authentication'] = auths

                                if hasattr(obj, 'throttle_classes') and obj.throttle_classes:
                                    throttles = [t.__name__ for t in obj.throttle_classes]
                                    views_report.append(f"    - Throttles: {', '.join(throttles)}")
                                    view_info['throttle_classes'] = throttles

                        # Enhanced function-based view detection
                        elif self._is_function_based_view(obj):
                            views_report.append(f"\n  Function View: {name}")
                            view_info['type'] = 'function_based'

                            # Extract HTTP methods from @api_view decorator
                            if hasattr(obj, 'actions'):
                                methods = list(obj.actions.keys())
                                views_report.append(f"    - HTTP Methods: {', '.join(methods)}")
                                view_info['http_methods'] = methods

                        if view_info['type']:
                            view_metadata[f"{app_name}.{name}"] = view_info
                            self.inspection_data['views'][f"{app_name}.{name}"] = view_info

                except Exception as e:
                    logger.error(f"Error inspecting views in {views_module_name}: {e}")
                    views_report.append(f"    Error: {str(e)}")

            # Enhanced router detection
            if self.drf_available:
                self._inspect_routers(views_report, view_metadata, installed_apps)

            return views_report, view_registry, view_metadata

    def _inspect_routers(self, views_report: List[str], view_metadata: Dict, installed_apps):
        """Inspect DRF routers with support for all router types"""
        views_report.append(f"\n\nDRF Router Registrations:")
        views_report.append("-" * 40)

        for app_config in installed_apps:
            app_name = app_config.name.split('.')[-1]
            urls_module_name = f"{app_config.name}.urls"

            urls_module = self._safe_import_module(urls_module_name)
            if not urls_module:
                continue

            try:
                for name, obj in inspect.getmembers(urls_module):
                    # Enhanced router detection - support all router types
                    if isinstance(obj, self.routers.BaseRouter):
                        views_report.append(f"\n  Router found in {app_name} ({type(obj).__name__}):")

                        for registry_entry in obj.registry:
                            # Handle different registry tuple lengths
                            if len(registry_entry) >= 3:
                                prefix, viewset, basename = registry_entry[:3]
                                views_report.append(f"    - {prefix}/ -> {viewset.__name__} (basename: {basename})")

                                # Add to view metadata
                                router_view_key = f"{app_name}.{viewset.__name__}"
                                if router_view_key not in view_metadata:
                                    view_metadata[router_view_key] = {
                                        'name': viewset.__name__,
                                        'app': app_name,
                                        'type': 'router_registered',
                                        'router_type': type(obj).__name__,
                                        'url_prefix': prefix,
                                        'basename': basename
                                    }
                                    self.inspection_data['views'][router_view_key] = view_metadata[router_view_key]

            except Exception as e:
                logger.error(f"Error inspecting routers in {urls_module_name}: {e}")

    def inspect_serializers(self) -> Tuple[List[str], Dict[str, List[str]], Dict]:
        """Enhanced serializer inspection"""
        with self._time_phase("Serializer Inspection"):
            serializers_report = []
            serializer_field_registry = {}
            serializer_metadata = {}

            apps_to_check = self.config.apps_to_inspect or []
            installed_apps = [
                app_config for app_config in self.apps.get_app_configs()
                if not apps_to_check or app_config.name.split('.')[-1] in apps_to_check
            ]

            for app_config in installed_apps:
                app_name = app_config.name.split('.')[-1]
                serializers_module_name = f"{app_config.name}.serializers"

                serializers_module = self._safe_import_module(serializers_module_name)
                if not serializers_module:
                    continue

                serializers_report.append(f"\nApp: {app_name}")
                serializers_report.append("-" * 40)

                try:
                    for name, obj in inspect.getmembers(serializers_module):
                        if not inspect.isclass(obj):
                            continue

                        serializer_info = {
                            'name': name,
                            'app': app_name,
                            'type': None,
                            'model': None,
                            'fields': [],
                            'excluded_fields': [],
                            'explicit_fields': [],
                            'field_sources': {}
                        }

                        is_serializer = False

                        # Enhanced serializer detection with proper error handling
                        if self.drf_available:
                            try:
                                if issubclass(obj, self.serializers.BaseSerializer):
                                    is_serializer = True
                                    if issubclass(obj, self.serializers.ModelSerializer):
                                        serializer_info['type'] = 'model_serializer'
                                    else:
                                        serializer_info['type'] = 'base_serializer'
                            except TypeError:
                                # obj is not a class that can be used with issubclass
                                pass

                        # Fallback: check for Meta attribute
                        if not is_serializer and hasattr(obj, 'Meta'):
                            is_serializer = True
                            serializer_info['type'] = 'custom_serializer'

                        if is_serializer:
                            serializers_report.append(f"\n  Serializer: {name}")
                            serializers_report.append(f"    Type: {serializer_info['type']}")

                            # Model information
                            if hasattr(obj, 'Meta') and hasattr(obj.Meta, 'model'):
                                model_name = obj.Meta.model.__name__
                                serializers_report.append(f"    - Model: {model_name}")
                                serializer_info['model'] = model_name

                                # Fields information
                                if hasattr(obj.Meta, 'fields'):
                                    fields = obj.Meta.fields
                                    if fields == '__all__':
                                        serializers_report.append(f"    - Fields: All model fields")
                                        serializer_info['fields'] = '__all__'
                                    else:
                                        fields_str = ", ".join(fields)
                                        serializers_report.append(f"    - Fields: {fields_str}")
                                        serializer_info['fields'] = list(fields)
                                        serializer_field_registry[f"{app_name}.{name}"] = list(fields)

                                # Excluded fields
                                if hasattr(obj.Meta, 'exclude'):
                                    exclude_str = ", ".join(obj.Meta.exclude)
                                    serializers_report.append(f"    - Excluded: {exclude_str}")
                                    serializer_info['excluded_fields'] = list(obj.Meta.exclude)

                            # Enhanced explicit field detection with source mapping
                            explicit_fields = []
                            field_sources = {}

                            if self.drf_available:
                                try:
                                    # Create a temporary instance to get declared fields
                                    temp_instance = obj()
                                    for field_name, field_obj in temp_instance.fields.items():
                                        if hasattr(field_obj, 'source') and field_obj.source != field_name:
                                            field_sources[field_name] = field_obj.source

                                    # Get explicitly declared fields from class
                                    for field_name, field_obj in inspect.getmembers(obj):
                                        if (not field_name.startswith('_') and
                                            hasattr(field_obj, '__class__') and
                                            issubclass(field_obj.__class__, self.serializers.Field)):
                                            explicit_fields.append(field_name)

                                except Exception as e:
                                    logger.debug(f"Could not analyze fields for {name}: {e}")

                            if explicit_fields:
                                explicit_fields_str = ", ".join(explicit_fields)
                                serializers_report.append(f"    - Explicit fields: {explicit_fields_str}")
                                serializer_info['explicit_fields'] = explicit_fields

                            if field_sources:
                                sources_str = ", ".join([f"{k}->{v}" for k, v in field_sources.items()])
                                serializers_report.append(f"    - Field sources: {sources_str}")
                                serializer_info['field_sources'] = field_sources

                            # Add to registry
                            serializer_key = f"{app_name}.{name}"
                            if serializer_key in serializer_field_registry:
                                serializer_field_registry[serializer_key].extend(explicit_fields)
                            else:
                                serializer_field_registry[serializer_key] = explicit_fields

                            serializer_metadata[serializer_key] = serializer_info
                            self.inspection_data['serializers'][serializer_key] = serializer_info

                except Exception as e:
                    logger.error(f"Error inspecting serializers in {serializers_module_name}: {e}")
                    serializers_report.append(f"    Error: {str(e)}")

            return serializers_report, serializer_field_registry, serializer_metadata

    def inspect_urls(self) -> Tuple[List[str], List[Dict]]:
        """Enhanced URL inspection with namespace support"""
        with self._time_phase("URL Inspection"):
            urls_report = []
            url_patterns_data = []

            resolver = self.get_resolver()
            urls_report.append("\nURL Patterns (Enhanced):")
            urls_report.append("-" * 40)

            def extract_patterns_enhanced(resolver, prefix="", namespace="", depth=0):
                if depth > 10:  # Prevent infinite recursion
                    logger.warning(f"Maximum URL recursion depth reached at {prefix}")
                    return []

                patterns = []

                try:
                    for pattern in resolver.url_patterns:
                        normalized_pattern = self._normalize_url_pattern(pattern)
                        path = prefix + normalized_pattern
                        current_namespace = namespace

                        # Handle URL resolvers (includes)
                        if hasattr(pattern, 'url_patterns'):
                            # Check for namespace
                            pattern_namespace = getattr(pattern, 'namespace', '')
                            if pattern_namespace:
                                current_namespace = f"{namespace}:{pattern_namespace}" if namespace else pattern_namespace

                            patterns.extend(extract_patterns_enhanced(pattern, path, current_namespace, depth + 1))
                        else:
                            # Terminal URL pattern
                            view_name = ""
                            view_class = ""

                            if hasattr(pattern, 'callback'):
                                if hasattr(pattern.callback, '__name__'):
                                    view_name = pattern.callback.__name__
                                elif hasattr(pattern.callback, '__class__'):
                                    view_name = pattern.callback.__class__.__name__

                                # Try to get the actual view class for CBVs
                                if hasattr(pattern.callback, 'view_class'):
                                    view_class = pattern.callback.view_class.__name__

                            pattern_info = {
                                'path': path,
                                'view_name': view_name,
                                'view_class': view_class,
                                'namespace': current_namespace,
                                'name': getattr(pattern, 'name', ''),
                                'is_api': 'api' in path.lower(),
                                'http_methods': self._extract_http_methods_from_pattern(pattern)
                            }

                            patterns.append(pattern_info)
                            url_patterns_data.append(pattern_info)

                except Exception as e:
                    logger.error(f"Error extracting URL patterns at {prefix}: {e}")

                return patterns

            all_patterns = extract_patterns_enhanced(resolver)

            # Group and display patterns
            api_patterns = [p for p in all_patterns if p['is_api']]
            other_patterns = [p for p in all_patterns if not p['is_api']]

            if api_patterns:
                urls_report.append("\nAPI Endpoints:")
                for pattern in sorted(api_patterns, key=lambda x: x['path']):
                    namespace_info = f" (namespace: {pattern['namespace']})" if pattern['namespace'] else ""
                    name_info = f" [name: {pattern['name']}]" if pattern['name'] else ""
                    methods_info = f" [{', '.join(pattern['http_methods'])}]" if pattern['http_methods'] else ""
                    urls_report.append(f"  {pattern['path']} -> {pattern['view_name']}{methods_info}{namespace_info}{name_info}")

            # Limit other URLs to prevent huge reports
            max_other_urls = min(self.config.max_lines_per_section, len(other_patterns))
            urls_report.append(f"\nOther URLs (showing {max_other_urls} of {len(other_patterns)}):")

            for pattern in sorted(other_patterns, key=lambda x: x['path'])[:max_other_urls]:
                namespace_info = f" (namespace: {pattern['namespace']})" if pattern['namespace'] else ""
                name_info = f" [name: {pattern['name']}]" if pattern['name'] else ""
                urls_report.append(f"  {pattern['path']} -> {pattern['view_name']}{namespace_info}{name_info}")

            self.inspection_data['urls'] = url_patterns_data
            return urls_report, url_patterns_data

    def _extract_http_methods_from_pattern(self, pattern) -> List[str]:
        """Extract HTTP methods from URL pattern"""
        methods = []

        if hasattr(pattern, 'callback'):
            callback = pattern.callback

            # For class-based views
            if hasattr(callback, 'view_class'):
                view_class = callback.view_class
                for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    if hasattr(view_class, method):
                        methods.append(method.upper())

            # For function-based views with @api_view
            elif hasattr(callback, 'actions'):
                methods.extend([m.upper() for m in callback.actions.keys()])

        return methods

    def check_consistency(self, model_field_registry, serializer_field_registry, view_metadata, serializer_metadata):
        """Enhanced consistency checking with field source mapping"""
        with self._time_phase("Consistency Check"):
            consistency_report = []

            consistency_report.append("\nEnhanced Consistency Check:")
            consistency_report.append("-" * 40)

            # Model-Serializer consistency with source mapping
            consistency_report.append("\n1. Model-Serializer Field Consistency:")
            for serializer_key, serializer_fields in serializer_field_registry.items():
                app_name, serializer_name = serializer_key.split('.')

                # Use actual model from serializer metadata
                actual_model = None
                model_key = None

                if serializer_key in serializer_metadata and serializer_metadata[serializer_key]['model']:
                    actual_model = serializer_metadata[serializer_key]['model']

                    # Find the model key
                    for mk in model_field_registry.keys():
                        if mk.endswith(f".{actual_model}"):
                            model_key = mk
                            break
                else:
                    # Fallback to naming convention
                    possible_model_name = serializer_name.replace('Serializer', '')
                    model_key = f"{app_name}.{possible_model_name}"
                    actual_model = possible_model_name

                if model_key and model_key in model_field_registry:
                    model_fields = model_field_registry[model_key]
                    serializer_info = serializer_metadata.get(serializer_key, {})
                    field_sources = serializer_info.get('field_sources', {})

                    # Check for fields in serializer not in model
                    for field in serializer_fields:
                        if field in ['id', 'url']:  # Skip common auto-generated fields
                            continue

                        # Check if field maps to a different model field via source
                        target_field = field_sources.get(field, field)

                        if target_field not in model_fields:
                            issue = f"Field '{field}' in serializer '{serializer_name}' (source: '{target_field}') not found in model '{actual_model}'"
                            consistency_report.append(f"    ⚠️  {issue}")
                            self._add_issue(issue, "consistency")
                        else:
                            if field != target_field:
                                consistency_report.append(f"    ✅ Field '{field}' -> '{target_field}' mapping verified in '{serializer_name}'")

                    consistency_report.append(f"    ✅ Checked serializer '{serializer_name}' against model '{actual_model}'")
                else:
                    issue = f"Model '{actual_model}' not found for serializer '{serializer_name}'"
                    consistency_report.append(f"    ⚠️  {issue}")
                    self._add_issue(issue, "consistency")

            # View-Serializer-Model consistency
            consistency_report.append("\n2. View-Serializer-Model Consistency:")
            for view_key, view_info in view_metadata.items():
                if view_info.get('serializer') and view_info.get('model'):
                    view_serializer = view_info['serializer']
                    view_model = view_info['model']

                    # Find the serializer metadata
                    serializer_key = f"{view_info['app']}.{view_serializer}"
                    if serializer_key in serializer_metadata:
                        serializer_model = serializer_metadata[serializer_key].get('model')

                        if serializer_model and serializer_model != view_model:
                            issue = f"View '{view_info['name']}' uses model '{view_model}' but serializer '{view_serializer}' is for model '{serializer_model}'"
                            consistency_report.append(f"    ⚠️  {issue}")
                            self._add_issue(issue, "consistency")
                        else:
                            consistency_report.append(f"    ✅ View '{view_info['name']}' properly aligned with serializer and model")

            return consistency_report

    def analyze_security(self, view_metadata):
        """Enhanced security analysis"""
        with self._time_phase("Security Analysis"):
            if not (self.config.check_security and self.drf_available):
                return ["Security analysis skipped (DRF not available or disabled)"]

            security_report = []
            security_report.append("\nSecurity Analysis:")
            security_report.append("-" * 40)

            # Get default permissions from settings
            default_permissions = self._get_default_permissions()

            # Check for views without authentication/permissions
            unprotected_views = []
            weak_permissions = []

            for view_key, view_info in view_metadata.items():
                if view_info.get('type') in ['viewset', 'class_based', 'router_registered']:
                    view_permissions = view_info.get('permissions', [])
                    view_auth = view_info.get('authentication', [])

                    # Check if view has no explicit security AND no default security
                    if not view_permissions and not view_auth and not default_permissions:
                        unprotected_views.append(view_info['name'])

                    # Check for weak permissions
                    if 'AllowAny' in view_permissions:
                        weak_permissions.append({
                            'view': view_info['name'],
                            'issue': 'Uses AllowAny permission'
                        })

            # Report findings
            if default_permissions:
                security_report.append(f"✅ Default permissions configured: {', '.join(default_permissions)}")
            else:
                security_report.append("⚠️  No default permissions configured")

            if unprotected_views:
                security_report.append(f"\n⚠️  Views without explicit security ({len(unprotected_views)}):")
                for view in unprotected_views[:10]:  # Limit output
                    security_report.append(f"    - {view}")
                if len(unprotected_views) > 10:
                    security_report.append(f"    ... and {len(unprotected_views) - 10} more")

                issue = f"Found {len(unprotected_views)} views without explicit security configuration"
                self._add_issue(issue, "security")
                self.security_issues.append({
                    'type': 'unprotected_views',
                    'count': len(unprotected_views),
                    'views': unprotected_views
                })
            else:
                security_report.append("✅ All views have security configurations")

            if weak_permissions:
                security_report.append(f"\n⚠️  Views with weak permissions ({len(weak_permissions)}):")
                for item in weak_permissions:
                    security_report.append(f"    - {item['view']}: {item['issue']}")
                    self._add_issue(f"{item['view']}: {item['issue']}", "security")

            self.inspection_data['security_issues'] = self.security_issues
            return security_report

    def _add_issue(self, issue_description: str, issue_type: str = "warning"):
        """Add an issue with proper categorization"""
        issue_entry = {
            'type': issue_type,
            'description': issue_description,
            'timestamp': datetime.datetime.now().isoformat()
        }

        self.issues.append(f"{issue_type.capitalize()}: {issue_description}")

        if issue_type == "security":
            self.security_issues.append(issue_entry)
        else:
            self.inspection_data['consistency_issues'].append(issue_entry)

    def generate_summary(self):
        """Generate inspection summary"""
        summary = {
            'total_models': len(self.inspection_data['models']),
            'total_views': len(self.inspection_data['views']),
            'total_serializers': len(self.inspection_data['serializers']),
            'total_urls': len(self.inspection_data['urls']),
            'total_issues': len(self.issues),
            'consistency_issues': len(self.inspection_data['consistency_issues']),
            'security_issues': len(self.security_issues),
            'total_timing': sum(t.duration for t in self.timings),
            'apps_inspected': len(set(
                model_info['app'] for model_info in self.inspection_data['models'].values()
            ))
        }

        self.inspection_data['summary'] = summary
        return summary

    def export_html_report(self):
        """Generate HTML report"""
        if not self.config.export_html:
            return

        try:
            html_content = self._generate_html_content()

            with open(self.config.html_output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML report exported to: {self.config.html_output_file}")

        except Exception as e:
            logger.error(f"Failed to export HTML report: {e}")

    def _generate_html_content(self) -> str:
        """Generate HTML content for the report"""
        summary = self.inspection_data['summary']

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Django Inspection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .summary-item {{ text-align: center; padding: 10px; background-color: #e0e0e0; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .issue {{ color: #d32f2f; }}
                .success {{ color: #388e3c; }}
                .warning {{ color: #f57c00; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Django Inspection Report</h1>
                <p>Generated: {self.inspection_data['timestamp']}</p>
                <p>Django Version: {self.inspection_data['django_version']}</p>
                <p>DRF Available: {self.inspection_data['drf_available']}</p>
            </div>

            <div class="summary">
                <div class="summary-item">
                    <h3>{summary['total_models']}</h3>
                    <p>Models</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['total_views']}</h3>
                    <p>Views</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['total_serializers']}</h3>
                    <p>Serializers</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['total_urls']}</h3>
                    <p>URLs</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['total_issues']}</h3>
                    <p>Issues</p>
                </div>
            </div>

            <div class="section">
                <h2>Performance Timing</h2>
                <table>
                    <tr><th>Phase</th><th>Duration (s)</th></tr>
        """

        for timing in self.timings:
            html += f"<tr><td>{timing.phase}</td><td>{timing.duration:.2f}</td></tr>"

        html += f"""
                </table>
                <p>Total time: {summary['total_timing']:.2f} seconds</p>
            </div>

            <div class="section">
                <h2>Issues Summary</h2>
        """

        if self.issues:
            html += "<ul>"
            for issue in self.issues[:20]:  # Limit to first 20 issues
                css_class = "issue" if "Error" in issue else "warning"
                html += f'<li class="{css_class}">{issue}</li>'
            html += "</ul>"
            if len(self.issues) > 20:
                html += f"<p>... and {len(self.issues) - 20} more issues</p>"
        else:
            html += '<p class="success">✅ No issues detected!</p>'

        html += """
            </div>

            <div class="section">
                <h2>Raw Report</h2>
                <pre>
        """

        # Add truncated text report
        text_report = '\n'.join(self.report)
        if len(text_report) > 10000:
            text_report = text_report[:10000] + "\n\n... (truncated - see full text report for complete details)"

        html += text_report

        html += """
                </pre>
            </div>
        </body>
        </html>
        """

        return html

    def export_structured_data(self):
        """Export data to JSON and CSV formats"""
        self.inspection_data['timestamp'] = datetime.datetime.now().isoformat()

        # Export to JSON
        if self.config.export_json:
            try:
                with open(self.config.json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.inspection_data, f, indent=2, default=str)
                logger.info(f"JSON data exported to: {self.config.json_output_file}")
            except Exception as e:
                logger.error(f"Failed to export JSON: {e}")

        # Export to CSV
        if self.config.export_csv:
            try:
                with open(self.config.csv_output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)

                    # Write header
                    writer.writerow(['Component', 'App', 'Name', 'Type', 'Details', 'Issues'])

                    # Models
                    for model_key, model_info in self.inspection_data['models'].items():
                        writer.writerow([
                            'Model',
                            model_info['app'],
                            model_info['name'],
                            'Proxy' if model_info['is_proxy'] else 'Regular',
                            f"{len(model_info['fields'])} fields, {len(model_info['relationships'])} relationships",
                            ''
                        ])

                    # Views
                    for view_key, view_info in self.inspection_data['views'].items():
                        writer.writerow([
                            'View',
                            view_info['app'],
                            view_info['name'],
                            view_info['type'],
                            f"Methods: {', '.join(view_info.get('http_methods', []))}",
                            ''
                        ])

                    # Serializers
                    for ser_key, ser_info in self.inspection_data['serializers'].items():
                        writer.writerow([
                            'Serializer',
                            ser_info['app'],
                            ser_info['name'],
                            ser_info['type'],
                            f"Model: {ser_info.get('model', 'None')}",
                            ''
                        ])

                logger.info(f"CSV summary exported to: {self.config.csv_output_file}")
            except Exception as e:
                logger.error(f"Failed to export CSV: {e}")

    def add_to_report(self, section_title: str, content: Union[List[str], str]):
        """Add a section to the report"""
        self.report.append("\n" + "=" * 80)
        self.report.append(section_title)
        self.report.append("=" * 80)
        if isinstance(content, list):
            # Limit section size to prevent huge reports
            if len(content) > self.config.max_lines_per_section:
                content = content[:self.config.max_lines_per_section]
                content.append(f"... (truncated - {len(content)} total lines)")
            self.report.extend(content)
        else:
            self.report.append(content)

    def run_inspection(self):
        """Run the complete inspection process"""
        try:
            logger.info("Starting Django inspection...")

            # Add report header
            self.add_to_report("PRODUCTION DJANGO INSPECTION REPORT", [
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Django Version: {self.inspection_data['django_version']}",
                f"DRF Available: {self.inspection_data['drf_available']}",
                f"Apps to inspect: {self.config.apps_to_inspect or 'All'}",
                f"Timing enabled: {self.config.timing_enabled}"
            ])

            # Run inspections
            models_report, model_field_registry, model_metadata = self.inspect_models()
            self.add_to_report("MODELS", models_report)

            views_report, view_registry, view_metadata = self.inspect_views()
            self.add_to_report("VIEWS", views_report)

            serializers_report, serializer_field_registry, serializer_metadata = self.inspect_serializers()
            self.add_to_report("SERIALIZERS", serializers_report)

            urls_report, url_patterns_data = self.inspect_urls()
            self.add_to_report("URLS", urls_report)

            # Consistency and security checks
            consistency_report = self.check_consistency(
                model_field_registry, serializer_field_registry, view_metadata, serializer_metadata
            )
            self.add_to_report("CONSISTENCY CHECK", consistency_report)

            security_report = self.analyze_security(view_metadata)
            self.add_to_report("SECURITY ANALYSIS", security_report)

            # Performance timing report
            if self.config.timing_enabled and self.timings:
                timing_report = ["\nPerformance Timing:"]
                for timing in self.timings:
                    timing_report.append(f"  {timing.phase}: {timing.duration:.2f}s")
                total_time = sum(t.duration for t in self.timings)
                timing_report.append(f"\nTotal inspection time: {total_time:.2f}s")
                self.add_to_report("PERFORMANCE TIMING", timing_report)

            # Generate summary
            summary = self.generate_summary()
            summary_report = [
                f"Total Models: {summary['total_models']}",
                f"Total Views: {summary['total_views']}",
                f"Total Serializers: {summary['total_serializers']}",
                f"Total URLs: {summary['total_urls']}",
                f"Total Issues: {summary['total_issues']}",
                f"Apps Inspected: {summary['apps_inspected']}"
            ]
            self.add_to_report("SUMMARY", summary_report)

            # Issues summary
            if self.issues:
                self.add_to_report("ISSUES FOUND", self.issues)
            else:
                self.add_to_report("ISSUES FOUND", ["✅ No issues detected!"])

            # Recommendations
            recommendations = self._generate_recommendations()
            self.add_to_report("RECOMMENDATIONS", recommendations)

            # Write main report
            with open(self.config.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report))

            # Export structured data
            self.export_structured_data()

            # Generate HTML report
            self.export_html_report()

            # Log completion
            logger.info(f"Inspection completed successfully!")
            logger.info(f"Text report: {self.config.output_file}")
            if self.config.export_json:
                logger.info(f"JSON data: {self.config.json_output_file}")
            if self.config.export_csv:
                logger.info(f"CSV summary: {self.config.csv_output_file}")
            if self.config.export_html:
                logger.info(f"HTML report: {self.config.html_output_file}")

            # Return exit code for CI
            if self.config.exit_on_issues and len(self.issues) > self.config.issue_threshold:
                logger.error(f"Found {len(self.issues)} issues (threshold: {self.config.issue_threshold})")
                return 1

            return 0

        except Exception as e:
            logger.error(f"Inspection failed: {e}")
            import traceback
            traceback.print_exc()
            return 2

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        summary = self.inspection_data['summary']

        if summary['consistency_issues'] > 0:
            recommendations.append("🔧 Address model-serializer field mismatches")

        if summary['security_issues'] > 0:
            recommendations.append("🔒 Review and fix security configuration issues")

        if summary['total_models'] > 50:
            recommendations.append("📊 Consider using database connection pooling for large model counts")

        if summary['total_urls'] > 200:
            recommendations.append("🚀 Consider implementing URL caching or optimization")

        recommendations.extend([
            "✅ Use this report's JSON/CSV exports for automated CI checks",
            "📈 Monitor performance timing trends over time",
            "🔄 Run this inspection regularly to catch issues early",
            "📚 Keep this report updated with your codebase changes"
        ])

        return recommendations


def create_management_command():
    """Create Django management command wrapper"""
    command_code = '''
from django.core.management.base import BaseCommand
from django.core.management import CommandError
import os
import sys

class Command(BaseCommand):
    help = 'Run comprehensive Django project inspection'

    def add_arguments(self, parser):
        parser.add_argument('--apps', nargs='+', help='Specific apps to inspect')
        parser.add_argument('--output', default='inspection_report.txt', help='Output file path')
        parser.add_argument('--json', action='store_true', help='Export JSON data')
        parser.add_argument('--csv', action='store_true', help='Export CSV summary')
        parser.add_argument('--html', action='store_true', help='Export HTML report')
        parser.add_argument('--no-security', action='store_true', help='Skip security checks')
        parser.add_argument('--exit-on-issues', action='store_true', help='Exit with error code if issues found')
        parser.add_argument('--issue-threshold', type=int, default=10, help='Issue threshold for exit code')

    def handle(self, *args, **options):
        # Import here to avoid circular imports
        from .production_inspect_django import ProductionInspector, InspectionConfig

        config = InspectionConfig(
            output_file=options['output'],
            apps_to_inspect=options['apps'],
            export_json=options['json'],
            export_csv=options['csv'],
            export_html=options['html'],
            check_security=not options['no_security'],
            exit_on_issues=options['exit_on_issues'],
            issue_threshold=options['issue_threshold']
        )

        inspector = ProductionInspector(config)
        exit_code = inspector.run_inspection()

        if exit_code != 0:
            raise CommandError(f"Inspection completed with issues (exit code: {exit_code})")

        self.stdout.write(self.style.SUCCESS('Inspection completed successfully'))
'''

    # Write the management command
    management_dir = Path("management/commands")
    management_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py files
    (management_dir.parent / "__init__.py").touch()
    (management_dir / "__init__.py").touch()

    with open(management_dir / "inspect_project.py", "w") as f:
        f.write(command_code)

    print("Management command created: management/commands/inspect_project.py")
    print("Usage: python manage.py inspect_project --help")


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Production Django Project Inspector')
    parser.add_argument('--apps', nargs='+', help='Specific apps to inspect')
    parser.add_argument('--output', default='production_inspection_report.txt', help='Output file path')
    parser.add_argument('--json', action='store_true', help='Export JSON data')
    parser.add_argument('--csv', action='store_true', help='Export CSV summary')
    parser.add_argument('--html', action='store_true', help='Export HTML report')
    parser.add_argument('--no-security', action='store_true', help='Skip security checks')
    parser.add_argument('--no-timing', action='store_true', help='Disable performance timing')
    parser.add_argument('--exit-on-issues', action='store_true', help='Exit with error code if issues found')
    parser.add_argument('--issue-threshold', type=int, default=10, help='Issue threshold for exit code')
    parser.add_argument('--max-lines', type=int, default=1000, help='Max lines per report section')
    parser.add_argument('--create-command', action='store_true', help='Create Django management command')
    parser.add_argument('--config', help='Path to configuration file (JSON)')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    # Create management command if requested
    if args.create_command:
        create_management_command()
        return 0

    # Load configuration
    config = InspectionConfig()

    # Load from config file if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            logger.info(f"Configuration loaded from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return 2

    # Override with command line arguments
    if args.apps:
        config.apps_to_inspect = args.apps
    if args.output:
        config.output_file = args.output
    if args.json:
        config.export_json = True
    if args.csv:
        config.export_csv = True
    if args.html:
        config.export_html = True
    if args.no_security:
        config.check_security = False
    if args.no_timing:
        config.timing_enabled = False
    if args.exit_on_issues:
        config.exit_on_issues = True
    if args.issue_threshold:
        config.issue_threshold = args.issue_threshold
    if args.max_lines:
        config.max_lines_per_section = args.max_lines

    try:
        # Initialize and run inspector
        inspector = ProductionInspector(config)
        exit_code = inspector.run_inspection()

        if not args.quiet:
            print("\n" + "=" * 80)
            print("PRODUCTION DJANGO INSPECTION COMPLETED")
            print("=" * 80)
            print(f"Exit code: {exit_code}")
            print(f"Total issues found: {len(inspector.issues)}")
            print(f"Reports generated:")
            print(f"  • Text: {config.output_file}")
            if config.export_json:
                print(f"  • JSON: {config.json_output_file}")
            if config.export_csv:
                print(f"  • CSV: {config.csv_output_file}")
            if config.export_html:
                print(f"  • HTML: {config.html_output_file}")

            if inspector.timings:
                total_time = sum(t.duration for t in inspector.timings)
                print(f"Total inspection time: {total_time:.2f} seconds")

        return exit_code

    except KeyboardInterrupt:
        logger.info("Inspection cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Inspection failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 2


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "output_file": "django_inspection_report.txt",
        "json_output_file": "django_inspection_data.json",
        "csv_output_file": "django_inspection_summary.csv",
        "html_output_file": "django_inspection_report.html",
        "apps_to_inspect": ["core", "accounts", "api"],
        "detailed_view": True,
        "export_json": True,
        "export_csv": True,
        "export_html": True,
        "check_security": True,
        "analyze_performance": True,
        "max_lines_per_section": 1000,
        "exit_on_issues": False,
        "issue_threshold": 10,
        "timing_enabled": True
    }

    config_file = "django_inspection_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)

    print(f"Sample configuration created: {config_file}")
    print("Edit this file and use with: --config django_inspection_config.json")


def create_ci_script():
    """Create a CI-friendly script"""
    ci_script = '''#!/bin/bash
# CI Script for Django Inspection
# Usage: ./django_inspection_ci.sh

set -e  # Exit on any error

echo "Starting Django project inspection..."

# Run inspection with CI-friendly options
python production_inspect_django.py \\
    --json \\
    --csv \\
    --exit-on-issues \\
    --issue-threshold 5 \\
    --quiet \\
    --output "ci_inspection_report.txt"

# Check if reports were generated
if [ ! -f "inspection_data.json" ]; then
    echo "ERROR: JSON report not generated"
    exit 1
fi

# Extract key metrics
TOTAL_ISSUES=$(python -c "import json; data=json.load(open('inspection_data.json')); print(data['summary']['total_issues'])")
SECURITY_ISSUES=$(python -c "import json; data=json.load(open('inspection_data.json')); print(len(data['security_issues']))")

echo "Inspection completed:"
echo "  Total issues: $TOTAL_ISSUES"
echo "  Security issues: $SECURITY_ISSUES"

# Fail if too many issues
if [ "$TOTAL_ISSUES" -gt 10 ]; then
    echo "ERROR: Too many issues found ($TOTAL_ISSUES > 10)"
    exit 1
fi

if [ "$SECURITY_ISSUES" -gt 0 ]; then
    echo "ERROR: Security issues found ($SECURITY_ISSUES)"
    exit 1
fi

echo "✅ Inspection passed - no critical issues found"
'''

    with open("django_inspection_ci.sh", "w") as f:
        f.write(ci_script)

    # Make executable
    os.chmod("django_inspection_ci.sh", 0o755)

    print("CI script created: django_inspection_ci.sh")
    print("Usage: ./django_inspection_ci.sh")


def create_pre_commit_hook():
    """Create a pre-commit hook"""
    hook_script = '''#!/bin/bash
# Pre-commit hook for Django inspection
# Only inspect modified apps

# Get list of modified Python files
MODIFIED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\\.py$" || true)

if [ -z "$MODIFIED_FILES" ]; then
    echo "No Python files modified, skipping inspection"
    exit 0
fi

# Extract app names from modified files
MODIFIED_APPS=$(echo "$MODIFIED_FILES" | cut -d'/' -f1 | sort -u | tr '\\n' ' ')

echo "Running Django inspection on modified apps: $MODIFIED_APPS"

# Run inspection on only modified apps
python production_inspect_django.py \\
    --apps $MODIFIED_APPS \\
    --exit-on-issues \\
    --issue-threshold 0 \\
    --output "pre_commit_inspection.txt"

if [ $? -ne 0 ]; then
    echo "❌ Django inspection failed - commit blocked"
    echo "Review pre_commit_inspection.txt for details"
    exit 1
fi

echo "✅ Django inspection passed"
exit 0
'''

    # Create .git/hooks directory if it doesn't exist
    hooks_dir = ".git/hooks"
    if os.path.exists(".git") and not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)

    hook_file = os.path.join(hooks_dir, "pre-commit")
    with open(hook_file, "w") as f:
        f.write(hook_script)

    # Make executable
    os.chmod(hook_file, 0o755)

    print(f"Pre-commit hook created: {hook_file}")
    print("This will run inspection on modified apps before each commit")


if __name__ == "__main__":
    print("=" * 80)
    print("PRODUCTION DJANGO INSPECTION TOOL")
    print("=" * 80)
    print("Enhanced version with:")
    print("• Comprehensive edge-case handling")
    print("• Performance timing and optimization")
    print("• Security analysis and recommendations")
    print("• Multiple export formats (TXT/JSON/CSV/HTML)")
    print("• CI/CD integration support")
    print("• Django management command generation")
    print("• Pre-commit hook support")
    print()

    # Check if user wants to create additional files
    if len(sys.argv) == 1:
        print("Available setup options:")
        print("  --create-command    : Create Django management command")
        print("  python -c 'from production_inspect_django import create_sample_config; create_sample_config()'")
        print("  python -c 'from production_inspect_django import create_ci_script; create_ci_script()'")
        print("  python -c 'from production_inspect_django import create_pre_commit_hook; create_pre_commit_hook()'")
        print()
        print("Run with --help for all options")
        print()

    exit_code = main()
    sys.exit(exit_code)
