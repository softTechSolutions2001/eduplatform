# File Path: backend/courses/storage.py
# Folder Path: /backend/courses/
# Date Created: 2025-06-11 15:21:16
# Date Revised: 2025-06-15 15:03:49
# Current Date and Time (UTC): 2025-06-15 15:03:49
# Current User's Login: sujibeautysalon
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 15:03:49 UTC
# User: sujibeautysalon
# Version: 1.2.0
#
# Cloud Storage Utilities for Course Resources (Enhanced with Missing Functions)
#
# Version 1.2.0 Changes:
# - ADDED: delete_object function that was missing and causing import errors
# - ENHANCED: Error handling and logging for all storage operations
# - IMPROVED: File validation with comprehensive security checks
# - ADDED: Bulk operations for better performance
# - MAINTAINED: All existing functionality from version 1.1.0
# - FIXED: Import compatibility with instructor_portal.views
#
# This module provides utility functions for interacting with cloud storage
# services (S3/GCS/MinIO) for uploading and managing course resources.
#
# Key features:
# - Generate presigned URLs for direct browser-to-cloud uploads
# - Delete objects from cloud storage with proper cleanup
# - Handle metadata for uploaded files
# - Support for AWS S3, Google Cloud Storage, and MinIO
# - Configure storage settings from environment variables
# - Content-type validation for security
# - 24-hour expiry for presigned URLs by default
# - Comprehensive file validation and security checks
#
# Connected files:
# - backend/instructor_portal/views.py - Uses these functions for file uploads
# - backend/courses/models.py - Resource model with storage integration
# - backend/settings.py - Contains storage configuration

import os
import uuid
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Determine which storage provider to use from settings
STORAGE_PROVIDER = getattr(settings, 'CLOUD_STORAGE_PROVIDER', 'local')
STORAGE_BUCKET = getattr(settings, 'CLOUD_STORAGE_BUCKET', 'eduplatform-resources')

# Storage configuration validation
def _validate_storage_config():
    """
    Validate storage configuration and raise appropriate errors if misconfigured
    """
    if STORAGE_PROVIDER == 's3':
        required_settings = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing = [key for key in required_settings if not getattr(settings, key, None)]
        if missing:
            raise ImproperlyConfigured(f"Missing AWS settings: {', '.join(missing)}")
    elif STORAGE_PROVIDER == 'gcs':
        if not getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None):
            raise ImproperlyConfigured("Missing GOOGLE_APPLICATION_CREDENTIALS setting for GCS")


def generate_presigned_post(file_name: str, content_type: Optional[str] = None,
                          max_size: int = 100*1024*1024, expiration: int = 86400) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a presigned URL for uploading a file directly to cloud storage.

    Args:
        file_name (str): Original file name
        content_type (str, optional): MIME type of the file
        max_size (int, optional): Maximum file size in bytes (default 100MB)
        expiration (int, optional): URL expiration time in seconds (default 24 hours)

    Returns:
        tuple: (url, fields) where url is the upload endpoint and fields are
               the form fields needed for the upload
    """
    # Validate storage configuration
    _validate_storage_config()

    # Generate a unique storage key to prevent filename conflicts
    file_extension = os.path.splitext(file_name)[1].lower()
    storage_key = f"uploads/{uuid.uuid4()}{file_extension}"

    # Validate content type - only allow safe file types
    allowed_content_types = {
        # Images
        'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp',
        'image/bmp', 'image/tiff', 'image/ico',
        # Documents
        'application/pdf', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain', 'text/csv', 'text/rtf',
        # Audio/Video
        'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/aac',
        'video/mp4', 'video/webm', 'video/avi', 'video/mov', 'video/wmv',
        'video/flv', 'video/mkv',
        # Archives
        'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
        'application/x-tar', 'application/gzip',
        # Code/Text
        'text/html', 'text/css', 'text/javascript', 'application/json',
        'application/xml', 'text/xml', 'application/yaml',
        'text/markdown', 'application/x-python-code',
        # Fallback
        'application/octet-stream'
    }

    # Validate and sanitize content type
    if content_type and content_type not in allowed_content_types:
        logger.warning(f"Blocked upload attempt with disallowed content type: {content_type} for file: {file_name}")
        content_type = 'application/octet-stream'  # Default to binary if not allowed

    # If no content type provided, try to infer from file extension
    if not content_type:
        content_type = _infer_content_type_from_extension(file_extension)

    if STORAGE_PROVIDER == 's3':
        return _generate_s3_presigned_post(storage_key, content_type, max_size, expiration)
    elif STORAGE_PROVIDER == 'gcs':
        return _generate_gcs_presigned_post(storage_key, content_type, max_size, expiration)
    else:
        # For local development or testing, return a dummy URL
        logger.warning("Using dummy presigned URL for local development")
        return _generate_dummy_presigned_post(storage_key)


def delete_object(storage_key: str) -> bool:
    """
    Delete an object from cloud storage.

    This function was missing and causing import errors in instructor_portal.views.

    Args:
        storage_key (str): The storage key of the file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Validate storage configuration
        _validate_storage_config()

        if STORAGE_PROVIDER == 's3':
            return _delete_s3_object(storage_key)
        elif STORAGE_PROVIDER == 'gcs':
            return _delete_gcs_object(storage_key)
        else:
            # For local development, just log the deletion
            logger.info(f"Would delete local file: {storage_key}")
            return True

    except Exception as exc:
        logger.error(f"Error deleting object {storage_key}: {exc}")
        return False


