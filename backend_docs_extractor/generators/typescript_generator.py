# fmt: off
# isort: skip_file

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TypeScript Interface Generator

This module generates TypeScript interfaces from extracted backend information,
providing type definitions for models, API responses, and more.

Author: nanthiniSanthanam
Generated: 2025-05-04 14:17:12

Configuration Variables:
- OUTPUT_DIR: Directory where TypeScript files will be generated
- GENERATE_TYPESCRIPT: Boolean flag to enable/disable TypeScript generation
- DETAIL_LEVEL: Level of detail for generated interfaces ("basic", "standard", "comprehensive")
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Optional

logger = logging.getLogger(__name__)


class TypeScriptGenerator:
    """Generate TypeScript interfaces from extracted backend information"""

    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.detail_level = config.DETAIL_LEVEL

        # Mapping of Django field types to TypeScript types
        self.type_mapping = {
            # String types
            'CharField': 'string',
            'TextField': 'string',
            'EmailField': 'string',
            'URLField': 'string',
            'SlugField': 'string',
            'UUIDField': 'string',
            'FileField': 'string',
            'ImageField': 'string',
            'FilePathField': 'string',

            # Number types
            'IntegerField': 'number',
            'BigIntegerField': 'number',
            'PositiveIntegerField': 'number',
            'PositiveSmallIntegerField': 'number',
            'SmallIntegerField': 'number',
            'FloatField': 'number',
            'DecimalField': 'number',
            'AutoField': 'number',
            'BigAutoField': 'number',

            # Boolean types
            'BooleanField': 'boolean',
            'NullBooleanField': 'boolean | null',

            # Date/time types
            'DateField': 'string', # ISO date format
            'TimeField': 'string', # ISO time format
            'DateTimeField': 'string', # ISO datetime format
            'DurationField': 'string',

            # Special types
            'JSONField': 'any', # Would be more specific if schema is known
            'ArrayField': 'any[]', # Would be more specific if element type is known
            'BinaryField': 'string', # Base64 encoded

            # Default fallback
            'default': 'any'
        }

        # Set to track generated interface names to avoid duplicates
        self.generated_interfaces = set()

        # Keep track of models that need to be generated for cross-references
        self.models_to_generate = {}

    def generate(self, models: Dict[str, Any], apis: Dict[str, Any],
                 serializers: Dict[str, Any], output_dir: Path) -> None:
        """Generate TypeScript interfaces

        Args:
            models: Extracted model information
            apis: Extracted API endpoint information
            serializers: Extracted serializer information
            output_dir: Directory where TypeScript files will be generated
        """
        logger.info("Generating TypeScript interfaces")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create index.ts with exports
        self._generate_index_file(output_dir)

        # Generate model interfaces
        self._generate_model_interfaces(models, output_dir)

        # Generate API response types
        self._generate_api_types(apis, serializers, output_dir)

        # Generate utility types
        self._generate_utility_types(output_dir)

        logger.info(f"TypeScript interfaces generated in {output_dir}")

    def _generate_index_file(self, output_dir: Path) -> None:
        """Generate index.ts file that exports all types

        Args:
            output_dir: Directory where TypeScript files will be generated
        """
        index_path = output_dir / 'index.ts'

        index_content = [
            '/**',
            ' * TypeScript interface definitions for backend models and APIs',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            '',
            '// Export model interfaces',
            "export * from './models';",
            '',
            '// Export API types',
            "export * from './api';",
            '',
            '// Export utility types',
            "export * from './utils';",
            ''
        ]

        with open(index_path, 'w') as f:
            f.write('\n'.join(index_content))

        logger.info("Generated index.ts")

    def _generate_model_interfaces(self, models: Dict[str, Any], output_dir: Path) -> None:
        """Generate TypeScript interfaces for Django models

        Args:
            models: Extracted model information
            output_dir: Directory where TypeScript files will be generated
        """
        models_dir = output_dir / 'models'
        models_dir.mkdir(exist_ok=True)

        # Track all generated models for the barrel file
        generated_models = []

        # First pass: collect all model names and their app, for cross-referencing
        for app_label, app_info in models.items():
            for model_name, model_info in app_info.get('models', {}).items():
                sanitized_name = self._sanitize_interface_name(model_name)
                self.models_to_generate[f"{app_label}.{model_name}"] = sanitized_name

        # Generate an interface file for each app
        for app_label, app_info in models.items():
            if not app_info.get('models'):
                continue

            # Create app-specific file
            app_name = app_label.split('.')[-1]
            file_name = f"{app_name.lower()}.ts"
            file_path = models_dir / file_name

            app_models_content = [
                '/**',
                f' * TypeScript interfaces for {app_label} models',
                f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                ' */',
                '',
            ]

            # Add imports for cross-referenced models from other apps
            imports = self._get_model_imports(app_label, app_info)
            if imports:
                app_models_content.extend(imports)
                app_models_content.append('')

            # Generate interfaces for each model
            for model_name, model_info in sorted(app_info.get('models', {}).items()):
                interface_content = self._generate_model_interface(model_name, model_info, app_label)
                app_models_content.extend(interface_content)
                app_models_content.append('')

                # Add to list of generated models
                sanitized_name = self._sanitize_interface_name(model_name)
                generated_models.append((sanitized_name, f"./{app_name.lower()}"))

            # Write the file
            with open(file_path, 'w') as f:
                f.write('\n'.join(app_models_content))

            logger.info(f"Generated model interfaces for {app_label}")

        # Create barrel file for all models
        self._generate_barrel_file(models_dir, generated_models, 'models')

    def _get_model_imports(self, current_app: str, app_info: Dict[str, Any]) -> List[str]:
        """Get import statements for models referenced from other apps

        Args:
            current_app: Name of the current app
            app_info: Information about the current app

        Returns:
            List of import statements
        """
        imports_by_app = {}

        # Check each model
        for model_name, model_info in app_info.get('models', {}).items():
            # Check foreign keys
            for fk in model_info.get('relationships', {}).get('foreign_keys', []):
                if fk['target_app'] != current_app:
                    target_app = fk['target_app'].split('.')[-1].lower()
                    target_model = self._sanitize_interface_name(fk['target_model'])
                    if target_app not in imports_by_app:
                        imports_by_app[target_app] = set()
                    imports_by_app[target_app].add(target_model)

            # Check many-to-many relationships
            for m2m in model_info.get('relationships', {}).get('many_to_many', []):
                if m2m['target_app'] != current_app:
                    target_app = m2m['target_app'].split('.')[-1].lower()
                    target_model = self._sanitize_interface_name(m2m['target_model'])
                    if target_app not in imports_by_app:
                        imports_by_app[target_app] = set()
                    imports_by_app[target_app].add(target_model)

            # Check one-to-one relationships
            for o2o in model_info.get('relationships', {}).get('one_to_one', []):
                if o2o['target_app'] != current_app:
                    target_app = o2o['target_app'].split('.')[-1].lower()
                    target_model = self._sanitize_interface_name(o2o['target_model'])
                    if target_app not in imports_by_app:
                        imports_by_app[target_app] = set()
                    imports_by_app[target_app].add(target_model)

        # Generate import statements
        import_statements = []
        for app, models in imports_by_app.items():
            models_list = ', '.join(sorted(models))
            import_statements.append(f"import {{ {models_list} }} from './{app}';")

        return import_statements

    def _generate_model_interface(self, model_name: str, model_info: Dict[str, Any], 
                                  app_label: str) -> List[str]:
        """Generate TypeScript interface for a Django model

        Args:
            model_name: Name of the model
            model_info: Model information
            app_label: Name of the app containing the model

        Returns:
            List of TypeScript interface content lines
        """
        interface_name = self._sanitize_interface_name(model_name)
        self.generated_interfaces.add(interface_name)

        # Start interface definition
        interface_content = [
            '/**',
            f' * Interface for {model_name} model',
            f' * Table name: {model_info.get("table_name")}',
            ' */',
            f'export interface {interface_name} {{',
        ]

        # Add fields
        for field_name, field_info in sorted(model_info.get('fields', {}).items()):
            field_type = self._get_typescript_type(field_info)
            nullable = field_info.get('null', False)
            optional = field_info.get('blank', False) and not field_info.get('primary_key', False)

            # Add JSDoc comment for field if there's help text
            help_text = field_info.get('help_text')
            if help_text and help_text != field_name:
                interface_content.append(f'  /** {help_text} */')

            # Create the field definition with appropriate nullability/optionality
            field_def = f"  {field_name}"
            if optional:
                field_def += "?"
            field_def += ": " + field_type
            if nullable and not optional:
                field_def += " | null"
            field_def += ";"

            interface_content.append(field_def)

        # Add relationship fields
        relationships = model_info.get('relationships', {})

        # Foreign Keys
        for fk in relationships.get('foreign_keys', []):
            field_name = fk.get('name')
            target_model = fk.get('target_model')
            target_interface = self._sanitize_interface_name(target_model)
            nullable = fk.get('null', False)
            optional = fk.get('blank', False)

            # Add JSDoc for relationship
            interface_content.append(f'  /** Foreign key to {target_model} */')

            # Create field with appropriate nullability/optionality
            field_def = f"  {field_name}"
            if optional:
                field_def += "?"
            field_def += f": {target_interface}"
            if nullable and not optional:
                field_def += " | null"
            field_def += ";"

            interface_content.append(field_def)

            # Add the ID field for the foreign key as well
            interface_content.append(f'  /** ID for {field_name} relationship */')
            field_def = f"  {field_name}_id"
            if optional:
                field_def += "?"
            field_def += ": number"
            if nullable and not optional:
                field_def += " | null"
            field_def += ";"

            interface_content.append(field_def)

        # Many-to-Many Fields
        for m2m in relationships.get('many_to_many', []):
            field_name = m2m.get('name')
            target_model = m2m.get('target_model')
            target_interface = self._sanitize_interface_name(target_model)

            interface_content.append(f'  /** Many-to-many relationship with {target_model} */')
            interface_content.append(f'  {field_name}: {target_interface}[];')

        # One-to-One Fields
        for o2o in relationships.get('one_to_one', []):
            field_name = o2o.get('name')
            target_model = o2o.get('target_model')
            target_interface = self._sanitize_interface_name(target_model)
            nullable = o2o.get('null', False)
            optional = o2o.get('blank', False)

            interface_content.append(f'  /** One-to-one relationship with {target_model} */')

            field_def = f"  {field_name}"
            if optional:
                field_def += "?"
            field_def += f": {target_interface}"
            if nullable and not optional:
                field_def += " | null"
            field_def += ";"

            interface_content.append(field_def)

        # Handle reverse relations depending on detail level
        if self.detail_level in ["standard", "comprehensive"]:
            for rev in relationships.get('reverse_relations', []):
                if rev['multiple']:
                    # This is a one-to-many or many-to-many reverse relation
                    field_name = rev.get('name')
                    related_model = rev.get('related_model')
                    related_interface = self._sanitize_interface_name(related_model)

                    interface_content.append(f'  /** Reverse relation to {related_model} */')
                    interface_content.append(f'  {field_name}?: {related_interface}[];')
                else:
                    # This is a one-to-one reverse relation
                    field_name = rev.get('name')
                    related_model = rev.get('related_model')
                    related_interface = self._sanitize_interface_name(related_model)

                    interface_content.append(f'  /** Reverse one-to-one relation to {related_model} */')
                    interface_content.append(f'  {field_name}?: {related_interface};')

        # Close interface definition
        interface_content.append('}')

        return interface_content

    def _generate_api_types(self, apis: Dict[str, Any], serializers: Dict[str, Any], 
                          output_dir: Path) -> None:
        """Generate TypeScript types for API responses

        Args:
            apis: Extracted API endpoint information
            serializers: Extracted serializer information
            output_dir: Directory where TypeScript files will be generated
        """
        api_dir = output_dir / 'api'
        api_dir.mkdir(exist_ok=True)

        # Generate response types for each endpoint
        endpoints = apis.get('endpoints', [])
        grouped_endpoints = apis.get('grouped', {})

        # Track all generated types for the barrel file
        generated_types = []

        if grouped_endpoints:
            # Generate types by app
            for app_name, app_info in grouped_endpoints.items():
                # Skip if no endpoints
                if not app_info.get('endpoints'):
                    continue

                # Create app-specific file
                sanitized_app_name = app_name.lower().replace('.', '_')
                file_name = f"{sanitized_app_name}.ts"
                file_path = api_dir / file_name

                app_types_content = [
                    '/**',
                    f' * TypeScript types for {app_name} API endpoints',
                    f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    ' */',
                    '',
                    '// Import model interfaces',
                    "import { PaginatedResponse } from '../utils';",
                ]

                # Get model imports
                model_imports = self._get_api_model_imports(app_info.get('endpoints', []))
                app_types_content.extend(model_imports)
                app_types_content.append('')

                # Generate types for each endpoint
                for endpoint in app_info.get('endpoints', []):
                    endpoint_types = self._generate_endpoint_types(endpoint)
                    if endpoint_types:
                        app_types_content.extend(endpoint_types)
                        app_types_content.append('')

                        # Add to list of generated types
                        type_name = self._get_response_type_name(endpoint)
                        generated_types.append((type_name, f"./{sanitized_app_name}"))

                # Write the file
                with open(file_path, 'w') as f:
                    f.write('\n'.join(app_types_content))

                logger.info(f"Generated API types for {app_name}")
        else:
            # Generate a single file for all endpoints
            file_path = api_dir / 'endpoints.ts'

            types_content = [
                '/**',
                ' * TypeScript types for API endpoints',
                f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                ' */',
                '',
                '// Import model interfaces',
                "import { PaginatedResponse } from '../utils';",
            ]

            # Get model imports
            model_imports = self._get_api_model_imports(endpoints)
            types_content.extend(model_imports)
            types_content.append('')

            # Generate types for each endpoint
            for endpoint in endpoints:
                endpoint_types = self._generate_endpoint_types(endpoint)
                if endpoint_types:
                    types_content.extend(endpoint_types)
                    types_content.append('')

                    # Add to list of generated types
                    type_name = self._get_response_type_name(endpoint)
                    generated_types.append((type_name, "./endpoints"))

            # Write the file
            with open(file_path, 'w') as f:
                f.write('\n'.join(types_content))

            logger.info("Generated API types")

        # Create barrel file for all API types
        self._generate_barrel_file(api_dir, generated_types, 'api')

    def _get_api_model_imports(self, endpoints: List[Dict[str, Any]]) -> List[str]:
        """Get model imports needed for API types

        Args:
            endpoints: List of API endpoint information

        Returns:
            List of import statements
        """
        models_by_app = {}

        for endpoint in endpoints:
            serializer_info = endpoint.get('serializer', {})
            if not serializer_info:
                continue

            # Get model info from serializer if available
            model_info = serializer_info.get('model', {})
            if model_info:
                model_name = model_info.get('name')
                app_name = model_info.get('app')

                if not model_name or not app_name:
                    continue

                app_short_name = app_name.split('.')[-1].lower()
                model_interface = self._sanitize_interface_name(model_name)

                if app_short_name not in models_by_app:
                    models_by_app[app_short_name] = set()
                models_by_app[app_short_name].add(model_interface)

        # Generate import statements
        import_statements = []
        for app, models in models_by_app.items():
            models_list = ', '.join(sorted(models))
            import_statements.append(f"import {{ {models_list} }} from '../models/{app}';")

        return import_statements

    def _generate_endpoint_types(self, endpoint: Dict[str, Any]) -> List[str]:
        """Generate TypeScript types for an API endpoint

        Args:
            endpoint: API endpoint information

        Returns:
            List of TypeScript type definitions
        """
        result = []

        # Skip if no serializer info
        serializer_info = endpoint.get('serializer', {})
        if not serializer_info:
            return result

        # Get basic info
        path = endpoint.get('path', '')
        http_methods = endpoint.get('http_methods', [])

        # Generate response type name based on path
        type_name = self._get_response_type_name(endpoint)

        # Add JSDoc comment
        result.append('/**')
        result.append(f' * Response type for {", ".join(method.upper() for method in http_methods)} {path}')
        result.append(' */')

        # If serializer is directly tied to a model
        model_info = serializer_info.get('model', {})
        if model_info:
            model_name = model_info.get('name')
            if model_name:
                model_interface = self._sanitize_interface_name(model_name)

                # Check if the endpoint likely returns a list (paginated or not)
                is_list_endpoint = (
                    'list' in endpoint.get('view', {}).get('name', '').lower() or
                    path.endswith('/') and not any(segment.startswith('{') for segment in path.split('/'))
                )

                if is_list_endpoint:
                    # List response, likely paginated
                    result.append(f'export type {type_name} = PaginatedResponse<{model_interface}>;')
                else:
                    # Single item response
                    result.append(f'export type {type_name} = {model_interface};')

                return result

        # If serializer has fields defined directly
        fields = serializer_info.get('fields', {})
        if fields:
            # Generate interface for the response
            result.append(f'export interface {type_name} {{')

            for field_name, field_info in sorted(fields.items()):
                field_type = self._get_typescript_type(field_info)
                read_only = field_info.get('read_only', False)
                required = not field_info.get('allow_null', False) and field_info.get('required', True)

                # Add JSDoc if there's help text
                help_text = field_info.get('help_text', '')
                if help_text:
                    result.append(f'  /** {help_text} */')

                # Create field definition
                field_def = f"  {field_name}"
                if not required:
                    field_def += "?"
                field_def += f": {field_type}"
                if field_info.get('allow_null', False) and required:
                    field_def += " | null"
                field_def += ";"

                # Add readonly comment if applicable
                if read_only:
                    field_def += " // read-only"

                result.append(field_def)

            # Close interface
            result.append('}')

            # Check if it's a list endpoint
            is_list_endpoint = (
                'list' in endpoint.get('view', {}).get('name', '').lower() or
                path.endswith('/') and not any(segment.startswith('{') for segment in path.split('/'))
            )

            if is_list_endpoint:
                # Add paginated type
                result.append('')
                result.append('/**')
                result.append(f' * Paginated response for {path}')
                result.append(' */')
                result.append(f'export type Paginated{type_name} = PaginatedResponse<{type_name}>;')

        return result

    def _generate_utility_types(self, output_dir: Path) -> None:
        """Generate utility TypeScript types

        Args:
            output_dir: Directory where TypeScript files will be generated
        """
        utils_dir = output_dir / 'utils'
        utils_dir.mkdir(exist_ok=True)

        # Create utility types file
        utils_path = utils_dir / 'index.ts'

        utils_content = [
            '/**',
            ' * Utility TypeScript types',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            '',
            '/**',
            ' * Generic paginated response from Django Rest Framework',
            ' */',
            'export interface PaginatedResponse<T> {',
            '  /** Total number of results across all pages */',
            '  count: number;',
            '  /** URL to next page of results, null if last page */',
            '  next: string | null;',
            '  /** URL to previous page of results, null if first page */',
            '  previous: string | null;',
            '  /** Results for current page */',
            '  results: T[];',
            '}',
            '',
            '/**',
            ' * Generic error response',
            ' */',
            'export interface ErrorResponse {',
            '  /** Main error message */',
            '  detail?: string;',
            '  /** Detailed field errors */',
            '  [fieldName: string]: string | string[] | undefined;',
            '}',
            '',
            '/**',
            ' * Token authentication response',
            ' */',
            'export interface TokenResponse {',
            '  /** Authentication token */',
            '  token: string;',
            '}',
            '',
            '/**',
            ' * JWT authentication response',
            ' */',
            'export interface JWTResponse {',
            '  /** JWT access token */',
            '  access: string;',
            '  /** JWT refresh token */',
            '  refresh: string;',
            '}',
            '',
            '/**',
            ' * Upload response for file uploads',
            ' */',
            'export interface UploadResponse {',
            '  /** URL to the uploaded file */',
            '  url: string;',
            '  /** Name of the uploaded file */',
            '  name?: string;',
            '  /** Size of the file in bytes */',
            '  size?: number;',
            '}',
            ''
        ]

        # Write the file
        with open(utils_path, 'w') as f:
            f.write('\n'.join(utils_content))

        logger.info("Generated utility TypeScript types")

    def _generate_barrel_file(self, directory: Path, items: List[tuple], module_name: str) -> None:
        """Generate a barrel file (index.ts) that re-exports all types

        Args:
            directory: Directory where the barrel file should be created
            items: List of (type_name, relative_path) tuples to export
            module_name: Name of the module (for documentation)
        """
        index_path = directory / 'index.ts'

        index_content = [
            '/**',
            f' * TypeScript {module_name} - Barrel file for unified imports',
            f' * Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            ''
        ]

        # Group by file
        exports_by_file = {}
        for item_name, file_path in items:
            if file_path not in exports_by_file:
                exports_by_file[file_path] = []
            exports_by_file[file_path].append(item_name)

        # Generate export statements
        for file_path, type_names in exports_by_file.items():
            types_str = ', '.join(sorted(type_names))
            index_content.append(f'export {{ {types_str} }} from \'{file_path}\';')

        # Write the file
        with open(index_path, 'w') as f:
            f.write('\n'.join(index_content))

        logger.info(f"Generated barrel file for {module_name}")

    def _get_typescript_type(self, field_info: Dict[str, Any]) -> str:
        """Convert Django/DRF field type to TypeScript type

        Args:
            field_info: Field information from extracted data

        Returns:
            TypeScript type as string
        """
        field_type = field_info.get('type', '')

        # Check if it's an array/list
        if field_type in ['ListField', 'ArrayField']:
            child_type = field_info.get('child_type', {})
            if child_type:
                child_ts_type = self._get_typescript_type(child_type)
                return f"{child_ts_type}[]"
            else:
                return "any[]"

        # Check if it's a nested object/serializer
        if field_type == 'NestedSerializer' or field_type == 'ModelSerializer':
            # For nested serializers, we'll create inline interfaces
            nested_fields = field_info.get('fields', {})
            if nested_fields:
                nested_parts = []
                for nested_name, nested_info in nested_fields.items():
                    nested_type = self._get_typescript_type(nested_info)
                    required = not nested_info.get('allow_null', False) and nested_info.get('required', True)

                    field_def = nested_name
                    if not required:
                        field_def += "?"
                    field_def += f": {nested_type}"
                    if nested_info.get('allow_null', False) and required:
                        field_def += " | null"

                    nested_parts.append(f"  {field_def};")

                if nested_parts:
                    # Use an inline interface
                    return "{\n" + "\n".join(nested_parts) + "\n}"

            # If the nested serializer has a model reference
            model_info = field_info.get('model', {})
            if model_info:
                model_name = model_info.get('name', '')
                if model_name:
                    return self._sanitize_interface_name(model_name)

            return 'any'

        # Check if it's a choice field
        if field_type == 'ChoiceField':
            choices = field_info.get('choices', [])
            if choices:
                choice_values = []
                for choice in choices:
                    # Handle both simple choices and grouped choices
                    if 'group' in choice:
                        for sub_choice in choice.get('choices', []):
                            value = sub_choice.get('value')
                            if value is not None:
                                if isinstance(value, str):
                                    choice_values.append(f'"{value}"')
                                else:
                                    choice_values.append(str(value))
                    else:
                        value = choice.get('value')
                        if value is not None:
                            if isinstance(value, str):
                                choice_values.append(f'"{value}"')
                            else:
                                choice_values.append(str(value))

                if choice_values:
                    return " | ".join(choice_values)

        # Check if it's a many-related field
        if field_type in ['ManyRelatedField', 'PrimaryKeyRelatedField'] and field_info.get('many', False):
            # Check if there's a target model
            related_model = field_info.get('related_model', '')
            if related_model:
                model_interface = self._sanitize_interface_name(related_model)
                return f"{model_interface}[]"
            else:
                return "any[]"

        # Check if it's a related field
        if field_type in ['PrimaryKeyRelatedField', 'RelatedField', 'HyperlinkedRelatedField']:
            # Check if there's a target model
            related_model = field_info.get('related_model', '')
            if related_model:
                model_interface = self._sanitize_interface_name(related_model)
                return model_interface
            else:
                return "any"

        # Lookup the type in the mapping
        return self.type_mapping.get(field_type, self.type_mapping['default'])

    def _sanitize_interface_name(self, name: str) -> str:
        """Sanitize a name to be a valid TypeScript interface name

        Args:
            name: Original name to sanitize

        Returns:
            Valid TypeScript interface name
        """
        # Ensure it starts with an uppercase letter
        if name and not name[0].isupper():
            name = name[0].upper() + name[1:]

        # Remove any invalid characters
        sanitized = ''.join(c for c in name if c.isalnum() or c == '_')

        return sanitized

    def _get_response_type_name(self, endpoint: Dict[str, Any]) -> str:
        """Generate a TypeScript response type name for an endpoint

        Args:
            endpoint: API endpoint information

        Returns:
            Type name for the endpoint response
        """
        path = endpoint.get('path', '')
        view_name = endpoint.get('view', {}).get('name', '')

        if view_name:
            # Use view name if available
            response_name = view_name.replace('APIView', '').replace('ViewSet', '')
            response_name = response_name.replace('View', '').strip()

            if 'list' in view_name.lower():
                return f"{response_name}Response"
            elif 'detail' in view_name.lower() or 'retrieve' in view_name.lower():
                return f"{response_name}Response"
            else:
                return f"{response_name}Response"
        else:
            # Generate from path
            path_parts = [p for p in path.split('/') if p and not p.startswith('{')]

            if not path_parts:
                return "ApiResponse"

            # Get last meaningful part of the path
            last_part = path_parts[-1]

            # Capitalize and remove any non-alphanumeric characters
            cleaned_part = ''.join(c for c in last_part.title() if c.isalnum())

            return f"{cleaned_part}Response"
# END OF CODE