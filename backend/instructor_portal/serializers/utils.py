#
# File Path: instructor_portal/serializers/utils.py
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
# Validation utilities and helper functions for instructor_portal serializers
# Split from original serializers.py maintaining exact code compatibility

import os
import hashlib
import logging
import re
from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from django.conf import settings

logger = logging.getLogger(__name__)

# Constants from original file
MAX_BULK_OPERATION_SIZE = getattr(settings, 'MAX_BULK_OPERATION_SIZE', 100)
MAX_RESOURCE_FILE_SIZE = getattr(settings, 'MAX_RESOURCE_FILE_SIZE', 100 * 1024 * 1024)  # 100MB
MAX_THUMBNAIL_SIZE = getattr(settings, 'MAX_THUMBNAIL_SIZE', 5 * 1024 * 1024)  # 5MB
MAX_JSON_COMPRESSION_SIZE = getattr(settings, 'MAX_JSON_COMPRESSION_SIZE', 10 * 1024 * 1024)  # 10MB
PERMISSIONS_CACHE_TIMEOUT = getattr(settings, 'PERMISSIONS_CACHE_TIMEOUT', 180)  # 3 minutes

def safe_decimal_conversion(value, default=Decimal('0.00'), raise_validation_error=False):
    """
    Safely convert value to Decimal for financial data

    Args:
        value: The value to convert
        default: Default value if conversion fails
        raise_validation_error: If True, raises ValidationError instead of returning default
    """
    try:
        if value is None:
            return default
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as e:
        if raise_validation_error:
            raise serializers.ValidationError(f"Invalid decimal value: {value}. Error: {e}")
        return default

def validate_file_path_security(file_path):
    """
    Enhanced file path security validation
    Handles both string paths and file objects safely
    Rejects absolute paths and Windows drive letters
    """
    # Convert to string if we received a file object or other type
    if file_path is None:
        return False

    try:
        path_str = str(file_path)
    except Exception:
        return False

    # Normalize path
    normalized_path = os.path.normpath(path_str)

    # Check for path traversal attempts
    if '..' in normalized_path:
        return False

    # Check for absolute paths (Unix/Linux/Mac)
    if normalized_path.startswith('/'):
        return False

    # Check for Windows drive letters (C:\, D:\, etc.)
    if re.match(r'^[a-zA-Z]:\\', normalized_path):
        return False

    # Check for UNC paths (\\server\share)
    if normalized_path.startswith('\\\\'):
        return False

    return True

def validate_instructor_tier_access(instructor_profile, required_tier, feature_name):
    """Validate if instructor tier has access to specific feature"""
    from ..models import InstructorProfile

    tier_hierarchy = {
        InstructorProfile.Tier.BRONZE: 1,
        InstructorProfile.Tier.SILVER: 2,
        InstructorProfile.Tier.GOLD: 3,
        InstructorProfile.Tier.PLATINUM: 4,
        InstructorProfile.Tier.DIAMOND: 5,
    }

    current_level = tier_hierarchy.get(instructor_profile.tier, 1)
    required_level = tier_hierarchy.get(required_tier, 1)

    if current_level < required_level:
        raise serializers.ValidationError(
            f"{feature_name} requires {required_tier} tier or higher. Current tier: {instructor_profile.tier}"
        )

def calculate_content_hash(content):
    """Calculate SHA-256 hash of content for versioning"""
    # Always ensure content is encoded as UTF-8 string
    if isinstance(content, str):
        encoded_content = content.encode('utf-8')
    else:
        try:
            encoded_content = str(content).encode('utf-8')
        except Exception:
            # If we can't convert to string, use the repr
            encoded_content = repr(content).encode('utf-8')

    return hashlib.sha256(encoded_content).hexdigest()
