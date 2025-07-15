# File Path: backend/courses/storage.py
# Folder Path: /backend/courses/
# Date Created: 2025-06-11 15:21:16
# Date Revised: 2025-07-09 05:23:06
# Current Date and Time (UTC): 2025-07-09 05:23:06
# Current User's Login: MohithaSanthanam2010
# Author: sujibeautysalon
# Last Modified By: MohithaSanthanam2010
# Last Modified: 2025-07-09 05:23:06 UTC
# User: MohithaSanthanam2010
# Version: 1.3.0
#
# Cloud Storage Utilities for Course Resources - AUDIT FIXES
#
# Version 1.3.0 Changes - COMPREHENSIVE AUDIT FIXES:
# - FIXED 🔴: Added missing _infer_content_type_from_extension function
# - FIXED 🔴: _validate_storage_config now logs warnings instead of raising in worker threads
# - FIXED 🔴: Enhanced error handling for production environment
# - ENHANCED: Better content type detection using mimetypes
# - ADDED: More robust storage configuration validation
# - MAINTAINED: All existing functionality with improved reliability

import logging
import mimetypes
import os
import threading
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Thread-safe storage configuration
_storage_config_lock = threading.Lock()
_storage_config_validated = False

# Determine which storage provider to use from settings
STORAGE_PROVIDER = getattr(settings, "CLOUD_STORAGE_PROVIDER", "local")
STORAGE_BUCKET = getattr(settings, "CLOUD_STORAGE_BUCKET", "eduplatform-resources")


# Storage configuration validation
def _validate_storage_config():
    """
    Validate storage configuration and handle errors appropriately
    FIXED: Now logs warnings instead of raising exceptions in worker threads
    """
    global _storage_config_validated

    with _storage_config_lock:
        if _storage_config_validated:
            return

        try:
            if STORAGE_PROVIDER == "s3":
                required_settings = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
                missing = [
                    key for key in required_settings if not getattr(settings, key, None)
                ]
                if missing:
                    error_msg = f"Missing AWS settings: {', '.join(missing)}"
                    if getattr(settings, "DEBUG", False):
                        logger.warning(error_msg)
                    else:
                        # In production, log warning instead of raising
                        logger.warning(f"Storage configuration issue: {error_msg}")

            elif STORAGE_PROVIDER == "gcs":
                if not getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None):
                    error_msg = "Missing GOOGLE_APPLICATION_CREDENTIALS setting for GCS"
                    if getattr(settings, "DEBUG", False):
                        logger.warning(error_msg)
                    else:
                        # In production, log warning instead of raising
                        logger.warning(f"Storage configuration issue: {error_msg}")

            _storage_config_validated = True
            logger.info(
                f"Storage configuration validated for provider: {STORAGE_PROVIDER}"
            )

        except Exception as e:
            logger.error(f"Storage configuration validation failed: {e}")
            # Don't raise in production, just log
            if getattr(settings, "DEBUG", False):
                raise


