/**
 * File Path: frontend/src/courseBuilder/api/courseBuilderAPI.ts
 * Version: 2.5.4
 * Date Created: 2025-06-14 15:05:58
 * Date Revised: 2025-06-14 16:36:16
 * Author: sujibeautysalon
 * Last Modified By: sujibeautysalon
 * Last Modified: 2025-06-14 16:36:16 UTC
 * User: sujibeautysalon
 *
 * Enhanced Course Builder API Client with Resilient Network Management
 *
 * This module provides a comprehensive API client for the course builder with
 * advanced error handling, retry logic, and network resilience features.
 *
 * Key Features:
 * - Course CRUD operations with versioning support
 * - Module and lesson management with proper ordering
 * - Content publishing and draft handling
 * - Course cloning and version control
 * - Template-based course creation
 * - Title uniqueness validation with fallback
 * - File upload support with progress tracking
 * - AbortSignal support for all requests
 * - Exponential backoff retry logic
 * - Centralized auth token management
 * - Deep camelCase conversion for nested objects
 * - Comprehensive error handling with user-friendly messages
 *
 * Version 2.5.4 Changes (Critical Bug Fixes):
 * - FIXED: Django-style query parameters using literal snake_case (title__iexact)
 * - FIXED: FormData fields using proper snake_case keys (is_draft)
 * - FIXED: Module stripping to prevent modules_json from reaching backend
 * - FIXED: __DEV__ global declaration for TypeScript compatibility
 * - MAINTAINED: All existing functionality without introducing new errors
 *
 * Connected Files:
 * - frontend/src/courseBuilder/hooks/useAutoSave.ts - Uses API for autosave
 * - frontend/src/courseBuilder/store/courseSlice.ts - State management
 * - frontend/src/utils/secureTokenStorage.js - Token management
 * - frontend/src/utils/buildCourseFormData.ts - FormData serialization
 * - frontend/src/courseBuilder/utils/caseConvert.ts - Key case conversion
 */

import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import secureTokenStorage from '../../utils/secureTokenStorage';
import { camelToSnake, snakeToCamel } from '../utils/caseConvert';
import { pick } from '../utils/object';

// ✅ FIXED: Global __DEV__ declaration for TypeScript compatibility
declare const __DEV__: boolean;

// ✅ Type augmentation for axios config metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: { requestId: string; startTime: number };
  }
}

// ✅ Enhanced mapKeysDeep implementation for nested object conversion
const mapKeysDeep = <T = any>(
  obj: T,
  transform: (k: string) => string
): T => {
  if (Array.isArray(obj)) {
    return obj.map(v => mapKeysDeep(v, transform)) as unknown as T;
  }

  if (obj && typeof obj === 'object' && obj.constructor === Object) {
    return Object.fromEntries(
      Object.entries(obj).map(([k, v]) => [transform(k), mapKeysDeep(v, transform)])
    ) as T;
  }
  return obj;
};

// ✅ Utility functions for better maintainability
const isRetryableStatus = (status?: number): boolean =>
  [408, 429, 500, 502, 503, 504].includes(status ?? 0);

// ✅ FIXED: Renamed to avoid shadowing with exported method
const isClientOnline = (): boolean => {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
};

// ✅ Safe environment variable access utility
const getEnvVar = (key: string, defaultValue: string = ''): string => {
  // Check if we're in a browser environment
  if (typeof window !== 'undefined') {
    // For Vite-based projects
    if (typeof import.meta !== 'undefined' && import.meta.env) {
      return (import.meta.env as any)[key] || defaultValue;
    }

    // For Create React App or Webpack-based projects with injected env vars
    if (typeof (window as any).__ENV__ !== 'undefined') {
      return (window as any).__ENV__[key] || defaultValue;
    }

    // Fallback to checking global variables that might be injected at build time
    if (typeof (window as any)[key] !== 'undefined') {
      return (window as any)[key] || defaultValue;
    }
  }

  // For Node.js environment (SSR, testing, etc.)
  if (typeof process !== 'undefined' && process.env) {
    return process.env[key] || defaultValue;
  }

  return defaultValue;
};

