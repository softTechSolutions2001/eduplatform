/**
 * File: frontend/src/courseBuilder/CourseBuilder.tsx
 * Version: 3.3.0
 * Date: 2025-06-25 04:25:11 UTC
 * Author: saiacupunctureFolllow
 * Last Modified: 2025-06-25 04:25:11 UTC
 *
 * Enhanced Course Builder Root Component - Zustand Migration
 *
 * This component serves as the entry point for the course building experience,
 * handling course initialization, session management, state management via Zustand,
 * status tracking, and navigation between different builder views.
 *
 * Key improvements:
 * - Migrated from Redux to Zustand for state management
 * - Removed unnecessary Redux Provider and store configuration
 * - Direct Zustand store integration for better performance
 * - Session-based routing system with offline fallback
 * - Enhanced error boundaries
 * - Improved DnD provider integration
 * - Better callback handling for publish/exit flows
 * - Fixed memory leaks and improved stability
 * - Improved type safety and error handling
 * - Enhanced session creation with offline mode support
 */

import React, { useCallback, useEffect, useState } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { ErrorBoundary } from 'react-error-boundary';
import {
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
  useSearchParams,
} from 'react-router-dom';
import MainLayout from '../components/layouts/MainLayout';
import courseBuilderAPI from './api/courseBuilderAPI';
import { builderApiService } from './api/dndSession';
import NewCourseDialog from './components/NewCourseDialog';
import { useAutoSave } from './hooks/useAutoSave';
import BuilderBoard from './pages/BuilderBoard';
import Instructions from './pages/Instructions';
import ReviewPublish from './pages/ReviewPublish';
import { useCourseStore } from './store/courseSlice';
import './styles/courseBuilder.css';

// Enhanced loading states as a discriminated union of string literals
type LoadingState = 'idle' | 'loading' | 'creating_draft' | 'creating_session' | 'error' | 'success';

// Enhanced error fallback component
const BuilderErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({
  error,
  resetErrorBoundary,
}) => {
  const handleDashboardRedirect = useCallback(() => {
    try {
      window.location.href = '/instructor/dashboard';
    } catch (err) {
      // Fallback if navigation fails
      window.location.reload();
    }
  }, []);

  return (
    <div className="flex justify-center items-center h-screen bg-gray-50">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-lg">
        <div
          className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center"
          role="img"
          aria-label="Error icon"
        >
          <svg
            className="w-8 h-8 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Course Builder Error
        </h3>
        <p className="text-red-600 mb-6">{error.message}</p>

        <div className="space-y-3">
          <button
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={resetErrorBoundary}
          >
            Try Again
          </button>

          <button
            className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            onClick={handleDashboardRedirect}
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

// Enhanced DnD Provider wrapper
const CustomDnDProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <DndProvider backend={HTML5Backend}>
      {children}
    </DndProvider>
  );
};

// Combined state interface for better state management
interface CourseBuilderState {
  loadingState: LoadingState;
  error: string | null;
  retryCount: number;
  showTitleDialog: boolean;
  loadingProgress: number;
  isOfflineMode: boolean;
}

// Props interface for the main CourseBuilder component
interface CourseBuilderProps {
  sessionId?: string;
  onPublish?: (courseId: number) => void;
  onExit?: () => void;
}

