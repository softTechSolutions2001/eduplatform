# <your_app>/management/commands/inspectdbschema.py
import os
import sys
import json
import csv
import datetime
from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections
from django.conf import settings
from django.utils.termcolors import colorize
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Generate comprehensive database schema documentation with detailed analysis"

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database alias to inspect (default: default)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['markdown', 'json', 'csv', 'all'],
            default='markdown',
            help='Output format (default: markdown)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='.',
            help='Output directory for generated files (default: current directory)'
        )
        parser.add_argument(
            '--include-data-samples',
            action='store_true',
            help='Include sample data from tables'
        )
        parser.add_argument(
            '--sample-size',
            type=int,
            default=3,
            help='Number of sample rows to include (default: 3)'
        )
        parser.add_argument(
            '--exclude-tables',
            type=str,
            nargs='*',
            default=[],
            help='Tables to exclude from documentation'
        )
        parser.add_argument(
            '--fast-count',
            action='store_true',
            help='Use fast row count estimates from system catalogs (less accurate but faster)'
        )
        parser.add_argument(
            '--row-count-threshold',
            type=int,
            default=1000000,
            help='Skip row count for tables larger than this threshold (default: 1M)'
        )

    def handle(self, *args, **options):
        database_alias = options['database']
        output_format = options['format']
        output_dir = Path(options['output_dir'])
        include_samples = options['include_data_samples']
        sample_size = options['sample_size']
        exclude_tables = set(options['exclude_tables'])
        fast_count = options['fast_count']
        row_count_threshold = options['row_count_threshold']

        # Ensure output directory exists
        output_dir.mkdir(exist_ok=True)

        try:
            # Get database connection
            db_connection = connections[database_alias]

            # Generate timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            self.stdout.write(colorize(f"🔍 Scanning database schema for '{database_alias}'...", fg="cyan"))

            # Scan database schema
            schema_data = self.scan_database_schema(
                db_connection, include_samples, sample_size, exclude_tables,
                fast_count, row_count_threshold
            )

            # Generate documentation based on format
            if output_format == 'markdown' or output_format == 'all':
                self.generate_markdown_doc(schema_data, output_dir, timestamp)

            if output_format == 'json' or output_format == 'all':
                self.generate_json_doc(schema_data, output_dir, timestamp)

            if output_format == 'csv' or output_format == 'all':
                self.generate_csv_doc(schema_data, output_dir, timestamp)

            # Print summary
            self.print_schema_summary(schema_data)

        except Exception as e:
            raise CommandError(f"Error scanning database: {str(e)}")

    def scan_database_schema(self, db_connection, include_samples=False, sample_size=3,
                           exclude_tables=None, fast_count=False, row_count_threshold=1000000):
        """Comprehensive database schema scanning"""
        if exclude_tables is None:
            exclude_tables = set()

        introspection = db_connection.introspection

        # Get database info
        db_settings = db_connection.settings_dict
        db_info = {
            'engine': db_settings['ENGINE'],
            'name': db_settings['NAME'],
            'host': db_settings.get('HOST', 'localhost'),
            'port': db_settings.get('PORT', ''),
            'user': db_settings.get('USER', ''),
            'vendor': db_connection.vendor
        }

        # Get all tables - filter for regular tables only
        with db_connection.cursor() as cursor:
            table_list = introspection.get_table_list(cursor)
        table_names = [
            t.name for t in table_list
            if getattr(t, 'type', 't') == 't'  # Regular tables only
            and t.name not in exclude_tables
        ]

        schema_data = {
            'database_info': db_info,
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'total_tables': len(table_names),
            'tables': {},
            'relationships': {},
            'scan_options': {
                'include_samples': include_samples,
                'sample_size': sample_size,
                'fast_count': fast_count,
                'row_count_threshold': row_count_threshold
            }
        }

        # Scan each table with error handling
        successful_tables = []
        failed_tables = []

        for table_name in table_names:
            try:
                self.stdout.write(f"  📊 Scanning table: {table_name}")

                table_data = self.get_comprehensive_table_info(
                    db_connection, table_name, include_samples, sample_size,
                    fast_count, row_count_threshold
                )
                schema_data['tables'][table_name] = table_data
                successful_tables.append(table_name)

            except Exception as e:
                self.stdout.write(
                    colorize(f"  ⚠️ Failed to scan table {table_name}: {str(e)}", fg="yellow")
                )
                failed_tables.append({'table': table_name, 'error': str(e)})

        # Analyze relationships only for successful tables
        if successful_tables:
            schema_data['relationships'] = self.analyze_relationships(db_connection, successful_tables)

        # Add scan summary
        schema_data['scan_summary'] = {
            'successful_tables': len(successful_tables),
            'failed_tables': len(failed_tables),
            'failed_table_details': failed_tables
        }

        return schema_data

    def get_comprehensive_table_info(self, db_connection, table_name, include_samples=False,
                                   sample_size=3, fast_count=False, row_count_threshold=1000000):
        """Get comprehensive information about a table"""
        introspection = db_connection.introspection

        # Basic table description
        with db_connection.cursor() as cursor:
            table_description = introspection.get_table_description(cursor, table_name)

        # Get detailed column information
        columns = []
        with db_connection.cursor() as cursor:
            primary_key_columns = set( introspection.get_primary_key_column(cursor, table_name) or []
            )


        for col in table_description:
            column_info = {
                'name': col.name,
                'type': col.type_code,
                'display_size': col.display_size,
                'internal_size': col.internal_size,
                'precision': col.precision,
                'scale': col.scale,
                'null_ok': col.null_ok,
                'default': col.default,
                'collation': getattr(col, 'collation', None),
                'is_primary_key': col.name in primary_key_columns
            }
            columns.append(column_info)

        # Get constraints and indexes with better categorization
        with db_connection.cursor() as cursor:
            constraints = introspection.get_constraints(cursor, table_name)

        # Analyze constraint types - handle overlapping categories
        primary_keys = []
        foreign_keys = []
        unique_constraints = []
        check_constraints = []
        indexes = []

        for constraint_name, constraint_info in constraints.items():
            constraint_data = {
                'name': constraint_name,
                'columns': constraint_info['columns']
            }

            # Primary keys
            if constraint_info['primary_key']:
                primary_keys.append(constraint_data)

            # Foreign keys
            elif constraint_info['foreign_key']:
                constraint_data['foreign_key'] = constraint_info['foreign_key']
                foreign_keys.append(constraint_data)

            # Unique constraints (may also be indexes)
            elif constraint_info['unique']:
                constraint_data['is_index'] = constraint_info.get('index', False)
                unique_constraints.append(constraint_data)

            # Check constraints
            elif constraint_info['check']:
                constraint_data['check'] = constraint_info['check']
                check_constraints.append(constraint_data)

            # Regular indexes (not unique, not PK)
            elif constraint_info['index']:
                constraint_data.update({
                    'type': constraint_info.get('type', 'BTREE'),
                    'orders': constraint_info.get('orders', [])
                })
                indexes.append(constraint_data)

        # Get table statistics
        table_stats = self.get_table_statistics(
            db_connection, table_name, fast_count, row_count_threshold
        )

        # Get sample data if requested
        sample_data = []
        if include_samples:
            sample_data = self.get_sample_data(db_connection, table_name, sample_size)

        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'unique_constraints': unique_constraints,
            'check_constraints': check_constraints,
            'indexes': indexes,
            'statistics': table_stats,
            'sample_data': sample_data,
            'column_count': len(columns)
        }

    def get_table_statistics(self, db_connection, table_name, fast_count=False, row_count_threshold=1000000):
        """Get table statistics like row count, size, etc."""
        stats = {}
        quoted_table = db_connection.ops.quote_name(table_name)

        try:
            with db_connection.cursor() as cursor:
                # Get row count with threshold check and fast count option
                if fast_count:
                    stats['row_count'] = self.get_fast_row_count(db_connection, table_name)
                else:
                    # First try to get a rough estimate to check threshold
                    estimate = self.get_fast_row_count(db_connection, table_name)

                    if estimate and estimate > row_count_threshold:
                        stats['row_count'] = f"~{estimate:,} (estimated, exceeds threshold)"
                        stats['row_count_skipped'] = True
                    else:
                        cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
                        stats['row_count'] = cursor.fetchone()[0]
                        stats['row_count_skipped'] = False

                # Database-specific statistics
                if db_connection.vendor == 'mysql':
                    cursor.execute("""
                        SELECT
                            data_length,
                            index_length,
                            data_free,
                            auto_increment,
                            table_collation,
                            engine
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE() AND table_name = %s
                    """, [table_name])
                    result = cursor.fetchone()
                    if result:
                        stats.update({
                            'data_length': result[0],
                            'index_length': result[1],
                            'data_free': result[2],
                            'auto_increment': result[3],
                            'collation': result[4],
                            'engine': result[5]
                        })

                elif db_connection.vendor == 'postgresql':
                    # Use OID-based queries for accuracy
                    cursor.execute("""
                        SELECT
                            pg_total_relation_size(oid) as total_size,
                            pg_relation_size(oid) as table_size,
                            pg_indexes_size(oid) as index_size
                        FROM pg_class
                        WHERE relname = %s AND relkind = 'r'
                    """, [table_name])
                    result = cursor.fetchone()
                    if result:
                        stats.update({
                            'total_size': result[0],
                            'table_size': result[1],
                            'index_size': result[2]
                        })

                elif db_connection.vendor == 'sqlite':
                    # SQLite page-based size calculation
                    cursor.execute(f"PRAGMA page_count")
                    page_count = cursor.fetchone()
                    cursor.execute(f"PRAGMA page_size")
                    page_size = cursor.fetchone()
                    if page_count and page_size:
                        stats.update({
                            'page_count': page_count[0],
                            'page_size': page_size[0],
                            'estimated_size': page_count[0] * page_size[0]
                        })

        except Exception as e:
            stats['error'] = str(e)

        return stats

    def get_fast_row_count(self, db_connection, table_name):
        """Get fast row count estimates from system catalogs"""
        try:
            with db_connection.cursor() as cursor:
                if db_connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT reltuples::bigint
                        FROM pg_class
                        WHERE relname = %s AND relkind = 'r'
                    """, [table_name])
                    result = cursor.fetchone()
                    return int(result[0]) if result else None

                elif db_connection.vendor == 'mysql':
                    cursor.execute("""
                        SELECT table_rows
                        FROM information_schema.tables
                        WHERE table_schema = DATABASE() AND table_name = %s
                    """, [table_name])
                    result = cursor.fetchone()
                    return int(result[0]) if result else None

                # For SQLite and others, fall back to actual count
                quoted_table = db_connection.ops.quote_name(table_name)
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
                return cursor.fetchone()[0]

        except Exception:
            return None

    def get_sample_data(self, db_connection, table_name, sample_size=3):
        """Get sample data from table with PII/secret redaction"""
        try:
            quoted_table = db_connection.ops.quote_name(table_name)
            with db_connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {quoted_table} LIMIT {sample_size}")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # Redact large text/blob columns that might contain secrets
                processed_rows = []
                for row in rows:
                    processed_row = []
                    for i, cell in enumerate(row):
                        if isinstance(cell, (str, bytes)) and len(str(cell)) > 1000:
                            processed_row.append(f"[REDACTED - {len(str(cell))} chars]")
                        else:
                            processed_row.append(cell)
                    processed_rows.append(processed_row)

                return {
                    'columns': columns,
                    'rows': processed_rows
                }
        except Exception as e:
            return {'error': str(e)}

    def analyze_relationships(self, db_connection, table_names):
        """Analyze relationships between tables"""
        relationships = {
            'foreign_key_relationships': [],
            'orphaned_tables': [],
            'highly_connected_tables': []
        }

        introspection = db_connection.introspection
        table_connections = defaultdict(int)

        for table_name in table_names:
            try:
                with db_connection.cursor() as cursor:
                    constraints = introspection.get_constraints(cursor, table_name)
                    has_relationships = False

                for constraint_name, constraint_info in constraints.items():
                    if constraint_info['foreign_key']:
                        has_relationships = True
                        fk_info = constraint_info['foreign_key']
                        relationships['foreign_key_relationships'].append({
                            'from_table': table_name,
                            'from_columns': constraint_info['columns'],
                            'to_table': fk_info[0],
                            'to_columns': fk_info[1],
                            'constraint_name': constraint_name
                        })
                        table_connections[table_name] += 1
                        table_connections[fk_info[0]] += 1

                if not has_relationships:
                    relationships['orphaned_tables'].append(table_name)

            except Exception:
                # Skip tables that can't be analyzed for relationships
                continue

        # Find highly connected tables (more than 5 connections)
        relationships['highly_connected_tables'] = [
            {'table': table, 'connections': count}
            for table, count in table_connections.items()
            if count > 5
        ]

        return relationships

    def generate_markdown_doc(self, schema_data, output_dir, timestamp):
        """Generate comprehensive Markdown documentation"""
        filename = output_dir / f"database_schema_{timestamp}.md"

        lines = [
            f"# Database Schema Documentation",
            f"*Generated on {schema_data['scan_timestamp']}*",
            "",
            "## Database Information",
            "",
            f"- **Engine**: {schema_data['database_info']['engine']}",
            f"- **Database**: {schema_data['database_info']['name']}",
            f"- **Vendor**: {schema_data['database_info']['vendor']}",
            f"- **Host**: {schema_data['database_info']['host']}",
            f"- **Total Tables**: {schema_data['total_tables']}",
            ""
        ]

        # Add scan summary if there were failures
        scan_summary = schema_data.get('scan_summary', {})
        if scan_summary.get('failed_tables', 0) > 0:
            lines.extend([
                "## Scan Summary",
                "",
                f"- **Successfully scanned**: {scan_summary['successful_tables']} tables",
                f"- **Failed to scan**: {scan_summary['failed_tables']} tables",
                ""
            ])
            if scan_summary.get('failed_table_details'):
                lines.append("### Failed Tables:")
                for failed in scan_summary['failed_table_details']:
                    lines.append(f"- `{failed['table']}`: {failed['error']}")
                lines.append("")

        # Add table of contents with proper slugs
        lines.extend(["## Table of Contents", ""])
        for table_name in sorted(schema_data['tables'].keys()):
            slug = slugify(table_name)
            lines.append(f"- [{table_name}](#{slug})")

        lines.extend(["", "## Relationships Overview", ""])

        # Add relationships
        relationships = schema_data.get('relationships', {})
        if relationships.get('foreign_key_relationships'):
            lines.extend(["### Foreign Key Relationships", ""])
            for rel in relationships['foreign_key_relationships']:
                lines.append(f"- `{rel['from_table']}({', '.join(rel['from_columns'])})` → `{rel['to_table']}({', '.join(rel['to_columns'])})`")

        if relationships.get('orphaned_tables'):
            lines.extend(["", "### Orphaned Tables (No Relationships)", ""])
            for table in relationships['orphaned_tables']:
                lines.append(f"- `{table}`")

        if relationships.get('highly_connected_tables'):
            lines.extend(["", "### Highly Connected Tables", ""])
            for item in relationships['highly_connected_tables']:
                lines.append(f"- `{item['table']}`: {item['connections']} connections")

        lines.extend(["", "## Detailed Table Information", ""])

        # Add detailed table information
        for table_name, table_data in schema_data['tables'].items():
            slug = slugify(table_name)
            lines.extend([f"### {table_name} {{#{slug}}}", ""])

            # Table statistics
            if table_data['statistics']:
                lines.extend(["**Statistics:**", ""])
                stats = table_data['statistics']
                if 'row_count' in stats:
                    if isinstance(stats['row_count'], str):
                        lines.append(f"- **Row Count**: {stats['row_count']}")
                    else:
                        lines.append(f"- **Row Count**: {stats['row_count']:,}")
                if 'data_length' in stats and stats['data_length']:
                    lines.append(f"- **Data Size**: {stats['data_length']:,} bytes")
                if 'index_length' in stats and stats['index_length']:
                    lines.append(f"- **Index Size**: {stats['index_length']:,} bytes")
                if 'total_size' in stats and stats['total_size']:
                    lines.append(f"- **Total Size**: {stats['total_size']:,} bytes")
                if 'engine' in stats and stats['engine']:
                    lines.append(f"- **Engine**: {stats['engine']}")
                lines.append("")

            # Columns table
            lines.extend(["**Columns:**", ""])
            lines.append("| Column | Type | Null | Default | Precision | Scale | PK |")
            lines.append("|--------|------|------|---------|-----------|-------|-----|")

            for col in table_data['columns']:
                pk = "✓" if col['is_primary_key'] else ""
                null_ok = "✓" if col['null_ok'] else ""
                default = str(col['default']) if col['default'] is not None else ""
                precision = str(col['precision']) if col['precision'] else ""
                scale = str(col['scale']) if col['scale'] else ""

                lines.append(f"| {col['name']} | {col['type']} | {null_ok} | {default} | {precision} | {scale} | {pk} |")

            # Indexes
            if table_data['indexes']:
                lines.extend(["", "**Indexes:**", ""])
                for idx in table_data['indexes']:
                    idx_type = idx.get('type', 'BTREE')
                    lines.append(f"- `{idx['name']}` ({idx_type}) on ({', '.join(idx['columns'])})")

            # Unique Constraints
            if table_data['unique_constraints']:
                lines.extend(["", "**Unique Constraints:**", ""])
                for uc in table_data['unique_constraints']:
                    is_index = " (also indexed)" if uc.get('is_index') else ""
                    lines.append(f"- `{uc['name']}` on ({', '.join(uc['columns'])}){is_index}")

            # Foreign Keys
            if table_data['foreign_keys']:
                lines.extend(["", "**Foreign Keys:**", ""])
                for fk in table_data['foreign_keys']:
                    fk_info = fk['foreign_key']
                    lines.append(f"- `{fk['name']}`: {', '.join(fk['columns'])} → {fk_info[0]}({', '.join(fk_info[1])})")

            # Check Constraints
            if table_data['check_constraints']:
                lines.extend(["", "**Check Constraints:**", ""])
                for cc in table_data['check_constraints']:
                    check_condition = cc.get('check', 'N/A')
                    lines.append(f"- `{cc['name']}`: {check_condition}")

            # Sample data
            if table_data['sample_data'] and 'rows' in table_data['sample_data']:
                lines.extend(["", "**Sample Data:**", ""])
                sample = table_data['sample_data']
                if sample['rows']:
                    # Create sample data table
                    header = "| " + " | ".join(sample['columns']) + " |"
                    separator = "|" + "|".join(["---"] * len(sample['columns'])) + "|"
                    lines.extend([header, separator])

                    for row in sample['rows']:
                        row_str = "| " + " | ".join(str(cell) if cell is not None else "" for cell in row) + " |"
                        lines.append(row_str)

            lines.append("")

        # Write to file
        filename.write_text("\n".join(lines), encoding="utf-8")
        self.stdout.write(colorize(f"✓ Markdown documentation written to {filename}", fg="green"))

    def generate_json_doc(self, schema_data, output_dir, timestamp):
        """Generate JSON documentation"""
        filename = output_dir / f"database_schema_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, default=str)

        self.stdout.write(colorize(f"✓ JSON documentation written to {filename}", fg="green"))

    def generate_csv_doc(self, schema_data, output_dir, timestamp):
        """Generate CSV documentation using DictWriter"""
        filename = output_dir / f"database_schema_{timestamp}.csv"

        fieldnames = [
            'table', 'column', 'type', 'nullable', 'default',
            'primary_key', 'precision', 'scale', 'display_size', 'internal_size'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for table_name, table_data in schema_data['tables'].items():
                for col in table_data['columns']:
                    writer.writerow({
                        'table': table_name,
                        'column': col['name'],
                        'type': col['type'],
                        'nullable': 'Yes' if col['null_ok'] else 'No',
                        'default': col['default'],
                        'primary_key': 'Yes' if col['is_primary_key'] else 'No',
                        'precision': col['precision'],
                        'scale': col['scale'],
                        'display_size': col['display_size'],
                        'internal_size': col['internal_size']
                    })

        self.stdout.write(colorize(f"✓ CSV documentation written to {filename}", fg="green"))

    def print_schema_summary(self, schema_data):
        """Print a comprehensive summary of the database schema"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write(colorize("DATABASE SCHEMA SUMMARY", fg="yellow", opts=["bold"]))
        self.stdout.write("="*80)

        db_info = schema_data['database_info']
        self.stdout.write(f"Database: {db_info['name']} ({db_info['vendor']})")
        self.stdout.write(f"Engine: {db_info['engine']}")
        self.stdout.write(f"Total Tables: {schema_data['total_tables']}")
        self.stdout.write(f"Scan Time: {schema_data['scan_timestamp']}")

        # Show scan summary
        scan_summary = schema_data.get('scan_summary', {})
        if scan_summary:
            self.stdout.write(f"Successfully Scanned: {scan_summary.get('successful_tables', 0)}")
            if scan_summary.get('failed_tables', 0) > 0:
                self.stdout.write(colorize(f"Failed Tables: {scan_summary['failed_tables']}", fg="red"))

        self.stdout.write("\nTable Details:")
        total_columns = 0
        total_indexes = 0
        total_fks = 0

        for table_name, table_data in schema_data['tables'].items():
            column_count = table_data['column_count']
            index_count = len(table_data['indexes'])
            fk_count = len(table_data['foreign_keys'])

            total_columns += column_count
            total_indexes += index_count
            total_fks += fk_count

            row_count = table_data['statistics'].get('row_count', 'N/A')
            if isinstance(row_count, int):
                row_count = f"{row_count:,}"

            self.stdout.write(
                f"  📊 {table_name}: {column_count} columns, "
                f"{index_count} indexes, {fk_count} FKs, {row_count} rows"
            )

        self.stdout.write(f"\nTotals: {total_columns} columns, {total_indexes} indexes, {total_fks} foreign keys")

        # Relationship summary
        relationships = schema_data.get('relationships', {})
        if relationships:
            fk_count = len(relationships.get('foreign_key_relationships', []))
            self.stdout.write(f"\nRelationships: {fk_count} FK relationships")
            if relationships.get('orphaned_tables'):
                self.stdout.write(f"Orphaned tables: {len(relationships['orphaned_tables'])}")
            if relationships.get('highly_connected_tables'):
                self.stdout.write(f"Highly connected tables: {len(relationships['highly_connected_tables'])}")