// ✅ Safe development mode detection
const isDevelopment = (): boolean => {
  const nodeEnv = getEnvVar('NODE_ENV', 'production');
  const mode = getEnvVar('MODE', '');
  const dev = getEnvVar('DEV', '');

  return (
    nodeEnv === 'development' ||
    mode === 'development' ||
    dev === 'true' ||
    // Fallback: check if we're on localhost
    (typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname.includes('local')))
  );
};

// ✅ API configuration with safe env access
const API_CONFIG = {
  baseURL: getEnvVar('REACT_APP_API_BASE_URL', '/api'),
  timeout: 30000, // 30 seconds
  retryAttempts: 3,
  retryDelay: 1000, // Base delay for exponential backoff
  maxRetryDelay: 10000, // Maximum retry delay
};

// ✅ Enhanced axios instance without default Content-Type header
const api = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
});

// ✅ Request tracking for concurrent request management
const activeRequests = new Map<string, AbortController>();

// ✅ Enhanced error handling with proper typing
interface APIError extends Error {
  status?: number;
  code?: string;
  details?: Record<string, any>;
  isRetryable?: boolean;
}

const createAPIError = (
  message: string,
  status?: number,
  code?: string,
  details?: Record<string, any>
): APIError => {
  const error = new Error(message) as APIError;
  error.status = status;
  error.code = code;
  error.details = details;
  error.isRetryable = isRetryableStatus(status);
  return error;
};

// ✅ Centralized error unwrapping with real-time network checks
const unwrap = (err: any, defaultMessage = 'Request failed'): never => {
  if (axios.isCancel(err)) {
    throw createAPIError('Request was cancelled', 0, 'REQUEST_CANCELLED');
  }

  // Real-time network status check
  if (!isClientOnline()) {
    throw createAPIError('No internet connection', 0, 'NETWORK_OFFLINE');
  }

  const response = err?.response as AxiosResponse | undefined;

  if (!response) {
    // Network error or timeout
    if (err.code === 'ECONNABORTED') {
      throw createAPIError('Request timeout', 0, 'TIMEOUT');
    }
    if (err.code === 'ERR_NETWORK') {
      throw createAPIError('Network error', 0, 'NETWORK_ERROR');
    }
    throw createAPIError(defaultMessage, 0, 'UNKNOWN_ERROR');
  }

  const { status, data } = response;

  // Extract error message from response
  let errorMessage = defaultMessage;
  let errorDetails: Record<string, any> = {};

  if (typeof data === 'string') {
    errorMessage = data;
  } else if (data && typeof data === 'object') {
    if (data.detail) {
      errorMessage = data.detail;
    } else if (data.message) {
      errorMessage = data.message;
    } else if (data.error) {
      errorMessage = data.error;
    } else {
      // Handle field-level errors
      const fieldErrors = Object.entries(data)
        .filter(([key, value]) => key !== 'detail' && key !== 'message')
        .map(([field, errors]) => {
          const errorList = Array.isArray(errors) ? errors : [errors];
          return `${field}: ${errorList.join(', ')}`;
        });

      if (fieldErrors.length > 0) {
        errorMessage = fieldErrors.join('; ');
        errorDetails = data;
      }
    }
  }

  throw createAPIError(errorMessage, status, `HTTP_${status}`, errorDetails);
};

