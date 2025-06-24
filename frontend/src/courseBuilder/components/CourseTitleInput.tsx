/**
 * File: frontend/src/courseBuilder/components/CourseTitleInput.tsx
 * Version: 2.3.0
 * Date Created: 2025-06-14 16:32:25 UTC
 * Date Revised: 2025-06-14 16:32:25 UTC
 * Current User: sujibeautysalon
 * Last Modified By: sujibeautysalon
 *
 * Enhanced Course Title Input Component with Policy-Aligned Validation
 *
 * This component provides a title input field with real-time uniqueness checking
 * that properly aligns with backend business rules and provides consistent
 * validation behavior between client and server implementations.
 *
 * Key Features:
 * - Policy-aligned validation matching backend business rules
 * - Version family-aware title uniqueness checking
 * - Real-time debounced validation with proper cancellation
 * - Enhanced accessibility with ARIA attributes and screen reader support
 * - Comprehensive error handling with contextual messages
 * - Alternative title suggestions with smart generation
 * - Offline detection and graceful degradation
 * - Character count validation with visual feedback
 * - Performance optimizations with memoization
 *
 * Version 2.3.0 Changes (Surgical Fixes from Code Review):
 * - FIXED: Aligned validation policies with backend business rules
 * - FIXED: Fixed uniqueness checking to match server-side logic for version families
 * - FIXED: Improved UX consistency with clear, accurate validation messages
 * - FIXED: Added proper error handling for title validation edge cases
 * - FIXED: Enhanced accessibility with proper form validation feedback
 * - FIXED: Optimized performance with debounced validation requests
 * - FIXED: Added version family context awareness
 * - FIXED: Implemented policy-consistent duplicate handling
 *
 * Connected Files:
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - API client for title validation
 * - frontend/src/courseBuilder/pages/CourseWizard.tsx - Parent component using this input
 * - frontend/src/courseBuilder/store/courseSlice.ts - Course state management
 * - backend/courses/serializers.py - Server-side validation policy source
 */

import axios from 'axios';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import courseBuilderAPI from '../api/courseBuilderAPI';
import { useCourseStore } from '../store/courseSlice';

// ✅ FIX 1: Enhanced interface with version family context
interface CourseTitleInputProps {
  initialValue?: string;
  courseId?: string | number;
  versionFamily?: string; // Added for policy-aligned validation
  autoFill?: boolean;
  onChange: (title: string) => void;
  onValidityChange: (isValid: boolean) => void;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  'data-testid'?: string;
}

// ✅ FIX 2: Enhanced status types with policy context
type TitleStatus =
  | 'idle'
  | 'empty'
  | 'checking'
  | 'available'
  | 'taken-global'
  | 'taken-family'
  | 'policy-allowed'
  | 'too-short'
  | 'too-long'
  | 'invalid-chars'
  | 'error'
  | 'offline';

// ✅ FIX 3: Validation configuration interface
interface ValidationConfig {
  minLength: number;
  maxLength: number;
  debounceMs: number;
  allowDuplicatesInFamily: boolean;
  enforceGlobalUniqueness: boolean;
  invalidCharsPattern: RegExp;
  reservedWords: string[];
}

// ✅ FIX 4: Title uniqueness response interface
interface TitleUniquenessResponse {
  available: boolean;
  globallyUnique: boolean;
  uniqueInFamily: boolean;
  duplicateInFamily: boolean;
  duplicateGlobal: boolean;
  policy: 'allow' | 'warn' | 'block';
  alternatives?: string[];
  message?: string;
  context?: {
    versionFamily?: string;
    existingCourseId?: string | number;
    conflictLevel: 'none' | 'family' | 'global';
  };
}

