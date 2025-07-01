#!/usr/bin/env python3
"""
Django Model Inspector - Comprehensive schema analysis tool
Addresses all dataclass ordering issues, mutable defaults, field coverage gaps, and Unicode encoding.
Generates clean markdown output with full relationship mapping.
"""

import os
import sys
import hashlib
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path

import django
from django.apps import apps
from django.db import models
from django.db.models import Field
from django.db.models.fields import related
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.management.base import BaseCommand


@dataclass
class FieldInfo:
    """Fixed dataclass with proper ordering and default factories"""
    # Basic field info (no defaults)
    name: str
    type: str
    db_column: str
    null: bool
    blank: bool
    primary_key: bool
    unique: bool
    db_index: bool
    editable: bool
    auto_created: bool
    concrete: bool

    # Fields with defaults (must come after non-default fields)
    default: Any = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    max_value: Optional[Union[int, float]] = None
    min_value: Optional[Union[int, float]] = None
    decimal_places: Optional[int] = None
    max_digits: Optional[int] = None
    auto_now: bool = False
    auto_now_add: bool = False
    upload_to: Optional[str] = None
    storage: Optional[str] = None

    # Calendar uniqueness constraints
    unique_for_date: bool = False
    unique_for_month: bool = False
    unique_for_year: bool = False

    # Relationship specific
    related_model: Optional[str] = None
    on_delete: Optional[str] = None
    to_field: Optional[str] = None
    related_name: Optional[str] = None
    related_query_name: Optional[str] = None
    through: Optional[str] = None
    symmetrical: Optional[bool] = None
    db_constraint: Optional[bool] = None
    limit_choices_to: Any = None
    queryset_class: Optional[str] = None

    # Generic FK/Relation specific
    content_type_field: Optional[str] = None
    object_id_field: Optional[str] = None
    fk_field: Optional[str] = None

    # Use field() with default_factory for mutable defaults
    validators: List[str] = field(default_factory=list)
    choices: List[tuple] = field(default_factory=list)


@dataclass
class ConstraintInfo:
    name: Optional[str]
    type: str
    fields: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    deferrable: bool = False


@dataclass
class IndexInfo:
    name: Optional[str]
    fields: List[str] = field(default_factory=list)
    unique: bool = False
    partial: bool = False
    condition: Optional[str] = None
    opclasses: List[str] = field(default_factory=list)


@dataclass
class ManagerInfo:
    name: str
    class_name: str
    module: str
    is_default: bool
    is_base: bool


@dataclass
class ModelInfo:
    """Fixed dataclass with proper ordering"""
    # Basic info (no defaults)
    name: str
    app_label: str
    module: str
    label: str
    label_lower: str
    db_table: str
    abstract: bool
    proxy: bool
    managed: bool
    verbose_name: str
    verbose_name_plural: str

    # Fields with defaults
    ordering: List[str] = field(default_factory=list)
    default_permissions: List[str] = field(default_factory=list)
    permissions: List[tuple] = field(default_factory=list)
    get_latest_by: Optional[str] = None
    default_related_name: Optional[str] = None
    db_tablespace: Optional[str] = None
    required_db_vendor: Optional[str] = None
    required_db_features: List[str] = field(default_factory=list)
    db_table_comment: Optional[str] = None

    # Structure
    fields: List[FieldInfo] = field(default_factory=list)
    constraints: List[ConstraintInfo] = field(default_factory=list)
    indexes: List[IndexInfo] = field(default_factory=list)
    managers: List[ManagerInfo] = field(default_factory=list)
    mro: List[str] = field(default_factory=list)

    # Validation flags
    duplicate_columns: List[str] = field(default_factory=list)
    duplicate_db_table: bool = False


