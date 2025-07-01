# File Path: instructor_portal/models/drafts.py
# Folder Path: instructor_portal/models/
# Date Created: 2025-06-26 13:09:54
# Date Revised: 2025-06-27 03:27:18
# Author: softTechSolutions2001
# Version: 1.0.1
#
# Draft content models - File drafts and content management
# Split from original models.py maintaining exact code compatibility

import logging
import hashlib
import os
import uuid
from typing import Dict, Any, List, Optional

from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from .utils import TierManager

logger = logging.getLogger(__name__)


class DraftCourseContent(models.Model):
    """
    Temporary storage for course content during creation process
    ENHANCED: Versioning support for AI iteration and content refinement
    """

    class ContentType(models.TextChoices):
        COURSE_INFO = 'course_info', _('Course Information')
        MODULE = 'module', _('Module Content')
        LESSON = 'lesson', _('Lesson Content')
        ASSESSMENT = 'assessment', _('Assessment Content')
        RESOURCE = 'resource', _('Resource/Material')

    session = models.ForeignKey(
        'CourseCreationSession',
        on_delete=models.CASCADE,
        related_name='draft_content',
        verbose_name=_('Creation Session')
    )

    content_type = models.CharField(
        max_length=30,
        choices=ContentType.choices,
        verbose_name=_('Content Type')
    )

    content_id = models.CharField(
        max_length=50,
        verbose_name=_('Content Identifier'),
        help_text=_('Unique identifier for this content piece')
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Content Version'),
        help_text=_('Version number for AI iteration support')
    )

    # Content Data
    content_data = models.JSONField(
        verbose_name=_('Content Data'),
        help_text=_('JSON structure containing the actual content')
    )

    # Content Metadata
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Content Title')
    )

    order = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Display Order')
    )

    # Status and Validation
    is_complete = models.BooleanField(
        default=False,
        verbose_name=_('Is Complete'),
        help_text=_('Whether this content piece is ready for publication')
    )

    validation_errors = models.JSONField(
        default=list,
        verbose_name=_('Validation Errors'),
        help_text=_('List of validation errors for this content')
    )

    # Auto-save tracking
    auto_save_version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Auto-save Version'),
        help_text=_('Internal version for auto-save functionality')
    )

    last_saved = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Saved')
    )

    # AI generation metadata
    ai_generated = models.BooleanField(
        default=False,
        verbose_name=_('AI Generated'),
        help_text=_('Whether this content was generated using AI')
    )

    ai_prompt = models.TextField(
        blank=True,
        verbose_name=_('AI Prompt'),
        help_text=_('Original AI prompt used to generate this content')
    )

    class Meta:
        verbose_name = _('Draft Course Content')
        verbose_name_plural = _('Draft Course Contents')
        unique_together = [['session', 'content_type', 'content_id', 'version']]
        ordering = ['order', 'version']
        indexes = [
            models.Index(fields=['session', 'content_type']),
            models.Index(fields=['session', 'order']),
            models.Index(fields=['session', 'content_type', 'version']),
            models.Index(fields=['is_complete', 'last_saved']),
        ]

    def __str__(self):
        return f"{self.session.session_id} - {self.get_content_type_display()}: {self.title} (v{self.version})"

    def create_new_version(self) -> 'DraftCourseContent':
        """Create a new version of this content for AI iteration"""
        try:
            # Get the latest version number
            latest_version = DraftCourseContent.objects.filter(
                session=self.session,
                content_type=self.content_type,
                content_id=self.content_id
            ).aggregate(max_version=models.Max('version'))['max_version'] or 0

            # Create new version
            new_version = DraftCourseContent.objects.create(
                session=self.session,
                content_type=self.content_type,
                content_id=self.content_id,
                version=latest_version + 1,
                content_data=self.content_data.copy(),
                title=self.title,
                order=self.order,
                is_complete=False,  # New version starts as incomplete
                auto_save_version=1,  # Reset auto-save version
                ai_generated=self.ai_generated,
                ai_prompt=self.ai_prompt
            )

            logger.info(f"Created new version {new_version.version} for content {self.content_id}")
            return new_version

        except Exception as e:
            logger.error(f"Error creating new version: {e}")
            raise

    def validate_content(self) -> List[str]:
        """Validate content and return list of errors"""
        errors = []

        try:
            # Basic validation based on content type
            if self.content_type == self.ContentType.COURSE_INFO:
                if not self.content_data.get('title'):
                    errors.append("Course title is required")
                if not self.content_data.get('description'):
                    errors.append("Course description is required")
                if not self.content_data.get('category_id'):
                    errors.append("Course category is required")

            elif self.content_type == self.ContentType.MODULE:
                if not self.title:
                    errors.append("Module title is required")
                if not self.content_data.get('description'):
                    errors.append("Module description is recommended")

            elif self.content_type == self.ContentType.LESSON:
                if not self.title:
                    errors.append("Lesson title is required")
                if not self.content_data.get('content') and not self.content_data.get('video_url'):
                    errors.append("Lesson must have content or video")

                # Duration validation
                duration = self.content_data.get('duration_minutes', 0)
                if duration < 1:
                    errors.append("Lesson duration must be at least 1 minute")

            elif self.content_type == self.ContentType.ASSESSMENT:
                if not self.content_data.get('questions'):
                    errors.append("Assessment must have at least one question")

                questions = self.content_data.get('questions', [])
                for i, question in enumerate(questions):
                    if not question.get('question_text'):
                        errors.append(f"Question {i+1} text is required")
                    if not question.get('options') or len(question.get('options', [])) < 2:
                        errors.append(f"Question {i+1} must have at least 2 options")

            elif self.content_type == self.ContentType.RESOURCE:
                if not self.content_data.get('resource_type'):
                    errors.append("Resource type is required")
                if not self.content_data.get('resource_url') and not self.content_data.get('file_path'):
                    errors.append("Resource must have a URL or file attachment")

            # Update validation errors in the model
            if errors != self.validation_errors:
                self.validation_errors = errors
                self.save(update_fields=['validation_errors'])

            return errors

        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return [f"Validation error: {str(e)}"]

    def mark_complete(self) -> bool:
        """Mark content as complete after validation"""
        try:
            errors = self.validate_content()
            if not errors:
                self.is_complete = True
                self.save(update_fields=['is_complete'])
                logger.info(f"Marked content {self.content_id} as complete")
                return True
            else:
                logger.warning(f"Cannot mark content {self.content_id} as complete due to validation errors: {errors}")
                return False
        except Exception as e:
            logger.error(f"Error marking content as complete: {e}")
            return False