// Main component that wraps the course builder with error boundaries
const CourseBuilder: React.FC<CourseBuilderProps> = ({
  sessionId: propSessionId,
  onPublish,
  onExit,
}) => {
  const navigate = useNavigate();

  // Enhanced state management for session creation
  const [state, setState] = useState<CourseBuilderState>({
    loadingState: 'idle',
    error: null,
    retryCount: 0,
    showTitleDialog: false,
    loadingProgress: 0,
    isOfflineMode: false,
  });

  // Enhanced session creation with offline fallback
  const createNewSession = useCallback(async () => {
    if (!propSessionId) {
      try {
        setState(prev => ({ ...prev, loadingState: 'creating_session', loadingProgress: 20 }));
        const newSessionId = await builderApiService.createSession();

        // Wait a bit for the navigation to complete
        await new Promise(resolve => setTimeout(resolve, 100));
        setState(prev => ({ ...prev, loadingState: 'success', loadingProgress: 100 }));
        navigate(`/course-builder/${newSessionId}`, { replace: true });
      } catch (error) {
        console.error('Failed to create new session:', error);

        // ✅ ENHANCED: Create fallback offline session
        const offlineSessionId = `offline_${Date.now()}`;
        setState(prev => ({
          ...prev,
          loadingState: 'success',
          loadingProgress: 100,
          isOfflineMode: true,
          error: 'Working in offline mode. Session created locally.'
        }));
        navigate(`/course-builder/${offlineSessionId}`, { replace: true });
      }
    }
  }, [propSessionId, navigate]);

  // Create new session if none provided
  useEffect(() => {
    createNewSession();
  }, [createNewSession]);

  // Handle publish callback with error handling
  const handlePublishComplete = useCallback((courseId: number) => {
    try {
      if (onPublish) {
        onPublish(courseId);
      } else {
        navigate(`/instructor/courses/${courseId}`);
      }
    } catch (error) {
      console.error('Error in publish callback:', error);
      // Fallback navigation
      navigate('/instructor/courses');
    }
  }, [onPublish, navigate]);

  // Handle exit callback with error handling
  const handleExit = useCallback(() => {
    try {
      if (onExit) {
        onExit();
      } else {
        navigate('/instructor/courses');
      }
    } catch (error) {
      console.error('Error in exit callback:', error);
      // Fallback navigation
      window.location.href = '/instructor/courses';
    }
  }, [onExit, navigate]);

  // Enhanced loading component with offline mode indication
  const LoadingComponent = () => (
    <div className="flex flex-col justify-center items-center h-screen bg-gray-50">
      <div className="text-center max-w-md">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-6"></div>

        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-800">
            {state.loadingState === 'creating_session'
              ? 'Initializing session...'
              : 'Loading...'}
          </h3>
          <p className="text-gray-600">
            {state.loadingState === 'creating_session'
              ? 'Setting up your workspace. This may take a moment.'
              : 'Please wait while we prepare your environment.'}
          </p>
        </div>

        {/* Dynamic progress indicator */}
        <div className="mt-6 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${state.loadingProgress}%` }}
          ></div>
        </div>

        {/* Progress percentage */}
        <div className="mt-2 text-sm text-gray-500">
          {state.loadingProgress}%
        </div>

        {/* Offline mode indicator during loading */}
        {state.isOfflineMode && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              🔄 Switching to offline mode...
            </p>
          </div>
        )}
      </div>
    </div>
  );

  // Show loading while creating session
  if (state.loadingState === 'creating_session') {
    return <LoadingComponent />;
  }

  return (
    <ErrorBoundary FallbackComponent={BuilderErrorFallback}>
      <MainLayout>
        <div className="course-builder-container" data-testid="course-builder">
          {/* Offline mode notification */}
          {state.isOfflineMode && state.error && (
            <div className="fixed top-4 right-4 z-50 max-w-sm">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 shadow-lg">
                <div className="flex items-start">
                  <svg
                    className="w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div>
                    <p className="text-sm text-yellow-800 font-medium">
                      Offline Mode
                    </p>
                    <p className="text-xs text-yellow-700 mt-1">{state.error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <Routes>
            <Route
              path=":sessionId"
              element={
                <CustomDnDProvider>
                  <CourseEditorWrapper />
                </CustomDnDProvider>
              }
            />
            <Route
              path=":sessionId/instructions"
              element={<Instructions />}
            />
            <Route
              path=":sessionId/review"
              element={
                <ReviewPublish
                  onPublishComplete={handlePublishComplete}
                  onCancel={handleExit}
                />
              }
            />
            <Route
              path=""
              element={
                propSessionId ? (
                  <Navigate to={`${propSessionId}`} replace />
                ) : (
                  <CustomDnDProvider>
                    <CourseEditorWrapper />
                  </CustomDnDProvider>
                )
              }
            />
          </Routes>
        </div>
      </MainLayout>
    </ErrorBoundary>
  );
};

// Enhanced wrapper component with better state management and session handling
const CourseEditorWrapper: React.FC = () => {
  const { sessionId, courseSlug } = useParams<{ sessionId?: string; courseSlug?: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Access Zustand store directly
  const setCourse = useCourseStore(state => state.setCourse);
  const course = useCourseStore(state => state.course);

  // Combined state for better management
  const [state, setState] = useState<CourseBuilderState>({
    loadingState: 'idle',
    error: null,
    retryCount: 0,
    showTitleDialog: false,
    loadingProgress: 60,
    isOfflineMode: false,
  });

  const { saveStatus, lastSaved } = useAutoSave();

  // Memoized search param getters with proper dependencies
  const templateId = searchParams.get('template');
  const isNewCourse = searchParams.get('new') === 'true';

  // Check if we're in offline mode based on session ID
  const isOfflineSession = sessionId?.startsWith('offline_') || sessionId?.startsWith('temp_');

  // Improved error handler with proper typing
  const handleError = useCallback((err: Error | unknown, context: string) => {
    console.error(`${context}:`, err);
    const errorMessage = err instanceof Error
      ? err.message
      : `Failed to ${context.toLowerCase()}. Please try again.`;

    setState(prev => ({
      ...prev,
      error: errorMessage,
      loadingState: 'error',
    }));
  }, []);

  // Enhanced session creation with better error handling and retry logic
  const createSession = useCallback(async (): Promise<string> => {
    if (sessionId) return sessionId;

    try {
      setState(prev => ({ ...prev, loadingState: 'creating_session' }));
      const newSessionId = await builderApiService.createSession();
      setState(prev => ({ ...prev, loadingState: 'success' }));
      navigate(`/course-builder/${newSessionId}`, { replace: true });
      return newSessionId;
    } catch (err) {
      console.error('Failed to create session:', err);
      // Create a temporary session ID for offline mode
      const tempSessionId = `temp_${Date.now()}`;
      setState(prev => ({
        ...prev,
        loadingState: 'success',
        isOfflineMode: true,
        error: 'Working in offline mode. Changes may not be saved to the server.'
      }));
      navigate(`/course-builder/${tempSessionId}`, { replace: true });
      return tempSessionId;
    }
  }, [sessionId, navigate]);

  // Modified createDraftCourse with improved state management
  const createDraftCourse = useCallback(
    async (providedTitle?: string) => {
      try {
        setState(prev => ({
          ...prev,
          loadingState: 'creating_draft',
          error: null,
        }));

        // Ensure we have a session
        const currentSessionId = await createSession();

        // If no title and no template, show the dialog
        if (!providedTitle && !templateId) {
          setState(prev => ({
            ...prev,
            loadingState: 'idle',
            showTitleDialog: true,
          }));
          return null;
        }

        let draftData;

        try {
          if (templateId) {
            // Create from template - templates have predefined titles
            console.log(`Creating course from template: ${templateId} in session: ${currentSessionId}`);
            draftData = courseBuilderAPI.createFromTemplate
              ? await courseBuilderAPI.createFromTemplate(templateId, currentSessionId)
              : await courseBuilderAPI.cloneVersion(templateId, currentSessionId);
          } else {
            // Create with provided title from dialog
            console.log(`Creating new course with title: ${providedTitle} in session: ${currentSessionId}`);
            draftData = await courseBuilderAPI.createDraft(providedTitle, currentSessionId);
          }

          // Update Zustand store directly
          setCourse(draftData);

          // Navigate to the course within the session
          navigate(`${currentSessionId}/${draftData.slug}`, { replace: true });

          setState(prev => ({ ...prev, loadingState: 'success' }));
          return draftData;
        } catch (err: unknown) {
          // If API call fails, create a temporary course in memory
          console.error('Failed to create draft course from API:', err);

          // Create a temporary course that works without backend
          const tempCourse = {
            id: `temp_${Date.now()}`,
            title: providedTitle || 'New Course (Working Offline)',
            slug: `temp-course-${Date.now()}`,
            description: '',
            modules: [],
            sessionId: currentSessionId,
            isTemporary: true,
          };

          // Set temporary course in Zustand store
          setCourse(tempCourse);

          // Don't show the error UI immediately if we have a fallback course
          setState(prev => ({
            ...prev,
            loadingState: 'success',
            isOfflineMode: true,
            error: 'Working in offline mode. Changes may not be saved to the server.',
          }));

          return tempCourse;
        }
      } catch (err) {
        handleError(err, 'create new course');
        throw err;
      }
    },
    [templateId, navigate, handleError, createSession, setCourse]
  );

  const handleCourseCreatedFromDialog = useCallback(
    (newCourse: any) => {
      setState(prev => ({ ...prev, showTitleDialog: false }));
      setCourse(newCourse);

      // Navigate to the course within the current session
      const currentSessionId = sessionId || `temp_${Date.now()}`;
      navigate(`${currentSessionId}/${newCourse.slug}`, { replace: true });
    },
    [navigate, sessionId, setCourse]
  );

  const loadExistingCourse = useCallback(
    async (slug: string) => {
      try {
        setState(prev => ({
          ...prev,
          loadingState: 'loading',
          error: null,
        }));

        console.log(`Loading course: ${slug} in session: ${sessionId}`);
        const courseData = await courseBuilderAPI.getCourse(slug, sessionId);
        setCourse(courseData);

        setState(prev => ({ ...prev, loadingState: 'success' }));
        return courseData;
      } catch (err) {
        handleError(err, 'load course data');
        throw err;
      }
    },
    [handleError, sessionId, setCourse]
  );

  const initializeCourse = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loadingState: 'loading' }));

      if (!courseSlug || isNewCourse) {
        await createDraftCourse();
      } else {
        await loadExistingCourse(courseSlug);
      }
    } catch (err) {
      // Error already handled in individual functions
    }
  }, [courseSlug, isNewCourse, createDraftCourse, loadExistingCourse]);

  const handleRetry = useCallback(() => {
    setState(prev => ({
      ...prev,
      retryCount: prev.retryCount + 1,
      error: null,
    }));
    initializeCourse();
  }, [initializeCourse]);

  // Fixed progress simulation with proper cleanup and better timing
  useEffect(() => {
    let intervalId: number | null = null;

    const PROGRESS_INCREMENT = 8; // Slightly faster increment
    const PROGRESS_INTERVAL = 400; // Slightly faster interval
    const MAX_PROGRESS = 90;

    if (
      state.loadingState === 'loading' ||
      state.loadingState === 'creating_draft' ||
      state.loadingState === 'creating_session'
    ) {
      // Reset progress when starting new loading operation
      if (state.loadingProgress === 100) {
        setState(prev => ({ ...prev, loadingProgress: 0 }));
      }

      intervalId = window.setInterval(() => {
        setState(prev => ({
          ...prev,
          loadingProgress: prev.loadingProgress < MAX_PROGRESS
            ? Math.min(prev.loadingProgress + PROGRESS_INCREMENT, MAX_PROGRESS)
            : prev.loadingProgress,
        }));
      }, PROGRESS_INTERVAL);
    } else if (state.loadingState === 'success') {
      // Complete the progress bar immediately when successful
      setState(prev => ({ ...prev, loadingProgress: 100 }));
    } else if (state.loadingState === 'error') {
      // Stop progress on error
      setState(prev => ({ ...prev, loadingProgress: 0 }));
    }

    return () => {
      if (intervalId !== null) {
        clearInterval(intervalId);
      }
    };
  }, [state.loadingState, state.loadingProgress]);

  useEffect(() => {
    if (sessionId) {
      initializeCourse();
    }
  }, [initializeCourse, sessionId]);

  // Enhanced loading component
  const LoadingComponent = () => (
    <div className="flex flex-col justify-center items-center h-screen bg-gray-50">
      <div className="text-center max-w-md">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-6"></div>

        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-800">
            {state.loadingState === 'creating_session'
              ? 'Initializing session...'
              : state.loadingState === 'creating_draft'
                ? templateId
                  ? 'Creating course from template...'
                  : 'Setting up your new course...'
                : 'Loading course...'}
          </h3>
          <p className="text-gray-600">
            {state.loadingState === 'creating_session'
              ? 'Setting up your workspace.'
              : state.loadingState === 'creating_draft'
                ? 'This will just take a moment.'
                : 'Retrieving your course data.'}
          </p>
        </div>

        {/* Dynamic progress indicator for long operations */}
        <div className="mt-6 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${state.loadingProgress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );

  // Enhanced error component
  const ErrorComponent = () => (
    <div className="flex justify-center items-center h-screen bg-gray-50">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-lg">
        <div
          className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center"
          role="img"
          aria-label="Error icon"
        >
          <svg
            className="w-8 h-8 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Something went wrong
        </h3>
        <p className="text-red-600 mb-6">{state.error}</p>

        <div className="space-y-3">
          <button
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={handleRetry}
          >
            Try Again {state.retryCount > 0 ? `(${state.retryCount})` : ''}
          </button>

          <button
            className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            onClick={() => {
              try {
                navigate('/instructor/dashboard');
              } catch (err) {
                window.location.href = '/instructor/dashboard';
              }
            }}
          >
            Return to Dashboard
          </button>
        </div>

        {state.retryCount > 2 && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              Having trouble? Try refreshing the page or contact support if the
              issue persists.
            </p>
          </div>
        )}
      </div>
    </div>
  );

  // Don't render the main UI if we're showing the title dialog
  if (state.showTitleDialog) {
    return (
      <NewCourseDialog
        isOpen={state.showTitleDialog}
        onClose={() => {
          setState(prev => ({ ...prev, showTitleDialog: false }));
          navigate('/instructor/dashboard', { replace: true });
        }}
        onCourseCreated={handleCourseCreatedFromDialog}
      />
    );
  }

  // Render based on loading state
  if (
    state.loadingState === 'loading' ||
    state.loadingState === 'creating_draft' ||
    state.loadingState === 'creating_session'
  ) {
    return <LoadingComponent />;
  }

  if (state.loadingState === 'error') {
    return <ErrorComponent />;
  }

  return (
    <div className="relative">
      {/* Auto-save status indicator */}
      {course?.id && (
        <div className="fixed top-4 right-4 z-50">
          <div
            className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-300 ${saveStatus === 'saving'
              ? 'bg-yellow-100 text-yellow-800'
              : saveStatus === 'saved'
                ? 'bg-green-100 text-green-800'
                : saveStatus === 'error'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-600'
              }`}
          >
            {saveStatus === 'saving' && '💾 Saving...'}
            {saveStatus === 'saved' &&
              `✅ Saved ${lastSaved ? new Date(lastSaved).toLocaleTimeString() : ''}`}
            {saveStatus === 'error' && '❌ Save failed'}
            {saveStatus === 'idle' && '📝 Ready'}
          </div>
        </div>
      )}

      {/* Session indicator with offline mode detection */}
      {sessionId && (
        <div className="fixed top-4 left-4 z-50">
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${isOfflineSession
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-blue-100 text-blue-800'
            }`}>
            {isOfflineSession ? '🔄 Offline' : '🌐 Online'} Session: {sessionId.substring(0, 8)}...
          </div>
        </div>
      )}

      {/* Offline mode warning - Enhanced with better positioning and dismissible option */}
      {(state.error && course?.isTemporary) || state.isOfflineMode && (
        <div className="fixed top-16 right-4 z-50 max-w-sm">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 shadow-lg">
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <svg
                  className="w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <div>
                  <p className="text-sm text-yellow-800 font-medium">
                    Offline Mode
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    {state.error || 'Working in offline mode. Changes may not be saved to the server.'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setState(prev => ({ ...prev, error: null }))}
                className="ml-2 text-yellow-400 hover:text-yellow-600 transition-colors"
                aria-label="Dismiss notification"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pass the course slug with fallback to the store value and session ID */}
      <BuilderBoard
        courseSlug={courseSlug ?? course?.slug}
        sessionId={sessionId}
      />
    </div>
  );
};

export default CourseBuilder;