class DjangoModelInspector:
    def __init__(self, include_django_apps=False, exclude_apps=None):
        self.include_django_apps = include_django_apps
        self.exclude_apps = set(exclude_apps or [])
        self.models_info = []
        self.table_collisions = defaultdict(list)

    def get_models(self):
        """Get all models based on configuration with full coverage"""
        all_models = apps.get_models(
            include_auto_created=True,
            include_swapped=True
        )

        filtered_models = []
        for model in all_models:
            app_label = model._meta.app_label

            # Skip excluded apps
            if app_label in self.exclude_apps:
                continue

            # Skip Django apps unless explicitly included
            if not self.include_django_apps and app_label in {
                'admin', 'auth', 'contenttypes', 'sessions', 'messages',
                'staticfiles', 'sites'
            }:
                continue

            filtered_models.append(model)

        return filtered_models

    def safe_repr(self, obj):
        """Safely represent any object with improved callable handling"""
        if obj is None:
            return None
        if obj is models.NOT_PROVIDED:
            return None
        if callable(obj):
            try:
                from inspect import signature
                return f"<callable {obj.__name__}{signature(obj)}>"
            except Exception:
                return f"<callable {getattr(obj, '__name__', str(obj))}>"
        # Escape pipe characters for markdown tables
        return str(obj).replace("|", "\\|")

    def get_dotted_name(self, model_class):
        """Get fully qualified model name"""
        return f"{model_class._meta.app_label}.{model_class._meta.model_name}"

    def extract_field_info(self, field) -> FieldInfo:
        """Extract comprehensive field information with full coverage"""
        # Safe extraction of choices - fix for the main error
        field_choices = getattr(field, 'choices', None)
        choices_list = list(field_choices) if field_choices is not None else []

        # Safe extraction of validators
        field_validators = getattr(field, 'validators', None)
        validators_list = [str(v) for v in field_validators] if field_validators is not None else []

        info = FieldInfo(
            name=field.name,
            type=field.__class__.__name__,
            db_column=getattr(field, 'db_column', None) or field.name,
            null=getattr(field, 'null', False),
            blank=getattr(field, 'blank', False),
            primary_key=getattr(field, 'primary_key', False),
            unique=getattr(field, 'unique', False),
            db_index=getattr(field, 'db_index', False),
            editable=getattr(field, 'editable', True),
            auto_created=getattr(field, 'auto_created', False),
            concrete=getattr(field, 'concrete', True),
            default=self.safe_repr(getattr(field, 'default', None)),
            validators=validators_list,
            choices=choices_list
        )

        # Type-specific attributes
        for attr in ['max_length', 'min_length', 'max_value', 'min_value',
                     'decimal_places', 'max_digits', 'auto_now', 'auto_now_add']:
            if hasattr(field, attr):
                setattr(info, attr, getattr(field, attr))

        # Calendar uniqueness constraints
        for attr in ('unique_for_date', 'unique_for_month', 'unique_for_year'):
            if getattr(field, attr, None):  # Check for None as well as False
                setattr(info, attr, True)

        # File fields
        if hasattr(field, 'upload_to'):
            info.upload_to = str(field.upload_to) if field.upload_to else None
        if hasattr(field, 'storage'):
            info.storage = field.storage.__class__.__name__ if field.storage else None

        # Relationship fields
        if isinstance(field, (related.ForeignKey, related.OneToOneField, related.ManyToManyField)):
            try:
                info.related_model = self.get_dotted_name(field.related_model)
            except Exception:
                info.related_model = str(field.related_model)

            if hasattr(field, 'remote_field') and field.remote_field:
                try:
                    if hasattr(field.remote_field, 'on_delete'):
                        info.on_delete = getattr(field.remote_field.on_delete, '__name__', str(field.remote_field.on_delete))
                    info.to_field = getattr(field.remote_field, 'to_field', None)
                    info.related_name = getattr(field.remote_field, 'related_name', None)
                    info.db_constraint = getattr(field, 'db_constraint', True)
                    info.limit_choices_to = self.safe_repr(getattr(field, 'limit_choices_to', None))

                    if hasattr(field, 'get_queryset'):
                        try:
                            qs = field.get_queryset()
                            info.queryset_class = qs.__class__.__name__ if qs else None
                        except Exception:
                            info.queryset_class = None
                except Exception:
                    pass  # Skip if any relationship attribute extraction fails

            if isinstance(field, related.ManyToManyField):
                info.symmetrical = getattr(field, 'symmetrical', None)
                if hasattr(field, 'remote_field') and field.remote_field and hasattr(field.remote_field, 'through'):
                    through_model = field.remote_field.through
                    if hasattr(through_model, '_meta') and through_model._meta.auto_created:
                        info.through = f"{through_model._meta.app_label}.{through_model._meta.model_name}"

        # Generic Foreign Key and Generic Relations
        elif isinstance(field, GenericForeignKey):
            info.content_type_field = getattr(field, 'ct_field', None)
            info.object_id_field = getattr(field, 'fk_field', None)
            info.related_model = "contenttypes.ContentType"

        elif isinstance(field, GenericRelation):
            try:
                info.related_model = self.get_dotted_name(field.related_model)
                info.content_type_field = getattr(field, 'content_type_field_name', None)
                info.object_id_field = getattr(field, 'object_id_field_name', None)

                if hasattr(field, 'related_query_name') and callable(field.related_query_name):
                    try:
                        info.related_query_name = field.related_query_name()
                    except Exception:
                        info.related_query_name = None

                info.limit_choices_to = self.safe_repr(getattr(field, 'limit_choices_to', None))

                if hasattr(field, 'get_queryset'):
                    try:
                        qs = field.get_queryset()
                        info.queryset_class = qs.__class__.__name__ if qs else None
                    except Exception:
                        info.queryset_class = None
            except Exception:
                pass  # Skip if any generic relation attribute extraction fails

        return info

    def extract_constraints(self, model) -> List[ConstraintInfo]:
        """Extract all constraint information including legacy"""
        constraints = []

        try:
            # Modern constraints
            if hasattr(model._meta, 'constraints'):
                for constraint in model._meta.constraints:
                    constraint_info = ConstraintInfo(
                        name=getattr(constraint, 'name', None),
                        type=constraint.__class__.__name__,
                        fields=list(getattr(constraint, 'fields', [])),
                        deferrable=getattr(constraint, 'deferrable', False)
                    )

                    if hasattr(constraint, 'condition') and constraint.condition:
                        constraint_info.condition = str(constraint.condition)

                    constraints.append(constraint_info)

            # Legacy unique_together and index_together
            if hasattr(model._meta, 'unique_together') and model._meta.unique_together:
                for fields_tuple in model._meta.unique_together:
                    constraints.append(ConstraintInfo(
                        name=f"unique_together_{model._meta.db_table}",
                        type="unique_together",
                        fields=list(fields_tuple)
                    ))

            if hasattr(model._meta, 'index_together') and model._meta.index_together:
                for fields_tuple in model._meta.index_together:
                    constraints.append(ConstraintInfo(
                        name=f"index_together_{model._meta.db_table}",
                        type="index_together",
                        fields=list(fields_tuple)
                    ))
        except Exception as e:
            # If constraint extraction fails, continue without constraints
            pass

        return constraints

    def extract_indexes(self, model) -> List[IndexInfo]:
        """Extract all index information"""
        indexes = []

        try:
            if hasattr(model._meta, 'indexes'):
                for index in model._meta.indexes:
                    index_info = IndexInfo(
                        name=getattr(index, 'name', None),
                        fields=list(getattr(index, 'fields', [])),
                        unique=getattr(index, 'unique', False),
                        opclasses=list(getattr(index, 'opclasses', []))
                    )

                    if hasattr(index, 'condition') and index.condition:
                        index_info.condition = str(index.condition)
                        index_info.partial = True

                    indexes.append(index_info)
        except Exception:
            # If index extraction fails, continue without indexes
            pass

        return indexes

    def extract_managers(self, model) -> List[ManagerInfo]:
        """Extract manager information"""
        managers = []

        try:
            if hasattr(model._meta, 'managers_map'):
                for name, manager in model._meta.managers_map.items():
                    managers.append(ManagerInfo(
                        name=name,
                        class_name=manager.__class__.__name__,
                        module=getattr(manager.__class__, '__module__', 'unknown'),
                        is_default=(name == getattr(model._meta, 'default_manager_name', None)),
                        is_base=(name == getattr(model._meta, 'base_manager_name', None))
                    ))
        except Exception:
            # If manager extraction fails, continue without managers
            pass

        return managers

    def detect_duplicate_columns(self, fields: List[FieldInfo]) -> List[str]:
        """Detect fields mapping to same db_column"""
        column_map = defaultdict(list)
        for field in fields:
            column_map[field.db_column].append(field.name)

        duplicates = []
        for db_col, field_names in column_map.items():
            if len(field_names) > 1:
                duplicates.extend(sorted(field_names))

        return duplicates

    def extract_model_info(self, model) -> ModelInfo:
        """Extract comprehensive model information"""
        meta = model._meta

        # Extract ALL fields including hidden ones, but skip reverse M2M/FK relations
        fields_info = []
        try:
            for field in meta.get_fields(include_hidden=True):
                if field.auto_created and not field.concrete:   # skip reverse M2M/FK
                    continue
                if hasattr(field, 'name'):  # Skip reverse relations without names
                    try:
                        field_info = self.extract_field_info(field)
                        fields_info.append(field_info)
                    except Exception as e:
                        # Skip problematic fields but continue processing
                        print(f"Warning: Could not extract info for field {getattr(field, 'name', 'unknown')}: {e}")
                        continue
        except Exception as e:
            print(f"Warning: Could not extract fields for model {model.__name__}: {e}")

        # Extract MRO (excluding object)
        mro = []
        try:
            mro = [cls.__name__ for cls in model.__mro__[:-1]]
        except Exception:
            mro = [model.__name__]

        model_info = ModelInfo(
            name=model.__name__,
            app_label=meta.app_label,
            module=getattr(model, '__module__', 'unknown'),
            label=meta.label,
            label_lower=meta.label_lower,
            db_table=meta.db_table,
            abstract=meta.abstract,
            proxy=meta.proxy,
            managed=meta.managed,
            verbose_name=str(meta.verbose_name),
            verbose_name_plural=str(meta.verbose_name_plural),
            ordering=list(meta.ordering) if meta.ordering else [],
            default_permissions=list(getattr(meta, 'default_permissions', [])),
            permissions=list(getattr(meta, 'permissions', [])),
            get_latest_by=getattr(meta, 'get_latest_by', None),
            default_related_name=getattr(meta, 'default_related_name', None),
            db_tablespace=getattr(meta, 'db_tablespace', None),
            required_db_vendor=getattr(meta, 'required_db_vendor', None),
            required_db_features=list(getattr(meta, 'required_db_features', [])),
            db_table_comment=getattr(meta, 'db_table_comment', None),
            fields=fields_info,
            constraints=self.extract_constraints(model),
            indexes=self.extract_indexes(model),
            managers=self.extract_managers(model),
            mro=mro,
            duplicate_columns=self.detect_duplicate_columns(fields_info)
        )

        return model_info

    def detect_collisions(self):
        """Detect table collisions"""
        for model_info in self.models_info:
            self.table_collisions[model_info.db_table].append(model_info.label)

        # Mark models with duplicate tables
        for table, labels in self.table_collisions.items():
            if len(labels) > 1 and any(m.managed for m in self.models_info if m.db_table == table):
                for model_info in self.models_info:
                    if model_info.db_table == table:
                        model_info.duplicate_db_table = True

    def to_dict(self, obj):
        """Convert dataclass to dict recursively"""
        if isinstance(obj, (FieldInfo, ConstraintInfo, IndexInfo, ManagerInfo, ModelInfo)):
            result = asdict(obj)
            return result
        elif isinstance(obj, list):
            return [self.to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.to_dict(value) for key, value in obj.items()}
        else:
            return obj

    def inspect(self) -> Dict[str, Any]:
        """Main inspection method"""
        models = self.get_models()

        for model in models:
            try:
                model_info = self.extract_model_info(model)
                self.models_info.append(model_info)
            except Exception as e:
                print(f"Error processing model {model.__name__}: {e}")
                continue

        self.detect_collisions()

        return {
            'models': [self.to_dict(model_info) for model_info in self.models_info],
            'summary': {
                'total_models': len(self.models_info),
                'table_collisions': {k: v for k, v in self.table_collisions.items() if len(v) > 1}
            }
        }

    def generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate clean, focused markdown report"""
        lines = ["# Django Models Schema Report\n"]

        # Summary
        summary = data['summary']
        lines.append(f"**Total Models**: {summary['total_models']}")

        if summary['table_collisions']:
            lines.append(f"**Table Collisions**: {len(summary['table_collisions'])}")
            for table, labels in summary['table_collisions'].items():
                lines.append(f"- `{table}`: {', '.join(labels)}")

        lines.append("")

        # Group models by app
        models_by_app = defaultdict(list)
        for model_data in data['models']:
            models_by_app[model_data['app_label']].append(model_data)

        # Models by app
        for app_label in sorted(models_by_app.keys()):
            lines.append(f"## App: {app_label}\n")

            for model_data in sorted(models_by_app[app_label], key=lambda x: x['name']):
                # Use ASCII arrow instead of Unicode for better compatibility
                lines.append(f"### {model_data['name']} -> `{model_data['db_table']}`")

                # Warnings first
                warnings = []
                if model_data['duplicate_db_table']:
                    warnings.append("WARNING: Duplicate table name")
                if model_data['duplicate_columns']:
                    warnings.append(f"WARNING: Duplicate columns: {', '.join(model_data['duplicate_columns'])}")

                if warnings:
                    for warning in warnings:
                        lines.append(f"{warning}")
                    lines.append("")

                # Fields table
                if model_data['fields']:
                    lines.extend([
                        "| Field | Type | Column | Null | Key | Related |",
                        "|-------|------|--------|------|-----|---------|"
                    ])

                    for field in model_data['fields']:
                        # Build key indicators
                        key_indicators = []
                        if field['primary_key']:
                            key_indicators.append('PK')
                        if field['unique']:
                            key_indicators.append('UQ')
                        if field['db_index']:
                            key_indicators.append('IDX')
                        # Add calendar uniqueness indicators
                        if field.get('unique_for_date'):
                            key_indicators.append('UQ_DATE')
                        if field.get('unique_for_month'):
                            key_indicators.append('UQ_MONTH')
                        if field.get('unique_for_year'):
                            key_indicators.append('UQ_YEAR')
                        key_str = ','.join(key_indicators)

                        # Build related info
                        related = ""
                        if field['related_model']:
                            related = field['related_model']
                            if field['on_delete']:
                                related += f" ({field['on_delete']})"
                        elif field['content_type_field']:
                            related = f"Generic({field['content_type_field']}, {field['object_id_field']})"

                        # Truncate long field names and related info for table readability
                        field_name = field['name'][:57] + "..." if len(field['name']) > 60 else field['name']
                        field_type = field['type'][:57] + "..." if len(field['type']) > 60 else field['type']
                        db_column = field['db_column'][:57] + "..." if len(field['db_column']) > 60 else field['db_column']
                        related = related[:57] + "..." if len(related) > 60 else related

                        # Use checkmark symbol that's ASCII-compatible
                        null_mark = 'Y' if field['null'] else ''

                        lines.append(
                            f"| `{field_name}` | {field_type} | {db_column} | "
                            f"{null_mark} | {key_str} | {related} |"
                        )

                # Constraints and indexes (one-liners)
                if model_data['constraints']:
                    lines.append("\n**Constraints:**")
                    for constraint in model_data['constraints']:
                        fields_str = ', '.join(constraint['fields'])
                        lines.append(f"- `{constraint['name']}` ({constraint['type']}): [{fields_str}]")

                if model_data['indexes']:
                    lines.append("\n**Indexes:**")
                    for index in model_data['indexes']:
                        fields_str = ', '.join(index['fields'])
                        flags = []
                        if index['unique']:
                            flags.append('UNIQUE')
                        if index['partial']:
                            flags.append('PARTIAL')
                        flag_str = f" [{','.join(flags)}]" if flags else ""
                        lines.append(f"- `{index['name']}`: [{fields_str}]{flag_str}")

                lines.append("\n---\n")

        return '\n'.join(lines)

    def generate_hash(self, content: str) -> str:
        """Generate hash of content for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()