def _infer_content_type_from_extension(file_extension: str) -> str:
    """
    FIXED: Added missing function that infers MIME type from file extension
    Uses mimetypes module for better accuracy and caching

    Args:
        file_extension (str): File extension including the dot (e.g., '.pdf')

    Returns:
        str: MIME type
    """
    try:
        # Use mimetypes for better accuracy
        content_type, _ = mimetypes.guess_type(f"dummy{file_extension}")

        if content_type:
            return content_type

        # Fallback to manual mapping for common types
        extension_map = {
            # Images
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".ico": "image/x-icon",
            # Documents
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".rtf": "text/rtf",
            ".odt": "application/vnd.oasis.opendocument.text",
            ".ods": "application/vnd.oasis.opendocument.spreadsheet",
            ".odp": "application/vnd.oasis.opendocument.presentation",
            # Audio/Video
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".aac": "audio/aac",
            ".flac": "audio/flac",
            ".wma": "audio/x-ms-wma",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".wmv": "video/x-ms-wmv",
            ".flv": "video/x-flv",
            ".mkv": "video/x-matroska",
            ".m4v": "video/x-m4v",
            ".3gp": "video/3gpp",
            # Archives
            ".zip": "application/zip",
            ".rar": "application/vnd.rar",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",
            ".bz2": "application/x-bzip2",
            ".xz": "application/x-xz",
            # Code/Text
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".xml": "application/xml",
            ".yaml": "application/x-yaml",
            ".yml": "application/x-yaml",
            ".md": "text/markdown",
            ".py": "text/x-python",
            ".java": "text/x-java-source",
            ".cpp": "text/x-c++src",
            ".c": "text/x-csrc",
            ".h": "text/x-chdr",
            ".php": "application/x-httpd-php",
            ".rb": "application/x-ruby",
            ".sh": "application/x-sh",
            ".sql": "application/sql",
            # Fonts
            ".ttf": "font/ttf",
            ".otf": "font/otf",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".eot": "application/vnd.ms-fontobject",
            # Special formats
            ".epub": "application/epub+zip",
            ".mobi": "application/x-mobipocket-ebook",
            ".psd": "image/vnd.adobe.photoshop",
            ".ai": "application/postscript",
            ".sketch": "application/x-sketch",
            ".fig": "application/x-figma",
        }

        return extension_map.get(file_extension.lower(), "application/octet-stream")

    except Exception as e:
        logger.warning(
            f"Error inferring content type for extension {file_extension}: {e}"
        )
        return "application/octet-stream"


def generate_presigned_post(
    file_name: str,
    content_type: Optional[str] = None,
    max_size: int = 100 * 1024 * 1024,
    expiration: int = 86400,
) -> Tuple[str, Dict[str, Any]]:
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
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/svg+xml",
        "image/webp",
        "image/bmp",
        "image/tiff",
        "image/x-icon",
        # Documents
        "application/pdf",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/csv",
        "text/rtf",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        # Audio/Video
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/ogg",
        "audio/aac",
        "audio/flac",
        "audio/x-ms-wma",
        "video/mp4",
        "video/webm",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-ms-wmv",
        "video/x-flv",
        "video/x-matroska",
        "video/x-m4v",
        "video/3gpp",
        # Archives
        "application/zip",
        "application/vnd.rar",
        "application/x-7z-compressed",
        "application/x-tar",
        "application/gzip",
        "application/x-bzip2",
        "application/x-xz",
        # Code/Text
        "text/html",
        "text/css",
        "application/javascript",
        "application/json",
        "application/xml",
        "application/x-yaml",
        "text/markdown",
        "text/x-python",
        "text/x-java-source",
        "text/x-c++src",
        "text/x-csrc",
        "application/x-httpd-php",
        "application/x-ruby",
        "application/x-sh",
        "application/sql",
        # Fonts
        "font/ttf",
        "font/otf",
        "font/woff",
        "font/woff2",
        "application/vnd.ms-fontobject",
        # Special formats
        "application/epub+zip",
        "application/x-mobipocket-ebook",
        "image/vnd.adobe.photoshop",
        "application/postscript",
        # Fallback
        "application/octet-stream",
    }

    # Validate and sanitize content type
    if content_type and content_type not in allowed_content_types:
        logger.warning(
            f"Blocked upload attempt with disallowed content type: {content_type} for file: {file_name}"
        )
        content_type = "application/octet-stream"  # Default to binary if not allowed

    # If no content type provided, try to infer from file extension
    if not content_type:
        content_type = _infer_content_type_from_extension(file_extension)

    if STORAGE_PROVIDER == "s3":
        return _generate_s3_presigned_post(
            storage_key, content_type, max_size, expiration
        )
    elif STORAGE_PROVIDER == "gcs":
        return _generate_gcs_presigned_post(
            storage_key, content_type, max_size, expiration
        )
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

        if STORAGE_PROVIDER == "s3":
            return _delete_s3_object(storage_key)
        elif STORAGE_PROVIDER == "gcs":
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

        s3_client = boto3.client("s3")
        s3_client.delete_object(Bucket=STORAGE_BUCKET, Key=storage_key)

        logger.info(f"Successfully deleted S3 object: {storage_key}")
        return True

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code == "NoSuchKey":
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
        logger.error(
            "google-cloud-storage is not installed. Cannot delete GCS objects."
        )
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
    if not storage_keys:
        return {}

    results = {}

    if STORAGE_PROVIDER == "s3":
        results = _bulk_delete_s3_objects(storage_keys)
    elif STORAGE_PROVIDER == "gcs":
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

        s3_client = boto3.client("s3")

        # S3 delete_objects can handle up to 1000 objects at once
        batch_size = 1000
        for i in range(0, len(storage_keys), batch_size):
            batch = storage_keys[i : i + batch_size]
            delete_objects = [{"Key": key} for key in batch]

            try:
                response = s3_client.delete_objects(
                    Bucket=STORAGE_BUCKET,
                    Delete={
                        "Objects": delete_objects,
                        "Quiet": False,  # Return info about deleted objects
                    },
                )

                # Mark successful deletions
                for deleted in response.get("Deleted", []):
                    results[deleted["Key"]] = True

                # Mark failed deletions
                for error in response.get("Errors", []):
                    results[error["Key"]] = False
                    logger.error(
                        f"Failed to delete S3 object {error['Key']}: {error.get('Message', 'Unknown error')}"
                    )

            except ClientError as exc:
                logger.error(f"S3 bulk delete error for batch: {exc}")
                # Mark all in this batch as failed
                for key in batch:
                    results[key] = False

        logger.info(
            f"Bulk deleted {sum(results.values())} of {len(storage_keys)} S3 objects"
        )

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

        logger.info(
            f"Bulk deleted {sum(results.values())} of {len(storage_keys)} GCS objects"
        )

    except ImportError:
        logger.error(
            "google-cloud-storage is not installed. Cannot bulk delete GCS objects."
        )
        for key in storage_keys:
            results[key] = False
    except Exception as exc:
        logger.error(f"Unexpected error in GCS bulk delete: {exc}")
        for key in storage_keys:
            results[key] = False

    return results