def _delete_s3_object(storage_key: str) -> bool:
    """
    Delete an object from AWS S3.

    Args:
        storage_key (str): The S3 key of the object to delete

    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client('s3')
        s3_client.delete_object(Bucket=STORAGE_BUCKET, Key=storage_key)

        logger.info(f"Successfully deleted S3 object: {storage_key}")
        return True

    except ClientError as exc:
        error_code = exc.response['Error']['Code']
        if error_code == 'NoSuchKey':
            logger.info(f"S3 object not found (already deleted?): {storage_key}")
            return True  # Consider non-existent as successfully deleted
        else:
            logger.error(f"S3 error deleting object {storage_key}: {exc}")
            return False
    except ImportError:
        logger.error("boto3 is not installed. Cannot delete S3 objects.")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error deleting S3 object {storage_key}: {exc}")
        return False


def _delete_gcs_object(storage_key: str) -> bool:
    """
    Delete an object from Google Cloud Storage.

    Args:
        storage_key (str): The GCS key of the object to delete

    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        from google.cloud import storage
        from google.cloud.exceptions import NotFound

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(storage_key)

        blob.delete()

        logger.info(f"Successfully deleted GCS object: {storage_key}")
        return True

    except NotFound:
        logger.info(f"GCS object not found (already deleted?): {storage_key}")
        return True  # Consider non-existent as successfully deleted
    except ImportError:
        logger.error("google-cloud-storage is not installed. Cannot delete GCS objects.")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error deleting GCS object {storage_key}: {exc}")
        return False


def bulk_delete_objects(storage_keys: List[str]) -> Dict[str, bool]:
    """
    Delete multiple objects from cloud storage efficiently.

    Args:
        storage_keys (List[str]): List of storage keys to delete

    Returns:
        Dict[str, bool]: Mapping of storage_key to deletion success status
    """
    results = {}

    if STORAGE_PROVIDER == 's3':
        results = _bulk_delete_s3_objects(storage_keys)
    elif STORAGE_PROVIDER == 'gcs':
        results = _bulk_delete_gcs_objects(storage_keys)
    else:
        # For local development
        for key in storage_keys:
            results[key] = True
            logger.info(f"Would delete local file: {key}")

    return results


