# your_app/management/commands/list_endpoints.py

import json
import time
import signal
import sys
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.utils.log import configure_logging
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse, NoReverseMatch
from educore.utils.endpoint_extractor import EndpointExtractor  # Adjust import path


class TimeoutError(Exception):
    """Custom timeout exception"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Request timed out")


class Command(BaseCommand):
    """
    Django management command for listing and testing endpoints
    Usage:
        python manage.py list_endpoints                    # List only
        python manage.py list_endpoints --test             # List and test
        python manage.py list_endpoints --test-only        # Test only
        python manage.py list_endpoints --success-code 200 # Custom success criteria
    """
    help = "Extract, display, and optionally test all Django URL endpoints"

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
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test all endpoints after listing them'
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test endpoints, skip listing'
        )
        parser.add_argument(
            '--methods',
            type=str,
            nargs='+',
            default=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            help='HTTP methods to test'
        )
        parser.add_argument(
            '--test-output',
            type=str,
            default='endpoint_test_results.json',
            help='Output file for test results'
        )
        parser.add_argument(
            '--exclude-patterns',
            type=str,
            nargs='+',
            default=['admin', 'static', 'media'],
            help='URL patterns to exclude from testing'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout for each request in seconds'
        )
        parser.add_argument(
            '--max-endpoints',
            type=int,
            help='Maximum number of endpoints to test (for large projects)'
        )
        parser.add_argument(
            '--success-threshold',
            type=int,
            default=400,
            help='HTTP status codes below this are considered successful (default: 400)'
        )
        parser.add_argument(
            '--test-username',
            type=str,
            default='endpoint_test_user',
            help='Username for test user'
        )
        parser.add_argument(
            '--test-password',
            type=str,
            default='testpass123',
            help='Password for test user'
        )
        parser.add_argument(
            '--deduplicate',
            action='store_true',
            default=True,
            help='Remove duplicate endpoints (default: True)'
        )

    def handle(self, *args, **options):
        try:
            # Configure logging to prevent duplicate warnings
            try:
                configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
            except Exception:
                pass  # Fallback if logging config fails

            extractor = EndpointExtractor()
            endpoints = extractor.get_all_endpoints()

            # Ensure endpoints is a list and handle empty case
            if not isinstance(endpoints, list):
                endpoints = []

            if not endpoints:
                self.stdout.write(self.style.WARNING("No endpoints found"))
                return

            # Deduplicate endpoints by URL
            if options['deduplicate']:
                original_count = len(endpoints)
                seen_urls = set()
                deduplicated = []
                for ep in endpoints:
                    url = ep.get('url')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        deduplicated.append(ep)
                endpoints = deduplicated
                dedup_count = original_count - len(endpoints)
                if dedup_count > 0:
                    self.stdout.write(f"🔄 Deduplicated {dedup_count} endpoints")

            if options['api_only']:
                endpoints = [ep for ep in endpoints if ep.get('is_api', False)]

            # Listing phase
            if not options['test_only']:
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

            # Testing phase
            if options['test'] or options['test_only']:
                self.stdout.write(
                    self.style.WARNING("\n🧪 Starting endpoint testing...")
                )
                test_results = self.test_endpoints(endpoints, options)
                self.generate_test_report(test_results, options)

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error: {e}")
            )
            raise  # Re-raise to ensure proper exit code

    def test_endpoints(self, endpoints, options):
        """Test all endpoints with various HTTP methods"""
        client = Client()
        test_user = None
        user_created = False
        User = get_user_model()

        # Create test user for authenticated requests
        try:
            with transaction.atomic():
                test_user = User.objects.create_user(
                    username=options['test_username'],
                    password=options['test_password'],
                    email='test@example.com'
                )
                user_created = True
        except Exception:
            try:
                test_user = User.objects.get(username=options['test_username'])
                # Ensure password is correct
                if not test_user.check_password(options['test_password']):
                    test_user.set_password(options['test_password'])
                    test_user.save()
                user_created = False
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING("Could not create test user. Testing without authentication.")
                )
                user_created = False

        try:
            # Filter endpoints for testing
            testable_endpoints = self.filter_testable_endpoints(endpoints, options)

            if options.get('max_endpoints') and options['max_endpoints'] > 0:
                testable_endpoints = testable_endpoints[:options['max_endpoints']]

            if not testable_endpoints:
                self.stdout.write(self.style.WARNING("No testable endpoints found"))
                return []

            self.stdout.write(f"Testing {len(testable_endpoints)} endpoints...")

            results = []
            start_time = time.time()

            for i, endpoint in enumerate(testable_endpoints, 1):
                url = endpoint.get('url', 'Unknown URL')
                self.stdout.write(f"Testing {i}/{len(testable_endpoints)}: {url}")

                result = self.test_single_endpoint(
                    client, endpoint, options['methods'], test_user, options
                )
                results.append(result)

                # Progress indicator
                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (len(testable_endpoints) - i) * avg_time
                    self.stdout.write(f"Progress: {i}/{len(testable_endpoints)} - ETA: {remaining:.1f}s")

            return results

        finally:
            # Cleanup test user
            if test_user and user_created:
                try:
                    test_user.delete()
                except Exception:
                    pass

    def filter_testable_endpoints(self, endpoints, options):
        """Filter endpoints that can be tested"""
        testable = []
        exclude_patterns = options.get('exclude_patterns', [])

        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue

            url = endpoint.get('url', '')
            name = endpoint.get('name', '')

            # Skip if no URL available
            if not url:
                continue

            # Skip if matches exclude patterns
            if any(pattern in url.lower() or pattern in name.lower() for pattern in exclude_patterns):
                continue

            testable.append(endpoint)

        return testable

    def test_single_endpoint(self, client, endpoint, methods, test_user, options):
        """Test a single endpoint with different HTTP methods and auth states"""
        url = endpoint.get('url', '')
        name = endpoint.get('name', 'unnamed')
        success_threshold = options['success_threshold']

        result = {
            'endpoint': endpoint,
            'url': url,
            'name': name,
            'tests': {},
            'summary': {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0
            }
        }

        # Test anonymous access for all methods
        for method in methods:
            method_lower = method.lower()
            test_name = f'{method}_anonymous'

            try:
                response = self.make_request(client, method_lower, url, options['timeout'])
                result['tests'][test_name] = {
                    'status_code': response.status_code,
                    'success': response.status_code < success_threshold,
                    'content_type': response.get('content-type', ''),
                    'has_content': len(getattr(response, 'content', b'')) > 0,
                    'error': None
                }
            except Exception as e:
                result['tests'][test_name] = {
                    'status_code': None,
                    'success': False,
                    'error': str(e)[:200]  # Truncate long errors
                }

            result['summary']['total_tests'] += 1
            if result['tests'][test_name]['success']:
                result['summary']['successful_tests'] += 1
            else:
                result['summary']['failed_tests'] += 1

        # Test authenticated access if user available
        if test_user:
            # Login once for all authenticated tests
            try:
                login_result = client.login(username=options['test_username'], password=options['test_password'])
                login_successful = login_result
            except Exception as e:
                login_successful = False
                self.stdout.write(f"Failed to login: {e}")

            if login_successful:
                for method in methods:
                    method_lower = method.lower()
                    test_name = f'{method}_authenticated'

                    try:
                        response = self.make_request(client, method_lower, url, options['timeout'])
                        result['tests'][test_name] = {
                            'status_code': response.status_code,
                            'success': response.status_code < success_threshold,
                            'content_type': response.get('content-type', ''),
                            'has_content': len(getattr(response, 'content', b'')) > 0,
                            'error': None
                        }
                    except Exception as e:
                        result['tests'][test_name] = {
                            'status_code': None,
                            'success': False,
                            'error': str(e)[:200]
                        }

                    result['summary']['total_tests'] += 1
                    if result['tests'][test_name]['success']:
                        result['summary']['successful_tests'] += 1
                    else:
                        result['summary']['failed_tests'] += 1

                # Logout after all tests for this endpoint
                client.logout()

        return result

    def make_request(self, client, method, url, timeout):
        """Make HTTP request with timeout handling"""
        # Validate method exists on client
        if not hasattr(client, method):
            raise AttributeError(f"Client does not support method: {method}")

        # Only use timeout on Unix systems (Windows doesn't support SIGALRM)
        use_timeout = timeout and timeout > 0 and hasattr(signal, 'SIGALRM')

        if use_timeout and sys.platform != 'win32':
            # Set up timeout signal
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            try:
                response = getattr(client, method)(url)
                signal.alarm(0)  # Cancel the alarm
                return response
            except TimeoutError:
                raise Exception(f"Request timed out after {timeout} seconds")
            finally:
                signal.alarm(0)  # Ensure alarm is cancelled
                signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
        else:
            return getattr(client, method)(url)

    def generate_test_report(self, results, options):
        """Generate comprehensive test report"""
        if not results:
            self.stdout.write(self.style.WARNING("No test results to report"))
            return

        total_endpoints = len(results)
        successful_endpoints = sum(1 for r in results if r['summary']['successful_tests'] > 0)
        failed_endpoints = total_endpoints - successful_endpoints

        total_tests = sum(r['summary']['total_tests'] for r in results)
        successful_tests = sum(r['summary']['successful_tests'] for r in results)
        failed_tests = sum(r['summary']['failed_tests'] for r in results)

        # Avoid division by zero
        endpoint_success_rate = (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        test_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # Console report
        self.stdout.write(self.style.SUCCESS(f"\n{'='*80}"))
        self.stdout.write(self.style.SUCCESS("🧪 ENDPOINT TESTING REPORT"))
        self.stdout.write(self.style.SUCCESS(f"{'='*80}"))

        self.stdout.write(f"📊 Summary:")
        self.stdout.write(f"   Total Endpoints: {total_endpoints}")
        self.stdout.write(f"   Successful Endpoints: {successful_endpoints}")
        self.stdout.write(f"   Failed Endpoints: {failed_endpoints}")
        self.stdout.write(f"   Success Rate: {endpoint_success_rate:.1f}%")
        self.stdout.write(f"")
        self.stdout.write(f"   Total Tests: {total_tests}")
        self.stdout.write(f"   Successful Tests: {successful_tests}")
        self.stdout.write(f"   Failed Tests: {failed_tests}")
        self.stdout.write(f"   Test Success Rate: {test_success_rate:.1f}%")
        self.stdout.write(f"   Success Threshold: < {options['success_threshold']} status code")

        # Status code analysis
        status_codes = defaultdict(int)
        error_types = defaultdict(int)

        for result in results:
            for test in result['tests'].values():
                if test.get('status_code') is not None:
                    status_codes[test['status_code']] += 1
                if test.get('error'):
                    error_type = test['error'].split(':')[0] if ':' in test['error'] else test['error']
                    error_types[error_type] += 1

        if status_codes:
            self.stdout.write(f"\n📈 Status Code Distribution:")
            for code, count in sorted(status_codes.items()):
                emoji = "✅" if code < options['success_threshold'] else "⚠️" if code < 500 else "❌"
                self.stdout.write(f"   {emoji} {code}: {count} responses")

        if error_types:
            self.stdout.write(f"\n🚨 Common Errors:")
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                self.stdout.write(f"   ❌ {error}: {count} occurrences")

        # Failed endpoints details
        completely_failed = [r for r in results if r['summary']['successful_tests'] == 0]
        if completely_failed:
            self.stdout.write(f"\n💥 Completely Failed Endpoints ({len(completely_failed)}):")
            for failure in completely_failed[:10]:  # Show first 10
                self.stdout.write(f"   ❌ {failure['url']} ({failure['name']})")
                # Show first error
                for test_name, test_result in failure['tests'].items():
                    if test_result.get('error'):
                        self.stdout.write(f"      └── {test_name}: {test_result['error'][:100]}...")
                        break

        # Endpoints with mixed results
        mixed_results = [r for r in results if 0 < r['summary']['successful_tests'] < r['summary']['total_tests']]
        if mixed_results:
            self.stdout.write(f"\n⚠️ Endpoints with Mixed Results ({len(mixed_results)}):")
            for mixed in mixed_results[:5]:
                mixed_success_rate = (mixed['summary']['successful_tests'] / mixed['summary']['total_tests']) * 100
                self.stdout.write(f"   🔄 {mixed['url']} ({mixed_success_rate:.1f}% success)")

        # Save detailed results to JSON
        try:
            with open(options['test_output'], 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total_endpoints': total_endpoints,
                        'successful_endpoints': successful_endpoints,
                        'failed_endpoints': failed_endpoints,
                        'success_rate': endpoint_success_rate,
                        'total_tests': total_tests,
                        'successful_tests': successful_tests,
                        'failed_tests': failed_tests,
                        'test_success_rate': test_success_rate,
                        'success_threshold': options['success_threshold'],
                        'status_code_distribution': dict(status_codes),
                        'error_types': dict(error_types)
                    },
                    'detailed_results': results
                }, f, indent=2, default=str)

            self.stdout.write(f"\n💾 Detailed results saved to: {options['test_output']}")
        except Exception as e:
            self.stderr.write(f"Failed to save test results: {e}")

        self.stdout.write(self.style.SUCCESS(f"{'='*80}"))