// ✅ Fixed exponential backoff retry logic with proper error detection
const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxAttempts: number = API_CONFIG.retryAttempts
): Promise<T> => {
  let lastError: any;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await requestFn();
    } catch (error: any) {
      lastError = error;

      // Don't retry if request was cancelled
      if (axios.isCancel(error) || attempt === maxAttempts) {
        break;
      }

      // Properly check retryable status from AxiosError
      const status = (error as AxiosError)?.response?.status;
      const retryable = error.isRetryable ?? isRetryableStatus(status);

      if (!retryable) {
        break;
      }

      // Calculate delay with exponential backoff and jitter
      const baseDelay = API_CONFIG.retryDelay * Math.pow(2, attempt - 1);
      const jitter = Math.random() * 0.1 * baseDelay; // 10% jitter
      const delay = Math.min(baseDelay + jitter, API_CONFIG.maxRetryDelay);

      // ✅ FIXED: Safe development logging with fallback
      if (typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment()) {
        console.log(`Retrying request (attempt ${attempt}/${maxAttempts}) after ${delay}ms`);
      }
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
};

// ✅ Enhanced request interceptor with comprehensive parameter conversion
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // ✅ FIXED: Improved type safety for headers
    config.headers ||= {};

    // Set default Content-Type for non-FormData requests
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
    }

    // Add authentication token
    const token = secureTokenStorage.getValidToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // ✅ FIXED: Convert query parameters to snake_case for proper API filtering
    if (config.params) {
      config.params = mapKeysDeep(config.params, camelToSnake);
    }

    // Convert camelCase to snake_case for non-FormData requests
    if (config.data && !(config.data instanceof FormData)) {
      config.data = mapKeysDeep(config.data, camelToSnake);
    }

    // ✅ FIXED: Handle per-call Content-Type override for FormData
    if (config.data instanceof FormData) {
      // Remove Content-Type header to let browser set it with boundary
      delete config.headers['Content-Type'];
    }

    // Add request ID for tracking
    const requestId = `${config.method?.toLowerCase()}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    config.metadata = { requestId, startTime: Date.now() };

    // ✅ FIXED: Safe development logging with fallback
    if (typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment()) {
      console.log(`🚀 API Request [${requestId}]:`, {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        headers: config.headers,
        params: config.params,
        data: config.data instanceof FormData ? '[FormData]' : config.data,
      });
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// ✅ Enhanced response interceptor with deep conversion and logging
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Convert snake_case to camelCase
    if (response.data) {
      response.data = mapKeysDeep(response.data, snakeToCamel);
    }

    // ✅ FIXED: Safe development logging with fallback
    const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
    if (devMode && response.config.metadata) {
      const duration = Date.now() - response.config.metadata.startTime;
      console.log(`✅ API Response [${response.config.metadata.requestId}] (${duration}ms):`, {
        status: response.status,
        statusText: response.statusText,
        data: response.data,
      });
    }

    return response;
  },
  (error: AxiosError) => {
    // ✅ FIXED: Safe development logging with fallback
    const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
    if (devMode && error.config?.metadata) {
      const duration = Date.now() - error.config.metadata.startTime;
      console.error(`❌ API Error [${error.config.metadata.requestId}] (${duration}ms):`, {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
      });
    }

    return Promise.reject(error);
  }
);

// ✅ Request cancellation utilities with memory leak prevention
const cancelRequest = (requestId: string) => {
  const controller = activeRequests.get(requestId);
  if (controller) {
    controller.abort();
    activeRequests.delete(requestId);
  }
};

const createCancellableRequest = (requestId: string, signal?: AbortSignal): AbortController => {
  // Cancel existing request with same ID
  cancelRequest(requestId);

  const controller = new AbortController();
  activeRequests.set(requestId, controller);

  // Prevent memory leak with proper event listener cleanup
  if (signal) {
    const onAbort = () => controller.abort();
    signal.addEventListener('abort', onAbort, { once: true });
  }

  return controller;
};

// ✅ Pending reorder controller with proper tracking
let pendingReorder: AbortController | null = null;
export const cancelReorder = () => {
  if (pendingReorder) {
    pendingReorder.abort();
    activeRequests.delete('reorder-modules'); // Clean up from tracking
    pendingReorder = null;
  }
};

/**
 * Generate alternative title suggestions
 */
function generateTitleAlternatives(title: string): string[] {
  const userFullName = 'You';
  const currentYear = new Date().getFullYear();

  const suggestions = [
    `${title} by ${userFullName}`,
    `${title} (${currentYear})`,
    `${title} - Advanced`,
    `${userFullName}'s ${title}`,
    `${title} - Complete Guide`,
    `Mastering ${title}`,
  ];

  return suggestions.map(suggestion =>
    suggestion.length > 160 ? suggestion.substring(0, 157) + '...' : suggestion
  );
}

