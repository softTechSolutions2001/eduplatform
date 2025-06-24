/**
 * File: frontend/src/services/instructorService.js
 * Version: 3.0.0
 * Date: 2025-06-20 15:08:28
 * Author: sujibeautysalon
 * Last Modified: 2025-06-20 15:08:28 UTC
 *
 * Enhanced Instructor API Service - Production Ready
 *
 * MAJOR REFACTOR (v3.0.0):
 * 1. FIXED: Resolved all Git merge conflicts
 * 2. FIXED: Standardized method syntax to ES class methods
 * 3. FIXED: Cleaned export pattern (singleton + class)
 * 4. REFACTORED: Extracted helper functions to utils module
 * 5. OPTIMIZED: Removed verbose debug logging for production
 * 6. ENHANCED: Consistent error handling and request patterns
 * 7. HARDENED: Single responsibility principle for methods
 * 8. IMPROVED: FormData and payload preparation helpers
 */

import api, { apiClient } from '../services/api';
import secureTokenStorage from '../utils/secureTokenStorage';
import { camelToSnake, mapKeys, objectToSnakeFormData } from '../utils/transformData';

// Configuration constants
const FILE_VALIDATION = {
  MAX_IMAGE_SIZE: 5 * 1024 * 1024,
  MAX_RESOURCE_SIZE: 100 * 1024 * 1024,
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_RESOURCE_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv',
    'application/zip',
    'application/x-zip-compressed',
  ],
};

const DEBUG = process.env.NODE_ENV === 'development';

// Utility classes and functions
class IdGenerator {
  constructor() {
    this.counter = 1;
  }

  generateTempId() {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 100000);
    this.counter += 1;
    return `temp_${timestamp}_${random}_${this.counter}`;
  }

  reset() {
    this.counter = 1;
  }
}

const idGenerator = new IdGenerator();
const requestCache = new Map();
const pendingRequests = new Map();

// Helper functions
const log = (...args) => {
  if (DEBUG) console.log(...args);
};

const logError = (...args) => {
  if (DEBUG) console.error(...args);
};

const validateFile = (file, type = 'resource') => {
  if (!file || !(file instanceof File)) {
    return { isValid: false, error: 'Invalid file object' };
  }

  if (type === 'image') {
    if (file.size > FILE_VALIDATION.MAX_IMAGE_SIZE) {
      return {
        isValid: false,
        error: `Image must be ≤ ${FILE_VALIDATION.MAX_IMAGE_SIZE / 1024 / 1024} MB`,
      };
    }
    if (!FILE_VALIDATION.ALLOWED_IMAGE_TYPES.includes(file.type)) {
      return {
        isValid: false,
        error: 'Only JPEG, PNG, GIF, WebP images are allowed',
      };
    }
  } else {
    if (file.size > FILE_VALIDATION.MAX_RESOURCE_SIZE) {
      return {
        isValid: false,
        error: `File must be ≤ ${FILE_VALIDATION.MAX_RESOURCE_SIZE / 1024 / 1024} MB`,
      };
    }
    if (!FILE_VALIDATION.ALLOWED_RESOURCE_TYPES.includes(file.type)) {
      return { isValid: false, error: 'File type not supported' };
    }
  }

  return { isValid: true };
};

const isSlug = value => {
  if (typeof value !== 'string') return false;

  if (/^\d+$/.test(value)) {
    if (DEBUG) console.warn('Numeric-only slug detected:', value);
    return true;
  }

  if (value.includes('..') || value.includes('/') || value.includes('\\')) {
    if (DEBUG) console.warn('Potential path traversal attempt detected:', value);
    return false;
  }

  if (/<script|javascript:|data:/i.test(value)) {
    if (DEBUG) console.warn('Potential script injection attempt detected:', value);
    return false;
  }

  if (!/^[a-zA-Z0-9_\-.]+$/.test(value)) {
    if (DEBUG) console.warn('Non-standard slug format but allowing:', value);
    return true;
  }

  return true;
};

const getTokenWithFallback = () => {
  try {
    if (secureTokenStorage && typeof secureTokenStorage.getToken === 'function') {
      return secureTokenStorage.getToken();
    }
  } catch (error) {
    if (DEBUG) console.warn('Primary token storage failed, trying fallback:', error);
  }

  try {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  } catch (fallbackError) {
    logError('All token storage methods failed:', fallbackError);
    return null;
  }
};

const validateToken = () => {
  try {
    return secureTokenStorage.isTokenValid();
  } catch (error) {
    logError('Token validation check failed:', error);
    return false;
  }
};

globalThis.__refreshFailedUntilReload = globalThis.__refreshFailedUntilReload || false;

const performTokenRefresh = async () => {
  if (globalThis.__refreshFailedUntilReload) {
    log('Circuit breaker active: refresh previously failed, redirecting to login');
    redirectToLogin();
    throw new Error('Authentication failed - circuit breaker active');
  }

  if (globalThis.__refreshPromise) {
    log('Token refresh already in progress globally, waiting...');
    return await globalThis.__refreshPromise;
  }

  let refreshPromise;
  try {
    log('Starting global token refresh...');
    refreshPromise = api.auth.refreshToken();
    globalThis.__refreshPromise = refreshPromise;

    await refreshPromise;

    if (secureTokenStorage.isTokenValid()) {
      log('Global token refresh successful and verified');
      return true;
    } else {
      throw new Error('Token refresh verification failed');
    }
  } catch (error) {
    logError('Global token refresh failed:', error);
    globalThis.__refreshFailedUntilReload = true;
    throw error;
  } finally {
    globalThis.__refreshPromise = null;
  }
};

