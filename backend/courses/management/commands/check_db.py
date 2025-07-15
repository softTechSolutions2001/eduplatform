import json
import os
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

# python manage.py check_db --all-apps --export-md report.md


class Command(BaseCommand):
    help = "Generic database column checker and query tester for any Django project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md_output = []
        self.export_to_md = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--table", type=str, help="Specific table to check (e.g., myapp_mymodel)"
        )
        parser.add_argument(
            "--column", type=str, help="Specific column to check (use with --table)"
        )
        parser.add_argument(
            "--app", type=str, help="Check all tables for a specific app (e.g., myapp)"
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Check specific model (format: app.Model, e.g., myapp.MyModel)",
        )
        parser.add_argument(
            "--all-apps", action="store_true", help="Check all installed apps"
        )
        parser.add_argument(
            "--test-query",
            type=str,
            help="Test a specific query (format: app.Model:field1,field2)",
        )
        parser.add_argument(
            "--config-file",
            type=str,
            help="Path to JSON config file with columns/queries to check",
        )
        parser.add_argument(
            "--skip-system-apps",
            action="store_true",
            help="Skip Django system apps (admin, auth, contenttypes, etc.)",
        )
        parser.add_argument(
            "--export-schema",
            type=str,
            help="Export database schema to file (JSON format)",
        )
        parser.add_argument(
            "--export-md",
            type=str,
            help="Export results to markdown file",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output including column types and constraints",
        )
        parser.add_argument(
            "--batch-check",
            action="store_true",
            help="Use batch queries for better performance (recommended for large schemas)",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        self.batch_check = options["batch_check"]
        self.export_to_md = bool(options.get("export_md"))
        self.md_file_path = options.get("export_md")

        if self.export_to_md:
            self.md_output = []
            self.add_md_header()

        self.write_output("=== GENERIC DATABASE CHECKER ===", "SUCCESS")

        # Export schema if requested
        if options["export_schema"]:
            self.export_database_schema(options["export_schema"])
            if self.export_to_md:
                self.write_md_file()
            return

        # Load config file if provided
        config = self.load_config_file(options.get("config_file"))

        # Execute based on options
        if options["table"] and options["column"]:
            self.check_specific_column(options["table"], options["column"])
        elif options["model"]:
            self.check_specific_model(options["model"])
        elif options["app"]:
            self.check_app_tables(options["app"], options["skip_system_apps"])
        elif options["all_apps"]:
            self.check_all_apps(options["skip_system_apps"])
        elif options["test_query"]:
            self.test_specific_query(options["test_query"])
        elif config:
            self.check_from_config(config)
        else:
            self.show_help()

        self.write_output("\n=== CHECK COMPLETE ===", "SUCCESS")

        # Write markdown file if requested
        if self.export_to_md:
            self.write_md_file()

    def add_md_header(self):
        """Add markdown header with metadata"""
        self.md_output.append("# Database Check Report")
        self.md_output.append("")
        self.md_output.append(
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.md_output.append(f"**Database:** {connection.vendor}")
        self.md_output.append("")
        self.md_output.append("---")
        self.md_output.append("")

    def write_output(self, message, style=None):
        """Write to both console and markdown buffer"""
        if style == "SUCCESS":
            self.stdout.write(self.style.SUCCESS(message))
        elif style == "ERROR":
            self.stdout.write(self.style.ERROR(message))
        else:
            self.stdout.write(message)

        if self.export_to_md:
            # Clean up styling markers for markdown
            clean_message = message.replace("✅", "✅").replace("❌", "❌")
            self.md_output.append(clean_message)

    def write_md_section(self, title, level=2):
        """Add a markdown section header"""
        if self.export_to_md:
            self.md_output.append("")
            self.md_output.append("#" * level + " " + title)
            self.md_output.append("")

    def write_md_file(self):
        """Write the markdown output to file"""
        try:
            with open(self.md_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.md_output))
            self.stdout.write(
                self.style.SUCCESS(f"✅ Report exported to: {self.md_file_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to write markdown file: {e}")
            )

    def load_config_file(self, config_path):
        """Load configuration from JSON file"""
        if not config_path:
            return None

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            self.write_output(f"Loaded configuration from: {config_path}")
            return config
        except FileNotFoundError:
            self.write_output(f"Config file not found: {config_path}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            self.write_output(f"Invalid JSON in config file: {e}", "ERROR")
            return None

    def check_from_config(self, config):
        """Check database based on configuration file"""
        # Check specific columns
        if "columns" in config:
            self.write_md_section("Configured Columns Check")
            self.write_output("--- CHECKING CONFIGURED COLUMNS ---", "SUCCESS")
            for item in config["columns"]:
                table = item.get("table")
                column = item.get("column")
                if table and column:
                    self.check_specific_column(table, column)

        # Check models
        if "models" in config:
            self.write_md_section("Configured Models Check")
            self.write_output("--- CHECKING CONFIGURED MODELS ---", "SUCCESS")
            for model_path in config["models"]:
                self.check_specific_model(model_path)

        # Test queries
        if "queries" in config:
            self.write_md_section("Configured Queries Test")
            self.write_output("--- TESTING CONFIGURED QUERIES ---", "SUCCESS")
            for query in config["queries"]:
                self.test_specific_query(query)

    def check_specific_column(self, table_name, column_name):
        """Check if a specific column exists in a table"""
        exists = self.check_column_exists_safe(table_name, column_name)
        if exists:
            self.write_output(f"✅ Column {table_name}.{column_name} exists", "SUCCESS")
            if self.verbose:
                self.get_column_info_safe(table_name, column_name)
        else:
            self.write_output(
                f"❌ Column {table_name}.{column_name} does not exist", "ERROR"
            )

    def check_specific_model(self, model_path):
        """Check a specific model (format: app.Model)"""
        try:
            app_name, model_name = model_path.split(".")
            model = apps.get_model(app_name, model_name)
            table_name = model._meta.db_table

            self.write_md_section(f"Model: {model_path}", 3)
            self.write_output(f"\nChecking model: {model_path} (table: {table_name})")

            if self.check_table_exists_safe(table_name):
                self.write_output(f"✅ Table {table_name} exists", "SUCCESS")

                # Get all columns for this table in one query if using batch mode
                if self.batch_check:
                    existing_columns = self.get_table_columns_batch(table_name)

                # Check each field
                for field in model._meta.concrete_fields:
                    column_name = field.column

                    if self.batch_check:
                        exists = column_name in existing_columns
                    else:
                        exists = self.check_column_exists_safe(table_name, column_name)

                    if exists:
                        field_type = field.__class__.__name__
                        self.write_output(f"  ✅ {column_name} ({field_type})")
                    else:
                        self.write_output(f"  ❌ {column_name} MISSING", "ERROR")
            else:
                self.write_output(f"❌ Table {table_name} does not exist", "ERROR")

        except ValueError:
            self.write_output(
                f"❌ Invalid model format: {model_path}. Use app.Model format.", "ERROR"
            )
        except LookupError:
            self.write_output(f'❌ Model "{model_path}" not found', "ERROR")

    def check_app_tables(self, app_name, skip_system=False):
        """Check all tables for a specific app"""
        try:
            app_models = apps.get_app_config(app_name).get_models()
            self.write_md_section(f"App: {app_name}")
            self.write_output(f"Checking tables for app: {app_name}")

            # Get all tables and columns in batch if using batch mode
            if self.batch_check:
                all_tables = [model._meta.db_table for model in app_models]
                table_columns_map = self.get_multiple_tables_columns_batch(all_tables)

            for model in app_models:
                table_name = model._meta.db_table
                model_name = model.__name__

                self.write_md_section(f"Model: {model_name}", 3)
                self.write_output(
                    f"\nChecking model: {model_name} (table: {table_name})"
                )

                if self.batch_check:
                    table_exists = table_name in table_columns_map
                    existing_columns = table_columns_map.get(table_name, set())
                else:
                    table_exists = self.check_table_exists_safe(table_name)
                    existing_columns = None

                if table_exists:
                    self.write_output(f"✅ Table {table_name} exists", "SUCCESS")

                    # Check each field
                    for field in model._meta.concrete_fields:
                        column_name = field.column
                        field_type = field.__class__.__name__

                        if self.batch_check:
                            exists = column_name in existing_columns
                        else:
                            exists = self.check_column_exists_safe(
                                table_name, column_name
                            )

                        if exists:
                            if self.verbose:
                                self.write_output(f"  ✅ {column_name} ({field_type})")
                            else:
                                self.write_output(f"  ✅ {column_name}")
                        else:
                            self.write_output(
                                f"  ❌ {column_name} MISSING ({field_type})", "ERROR"
                            )
                else:
                    self.write_output(f"❌ Table {table_name} does not exist", "ERROR")

        except LookupError:
            self.write_output(f'❌ App "{app_name}" not found', "ERROR")

    def check_all_apps(self, skip_system=False):
        """Check all installed apps"""
        system_apps = self.get_system_apps()
        all_apps = apps.get_app_configs()

        self.write_md_section("All Apps Check")

        for app_config in all_apps:
            app_name = app_config.name.split(".")[-1]
            full_app_name = app_config.name

            if skip_system and (
                app_name in system_apps or full_app_name.startswith("django.")
            ):
                continue

            if app_config.models:  # Only check apps that have models
                self.write_output(f'\n{"="*50}')
                self.check_app_tables(app_name, skip_system)

    def get_system_apps(self):
        """Get comprehensive list of Django system apps"""
        return {
            "admin",
            "auth",
            "contenttypes",
            "sessions",
            "messages",
            "staticfiles",
            "sites",
            "flatpages",
            "redirects",
            "humanize",
            "syndication",
            "sitemaps",
            "postgres",
            "gis",
            "admindocs",
            "django_celery_beat",
            "django_celery_results",
            "corsheaders",
            "rest_framework",
            "rest_framework_simplejwt",
            "django_extensions",
        }

    def test_specific_query(self, query_string):
        """Test a specific query (format: app.Model:field1,field2)"""
        try:
            model_part, fields_part = query_string.split(":")
            app_name, model_name = model_part.split(".")
            fields = [f.strip() for f in fields_part.split(",")]

            model = apps.get_model(app_name, model_name)

            # Test the query
            queryset = model.objects.values(*fields)[:5]
            result_list = list(queryset)

            self.write_output(
                f"✅ Query on {model_name} works, found {len(result_list)} records",
                "SUCCESS",
            )

            # Show sample data if available
            if result_list and self.verbose:
                self.write_output("Sample data:")
                for i, record in enumerate(result_list[:2]):
                    self.write_output(f"  Record {i+1}: {record}")

            return True

        except Exception as e:
            self.write_output(f"❌ Query failed: {e}", "ERROR")
            return False

    def check_table_exists_safe(self, table_name):
        """Safely check if a table exists using information_schema"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = %s AND table_schema = 'public'
                    """,
                        [table_name],
                    )
                elif connection.vendor == "mysql":
                    cursor.execute(
                        """
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = %s AND table_schema = DATABASE()
                    """,
                        [table_name],
                    )
                elif connection.vendor == "sqlite":
                    cursor.execute(
                        """
                        SELECT 1 FROM sqlite_master
                        WHERE type = 'table' AND name = %s
                    """,
                        [table_name],
                    )
                else:
                    # Fallback for other databases
                    cursor.execute("SELECT 1 FROM %s LIMIT 1", [table_name])

                return cursor.fetchone() is not None
        except Exception:
            return False

    def check_column_exists_safe(self, table_name, column_name):
        """Safely check if a column exists using information_schema"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = %s AND column_name = %s
                        AND table_schema = 'public'
                    """,
                        [table_name, column_name],
                    )
                elif connection.vendor == "mysql":
                    cursor.execute(
                        """
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = %s AND column_name = %s
                        AND table_schema = DATABASE()
                    """,
                        [table_name, column_name],
                    )
                elif connection.vendor == "sqlite":
                    cursor.execute("PRAGMA table_info(%s)", [table_name])
                    columns = cursor.fetchall()
                    return any(col[1] == column_name for col in columns)
                else:
                    # Fallback
                    cursor.execute(
                        "SELECT %s FROM %s LIMIT 1", [column_name, table_name]
                    )

                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_table_columns_batch(self, table_name):
        """Get all columns for a table in one query"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = 'public'
                    """,
                        [table_name],
                    )
                elif connection.vendor == "mysql":
                    cursor.execute(
                        """
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = DATABASE()
                    """,
                        [table_name],
                    )
                elif connection.vendor == "sqlite":
                    cursor.execute("PRAGMA table_info(%s)", [table_name])
                    return {col[1] for col in cursor.fetchall()}

                return {row[0] for row in cursor.fetchall()}
        except Exception:
            return set()

    def get_multiple_tables_columns_batch(self, table_names):
        """Get columns for multiple tables in one query"""
        if not table_names:
            return {}

        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    placeholders = ",".join(["%s"] * len(table_names))
                    cursor.execute(
                        f"""
                        SELECT table_name, column_name
                        FROM information_schema.columns
                        WHERE table_name IN ({placeholders}) AND table_schema = 'public'
                    """,
                        table_names,
                    )
                elif connection.vendor == "mysql":
                    placeholders = ",".join(["%s"] * len(table_names))
                    cursor.execute(
                        f"""
                        SELECT table_name, column_name
                        FROM information_schema.columns
                        WHERE table_name IN ({placeholders}) AND table_schema = DATABASE()
                    """,
                        table_names,
                    )
                elif connection.vendor == "sqlite":
                    # SQLite doesn't have information_schema, fall back to individual queries
                    result = {}
                    for table_name in table_names:
                        result[table_name] = self.get_table_columns_batch(table_name)
                    return result

                result = {}
                for table_name, column_name in cursor.fetchall():
                    if table_name not in result:
                        result[table_name] = set()
                    result[table_name].add(column_name)

                return result
        except Exception:
            return {}

    def get_column_info_safe(self, table_name, column_name):
        """Get detailed information about a column safely"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT data_type, is_nullable, column_default,
                               character_maximum_length, numeric_precision, numeric_scale
                        FROM information_schema.columns
                        WHERE table_name = %s AND column_name = %s AND table_schema = 'public'
                    """,
                        [table_name, column_name],
                    )
                    result = cursor.fetchone()
                    if result:
                        (
                            data_type,
                            is_nullable,
                            default,
                            max_length,
                            precision,
                            scale,
                        ) = result
                        info = f"    Type: {data_type}"
                        if max_length:
                            info += f"({max_length})"
                        elif precision:
                            info += f"({precision}"
                            if scale:
                                info += f",{scale}"
                            info += ")"
                        info += f", Nullable: {is_nullable}, Default: {default}"
                        self.write_output(info)

                elif connection.vendor == "mysql":
                    cursor.execute(
                        """
                        SELECT DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT,
                               CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = %s AND COLUMN_NAME = %s AND TABLE_SCHEMA = DATABASE()
                    """,
                        [table_name, column_name],
                    )
                    result = cursor.fetchone()
                    if result:
                        (
                            data_type,
                            is_nullable,
                            default,
                            max_length,
                            precision,
                            scale,
                        ) = result
                        info = f"    Type: {data_type}"
                        if max_length:
                            info += f"({max_length})"
                        elif precision:
                            info += f"({precision}"
                            if scale:
                                info += f",{scale}"
                            info += ")"
                        info += f", Nullable: {is_nullable}, Default: {default}"
                        self.write_output(info)

                elif connection.vendor == "sqlite":
                    cursor.execute("PRAGMA table_info(%s)", [table_name])
                    columns = cursor.fetchall()
                    for col in columns:
                        if col[1] == column_name:
                            self.write_output(
                                f"    Type: {col[2]}, Nullable: {not col[3]}, Default: {col[4]}"
                            )
                            break

        except Exception as e:
            self.write_output(f"    Could not get column details: {e}")

    def export_database_schema(self, output_file):
        """Export database schema to JSON file with enhanced information"""
        schema = {}

        try:
            all_apps = apps.get_app_configs()

            for app_config in all_apps:
                app_name = app_config.name.split(".")[-1]

                if app_config.models:
                    schema[app_name] = {}

                    for model in app_config.models.values():
                        table_name = model._meta.db_table
                        schema[app_name][model.__name__] = {
                            "table": table_name,
                            "fields": {},
                            "meta": {
                                "ordering": (
                                    list(model._meta.ordering)
                                    if model._meta.ordering
                                    else []
                                ),
                                "unique_together": list(model._meta.unique_together),
                                "indexes": [idx.name for idx in model._meta.indexes],
                                "constraints": [
                                    constraint.name
                                    for constraint in model._meta.constraints
                                ],
                            },
                        }

                        for field in model._meta.concrete_fields:
                            field_info = {
                                "column": field.column,
                                "type": field.__class__.__name__,
                                "null": field.null,
                                "blank": field.blank,
                                "primary_key": field.primary_key,
                                "unique": field.unique,
                            }

                            # Add foreign key information
                            if hasattr(field, "related_model") and field.related_model:
                                field_info["foreign_key"] = {
                                    "model": f"{field.related_model._meta.app_label}.{field.related_model.__name__}",
                                    "table": field.related_model._meta.db_table,
                                }

                            # Add choices if available
                            if hasattr(field, "choices") and field.choices:
                                field_info["choices"] = field.choices

                            schema[app_name][model.__name__]["fields"][
                                field.name
                            ] = field_info

            with open(output_file, "w") as f:
                json.dump(schema, f, indent=2)

            self.write_output(
                f"✅ Enhanced schema exported to: {output_file}", "SUCCESS"
            )

        except Exception as e:
            self.write_output(f"❌ Failed to export schema: {e}", "ERROR")

    def show_help(self):
        """Show usage examples"""
        self.write_md_section("Usage Examples")
        self.write_output("=== USAGE EXAMPLES ===", "SUCCESS")
        self.write_output("Check specific column:")
        self.write_output(
            "  python manage.py check_db --table myapp_mymodel --column field_name"
        )
        self.write_output("\nCheck specific model:")
        self.write_output("  python manage.py check_db --model myapp.MyModel")
        self.write_output("\nCheck all tables in an app:")
        self.write_output("  python manage.py check_db --app myapp")
        self.write_output("\nCheck all apps (skip system apps, use batch mode):")
        self.write_output(
            "  python manage.py check_db --all-apps --skip-system-apps --batch-check"
        )
        self.write_output("\nTest a specific query:")
        self.write_output(
            '  python manage.py check_db --test-query "myapp.MyModel:field1,field2"'
        )
        self.write_output("\nUse config file:")
        self.write_output(
            "  python manage.py check_db --config-file db_check_config.json"
        )
        self.write_output("\nExport enhanced schema:")
        self.write_output("  python manage.py check_db --export-schema schema.json")
        self.write_output("\nExport results to markdown:")
        self.write_output(
            "  python manage.py check_db --all-apps --export-md report.md"
        )
        self.write_output("\nVerbose output with batch checking:")
        self.write_output(
            "  python manage.py check_db --all-apps --verbose --batch-check --export-md detailed_report.md"
        )

        # Show config file example
        self.write_md_section("Config File Example")
        self.write_output("=== CONFIG FILE EXAMPLE ===", "SUCCESS")
        config_example = {
            "columns": [
                {"table": "myapp_mymodel", "column": "field_name"},
                {"table": "otherapp_model", "column": "another_field"},
            ],
            "models": ["myapp.MyModel", "otherapp.AnotherModel"],
            "queries": [
                "myapp.MyModel:id,name,created_at",
                "otherapp.AnotherModel:title,slug",
            ],
        }
        self.write_output(json.dumps(config_example, indent=2))

        self.write_md_section("Performance Tips")
        self.write_output("=== PERFORMANCE TIPS ===", "SUCCESS")
        self.write_output("• Use --batch-check for large schemas (faster)")
        self.write_output("• Use --skip-system-apps to focus on your code")
        self.write_output("• Use config files for CI/CD pipelines")
        self.write_output("• Use --export-md for documentation and reporting")
        self.write_output("• PostgreSQL users: batch mode is highly recommended")