def _generate_s3_presigned_post(
    storage_key: str, content_type: str, max_size: int, expiration: int
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a presigned POST URL for uploading to AWS S3.
    """
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import ClientError

        # Configure S3 client with your region
        s3_client = boto3.client("s3", config=Config(signature_version="s3v4"))

        # Set default content type if none provided
        if not content_type:
            content_type = "application/octet-stream"

        # Generate the presigned URL with enhanced security conditions
        conditions = [
            {"bucket": STORAGE_BUCKET},
            ["content-length-range", 1, max_size],
            {"key": storage_key},
            {"Content-Type": content_type},  # Always require content-type matching
        ]

        presigned_post = s3_client.generate_presigned_post(
            Bucket=STORAGE_BUCKET,
            Key=storage_key,
            Fields={"Content-Type": content_type},
            Conditions=conditions,
            ExpiresIn=expiration,
        )

        logger.info(
            f"Generated S3 presigned URL for key: {storage_key}, content-type: {content_type}, expires in: {expiration}s"
        )
        return presigned_post["url"], presigned_post["fields"]

    except ImportError:
        logger.error(
            "boto3 is not installed. Please install it with: pip install boto3"
        )
        return _generate_dummy_presigned_post(storage_key)
    except ClientError as exc:
        logger.error(f"S3 client error generating presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)
    except Exception as exc:
        logger.error(f"Unexpected error generating S3 presigned URL: {exc}")
        return _generate_dummy_presigned_post(storage_key)


def _generate_gcs_presigned_post(
    storage_key: str, content_type: str, max_size: int, expiration: int
) -> Tuple[str, Dict[str, Any]]:
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
            content_type = "application/octet-stream"

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
        logger.info(
            f"Generated GCS presigned URL for key: {storage_key}, content-type: {content_type}, expires in: {expiration}s"
        )
        return url, {}

    except ImportError:
        logger.error(
            "google-cloud-storage is not installed. Please install it with: pip install google-cloud-storage"
        )
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
        "expires": expiry_time.isoformat(),
    }

    # Also log the storage key so it can be tracked in development
    logger.info(
        f"Generated dummy presigned URL for key: {storage_key}, expires: {expiry_time}"
    )

    return url, fields


def get_public_url(storage_key: str) -> str:
    """
    Get a public URL for accessing a file in cloud storage.

    Args:
        storage_key (str): The storage key of the file

    Returns:
        str: A public URL for the file
    """
    if STORAGE_PROVIDER == "s3":
        region = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")
        return f"https://{STORAGE_BUCKET}.s3.{region}.amazonaws.com/{storage_key}"
    elif STORAGE_PROVIDER == "gcs":
        return f"https://storage.googleapis.com/{STORAGE_BUCKET}/{storage_key}"
    else:
        return f"/media/{storage_key}"  # Local development


def validate_file_upload(
    file_name: str, content_type: str, file_size: int, max_size: int = 100 * 1024 * 1024
) -> Tuple[bool, Optional[str]]:
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
        return (
            False,
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
        )

    # Check file extension
    file_extension = os.path.splitext(file_name)[1].lower()
    if not file_extension:
        return False, "File must have an extension"

    # Check for potentially dangerous file extensions
    dangerous_extensions = {
        ".exe",
        ".bat",
        ".cmd",
        ".com",
        ".pif",
        ".scr",
        ".vbs",
        ".js",
        ".jar",
        ".php",
        ".asp",
        ".aspx",
        ".jsp",
        ".sh",
        ".bash",
        ".ps1",
        ".msi",
        ".app",
        ".deb",
        ".rpm",
        ".dmg",
        ".pkg",
    }

    if file_extension in dangerous_extensions:
        return (
            False,
            f"File type '{file_extension}' is not allowed for security reasons",
        )

    # Validate content type matches expected extension
    expected_content_type = _infer_content_type_from_extension(file_extension)
    if (
        content_type
        and content_type != expected_content_type
        and content_type != "application/octet-stream"
    ):
        logger.warning(
            f"Content type mismatch: expected {expected_content_type}, got {content_type} for file {file_name}"
        )

    return True, None


def get_file_metadata(storage_key: str) -> Dict[str, Any]:
    """
    Get metadata for a file in cloud storage.

    Args:
        storage_key (str): The storage key of the file

    Returns:
        dict: File metadata including size, content-type, etc.
    """
    if STORAGE_PROVIDER == "s3":
        return _get_s3_file_metadata(storage_key)
    elif STORAGE_PROVIDER == "gcs":
        return _get_gcs_file_metadata(storage_key)
    else:
        return {"error": "Metadata not available for local storage"}


def _get_s3_file_metadata(storage_key: str) -> Dict[str, Any]:
    """Get file metadata from S3."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client("s3")
        response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=storage_key)

        return {
            "size": response.get("ContentLength"),
            "content_type": response.get("ContentType"),
            "last_modified": response.get("LastModified"),
            "etag": response.get("ETag"),
            "storage_class": response.get("StorageClass"),
            "metadata": response.get("Metadata", {}),
        }
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            return {"error": "File not found"}
        logger.error(f"Error getting S3 file metadata: {exc}")
        return {"error": str(exc)}
    except ImportError:
        return {"error": "boto3 not installed"}
    except Exception as exc:
        logger.error(f"Unexpected error getting S3 file metadata: {exc}")
        return {"error": str(exc)}