class Command(BaseCommand):
    help = "Generate comprehensive Django model schema report"

    def add_arguments(self, parser):
        parser.add_argument('--include-django', action='store_true',
                          help='Include Django core apps')
        parser.add_argument('--exclude-app', action='append', default=[],
                          help='Apps to exclude (can be used multiple times)')
        parser.add_argument('-o', '--output', help='Output file (default: stdout)')
        parser.add_argument('--hash-only', action='store_true',
                          help='Output only the schema hash')

    def handle(self, *args, **options):
        # Setup Django if needed
        if not apps.ready:
            django.setup()

        # Run inspection
        inspector = DjangoModelInspector(
            include_django_apps=options['include_django'],
            exclude_apps=options['exclude_app']
        )

        data = inspector.inspect()
        markdown = inspector.generate_markdown(data)
        content_hash = inspector.generate_hash(markdown)

        if options['hash_only']:
            self.stdout.write(content_hash)
            return

        if options['output']:
            # Fix: Explicitly specify UTF-8 encoding for file writing
            Path(options['output']).write_text(markdown, encoding='utf-8')
            self.stdout.write(
                self.style.SUCCESS(f"Report written to {options['output']} (hash: {content_hash[:12]})")
            )
        else:
            self.stdout.write(markdown)
            self.stdout.write(f"\n<!-- Hash: {content_hash} -->")


def main():
    """CLI entry point for standalone usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Django Model Inspector')
    parser.add_argument('--settings', help='Django settings module')
    parser.add_argument('--include-django', action='store_true', help='Include Django core apps')
    parser.add_argument('--exclude-app', action='append', default=[], help='Apps to exclude')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--hash-only', action='store_true', help='Output only the schema hash')

    args = parser.parse_args()

    # Setup Django
    if args.settings:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', args.settings)
    django.setup()

    # Run inspection
    inspector = DjangoModelInspector(
        include_django_apps=args.include_django,
        exclude_apps=args.exclude_app
    )

    data = inspector.inspect()
    markdown = inspector.generate_markdown(data)
    content_hash = inspector.generate_hash(markdown)

    if args.hash_only:
        print(content_hash)
        return

    if args.output:
        # Fix: Explicitly specify UTF-8 encoding for file writing
        Path(args.output).write_text(markdown, encoding='utf-8')
        print(f"Report written to {args.output} (hash: {content_hash[:12]})")
    else:
        print(markdown)
        print(f"\n<!-- Hash: {content_hash} -->")


if __name__ == '__main__':
    main()