class CourseContentDraft(models.Model):
    """
    Enhanced content management for course creation with file support
    ENHANCED: Complete file upload, processing, and versioning system
    """

    session = models.ForeignKey(
        'CourseCreationSession',
        on_delete=models.CASCADE,
        related_name='content_drafts',
        verbose_name=_('Creation Session')
    )

    content_type = models.CharField(
        max_length=30,
        choices=DraftCourseContent.ContentType.choices,
        verbose_name=_('Content Type')
    )

    # File handling with sharded paths
    file_path = models.FileField(
        upload_to='course_drafts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Content File')
    )

    # Content versioning and integrity
    content_hash = models.CharField(
        max_length=64,
        verbose_name=_('Content Hash'),
        help_text=_('SHA-256 hash for content deduplication and integrity')
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Content Version')
    )

    # Processing status
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_('Is Processed'),
        help_text=_('Whether file has been processed and validated')
    )

    processing_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', _('Pending Processing')),
            ('processing', _('Processing')),
            ('completed', _('Processing Completed')),
            ('failed', _('Processing Failed')),
            ('virus_scan', _('Virus Scanning')),
            ('format_conversion', _('Format Conversion'))
        ],
        default='pending',
        verbose_name=_('Processing Status')
    )

    processing_error = models.TextField(
        blank=True,
        verbose_name=_('Processing Error'),
        help_text=_('Error message if processing failed')
    )

    # File metadata
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('File Size (bytes)')
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('MIME Type')
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Original Filename')
    )

    # Processing metadata
    processing_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Processing Metadata'),
        help_text=_('Additional metadata from processing (dimensions, duration, etc.)')
    )

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date')
    )

    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processed Date')
    )

    class Meta:
        verbose_name = _('Course Content Draft')
        verbose_name_plural = _('Course Content Drafts')
        unique_together = [['session', 'content_type', 'version']]
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['session', 'processing_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['is_processed', 'created_date']),
            models.Index(fields=['processing_status', 'created_date']),
        ]

    def __str__(self):
        return f"Content Draft - {self.session.session_id} ({self.get_content_type_display()} v{self.version})"

    def save(self, *args, **kwargs):
        """Enhanced save with content hash generation and metadata extraction"""
        if self.file_path and not self.content_hash:
            try:
                # Generate hash from file content
                with default_storage.open(self.file_path.name, 'rb') as f:
                    file_content = f.read()
                    self.content_hash = hashlib.sha256(file_content).hexdigest()

                # Extract file metadata
                self.file_size = self.file_path.size
                self.original_filename = os.path.basename(self.file_path.name)

                # Determine MIME type
                import mimetypes
                file_ext = os.path.splitext(self.file_path.name)[1].lower()
                self.mime_type = mimetypes.types_map.get(file_ext, 'application/octet-stream')

            except Exception as e:
                logger.error(f"Error generating file metadata: {e}")
                # FIX: Use uuid.uuid4().hex which is guaranteed to be 32 chars
                self.content_hash = f"error-{uuid.uuid4().hex[:8]}"

        super().save(*args, **kwargs)

    def process_file(self) -> bool:
        """Process uploaded file with comprehensive validation and metadata extraction"""
        if not self.file_path:
            self.processing_status = 'failed'
            self.processing_error = 'No file to process'
            self.save(update_fields=['processing_status', 'processing_error'])
            return False

        try:
            self.processing_status = 'processing'
            self.save(update_fields=['processing_status'])

            # Check file size limits based on instructor tier
            if self.file_size and self.session.instructor:
                tier = self.session.instructor.tier
                if not TierManager.check_file_size_limit(tier, self.file_size):
                    self.processing_status = 'failed'
                    self.processing_error = f'File size exceeds tier limit for {tier} instructors'
                    self.save(update_fields=['processing_status', 'processing_error'])
                    return False

            # Check file type permissions
            if self.session.instructor:
                tier = self.session.instructor.tier
                file_ext = os.path.splitext(self.original_filename)[1].lower().lstrip('.')
                if not TierManager.is_file_type_allowed(tier, file_ext):
                    self.processing_status = 'failed'
                    self.processing_error = f'File type .{file_ext} not allowed for {tier} instructors'
                    self.save(update_fields=['processing_status', 'processing_error'])
                    return False

            # Extract content-specific metadata
            metadata = {}

            if self.mime_type.startswith('image/'):
                metadata.update(self._extract_image_metadata())
            elif self.mime_type.startswith('video/'):
                metadata.update(self._extract_video_metadata())
            elif self.mime_type.startswith('audio/'):
                metadata.update(self._extract_audio_metadata())
            elif self.mime_type == 'application/pdf':
                metadata.update(self._extract_pdf_metadata())

            self.processing_metadata = metadata

            # Mark as processed
            self.is_processed = True
            self.processing_status = 'completed'
            self.processed_date = timezone.now()
            self.save(update_fields=[
                'is_processed', 'processing_status', 'processed_date', 'processing_metadata'
            ])

            logger.info(f"Successfully processed file {self.original_filename}")
            return True

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            self.processing_status = 'failed'
            self.processing_error = str(e)
            self.save(update_fields=['processing_status', 'processing_error'])
            return False

    def _extract_image_metadata(self) -> Dict[str, Any]:
        """Extract metadata from image files"""
        metadata = {}
        try:
            from PIL import Image
            with default_storage.open(self.file_path.name, 'rb') as f:
                with Image.open(f) as img:
                    metadata.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format,
                        'mode': img.mode
                    })
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_video_metadata(self) -> Dict[str, Any]:
        """Extract metadata from video files"""
        metadata = {}
        try:
            # Placeholder for video metadata extraction
            # You would integrate with libraries like ffmpeg-python here
            metadata.update({
                'extracted': False,
                'note': 'Video metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_audio_metadata(self) -> Dict[str, Any]:
        """Extract metadata from audio files"""
        metadata = {}
        try:
            # Placeholder for audio metadata extraction
            # You would integrate with libraries like mutagen here
            metadata.update({
                'extracted': False,
                'note': 'Audio metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def _extract_pdf_metadata(self) -> Dict[str, Any]:
        """Extract metadata from PDF files"""
        metadata = {}
        try:
            # Placeholder for PDF metadata extraction
            # You would integrate with libraries like PyPDF2 or pdfplumber here
            metadata.update({
                'extracted': False,
                'note': 'PDF metadata extraction not implemented'
            })
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def get_download_url(self) -> Optional[str]:
        """Get secure download URL for the file"""
        try:
            if self.file_path and self.is_processed:
                return default_storage.url(self.file_path.name)
            return None
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            return None

    def delete_file(self) -> bool:
        """Safely delete the associated file"""
        try:
            if self.file_path and default_storage.exists(self.file_path.name):
                default_storage.delete(self.file_path.name)
                logger.info(f"Deleted file {self.file_path.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


# Signal handlers for file cleanup
@receiver(pre_delete, sender=CourseContentDraft)
def cleanup_file_on_delete(sender, instance, **kwargs):
    """Clean up file when CourseContentDraft is deleted"""
    try:
        instance.delete_file()
    except Exception as e:
        logger.error(f"Error cleaning up file on delete: {e}")


@receiver(post_save, sender=CourseContentDraft)
def process_content_draft_file(sender, instance, created, **kwargs):
    """Process newly uploaded content draft files"""
    try:
        # Only process newly created unprocessed files
        if created and instance.file_path and not instance.is_processed:
            instance.processing_status = 'processing'
            instance.save(update_fields=['processing_status'])

            try:
                # Process directly (in production, use async task queue)
                success = instance.process_file()
                if not success:
                    logger.warning(f"Failed to process file for content draft {instance.id}")
            except Exception as e:
                logger.error(f"Error processing content draft file: {e}")
                instance.processing_status = 'failed'
                instance.processing_error = str(e)
                instance.save(update_fields=['processing_status', 'processing_error'])

    except Exception as e:
        logger.error(f"Error handling content draft creation: {e}")