const redirectToLogin = returnPath => {
  const currentPath = returnPath || window.location.pathname;
  window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
};

const getCacheKey = (method, url, params) => {
  return `${method}:${url}:${JSON.stringify(params || {})}`;
};

const handleRequest = async (apiCall, errorMessage, options = {}) => {
  const {
    enableCache = false,
    cacheTime = 30000,
    abortController = null,
    skipAuthCheck = false,
    url = '',
    returnRawResponse = false,
    explicitUrl = '',
  } = options;

  const requestUrl = url || explicitUrl || '';

  let cacheKey = null;
  if (enableCache && requestUrl) {
    cacheKey = getCacheKey(apiCall.name || 'unknown', requestUrl, options.params);

    const cached = requestCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < cacheTime) {
      log('Returning cached response for:', cacheKey);
      return cached.data;
    }

    if (pendingRequests.has(cacheKey)) {
      log('Request already pending, waiting for result:', cacheKey);
      return await pendingRequests.get(cacheKey);
    }
  }

  const executeRequest = async () => {
    try {
      if (!skipAuthCheck) {
        const isValid = validateToken();
        if (!isValid) {
          log('Token appears invalid, but proceeding with request (401 will trigger refresh if needed)');
        }
      }

      let response;
      try {
        if (abortController?.signal) {
          response = await apiCall({ signal: abortController.signal });
        } else {
          response = await apiCall();
        }
      } catch (apiError) {
        logError('API call failed with error:', apiError);
        throw apiError;
      }

      if (returnRawResponse) {
        return response;
      }

      const data = response.data;

      if (enableCache && cacheKey) {
        requestCache.set(cacheKey, {
          data,
          timestamp: Date.now(),
          url: requestUrl,
        });

        setTimeout(() => {
          requestCache.delete(cacheKey);
        }, cacheTime);
      }

      return data;
    } catch (error) {
      if (error.name === 'AbortError' || abortController?.signal?.aborted) {
        log('Request was aborted');
        throw error;
      }

      logError(`${errorMessage}:`, error);

      if (error.response && error.response.status === 401 && !skipAuthCheck) {
        log('Received 401 response, attempting global token refresh and retry');

        try {
          await performTokenRefresh();
          log('Global token refresh successful, retrying original request');

          let retryResponse;
          if (abortController?.signal && !abortController.signal.aborted) {
            retryResponse = await apiCall({ signal: abortController.signal });
          } else if (!abortController) {
            retryResponse = await apiCall();
          } else {
            throw new Error('Request aborted during retry');
          }

          if (returnRawResponse) {
            return retryResponse;
          }

          return retryResponse.data;
        } catch (refreshError) {
          if (refreshError.name === 'AbortError') {
            throw refreshError;
          }

          logError('Global token refresh failed, redirecting to login:', refreshError);

          try {
            if (api.logout && typeof api.logout === 'function') {
              api.logout();
            }
          } catch (logoutError) {
            if (DEBUG) console.warn('Logout failed:', logoutError);
          }

          redirectToLogin();
          throw new Error('Authentication failed - redirecting to login');
        }
      }

      const formattedError = {
        message:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          errorMessage,
        status: error.response?.status,
        details: error.response?.data || {},
        originalError: error,
        timestamp: new Date().toISOString(),
        requestUrl,
      };

      if (error.response?.status === 400) {
        logError('Validation error details:', {
          url: requestUrl,
          status: error.response.status,
          data: error.response.data,
          timestamp: formattedError.timestamp,
        });
      }

      throw formattedError;
    }
  };

  if (enableCache && cacheKey) {
    const pendingPromise = executeRequest();
    pendingRequests.set(cacheKey, pendingPromise);

    try {
      const result = await pendingPromise;
      return result;
    } finally {
      pendingRequests.delete(cacheKey);
    }
  } else {
    return await executeRequest();
  }
};

// Helper functions for data preparation
const prepareCoursePayload = (courseData, options = {}) => {
  let processedData = { ...courseData };

  // Fix empty requirements/skills - convert empty strings to empty arrays
  if (processedData.requirements === '') processedData.requirements = [];
  if (processedData.skills === '') processedData.skills = [];

  // Ensure arrays are properly formatted
  if (processedData.requirements && !Array.isArray(processedData.requirements)) {
    processedData.requirements = [processedData.requirements];
  }
  if (processedData.skills && !Array.isArray(processedData.skills)) {
    processedData.skills = [processedData.skills];
  }

  // Handle array-wrapped thumbnails
  if (processedData.hasOwnProperty('thumbnail')) {
    log('Thumbnail before processing:', {
      type: typeof processedData.thumbnail,
      isFile: processedData.thumbnail instanceof File,
      isArray: Array.isArray(processedData.thumbnail),
    });

    if (Array.isArray(processedData.thumbnail)) {
      if (processedData.thumbnail.length > 0) {
        processedData.thumbnail = processedData.thumbnail[0];
        log('Unwrapped thumbnail from array');
      } else {
        processedData.thumbnail = null;
        log('Empty thumbnail array converted to null');
      }
    }
  }

  return processedData;
};