// ✅ Production-ready API methods with all critical fixes applied
export default {
  /**
   * Check title uniqueness with enhanced fallback handling
   */
  checkTitleUniqueness: async (title: string, options: AxiosRequestConfig = {}) => {
    const requestId = `check-title-${title}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Checking if title is unique:', title);
      }

      const checkUniqueness = async (endpoint: string, params: any) => {
        const response = await api.get(endpoint, {
          params,
          signal: controller.signal,
          ...options,
        });

        const courses = response.data?.results || response.data || [];
        const titleExists = Array.isArray(courses) && courses.length > 0;

        return {
          available: !titleExists,
          alternatives: titleExists ? generateTitleAlternatives(title) : [],
        };
      };

      try {
        // ✅ FIXED: Use literal snake_case to avoid conversion issues
        return await retryRequest(() =>
          checkUniqueness('/instructor/courses/', { title__iexact: title })
        );
      } catch (error: any) {
        // Fallback to public courses route only on 404
        if (error.status === 404) {
          const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
          if (devMode) {
            console.log('Instructor route not found, trying public courses route');
          }
          return await retryRequest(() =>
            checkUniqueness('/courses/', { title__iexact: title })
          );
        }
        throw error;
      }
    } catch (error: any) {
      if (axios.isCancel(error)) {
        return { available: true, alternatives: [] };
      }

      if (error.status === 401) {
        throw createAPIError('Authentication required. Please log in again.', 401, 'AUTH_REQUIRED');
      } else if (error.status === 429) {
        throw createAPIError('Too many requests. Please try again in a moment.', 429, 'RATE_LIMITED');
      } else {
        console.warn('Error in title uniqueness check, assuming title is unique');
        return { available: true, alternatives: [] };
      }
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Create a draft course with enhanced error handling
   */
  createDraft: async (title: string = 'Untitled', options: AxiosRequestConfig = {}) => {
    const requestId = 'create-draft';
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const courseData = {
        title,
        description: 'Draft course description. To be updated.',
        isDraft: true,
      };

      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Creating course with data:', courseData);
      }

      return await retryRequest(async () => {
        const response = await api.post('/instructor/courses/', courseData, {
          signal: controller.signal,
          ...options,
        });
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to create draft course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Create course from FormData
   */
  createCourse: async (formData: FormData, options: AxiosRequestConfig = {}) => {
    const requestId = 'create-course';
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      return await retryRequest(async () => {
        const response = await api.post('/instructor/courses/', formData, {
          signal: controller.signal,
          ...options,
        });
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to create course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Create course from template
   */
  createFromTemplate: async (templateId: string, options: AxiosRequestConfig = {}) => {
    const requestId = `create-from-template-${templateId}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log(`Creating course from template: ${templateId}`);
      }

      return await retryRequest(async () => {
        const response = await api.post(
          '/instructor/courses/create_from_template/',
          { templateId },
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to create course from template');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Clone course version
   */
  cloneVersion: async (slug: string, options: AxiosRequestConfig = {}) => {
    const requestId = `clone-version-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Creating new draft version for course:', slug);
      }

      return await retryRequest(async () => {
        const response = await api.post(
          `/instructor/courses/${slug}/clone/`,
          {},
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to clone course version');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Update course (JSON data)
   */
  updateCourse: async (slug: string, courseData: any, options: AxiosRequestConfig = {}) => {
    const requestId = `update-course-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      // ✅ FIXED: Strip both camelCase and snake_case module fields
      const { modules, modulesJson, modules_json, ...courseDataWithoutModules } = courseData;

      if (modules || modulesJson || modules_json) {
        console.warn('PATCH /course should not include modules; use reorderModules instead');
      }

      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Updating course without modules:', courseDataWithoutModules);
      }

      return await retryRequest(async () => {
        const response = await api.patch(
          `/instructor/courses/${slug}/`,
          courseDataWithoutModules,
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to update course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Enhanced FormData update with proper header handling
   */
  updateCourseFormData: async (slug: string, formData: FormData, options: AxiosRequestConfig = {}) => {
    const requestId = `update-course-formdata-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      // ✅ FIXED: Use proper snake_case key for FormData
      if (!formData.has('is_draft')) {
        formData.append('is_draft', 'true');
      }

      return await retryRequest(async () => {
        const response = await api.patch(
          `/instructor/courses/${slug}/`,
          formData,
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to update course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Update course tracking data
   */
  updateCourseTracking: async (slug: string, trackingData: any, options: AxiosRequestConfig = {}) => {
    const requestId = `update-tracking-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const data = pick(trackingData, [
        'completionStatus',
        'completionPercentage',
        'creationMethod',
      ]);

      const response = await api.put(
        `/instructor/courses/${slug}/update_tracking/`,
        data,
        {
          signal: controller.signal,
          ...options,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error updating course tracking:', error);
      return null; // Fail silently for tracking
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Get course by slug
   */
  getCourse: async (slug: string, options: AxiosRequestConfig = {}) => {
    const requestId = `get-course-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      return await retryRequest(async () => {
        const response = await api.get(`/instructor/courses/${slug}/`, {
          signal: controller.signal,
          ...options,
        });
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to load course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Get modules for a course
   */
  getModules: async (courseSlug: string, options: AxiosRequestConfig = {}) => {
    const requestId = `get-modules-${courseSlug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Fetching modules for course slug:', courseSlug);
      }

      return await retryRequest(async () => {
        const response = await api.get(`/instructor/courses/${courseSlug}/modules/`, {
          signal: controller.signal,
          ...options,
        });
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to load modules');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Create module with simplified single signature
   */
  createModule: async (
    courseId: number,
    moduleData: any,
    options: AxiosRequestConfig = {}
  ) => {
    const requestId = `create-module-${courseId}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const { order, ...moduleDataWithoutOrder } = moduleData;

      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Creating module for course:', courseId, moduleDataWithoutOrder);
      }

      return await retryRequest(async () => {
        const response = await api.post(
          '/instructor/modules/',
          {
            ...moduleDataWithoutOrder,
            course: courseId,
          },
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to create module');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Create a new lesson
   */
  createLesson: async (moduleId: string | number, lessonData: any, options: AxiosRequestConfig = {}) => {
    const requestId = `create-lesson-${moduleId}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
      if (devMode) {
        console.log('Creating lesson with data:', JSON.stringify(lessonData));
      }

      if (!lessonData.content || lessonData.content.trim() === '') {
        lessonData.content = '<p>Default lesson content.</p>';
      }

      const requestData = {
        title: lessonData.title || 'New Lesson',
        module: moduleId,
        content: lessonData.content,
        guestContent: lessonData.guestContent || '',
        registeredContent: lessonData.registeredContent || '',
        type: lessonData.type || 'reading',
        order: lessonData.order || 1,
        accessLevel: lessonData.accessLevel || 'registered',
        durationMinutes: lessonData.durationMinutes || 15,
        hasAssessment: lessonData.hasAssessment || false,
        hasLab: lessonData.hasLab || false,
        isFreePreview: lessonData.isFreePreview || false,
      };

      if (devMode) {
        console.log('Formatted request data:', JSON.stringify(requestData));
      }

      return await retryRequest(async () => {
        const response = await api.post('/instructor/lessons/', requestData, {
          signal: controller.signal,
          ...options,
        });
        if (devMode) {
          console.log('Lesson creation response:', response.data);
        }
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to create lesson');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Enhanced reorderModules with proper request tracking
   */
  reorderModules: async (slug: string, ids: (string | number)[], options: AxiosRequestConfig = {}) => {
    const requestId = 'reorder-modules';

    try {
      // Filter out temporary IDs before sending to backend
      const safeIds = ids.filter(id => typeof id === 'number');

      // Cancel any pending reorder
      cancelReorder();
      pendingReorder = new AbortController();

      // Add to active requests tracking
      activeRequests.set(requestId, pendingReorder);

      // Link external signal if provided
      if (options.signal) {
        const onAbort = () => pendingReorder?.abort();
        options.signal.addEventListener('abort', onAbort, { once: true });
      }

      return await retryRequest(async () => {
        const response = await api.post(
          `/instructor/courses/${slug}/modules/reorder/`,
          { modules: safeIds },
          {
            signal: pendingReorder?.signal,
            ...options
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to reorder modules');
    } finally {
      activeRequests.delete(requestId);
      pendingReorder = null;
    }
  },

  /**
   * Reorder lessons within a module
   */
  reorderLessons: async (modId: number, ids: (string | number)[], options: AxiosRequestConfig = {}) => {
    const requestId = `reorder-lessons-${modId}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      // Filter out temporary IDs before sending to backend
      const safeIds = ids.filter(id => typeof id === 'number');

      return await retryRequest(async () => {
        const response = await api.post(
          `/instructor/modules/${modId}/lessons/reorder/`,
          { lessons: safeIds },
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to reorder lessons');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Publish a course
   */
  publish: async (slug: string, options: AxiosRequestConfig = {}) => {
    const requestId = `publish-course-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      return await retryRequest(async () => {
        const response = await api.put(
          `/instructor/courses/${slug}/publish/`,
          {
            isPublished: true,
            isDraft: false,
          },
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to publish course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Unpublish a course
   */
  unpublish: async (slug: string, options: AxiosRequestConfig = {}) => {
    const requestId = `unpublish-course-${slug}`;
    const controller = createCancellableRequest(requestId, options.signal);

    try {
      return await retryRequest(async () => {
        const response = await api.put(
          `/instructor/courses/${slug}/publish/`,
          {
            isPublished: false,
          },
          {
            signal: controller.signal,
            ...options,
          }
        );
        return response.data;
      });
    } catch (error: any) {
      unwrap(error, 'Failed to unpublish course');
    } finally {
      activeRequests.delete(requestId);
    }
  },

  /**
   * Check if course can be edited directly
   */
  canEditDirectly: (courseData: any) => {
    if (courseData.isPublished && !courseData.isDraft) {
      return false;
    }
    return true;
  },

  /**
   * Cancel all active requests
   */
  cancelAllRequests: () => {
    const devMode = typeof __DEV__ !== 'undefined' ? __DEV__ : isDevelopment();
    if (devMode) {
      console.log(`Cancelling ${activeRequests.size} active requests`);
    }
    activeRequests.forEach((controller, requestId) => {
      controller.abort();
    });
    activeRequests.clear();
    cancelReorder();
  },

  /**
   * Get network status and request statistics
   */
  getNetworkStatus: () => ({
    isOnline: isClientOnline(),
    activeRequestCount: activeRequests.size,
  }),

  /**
   * Get environment configuration (for debugging)
   */
  getConfig: () => ({
    baseURL: API_CONFIG.baseURL,
    isDevelopment: isDevelopment(),
    environment: getEnvVar('NODE_ENV', 'unknown'),
  }),
} as const;