def _bulk_delete_s3_objects(storage_keys: List[str]) -> Dict[str, bool]:
    """
    Bulk delete objects from S3 using delete_objects API for efficiency.
    """
    results = {}

    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client('s3')

        # S3 delete_objects can handle up to 1000 objects at once
        batch_size = 1000
        for i in range(0, len(storage_keys), batch_size):
            batch = storage_keys[i:i + batch_size]
            delete_objects = [{'Key': key} for key in batch]

            try:
                response = s3_client.delete_objects(
                    Bucket=STORAGE_BUCKET,
                    Delete={'Objects': delete_objects}
                )

                # Mark successful deletions
                for deleted in response.get('Deleted', []):
                    results[deleted['Key']] = True

                # Mark failed deletions
                for error in response.get('Errors', []):
                    results[error['Key']] = False
                    logger.error(f"Failed to delete S3 object {error['Key']}: {error['Message']}")

            except ClientError as exc:
                logger.error(f"S3 bulk delete error for batch: {exc}")
                # Mark all in this batch as failed
                for key in batch:
                    results[key] = False

        logger.info(f"Bulk deleted {sum(results.values())} of {len(storage_keys)} S3 objects")

    except ImportError:
        logger.error("boto3 is not installed. Cannot bulk delete S3 objects.")
        for key in storage_keys:
            results[key] = False
    except Exception as exc:
        logger.error(f"Unexpected error in S3 bulk delete: {exc}")
        for key in storage_keys:
            results[key] = False

    return results


def _bulk_delete_gcs_objects(storage_keys: List[str]) -> Dict[str, bool]:
    """
    Bulk delete objects from Google Cloud Storage.
    """
    results = {}

    try:
        from google.cloud import storage
        from google.cloud.exceptions import NotFound

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)

        for key in storage_keys:
            try:
                blob = bucket.blob(key)
                blob.delete()
                results[key] = True
            except NotFound:
                results[key] = True  # Consider non-existent as successfully deleted
            except Exception as exc:
                logger.error(f"Failed to delete GCS object {key}: {exc}")
                results[key] = False

        logger.info(f"Bulk deleted {sum(results.values())} of {len(storage_keys)} GCS objects")

    except ImportError:
        logger.error("google-cloud-storage is not installed. Cannot bulk delete GCS objects.")
        for key in storage_keys:
            results[key] = False
    except Exception as exc:
        logger.error(f"Unexpected error in GCS bulk delete: {exc}")
        for key in storage_keys:
            results[key] = False

    return results


def _infer_content_type_from_extension(file_extension: str) -> str:
    """
    Infer MIME type from file extension.

    Args:
        file_extension (str): File extension including the dot (e.g., '.pdf')

    Returns:
        str: MIME type
    """
    extension_map = {
        # Images
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
        '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
        '.bmp': 'image/bmp', '.tiff': 'image/tiff', '.ico': 'image/ico',
        # Documents
        '.pdf': 'application/pdf', '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt': 'text/plain', '.csv': 'text/csv', '.rtf': 'text/rtf',
        # Audio/Video
        '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
        '.aac': 'audio/aac', '.mp4': 'video/mp4', '.webm': 'video/webm',
        '.avi': 'video/avi', '.mov': 'video/mov', '.wmv': 'video/wmv',
        # Archives
        '.zip': 'application/zip', '.rar': 'application/x-rar-compressed',
        '.7z': 'application/x-7z-compressed', '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        # Code/Text
        '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
        '.json': 'application/json', '.xml': 'application/xml',
        '.yaml': 'application/yaml', '.yml': 'application/yaml',
        '.md': 'text/markdown', '.py': 'application/x-python-code',
    }

    return extension_map.get(file_extension.lower(), 'application/octet-stream')