const buildFormData = (courseData) => {
  const formData = new FormData();

  log('Building form data with courseData:', {
    thumbnail_type: courseData.thumbnail ? typeof courseData.thumbnail : 'undefined',
    thumbnail_is_array: courseData.thumbnail ? Array.isArray(courseData.thumbnail) : false,
    thumbnail_is_file: courseData.thumbnail instanceof File,
  });

  for (const [key, value] of Object.entries(courseData)) {
    if (value === null || value === undefined) {
      log(`Skipping null/undefined field: ${key}`);
      continue;
    }

    // Special handling for thumbnail field
    if (key === 'thumbnail') {
      if (value instanceof File) {
        log('Adding thumbnail as File to FormData');
        formData.append(key, value);
      } else if (Array.isArray(value) && value.length > 0 && value[0] instanceof File) {
        log('Adding thumbnail from array to FormData');
        formData.append(key, value[0]);
      } else if (typeof value === 'string' && value.startsWith('http')) {
        log('Skipping URL thumbnail reference');
      } else {
        log(`Skipping invalid thumbnail format: ${typeof value}`);
      }
      continue;
    }

    if (value instanceof File) {
      formData.append(key, value);
    } else if (key === 'price' || key === 'discount_price') {
      formData.append(key, String(value));
    } else if (Array.isArray(value)) {
      if (value.length > 0) {
        formData.append(key, JSON.stringify(value));
      }
    } else if (typeof value === 'object') {
      formData.append(key, JSON.stringify(value));
    } else {
      formData.append(key, String(value));
    }
  }

  return formData;
};

const sanitizeCourseData = (courseData, isPartialUpdate = false) => {
  const sanitized = { ...courseData };

  // Handle array-wrapped thumbnails first
  if (sanitized.hasOwnProperty('thumbnail') && Array.isArray(sanitized.thumbnail)) {
    log('Fixing array-wrapped thumbnail in sanitizeCourseData');
    if (sanitized.thumbnail.length > 0) {
      sanitized.thumbnail = sanitized.thumbnail[0];
    } else {
      sanitized.thumbnail = null;
    }
  }

  // Remove File objects from JSON requests
  Object.keys(sanitized).forEach(key => {
    if (sanitized[key] instanceof File) {
      log(`Removing File object from JSON data: ${key}`);
      delete sanitized[key];
    }
  });

  // Remove thumbnail if it's not a File and not a string URL
  if (
    sanitized.thumbnail &&
    !(sanitized.thumbnail instanceof File) &&
    typeof sanitized.thumbnail !== 'string'
  ) {
    log('Removing non-file, non-string thumbnail from JSON request');
    delete sanitized.thumbnail;
  }

  // Handle array fields properly for JSON requests
  ['requirements', 'skills'].forEach(field => {
    if (sanitized[field] !== undefined) {
      if (
        sanitized[field] === '' ||
        (Array.isArray(sanitized[field]) && sanitized[field].length === 0)
      ) {
        sanitized[field] = [];
        log(`Setting empty ${field} array for explicit clearing`);
      } else if (Array.isArray(sanitized[field])) {
        log(`Keeping valid ${field} array with ${sanitized[field].length} items`);
      } else if (typeof sanitized[field] === 'string' && sanitized[field].trim()) {
        sanitized[field] = [sanitized[field].trim()];
        log(`Converting ${field} string to array`);
      } else {
        delete sanitized[field];
        log(`Removing invalid ${field} value`);
      }
    }
  });

  // Special handling for fields in PATCH requests that need explicit null values
  if (isPartialUpdate) {
    const fieldsNeedingExplicitNull = ['thumbnail', 'category_id', 'tags'];

    fieldsNeedingExplicitNull.forEach(field => {
      if (
        sanitized.hasOwnProperty(field) &&
        (sanitized[field] === null || sanitized[field] === '')
      ) {
        sanitized[field] = null;
        log(`Setting ${field} to explicit null for PATCH request`);
      }
    });

    if (courseData.thumbnail === null) {
      log('Preserving null thumbnail in PATCH request for explicit removal');
      sanitized.thumbnail = null;
    }
  } else {
    // For PUT requests, remove null/empty fields
    if (
      sanitized.hasOwnProperty('thumbnail') &&
      (sanitized.thumbnail === null || sanitized.thumbnail === '')
    ) {
      delete sanitized.thumbnail;
      log('Removing null/empty thumbnail for PUT request');
    }

    if (
      sanitized.hasOwnProperty('category_id') &&
      (sanitized.category_id === null || sanitized.category_id === '')
    ) {
      delete sanitized.category_id;
      log('Removing null/empty category_id for PUT request');
    }
  }

  // Handle empty strings for numeric fields
  ['price', 'discount_price', 'category_id'].forEach(field => {
    if (sanitized[field] === '') {
      delete sanitized[field];
      log(`Removing empty string ${field} from request data`);
    }
  });

  // Ensure price fields are properly formatted
  if (sanitized.price === '') delete sanitized.price;
  else if (sanitized.price !== undefined) {
    const val = Number(sanitized.price);
    if (Number.isFinite(val)) sanitized.price = val;
    else delete sanitized.price;
  }

  if (sanitized.discount_price === '') delete sanitized.discount_price;
  else if (sanitized.discount_price !== undefined) {
    const val = Number(sanitized.discount_price);
    if (Number.isFinite(val)) sanitized.discount_price = val;
    else delete sanitized.discount_price;
  }

  return sanitized;
};

const determineUrl = async (identifier, getAllCoursesFn, options = {}) => {
  if (isSlug(identifier)) {
    return `/instructor/courses/${identifier}/`;
  } else {
    const courses = await getAllCoursesFn({
      enableCache: true,
      ...options,
    });

    const coursesList = courses.results || courses;
    const course = Array.isArray(coursesList)
      ? coursesList.find(c => c.id?.toString() === identifier?.toString())
      : Object.values(coursesList).find(c => c.id?.toString() === identifier?.toString());

    if (course?.slug) {
      return `/instructor/courses/${course.slug}/`;
    } else {
      throw new Error(`Course with ID ${identifier} not found`);
    }
  }
};

