/**
 * File: frontend/src/courseBuilder/components/ResourceChip.tsx
 * Version: 2.1.0
 * Date Created: 2025-06-14 15:49:14
 * Date Revised: 2025-06-14 15:49:14 UTC
 * Current User: sujibeautysalon
 * Last Modified By: sujibeautysalon
 *
 * Enhanced ResourceChip Component with Performance and Accessibility Optimizations
 *
 * This component represents a single resource within a lesson with comprehensive
 * error handling, accessibility features, and performance optimizations.
 *
 * Key Features:
 * - Controlled input components eliminating React warnings
 * - Performance optimizations with React.memo and useCallback
 * - Enhanced accessibility with proper ARIA attributes
 * - Comprehensive error handling with user feedback
 * - File upload with progress tracking and error recovery
 * - Premium resource management with visual indicators
 * - Keyboard navigation support for all interactions
 *
 * Version 2.1.0 Changes (Surgical Fixes from Code Review):
 * - FIXED: React warnings from uncontrolled components
 * - FIXED: Performance optimizations with React.memo and proper memoization
 * - FIXED: Enhanced accessibility with ARIA attributes and keyboard support
 * - FIXED: State management with immutable operations
 * - FIXED: Added comprehensive error handling and user feedback
 * - FIXED: Memory leak prevention with proper cleanup
 * - FIXED: Enhanced file upload with proper progress tracking
 * - FIXED: Improved UX with loading states and visual feedback
 *
 * Connected Files:
 * - frontend/src/courseBuilder/components/LessonCard.tsx - Parent lesson component
 * - frontend/src/services/instructorService.ts - File upload service
 * - frontend/src/courseBuilder/store/courseSlice.ts - State management
 * - frontend/src/courseBuilder/store/schema.ts - Type definitions
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import instructorService from '../../services/instructorService';
import { useCourseStore } from '../store/courseSlice';
import { Resource } from '../store/schema';

// ✅ FIX 1: Enhanced interface with better typing
interface ResourceChipProps {
  resource: Resource;
  moduleId: string | number;
  lessonId: string | number;
  readOnly?: boolean;
  showPremiumToggle?: boolean;
  maxUploadSize?: number;
  onError?: (error: Error) => void;
  className?: string;
  'data-testid'?: string;
}

// ✅ FIX 2: Enhanced upload state with better typing
interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  phase: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
}

// ✅ FIX 3: Resource type configuration for better maintainability
const RESOURCE_TYPES = {
  document: {
    accept: '.pdf,.doc,.docx,.txt,.rtf,.odt',
    icon: 'document',
    label: 'Document',
  },
  pdf: {
    accept: '.pdf',
    icon: 'document',
    label: 'PDF Document',
  },
  video: {
    accept: 'video/*,.mp4,.avi,.mov,.wmv,.flv,.webm',
    icon: 'video',
    label: 'Video',
  },
  image: {
    accept: 'image/*,.jpg,.jpeg,.png,.gif,.bmp,.svg,.webp',
    icon: 'image',
    label: 'Image',
  },
  code: {
    accept: '.js,.ts,.jsx,.tsx,.html,.css,.scss,.json,.xml,.yaml,.yml,.py,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift',
    icon: 'code',
    label: 'Code',
  },
  link: {
    accept: undefined,
    icon: 'link',
    label: 'Link',
  },
} as const;

const DEFAULT_MAX_UPLOAD_SIZE = 9 * 1024 * 1024; // 9MB

/**
 * Enhanced ResourceChip component with comprehensive fixes and optimizations
 * Represents a single resource within a lesson with robust error handling
 */
