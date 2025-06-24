/**
 * File: frontend/src/utils/transformData.js
 * Purpose: Utility functions for transforming data between backend and frontend
 * Updated: 2025-08-01, 10:52:16
 *
 * These functions handle the conversion between snake_case (backend) and
 * camelCase (frontend) naming conventions, ensuring compatibility between
 * the two systems, as well as other data transformations needed for course management.
 */

import camelcaseKeys from 'camelcase-keys';
import snakecaseKeys from 'snakecase-keys';

/**
 * Transform object keys based on a transform function
 * @param {Object|Array} data - Object or array to transform
 * @param {Function} transformer - Function to transform keys
 * @returns {Object|Array} - Transformed data
 */
export const mapKeys = (data, transformer) => {
  if (!data) return data;

  // Handle arrays - map each item recursively
  if (Array.isArray(data)) {
    return data.map(item => mapKeys(item, transformer));
  }

  // Handle non-objects
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  // Special handling for Date objects
  if (data instanceof Date) {
    return data;
  }

  // Process regular objects
  const result = {};
  Object.entries(data).forEach(([key, value]) => {
    // Transform the key
    const transformedKey = transformer(key);

    // Handle nested objects and arrays recursively
    if (
      value &&
      typeof value === 'object' &&
      !(value instanceof File) &&
      !(value instanceof Blob) &&
      !(value instanceof FormData)
    ) {
      result[transformedKey] = mapKeys(value, transformer);
    } else {
      result[transformedKey] = value;
    }
  });

  return result;
};

/**
 * Transform backend data (snake_case) to frontend format (camelCase)
 * @param {Object|Array} data - Data from backend API
 * @returns {Object|Array} - Transformed data in camelCase
 */
export const snakeToCamel = data => {
  // Use the mapKeys implementation for better handling of special types
  if (typeof mapKeys === 'function') {
    return mapKeys(data, key => {
      // Convert snake_case to camelCase
      return key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    });
  }
  // Fallback to library implementation
  return camelcaseKeys(data, { deep: true });
};

/**
 * Transform frontend data (camelCase) to backend format (snake_case)
 * @param {Object|Array} data - Data to send to backend API
 * @returns {Object|Array} - Transformed data in snake_case
 */
export const camelToSnake = data => {
  // Use the mapKeys implementation for better handling of special types
  if (typeof mapKeys === 'function') {
    return mapKeys(data, key => {
      // Convert camelCase to snake_case
      return key.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase();
    });
  }
  // Fallback to library implementation
  return snakecaseKeys(data, { deep: true });
};

/**
 * Convert an object to FormData with snake_case keys
 * @param {Object} obj - Object to convert to FormData
 * @returns {FormData} - FormData with snake_case keys
 */
export const objectToSnakeFormData = obj => {
  const formData = new FormData();

  Object.keys(obj).forEach(key => {
    if (obj[key] !== undefined && obj[key] !== null) {
      // Convert key to snake_case
      const snakeKey = camelToSnake(key);

      // Handle File objects and arrays of files specially
      if (obj[key] instanceof File) {
        formData.append(snakeKey, obj[key]);
      } else if (Array.isArray(obj[key]) && obj[key][0] instanceof File) {
        obj[key].forEach(file => formData.append(`${snakeKey}[]`, file));
      } else if (typeof obj[key] === 'object' && !(obj[key] instanceof File)) {
        formData.append(snakeKey, JSON.stringify(camelToSnake(obj[key])));
      } else {
        formData.append(snakeKey, obj[key]);
      }
    }
  });

  return formData;
};

/**
 * Format date to display format
 * @param {string} dateString - ISO date string from backend
 * @returns {string} - Formatted date string
 */
export const formatDate = dateString => {
  if (!dateString) return '';

  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

/**
 * Format price to display format
 * @param {number} price - Price value
 * @returns {string} - Formatted price string
 */
export const formatPrice = price => {
  if (price === 0) return 'Free';

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
};

/**
 * Format duration for display
 * @param {number} minutes - Duration in minutes
 * @returns {string} - Formatted duration string
 */
export const formatDuration = minutes => {
  if (!minutes) return '';

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) {
    return `${mins} min${mins !== 1 ? 's' : ''}`;
  } else if (mins === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  } else {
    return `${hours} hour${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''
      }`;
  }
};

/**
 * Split a string into an array of trimmed, non-empty strings
 * Useful for converting newline-separated text to an array for API calls
 *
 * @param {string|Array} text - String to split or array to return as-is
 * @param {string} delimiter - Delimiter to split on (default: '\n')
 * @returns {Array} - Array of trimmed, non-empty strings
 */