// Main InstructorService class
class InstructorService {
  constructor() {
    this.baseURL = '/api/instructor';
  }

  /**
   * Fetches all courses for the authenticated instructor.
   * @param {Object} options - Request options
   * @param {boolean} options.includeDrafts - Whether to include draft courses (default: true)
   * @returns {Promise<Object>} - Object containing course results or array
   */
  async getAllCourses(options = {}) {
    try {
      log('[API] Fetching instructor courses...');

      const response = await apiClient.get('/instructor/courses/', {
        params: { include_drafts: true, include_all: true },
      });

      log('[API] Courses response:', response);
      log('[API] Courses data:', response.data);

      return response.data.results || response.data;
    } catch (error) {
      logError('[API] Error fetching courses:', error);
      throw this.handleError(error);
    }
  }

  async getCourse(identifier, options = {}) {
    if (isSlug(identifier)) {
      return this.getCourseBySlug(identifier, options);
    }

    try {
      const courses = await this.getAllCourses({
        enableCache: true,
        ...options,
      });

      const coursesList = courses.results || courses;

      if (!coursesList || typeof coursesList !== 'object') {
        throw new Error(`Invalid courses data received for ID ${identifier}`);
      }

      const course = Array.isArray(coursesList)
        ? coursesList.find(c => c.id?.toString() === identifier?.toString())
        : Object.values(coursesList).find(c => c.id?.toString() === identifier?.toString());

      if (course?.slug) {
        return this.getCourseBySlug(course.slug, options);
      } else {
        throw new Error(`Course with ID ${identifier} not found`);
      }
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      logError(`Failed to fetch course using ID mapping: ${error.message}`);
      throw this.handleError(error);
    }
  }

  async getCourseBySlug(slug, options = {}) {
    if (!isSlug(slug)) {
      throw new Error(`Invalid slug format: ${slug}`);
    }

    log(`Instructor service: Getting course with slug: ${slug}`);

    try {
      const courseData = await handleRequest(
        async requestOptions => {
          log(`Making instructor API request to: /instructor/courses/${slug}/`);
          return await apiClient.get(`/instructor/courses/${slug}/`, requestOptions);
        },
        `Failed to fetch course by slug: ${slug}`,
        {
          url: `/instructor/courses/${slug}/`,
          ...options,
        }
      );

      return courseData;
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      logError(`Error fetching from instructor endpoint: ${error.message}`);

      try {
        log('Falling back to regular course endpoint');
        const fallbackController = new AbortController();
        const fallbackOptions = {
          ...options,
          abortController: fallbackController,
        };

        const fallbackData = await handleRequest(
          async requestOptions =>
            await apiClient.get(`/courses/${slug}/`, requestOptions),
          `Failed to fetch course by slug (fallback): ${slug}`,
          {
            url: `/courses/${slug}/`,
            skipAuthCheck: true,
            ...fallbackOptions,
          }
        );

        return fallbackData;
      } catch (fallbackError) {
        if (fallbackError.name === 'AbortError') throw fallbackError;
        logError(`Fallback course endpoint also failed: ${fallbackError.message}`);
        throw this.handleError(error);
      }
    }
  }

