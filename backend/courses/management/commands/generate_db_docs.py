import json
import pathlib
from datetime import datetime

import django
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, models


class Command(BaseCommand):
    help = "Generate comprehensive database schema documentation"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="docs",
            help="Directory to save documentation files (default: docs)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["both", "json", "markdown"],
            default="both",
            help="Output format (default: both)",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🔍 Extracting table information from Django models...")
        )

        tables = self.get_table_info()

        self.stdout.write(self.style.SUCCESS("📝 Creating documentation..."))

        # Create output directory
        output_dir = pathlib.Path(options["output_dir"])
        output_dir.mkdir(exist_ok=True)

        # Generate documentation based on format choice
        if options["format"] in ["both", "json"]:
            self.create_json_documentation(tables, output_dir)

        if options["format"] in ["both", "markdown"]:
            self.create_markdown_documentation(tables, output_dir)

        # Print summary
        self.print_summary(tables)

    def get_table_info(self):
        """Extract comprehensive table information from Django models"""
        tables = {}

        # Skip auto-created M2M tables and only get real models
        for model in apps.get_models(include_auto_created=False):
            meta = model._meta
            app_label = meta.app_label
            model_name = meta.model_name

            # Get field information - only concrete fields with actual DB columns
            fields = []
            for field in meta.concrete_fields:
                # Handle default values properly (including callables)
                default = None
                if field.default is not models.NOT_PROVIDED:
                    try:
                        default = (
                            field.get_default()
                            if callable(field.default)
                            else field.default
                        )
                    except:
                        default = str(field.default)

                # Handle db_type safely (some fields may not support it)
                try:
                    db_type = field.db_type(connection)
                except Exception:
                    db_type = "N/A"

                field_info = {
                    "column": field.column,
                    "type": field.get_internal_type(),
                    "db_type": db_type,
                    "null": field.null,
                    "blank": field.blank,
                    "default": default,
                    "primary_key": field.primary_key,
                    "unique": field.unique,
                    "max_length": getattr(field, "max_length", None),
                    "help_text": field.help_text,
                    "choices": getattr(field, "choices", None),
                    "related_model": (
                        field.remote_field.model._meta.db_table
                        if field.is_relation and field.remote_field
                        else None
                    ),
                    "relationship_type": field.__class__.__name__,
                }

                fields.append(field_info)

            # Handle unique_together (legacy) and UniqueConstraint (modern)
            unique_sets = list(meta.unique_together) if meta.unique_together else []
            # Add modern UniqueConstraint fields
            unique_sets += [
                constraint.fields
                for constraint in meta.constraints
                if isinstance(constraint, models.UniqueConstraint)
            ]

            # Get model metadata
            tables[meta.db_table] = {
                "app_label": app_label,
                "model_name": model_name,
                "verbose_name": str(meta.verbose_name),
                "verbose_name_plural": str(meta.verbose_name_plural),
                "db_table": meta.db_table,
                "fields": fields,
                "indexes": [idx.name for idx in meta.indexes] if meta.indexes else [],
                "constraints": (
                    [constraint.name for constraint in meta.constraints]
                    if meta.constraints
                    else []
                ),
                "ordering": ", ".join(meta.ordering) if meta.ordering else "",
                "unique_together": unique_sets,
            }

        return tables

    def create_json_documentation(self, tables, output_dir):
        """Create JSON documentation"""
        json_path = output_dir / "database_schema.json"
        json_path.write_text(json.dumps(tables, indent=2, default=str))
        self.stdout.write(self.style.SUCCESS(f"✅ JSON schema written to: {json_path}"))

    def create_markdown_documentation(self, tables, output_dir):
        """Create comprehensive Markdown documentation"""

        # Group tables by app
        apps_tables = {}
        for table_name, table_info in tables.items():
            app_label = table_info["app_label"]
            if app_label not in apps_tables:
                apps_tables[app_label] = []
            apps_tables[app_label].append((table_name, table_info))

        # Start building markdown content
        md_content = f"""# Database Schema Documentation

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Django Version:** {django.get_version()}
**Total Tables:** {len(tables)}
**Total Apps:** {len(apps_tables)}

## Table of Contents

"""

        # Add table of contents
        for app_label in sorted(apps_tables.keys()):
            md_content += (
                f"- [{app_label.title()} App](#{app_label.replace('_', '-')}-app)\n"
            )
            for table_name, table_info in sorted(apps_tables[app_label]):
                md_content += f"  - [{table_info['verbose_name']}](#{table_name.replace('_', '-')})\n"

        md_content += "\n---\n\n"

        # Generate detailed documentation for each app
        for app_label in sorted(apps_tables.keys()):
            md_content += f"## {app_label.title()} App\n\n"

            for table_name, table_info in sorted(apps_tables[app_label]):
                md_content += f"### {table_info['verbose_name']} (`{table_name}`)\n\n"

                # Model information
                md_content += f"**Model:** `{table_info['model_name']}`  \n"
                md_content += f"**App:** `{app_label}`  \n"
                md_content += f"**Verbose Name:** {table_info['verbose_name']}  \n"
                md_content += (
                    f"**Plural Name:** {table_info['verbose_name_plural']}  \n"
                )

                if table_info["ordering"]:
                    md_content += (
                        f"**Default Ordering:** {', '.join(table_info['ordering'])}  \n"
                    )

                md_content += "\n"

                # Fields table
                md_content += "#### Fields\n\n"
                md_content += "| Column | Type | DB Type | Null | Default | PK | Unique | Max Length | Description |\n"
                md_content += "|--------|------|---------|------|---------|----|---------|-----------|--------------|\n"

                for field in table_info["fields"]:
                    column = field["column"]
                    field_type = field["type"]
                    db_type = field["db_type"] or "-"
                    null = "✓" if field["null"] else "✗"
                    default = field["default"] or "-"
                    pk = "✓" if field["primary_key"] else "✗"
                    unique = "✓" if field["unique"] else "✗"
                    max_length = (
                        str(field["max_length"]) if field["max_length"] else "-"
                    )
                    help_text = field["help_text"] or "-"

                    md_content += f"| `{column}` | {field_type} | {db_type} | {null} | {default} | {pk} | {unique} | {max_length} | {help_text} |\n"

                # Relationships
                relationships = [f for f in table_info["fields"] if f["related_model"]]
                if relationships:
                    md_content += "\n#### Relationships\n\n"
                    md_content += "| Field | Type | Related Table |\n"
                    md_content += "|-------|------|---------------|\n"
                    for rel in relationships:
                        md_content += f"| `{rel['column']}` | {rel['relationship_type']} | `{rel['related_model']}` |\n"

                # Constraints and indexes
                if table_info["constraints"]:
                    md_content += "\n#### Constraints\n\n"
                    for constraint in table_info["constraints"]:
                        md_content += f"- {constraint}\n"

                if table_info["unique_together"]:
                    md_content += "\n#### Unique Together\n\n"
                    for unique_set in table_info["unique_together"]:
                        md_content += f"- {', '.join(unique_set)}\n"

                if table_info["indexes"]:
                    md_content += "\n#### Indexes\n\n"
                    for index in table_info["indexes"]:
                        md_content += f"- {index}\n"

                md_content += "\n---\n\n"

        # Add summary statistics
        md_content += "## Summary Statistics\n\n"
        md_content += f"| App | Tables | Total Fields |\n"
        md_content += f"|-----|--------|-------------|\n"

        for app_label in sorted(apps_tables.keys()):
            table_count = len(apps_tables[app_label])
            field_count = sum(
                len(table_info["fields"]) for _, table_info in apps_tables[app_label]
            )
            md_content += f"| {app_label} | {table_count} | {field_count} |\n"

        total_fields = sum(len(table_info["fields"]) for table_info in tables.values())
        md_content += f"| **Total** | **{len(tables)}** | **{total_fields}** |\n"

        # Write Markdown file
        md_path = output_dir / "DATABASE_SCHEMA.md"
        md_path.write_text(md_content, encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(f"✅ Markdown documentation written to: {md_path}")
        )

    def print_summary(self, tables):
        """Print summary statistics"""
        self.stdout.write(self.style.SUCCESS(f"\n📊 Summary:"))
        self.stdout.write(f"   • Total tables: {len(tables)}")
        self.stdout.write(
            f"   • Total fields: {sum(len(table_info['fields']) for table_info in tables.values())}"
        )
        self.stdout.write(
            f"   • Apps documented: {len(set(table_info['app_label'] for table_info in tables.values()))}"
        )
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Documentation generated successfully!")
        )
