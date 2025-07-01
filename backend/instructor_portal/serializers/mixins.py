#
# File Path: instructor_portal/serializers/mixins.py
# Folder Path: instructor_portal/serializers/
# Date Created: 2025-06-26 13:35:44
# Date Revised: 2025-06-27 06:16:38
# Current Date and Time (UTC): 2025-06-27 06:16:38
# Current User's Login: softTechSolutions2001
# Author: softTechSolutions2001
# Last Modified By: softTechSolutions2001
# Last Modified: 2025-06-27 06:16:38 UTC
# User: softTechSolutions2001
# Version: 1.0.1
#
# Shared mixins and utilities for instructor_portal serializers
# Split from original serializers.py maintaining exact code compatibility

import json
import base64
import zlib
import logging
from django.conf import settings
from rest_framework import serializers

logger = logging.getLogger(__name__)

# Configuration constants
MAX_JSON_COMPRESSION_SIZE = getattr(settings, 'MAX_JSON_COMPRESSION_SIZE', 10 * 1024 * 1024)  # 10MB

class JsonFieldMixin:
    """Mixin for handling JSON field validation and coercion"""

    def _coerce_json(self, value):
        """Coerce string to JSON with error handling"""
        if isinstance(value, str):
            try:
                if len(value.encode('utf-8')) > MAX_JSON_COMPRESSION_SIZE:
                    raise serializers.ValidationError(
                        f"JSON data too large. Maximum size: {MAX_JSON_COMPRESSION_SIZE // (1024*1024)}MB"
                    )
                return json.loads(value)
            except json.JSONDecodeError as exc:
                logger.error("JSON coercion failed: %s", exc)
                raise serializers.ValidationError(f"Invalid JSON format: {exc}")

        return value

    def _inflate_modules_if_needed(self, data):
        """Decompress and convert modules_json_gz to modules_json if present"""
        gz_key = 'modules_json_gz'
        if gz_key in data:
            try:
                compressed_data = data[gz_key]
                try:
                    raw = base64.b64decode(compressed_data)
                except Exception as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Invalid base64 encoding: {exc}'}
                    )

                try:
                    json_bytes = zlib.decompress(raw, wbits=-15)
                except Exception as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Decompression failed: {exc}'}
                    )

                if len(json_bytes) > MAX_JSON_COMPRESSION_SIZE:
                    raise serializers.ValidationError(
                        {'modules_json_gz': 'Decompressed data too large'}
                    )

                try:
                    json_str = json_bytes.decode('utf-8')
                    data['modules_json'] = json_str
                    # Fix for audit: log original compressed size (raw bytes length) instead of base64 string length
                    logger.info("Successfully decompressed modules_json_gz (%d bytes -> %d bytes)",
                              len(raw), len(json_str))
                except UnicodeDecodeError as exc:
                    raise serializers.ValidationError(
                        {'modules_json_gz': f'Invalid UTF-8 encoding: {exc}'}
                    )
            except serializers.ValidationError:
                raise
            except Exception as exc:
                logger.error("Unexpected error in modules decompression: %s", exc)
                raise serializers.ValidationError(
                    {'modules_json_gz': f'Decompression failed: {exc}'}
                )

        return data

    def validate_json_list(self, value, field_name, max_items=None):
        """Validate JSON field as list with security and limits"""
        if value is None:
            return []

        value = self._coerce_json(value)

        if not isinstance(value, list):
            raise serializers.ValidationError(f"{field_name} must be a list.")

        if max_items and len(value) > max_items:
            raise serializers.ValidationError(f"{field_name} cannot have more than {max_items} items.")

        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise serializers.ValidationError(f"{field_name}[{i}] must be a string.")

        return value

# Export the validate_json_list function directly for backward compatibility
validate_json_list = JsonFieldMixin().validate_json_list
