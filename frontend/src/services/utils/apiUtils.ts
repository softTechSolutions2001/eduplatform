/**
 * File: src/services/utils/apiUtils.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Utility functions for API operations
 */

import { logWarning } from '../../utils/logger';
import { camelToSnake, objectToSnakeFormData, snakeToCamel } from '../../utils/transformData';
import { CONTENT_CACHE_TTL } from '../http/constants';

export const createFormData = data => {
    const formData = new FormData();
    const snakeData = camelToSnake(data);

    Object.entries(snakeData).forEach(([key, value]) => {
        if (value instanceof File) {
            formData.append(key, value);
        } else if (Array.isArray(value)) {
            value.forEach(item => {
                formData.append(`${key}[]`, item);
            });
        } else if (value !== null && typeof value === 'object') {
            formData.append(key, JSON.stringify(value));
        } else if (value !== null && value !== undefined) {
            formData.append(key, value);
        }
    });

    return formData;
};

export const contentCache = {
    isOptedOut: () => {
        try {
            return localStorage.getItem('content_cache_opt_out') === 'true';
        } catch (e) {
            return false;
        }
    },

    setOptOut: optOut => {
        try {
            localStorage.setItem('content_cache_opt_out', optOut ? 'true' : 'false');
        } catch (e) {
            logWarning('Could not set content cache preference', { error: e });
        }
    },

    set: (key, data) => {
        if (contentCache.isOptedOut()) return false;

        try {
            const cacheData = {
                data,
                timestamp: new Date().toISOString(),
            };
            localStorage.setItem(key, JSON.stringify(cacheData));
            return true;
        } catch (e) {
            logWarning('Failed to cache content:', { error: e });
            return false;
        }
    },

    get: key => {
        if (contentCache.isOptedOut()) return null;

        try {
            const cachedData = localStorage.getItem(key);
            if (!cachedData) return null;

            const parsed = JSON.parse(cachedData);

            const cacheTime = new Date(parsed.timestamp).getTime();
            const now = new Date().getTime();
            if (now - cacheTime > CONTENT_CACHE_TTL) {
                localStorage.removeItem(key);
                return null;
            }

            return parsed.data;
        } catch (e) {
            logWarning('Failed to retrieve cached content:', { error: e });
            return null;
        }
    },

    clearAll: () => {
        try {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('content_cache_')) {
                    localStorage.removeItem(key);
                }
            });
        } catch (e) {
            logWarning('Failed to clear cached content:', { error: e });
        }
    },
};

export const apiUtils = {
    snakeToCamel,
    camelToSnake,
    createFormData,
    contentCache,

    // Expose FormData utility function from transformData
    objectToSnakeFormData,

    // Check if data is a special type that shouldn't be transformed
    isSpecialType: (data) => {
        return data instanceof FormData ||
            data instanceof File ||
            data instanceof Blob ||
            data instanceof ArrayBuffer;
    },

    // Format data for API request (handles case conversion)
    formatRequestData: (data) => {
        if (!data || apiUtils.isSpecialType(data)) {
            return data;
        }
        return camelToSnake(data);
    },

    // Format data from API response (handles case conversion)
    formatResponseData: (data) => {
        if (!data ||
            typeof data !== 'object' ||
            data instanceof Blob ||
            data instanceof ArrayBuffer) {
            return data;
        }
        return snakeToCamel(data);
    },

    isNetworkError: error => {
        return !error.response && error.request;
    },

    isAuthError: error => {
        return error.response && error.response.status === 401;
    },

    formatErrorMessage: error => {
        if (!error) return 'An unknown error occurred';

        if (error.message) return error.message;
        if (error.details?.detail) return error.details.detail;
        if (error.details?.message) return error.details.message;
        if (error.originalError?.message) return error.originalError.message;

        return 'An error occurred while processing your request';
    },
};