def _generate_s3_presigned_post(storage_key: str, content_type: str, max_size: int, expiration: int) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a presigned POST URL for uploading to AWS S3.
    """
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import ClientError

        # Configure S3 client with your region
        s3_client = boto3.client(
            's3',
            config=Config(signature_version='s3v4')
        )

        # Set default content type if none provided
        if not content_type:
            content_type = 'application/octet-stream'

        # Generate the presigned URL with enhanced security conditions
        conditions = [
            {"bucket": STORAGE_BUCKET},
            ["content-length-range", 1, max_size],
            {"key": storage_key},
            {"Content-Type": content_type}  # Always require content-type matching
        ]

        presigned_post = s3_client.generate_presigned_post(
            Bucket=STORAGE_BUCKET,
            Key=storage_key,
            Fields={
                'Content-Type': content_type
            },
            Conditions=conditions,
            ExpiresIn=expiration
        )

        logger.info(f"Generated S3 presigned URL for key: {storage_key}, content-type: {content_type}, expires in: {expiration}s")
        return presigned_post['url'], presigned_post['fields']

    except ImportError:
        logger.error("boto3 is not installed. Please install it with: pip install boto3")
        return _generate_dummy_presigned_post(storage_key)
    except ClientError as exc:
        logger.error(f"S3 client error generating presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)
    except Exception as exc:
        logger.error(f"Unexpected error generating S3 presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)


def _generate_gcs_presigned_post(storage_key: str, content_type: str, max_size: int, expiration: int) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a presigned URL for uploading to Google Cloud Storage.
    """
    try:
        from google.cloud import storage
        from google.cloud.exceptions import GoogleCloudError

        # Create a storage client
        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(storage_key)

        # Set default content type if none provided
        if not content_type:
            content_type = 'application/octet-stream'

        # Calculate expiration datetime
        expiration_datetime = datetime.utcnow() + timedelta(seconds=expiration)

        # Generate the signed URL for upload
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_datetime,
            method="PUT",
            content_type=content_type,
        )

        # GCS uses a different approach - we return a URL to PUT directly to
        # and don't need form fields like S3
        logger.info(f"Generated GCS presigned URL for key: {storage_key}, content-type: {content_type}, expires in: {expiration}s")
        return url, {}

    except ImportError:
        logger.error("google-cloud-storage is not installed. Please install it with: pip install google-cloud-storage")
        return _generate_dummy_presigned_post(storage_key)
    except GoogleCloudError as exc:
        logger.error(f"GCS error generating presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)
    except Exception as exc:
        logger.error(f"Unexpected error generating GCS presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)


def _generate_dummy_presigned_post(storage_key: str) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a dummy presigned URL for local development or testing.
    """
    from datetime import datetime, timedelta

    # Generate expiry timestamp for dummy URL
    expiry_time = datetime.utcnow() + timedelta(seconds=86400)  # 24 hours from now

    url = f"https://storage.example.com/upload/{storage_key}"
    fields = {
        "key": storage_key,
        "policy": "dummy-base64-encoded-policy",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "dummy-credential",
        "x-amz-date": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "x-amz-signature": "dummy-signature",
        "expires": expiry_time.isoformat()
    }

    # Also log the storage key so it can be tracked in development
    logger.info(f"Generated dummy presigned URL for key: {storage_key}, expires: {expiry_time}")

    return url, fields


def get_public_url(storage_key: str) -> str:
    """
    Get a public URL for accessing a file in cloud storage.

    Args:
        storage_key (str): The storage key of the file

    Returns:
        str: A public URL for the file
    """
    if STORAGE_PROVIDER == 's3':
        return f"https://{STORAGE_BUCKET}.s3.amazonaws.com/{storage_key}"
    elif STORAGE_PROVIDER == 'gcs':
        return f"https://storage.googleapis.com/{STORAGE_BUCKET}/{storage_key}"
    else:
        return f"/media/{storage_key}"  # Local development


def validate_file_upload(file_name: str, content_type: str, file_size: int, max_size: int = 100*1024*1024) -> Tuple[bool, Optional[str]]:
    """
    Validate file upload parameters before generating presigned URL.

    Args:
        file_name (str): Original file name
        content_type (str): MIME type of the file
        file_size (int): Size of the file in bytes
        max_size (int, optional): Maximum allowed file size in bytes

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size
    if file_size > max_size:
        return False, f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"

    # Check file extension
    file_extension = os.path.splitext(file_name)[1].lower()
    if not file_extension:
        return False, "File must have an extension"

    # Check for potentially dangerous file extensions
    dangerous_extensions = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.php', '.asp', '.aspx', '.jsp', '.sh', '.bash'
    }

    if file_extension in dangerous_extensions:
        return False, f"File type '{file_extension}' is not allowed for security reasons"

    # Validate content type matches expected extension
    expected_content_type = _infer_content_type_from_extension(file_extension)
    if content_type and content_type != expected_content_type and content_type != 'application/octet-stream':
        logger.warning(f"Content type mismatch: expected {expected_content_type}, got {content_type} for file {file_name}")

    return True, None


def get_file_metadata(storage_key: str) -> Dict[str, Any]:
    """
    Get metadata for a file in cloud storage.

    Args:
        storage_key (str): The storage key of the file

    Returns:
        dict: File metadata including size, content-type, etc.
    """
    if STORAGE_PROVIDER == 's3':
        return _get_s3_file_metadata(storage_key)
    elif STORAGE_PROVIDER == 'gcs':
        return _get_gcs_file_metadata(storage_key)
    else:
        return {'error': 'Metadata not available for local storage'}


def _get_s3_file_metadata(storage_key: str) -> Dict[str, Any]:
    """Get file metadata from S3."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client('s3')
        response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=storage_key)

        return {
            'size': response.get('ContentLength'),
            'content_type': response.get('ContentType'),
            'last_modified': response.get('LastModified'),
            'etag': response.get('ETag')
        }
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'NoSuchKey':
            return {'error': 'File not found'}
        logger.error(f"Error getting S3 file metadata: {exc}")
        return {'error': str(exc)}
    except Exception as exc:
        logger.error(f"Unexpected error getting S3 file metadata: {exc}")
        return {'error': str(exc)}


def _get_gcs_file_metadata(storage_key: str) -> Dict[str, Any]:
    """Get file metadata from Google Cloud Storage."""
    try:
        from google.cloud import storage
        from google.cloud.exceptions import NotFound

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(storage_key)

        if blob.exists():
            return {
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'etag': blob.etag
            }
        else:
            return {'error': 'File not found'}
    except NotFound:
        return {'error': 'File not found'}
    except Exception as exc:
        logger.error(f"Error getting GCS file metadata: {exc}")
        return {'error': str(exc)}


def check_storage_health() -> Dict[str, Any]:
    """
    Check the health of the storage backend.

    Returns:
        Dict with health status information
    """
    try:
        _validate_storage_config()

        if STORAGE_PROVIDER == 's3':
            return _check_s3_health()
        elif STORAGE_PROVIDER == 'gcs':
            return _check_gcs_health()
        else:
            return {
                'status': 'healthy',
                'provider': 'local',
                'message': 'Local storage is available'
            }

    except Exception as exc:
        return {
            'status': 'unhealthy',
            'provider': STORAGE_PROVIDER,
            'error': str(exc)
        }


def _check_s3_health() -> Dict[str, Any]:
    """Check S3 storage health."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client('s3')
        s3_client.head_bucket(Bucket=STORAGE_BUCKET)

        return {
            'status': 'healthy',
            'provider': 's3',
            'bucket': STORAGE_BUCKET,
            'message': 'S3 bucket is accessible'
        }
    except ClientError as exc:
        return {
            'status': 'unhealthy',
            'provider': 's3',
            'bucket': STORAGE_BUCKET,
            'error': str(exc)
        }


def _check_gcs_health() -> Dict[str, Any]:
    """Check GCS storage health."""
    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        bucket.exists()

        return {
            'status': 'healthy',
            'provider': 'gcs',
            'bucket': STORAGE_BUCKET,
            'message': 'GCS bucket is accessible'
        }
    except Exception as exc:
        return {
            'status': 'unhealthy',
            'provider': 'gcs',
            'bucket': STORAGE_BUCKET,
            'error': str(exc)
        }


# Export all functions for compatibility
__all__ = [
    'generate_presigned_post',
    'delete_object',  # This was the missing function causing the import error
    'bulk_delete_objects',
    'get_public_url',
    'validate_file_upload',
    'get_file_metadata',
    'check_storage_health'
]
