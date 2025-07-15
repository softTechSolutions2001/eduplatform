import copy
import hashlib
import importlib
import inspect
import json
import os
import sys
import tempfile
import time
import traceback
import uuid
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, models, transaction
from django.utils.module_loading import import_string
from model_bakery import baker
from rest_framework import serializers
from rest_framework.fields import Field


class Command(BaseCommand):
    help = "Dynamically test all serializers in the project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app", type=str, help="Test serializers for specific app only"
        )
        parser.add_argument(
            "--depth",
            type=int,
            default=3,
            help="Max depth for nested serializer testing",
        )
        parser.add_argument(
            "--samples",
            type=int,
            default=10,
            help="Number of test samples per serializer",
        )
        parser.add_argument(
            "--fail-fast",
            action="store_true",
            help="Stop at first failure",
        )
        parser.add_argument(
            "--json-report",
            type=str,
            help="Path to write JSON report",
        )
        parser.add_argument(
            "--cache-discovery",
            action="store_true",
            help="Cache serializer discovery for faster runs",
        )

    def handle(self, *args, **options):
        self.depth = options["depth"]
        self.samples = options["samples"]
        self.app_filter = options.get("app")
        self.fail_fast = options["fail_fast"]
        self.json_report = options.get("json_report")
        self.cache_discovery = options["cache_discovery"]

        results = SerializerTestRunner().run_comprehensive_tests(
            app_filter=self.app_filter,
            depth=self.depth,
            samples=self.samples,
            fail_fast=self.fail_fast,
            cache_discovery=self.cache_discovery,
        )

        self.print_results(results)

        if self.json_report:
            self.write_json_report(results)

    def print_results(self, results):
        """Print concise test results"""
        total_tests = sum(len(r["tests"]) for r in results.values())
        passed_tests = sum(
            sum(1 for t in r["tests"] if t["status"] == "PASS")
            for r in results.values()
        )
        failed_tests = total_tests - passed_tests

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"SERIALIZER TEST REPORT")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(
            f"Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}"
        )
        self.stdout.write(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")

        # Only show failures for concise output
        for serializer_path, result in results.items():
            if result["status"] == "FAIL":
                self.stdout.write(f"✗ {serializer_path}")
                for test in result["tests"]:
                    if test["status"] == "FAIL":
                        self.stdout.write(f"  └─ {test['test_name']}: {test['error']}")
            elif self.verbosity > 1:
                self.stdout.write(f"✓ {serializer_path}")

        self.stdout.write(f"\n{'='*60}")

    def write_json_report(self, results):
        """Write machine-readable JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_serializers": len(results),
                "total_tests": sum(len(r["tests"]) for r in results.values()),
                "passed_tests": sum(
                    sum(1 for t in r["tests"] if t["status"] == "PASS")
                    for r in results.values()
                ),
                "failed_tests": sum(
                    sum(1 for t in r["tests"] if t["status"] == "FAIL")
                    for r in results.values()
                ),
            },
            "results": results,
        }

        with open(self.json_report, "w") as f:
            json.dump(report, f, indent=2, cls=DjangoJSONEncoder)

        self.stdout.write(f"JSON report written to: {self.json_report}")


class SerializerTestRunner:
    def __init__(self):
        self.test_registry = TestRegistry()
        # Use portable cache location
        self.cache_file = (
            Path(tempfile.gettempdir()) / "serializer_discovery_cache.json"
        )

    def _get_cache_key(self):
        """Generate cache key based on settings, modules, and deployment info"""
        key_parts = [
            getattr(settings, "SECRET_KEY", ""),
            os.environ.get("DJANGO_SETTINGS_MODULE", ""),
            # Include git commit or image tag for deployment-aware caching
            os.environ.get("GIT_SHA", ""),
            os.environ.get("IMAGE_TAG", ""),
        ]

        # Add file content hash or mtime for each serializer module
        for app_config in apps.get_app_configs():
            try:
                module_path = f"{app_config.name}.serializers"
                module = importlib.import_module(module_path)
                if hasattr(module, "__file__") and module.__file__:
                    file_path = Path(module.__file__)
                    if file_path.exists():
                        # Use file content hash for more reliable cache invalidation
                        try:
                            with open(file_path, "rb") as f:
                                content_hash = hashlib.md5(f.read()).hexdigest()
                            key_parts.append(content_hash)
                        except (IOError, OSError):
                            # Fallback to mtime if file can't be read
                            key_parts.append(str(file_path.stat().st_mtime))
            except ImportError:
                continue

        return hashlib.md5("".join(key_parts).encode()).hexdigest()

    def discover_serializers(self, app_filter=None, use_cache=False):
        """Dynamically discover all serializers in the project"""
        cache_key = self._get_cache_key()

        if use_cache and self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    cached_data = json.load(f)

                # Check cache validity
                if cached_data.get("cache_key") == cache_key:
                    serializers_data = cached_data.get("serializers", {})
                    serializers_map = {}

                    for path, info in serializers_data.items():
                        try:
                            serializer_cls = import_string(path)
                            model_cls = (
                                import_string(info["model_path"])
                                if info["model_path"]
                                else None
                            )
                            serializers_map[path] = {
                                "serializer": serializer_cls,
                                "model": model_cls,
                                "app": info["app"],
                            }
                        except ImportError:
                            continue
                    return serializers_map
            except (json.JSONDecodeError, KeyError):
                pass

        serializers_map = {}
        cache_data = {"cache_key": cache_key, "serializers": {}}

        for app_config in apps.get_app_configs():
            if app_filter and app_config.name != app_filter:
                continue

            try:
                serializers_module = import_string(f"{app_config.name}.serializers")

                for name in dir(serializers_module):
                    obj = getattr(serializers_module, name)

                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, serializers.Serializer)
                        and obj != serializers.Serializer
                    ):
                        model = None
                        model_path = None
                        if hasattr(obj, "Meta") and hasattr(obj.Meta, "model"):
                            model = obj.Meta.model
                            model_path = f"{model.__module__}.{model.__name__}"

                        serializer_path = f"{app_config.name}.serializers.{name}"
                        serializers_map[serializer_path] = {
                            "serializer": obj,
                            "model": model,
                            "app": app_config.name,
                        }

                        cache_data["serializers"][serializer_path] = {
                            "model_path": model_path,
                            "app": app_config.name,
                        }

            except ImportError:
                continue

        if use_cache:
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

        return serializers_map

    def run_comprehensive_tests(
        self,
        app_filter=None,
        depth=3,
        samples=10,
        fail_fast=False,
        cache_discovery=False,
    ):
        """Run comprehensive tests on all discovered serializers"""
        serializers_map = self.discover_serializers(app_filter, cache_discovery)
        results = {}

        for serializer_path, serializer_info in serializers_map.items():
            result = self.test_serializer(
                serializer_info["serializer"], serializer_info["model"], depth, samples
            )
            results[serializer_path] = result

            if fail_fast and result["status"] == "FAIL":
                break

        return results

    def test_serializer(self, serializer_cls, model, depth, samples):
        """Test a single serializer comprehensively"""
        test_results = []

        for test_name, test_func in self.test_registry.get_tests():
            try:
                with transaction.atomic():
                    test_func(serializer_cls, model, depth, samples)
                    test_results.append(
                        {"test_name": test_name, "status": "PASS", "error": None}
                    )
            except Exception as e:
                test_results.append(
                    {"test_name": test_name, "status": "FAIL", "error": str(e)}
                )

        overall_status = (
            "PASS" if all(t["status"] == "PASS" for t in test_results) else "FAIL"
        )

        return {
            "status": overall_status,
            "tests": test_results,
            "serializer": serializer_cls.__name__,
            "model": model.__name__ if model else None,
        }


class TestRegistry:
    def __init__(self):
        self.tests = []
        self._register_all_tests()

    def register(self, name):
        """Decorator to register test functions"""

        def decorator(func):
            self.tests.append((name, func))
            return func

        return decorator

    def get_tests(self):
        return self.tests

    def _register_all_tests(self):
        """Register all test methods"""

        @self.register("Round-Trip Serialization")
        def test_round_trip(serializer_cls, model, depth, samples):
            if not model:
                return

            for _ in range(min(samples, 3)):
                with transaction.atomic():
                    try:
                        obj = baker.make(model)
                    except IntegrityError:
                        # Fallback to prepare + save for constraint violations
                        obj = baker.prepare(model)
                        obj.save()

                    serializer = serializer_cls(obj)
                    data = serializer.data

                    # Test JSON serialization with proper encoder
                    json_blob = json.dumps(data, cls=DjangoJSONEncoder)
                    restored_data = json.loads(json_blob)

                    # Use partial=True to handle write-only required fields
                    new_serializer = serializer_cls(data=restored_data, partial=True)
                    if not new_serializer.is_valid():
                        raise AssertionError(
                            f"Round-trip failed: {new_serializer.errors}"
                        )

        @self.register("Field Type Validation")
        def test_field_types(serializer_cls, model, depth, samples):
            serializer = serializer_cls()

            for field_name, field in serializer.fields.items():
                if field.read_only:
                    continue

                try:
                    # Test field-specific validations with partial=True
                    if isinstance(field, serializers.CharField):
                        if hasattr(field, "max_length") and field.max_length:
                            long_value = "x" * (field.max_length + 1)
                            test_serializer = serializer_cls(
                                data={field_name: long_value}, partial=True
                            )
                            if test_serializer.is_valid():
                                raise AssertionError(
                                    f"CharField {field_name} accepted too long value"
                                )

                    elif isinstance(field, serializers.EmailField):
                        test_serializer = serializer_cls(
                            data={field_name: "invalid-email"}, partial=True
                        )
                        if test_serializer.is_valid():
                            raise AssertionError(
                                f"EmailField {field_name} accepted invalid email"
                            )

                    elif isinstance(field, serializers.DecimalField):
                        if hasattr(field, "decimal_places"):
                            invalid_decimal = Decimal(
                                "1." + "1" * (field.decimal_places + 1)
                            )
                            test_serializer = serializer_cls(
                                data={field_name: invalid_decimal}, partial=True
                            )
                            if test_serializer.is_valid():
                                raise AssertionError(
                                    f"DecimalField {field_name} accepted invalid precision"
                                )

                    elif isinstance(field, serializers.IntegerField):
                        test_serializer = serializer_cls(
                            data={field_name: "not_an_integer"}, partial=True
                        )
                        if test_serializer.is_valid():
                            raise AssertionError(
                                f"IntegerField {field_name} accepted non-integer"
                            )

                    elif isinstance(field, serializers.DateTimeField):
                        test_serializer = serializer_cls(
                            data={field_name: "invalid-datetime"}, partial=True
                        )
                        if test_serializer.is_valid():
                            raise AssertionError(
                                f"DateTimeField {field_name} accepted invalid datetime"
                            )

                    elif isinstance(field, serializers.DateField):
                        test_serializer = serializer_cls(
                            data={field_name: "invalid-date"}, partial=True
                        )
                        if test_serializer.is_valid():
                            raise AssertionError(
                                f"DateField {field_name} accepted invalid date"
                            )

                    elif isinstance(field, serializers.ChoiceField):
                        if hasattr(field, "choices") and field.choices:
                            invalid_choice = f"__invalid__{uuid.uuid4().hex}"
                            test_serializer = serializer_cls(
                                data={field_name: invalid_choice}, partial=True
                            )
                            if test_serializer.is_valid():
                                raise AssertionError(
                                    f"ChoiceField {field_name} accepted invalid choice"
                                )

                    elif isinstance(field, serializers.BooleanField):
                        # Test boolean string parsing
                        test_serializer = serializer_cls(
                            data={field_name: "true"}, partial=True
                        )
                        if test_serializer.is_valid():
                            # Ensure it's actually parsed as boolean
                            validated_data = test_serializer.validated_data
                            if validated_data[field_name] is not True:
                                raise AssertionError(
                                    f"BooleanField {field_name} didn't parse 'true' as boolean True"
                                )

                except (TypeError, ValueError) as e:
                    # Skip fields that can't handle the test data type
                    continue

        @self.register("Required Field Validation")
        def test_required_fields(serializer_cls, model, depth, samples):
            serializer = serializer_cls()
            required_fields = [
                name
                for name, field in serializer.fields.items()
                if field.required and not field.read_only
            ]

            if required_fields:
                empty_serializer = serializer_cls(data={})
                if empty_serializer.is_valid():
                    raise AssertionError(
                        f"Serializer accepted empty data despite required fields: {required_fields}"
                    )

                for field_name in required_fields:
                    if field_name not in empty_serializer.errors:
                        raise AssertionError(
                            f"Required field {field_name} not in validation errors"
                        )

        @self.register("Read-Only Field Protection")
        def test_readonly_fields(serializer_cls, model, depth, samples):
            if not model:
                return

            with transaction.atomic():
                try:
                    obj = baker.make(model)
                except IntegrityError:
                    obj = baker.prepare(model)
                    obj.save()

                serializer = serializer_cls()
                readonly_fields = [
                    name for name, field in serializer.fields.items() if field.read_only
                ]

                if readonly_fields:
                    original_serializer = serializer_cls(obj)
                    original_data = original_serializer.data

                    for field_name in readonly_fields:
                        if field_name in original_data:
                            modified_data = original_data.copy()
                            modified_data[field_name] = "MODIFIED_VALUE"

                            update_serializer = serializer_cls(obj, data=modified_data)
                            if update_serializer.is_valid():
                                updated_obj = update_serializer.save()
                                current_serializer = serializer_cls(updated_obj)

                                if (
                                    current_serializer.data[field_name]
                                    != original_data[field_name]
                                ):
                                    raise AssertionError(
                                        f"Read-only field {field_name} was modified"
                                    )

        @self.register("Null Value Handling")
        def test_null_values(serializer_cls, model, depth, samples):
            serializer = serializer_cls()

            for field_name, field in serializer.fields.items():
                if field.read_only:
                    continue

                if field.allow_null:
                    test_serializer = serializer_cls(
                        data={field_name: None}, partial=True
                    )
                    if field.required and not test_serializer.is_valid():
                        if field_name in test_serializer.errors:
                            error_msg = str(test_serializer.errors[field_name]).lower()
                            if "null" in error_msg and "not allowed" in error_msg:
                                raise AssertionError(
                                    f"Nullable field {field_name} rejected null value"
                                )
                else:
                    test_serializer = serializer_cls(
                        data={field_name: None}, partial=True
                    )
                    if test_serializer.is_valid():
                        raise AssertionError(
                            f"Non-nullable field {field_name} accepted null value"
                        )

        @self.register("Nested Serializer Validation")
        def test_nested_serializers(serializer_cls, model, depth, samples):
            if depth <= 0:
                return

            serializer = serializer_cls()

            for field_name, field in serializer.fields.items():
                if isinstance(field, serializers.BaseSerializer):
                    with transaction.atomic():
                        if isinstance(field, serializers.ListSerializer):
                            if hasattr(field, "child") and isinstance(
                                field.child, serializers.ModelSerializer
                            ):
                                nested_model = field.child.Meta.model

                                # Ensure nested object creation is also in atomic block
                                try:
                                    nested_objs = baker.make(nested_model, _quantity=2)
                                except IntegrityError:
                                    nested_objs = [
                                        baker.prepare(nested_model) for _ in range(2)
                                    ]
                                    for obj in nested_objs:
                                        obj.save()

                                nested_serializer = field.child.__class__(
                                    nested_objs, many=True
                                )
                                nested_data = nested_serializer.data

                                if not field.read_only:
                                    test_serializer = serializer_cls(
                                        data={field_name: nested_data}, partial=True
                                    )
                                    if (
                                        not test_serializer.is_valid()
                                        and field_name in test_serializer.errors
                                    ):
                                        raise AssertionError(
                                            f"Nested list serializer {field_name} failed validation"
                                        )
                        elif isinstance(field, serializers.ModelSerializer):
                            nested_model = field.Meta.model
                            try:
                                nested_obj = baker.make(nested_model)
                            except IntegrityError:
                                nested_obj = baker.prepare(nested_model)
                                nested_obj.save()

                            nested_serializer = field.__class__(nested_obj)
                            nested_data = nested_serializer.data

                            if not field.read_only:
                                test_serializer = serializer_cls(
                                    data={field_name: nested_data}, partial=True
                                )
                                if (
                                    not test_serializer.is_valid()
                                    and field_name in test_serializer.errors
                                ):
                                    raise AssertionError(
                                        f"Nested serializer {field_name} failed validation"
                                    )

        @self.register("Relationship Field Validation")
        def test_relationship_fields(serializer_cls, model, depth, samples):
            serializer = serializer_cls()

            for field_name, field in serializer.fields.items():
                with transaction.atomic():
                    if isinstance(field, serializers.PrimaryKeyRelatedField):
                        if not field.read_only and hasattr(field, "queryset"):
                            related_model = field.queryset.model
                            try:
                                related_obj = baker.make(related_model)
                            except IntegrityError:
                                related_obj = baker.prepare(related_model)
                                related_obj.save()

                            test_serializer = serializer_cls(
                                data={field_name: related_obj.pk}, partial=True
                            )
                            if (
                                not test_serializer.is_valid()
                                and field_name in test_serializer.errors
                            ):
                                raise AssertionError(
                                    f"Valid PK relation {field_name} failed validation"
                                )

                            invalid_pk = 99999
                            test_serializer = serializer_cls(
                                data={field_name: invalid_pk}, partial=True
                            )
                            if test_serializer.is_valid():
                                raise AssertionError(
                                    f"Invalid PK relation {field_name} passed validation"
                                )

                    # Use ListSerializer instead of ManyRelatedField for better compatibility
                    elif isinstance(field, serializers.ListSerializer):
                        if (
                            not field.read_only
                            and hasattr(field, "child")
                            and isinstance(
                                field.child, serializers.PrimaryKeyRelatedField
                            )
                            and hasattr(field.child, "queryset")
                        ):

                            related_model = field.child.queryset.model
                            try:
                                related_objs = baker.make(
                                    related_model, _quantity=min(samples, 3)
                                )
                            except IntegrityError:
                                related_objs = [
                                    baker.prepare(related_model)
                                    for _ in range(min(samples, 3))
                                ]
                                for obj in related_objs:
                                    obj.save()

                            pks = [obj.pk for obj in related_objs]
                            test_serializer = serializer_cls(
                                data={field_name: pks}, partial=True
                            )
                            if (
                                not test_serializer.is_valid()
                                and field_name in test_serializer.errors
                            ):
                                raise AssertionError(
                                    f"Valid many-to-many relation {field_name} failed validation"
                                )

        @self.register("Bulk Serialization Performance")
        def test_bulk_performance(serializer_cls, model, depth, samples):
            if not model:
                return

            with transaction.atomic():
                try:
                    objs = baker.make(model, _quantity=samples)
                except IntegrityError:
                    objs = [baker.prepare(model) for _ in range(samples)]
                    for obj in objs:
                        obj.save()

                # Move timing after object creation
                start_time = time.time()
                serializer = serializer_cls(objs, many=True)
                data = serializer.data
                # Force full evaluation for lazy properties
                json_size = len(json.dumps(data, cls=DjangoJSONEncoder))
                elapsed = time.time() - start_time

                threshold = 2.0
                if elapsed > threshold:
                    raise AssertionError(
                        f"Bulk serialization took {elapsed:.2f}s (threshold: {threshold}s)"
                    )

                if len(data) != samples:
                    raise AssertionError(
                        f"Bulk serialization returned {len(data)} items, expected {samples}"
                    )

        @self.register("Partial Update Validation")
        def test_partial_updates(serializer_cls, model, depth, samples):
            if not model:
                return

            with transaction.atomic():
                try:
                    obj = baker.make(model)
                except IntegrityError:
                    obj = baker.prepare(model)
                    obj.save()

                serializer = serializer_cls(obj)
                original_data = serializer.data

                for field_name, field_value in original_data.items():
                    if field_name == "id":
                        continue

                    # Use deep copy to avoid reference mutations
                    partial_data = {field_name: copy.deepcopy(field_value)}
                    partial_serializer = serializer_cls(
                        obj, data=partial_data, partial=True
                    )

                    if not partial_serializer.is_valid():
                        field_obj = serializer.fields.get(field_name)
                        if field_obj and not field_obj.read_only:
                            raise AssertionError(
                                f"Partial update failed for field {field_name}: {partial_serializer.errors}"
                            )

        @self.register("Edge Case Data Types")
        def test_edge_cases(serializer_cls, model, depth, samples):
            serializer = serializer_cls()

            edge_cases = {
                "empty_string": "",
                "whitespace": "   ",
                "special_chars": "!@#$%^&*()",
                "unicode": "测试🚀",
                "very_long_string": "x" * 1000,
                "sql_injection": "'; DROP TABLE users; --",
                "xss_attempt": '<script>alert("xss")</script>',
                "negative_number": -999999,
                "zero": 0,
                "boolean_string": "true",
                "json_string": '{"key": "value"}',
            }

            for field_name, field in serializer.fields.items():
                if field.read_only:
                    continue

                for case_name, case_value in edge_cases.items():
                    try:
                        if isinstance(field, serializers.CharField) and case_name in [
                            "empty_string",
                            "whitespace",
                            "special_chars",
                            "unicode",
                            "very_long_string",
                            "sql_injection",
                            "xss_attempt",
                        ]:
                            test_serializer = serializer_cls(
                                data={field_name: case_value}, partial=True
                            )
                            if (
                                not test_serializer.is_valid()
                                and field_name in test_serializer.errors
                            ):
                                error_msg = str(test_serializer.errors[field_name])
                                if "unexpected error" in error_msg.lower():
                                    raise AssertionError(
                                        f"Unexpected error for {field_name} with {case_name}: {error_msg}"
                                    )

                        elif isinstance(
                            field, serializers.IntegerField
                        ) and case_name in ["negative_number", "zero"]:
                            test_serializer = serializer_cls(
                                data={field_name: case_value}, partial=True
                            )
                            if (
                                not test_serializer.is_valid()
                                and field_name in test_serializer.errors
                            ):
                                error_msg = str(test_serializer.errors[field_name])
                                if (
                                    "valid integer" not in error_msg.lower()
                                    and "required" not in error_msg.lower()
                                ):
                                    raise AssertionError(
                                        f"Unexpected integer validation error for {field_name}: {error_msg}"
                                    )

                        elif (
                            isinstance(field, serializers.BooleanField)
                            and case_name == "boolean_string"
                        ):
                            test_serializer = serializer_cls(
                                data={field_name: case_value}, partial=True
                            )
                            if test_serializer.is_valid():
                                # Explicitly check if boolean string was parsed correctly
                                validated_data = test_serializer.validated_data
                                if validated_data[field_name] is not True:
                                    raise AssertionError(
                                        f"BooleanField {field_name} didn't parse 'true' correctly"
                                    )

                    except (TypeError, ValueError):
                        # Skip incompatible field/value combinations
                        continue
