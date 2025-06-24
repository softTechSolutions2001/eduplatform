# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializer Inspector for Django REST Framework

This module analyzes Django REST Framework serializers to extract field information,
validation rules, and nested relationships.

Author: nanthiniSanthanam
Generated: 2025-05-04 05:04:05
"""

import inspect
import logging
import importlib
import pkgutil
import sys
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

# Try to import DRF
try:
    from rest_framework import serializers
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

logger = logging.getLogger(__name__)


class SerializerInspector:
    """Extract information about Django REST Framework serializers"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

        # Cache of discovered serializer classes
        self.serializer_classes = {}

    def extract(self) -> Dict[str, Any]:
        """Extract serializer information from the Django project"""
        logger.info("Extracting serializer information")

        if not DRF_AVAILABLE:
            logger.warning("Django REST Framework not found, skipping serializer extraction")
            return {}

        # Discover serializers in the project
        self._discover_serializers()

        # Extract information from each serializer
        serializer_info = {}
        for module_name, serializers_in_module in self.serializer_classes.items():
            module_info = {}

            for serializer_name, serializer_class in serializers_in_module.items():
                try:
                    class_info = self._extract_serializer_class(serializer_class)
                    module_info[serializer_name] = class_info
                except Exception as e:
                    logger.error(f"Error extracting info from {serializer_name}: {str(e)}")

            if module_info:
                serializer_info[module_name] = module_info

        logger.info(f"Extracted information for {len(self.serializer_classes)} serializer modules")
        return {
            'modules': serializer_info,
            'count': sum(len(classes) for classes in self.serializer_classes.values()),
        }

    def _discover_serializers(self):
        """Discover serializers in Django apps by searching for subclasses"""
        from django.apps import apps

        # Get all Django apps
        app_configs = apps.get_app_configs()

        # Filter apps based on configuration
        if self.config.INCLUDED_APPS:
            app_configs = [app for app in app_configs 
                          if app.name in self.config.INCLUDED_APPS]

        # Apply exclusions
        app_configs = [app for app in app_configs 
                      if app.name not in self.config.EXCLUDED_APPS]

        # Look for serializers in each app
        for app_config in app_configs:
            app_path = Path(app_config.path)
            logger.debug(f"Searching for serializers in {app_config.name}")

            # Check common serializer module naming patterns
            for serializer_module_name in ['serializers', 'api/serializers', 'api']:
                module_path = app_path / serializer_module_name
                if module_path.is_dir() and (module_path / '__init__.py').exists():
                    # This is a Python package
                    self._find_serializers_in_package(
                        f"{app_config.name}.{serializer_module_name.replace('/', '.')}"
                    )
                elif (module_path.parent / (module_path.name + '.py')).exists():
                    # This is a Python module
                    self._find_serializers_in_module(
                        f"{app_config.name}.{serializer_module_name.replace('/', '.')}"
                    )

    def _find_serializers_in_package(self, package_name: str):
        """Find serializers in a Python package"""
        try:
            package = importlib.import_module(package_name)

            # Get all modules in the package
            for _, modname, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                if ispkg:
                    # Recursively search subpackages
                    self._find_serializers_in_package(modname)
                else:
                    # Search this module
                    self._find_serializers_in_module(modname)
        except ImportError as e:
            logger.debug(f"Could not import package {package_name}: {str(e)}")

    def _find_serializers_in_module(self, module_name: str):
        """Find serializers in a Python module"""
        try:
            module = importlib.import_module(module_name)

            # Find all serializer classes in the module
            serializer_classes = {}
            for name, obj in inspect.getmembers(module):
                # Check if this is a serializer class
                if (inspect.isclass(obj) and
                    hasattr(obj, '__module__') and
                    obj.__module__ == module_name and
                    self._is_serializer_class(obj)):

                    serializer_classes[name] = obj

            if serializer_classes:
                self.serializer_classes[module_name] = serializer_classes
                logger.debug(f"Found {len(serializer_classes)} serializers in {module_name}")
        except ImportError as e:
            logger.debug(f"Could not import module {module_name}: {str(e)}")

    def _is_serializer_class(self, cls) -> bool:
        """Check if a class is a DRF serializer"""
        if not DRF_AVAILABLE:
            return False

        # Check if this is a direct subclass of a DRF serializer
        if hasattr(cls, '__bases__'):
            for base in cls.__bases__:
                if base.__module__.startswith('rest_framework.') and 'serializer' in base.__name__.lower():
                    return True

        # Check if this inherits from serializers.Serializer or serializers.ModelSerializer
        if DRF_AVAILABLE:
            return (issubclass(cls, serializers.Serializer) and 
                   cls is not serializers.Serializer and 
                   cls is not serializers.ModelSerializer)

        return False

    def _extract_serializer_class(self, serializer_class) -> Dict[str, Any]:
        """Extract information from a serializer class"""
        class_info = {
            'name': serializer_class.__name__,
            'module': serializer_class.__module__,
            'docstring': inspect.getdoc(serializer_class) or '',
            'is_model_serializer': self._is_model_serializer(serializer_class),
            'fields': {},
            'meta': self._extract_meta_options(serializer_class),
        }

        # Try to instantiate the serializer to get field info
        try:
            serializer = serializer_class()
            class_info['fields'] = self._extract_serializer_fields(serializer)
        except Exception as e:
            logger.debug(f"Could not instantiate {serializer_class.__name__}: {str(e)}")
            # Try to extract fields from class definition
            class_info['fields'] = self._extract_static_serializer_fields(serializer_class)

        # Extract validation methods
        class_info['validation_methods'] = self._extract_validation_methods(serializer_class)

        # Add model information for ModelSerializers
        if class_info['is_model_serializer']:
            model_info = self._extract_model_info(serializer_class)
            if model_info:
                class_info['model'] = model_info

        return class_info

    def _is_model_serializer(self, serializer_class) -> bool:
        """Check if a serializer is a ModelSerializer"""
        if not DRF_AVAILABLE:
            return False

        return issubclass(serializer_class, serializers.ModelSerializer)

    def _extract_meta_options(self, serializer_class) -> Dict[str, Any]:
        """Extract Meta options from a serializer class"""
        meta_options = {}

        # Check if the serializer has a Meta class
        if hasattr(serializer_class, 'Meta'):
            meta = serializer_class.Meta

            # Extract common Meta attributes
            if hasattr(meta, 'model'):
                meta_options['model'] = meta.model.__name__
                meta_options['model_module'] = meta.model.__module__

            if hasattr(meta, 'fields'):
                meta_options['fields'] = list(meta.fields) if meta.fields != '__all__' else '__all__'

            if hasattr(meta, 'exclude'):
                meta_options['exclude'] = list(meta.exclude)

            if hasattr(meta, 'read_only_fields'):
                meta_options['read_only_fields'] = list(meta.read_only_fields)

            if hasattr(meta, 'extra_kwargs'):
                meta_options['extra_kwargs'] = meta.extra_kwargs

            if hasattr(meta, 'depth'):
                meta_options['depth'] = meta.depth

        return meta_options

    def _extract_serializer_fields(self, serializer) -> Dict[str, Any]:
        """Extract field information from an instantiated serializer"""
        fields = {}

        for field_name, field in serializer.fields.items():
            field_info = {
                'type': field.__class__.__name__,
                'module': field.__class__.__module__,
                'required': getattr(field, 'required', False),
                'read_only': getattr(field, 'read_only', False),
                'write_only': getattr(field, 'write_only', False),
                'allow_null': getattr(field, 'allow_null', False),
                'default': self._get_field_default(field),
            }

            # Add help text if available
            if hasattr(field, 'help_text') and field.help_text:
                field_info['help_text'] = str(field.help_text)

            # Add label if available
            if hasattr(field, 'label') and field.label:
                field_info['label'] = str(field.label)

            # Add validators
            if hasattr(field, 'validators') and field.validators:
                field_info['validators'] = self._extract_validators(field.validators)

            # Handle nested serializers
            if hasattr(field, 'child') and field.child:
                field_info['child'] = {
                    'type': field.child.__class__.__name__,
                    'module': field.child.__class__.__module__,
                }

                # If the child is a serializer, try to extract its fields
                if isinstance(field.child, serializers.Serializer):
                    try:
                        field_info['child']['fields'] = self._extract_serializer_fields(field.child)
                    except Exception as e:
                        logger.debug(f"Could not extract child serializer fields: {str(e)}")

            # Handle explicitly defined serializer fields
            if isinstance(field, serializers.Serializer) or isinstance(field, serializers.ListSerializer):
                try:
                    field_info['fields'] = self._extract_serializer_fields(field)
                except Exception as e:
                    logger.debug(f"Could not extract nested serializer fields: {str(e)}")

            fields[field_name] = field_info

        return fields

    def _extract_static_serializer_fields(self, serializer_class) -> Dict[str, Any]:
        """Extract field information from a serializer class definition"""
        fields = {}

        # Inspect class attributes
        for name, attr in inspect.getmembers(serializer_class):
            # Skip special attributes, methods, and non-field attributes
            if (name.startswith('_') or inspect.ismethod(attr) or inspect.isfunction(attr) or
                not hasattr(attr, '__class__') or not DRF_AVAILABLE):
                continue

            # Check if this is a serializer field
            is_serializer_field = (
                hasattr(attr, '__class__') and 
                issubclass(attr.__class__, serializers.Field)
            )

            if is_serializer_field:
                field_info = {
                    'type': attr.__class__.__name__,
                    'module': attr.__class__.__module__,
                    'required': getattr(attr, 'required', False),
                    'read_only': getattr(attr, 'read_only', False),
                    'write_only': getattr(attr, 'write_only', False),
                    'allow_null': getattr(attr, 'allow_null', False),
                    'default': self._get_field_default(attr),
                }

                fields[name] = field_info

        return fields

    def _get_field_default(self, field):
        """Get the default value of a field"""
        if hasattr(field, 'default'):
            default = field.default

            # Handle callable defaults
            if callable(default) and default != serializers.empty:
                return f"{default.__module__}.{default.__name__}()"

            # Handle empty default
            if default == serializers.empty:
                return None

            return str(default)

        return None

    def _extract_validators(self, validators) -> List[Dict[str, Any]]:
        """Extract information about field validators"""
        result = []

        for validator in validators:
            validator_info = {
                'class': validator.__class__.__name__,
                'module': validator.__class__.__module__,
            }

            # Extract common validator attributes
            if hasattr(validator, 'message'):
                validator_info['message'] = str(validator.message)

            if hasattr(validator, 'code'):
                validator_info['code'] = validator.code

            # Extract specific validator attributes based on type
            if validator.__class__.__name__ == 'MinValueValidator':
                validator_info['min_value'] = validator.limit_value

            elif validator.__class__.__name__ == 'MaxValueValidator':
                validator_info['max_value'] = validator.limit_value

            elif validator.__class__.__name__ == 'MinLengthValidator':
                validator_info['min_length'] = validator.limit_value

            elif validator.__class__.__name__ == 'MaxLengthValidator':
                validator_info['max_length'] = validator.limit_value

            elif validator.__class__.__name__ == 'RegexValidator':
                validator_info['regex'] = str(validator.regex.pattern)

            result.append(validator_info)

        return result

    def _extract_validation_methods(self, serializer_class) -> List[Dict[str, Any]]:
        """Extract validation methods from a serializer class"""
        validation_methods = []

        # Check for common validation methods
        validation_prefixes = ['validate_', 'validate']

        for name, method in inspect.getmembers(serializer_class, predicate=inspect.isfunction):
            # Check if this is a validate method
            is_validate_method = name == 'validate' or name.startswith('validate_')

            if is_validate_method:
                validation_methods.append({
                    'name': name,
                    'docstring': inspect.getdoc(method) or '',
                    'parameters': [p.name for p in inspect.signature(method).parameters.values()
                                 if p.name != 'self'],
                })

        return validation_methods

    def _extract_model_info(self, serializer_class) -> Optional[Dict[str, Any]]:
        """Extract model information from a ModelSerializer"""
        if not hasattr(serializer_class, 'Meta') or not hasattr(serializer_class.Meta, 'model'):
            return None

        model = serializer_class.Meta.model

        model_info = {
            'name': model.__name__,
            'module': model.__module__,
            'app_label': model._meta.app_label,
        }

        return model_info