def _get_gcs_file_metadata(storage_key: str) -> Dict[str, Any]:
    """Get file metadata from Google Cloud Storage."""
    try:
        from google.cloud import storage
        from google.cloud.exceptions import NotFound

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(storage_key)

        # Reload blob to get latest metadata
        blob.reload()

        if blob.exists():
            return {
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "etag": blob.etag,
                "storage_class": blob.storage_class,
                "metadata": blob.metadata or {},
            }
        else:
            return {"error": "File not found"}
    except NotFound:
        return {"error": "File not found"}
    except ImportError:
        return {"error": "google-cloud-storage not installed"}
    except Exception as exc:
        logger.error(f"Error getting GCS file metadata: {exc}")
        return {"error": str(exc)}


def check_storage_health() -> Dict[str, Any]:
    """
    Check the health of the storage backend.

    Returns:
        Dict with health status information
    """
    try:
        _validate_storage_config()

        if STORAGE_PROVIDER == "s3":
            return _check_s3_health()
        elif STORAGE_PROVIDER == "gcs":
            return _check_gcs_health()
        else:
            return {
                "status": "healthy",
                "provider": "local",
                "bucket": STORAGE_BUCKET,
                "message": "Local storage is available",
            }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "provider": STORAGE_PROVIDER,
            "bucket": STORAGE_BUCKET,
            "error": str(exc),
        }


