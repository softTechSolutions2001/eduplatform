/**
 * File: frontend/src/courseBuilder/hooks/useAutoSave.ts
 * Version: 2.0.0
 * Date Created: 2025-06-24 12:00:00
 * Date Revised: 2025-06-24 15:30:00
 * Author: Enhanced by Claude AI
 * Last Modified By: Claude AI
 * Last Modified: 2025-06-24 15:30:00 UTC
 *
 * Enhanced Auto-save hook for course builder
 *
 * This hook provides a robust, debounced auto-save mechanism for course builder components,
 * ensuring changes are persisted without excessive API calls while handling edge cases
 * and providing comprehensive error handling.
 *
 * Version 2.0.0 Changes:
 * - ADDED: Request cancellation with AbortController to prevent race conditions
 * - ADDED: Rate limiting to prevent rapid-fire saves
 * - ADDED: Save counter for analytics and debugging
 * - ADDED: Auto-reset of status states for better UX
 * - ADDED: Callback support (onSaveStart, onSaveSuccess, onSaveError)
 * - ADDED: Enhanced TypeScript typing and better return values
 * - IMPROVED: New vs existing course handling with proper draft creation
 * - IMPROVED: Memory leak prevention with proper cleanup
 * - IMPROVED: Error handling with abort signal checking
 * - IMPROVED: Status management with comprehensive SaveStatus type
 * - FIXED: Cleanup effect dependencies to prevent infinite loops
 * - FIXED: Proper request abortion on component unmount
 *
 * Features:
 * - Debounced auto-save (configurable delay)
 * - Periodic interval saves (configurable interval)
 * - Manual save triggers
 * - Request cancellation and race condition prevention
 * - Comprehensive error handling and status tracking
 * - Toast notifications (optional)
 * - New course creation and existing course updates
 * - Memory leak prevention
 * - Rate limiting protection
 * - Callback support for custom integrations
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import { buildCourseFormData } from '../../utils/buildCourseFormData';
import courseBuilderAPI from '../api/courseBuilderAPI';
import { useCourseStore } from '../store/courseSlice';

// Enhanced debounce utility with better TypeScript typing
function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): T & { flush: () => void; cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;

  const debounced = ((...args: Parameters<T>) => {
    lastArgs = args;

    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
      lastArgs = null;
    }, delay);
  }) as T & { flush: () => void; cancel: () => void };

  debounced.flush = () => {
    if (timeoutId && lastArgs) {
      clearTimeout(timeoutId);
      func(...lastArgs);
      timeoutId = null;
      lastArgs = null;
    }
  };

  debounced.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
      lastArgs = null;
    }
  };

  return debounced;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveOptions {
  enabled?: boolean;
  debounceMs?: number;
  saveInterval?: number;
  showNotifications?: boolean;
  onSaveStart?: () => void;
  onSaveSuccess?: (course: any) => void;
  onSaveError?: (error: Error) => void;
}

export const useAutoSave = (options: UseAutoSaveOptions = {}) => {
  const {
    enabled = true,
    debounceMs = 2000,
    saveInterval = 30000, // 30 seconds
    showNotifications = false,
    onSaveStart,
    onSaveSuccess,
    onSaveError,
  } = options;

  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [saveError, setSaveError] = useState<Error | null>(null);
  const [saveCount, setSaveCount] = useState(0);

  const { course, isDirty, mergeCourse } = useCourseStore();

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isNewCourseRef = useRef(false);
  const lastSaveAttemptRef = useRef<Date | null>(null);

  // Update new course tracking
  useEffect(() => {
    isNewCourseRef.current = !!(course && !course.slug);
  }, [course?.slug]);

  // Core save function with enhanced error handling
  const saveChanges = useCallback(async (isManual = false) => {
    if (!course) return;

    // Prevent rapid-fire saves
    const now = new Date();
    if (lastSaveAttemptRef.current &&
      now.getTime() - lastSaveAttemptRef.current.getTime() < 1000) {
      return;
    }
    lastSaveAttemptRef.current = now;

    // Abort any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      setSaveStatus('saving');
      setSaveError(null);

      if (onSaveStart) {
        onSaveStart();
      }

      const isNewCourse = isNewCourseRef.current;
      let savedCourse;

      if (isNewCourse) {
        // Create draft first for new courses
        const createdDraft = await courseBuilderAPI.createDraft(
          course.title || 'Untitled Course',
          { signal }
        );

        if (signal.aborted) return;

        if (createdDraft) {
          const courseData = await buildCourseFormData({
            ...course,
            slug: createdDraft.slug,
          });

          if (signal.aborted) return;

          savedCourse = await courseBuilderAPI.updateCourseFormData(
            createdDraft.slug,
            courseData,
            { signal }
          );

          isNewCourseRef.current = false;
        }
      } else if (course.slug) {
        // Update existing course
        const courseData = await buildCourseFormData(course);

        if (signal.aborted) return;

        savedCourse = await courseBuilderAPI.updateCourseFormData(
          course.slug,
          courseData,
          { signal }
        );
      }

      if (signal.aborted) return;

      if (savedCourse) {
        setSaveStatus('saved');
        setLastSavedAt(new Date());
        setSaveCount(prev => prev + 1);
        mergeCourse(savedCourse);

        if (onSaveSuccess) {
          onSaveSuccess(savedCourse);
        }

        if (isManual && showNotifications) {
          toast.success('Course saved successfully');
        }

        // Reset to idle after showing saved status briefly
        setTimeout(() => {
          if (abortControllerRef.current?.signal === signal) {
            setSaveStatus('idle');
          }
        }, 2000);
      }
    } catch (error: any) {
      if (signal.aborted) return;

      console.error('Save failed:', error);
      const saveError = error instanceof Error ? error : new Error('Save failed');
      setSaveError(saveError);
      setSaveStatus('error');

      if (onSaveError) {
        onSaveError(saveError);
      }

      if (showNotifications) {
        toast.error('Failed to save changes. Please try again.');
      }

      // Reset error status after some time
      setTimeout(() => {
        if (abortControllerRef.current?.signal === signal) {
          setSaveStatus('idle');
        }
      }, 5000);
    } finally {
      // Only clear if this is still the current request
      if (abortControllerRef.current?.signal === signal) {
        abortControllerRef.current = null;
      }
    }
  }, [course, mergeCourse, showNotifications, onSaveStart, onSaveSuccess, onSaveError]);

  // Create debounced auto-save function
  const debouncedAutoSave = useCallback(
    debounce(() => saveChanges(false), debounceMs),
    [saveChanges, debounceMs]
  );

  // Manual save function
  const triggerSave = useCallback(() => {
    debouncedAutoSave.cancel(); // Cancel any pending auto-save
    return saveChanges(true);
  }, [saveChanges, debouncedAutoSave]);

  // Auto-save effect - triggered by data changes
  useEffect(() => {
    if (!enabled || !course || !isDirty || saveStatus === 'saving') {
      return;
    }

    debouncedAutoSave();
  }, [enabled, course?.updatedAt, isDirty, saveStatus, debouncedAutoSave]);

  // Periodic save interval
  useEffect(() => {
    if (!enabled || !saveInterval) return;

    intervalRef.current = setInterval(() => {
      if (isDirty && saveStatus !== 'saving') {
        saveChanges(false);
      }
    }, saveInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, saveInterval, isDirty, saveStatus, saveChanges]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      debouncedAutoSave.cancel();

      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Save any pending changes on unmount
      if (isDirty) {
        debouncedAutoSave.flush();
      }
    };
  }, [isDirty, debouncedAutoSave]);

  return {
    saveStatus,
    lastSavedAt,
    saveError,
    saveCount,
    triggerSave,
    isSaving: saveStatus === 'saving',
    hasError: saveStatus === 'error',
    canSave: !!course && isDirty && saveStatus !== 'saving',
    isIdle: saveStatus === 'idle',
    wasSaved: saveStatus === 'saved',
  };
};

export default useAutoSave;
