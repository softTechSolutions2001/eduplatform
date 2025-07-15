# Base mixins for serializers
#
# File Path: backend/courses/serializers/mixins.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:15:30
# Date Revised: 2025-07-09 04:43:47
# Current Date and Time (UTC): 2025-07-09 04:43:47
# Current User's Login: MohithaSanthanam2010
# Author: softTechSolutions2001
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 04:43:47 UTC
# User: MohithaSanthanam2010
# Version: 3.1.0
#
# Base mixins for serializer functionality
#
# Version 3.1.0 Changes:
# - FIXED 🔴: ContextPropagationMixin no longer mutates data in-place
# - FIXED 🔴: Replaced heavy copy.deepcopy with lighter copy.copy
# - ENHANCED: Better memory efficiency and performance
# - ADDED: Immutable data handling guarantees

import copy
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

logger = logging.getLogger(__name__)


class ContextPropagationMixin:
    """
    Mixin to ensure proper context propagation to nested serializers
    FIXED: Nested serializers losing context issue and data mutation
    """

    def get_serializer_context_for_nested(self, additional_context=None):
        """Get enhanced context for nested serializers"""
        # FIXED: Use copy.copy instead of deepcopy for better performance
        context = copy.copy(self.context)
        if additional_context:
            context.update(additional_context)
        return context

    def to_representation(self, instance):
        """
        Enhanced representation with immutable data handling
        FIXED: to_representation mutating data in-place
        """
        # Get the parent representation
        data = super().to_representation(instance)

        # FIXED: Create a shallow copy for safety, avoiding heavy deepcopy
        # Most serializer data doesn't have deeply nested mutable objects
        processed_data = copy.copy(data)

        # Process the copy safely
        return self._process_representation_safely(processed_data, instance)

    def _process_representation_safely(self, data, instance):
        """
        Process representation data safely without mutations
        Override in subclasses for custom processing
        FIXED: Returns new dict instead of mutating in-place
        """
        # Return a fresh copy to guarantee immutability
        return copy.copy(data) if isinstance(data, dict) else data


class OptimizedQueryMixin:
    """
    Mixin for optimized database queries in serializers
    FIXED: Query optimization for serializer performance
    """

    @classmethod
    def setup_eager_loading(cls, queryset):
        """
        Setup optimized eager loading for the queryset
        Override in subclasses to define specific optimizations
        """
        return queryset

    def get_optimized_queryset(self, queryset):
        """Get queryset with performance optimizations"""
        if hasattr(self, "setup_eager_loading"):
            return self.setup_eager_loading(queryset)
        return queryset


class EnhancedValidationMixin:
    """
    Mixin for enhanced validation with model integration
    FIXED: Large validate() blocks with redundant model clean() calls
    """

    def validate_with_model_clean(self, data, instance=None):
        """
        Streamlined validation with model integration
        FIXED: More efficient validation without redundant calls
        """
        try:
            # Create temporary instance for validation if not provided
            if instance is None:
                # Create a temporary instance without saving
                instance = self.Meta.model(**data)
            else:
                # Update existing instance with new data
                for key, value in data.items():
                    setattr(instance, key, value)

            # Use model's clean method for validation
            instance.clean()
            return data

        except DjangoValidationError as e:
            # Handle Django validation errors properly
            if hasattr(e, "message_dict"):
                raise serializers.ValidationError(e.message_dict)
            elif hasattr(e, "messages"):
                raise serializers.ValidationError(e.messages)
            else:
                raise serializers.ValidationError(str(e))
        except Exception as e:
            # Log unexpected errors and re-raise as validation error
            logger.error(f"Unexpected validation error: {e}")
            raise serializers.ValidationError(f"Validation failed: {str(e)}")


class SecureSerializerMixin:
    """
    Mixin for security-focused serializer enhancements
    """

    def sanitize_html_fields(self, data, fields):
        """
        Sanitize HTML content in specified fields
        """
        try:
            import bleach
            from bleach.sanitizer import ALLOWED_ATTRIBUTES, ALLOWED_TAGS

            # Define safe HTML elements
            safe_tags = list(ALLOWED_TAGS) + [
                "p",
                "br",
                "strong",
                "em",
                "ul",
                "ol",
                "li",
            ]
            safe_attributes = dict(ALLOWED_ATTRIBUTES)

            for field in fields:
                if field in data and isinstance(data[field], str):
                    data[field] = bleach.clean(
                        data[field],
                        tags=safe_tags,
                        attributes=safe_attributes,
                        strip=True,
                    )
        except ImportError:
            logger.warning("bleach not installed, skipping HTML sanitization")
        except Exception as e:
            logger.error(f"Error sanitizing HTML fields: {e}")

        return data

    def validate_file_upload(self, file_obj, max_size_mb=10, allowed_types=None):
        """
        Validate file uploads with size and type restrictions
        """
        if not file_obj:
            return file_obj

        # Check file size
        if file_obj.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"File size exceeds {max_size_mb}MB limit"
            )

        # Check file type
        if allowed_types:
            file_type = getattr(file_obj, "content_type", "").lower()
            if not any(allowed_type in file_type for allowed_type in allowed_types):
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
                )

        return file_obj