const ResourceChip: React.FC<ResourceChipProps> = React.memo(({
  resource,
  moduleId,
  lessonId,
  readOnly = false,
  showPremiumToggle = true,
  maxUploadSize = DEFAULT_MAX_UPLOAD_SIZE,
  onError,
  className = '',
  'data-testid': testId = 'resource-chip',
}) => {
  // ✅ FIX 4: Enhanced state management with proper typing
  const { updateResource, deleteResource } = useCourseStore();
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    phase: 'idle',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [resourceName, setResourceName] = useState(resource.name || resource.title || '');
  const [isDeleting, setIsDeleting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // ✅ FIX 5: Refs for cleanup and focus management
  const fileInputRef = useRef<HTMLInputElement>(null);
  const resourceChipRef = useRef<HTMLDivElement>(null);
  const nameInputRef = useRef<HTMLInputElement>(null);
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ✅ FIX 6: Sync local state with resource prop changes
  useEffect(() => {
    setResourceName(resource.name || resource.title || '');
  }, [resource.name, resource.title]);

  // ✅ FIX 7: Enhanced error handling with user feedback
  const handleError = useCallback((error: Error, context: string) => {
    console.error(`ResourceChip error in ${context}:`, error);
    setLocalError(error.message);

    // Clear error after 5 seconds
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
    }
    errorTimeoutRef.current = setTimeout(() => {
      setLocalError(null);
    }, 5000);

    if (onError) {
      onError(error);
    }
  }, [onError]);

  // ✅ FIX 8: Cleanup effect for timeouts
  useEffect(() => {
    return () => {
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
    };
  }, []);

  // ✅ FIX 9: Memoized resource type configuration
  const resourceTypeConfig = useMemo(() => {
    return RESOURCE_TYPES[resource.type as keyof typeof RESOURCE_TYPES] || RESOURCE_TYPES.document;
  }, [resource.type]);

  // ✅ FIX 10: Enhanced resource icon component with proper typing
  const ResourceIcon = useMemo(() => {
    const iconClass = 'w-4 h-4 flex-shrink-0';
    const iconProps = {
      className: iconClass,
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24',
      strokeWidth: 2,
      strokeLinecap: 'round' as const,
      strokeLinejoin: 'round' as const,
    };

    switch (resourceTypeConfig.icon) {
      case 'document':
        return (
          <svg {...iconProps} fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'video':
        return (
          <svg {...iconProps}>
            <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        );
      case 'image':
        return (
          <svg {...iconProps} fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'code':
        return (
          <svg {...iconProps}>
            <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        );
      case 'link':
        return (
          <svg {...iconProps}>
            <path d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
        );
      default:
        return (
          <svg {...iconProps}>
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
    }
  }, [resourceTypeConfig.icon]);

  // ✅ FIX 11: Enhanced file upload with comprehensive error handling
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (readOnly) return;

    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > maxUploadSize) {
      const sizeMB = Math.round(maxUploadSize / (1024 * 1024));
      handleError(new Error(`File size exceeds ${sizeMB}MB limit`), 'handleFileUpload');
      return;
    }

    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      phase: 'uploading',
    });
    setLocalError(null);

    try {
      let uploadedResource;

      if (file.size <= maxUploadSize && resource.type !== 'video') {
        // Direct upload for smaller files (except videos)
        setUploadState(prev => ({ ...prev, phase: 'uploading' }));

        uploadedResource = await instructorService.uploadResource(
          {
            file: file,
            title: resourceName || file.name,
            premium: resource.premium || false,
          },
          {
            onProgress: (progress) => {
              setUploadState(prev => ({
                ...prev,
                progress: Math.round(progress.percentCompleted),
              }));
            },
          }
        );
      } else {
        // Presigned URL upload for larger files or videos
        setUploadState(prev => ({ ...prev, phase: 'processing' }));

        const presignedData = await instructorService.getPresignedUrl({
          fileName: file.name,
          contentType: file.type,
        });

        setUploadState(prev => ({ ...prev, phase: 'uploading' }));

        await instructorService.uploadToPresignedUrl(presignedData.url, file, {
          onProgress: (progress) => {
            setUploadState(prev => ({
              ...prev,
              progress: Math.round(progress.percentCompleted),
            }));
          },
        });

        setUploadState(prev => ({ ...prev, phase: 'processing' }));

        uploadedResource = await instructorService.confirmResourceUpload({
          resourceId: resource.id,
          storageKey: presignedData.storage_key,
          filesize: file.size,
          mimeType: file.type,
          premium: resource.premium || false,
        });
      }

      // Update the resource with new data
      await updateResource(moduleId, lessonId, resource.id, {
        url: uploadedResource.url,
        name: uploadedResource.name || resourceName || file.name,
        title: uploadedResource.name || resourceName || file.name,
        type: uploadedResource.type || resource.type,
        storageKey: uploadedResource.storage_key,
        filesize: file.size,
        mimeType: file.type,
        uploaded: true,
      });

      setUploadState({
        isUploading: false,
        progress: 100,
        error: null,
        phase: 'complete',
      });

      toast.success('Resource uploaded successfully!');

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Reset to idle after showing success
      setTimeout(() => {
        setUploadState(prev => ({ ...prev, phase: 'idle', progress: 0 }));
      }, 2000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.';
      setUploadState({
        isUploading: false,
        progress: 0,
        error: errorMessage,
        phase: 'error',
      });
      handleError(error instanceof Error ? error : new Error(errorMessage), 'handleFileUpload');
    }
  }, [
    readOnly,
    maxUploadSize,
    resource.type,
    resource.id,
    resource.premium,
    resourceName,
    moduleId,
    lessonId,
    updateResource,
    handleError,
  ]);

  // ✅ FIX 12: Controlled input handler with validation
  const handleNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (readOnly) return;

    const newName = e.target.value;
    if (newName.length <= 100) { // Validate max length
      setResourceName(newName);
      setLocalError(null);
    } else {
      setLocalError('Resource name cannot exceed 100 characters');
    }
  }, [readOnly]);

  // ✅ FIX 13: Enhanced save name handler
  const handleSaveName = useCallback(async () => {
    if (readOnly || !resourceName.trim()) {
      if (!resourceName.trim()) {
        setLocalError('Resource name cannot be empty');
        return;
      }
      return;
    }

    const newName = resourceName.trim();
    if (newName === (resource.name || resource.title)) {
      setIsEditing(false);
      return;
    }

    try {
      await updateResource(moduleId, lessonId, resource.id, {
        name: newName,
        title: newName,
      });
      setIsEditing(false);
      setLocalError(null);
      toast.success('Resource name updated successfully');
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to update resource name'), 'handleSaveName');
    }
  }, [readOnly, resourceName, resource.name, resource.title, resource.id, moduleId, lessonId, updateResource, handleError]);

  // ✅ FIX 14: Enhanced delete handler with loading state
  const handleDelete = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (readOnly || isDeleting) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete the resource "${resource.name || resource.title}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteResource(moduleId, lessonId, resource.id);
      toast.success('Resource deleted successfully');
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to delete resource'), 'handleDelete');
    } finally {
      setIsDeleting(false);
    }
  }, [readOnly, isDeleting, resource.name, resource.title, moduleId, lessonId, resource.id, deleteResource, handleError]);

  // ✅ FIX 15: Enhanced premium toggle handler
  const handleTogglePremium = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (readOnly) return;

    try {
      await updateResource(moduleId, lessonId, resource.id, {
        premium: !resource.premium,
      });
      toast.success(`Resource ${resource.premium ? 'removed from' : 'marked as'} premium`);
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to update premium status'), 'handleTogglePremium');
    }
  }, [readOnly, moduleId, lessonId, resource.id, resource.premium, updateResource, handleError]);

  // ✅ FIX 16: Enhanced resource access handler
  const handleAccess = useCallback((e?: React.MouseEvent) => {
    if (e) e.stopPropagation();

    if (resource.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    } else {
      toast.info('Resource URL not available');
    }
  }, [resource.url]);

  // ✅ FIX 17: Enhanced upload click handler
  const handleUploadClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (!readOnly && !uploadState.isUploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [readOnly, uploadState.isUploading]);

  // ✅ FIX 18: Enhanced editing handlers
  const handleStartEditing = useCallback((e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (readOnly || uploadState.isUploading) return;

    setIsEditing(true);
    setLocalError(null);

    // Focus the input after state update
    setTimeout(() => {
      nameInputRef.current?.focus();
    }, 0);
  }, [readOnly, uploadState.isUploading]);

  const handleCancelEditing = useCallback(() => {
    setIsEditing(false);
    setResourceName(resource.name || resource.title || '');
    setLocalError(null);
  }, [resource.name, resource.title]);

  // ✅ FIX 19: Enhanced keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (readOnly) return;

    switch (e.key) {
      case 'Enter':
        if (isEditing) {
          handleSaveName();
        } else {
          handleAccess();
        }
        break;
      case 'Escape':
        if (isEditing) {
          handleCancelEditing();
        }
        break;
      case ' ':
        if (!isEditing) {
          e.preventDefault();
          handleStartEditing();
        }
        break;
    }
  }, [readOnly, isEditing, handleSaveName, handleAccess, handleCancelEditing, handleStartEditing]);

  // ✅ FIX 20: Memoized computed values for performance
  const containerClasses = useMemo(() => {
    const baseClasses = [
      'inline-flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 border relative',
      className,
    ];

    if (localError || uploadState.error) {
      baseClasses.push('bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200');
    } else if (resource.premium && showPremiumToggle) {
      baseClasses.push('bg-purple-50 border-purple-200 text-purple-800 dark:bg-purple-900/20 dark:border-purple-700 dark:text-purple-200');
    } else {
      baseClasses.push('bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700');
    }

    if (readOnly) {
      baseClasses.push('opacity-75');
    }

    if (uploadState.isUploading || isDeleting) {
      baseClasses.push('opacity-75');
    }

    return baseClasses.filter(Boolean).join(' ');
  }, [className, localError, uploadState.error, resource.premium, showPremiumToggle, readOnly, uploadState.isUploading, isDeleting]);

  const displayName = resource.name || resource.title || 'Untitled Resource';
  const resourceAriaLabel = `${resourceTypeConfig.label} resource: ${displayName}${resource.premium ? ' (Premium)' : ''}`;

  return (
    <div
      ref={resourceChipRef}
      className={containerClasses}
      role="listitem"
      tabIndex={readOnly ? -1 : 0}
      onKeyDown={handleKeyDown}
      aria-label={resourceAriaLabel}
      data-testid={testId}
    >
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileUpload}
        accept={resourceTypeConfig.accept}
        data-testid="file-input"
        disabled={readOnly || uploadState.isUploading}
        aria-label={`Upload ${resourceTypeConfig.label.toLowerCase()}`}
      />

      {/* Resource type icon */}
      <div className="text-current" title={resourceTypeConfig.label}>
        {ResourceIcon}
      </div>

      {/* Resource name section */}
      <div className="flex-1 min-w-0">
        {isEditing && !readOnly ? (
          <input
            ref={nameInputRef}
            type="text"
            className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-500 rounded px-2 py-1 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={resourceName}
            onChange={handleNameChange}
            onBlur={handleSaveName}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSaveName();
              } else if (e.key === 'Escape') {
                handleCancelEditing();
              }
            }}
            placeholder="Enter resource name"
            maxLength={100}
            data-testid="resource-name-input"
            aria-label="Resource name"
          />
        ) : (
          <span
            className={`text-sm truncate max-w-32 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 ${readOnly ? 'cursor-default hover:text-current' : ''}`}
            onClick={handleStartEditing}
            title={displayName}
            data-testid="resource-name"
          >
            {displayName}
          </span>
        )}
      </div>

      {/* Upload progress section */}
      {uploadState.isUploading && (
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-16 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300 rounded-full"
              style={{ width: `${uploadState.progress}%` }}
            />
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400 min-w-[2rem]">
            {uploadState.progress}%
          </span>
        </div>
      )}

      {/* Status indicators */}
      <div className="flex items-center gap-1 flex-shrink-0">
        {/* Upload success indicator */}
        {uploadState.phase === 'complete' && (
          <span className="text-green-500" title="Upload complete">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </span>
        )}

        {/* Upload processing indicator */}
        {uploadState.phase === 'processing' && (
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" title="Processing..." />
        )}

        {/* Error indicator */}
        {(uploadState.error || localError) && (
          <span className="text-red-500" title={uploadState.error || localError || 'Error occurred'}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
        )}

        {/* Uploaded indicator */}
        {(resource.uploaded || resource.url) && !uploadState.isUploading && !uploadState.error && !localError && (
          <span className="text-green-500" title="Resource available">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
        )}
      </div>

      {/* Action buttons */}
      {!readOnly && (
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Access/Download button */}
          {resource.url && (
            <button
              onClick={handleAccess}
              className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded p-1 transition-colors"
              aria-label="Open resource"
              data-testid="access-resource-btn"
              title="Open resource"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          )}

          {/* Upload/Replace button */}
          <button
            onClick={handleUploadClick}
            className={`text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded p-1 transition-colors ${uploadState.isUploading ? 'cursor-not-allowed opacity-50' : ''}`}
            aria-label={resource.url ? 'Replace resource' : 'Upload resource'}
            data-testid="upload-resource-btn"
            disabled={uploadState.isUploading}
            title={resource.url ? 'Replace resource' : 'Upload resource'}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </button>

          {/* Premium toggle button */}
          {showPremiumToggle && (
            <button
              onClick={handleTogglePremium}
              className={`focus:outline-none focus:ring-2 focus:ring-purple-500 rounded p-1 transition-colors ${resource.premium ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400'}`}
              aria-label={resource.premium ? 'Remove premium status' : 'Mark as premium'}
              data-testid="premium-toggle-btn"
              title={resource.premium ? 'Premium resource - click to remove' : 'Mark as premium'}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </button>
          )}

          {/* Edit name button */}
          {!isEditing && (
            <button
              onClick={handleStartEditing}
              className="text-gray-500 hover:text-yellow-600 dark:text-gray-400 dark:hover:text-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 rounded p-1 transition-colors"
              aria-label="Edit resource name"
              data-testid="edit-resource-btn"
              title="Edit resource name"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
          )}

          {/* Delete button */}
          <button
            onClick={handleDelete}
            className={`text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 focus:outline-none focus:ring-2 focus:ring-red-500 rounded p-1 transition-colors ${isDeleting ? 'cursor-not-allowed opacity-50' : ''}`}
            aria-label="Delete resource"
            data-testid="delete-resource-btn"
            disabled={isDeleting}
            title="Delete resource"
          >
            {isDeleting ? (
              <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            )}
          </button>
        </div>
      )}

      {/* Error message tooltip */}
      {(uploadState.error || localError) && (
        <div className="absolute z-10 mt-1 top-full left-0 p-2 bg-red-100 border border-red-200 rounded-md shadow-lg text-sm text-red-800 max-w-xs">
          {uploadState.error || localError}
          <button
            onClick={() => {
              setUploadState(prev => ({ ...prev, error: null }));
              setLocalError(null);
            }}
            className="ml-2 text-red-600 hover:text-red-800"
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
});

ResourceChip.displayName = 'ResourceChip';

export default ResourceChip;
