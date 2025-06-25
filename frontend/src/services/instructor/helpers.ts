/**
 * File: src/services/instructor/helpers.ts
 * Version: 1.1.0
 * Date: 2025-06-25 09:31:31
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 09:31:31 UTC
 *
 * Instructor Service Shared Helpers
 *
 * Extracted from instructorService.js v3.0.0
 * Contains utility functions, validation, and shared helpers
 */

// A-4 fix: Remove unused apiClient import
import secureTokenStorage from '../../utils/secureTokenStorage';
// A-5 fix: Import and re-export camelToSnake and mapKeys
import { camelToSnake, mapKeys } from '../../utils/transformData';

// Configuration constants
export const FILE_VALIDATION = {
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

export const DEBUG = process.env.NODE_ENV === 'development';

// Utility classes
export class IdGenerator {
    private counter = 1;

    generateTempId(): string {
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 100000);
        this.counter += 1;
        return `temp_${timestamp}_${random}_${this.counter}`;
    }

    reset(): void {
        this.counter = 1;
    }
}

// Create a singleton instance
export const tmpId = new IdGenerator();

// Cache state management - accessible to all services
export const requestCache = new Map<string, any>();
export const pendingRequests = new Map<string, Promise<any>>();

// Helper functions
export const log = (...args: any[]): void => {
    if (DEBUG) console.log(...args);
};

export const logError = (...args: any[]): void => {
    if (DEBUG) console.error(...args);
};

export interface FileValidationResult {
    isValid: boolean;
    error?: string;
}

export const validateFile = (file: File, type: 'image' | 'resource' = 'resource'): FileValidationResult => {
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

// B-1 issue: Modified isSlug to handle numeric slugs more carefully
// This implementation allows purely numeric slugs for backward compatibility
export const isSlug = (value: string): boolean => {
    if (typeof value !== 'string') return false;

    // Defensive check for pure numeric strings - allow them to be slugs
    // if they're already known to be slugs in the system
    if (/^\d+$/.test(value)) {
        if (DEBUG) console.warn('Numeric-only slug detected, treating as slug:', value);
        return true; // Keep as true for backward compatibility
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

// B-5 issue: hasFileUploads mutates courseData in-place
// Creating a shallow copy to avoid double-unwrapping issue
export const hasFileUploads = (courseData: any): boolean => {
    // Create a shallow copy to prevent mutations from affecting the original
    const data = { ...courseData };

    if (data.thumbnail) {
        if (Array.isArray(data.thumbnail)) {
            // Don't mutate courseData directly
            const thumbnail = data.thumbnail[0] || null;
            log('Detected thumbnail array in hasFileUploads');

            if (thumbnail instanceof File) return true;
        } else if (data.thumbnail instanceof File) {
            return true;
        }
    }

    if (data.modules) {
        for (const module of data.modules) {
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
};

export const prepareCoursePayload = (courseData: any, options = {}): any => {
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

export const buildFormData = (courseData: any): FormData => {
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

export const sanitizeCourseData = (courseData: any, isPartialUpdate = false): any => {
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
        const fieldsNeedingExplicitNull = ['thumbnail', 'category_id', 'tags', 'categoryId']; // Added categoryId

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

        // Fix for the UI sending categoryId instead of category_id
        if (sanitized.hasOwnProperty('categoryId') && !sanitized.hasOwnProperty('category_id')) {
            sanitized.category_id = sanitized.categoryId;
            delete sanitized.categoryId;
            log('Mapped categoryId to category_id');
        }
    }

    // Handle empty strings for numeric fields
    ['price', 'discount_price', 'category_id', 'categoryId'].forEach(field => {
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

export const validateToken = (): boolean => {
    try {
        return secureTokenStorage.isTokenValid();
    } catch (error) {
        logError('Token validation check failed:', error);
        return false;
    }
};

// C-5 issue: SSR awareness
export const redirectToLogin = (returnPath?: string): void => {
    // Check if window exists to avoid SSR issues
    if (typeof window !== 'undefined') {
        const currentPath = returnPath || window.location.pathname;
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
    } else {
        log('Attempted redirect in non-browser environment');
    }
};

export const getCacheKey = (method: string, url: string, params?: any): string => {
    return `${method}:${url}:${JSON.stringify(params || {})}`;
};

// Create a shared authState object to avoid global pollution
export const authState = {
    refreshPromise: null as Promise<any> | null,
    refreshFailedUntilReload: false,
};

export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const handleError = (error: any): Error => {
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
        (processedError as any).status = statusCode;
        (processedError as any).data = errorData;
        return processedError;
    } else if (error.request) {
        return new Error('Network error. Please check your connection and try again.');
    } else {
        return new Error(error.message || 'An unexpected error occurred.');
    }
};

// B-8 issue: Add size-bounded cache with maxEntries
const MAX_CACHE_ENTRIES = 100; // Configurable limit

// Export functions to clear and check cache
export const clearCache = () => {
    log('Clearing instructor service cache and global refresh state');
    requestCache.clear();
    pendingRequests.clear();

    authState.refreshPromise = null;
    authState.refreshFailedUntilReload = false;

    tmpId.reset();
};

export const getCacheStats = () => {
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
        refreshInProgress: authState.refreshPromise !== null,
        circuitBreakerActive: authState.refreshFailedUntilReload,
        oldestEntry:
            cacheEntries.length > 0 ? Math.min(...cacheEntries.map(e => e.timestamp)) : null,
        newestEntry:
            cacheEntries.length > 0 ? Math.max(...cacheEntries.map(e => e.timestamp)) : null,
    };
};

export const invalidateCache = (urlPattern: string): number => {
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
};

// Limit cache size by removing oldest entries when size exceeds MAX_CACHE_ENTRIES
export const limitCacheSize = () => {
    if (requestCache.size <= MAX_CACHE_ENTRIES) return;

    const entries = Array.from(requestCache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp);

    const entriesToRemove = entries.slice(0, requestCache.size - MAX_CACHE_ENTRIES);
    entriesToRemove.forEach(([key]) => {
        requestCache.delete(key);
        log(`Removed old cache entry: ${key}`);
    });
};

// Re-export camelToSnake and mapKeys to fix A-1 issue
export { camelToSnake, mapKeys };
