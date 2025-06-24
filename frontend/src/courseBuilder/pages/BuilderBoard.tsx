/**
 * File: frontend/src/courseBuilder/pages/BuilderBoard.tsx
 * Version: 2.3.0
 * Date Created: 2025-06-14 15:57:16
 * Date Revised: 2025-06-24 14:47:47
 * Current User: saiacupuncture
 * Last Modified By: saiacupuncture
 *
 * Enhanced Course Builder Board Component with Critical Fixes
 *
 * This is the main orchestration component for the course builder interface.
 * It manages course loading, module management, and drag-and-drop functionality
 * with comprehensive error handling and performance optimizations.
 *
 * Key Features:
 * - Race condition prevention with proper loading state guards
 * - Memory leak prevention with proper cleanup mechanisms
 * - Performance optimizations with React.memo and useCallback
 * - Enhanced error handling with comprehensive user feedback
 * - Accessibility improvements with proper ARIA attributes
 * - State synchronization between course and module loading
 * - Proper virtualization implementation for better performance
 * - Error boundaries for robust error handling
 *
 * Version 2.3.0 Changes:
 * - FIXED: VirtuosoGrid implementation error - replaced with proper Virtuoso component
 * - FIXED: Race condition in module loading with improved condition logic
 * - FIXED: Memory leak in useModuleLoader hook with specific dependencies
 * - IMPROVED: Error handling consistency with unified handleAsyncError utility
 * - IMPROVED: Memoization efficiency by removing unnecessary computations
 * - IMPROVED: Accessibility with proper ARIA attributes
 * - IMPROVED: Type safety with enhanced interface definitions
 * - IMPROVED: Key generation for better performance
 *
 * Connected Files:
 * - frontend/src/courseBuilder/components/ModuleCard.tsx - Module management
 * - frontend/src/courseBuilder/components/Toolbar.tsx - Action toolbar
 * - frontend/src/courseBuilder/store/courseSlice.ts - State management
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - API operations
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { FaPlus } from 'react-icons/fa';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Virtuoso } from 'react-virtuoso';
import courseBuilderAPI from '../api/courseBuilderAPI';
import { builderApiService } from '../api/dndSession';
import ModuleCard from '../components/ModuleCard';
import SwitchEditorBanner from '../components/SwitchEditorBanner';
import Toolbar from '../components/Toolbar';
import DnDContext from '../dnd/DnDContext';
import { useAutoSave } from '../hooks/useAutoSave';
import { useDirtyPrompt } from '../hooks/useDirtyPrompt';
import { courseSelectors, useCourseStore } from '../store/courseSlice';

// Enhanced type definitions for better type safety
interface Module {
  id: string;
  title: string;
  // Add other module properties as needed
}

interface Course {
  slug: string;
  title: string;
  modules?: Module[];
  isTemporary?: boolean;
  // Add other course properties as needed
}

interface BuilderBoardProps {
  courseSlug?: string;
  onError?: (error: Error) => void;
  className?: string;
}

interface LoadingSpinnerProps {
  message: string;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

interface ErrorDisplayProps {
  error: string;
  onRetry?: () => void;
  onGoBack?: () => void;
  retryCount?: number;
  className?: string;
}

interface EmptyModulesStateProps {
  onAddModule: () => void;
  disabled: boolean;
  isLoading?: boolean;
}

// Enhanced error boundary fallback component with development details
const ErrorFallback = ({ error, resetErrorBoundary }: any) => (
  <div className="flex justify-center items-center min-h-[400px] bg-gray-50">
    <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full mx-4">
      <div className="flex items-center mb-4">
        <svg className="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 className="text-xl font-semibold text-red-600">Something went wrong</h2>
      </div>

      <div className="mb-4">
        <p className="text-gray-700 mb-2">An unexpected error occurred:</p>
        <pre className="text-sm bg-gray-100 p-2 rounded border overflow-auto max-h-32">
          {error.message}
        </pre>
      </div>

      {process.env.NODE_ENV === 'development' && (
        <details className="mb-4">
          <summary className="cursor-pointer text-sm text-gray-600">
            Technical Details
          </summary>
          <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-auto">
            {error.stack}
          </pre>
        </details>
      )}

      <button
        onClick={resetErrorBoundary}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
      >
        Try again
      </button>
    </div>
  </div>
);

// Enhanced loading spinner with size variants
const LoadingSpinner: React.FC<LoadingSpinnerProps> = React.memo(({
  message,
  size = 'medium',
  className = ''
}) => {
  const sizeClasses = {
    small: 'h-6 w-6',
    medium: 'h-12 w-12',
    large: 'h-16 w-16'
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className="text-center" role="status" aria-live="polite">
        <div
          className={`animate-spin rounded-full border-b-2 border-blue-600 mx-auto ${sizeClasses[size]}`}
          aria-label="Loading"
        />
        <p className="mt-4 text-gray-600">{message}</p>
      </div>
    </div>
  );
});

LoadingSpinner.displayName = 'LoadingSpinner';

// Enhanced error display with better UX
const ErrorDisplay: React.FC<ErrorDisplayProps> = React.memo(({
  error,
  onRetry,
  onGoBack,
  retryCount = 0,
  className = '',
}) => (
  <div className={`flex justify-center items-center min-h-[400px] bg-gray-50 ${className}`}>
    <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full mx-4">
      <div className="flex items-center mb-4">
        <svg className="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 className="text-xl font-semibold text-red-600">Error</h2>
      </div>

      <p className="text-gray-700 mb-4">{error}</p>

      <div className="flex gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            data-testid="retry-button"
          >
            Retry {retryCount > 0 ? `(${retryCount})` : ''}
          </button>
        )}
        {onGoBack && (
          <button
            onClick={onGoBack}
            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            data-testid="go-back-button"
          >
            Go to Courses
          </button>
        )}
      </div>
    </div>
  </div>
));

ErrorDisplay.displayName = 'ErrorDisplay';

// Enhanced empty state with better accessibility
const EmptyModulesState: React.FC<EmptyModulesStateProps> = React.memo(({
  onAddModule,
  disabled,
  isLoading
}) => (
  <div className="py-12 text-center" data-testid="empty-modules">
    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 text-gray-400 mb-4">
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    </div>

    <h3 className="text-lg font-medium text-gray-900 mb-1">No Modules Yet</h3>
    <p className="text-gray-500 mb-4">Get started by adding your first module</p>

    <button
      data-testid="add-first-module-btn"
      onClick={onAddModule}
      disabled={disabled || isLoading}
      aria-label="Add new module to course"
      aria-describedby={disabled ? "readonly-banner" : undefined}
      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {isLoading ? (
        <>
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
          Adding...
        </>
      ) : (
        <>
          <FaPlus className="w-5 h-5 mr-2" />
          Add First Module
        </>
      )}
    </button>
  </div>
));

EmptyModulesState.displayName = 'EmptyModulesState';

// Enhanced read-only banner with proper ID for accessibility
const ReadOnlyBanner: React.FC = React.memo(() => (
  <div id="readonly-banner" className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 flex items-center">
    <svg className="h-5 w-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <div>
      <strong>This published course is read-only.</strong> Click "Create New Version" in the toolbar above to make edits.
    </div>
  </div>
));

ReadOnlyBanner.displayName = 'ReadOnlyBanner';

// Enhanced save status component
const SaveStatus: React.FC<{
  isAutoSaving: boolean;
  lastSavedAt: Date | null;
  saveError: Error | null;
  onRetry: () => void;
}> = React.memo(({ isAutoSaving, lastSavedAt, saveError, onRetry }) => {
  const formattedTime = useMemo(() => {
    if (!lastSavedAt) return '';

    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    }).format(lastSavedAt);
  }, [lastSavedAt]);

  return (
    <div className="text-sm text-gray-500 flex items-center" data-testid="save-status">
      {isAutoSaving && (
        <span className="text-blue-600 flex items-center">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-1" />
          Saving...
        </span>
      )}

      {!isAutoSaving && lastSavedAt && !saveError && (
        <span className="text-green-600 flex items-center" data-testid="last-saved">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Saved {formattedTime}
        </span>
      )}

      {saveError && (
        <span className="text-red-600 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Save failed: {saveError.message}
          <button
            onClick={onRetry}
            className="ml-2 text-blue-600 hover:text-blue-800 underline focus:outline-none"
          >
            Retry
          </button>
        </span>
      )}
    </div>
  );
});

SaveStatus.displayName = 'SaveStatus';

// Enhanced course loader with proper error handling and session support
const useCourseLoader = (courseSlug?: string, sessionId?: string) => {
  const { setCourse } = useCourseStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const loadCourse = useCallback(async () => {
    // Prevent API calls with invalid slugs or session IDs
    if ((!courseSlug || courseSlug.startsWith('temp_') || courseSlug === 'undefined') && !sessionId) {
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      setIsLoading(true);
      setError(null);

      let courseData;

      // Load from session if sessionId is provided
      if (sessionId) {
        courseData = await builderApiService.getSession(sessionId);
      } else if (courseSlug) {
        courseData = await courseBuilderAPI.getCourse(courseSlug, {
          signal: abortControllerRef.current.signal
        });
      }

      if (courseData) {
        setCourse(courseData);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        return; // Request was cancelled
      }

      const errorMessage = err.message || 'Failed to load course';
      setError(errorMessage);
      console.error('Course loading error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [courseSlug, sessionId, setCourse]);

  const retry = useCallback(() => {
    loadCourse();
  }, [loadCourse]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    loadCourse();
  }, [loadCourse]);

  return { isLoading, error, retry };
};

// Fixed module loader with proper dependencies and race condition prevention
const useModuleLoader = (courseSlug?: string, course?: Course) => {
  const { mergeCourse } = useCourseStore();
  const [isLoadingModules, setIsLoadingModules] = useState(false);
  const [moduleError, setModuleError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Fixed: Use specific course properties instead of the entire course object
  const fetchModules = useCallback(async () => {
    // Fixed: Simplified and improved condition logic to prevent race conditions
    if (!courseSlug ||
      !course ||
      course.isTemporary ||
      courseSlug.startsWith('temp_') ||
      courseSlug === 'undefined') {
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoadingModules(true);
    setModuleError(null);

    try {
      const modulesData = await courseBuilderAPI.getModules(courseSlug, {
        signal: abortControllerRef.current.signal
      });

      mergeCourse({ modules: modulesData });
    } catch (error: any) {
      if (error.name === 'AbortError') {
        return; // Request was cancelled
      }

      const errorMessage = error.message || 'Failed to fetch modules';
      setModuleError(errorMessage);
      console.error('Failed to fetch modules:', error);
    } finally {
      setIsLoadingModules(false);
    }
  }, [courseSlug, course?.slug, course?.isTemporary, mergeCourse]); // Fixed: Use specific properties

  const retryModules = useCallback(() => {
    fetchModules();
  }, [fetchModules]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { fetchModules, isLoadingModules, moduleError, retryModules };
};

// Enhanced ModuleList component with proper memoization
const ModuleList = React.memo<{
  modules: Module[];
  onMove: (dragIndex: number, hoverIndex: number) => void;
  readOnly: boolean;
  onError: (error: Error, context: string) => void;
}>(({ modules, onMove, readOnly, onError }) => {
  // Fixed: Use stable keys without index
  const moduleItems = useMemo(() =>
    modules.map((module, index) => ({
      module,
      index,
      key: module.id // Fixed: Use stable ID only
    })),
    [modules]
  );

  return (
    <div data-testid="modules-container" role="list" aria-label="Course modules">
      {moduleItems.length > 10 ? (
        // Fixed: Use proper Virtuoso component for vertical list instead of VirtuosoGrid
        <div className="space-y-4">
          <Virtuoso
            totalCount={moduleItems.length}
            overscan={5}
            itemContent={(index) => {
              const { module, index: moduleIndex, key } = moduleItems[index];
              return (
                <div key={key} className="mb-4">
                  <ModuleCard
                    module={module}
                    index={moduleIndex}
                    onMove={onMove}
                    readOnly={readOnly}
                    onError={onError}
                    data-testid={`module-card-${moduleIndex}`}
                  />
                </div>
              );
            }}
            style={{ height: '600px' }}
          />
        </div>
      ) : (
        // Use regular rendering for smaller lists
        <div className="space-y-4">
          {moduleItems.map(({ module, index: moduleIndex, key }) => (
            <ModuleCard
              key={key}
              module={module}
              index={moduleIndex}
              onMove={onMove}
              readOnly={readOnly}
              onError={onError}
              data-testid={`module-card-${moduleIndex}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}, (prevProps, nextProps) => {
  // Enhanced comparison for better performance
  return (
    prevProps.modules.length === nextProps.modules.length &&
    prevProps.readOnly === nextProps.readOnly &&
    prevProps.modules.every((module, index) =>
      module.id === nextProps.modules[index]?.id
    )
  );
});

ModuleList.displayName = 'ModuleList';

// Main component with comprehensive enhancements
const BuilderBoard: React.FC<BuilderBoardProps> = React.memo(({
  courseSlug,
  onError,
  className = ''
}) => {
  const {
    course,
    addModule,
    reorderModules,
    isDirty,
    lastSaved,
  } = useCourseStore();

  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const { isLoading, error, retry } = useCourseLoader(courseSlug, sessionId);
  const { fetchModules, isLoadingModules, moduleError, retryModules } = useModuleLoader(courseSlug, course);
  const { isAutoSaving, lastSavedAt, saveError, triggerSave } = useAutoSave();

  const [retryCount, setRetryCount] = useState(0);
  const [moduleRetryCount, setModuleRetryCount] = useState(0);
  const [isAddingModule, setIsAddingModule] = useState(false);

  // Cleanup refs for memory leak prevention
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Hooks
  useDirtyPrompt(isDirty);

  // Enhanced error handling utility for consistent error handling
  const handleAsyncError = useCallback(async (
    operation: () => Promise<void>,
    context: string,
    successMessage?: string
  ) => {
    try {
      await operation();
      if (successMessage) {
        toast.success(successMessage);
      }
    } catch (error) {
      const errorInstance = error instanceof Error ? error : new Error(`Failed to ${context}`);
      console.error(`BuilderBoard error in ${context}:`, errorInstance);

      if (onError) {
        onError(errorInstance);
      }

      toast.error(`${context}: ${errorInstance.message}`);
    }
  }, [onError]);

  // Enhanced retry handlers with proper count tracking
  const handleRetry = useCallback(() => {
    setRetryCount(prev => prev + 1);
    retry();
  }, [retry]);

  const handleRetryModules = useCallback(() => {
    setModuleRetryCount(prev => prev + 1);
    retryModules();
  }, [retryModules]);

  // Fixed: Enhanced module fetching with improved condition logic
  useEffect(() => {
    if (!course?.slug ||
      course.isTemporary ||
      isLoadingModules ||
      (course.modules && course.modules.length > 0)) {
      return;
    }

    console.log('Fetching modules for course slug:', course.slug);
    fetchModules();
  }, [course?.slug, course?.isTemporary, course?.modules?.length, fetchModules, isLoadingModules]);

  // Enhanced computed values with proper canEdit handling
  const showReadOnlyBanner = useMemo(() => {
    if (!course) return false;
    return courseSelectors.isPublished(course) && !courseSelectors.isDraft(course) && !courseSelectors.canEdit(course);
  }, [course]);

  // Fixed: Use direct computation for simple checks instead of unnecessary memoization
  const hasModules = Boolean(course?.modules?.length);

  // Enhanced move handler with async error handling
  const handleMoveModules = useCallback(async (dragIndex: number, hoverIndex: number) => {
    if (!course?.modules || showReadOnlyBanner) return;

    await handleAsyncError(async () => {
      const modules = [...course.modules!];
      const [dragged] = modules.splice(dragIndex, 1);
      modules.splice(hoverIndex, 0, dragged);

      const newOrder = modules.map(m => m.id);
      reorderModules(newOrder);

      // Sync with server for non-temporary courses
      if (course.slug && !course.isTemporary) {
        await courseBuilderAPI.reorderModules(course.slug, newOrder);
      }
    }, 'Module reordering', 'Module order updated successfully');
  }, [course, reorderModules, showReadOnlyBanner, handleAsyncError]);

  // Enhanced add module handler with consistent error handling
  const handleAddModule = useCallback(async () => {
    if (showReadOnlyBanner || isAddingModule) return;

    setIsAddingModule(true);
    await handleAsyncError(async () => {
      await addModule();
      triggerSave();
    }, 'Adding module', 'Module added successfully');
    setIsAddingModule(false);
  }, [addModule, showReadOnlyBanner, isAddingModule, handleAsyncError, triggerSave]);

  const handleGoToCourses = useCallback(() => {
    navigate('/instructor/courses');
  }, [navigate]);

  // Cleanup effect for memory leak prevention
  useEffect(() => {
    return () => {
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current);
      }
    };
  }, []);

  // Enhanced loading state
  if (isLoading) {
    return (
      <div className={`min-h-screen bg-gray-50 ${className}`}>
        <LoadingSpinner message="Loading course builder..." size="large" className="h-screen" />
      </div>
    );
  }

  // Enhanced error state
  if (error) {
    return (
      <div className={`min-h-screen bg-gray-50 ${className}`}>
        <ErrorDisplay
          error={error}
          onRetry={handleRetry}
          onGoBack={handleGoToCourses}
          retryCount={retryCount}
          className="h-screen"
        />
      </div>
    );
  }

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <DnDContext>
        <div className={`min-h-screen bg-gray-50 ${className}`} data-testid="course-builder">
          <Toolbar courseSlug={course?.slug} />

          <div className="container mx-auto px-4 py-6">
            <SwitchEditorBanner courseSlug={courseSlug} currentEditor="builder" />

            {showReadOnlyBanner && <ReadOnlyBanner />}

            {/* Enhanced Header with save status */}
            <header className="mb-6 flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                {course?.title || 'Untitled Course'}
              </h1>
              <SaveStatus
                isAutoSaving={isAutoSaving}
                lastSavedAt={lastSavedAt}
                saveError={saveError}
                onRetry={triggerSave}
              />
            </header>

            {/* Main Content */}
            <main className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <section className="mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-medium text-gray-900 flex items-center">
                    Modules
                    {(course?.modules?.length || 0) > 0 && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {course.modules.length}
                      </span>
                    )}
                    {isLoadingModules && (
                      <span className="ml-2 text-sm text-gray-500" role="status" aria-live="polite">
                        <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-1"></div>
                        Loading...
                      </span>
                    )}
                  </h2>

                  <div className="flex items-center gap-2">
                    {moduleError && (
                      <button
                        onClick={handleRetryModules}
                        className="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                        title="Retry loading modules"
                        data-testid="retry-modules-btn"
                      >
                        <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Retry {moduleRetryCount > 0 ? `(${moduleRetryCount})` : ''}
                      </button>
                    )}

                    <button
                      data-testid="add-module-btn"
                      onClick={handleAddModule}
                      disabled={showReadOnlyBanner || isLoadingModules || isAddingModule}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      title={showReadOnlyBanner ? 'You must create a new draft to edit' : 'Add Module'}
                      aria-label="Add new module to course"
                      aria-describedby={showReadOnlyBanner ? "readonly-banner" : undefined}
                    >
                      {isAddingModule ? (
                        <>
                          <div className="w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin mr-1.5" />
                          Adding...
                        </>
                      ) : (
                        <>
                          <FaPlus className="h-4 w-4 mr-1.5" />
                          Add Module
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Module Error Display */}
                {moduleError && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 flex items-center justify-between">
                    <div className="flex items-center">
                      <svg className="h-5 w-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>
                        <strong>Error loading modules:</strong> {moduleError}
                      </span>
                    </div>
                    <button
                      onClick={handleRetryModules}
                      className="text-red-600 hover:text-red-800 font-medium underline focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                    >
                      Try Again {moduleRetryCount > 0 ? `(${moduleRetryCount})` : ''}
                    </button>
                  </div>
                )}

                {/* Enhanced Modules Content with Fixed Virtualization */}
                {hasModules ? (
                  <ModuleList
                    modules={course.modules!}
                    onMove={handleMoveModules}
                    readOnly={showReadOnlyBanner}
                    onError={(error, context) => handleAsyncError(async () => { throw error; }, context)}
                  />
                ) : !isLoadingModules && !moduleError ? (
                  <EmptyModulesState
                    onAddModule={handleAddModule}
                    disabled={showReadOnlyBanner}
                    isLoading={isAddingModule}
                  />
                ) : null}

                {/* Loading state for modules */}
                {isLoadingModules && !hasModules && (
                  <div className="py-12 text-center" role="status" aria-live="polite">
                    <LoadingSpinner message="Loading modules..." size="medium" />
                  </div>
                )}
              </section>
            </main>
          </div>
        </div>
      </DnDContext>
    </ErrorBoundary>
  );
});

BuilderBoard.displayName = 'BuilderBoard';

export default BuilderBoard;
