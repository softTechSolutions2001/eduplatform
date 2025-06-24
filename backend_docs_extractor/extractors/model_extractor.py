# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django Model Extractor

This module extracts comprehensive information about Django models,
including fields, relationships, constraints, and more.

Author: nanthiniSanthanam
Generated: 2025-05-04 04:56:14
"""

import inspect
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from django.apps import apps
from django.db import models
from django.db.models import Field, ManyToManyField, ForeignKey, OneToOneField
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.db.models.constraints import BaseConstraint

logger = logging.getLogger(__name__)

class ModelExtractor:
    """Extract information about Django models"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

        # Get all apps to analyze
        self.apps_to_analyze = self._get_apps_to_analyze()

    def _get_apps_to_analyze(self) -> List[str]:
        """Get a list of apps to analyze based on configuration"""
        all_app_configs = apps.get_app_configs()

        if self.config.INCLUDED_APPS:
            app_configs = [app for app in all_app_configs 
                          if app.name in self.config.INCLUDED_APPS]
        else:
            app_configs = all_app_configs

        # Apply exclusions
        app_configs = [app for app in app_configs 
                      if app.name not in self.config.EXCLUDED_APPS]

        return [app.name for app in app_configs]

    def extract(self) -> Dict[str, Any]:
        """Extract model information from all configured apps"""
        logger.info("Extracting model information")

        result = {}

        for app_label in self.apps_to_analyze:
            app_models = {}

            try:
                app_config = apps.get_app_config(app_label.split('.')[-1])

                for model in app_config.get_models():
                    model_info = self._extract_model_info(model)
                    app_models[model.__name__] = model_info

                if app_models:
                    result[app_label] = {
                        'models': app_models,
                        'app_config': {
                            'name': app_config.name,
                            'label': app_config.label,
                            'path': str(Path(app_config.path)),
                        }
                    }
            except Exception as e:
                logger.error(f"Error extracting models for app {app_label}: {str(e)}")

        # Add relationships between models
        self._add_cross_model_relationships(result)

        logger.info(f"Extracted information for {len(result)} apps")
        return result

    def _extract_model_info(self, model_class) -> Dict[str, Any]:
        """Extract detailed information about a single model"""
        model_info = {
            'name': model_class.__name__,
            'table_name': model_class._meta.db_table,
            'app_label': model_class._meta.app_label,
            'verbose_name': str(model_class._meta.verbose_name),
            'verbose_name_plural': str(model_class._meta.verbose_name_plural),
            'fields': {},
            'relationships': {
                'foreign_keys': [],
                'many_to_many': [],
                'one_to_one': [],
                'reverse_relations': [],
            },
            'meta_options': self._extract_meta_options(model_class),
            'constraints': self._extract_constraints(model_class),
            'indexes': self._extract_indexes(model_class),
            'managers': self._extract_managers(model_class),
            'model_methods': self._extract_model_methods(model_class),
        }

        # Extract fields
        for field in model_class._meta.get_fields():
            if isinstance(field, ForeignKey):
                model_info['relationships']['foreign_keys'].append(
                    self._extract_foreign_key_info(field)
                )
            elif isinstance(field, ManyToManyField):
                model_info['relationships']['many_to_many'].append(
                    self._extract_many_to_many_info(field)
                )
            elif isinstance(field, OneToOneField):
                model_info['relationships']['one_to_one'].append(
                    self._extract_one_to_one_info(field)
                )
            elif isinstance(field, ForeignObjectRel):
                model_info['relationships']['reverse_relations'].append(
                    self._extract_reverse_relation_info(field)
                )
            else:
                # Regular field
                field_info = self._extract_field_info(field)
                model_info['fields'][field.name] = field_info

        # Extract custom properties if comprehensive detail level
        if self.detail_level == "comprehensive":
            model_info['properties'] = self._extract_properties(model_class)

            # Extract validation methods
            model_info['validation_methods'] = self._extract_validation_methods(model_class)

            # Extract field validation
            for field_name, field_info in model_info['fields'].items():
                field = model_class._meta.get_field(field_name)
                field_info['validators'] = self._extract_field_validators(field)

        return model_info

    def _extract_field_info(self, field) -> Dict[str, Any]:
        """Extract information about a regular model field"""
        field_info = {
            'name': field.name,
            'type': field.__class__.__name__,
            'module': field.__class__.__module__,
            'verbose_name': str(field.verbose_name),
            'help_text': str(field.help_text),
            'primary_key': field.primary_key,
            'unique': field.unique,
            'blank': field.blank,
            'null': field.null,
            'default': self._get_default_value(field),
            'editable': field.editable,
            'choices': self._extract_choices(field),
        }

        # Add field-specific attributes
        if hasattr(field, 'max_length'):
            field_info['max_length'] = field.max_length

        if field.__class__.__name__ == 'DecimalField':
            field_info['max_digits'] = field.max_digits
            field_info['decimal_places'] = field.decimal_places

        return field_info

    def _extract_foreign_key_info(self, field) -> Dict[str, Any]:
        """Extract information about a ForeignKey field"""
        return {
            'name': field.name,
            'type': 'ForeignKey',
            'target_model': field.related_model.__name__,
            'target_app': field.related_model._meta.app_label,
            'on_delete': field.remote_field.on_delete.__name__,
            'related_name': field.remote_field.related_name or '',
            'related_query_name': field.remote_field.related_query_name or '',
            'db_constraint': field.remote_field.db_constraint,
            'null': field.null,
            'blank': field.blank,
            'verbose_name': str(field.verbose_name),
            'help_text': str(field.help_text),
        }

    def _extract_many_to_many_info(self, field) -> Dict[str, Any]:
        """Extract information about a ManyToManyField"""
        return {
            'name': field.name,
            'type': 'ManyToManyField',
            'target_model': field.related_model.__name__,
            'target_app': field.related_model._meta.app_label,
            'related_name': field.remote_field.related_name or '',
            'related_query_name': field.remote_field.related_query_name or '',
            'through': field.remote_field.through._meta.object_name if field.remote_field.through else None,
            'through_app': field.remote_field.through._meta.app_label if field.remote_field.through else None,
            'symmetrical': getattr(field.remote_field, 'symmetrical', False),
            'verbose_name': str(field.verbose_name),
            'help_text': str(field.help_text),
        }

    def _extract_one_to_one_info(self, field) -> Dict[str, Any]:
        """Extract information about a OneToOneField"""
        return {
            'name': field.name,
            'type': 'OneToOneField',
            'target_model': field.related_model.__name__,
            'target_app': field.related_model._meta.app_label,
            'on_delete': field.remote_field.on_delete.__name__,
            'related_name': field.remote_field.related_name or '',
            'parent_link': field.remote_field.parent_link,
            'null': field.null,
            'blank': field.blank,
            'verbose_name': str(field.verbose_name),
            'help_text': str(field.help_text),
        }

    def _extract_reverse_relation_info(self, field) -> Dict[str, Any]:
        """Extract information about a reverse relation"""
        return {
            'name': field.name,
            'type': 'ReverseRelation',
            'related_model': field.related_model.__name__,
            'related_app': field.related_model._meta.app_label,
            'field_name': field.field.name,
            'multiple': field.multiple,
        }

    def _extract_meta_options(self, model_class) -> Dict[str, Any]:
        """Extract Meta options from a model"""
        meta = model_class._meta

        meta_options = {
            'abstract': meta.abstract,
            'app_label': meta.app_label,
            'db_table': meta.db_table,
            'db_tablespace': meta.db_tablespace,
            'managed': meta.managed,
            'ordering': meta.ordering or [],
            'permissions': [(p[0], str(p[1])) for p in meta.permissions],
            'default_permissions': list(meta.default_permissions),
            'proxy': meta.proxy,
            'verbose_name': str(meta.verbose_name),
            'verbose_name_plural': str(meta.verbose_name_plural),
            'unique_together': [list(ut) for ut in meta.unique_together],
        }

        # Add index_together if available
        if hasattr(meta, 'index_together'):
            meta_options['index_together'] = [list(it) for it in meta.index_together]

        return meta_options

    def _extract_constraints(self, model_class) -> List[Dict[str, Any]]:
        """Extract constraints from a model"""
        constraints = []

        for constraint in model_class._meta.constraints:
            constraint_info = {
                'name': constraint.name,
                'type': constraint.__class__.__name__,
            }

            # Extract specific constraint information based on type
            if hasattr(constraint, 'fields'):
                constraint_info['fields'] = list(constraint.fields)

            if hasattr(constraint, 'condition'):
                constraint_info['condition'] = str(constraint.condition)

            constraints.append(constraint_info)

        return constraints

    def _extract_indexes(self, model_class) -> List[Dict[str, Any]]:
        """Extract indexes from a model"""
        indexes = []

        for index in model_class._meta.indexes:
            index_info = {
                'name': index.name,
                'fields': list(index.fields),
            }

            # Extract additional index properties
            if hasattr(index, 'unique'):
                index_info['unique'] = index.unique

            if hasattr(index, 'db_tablespace'):
                index_info['db_tablespace'] = index.db_tablespace

            indexes.append(index_info)

        return indexes

    def _extract_managers(self, model_class) -> List[str]:
        """Extract custom managers from a model"""
        managers = []

        for manager_name, manager_instance in model_class._meta.managers_map.items():
            # Only include non-default managers
            if manager_name != 'objects' or manager_instance.__class__ != models.Manager:
                managers.append({
                    'name': manager_name,
                    'class': manager_instance.__class__.__name__,
                    'module': manager_instance.__class__.__module__,
                })

        return managers

    def _extract_model_methods(self, model_class) -> List[Dict[str, Any]]:
        """Extract non-private methods defined on the model"""
        methods = []

        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            # Skip private methods and methods inherited from models.Model
            if (not name.startswith('_') and 
                method.__qualname__.startswith(model_class.__name__) and
                not hasattr(models.Model, name)):

                method_info = {
                    'name': name,
                    'docstring': inspect.getdoc(method) or '',
                    'parameters': [p.name for p in inspect.signature(method).parameters.values()
                                  if p.name != 'self'],
                }
                methods.append(method_info)

        return methods

    def _extract_properties(self, model_class) -> List[Dict[str, Any]]:
        """Extract properties defined on the model"""
        properties = []

        for name, prop in inspect.getmembers(model_class, lambda o: isinstance(o, property)):
            if not name.startswith('_'):
                property_info = {
                    'name': name,
                    'docstring': inspect.getdoc(prop) or '',
                    'has_getter': prop.fget is not None,
                    'has_setter': prop.fset is not None,
                    'has_deleter': prop.fdel is not None,
                }
                properties.append(property_info)

        return properties

    def _extract_validation_methods(self, model_class) -> List[Dict[str, Any]]:
        """Extract validation methods from the model"""
        validation_methods = []

        # Check for common validation methods
        for method_name in ['clean', 'clean_fields', 'validate_unique', 'full_clean']:
            if hasattr(model_class, method_name):
                method = getattr(model_class, method_name)

                # Only include if it's not the default implementation from models.Model
                if method.__qualname__.startswith(model_class.__name__):
                    validation_methods.append({
                        'name': method_name,
                        'docstring': inspect.getdoc(method) or '',
                    })

        return validation_methods

    def _extract_field_validators(self, field) -> List[Dict[str, Any]]:
        """Extract validators from a field"""
        validators = []

        for validator in field.validators:
            validator_info = {
                'class': validator.__class__.__name__,
                'module': validator.__class__.__module__,
            }

            # Extract common validator attributes
            if hasattr(validator, 'limit_value'):
                validator_info['limit_value'] = validator.limit_value

            if hasattr(validator, 'message'):
                validator_info['message'] = str(validator.message)

            validators.append(validator_info)

        return validators

    def _extract_choices(self, field) -> List[Dict[str, Any]]:
        """Extract choices from a field"""
        result = []

        if field.choices:
            for value, label in field.choices:
                # Handle grouped choices
                if isinstance(label, (list, tuple)):
                    group_name = value
                    choices = []
                    for choice_value, choice_label in label:
                        choices.append({
                            'value': choice_value,
                            'label': str(choice_label)
                        })
                    result.append({
                        'group': str(group_name),
                        'choices': choices
                    })
                else:
                    result.append({
                        'value': value,
                        'label': str(label)
                    })

        return result

    def _get_default_value(self, field):
        """Get string representation of a field's default value"""
        if field.has_default():
            default = field.default

            # Handle callables like datetime.now
            if callable(default):
                return f"{default.__module__}.{default.__name__}()"

            return repr(default)

        return None

    def _add_cross_model_relationships(self, extracted_models):
        """Add cross-references between models for complex relationships"""
        # This adds bi-directional relationships to help frontend understand model connections

        # Build a map of all models
        model_map = {}
        for app_label, app_info in extracted_models.items():
            for model_name, model_info in app_info['models'].items():
                model_map[f"{app_label}.{model_name}"] = model_info

        # Now add cross-references
        for app_label, app_info in extracted_models.items():
            for model_name, model_info in app_info['models'].items():
                model_key = f"{app_label}.{model_name}"

                # Process foreign keys
                for fk in model_info['relationships']['foreign_keys']:
                    target_key = f"{fk['target_app']}.{fk['target_model']}"
                    if target_key in model_map:
                        # Add entry to model_references if it doesn't exist
                        if 'model_references' not in model_map[target_key]:
                            model_map[target_key]['model_references'] = []

                        model_map[target_key]['model_references'].append({
                            'type': 'foreign_key',
                            'from_model': model_name,
                            'from_app': app_label,
                            'field_name': fk['name'],
                            'related_name': fk['related_name']
                        })

                # Process many-to-many
                for m2m in model_info['relationships']['many_to_many']:
                    target_key = f"{m2m['target_app']}.{m2m['target_model']}"
                    if target_key in model_map:
                        # Add entry to model_references if it doesn't exist
                        if 'model_references' not in model_map[target_key]:
                            model_map[target_key]['model_references'] = []

                        model_map[target_key]['model_references'].append({
                            'type': 'many_to_many',
                            'from_model': model_name,
                            'from_app': app_label,
                            'field_name': m2m['name'],
                            'related_name': m2m['related_name']
                        })