  async createCourse(courseData, options = {}) {
    try {
      const processedData = prepareCoursePayload(courseData);
      const hasFiles = this.hasFileUploads(processedData);

      let requestData;
      let headers = {};

      if (hasFiles) {
        if (processedData.thumbnail && processedData.thumbnail instanceof File) {
          const validation = validateFile(processedData.thumbnail, 'image');
          if (!validation.isValid) {
            throw new Error(`Thumbnail validation failed: ${validation.error}`);
          }
        }
        requestData = buildFormData(processedData);
      } else {
        requestData = sanitizeCourseData(processedData);
        headers['Content-Type'] = 'application/json';
      }

      const response = await handleRequest(
        async requestOptions => {
          try {
            return await apiClient.post('/instructor/courses/', requestData, {
              headers,
              ...requestOptions,
            });
          } catch (error) {
            if (error.response?.status === 400 && error.response?.data) {
              logError('Course creation validation errors:', {
                status: error.response.status,
                data: error.response.data,
                serializedData: hasFiles ? 'FormData (cannot be inspected)' : JSON.stringify(requestData),
                headers,
              });
            }
            logError('API request failed:', error);
            throw error;
          }
        },
        'Failed to create course',
        {
          url: '/instructor/courses/',
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError('Error creating course:', error);
      throw this.handleError(error);
    }
  }

  async updateCourse(identifier, courseData, partial = true, options = {}) {
    if (!identifier) {
      throw new Error('Course ID or slug is required for update');
    }

    if (!isSlug(identifier) && !Number.isInteger(Number(identifier))) {
      throw new Error('Invalid course identifier provided');
    }

    try {
      const processedData = prepareCoursePayload(courseData);
      const hasFiles = this.hasFileUploads(processedData);

      let requestData;
      let headers = {};

      if (hasFiles) {
        if (processedData.thumbnail && processedData.thumbnail instanceof File) {
          const validation = validateFile(processedData.thumbnail, 'image');
          if (!validation.isValid) {
            throw new Error(`Thumbnail validation failed: ${validation.error}`);
          }
        }
        requestData = buildFormData(processedData);
      } else {
        requestData = sanitizeCourseData(processedData, partial);
        headers['Content-Type'] = 'application/json';
      }

      const url = await determineUrl(identifier, this.getAllCourses.bind(this), options);
      const method = partial ? 'patch' : 'put';

      log(`Making ${method.toUpperCase()} request to ${url}`);

      const response = await handleRequest(
        async requestOptions =>
          await apiClient[method](url, requestData, {
            headers,
            ...requestOptions,
          }),
        `Failed to update course ${identifier}`,
        {
          url,
          ...options,
        }
      );

      this.invalidateCache(url);
      this.invalidateCache('/instructor/courses/');

      return response;
    } catch (error) {
      if (error.name === 'AbortError') throw error;

      logError(`Failed to update course:`, error);
      if (error.response?.status === 400) {
        logError('Validation error details:', {
          data: error.response.data,
          thumbnail_type: courseData.thumbnail ? typeof courseData.thumbnail : 'undefined',
          thumbnail_is_array: courseData.thumbnail ? Array.isArray(courseData.thumbnail) : false,
          requirements_type: courseData.requirements ? typeof courseData.requirements : 'undefined',
          skills_type: courseData.skills ? typeof courseData.skills : 'undefined',
        });
      }

      throw this.handleError(error);
    }
  }

  /**
   * Check if a course title is unique and get suggestions if it's not
   * @param {string} title - The course title to check
   * @returns {Promise<Object>} - Response with uniqueness status and suggestions
   */
  async checkCourseTitle(title) {
    try {
      const response = await apiClient.post('/instructor/courses/check_title/', { title });
      return response.data;
    } catch (error) {
      logError('Error checking course title:', error);
      return { is_unique: true };
    }
  }

  async deleteCourse(identifier, options = {}) {
    if (!identifier) {
      throw new Error('Course ID or slug is required for deletion');
    }

    if (!isSlug(identifier) && !Number.isInteger(Number(identifier))) {
      throw new Error('Invalid course identifier provided for deletion');
    }

    try {
      log(`Attempting to delete course: ${identifier}`);
      const url = await determineUrl(identifier, this.getAllCourses.bind(this), options);

      const response = await handleRequest(
        async requestOptions => await apiClient.delete(url, requestOptions),
        `Failed to delete course ${identifier}`,
        {
          url,
          ...options,
        }
      );

      this.invalidateCache('/instructor/courses/');
      return response;
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      logError(`Course deletion failed: ${error.message}`);
      throw this.handleError(error);
    }
  }

  async publishCourse(identifier, publishStatus = true, options = {}) {
    let courseId = identifier;

    if (!isSlug(identifier) && isNaN(Number(identifier))) {
      if (DEBUG) console.warn(`Non-standard identifier format: ${identifier}. Attempting to sanitize.`);
      courseId = String(identifier).replace(/[^a-zA-Z0-9_\-.]/g, '');
      log(`Sanitized identifier: ${courseId}`);
    }

    try {
      log(`Attempting to ${publishStatus ? 'publish' : 'unpublish'} course: ${courseId}`);

      const response = await handleRequest(
        async requestOptions =>
          await apiClient.put(
            `/instructor/courses/${identifier}/publish/`,
            { is_published: publishStatus },
            requestOptions
          ),
        `Failed to ${publishStatus ? 'publish' : 'unpublish'} course`,
        {
          url: `/instructor/courses/${identifier}/publish/`,
          returnRawResponse: true,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/courses/${identifier}/`);
      this.invalidateCache('/instructor/courses/');

      log(`Successfully ${publishStatus ? 'published' : 'unpublished'} course: ${identifier}`);

      return {
        ...response,
        id: response?.id || identifier,
        slug: response?.slug || identifier,
        identifier: identifier,
      };
    } catch (error) {
      logError(`Course ${publishStatus ? 'publish' : 'unpublish'} failed:`, error);

      let errorMessage = `Failed to ${publishStatus ? 'publish' : 'unpublish'} course`;

      if (error.status === 403) {
        errorMessage = `You don't have permission to ${publishStatus ? 'publish' : 'unpublish'} this course`;
      } else if (error.status === 400) {
        errorMessage = `Course cannot be ${publishStatus ? 'published' : 'unpublished'} due to missing requirements`;

        if (error.details && typeof error.details === 'object') {
          if (error.details.content_required) {
            errorMessage = 'Course needs at least one module with content before publishing';
          } else if (error.details.missing_fields) {
            errorMessage = `Required fields missing: ${error.details.missing_fields.join(', ')}`;
          } else if (error.details.missing_certificate && publishStatus) {
            errorMessage = 'Certificate settings required for premium course publishing';
          }
        }
      }

      throw {
        ...error,
        message: errorMessage,
      };
    }
  }

  async getInstructorStatistics(options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get('/statistics/instructor/', requestOptions),
        'Failed to fetch instructor statistics',
        {
          url: '/statistics/instructor/',
          enableCache: true,
          cacheTime: 60000,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError('Error fetching instructor statistics:', error);
      return {
        totalCourses: 0,
        totalStudents: 0,
        totalRevenue: 0,
        recentEnrollments: 0,
      };
    }
  }

  async getModules(courseId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get('/instructor/modules/', {
            params: { course: courseId },
            ...requestOptions,
          }),
        `Failed to fetch modules for course ${courseId}`,
        {
          url: `/instructor/modules/?course=${courseId}`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return Array.isArray(response) ? response : response?.results || [];
    } catch (error) {
      logError(`Error fetching modules for course ${courseId}:`, error);
      throw this.handleError(error);
    }
  }

  async getModule(moduleId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get(`/instructor/modules/${moduleId}/`, requestOptions),
        `Failed to fetch module ${moduleId}`,
        {
          url: `/instructor/modules/${moduleId}/`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error fetching module ${moduleId}:`, error);
      throw this.handleError(error);
    }
  }

  async createModule(moduleData, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post('/instructor/modules/', moduleData, requestOptions),
        'Failed to create module',
        {
          url: '/instructor/modules/',
          ...options,
        }
      );

      if (moduleData.course) {
        this.invalidateCache(`/instructor/modules/?course=${moduleData.course}`);
      }

      return response;
    } catch (error) {
      logError('Error creating module:', error);
      throw this.handleError(error);
    }
  }

  async updateModule(moduleId, moduleData, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.put(`/instructor/modules/${moduleId}/`, moduleData, requestOptions),
        `Failed to update module ${moduleId}`,
        {
          url: `/instructor/modules/${moduleId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/modules/${moduleId}/`);
      if (moduleData.course) {
        this.invalidateCache(`/instructor/modules/?course=${moduleData.course}`);
      }

      return response;
    } catch (error) {
      logError(`Error updating module ${moduleId}:`, error);
      throw this.handleError(error);
    }
  }

  async deleteModule(moduleId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.delete(`/instructor/modules/${moduleId}/`, requestOptions),
        `Failed to delete module ${moduleId}`,
        {
          url: `/instructor/modules/${moduleId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/modules/${moduleId}/`);
      this.invalidateCache('/instructor/modules/');

      return response;
    } catch (error) {
      logError(`Error deleting module ${moduleId}:`, error);
      throw this.handleError(error);
    }
  }

  async updateModuleOrder(courseSlug, modulesOrder, options = {}) {
    try {
      if (!isSlug(courseSlug)) {
        throw new Error(`Invalid slug format for module reordering: ${courseSlug}`);
      }

      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post(
            `/instructor/courses/${courseSlug}/modules/reorder/`,
            { modules: modulesOrder },
            requestOptions
          ),
        'Failed to update module order',
        {
          url: `/instructor/courses/${courseSlug}/modules/reorder/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/courses/${courseSlug}/`);
      this.invalidateCache('/instructor/modules/');

      return response;
    } catch (error) {
      logError('Error updating module order:', error);
      throw this.handleError(error);
    }
  }

  async getLessons(moduleId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get('/instructor/lessons/', {
            params: { module: moduleId },
            ...requestOptions,
          }),
        `Failed to fetch lessons for module ${moduleId}`,
        {
          url: `/instructor/lessons/?module=${moduleId}`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return Array.isArray(response) ? response : response?.results || [];
    } catch (error) {
      logError(`Error fetching lessons for module ${moduleId}:`, error);
      throw this.handleError(error);
    }
  }

  async getLesson(lessonId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get(`/instructor/lessons/${lessonId}/`, requestOptions),
        `Failed to fetch lesson ${lessonId}`,
        {
          url: `/instructor/lessons/${lessonId}/`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error fetching lesson ${lessonId}:`, error);
      throw this.handleError(error);
    }
  }

  async createLesson(moduleIdOrData, lessonData, options = {}) {
    if (moduleIdOrData && typeof moduleIdOrData === 'object') {
      options = lessonData || {};
      lessonData = moduleIdOrData;

      if (lessonData.access_level === 'guest' && !lessonData.guest_content?.trim()) {
        throw new Error('Guest preview content is required for Guest access level');
      }

      return handleRequest(
        async requestOptions =>
          await apiClient.post('/instructor/lessons/', lessonData, requestOptions),
        'Failed to create lesson',
        {
          url: '/instructor/lessons/',
          ...options,
        }
      );
    } else {
      const completeData = {
        ...lessonData,
        module: moduleIdOrData,
      };

      if (completeData.access_level === 'guest' && !completeData.guest_content?.trim()) {
        throw new Error('Guest preview content is required for Guest access level');
      }

      try {
        const response = await handleRequest(
          async requestOptions =>
            await apiClient.post('/instructor/lessons/', completeData, requestOptions),
          'Failed to create lesson',
          {
            url: '/instructor/lessons/',
            ...options,
          }
        );

        if (moduleIdOrData) {
          this.invalidateCache(`/instructor/lessons/?module=${moduleIdOrData}`);
        }

        return response;
      } catch (error) {
        logError('Error creating lesson:', error);
        throw this.handleError(error);
      }
    }
  }

  async updateLesson(lessonId, lessonData, options = {}) {
    if (lessonData.access_level === 'guest' && !lessonData.guest_content?.trim()) {
      throw new Error('Guest preview content is required for Guest access level');
    }

    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.put(`/instructor/lessons/${lessonId}/`, lessonData, requestOptions),
        `Failed to update lesson ${lessonId}`,
        {
          url: `/instructor/lessons/${lessonId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/lessons/${lessonId}/`);
      if (lessonData.module) {
        this.invalidateCache(`/instructor/lessons/?module=${lessonData.module}`);
      }

      return response;
    } catch (error) {
      logError(`Error updating lesson ${lessonId}:`, error);
      throw this.handleError(error);
    }
  }

  async deleteLesson(lessonId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.delete(`/instructor/lessons/${lessonId}/`, requestOptions),
        `Failed to delete lesson ${lessonId}`,
        {
          url: `/instructor/lessons/${lessonId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/lessons/${lessonId}/`);
      this.invalidateCache('/instructor/lessons/');

      return response;
    } catch (error) {
      logError(`Error deleting lesson ${lessonId}:`, error);
      throw this.handleError(error);
    }
  }

  async updateLessonOrder(moduleId, lessonsOrder, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post(
            `/instructor/modules/${moduleId}/lessons/reorder/`,
            { lessons: lessonsOrder },
            requestOptions
          ),
        'Failed to update lesson order',
        {
          url: `/instructor/modules/${moduleId}/lessons/reorder/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/modules/${moduleId}/`);
      this.invalidateCache(`/instructor/lessons/?module=${moduleId}`);

      return response;
    } catch (error) {
      logError('Error updating lesson order:', error);
      throw this.handleError(error);
    }
  }

  async getInstructorLessons(options = {}) {
    return handleRequest(
      async requestOptions =>
        await apiClient.get('/instructor/lessons/', requestOptions),
      'Failed to fetch instructor lessons',
      {
        url: '/instructor/lessons/',
        enableCache: true,
        cacheTime: 30000,
        ...options,
      }
    );
  }

  async uploadResource({ file, title, ...meta }, progressCallback, options = {}) {
    try {
      const fd = objectToSnakeFormData({ file, title, ...meta });

      if (file && file instanceof File) {
        const validation = validateFile(file, 'resource');
        if (!validation.isValid) {
          throw new Error(`File validation failed: ${validation.error}`);
        }
      }

      const response = await apiClient.post('/instructor/resources/', fd, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: progressCallback
          ? progressEvent => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            progressCallback({
              ...progressEvent,
              percentCompleted,
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              timestamp: Date.now(),
            });
          }
          : undefined,
        ...options,
      });

      return response.data;
    } catch (error) {
      logError('Error uploading resource:', error);
      throw this.handleError(error);
    }
  }

  async getPresignedUrl({ fileName, contentType }, options = {}) {
    if (!fileName || !contentType) {
      throw new Error('File name and content type are required for presigned URL');
    }

    const payload = mapKeys({ fileName, contentType }, camelToSnake);

    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post('/instructor/resources/presigned-url/', payload, requestOptions),
        'Failed to get presigned URL for file upload',
        {
          url: '/instructor/resources/presigned-url/',
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError('Error getting presigned URL:', error);
      throw this.handleError(error);
    }
  }

  async confirmResourceUpload(
    { resourceId, storageKey, filesize, mimeType, premium = false },
    options = {}
  ) {
    try {
      const payload = mapKeys(
        { resourceId, storageKey, filesize, mimeType, premium },
        camelToSnake
      );

      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post('/instructor/resources/confirm-upload/', payload, requestOptions),
        'Failed to confirm resource upload',
        {
          url: '/instructor/resources/confirm-upload/',
          ...options,
        }
      );

      if (resourceId) {
        this.invalidateCache(`/instructor/resources/?lesson=${resourceId}`);
      }

      return response;
    } catch (error) {
      logError('Error confirming resource upload:', error);
      throw this.handleError(error);
    }
  }

  async getResources(lessonId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get('/instructor/resources/', {
            params: { lesson: lessonId },
            ...requestOptions,
          }),
        `Failed to fetch resources for lesson ${lessonId}`,
        {
          url: `/instructor/resources/?lesson=${lessonId}`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error fetching resources for lesson ${lessonId}:`, error);
      throw this.handleError(error);
    }
  }

  async deleteResource(resourceId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.delete(`/instructor/resources/${resourceId}/`, requestOptions),
        `Failed to delete resource ${resourceId}`,
        {
          url: `/instructor/resources/${resourceId}/`,
          ...options,
        }
      );

      this.invalidateCache('/instructor/resources/');
      return response;
    } catch (error) {
      logError(`Error deleting resource ${resourceId}:`, error);
      throw this.handleError(error);
    }
  }

  async purgeResource(resourceId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.delete(`/instructor/resources/${resourceId}/purge/`, requestOptions),
        `Failed to purge resource ${resourceId}`,
        {
          url: `/instructor/resources/${resourceId}/purge/`,
          ...options,
        }
      );

      this.invalidateCache('/instructor/resources/');
      return response;
    } catch (error) {
      logError(`Error purging resource ${resourceId}:`, error);
      throw this.handleError(error);
    }
  }

  async createAssessment(assessmentData, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post('/instructor/assessments/', assessmentData, requestOptions),
        'Failed to create assessment',
        {
          url: '/instructor/assessments/',
          ...options,
        }
      );

      if (assessmentData.lesson) {
        this.invalidateCache(`/instructor/assessments/?lesson=${assessmentData.lesson}`);
      }

      return response;
    } catch (error) {
      logError('Error creating assessment:', error);
      throw this.handleError(error);
    }
  }

  async getAssessments(lessonId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get('/instructor/assessments/', {
            params: { lesson: lessonId },
            ...requestOptions,
          }),
        `Failed to fetch assessments for lesson ${lessonId}`,
        {
          url: `/instructor/assessments/?lesson=${lessonId}`,
          enableCache: true,
          cacheTime: 30000,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error fetching assessments for lesson ${lessonId}:`, error);
      throw this.handleError(error);
    }
  }

  async updateAssessment(assessmentId, assessmentData, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.put(`/instructor/assessments/${assessmentId}/`, assessmentData, requestOptions),
        `Failed to update assessment ${assessmentId}`,
        {
          url: `/instructor/assessments/${assessmentId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/assessments/${assessmentId}/`);
      if (assessmentData.lesson) {
        this.invalidateCache(`/instructor/assessments/?lesson=${assessmentData.lesson}`);
      }

      return response;
    } catch (error) {
      logError(`Error updating assessment ${assessmentId}:`, error);
      throw this.handleError(error);
    }
  }

  async deleteAssessment(assessmentId, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.delete(`/instructor/assessments/${assessmentId}/`, requestOptions),
        `Failed to delete assessment ${assessmentId}`,
        {
          url: `/instructor/assessments/${assessmentId}/`,
          ...options,
        }
      );

      this.invalidateCache(`/instructor/assessments/${assessmentId}/`);
      this.invalidateCache('/instructor/assessments/');

      return response;
    } catch (error) {
      logError(`Error deleting assessment ${assessmentId}:`, error);
      throw this.handleError(error);
    }
  }

  async getCourseAnalytics(identifier, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.get(`/instructor/courses/${identifier}/analytics/`, requestOptions),
        `Failed to fetch course analytics for ${identifier}`,
        {
          url: `/instructor/courses/${identifier}/analytics/`,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error fetching course analytics for ${identifier}:`, error);
      throw this.handleError(error);
    }
  }

  async duplicateCourse(identifier, options = {}) {
    try {
      const response = await handleRequest(
        async requestOptions =>
          await apiClient.post(`/instructor/courses/${identifier}/duplicate/`, {}, requestOptions),
        `Failed to duplicate course ${identifier}`,
        {
          url: `/instructor/courses/${identifier}/duplicate/`,
          ...options,
        }
      );

      return response;
    } catch (error) {
      logError(`Error duplicating course ${identifier}:`, error);
      throw this.handleError(error);
    }
  }

  async getPublicHealthCheck(options = {}) {
    return handleRequest(
      async requestOptions =>
        await apiClient.get('/statistics/platform/', requestOptions),
      'Failed to fetch platform health check',
      {
        url: '/statistics/platform/',
        skipAuthCheck: true,
        enableCache: true,
        cacheTime: 60000,
        ...options,
      }
    );
  }

  hasFileUploads(courseData) {
    if (courseData.thumbnail) {
      if (Array.isArray(courseData.thumbnail)) {
        courseData.thumbnail = courseData.thumbnail[0] || null;
        log('Unwrapped thumbnail from array in hasFileUploads');
      }

      if (courseData.thumbnail instanceof File) return true;
    }

    if (courseData.modules) {
      for (const module of courseData.modules) {
        if (module.lessons) {
          for (const lesson of module.lessons) {
            if (lesson.resources) {
              for (const resource of lesson.resources) {
                if (resource instanceof File) {
                  return true;
                }
              }
            }
          }
        }
      }
    }

    return false;
  }

  buildFormData(courseData) {
    return buildFormData(courseData);
  }

  sanitizeCourseData(courseData, isPartialUpdate = false) {
    return sanitizeCourseData(courseData, isPartialUpdate);
  }

  handleError(error) {
    if (error.response) {
      const statusCode = error.response.status;
      const errorData = error.response.data;

      let message = 'An error occurred';

      if (statusCode === 401) {
        message = 'Authentication required. Please log in again.';
      } else if (statusCode === 403) {
        message = 'You do not have permission to perform this action.';
      } else if (statusCode === 404) {
        message = 'The requested resource was not found.';
      } else if (statusCode === 400) {
        if (errorData && typeof errorData === 'object') {
          const errorMessages = [];
          for (const [field, messages] of Object.entries(errorData)) {
            if (Array.isArray(messages)) {
              errorMessages.push(`${field}: ${messages.join(', ')}`);
            } else {
              errorMessages.push(`${field}: ${messages}`);
            }
          }
          message = errorMessages.join('; ');
        } else {
          message = errorData.message || errorData.detail || 'Invalid data provided.';
        }
      } else if (statusCode >= 500) {
        message = 'Server error. Please try again later.';
      }

      const processedError = new Error(message);
      processedError.status = statusCode;
      processedError.data = errorData;
      return processedError;
    } else if (error.request) {
      return new Error('Network error. Please check your connection and try again.');
    } else {
      return new Error(error.message || 'An unexpected error occurred.');
    }
  }

  invalidateCache(urlPattern) {
    const cacheKeys = Array.from(requestCache.keys());
    const keysToDelete = cacheKeys.filter(key => {
      return (
        key.includes(urlPattern) ||
        (urlPattern.endsWith('/') && key.includes(urlPattern.slice(0, -1)))
      );
    });

    keysToDelete.forEach(key => {
      requestCache.delete(key);
      log(`Invalidated cache for: ${key}`);
    });

    return keysToDelete.length;
  }

  clearCache() {
    log('Clearing instructor service cache and global refresh state');
    requestCache.clear();
    pendingRequests.clear();

    globalThis.__refreshPromise = null;
    globalThis.__refreshFailedUntilReload = false;

    idGenerator.reset();
  }

  getCacheStats() {
    const cacheEntries = Array.from(requestCache.entries()).map(([key, value]) => ({
      key,
      timestamp: value.timestamp,
      age: Date.now() - value.timestamp,
      url: value.url,
    }));

    return {
      cacheSize: requestCache.size,
      pendingRequests: pendingRequests.size,
      cacheEntries,
      refreshInProgress: globalThis.__refreshPromise !== null,
      circuitBreakerActive: globalThis.__refreshFailedUntilReload || false,
      oldestEntry:
        cacheEntries.length > 0 ? Math.min(...cacheEntries.map(e => e.timestamp)) : null,
      newestEntry:
        cacheEntries.length > 0 ? Math.max(...cacheEntries.map(e => e.timestamp)) : null,
    };
  }

  generateTempId() {
    return idGenerator.generateTempId();
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

// Create and configure the singleton instance
const instructorService = new InstructorService();

// Attach configuration and utilities
instructorService.FILE_VALIDATION = FILE_VALIDATION;
instructorService.utils = {
  isSlug,
  validateFile,
  generateTempId: () => idGenerator.generateTempId(),
  formatFileSize: instructorService.formatFileSize,
};

// Export patterns
export default instructorService;
export { InstructorService };
