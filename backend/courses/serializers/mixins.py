# Base mixins for serializers
#
# File Path: backend/courses/serializers/mixins.py
# Folder Path: backend/courses/serializers/
# Date Created: 2025-06-26 10:15:30
# Date Revised: 2025-06-26 16:20:53
# Current Date and Time (UTC): 2025-06-26 16:20:53
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-26 16:20:53 UTC
# User: softTechSolutions2001
# Version: 3.0.0
#
# Base mixins for serializer functionality

import copy
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

logger = logging.getLogger(__name__)

class ContextPropagationMixin:
    """
    Mixin to ensure proper context propagation to nested serializers
    FIXED: Nested serializers losing context issue
    """

    def get_serializer_context_for_nested(self, additional_context=None):
        """Get enhanced context for nested serializers"""
        context = self.context.copy()
        if additional_context:
            context.update(additional_context)
        return context

    def to_representation(self, instance):
        """
        Enhanced representation with immutable data handling
        FIXED: to_representation mutating data in-place
        """
        # Create a deep copy to prevent mutation of original data
        data = super().to_representation(instance)
        return self._process_representation_safely(copy.deepcopy(data), instance)

    def _process_representation_safely(self, data, instance):
        """
        Process representation data safely without mutations
        Override in subclasses for custom processing
        """
        return data


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
        if hasattr(self, 'setup_eager_loading'):
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
        """
        try:
            # Create temporary instance for validation if not provided
            if instance is None:
                instance = self.Meta.model(**data)
            else:
                for key, value in data.items():
                    setattr(instance, key, value)

            # Use model's clean method for validation
            instance.clean()
            return data

        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                raise serializers.ValidationError(e.message_dict)
            else:
                raise serializers.ValidationError(str(e))