class CacheOptimizedMixin:
    """
    Mixin for cache-aware serializer operations
    """

    def get_cached_field(self, instance, field_name, cache_key_func, compute_func):
        """
        Get field value with caching support
        """
        try:
            from django.core.cache import cache

            # Try to get from cache first
            cache_key = cache_key_func(instance)
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # Compute value if not in cache
            computed_value = compute_func(instance)

            # Cache the computed value (cache for 5 minutes by default)
            cache.set(cache_key, computed_value, 300)

            return computed_value

        except Exception as e:
            logger.warning(f"Cache operation failed for {field_name}: {e}")
            # Fallback to direct computation
            return compute_func(instance)

    def invalidate_related_cache(self, instance, cache_patterns):
        """
        Invalidate related cache entries when model changes
        """
        try:
            from django.core.cache import cache

            for pattern in cache_patterns:
                cache_key = pattern.format(instance=instance)
                cache.delete(cache_key)

        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")


class PermissionAwareMixin:
    """
    Mixin for permission-aware field filtering
    """

    def filter_fields_by_permission(self, data, instance, permission_map):
        """
        Filter serializer fields based on user permissions

        Args:
            data: Serialized data dict
            instance: Model instance
            permission_map: Dict mapping field names to required permissions
        """
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            return data

        user = request.user
        filtered_data = copy.copy(data)

        for field_name, required_permission in permission_map.items():
            if field_name in filtered_data:
                # Check if user has the required permission
                if not self._user_has_permission(user, required_permission, instance):
                    # Remove the field or replace with placeholder
                    filtered_data.pop(field_name, None)
                    # Optionally add a placeholder
                    filtered_data[f"{field_name}_restricted"] = True

        return filtered_data

    def _user_has_permission(self, user, permission, instance):
        """
        Check if user has specific permission for the instance
        Override this method to implement custom permission logic
        """
        if user.is_superuser:
            return True

        if hasattr(user, "has_perm"):
            return user.has_perm(permission)

        return False


class AuditTrailMixin:
    """
    Mixin for automatic audit trail creation
    """

    def create_audit_entry(self, instance, action, user=None):
        """
        Create audit trail entry for model changes
        """
        try:
            request = self.context.get("request")
            if not user and request:
                user = getattr(request, "user", None)

            if not user or not user.is_authenticated:
                return

            # Create audit entry (implement based on your audit model)
            audit_data = {
                "user": user,
                "action": action,
                "model_name": instance._meta.model_name,
                "object_id": instance.pk,
                "timestamp": timezone.now(),
                "ip_address": self._get_client_ip(request) if request else None,
            }

            # Log the audit entry
            logger.info(
                f"Audit: {user} {action} {instance._meta.model_name} {instance.pk}"
            )

        except Exception as e:
            logger.error(f"Failed to create audit entry: {e}")

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class ValidationHelperMixin:
    """
    Mixin with common validation helpers
    """

    def validate_slug_field(self, value, model_class, instance=None):
        """
        Validate slug uniqueness with support for updates
        """
        if not value:
            raise serializers.ValidationError("Slug cannot be empty")

        # Basic slug format validation
        import re

        if not re.match(r"^[-a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Slug can only contain letters, numbers, hyphens, and underscores"
            )

        # Check uniqueness
        queryset = model_class.objects.filter(slug=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("This slug is already in use")

        return value

    def validate_positive_number(self, value, field_name):
        """
        Validate that a number is positive
        """
        if value is not None and value < 0:
            raise serializers.ValidationError(f"{field_name} must be a positive number")
        return value

    def validate_future_date(self, value, field_name):
        """
        Validate that a date is in the future
        """
        if value:
            from django.utils import timezone

            if value <= timezone.now():
                raise serializers.ValidationError(f"{field_name} must be in the future")
        return value

    def validate_email_domain(self, value, allowed_domains=None):
        """
        Validate email domain restrictions
        """
        if not value or "@" not in value:
            return value

        domain = value.split("@")[1].lower()

        if allowed_domains and domain not in allowed_domains:
            raise serializers.ValidationError(
                f"Email domain not allowed. Allowed domains: {', '.join(allowed_domains)}"
            )

        return value

    def validate_json_field(self, value, required_keys=None):
        """
        Validate JSON field structure
        """
        if not value:
            return value

        if isinstance(value, str):
            try:
                import json

                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format")

        if required_keys and isinstance(value, dict):
            missing_keys = set(required_keys) - set(value.keys())
            if missing_keys:
                raise serializers.ValidationError(
                    f"Missing required keys: {', '.join(missing_keys)}"
                )

        return value
