import os
import django
from django.conf import settings
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
from django.core.management.base import BaseCommand
from django.utils.log import configure_logging
import sys
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, OrderedDict


class EndpointExtractor:
    """
    Enhanced Django endpoint extractor with improved error handling, deduplication, and canonicalization
    """

    # OPTIMIZATION 1: Pre-compile all regex patterns for performance
    CANON_REGEXPS = [
        # First, normalize escaped dots and backslashes (CRITICAL: must be first)
        (re.compile(r'\\.'), '.'),  # Un-escape dots before format regex runs
        (re.compile(r'\\'), ''),    # Remove any other stray backslashes
        # Tighter format suffix matching (handles both escaped and unescaped)
        (re.compile(r'\\?\.<[A-Za-z0-9_-]+>/?$'), ''),
        # Remove <drf_format_suffix:format> placeholder
        (re.compile(r'<drf_format_suffix:format>'), ''),
        # Mixed parameter + format (<pk>.<format> etc.) - handles both escaped and unescaped
        (re.compile(r'(<[^>]+>)\\?\.<[^/]+>/?$'), r'\1'),
        # Normalize converter patterns to consistent format
        (re.compile(r'<slug:(\w+)>'), '<slug>'),
        (re.compile(r'<str:(\w+)>'), '<str>'),
        (re.compile(r'<int:(\w+)>'), '<int>'),
        (re.compile(r'<uuid:(\w+)>'), '<uuid>'),
        (re.compile(r'<pk:(\w+)>'), '<int>'),
        # Handle named groups - convert (?P<name>pattern) to <name>
        (re.compile(r'\(\?P<(\w+)>[^)]+\)'), r'<\1>'),
        # Handle anonymous groups
        (re.compile(r'\([^)]+\)'), '<group>'),
        # More conservative regex replacements
        (re.compile(r'\\d\+'), '<int>'),                     # escaped digits
        (re.compile(r'\d\+'), '<int>'),                      # unescaped digits
        (re.compile(r'\[0-9\]\+'), '<int>'),                 # digit classes
        (re.compile(r'\[^/\]\+'), '<str>'),                  # non-slash characters
        (re.compile(r'\[\\w-\]\+'), '<slug>'),               # word characters and hyphens
        (re.compile(r'\[0-9a-f-\]\+'), '<uuid>'),            # UUID patterns
        (re.compile(r'\\w\+'), '<str>'),                     # escaped word characters
        # Collapse multiple slashes
        (re.compile(r'/+'), '/'),
    ]

    def __init__(self, settings_module: str = None):
        self.settings_module = settings_module or 'educore.settings'
        self.setup_django()

    def setup_django(self):
        """Setup Django if not already configured with better error handling"""
        try:
            if not settings.configured:
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.settings_module)
                # Suppress deprecated DB check warnings
                os.environ.setdefault('DJANGO_SUPPRESS_DEPRECATED_DB_CHECK', '1')

                # Configure logging to prevent duplicate warnings
                try:
                    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
                except Exception:
                    pass  # Fallback if logging config fails

                django.setup()
        except Exception as e:
            print(f"❌ Error setting up Django: {e}")
            print("Make sure DJANGO_SETTINGS_MODULE is correct and all dependencies are installed")
            sys.exit(1)

    def get_view_name(self, pattern: URLPattern) -> str:
        """
        Get view name/function from pattern with enhanced detection
        """
        if not hasattr(pattern, 'callback'):
            return 'Unknown'

        callback = pattern.callback

        # Check for view_class (CBV)
        if hasattr(callback, 'view_class'):
            return callback.view_class.__name__

        # Check for cls (Django 5.0+ async-class views)
        elif hasattr(callback, 'cls'):
            return callback.cls.__name__

        # Check for __name__ (FBV)
        elif hasattr(callback, '__name__'):
            return callback.__name__

        # Check for view function in wrapped decorators
        elif hasattr(callback, 'view_func') and hasattr(callback.view_func, '__name__'):
            return callback.view_func.__name__

        # Fallback to string representation
        else:
            return str(callback).split(' ')[1] if ' ' in str(callback) else str(callback)

    def get_http_methods(self, pattern: URLPattern) -> List[str]:
        """
        Extract HTTP methods from view with improved detection and lazy DRF handling
        """
        if not hasattr(pattern, 'callback'):
            return ['GET']

        callback = pattern.callback
        methods = []

        # Class-based views
        if hasattr(callback, 'view_class'):
            view_class = callback.view_class
            if hasattr(view_class, 'http_method_names'):
                # Only include methods that are actually implemented
                methods = [m.upper() for m in view_class.http_method_names
                          if m.lower() not in ['options', 'head', 'trace'] and
                          hasattr(view_class, m.lower())]

        # Django 5.0+ async-class views
        elif hasattr(callback, 'cls'):
            view_class = callback.cls
            if hasattr(view_class, 'http_method_names'):
                # Only include methods that are actually implemented
                methods = [m.upper() for m in view_class.http_method_names
                          if m.lower() not in ['options', 'head', 'trace'] and
                          hasattr(view_class, m.lower())]

        # Function-based view with @require_* decorator
        elif hasattr(callback, 'allowed_methods'):
            methods = [m.upper() for m in callback.allowed_methods
                      if m.upper() not in ['OPTIONS', 'TRACE']]

        # Check for Django REST Framework ViewSet with lazy evaluation
        elif hasattr(callback, 'actions'):
            try:
                # DRF ViewSet - get methods from actions (actual mapped methods)
                action_methods = {m.upper() for m in callback.actions.keys()}
                methods = list(action_methods)
            except Exception:
                # Fallback if DRF viewset evaluation fails (e.g., DB access)
                methods = ['GET']

        # Default for function-based views (most only handle GET)
        return methods if methods else ['GET']

    def canonicalize_url(self, url: str) -> str:
        """
        Canonicalize URL pattern using pre-compiled regexes for performance
        FIX 1️⃣: Strip literal "/?" BEFORE running the heavy regexes
        """
        if not url:
            return '/'

        # 0️⃣ quick cleans – these must run **before** the big regex loop
        url = url.replace(r'\.', '.')            # un-escape "\."
        url = re.sub(r'/\?$', '', url)           # ⚡ strip a trailing "/?"
        url = url.replace('\\', '')              # remove stray back-slashes

        # 1️⃣-4️⃣ heavy canonicalisation
        for pattern, replacement in self.CANON_REGEXPS:
            url = pattern.sub(replacement, url)

        # Trailing slash normalization (keep this separate for clarity)
        url = url.rstrip('/') or '/'

        # Ensure it starts with /
        if not url.startswith('/'):
            url = '/' + url

        return url

    def clean_url_pattern(self, pattern_str: str) -> str:
        """
        Clean up URL pattern for better readability - Enhanced version with canonicalization
        """
        pattern_str = str(pattern_str)

        # Remove regex anchors but keep static parts
        pattern_str = pattern_str.lstrip('^').rstrip('$')

        return self.canonicalize_url(pattern_str)

    def extract_urls(self, urlpatterns, prefix: str = '', namespace: str = '',
                    skip_admin: bool = False) -> List[Dict[str, Any]]:
        """
        Recursively extract all URL patterns with enhanced error handling and canonicalization
        IMPROVEMENT 2: Add skip_admin parameter for cleaner output
        """
        endpoints = []

        for pattern in urlpatterns:
            try:
                if isinstance(pattern, URLResolver):
                    # This is an include() - recurse into it
                    new_prefix = prefix + self.clean_url_pattern(pattern.pattern)
                    new_prefix = self.canonicalize_url(new_prefix)

                    # IMPROVEMENT 2: Skip admin patterns if requested
                    if skip_admin and any(new_prefix.startswith(admin_prefix)
                                        for admin_prefix in ['/admin/', '/grappelli/']):
                        continue

                    new_namespace = namespace
                    if pattern.namespace:
                        new_namespace = f"{namespace}:{pattern.namespace}" if namespace else pattern.namespace

                    # Handle potential lazy loading of URL patterns
                    try:
                        nested_patterns = pattern.url_patterns
                    except Exception as e:
                        print(f"⚠️  Warning: Could not load patterns for {new_prefix}: {e}")
                        continue

                    endpoints.extend(self.extract_urls(nested_patterns, new_prefix, new_namespace, skip_admin))

                elif isinstance(pattern, URLPattern):
                    # This is a regular URL pattern
                    # FIX 3️⃣: Apply canonicalization earlier in the pipeline
                    url = self.canonicalize_url(
                        prefix + self.clean_url_pattern(pattern.pattern)
                    )

                    # IMPROVEMENT 2: Skip admin patterns if requested
                    if skip_admin and any(url.startswith(admin_prefix)
                                        for admin_prefix in ['/admin/', '/grappelli/']):
                        continue

                    # Get additional info with error handling
                    try:
                        view_name = self.get_view_name(pattern)

                        # Filter RedirectView immediately
                        if view_name == 'RedirectView':
                            continue

                        methods = self.get_http_methods(pattern)
                        name = pattern.name if pattern.name else 'unnamed'

                        # Check if this is a DRF endpoint
                        is_api = self.is_api_endpoint(pattern)

                        # Create one endpoint per method for proper aggregation
                        for method in methods:
                            endpoint_info = {
                                'url': url,
                                'name': name,
                                'view': view_name,
                                'method': method,  # Single method per record
                                'namespace': namespace,
                                'is_api': is_api,
                                'pattern_type': 'URLPattern'
                            }
                            endpoints.append(endpoint_info)

                    except Exception as e:
                        print(f"⚠️  Warning: Error processing pattern {url}: {e}")
                        # Add a basic entry even if we can't get all details
                        endpoints.append({
                            'url': url,
                            'name': 'error',
                            'view': 'Unknown',
                            'method': 'GET',
                            'namespace': namespace,
                            'is_api': False,
                            'pattern_type': 'URLPattern'
                        })

            except Exception as e:
                print(f"⚠️  Warning: Error processing URL pattern: {e}")
                continue

        return endpoints

    def deduplicate_endpoints(self, raw_endpoints: List[Dict[str, Any]],
                            include_namespace: bool = True) -> List[Dict[str, Any]]:
        """
        FIX 2️⃣: Build bucket AFTER full canonicalisation and WITHOUT the view-name
        """
        buckets = defaultdict(lambda: {"methods": set(), "row": None})

        for raw in raw_endpoints:
            if raw['view'] == "RedirectView":
                continue  # Keep this guard (though should be filtered earlier)

            # Always work with the fully-normalised URL
            raw['url'] = self.canonicalize_url(raw['url'])

            # ⚠️ Do NOT include 'view' in the dedupe key – the same URL can be
            #    wired to several view classes in DRF's router (list/detail);
            #    we merge methods, not views.
            if include_namespace:
                key = (raw['url'], raw['name'], raw['namespace'])
            else:
                key = (raw['url'], raw['name'])

            bucket = buckets[key]
            bucket["methods"].add(raw['method'])
            bucket["row"] = raw  # Remember *one* row for the metadata

        clean_rows = []
        for bucket in buckets.values():
            row = bucket["row"]
            row['methods'] = sorted(list(bucket["methods"]))  # Convert back to list, sorted
            del row['method']  # Remove single method field
            clean_rows.append(row)

        return clean_rows

    def is_api_endpoint(self, pattern: URLPattern) -> bool:
        """
        IMPROVEMENT 4: Better DRF detection using introspection instead of string matching
        """
        if not hasattr(pattern, 'callback'):
            return False

        try:
            # Try to import DRF classes (lazy import to handle cases where DRF isn't installed)
            from rest_framework.views import APIView
            from rest_framework.viewsets import ViewSetMixin

            callback = pattern.callback

            # Check if it's a DRF class-based view
            if hasattr(callback, 'view_class'):
                return issubclass(callback.view_class, (APIView, ViewSetMixin))

            # Check for Django 5.0+ async views
            elif hasattr(callback, 'cls'):
                return issubclass(callback.cls, (APIView, ViewSetMixin))

        except ImportError:
            # DRF not installed, fall back to string matching
            pass

        # Fallback to string-based detection
        drf_indicators = [
            'APIView', 'ViewSet', 'GenericAPIView', 'ListAPIView',
            'CreateAPIView', 'RetrieveAPIView', 'UpdateAPIView', 'DestroyAPIView'
        ]

        view_name = str(pattern.callback)
        return any(indicator in view_name for indicator in drf_indicators)

    def get_all_endpoints(self, skip_admin: bool = False,
                         include_namespace_in_dedupe: bool = True) -> List[Dict[str, Any]]:
        """
        Main method to get all endpoints with enhanced features and deduplication
        """
        try:
            # Get the root URL resolver
            resolver = get_resolver()

            # Extract all URLs with details (returns raw data with single methods)
            raw_endpoints = self.extract_urls(resolver.url_patterns, skip_admin=skip_admin)

            # Apply the new deduplication logic that properly merges methods
            all_endpoints = self.deduplicate_endpoints(raw_endpoints, include_namespace_in_dedupe)

            # Sort by URL first, then method for more natural navigation
            all_endpoints.sort(key=lambda x: (
                x['url'],
                x['methods'][0] if x['methods'] else 'GET',
                x['namespace'] or ''
            ))

            return all_endpoints

        except Exception as e:
            print(f"❌ Error extracting endpoints: {e}")
            return []

    def write_endpoints_to_markdown(self, endpoints: List[Dict[str, Any]],
                                  filename: str = 'django_endpoints.md') -> bool:
        """
        Write endpoints to markdown file with enhanced formatting and analysis
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header with enhanced styling
                f.write(f"# 🚀 Django Project Endpoints\n\n")
                f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Total endpoints:** {len(endpoints)}\n\n")

                # Statistics
                api_count = sum(1 for ep in endpoints if ep.get('is_api', False))
                f.write(f"**API endpoints:** {api_count}\n")
                f.write(f"**Web endpoints:** {len(endpoints) - api_count}\n\n")
                f.write("---\n\n")

                # Group by namespace and type
                self._write_endpoints_by_category(f, endpoints)

                # Write detailed analysis
                self._write_endpoint_analysis(f, endpoints)

                f.write("\n---\n\n")
                f.write("*Generated by Enhanced Django Endpoints Extractor*\n")

            print(f"✅ Endpoints written to: {filename}")
            return True

        except Exception as e:
            print(f"❌ Error writing to file: {e}")
            return False

    def _write_endpoints_by_category(self, f, endpoints: List[Dict[str, Any]]):
        """Write endpoints organized by category with color-coded methods"""
        # Separate API and web endpoints
        api_endpoints = [ep for ep in endpoints if ep.get('is_api', False)]
        web_endpoints = [ep for ep in endpoints if not ep.get('is_api', False)]

        # Group by namespace
        namespaced = {}
        no_namespace = []

        for endpoint_list, title in [(api_endpoints, "API"), (web_endpoints, "Web")]:
            if not endpoint_list:
                continue

            f.write(f"## {title} Endpoints\n\n")

            # Reset grouping for each type
            namespaced.clear()
            no_namespace.clear()

            for endpoint in endpoint_list:
                if endpoint['namespace']:
                    if endpoint['namespace'] not in namespaced:
                        namespaced[endpoint['namespace']] = []
                    namespaced[endpoint['namespace']].append(endpoint)
                else:
                    no_namespace.append(endpoint)

            # Write main endpoints first
            if no_namespace:
                f.write(f"### Main {title} Endpoints\n\n")
                self._write_endpoint_table(f, no_namespace)

            # Write namespaced endpoints
            for namespace, ns_endpoints in namespaced.items():
                f.write(f"### {namespace.title().replace(':', ' - ')} {title} Endpoints\n\n")
                self._write_endpoint_table(f, ns_endpoints)

    def _write_endpoint_table(self, f, endpoints: List[Dict[str, Any]]):
        """Write a formatted table of endpoints with consolidated method display"""
        f.write("| URL | Methods | View | Name |\n")
        f.write("|-----|---------|------|------|\n")

        # Method color mapping
        method_colors = {
            'GET': '🟢',
            'POST': '🔵',
            'PUT': '🟡',
            'PATCH': '🟠',
            'DELETE': '🔴',
            'HEAD': '⚪',
            'OPTIONS': '⚫'
        }

        for endpoint in endpoints:
            # Consolidate methods into a single compact display
            if len(endpoint['methods']) == 1:
                method = endpoint['methods'][0]
                color = method_colors.get(method, '⚪')
                methods_display = f"**{color} {method}**"
            else:
                # Multiple methods - show as compact list
                method_parts = []
                for method in sorted(endpoint['methods']):
                    color = method_colors.get(method, '⚪')
                    method_parts.append(f"{color} {method}")
                methods_display = ' / '.join(method_parts)

            # Escape pipe characters in URLs
            url = endpoint['url'].replace('|', '\\|')
            f.write(f"| `{url}` | {methods_display} | `{endpoint['view']}` | {endpoint['name']} |\n")

        f.write("\n")

    def _write_endpoint_analysis(self, f, endpoints: List[Dict[str, Any]]):
        """Write detailed analysis section"""
        f.write("## 📊 Analysis\n\n")

        # HTTP Methods distribution
        method_counts = {}
        for endpoint in endpoints:
            for method in endpoint['methods']:
                method_counts[method] = method_counts.get(method, 0) + 1

        f.write("### HTTP Methods Distribution\n\n")
        for method, count in sorted(method_counts.items()):
            f.write(f"- **{method}**: {count} endpoints\n")
        f.write("\n")

        # View types analysis
        view_types = {}
        for endpoint in endpoints:
            view_name = endpoint['view']
            if any(indicator in view_name for indicator in ['View', 'APIView', 'ViewSet']):
                view_types['Class-based Views'] = view_types.get('Class-based Views', 0) + 1
            else:
                view_types['Function-based Views'] = view_types.get('Function-based Views', 0) + 1

        f.write("### View Types\n\n")
        for view_type, count in view_types.items():
            f.write(f"- **{view_type}**: {count} endpoints\n")
        f.write("\n")

        # Namespace analysis
        namespace_counts = {}
        for endpoint in endpoints:
            namespace = endpoint['namespace'] or 'Main'
            namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1

        if len(namespace_counts) > 1:
            f.write("### Namespace Distribution\n\n")
            for namespace, count in sorted(namespace_counts.items()):
                f.write(f"- **{namespace}**: {count} endpoints\n")
            f.write("\n")

    def print_endpoints(self, endpoints: List[Dict[str, Any]], api_only: bool = False):
        """
        Print all endpoints to console with enhanced formatting
        """
        if api_only:
            endpoints = [ep for ep in endpoints if ep.get('is_api', False)]
            print("\n🚀 Django API Endpoints")
        else:
            print("\n🚀 Django Project Endpoints")

        print("=" * 60)

        api_endpoints = [ep for ep in endpoints if ep.get('is_api', False)]
        web_endpoints = [ep for ep in endpoints if not ep.get('is_api', False)]

        for endpoint_list, title in [(api_endpoints, "API"), (web_endpoints, "Web")]:
            if not endpoint_list or (api_only and title == "Web"):
                continue

            print(f"\n📡 {title} Endpoints ({len(endpoint_list)})")
            print("-" * 40)

            for endpoint in endpoint_list:
                methods = ' / '.join(endpoint['methods'])  # Use consolidated methods display
                namespace = f" [{endpoint['namespace']}]" if endpoint['namespace'] else ""
                print(f"🔗 {endpoint['url']}")
                print(f"   Methods: {methods}")
                print(f"   View: {endpoint['view']}")
                print(f"   Name: {endpoint['name']}{namespace}")
                print()

        if not api_only:
            print(f"📊 Total endpoints: {len(endpoints)}")
            print(f"📡 API endpoints: {len(api_endpoints)}")
            print(f"🌐 Web endpoints: {len(web_endpoints)}")
        else:
            print(f"📊 API endpoints: {len(endpoints)}")


def main():
    """
    Main function to extract endpoints with enhanced error handling and proper exit codes
    """
    try:
        # Try to detect settings module from environment or common patterns
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        if not settings_module:
            # Try common patterns
            possible_settings = [
                'settings',
                'config.settings',
                'core.settings',
                'project.settings',
                'educore.settings'
            ]
            for setting in possible_settings:
                try:
                    __import__(setting)
                    settings_module = setting
                    break
                except ImportError:
                    continue

        if not settings_module:
            print("❌ Could not detect Django settings module.")
            print("Please set DJANGO_SETTINGS_MODULE environment variable.")
            sys.exit(1)

        extractor = EndpointExtractor(settings_module)
        endpoints = extractor.get_all_endpoints()

        if not endpoints:
            print("❌ No endpoints found. Check your Django configuration.")
            sys.exit(1)

        # Print to console
        extractor.print_endpoints(endpoints)

        # Write to markdown file
        success = extractor.write_endpoints_to_markdown(endpoints)

        # Create additional output formats
        try:
            with open('endpoints_simple.txt', 'w', encoding='utf-8') as f:
                for endpoint in endpoints:
                    f.write(f"{endpoint['url']}\n")
            print("✅ Simple list written to: endpoints_simple.txt")

            # Create JSON output for programmatic use
            with open('endpoints.json', 'w', encoding='utf-8') as f:
                json.dump(endpoints, f, indent=2, default=str)
            print("✅ JSON data written to: endpoints.json")
        except Exception as e:
            print(f"⚠️  Warning: Could not write additional files: {e}")

        if success:
            print(f"✅ Successfully processed {len(endpoints)} endpoints")
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you're running this from your Django project directory")
        print("and that all required environment variables are set")
        sys.exit(1)


# Django Management Command
class Command(BaseCommand):
    """
    Django management command for listing endpoints
    Usage: python manage.py list_endpoints
    """
    help = "Extract and display all Django URL endpoints"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='django_endpoints.md',
            help='Output filename for markdown file'
        )
        parser.add_argument(
            '--format',
            choices=['console', 'markdown', 'json', 'all'],
            default='all',
            help='Output format'
        )
        parser.add_argument(
            '--api-only',
            action='store_true',
            help='Show only API endpoints'
        )
        # IMPROVEMENT 2: Add skip-admin flag
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Omit Django admin patterns'
        )
        parser.add_argument(
            '--include-namespace-in-dedupe',
            action='store_true',
            default=True,
            help='Include namespace when deduplicating endpoints (default: True)'
        )

    def handle(self, *args, **options):
        try:
            # Configure logging to prevent duplicate warnings
            try:
                configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
            except Exception:
                pass  # Fallback if logging config fails

            extractor = EndpointExtractor()
            endpoints = extractor.get_all_endpoints(
                skip_admin=options['skip_admin'],
                include_namespace_in_dedupe=options['include_namespace_in_dedupe']
            )

            if options['api_only']:
                endpoints = [ep for ep in endpoints if ep.get('is_api', False)]

            if options['format'] in ['console', 'all']:
                extractor.print_endpoints(endpoints, api_only=options['api_only'])

            if options['format'] in ['markdown', 'all']:
                extractor.write_endpoints_to_markdown(endpoints, options['output'])

            if options['format'] in ['json', 'all']:
                json_filename = options['output'].replace('.md', '.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(endpoints, f, indent=2, default=str)
                self.stdout.write(f"✅ JSON written to: {json_filename}")

            self.stdout.write(
                self.style.SUCCESS(f"Successfully processed {len(endpoints)} endpoints")
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error: {e}")
            )
            raise  # Re-raise to ensure proper exit code