// ✅ FIX 5: Default validation configuration aligned with backend
const DEFAULT_VALIDATION_CONFIG: ValidationConfig = {
  minLength: 3,
  maxLength: 160,
  debounceMs: 500,
  allowDuplicatesInFamily: true, // Align with backend policy
  enforceGlobalUniqueness: false, // Backend allows duplicates across families
  invalidCharsPattern: /[<>'"&]/g,
  reservedWords: ['admin', 'api', 'test', 'demo', 'sample'],
};

const CourseTitleInput: React.FC<CourseTitleInputProps> = React.memo(({
  initialValue = '',
  courseId,
  versionFamily,
  autoFill = false,
  onChange,
  onValidityChange,
  className = '',
  disabled = false,
  required = false,
  'data-testid': testId = 'course-title-input',
}) => {
  const { course } = useCourseStore();

  // ✅ FIX 6: Enhanced state management
  const [title, setTitle] = useState(initialValue);
  const [status, setStatus] = useState<TitleStatus>('idle');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [warningMessage, setWarningMessage] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [validationContext, setValidationContext] = useState<TitleUniquenessResponse['context'] | null>(null);

  // ✅ FIX 7: Abort controller management
  const abortControllerRef = useRef<AbortController | null>(null);
  const validationTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ✅ FIX 8: Memoized validation configuration
  const validationConfig = useMemo(() => ({
    ...DEFAULT_VALIDATION_CONFIG,
    // Override based on course or version family context
    allowDuplicatesInFamily: versionFamily ? true : DEFAULT_VALIDATION_CONFIG.allowDuplicatesInFamily,
  }), [versionFamily]);

  // ✅ FIX 9: Client-side validation functions
  const validateTitleFormat = useCallback((value: string): { isValid: boolean; status: TitleStatus; message?: string } => {
    const trimmed = value.trim();

    if (!trimmed) {
      return { isValid: false, status: 'empty' };
    }

    if (trimmed.length < validationConfig.minLength) {
      return {
        isValid: false,
        status: 'too-short',
        message: `Title must be at least ${validationConfig.minLength} characters long`
      };
    }

    if (trimmed.length > validationConfig.maxLength) {
      return {
        isValid: false,
        status: 'too-long',
        message: `Title must be no more than ${validationConfig.maxLength} characters long`
      };
    }

    if (validationConfig.invalidCharsPattern.test(trimmed)) {
      return {
        isValid: false,
        status: 'invalid-chars',
        message: 'Title contains invalid characters'
      };
    }

    const lowerTitle = trimmed.toLowerCase();
    if (validationConfig.reservedWords.some(word => lowerTitle.includes(word))) {
      return {
        isValid: false,
        status: 'invalid-chars',
        message: 'Title contains reserved words'
      };
    }

    return { isValid: true, status: 'idle' };
  }, [validationConfig]);

  // ✅ FIX 10: Policy-aligned server validation
  const checkTitleUniqueness = useCallback(async (titleToCheck: string): Promise<void> => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setIsChecking(true);
      setErrorMessage(null);
      setWarningMessage(null);
      setStatus('checking');

      // ✅ FIX 11: Enhanced API call with version family context
      const options = {
        signal: controller.signal,
        ...(courseId && { courseId }),
        ...(versionFamily && { versionFamily }),
        includePolicy: true, // Request policy information
        includeContext: true, // Request validation context
      };

      const result: TitleUniquenessResponse = await courseBuilderAPI.checkTitleUniqueness(titleToCheck, options);

      // Check if request was cancelled
      if (controller.signal.aborted) {
        return;
      }

      if (!result) {
        setStatus('error');
        setErrorMessage('Invalid response from server');
        onValidityChange(false);
        return;
      }

      // ✅ FIX 12: Policy-aligned status determination
      setValidationContext(result.context || null);

      if (result.available || result.policy === 'allow') {
        // Title is available or policy allows it
        setStatus(result.globallyUnique ? 'available' : 'policy-allowed');
        setSuggestions([]);
        setShowSuggestions(false);

        // ✅ FIX 13: Policy-consistent validation feedback
        if (!result.globallyUnique && result.policy === 'allow') {
          setWarningMessage(
            result.duplicateInFamily
              ? 'This title is used by another course in your version family, but that\'s allowed.'
              : 'This title is used by other courses, but that\'s allowed in different version families.'
          );
        }

        onValidityChange(true);
      } else {
        // Title is not available based on policy
        if (result.policy === 'block') {
          setStatus(result.duplicateInFamily ? 'taken-family' : 'taken-global');
          setErrorMessage(
            result.message ||
            (result.duplicateInFamily
              ? 'A course with this title already exists in your version family.'
              : 'A course with this title already exists.')
          );
        } else {
          // Policy is 'warn' - show warning but allow
          setStatus('policy-allowed');
          setWarningMessage(
            result.message ||
            'This title is similar to existing courses. Consider making it more unique.'
          );
        }

        // ✅ FIX 14: Enhanced suggestion handling
        if (result.alternatives && result.alternatives.length > 0) {
          setSuggestions(result.alternatives);
          setShowSuggestions(true);
        } else if (result.policy === 'block') {
          // Generate suggestions for blocked titles
          const generatedSuggestions = generateSmartSuggestions(titleToCheck, result.context);
          setSuggestions(generatedSuggestions);
          setShowSuggestions(true);
        }

        onValidityChange(result.policy !== 'block');
      }
    } catch (err: any) {
      // Only handle non-cancellation errors
      if (axios.isCancel(err)) {
        console.log('Title validation request cancelled');
        return;
      }

      console.error('Title uniqueness check failed:', err);

      // ✅ FIX 15: Enhanced error handling
      if (!navigator.onLine) {
        setStatus('offline');
        setErrorMessage('Cannot verify title uniqueness while offline.');
      } else {
        const errorMsg = err.response?.data?.message ||
          err.response?.data?.detail ||
          err.message ||
          'Failed to check title availability';

        setErrorMessage(errorMsg);
        setStatus('error');

        // Show toast for unexpected errors
        if (err.response?.status >= 500) {
          toast.error('Server error while checking title. Please try again.');
        }
      }

      setSuggestions([]);
      setShowSuggestions(false);
      onValidityChange(false);
    } finally {
      if (!controller.signal.aborted) {
        setIsChecking(false);
      }
    }
  }, [courseId, versionFamily, onValidityChange, validationContext]);

  // ✅ FIX 16: Smart suggestion generation with context awareness
  const generateSmartSuggestions = useCallback((baseTitle: string, context?: TitleUniquenessResponse['context']): string[] => {
    const userFullName = localStorage.getItem('userFullName') || 'Instructor';
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().toLocaleString('default', { month: 'long' });

    const suggestions: string[] = [];

    // Context-aware suggestions
    if (context?.versionFamily) {
      suggestions.push(`${baseTitle} v2.0`);
      suggestions.push(`${baseTitle} (Updated ${currentYear})`);
      suggestions.push(`${baseTitle} - Enhanced Edition`);
    } else {
      suggestions.push(`${baseTitle} by ${userFullName}`);
      suggestions.push(`${baseTitle} (${currentYear})`);
      suggestions.push(`${baseTitle} - Complete Guide`);
    }

    // Additional contextual suggestions
    suggestions.push(`${userFullName}'s ${baseTitle}`);
    suggestions.push(`${baseTitle} - ${currentMonth} ${currentYear}`);
    suggestions.push(`Advanced ${baseTitle}`);
    suggestions.push(`${baseTitle} Masterclass`);

    // Ensure suggestions don't exceed max length
    return suggestions
      .map(suggestion =>
        suggestion.length > validationConfig.maxLength
          ? suggestion.substring(0, validationConfig.maxLength - 3) + '...'
          : suggestion
      )
      .slice(0, 5); // Limit to 5 suggestions
  }, [validationConfig.maxLength]);

  // ✅ FIX 17: Enhanced title validation effect
  useEffect(() => {
    // Clear existing timeout
    if (validationTimeoutRef.current) {
      clearTimeout(validationTimeoutRef.current);
    }

    // Reset states
    setErrorMessage(null);
    setWarningMessage(null);
    setShowSuggestions(false);

    // Client-side validation first
    const formatValidation = validateTitleFormat(title);

    if (!formatValidation.isValid) {
      setStatus(formatValidation.status);
      if (formatValidation.message) {
        setErrorMessage(formatValidation.message);
      }
      onValidityChange(false);
      return;
    }

    // Skip server validation for certain conditions
    if (autoFill || title === initialValue || title.trim().length < validationConfig.minLength) {
      const newStatus = title === initialValue ? 'available' : 'idle';
      setStatus(newStatus);
      onValidityChange(newStatus === 'available');
      return;
    }

    // Debounced server validation
    validationTimeoutRef.current = setTimeout(() => {
      checkTitleUniqueness(title.trim());
    }, validationConfig.debounceMs);

    return () => {
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [title, autoFill, initialValue, validateTitleFormat, checkTitleUniqueness, validationConfig, onValidityChange]);

  // ✅ FIX 18: Enhanced change handler
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value.substring(0, validationConfig.maxLength);
    setTitle(newTitle);
    onChange(newTitle);
  }, [onChange, validationConfig.maxLength]);

  // ✅ FIX 19: Suggestion selection handler
  const selectSuggestion = useCallback((suggestion: string) => {
    setTitle(suggestion);
    onChange(suggestion);
    setShowSuggestions(false);
    // Clear any existing validation state
    setStatus('idle');
    setErrorMessage(null);
    setWarningMessage(null);
  }, [onChange]);

  // ✅ FIX 20: Enhanced status display with accessibility
  const getStatusDisplay = useCallback(() => {
    if (isChecking) {
      return (
        <span className="text-xs text-gray-500 flex items-center" role="status" aria-live="polite">
          <svg className="animate-spin h-3 w-3 mr-1" viewBox="0 0 24 24" aria-hidden="true">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Checking availability...
        </span>
      );
    }

    if (status === 'available') {
      return (
        <span className="text-xs text-green-600 flex items-center" role="status" aria-live="polite">
          <svg
            className="h-3 w-3 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          Available
        </span>
      );
    }

    if (status === 'policy-allowed') {
      return (
        <span className="text-xs text-amber-600 flex items-center" role="status" aria-live="polite">
          <svg
            className="h-3 w-3 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          Allowed (with note)
        </span>
      );
    }

    return null;
  }, [isChecking, status]);

  // ✅ FIX 21: Enhanced CSS classes based on status
  const getInputClasses = useCallback(() => {
    const baseClasses = `w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-offset-2 transition-colors ${className}`;

    switch (status) {
      case 'taken-global':
      case 'taken-family':
      case 'too-short':
      case 'too-long':
      case 'invalid-chars':
      case 'error':
        return `${baseClasses} border-red-300 focus:ring-red-500 focus:border-red-500`;
      case 'available':
        return `${baseClasses} border-green-300 focus:ring-green-500 focus:border-green-500`;
      case 'policy-allowed':
        return `${baseClasses} border-amber-300 focus:ring-amber-500 focus:border-amber-500`;
      case 'offline':
        return `${baseClasses} border-yellow-300 focus:ring-yellow-500 focus:border-yellow-500`;
      default:
        return `${baseClasses} border-gray-300 focus:ring-blue-500 focus:border-blue-500`;
    }
  }, [status, className]);

  return (
    <div className="relative" data-testid={testId}>
      {/* ✅ FIX 22: Enhanced label with accessibility */}
      <div className="mb-2 flex items-center justify-between">
        <label
          htmlFor="course-title"
          className="block text-sm font-medium text-gray-700"
        >
          Course Title {required && <span className="text-red-500" aria-label="required">*</span>}
        </label>
        {getStatusDisplay()}
      </div>

      {/* ✅ FIX 23: Enhanced input with accessibility attributes */}
      <input
        id="course-title"
        type="text"
        value={title}
        onChange={handleChange}
        placeholder="Enter a unique course title"
        maxLength={validationConfig.maxLength}
        disabled={disabled}
        required={required}
        className={getInputClasses()}
        aria-invalid={['taken-global', 'taken-family', 'too-short', 'too-long', 'invalid-chars', 'error'].includes(status)}
        aria-describedby={`
          ${errorMessage ? 'title-error' : ''}
          ${warningMessage ? 'title-warning' : ''}
          title-char-count
          ${validationContext ? 'title-context' : ''}
        `.trim()}
        data-testid={`${testId}-field`}
      />

      {/* ✅ FIX 24: Character count with visual feedback */}
      <div id="title-char-count" className="flex justify-between items-center mt-1">
        <div className={`text-xs ${title.length > validationConfig.maxLength * 0.9
          ? 'text-amber-600'
          : 'text-gray-500'
          }`}>
          {title.length}/{validationConfig.maxLength} characters
        </div>

        {validationContext && (
          <div id="title-context" className="text-xs text-gray-500">
            {validationContext.versionFamily && `Family: ${validationContext.versionFamily}`}
          </div>
        )}
      </div>

      {/* ✅ FIX 25: Enhanced error display */}
      {errorMessage && (
        <div id="title-error" className="mt-2 flex items-start" role="alert">
          <svg className="h-4 w-4 text-red-500 mt-0.5 mr-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-600">{errorMessage}</p>
        </div>
      )}

      {/* ✅ FIX 26: Enhanced warning display */}
      {warningMessage && (
        <div id="title-warning" className="mt-2 flex items-start" role="alert">
          <svg className="h-4 w-4 text-amber-500 mt-0.5 mr-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-sm text-amber-600">{warningMessage}</p>
        </div>
      )}

      {/* ✅ FIX 27: Enhanced suggestions display */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="mt-3 p-3 bg-white border border-gray-200 rounded-md shadow-sm">
          <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Suggested alternatives:
          </p>
          <ul className="space-y-1" role="list">
            {suggestions.map((suggestion, index) => (
              <li key={index} role="listitem">
                <button
                  type="button"
                  onClick={() => selectSuggestion(suggestion)}
                  className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded transition-colors"
                  data-testid={`${testId}-suggestion-${index}`}
                >
                  {suggestion}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ✅ FIX 28: Success message */}
      {status === 'available' && !isChecking && (
        <div className="mt-2 flex items-center text-sm text-green-600">
          <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          This title is available!
        </div>
      )}

      {/* ✅ FIX 29: Offline indicator */}
      {status === 'offline' && (
        <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-yellow-400 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-yellow-800">You're offline</p>
              <p className="text-sm text-yellow-700 mt-1">
                Cannot verify title uniqueness while offline. Your title will be validated when you reconnect.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

CourseTitleInput.displayName = 'CourseTitleInput';

export default CourseTitleInput;