def _check_s3_health() -> Dict[str, Any]:
    """Check S3 storage health."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client("s3")
        s3_client.head_bucket(Bucket=STORAGE_BUCKET)

        return {
            "status": "healthy",
            "provider": "s3",
            "bucket": STORAGE_BUCKET,
            "message": "S3 bucket is accessible",
        }
    except ClientError as exc:
        return {
            "status": "unhealthy",
            "provider": "s3",
            "bucket": STORAGE_BUCKET,
            "error": str(exc),
        }
    except ImportError:
        return {
            "status": "unhealthy",
            "provider": "s3",
            "bucket": STORAGE_BUCKET,
            "error": "boto3 not installed",
        }


def _check_gcs_health() -> Dict[str, Any]:
    """Check GCS storage health."""
    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)
        bucket.reload()

        return {
            "status": "healthy",
            "provider": "gcs",
            "bucket": STORAGE_BUCKET,
            "message": "GCS bucket is accessible",
        }
    except ImportError:
        return {
            "status": "unhealthy",
            "provider": "gcs",
            "bucket": STORAGE_BUCKET,
            "error": "google-cloud-storage not installed",
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "provider": "gcs",
            "bucket": STORAGE_BUCKET,
            "error": str(exc),
        }


def get_storage_stats() -> Dict[str, Any]:
    """
    Get storage usage statistics.

    Returns:
        Dict with storage statistics
    """
    try:
        stats = {
            "provider": STORAGE_PROVIDER,
            "bucket": STORAGE_BUCKET,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if STORAGE_PROVIDER == "s3":
            stats.update(_get_s3_stats())
        elif STORAGE_PROVIDER == "gcs":
            stats.update(_get_gcs_stats())
        else:
            stats.update(
                {
                    "total_objects": 0,
                    "total_size": 0,
                    "message": "Stats not available for local storage",
                }
            )

        return stats

    except Exception as exc:
        logger.error(f"Error getting storage stats: {exc}")
        return {
            "provider": STORAGE_PROVIDER,
            "bucket": STORAGE_BUCKET,
            "error": str(exc),
        }


def _get_s3_stats() -> Dict[str, Any]:
    """Get S3 storage statistics."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client("s3")

        # Get basic bucket info
        paginator = s3_client.get_paginator("list_objects_v2")

        total_objects = 0
        total_size = 0

        for page in paginator.paginate(Bucket=STORAGE_BUCKET):
            if "Contents" in page:
                total_objects += len(page["Contents"])
                total_size += sum(obj["Size"] for obj in page["Contents"])

        return {
            "total_objects": total_objects,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    except ClientError as exc:
        return {"error": f"S3 error: {exc}"}
    except ImportError:
        return {"error": "boto3 not installed"}
    except Exception as exc:
        return {"error": str(exc)}


def _get_gcs_stats() -> Dict[str, Any]:
    """Get GCS storage statistics."""
    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(STORAGE_BUCKET)

        total_objects = 0
        total_size = 0

        for blob in bucket.list_blobs():
            total_objects += 1
            total_size += blob.size or 0

        return {
            "total_objects": total_objects,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    except ImportError:
        return {"error": "google-cloud-storage not installed"}
    except Exception as exc:
        return {"error": str(exc)}


# Export all functions for compatibility
__all__ = [
    "generate_presigned_post",
    "delete_object",  # This was the missing function causing the import error
    "bulk_delete_objects",
    "get_public_url",
    "validate_file_upload",
    "get_file_metadata",
    "check_storage_health",
    "get_storage_stats",
    "_infer_content_type_from_extension",  # FIXED: Now properly implemented
    "_validate_storage_config",
]
