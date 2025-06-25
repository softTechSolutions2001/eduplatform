/**
 * File: src/services/http/constants.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Shared constants for API configuration
 */

// Use the base URL from environment in production, but rely on Vite proxy in development
export const API_BASE_URL =
    process.env.NODE_ENV === 'production'
        ? import.meta.env.VITE_API_BASE_URL || '/api'
        : '/api';

export const TOKEN_STORAGE_KEYS = {
    ACCESS: 'accessToken',
    REFRESH: 'refreshToken',
    USER: 'user',
    PERSISTENCE: 'tokenPersistence',
};

export const DEBUG_MODE =
    import.meta.env.VITE_DEBUG_API === 'true' ||
    process.env.NODE_ENV === 'development';

export const ALLOW_MOCK_FALLBACK =
    import.meta.env.VITE_ALLOW_MOCK_FALLBACK === 'true' || false;

export const REQUEST_TIMEOUT = 15000;
export const CONTENT_CACHE_TTL = 60 * 60 * 1000; // 1 hour in milliseconds