export const splitToList = (text, delimiter = '\n') => {
  if (!text) return [];
  if (Array.isArray(text)) return text;

  // Only operate on real strings to prevent "text.split is not a function" errors
  if (typeof text !== 'string') return [];

  return text
    .split(delimiter)
    .map(item => item.trim())
    .filter(item => item !== '');
};

/**
 * Convert an array of strings to a newline-separated string
 * Useful for displaying array data in textareas
 *
 * @param {Array|string} list - Array to join or string to return as-is
 * @param {string} delimiter - Delimiter to join with (default: '\n')
 * @returns {string} - Joined string
 */
export const listToString = (list, delimiter = '\n') => {
  if (!list) return '';
  if (typeof list === 'string') return list;

  return list.join(delimiter);
};

/**
 * Remove temporary IDs from module and lesson objects
 * Used before sending data to backend to avoid validation errors
 *
 * @param {Object} item - Module or lesson object
 * @returns {Object} - Cleaned object without temporary IDs
 */
export const removeTemporaryId = item => {
  if (!item) return item;

  const result = { ...item };

  // Check if ID is a temporary one
  if (
    result.id &&
    typeof result.id === 'string' &&
    result.id.startsWith('temp_')
  ) {
    result.id = null;
  }

  return result;
};

/**
 * Transform course form data to match backend model format
 * Handles form fields, arrays, and file data
 *
 * @param {Object} formData - Form data from React state
 * @param {File|null} thumbnailFile - File object for course thumbnail
 * @returns {FormData} - FormData object ready to submit to API
 */
export const prepareCourseFormData = (formData, thumbnailFile = null) => {
  const data = new FormData();

  // Basic text fields
  data.append('title', formData.title || '');
  data.append('description', formData.description || '');

  if (formData.subtitle) {
    data.append('subtitle', formData.subtitle);
  }

  // Category
  if (formData.category_id) {
    data.append('category_id', formData.category_id);
  }

  // Level
  if (formData.level) {
    data.append('level', formData.level);
  }

  // Price fields
  data.append('price', formData.price === '' ? '0' : formData.price);

  if (formData.discount_price) {
    data.append('discount_price', formData.discount_price);
  }

  // Boolean fields
  data.append('has_certificate', formData.has_certificate || false);
  data.append('is_featured', formData.is_featured || false);
  if (formData.is_published !== undefined) {
    data.append('is_published', formData.is_published);
  }

  // Array fields - Now using hardened splitToList that handles any input type safely
  const requirements = splitToList(formData.requirements);
  const skills = splitToList(formData.skills);

  if (requirements.length > 0) {
    data.append('requirements', JSON.stringify(requirements));
  }

  if (skills.length > 0) {
    data.append('skills', JSON.stringify(skills));
  }

  // Add thumbnail file if provided
  if (thumbnailFile instanceof File) {
    data.append('thumbnail', thumbnailFile);
  }

  return data;
};

/**
 * Normalize course data coming from backend to frontend format
 * Ensures consistent data structure regardless of API response format
 *
 * @param {Object} courseData - Course data from API
 * @returns {Object} - Normalized course data
 */
export const normalizeCourseData = courseData => {
  if (!courseData) return null;

  return {
    id: courseData.id,
    title: courseData.title || '',
    subtitle: courseData.subtitle || '',
    description: courseData.description || '',
    slug: courseData.slug || null,
    category_id: courseData.category?.id || courseData.category_id || '',
    thumbnail: courseData.thumbnail || null,
    price: courseData.price?.toString() || '0',
    discount_price: courseData.discount_price?.toString() || '',
    level: courseData.level || 'all_levels',
    has_certificate: Boolean(courseData.has_certificate),
    is_featured: Boolean(courseData.is_featured),
    is_published: Boolean(courseData.is_published),
    requirements: Array.isArray(courseData.requirements)
      ? courseData.requirements
      : [],
    skills: Array.isArray(courseData.skills) ? courseData.skills : [],
    // Additional properties
    duration_minutes: courseData.duration_minutes || 0,
    duration_display: courseData.duration_display || '',
    enrollments_count:
      courseData.enrollments_count || courseData.enrolled_students || 0,
    rating: courseData.rating || courseData.avg_rating || 0,
    reviews_count: courseData.reviews_count || 0,
    modules: Array.isArray(courseData.modules) ? courseData.modules : [],
  };
};
