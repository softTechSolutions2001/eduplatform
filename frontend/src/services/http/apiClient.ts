/**
 * File: src/services/http/apiClient.ts
 * Path: src/services/http/apiClient.ts
 * Created: 2025-06-25
 * Last Modified: 2025-06-26 08:10:15
 * Modified By: softTechSolutions2001
 * Version: 1.0.4
 *
 * Axios client configuration and interceptors for API requests
 * Enhanced with improved error handling and TypeScript support
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { logError, logWarning } from '../../utils/logger';
import secureTokenStorage from '../../utils/secureTokenStorage';
import { camelToSnake, objectToSnakeFormData, snakeToCamel } from '../../utils/transformData';
import { DEBUG_MODE, REQUEST_TIMEOUT } from './constants';
import { API_ENDPOINTS } from './endpoints';

// Enhanced interface for custom axios instance
interface CustomAxiosInstance extends AxiosInstance {
    postForm: (url: string, data: any, config?: AxiosRequestConfig) => Promise<AxiosResponse>;
    putForm: (url: string, data: any, config?: AxiosRequestConfig) => Promise<AxiosResponse>;
}

// Get base URL with environment-specific handling and validation
const getBaseURL = (): string => {
    const envBaseURL = import.meta.env.VITE_API_BASE_URL;

    // Production environment requires explicit configuration
    if (process.env.NODE_ENV === 'production') {
        if (!envBaseURL) {
            const errorMsg = 'VITE_API_BASE_URL is required in production. Please configure your environment variables.';
            logError(new Error(errorMsg));
            throw new Error(errorMsg);
        }

        // Validate URL format in production
        try {
            new URL(envBaseURL);
        } catch {
            const errorMsg = `Invalid VITE_API_BASE_URL format: ${envBaseURL}`;
            logError(new Error(errorMsg));
            throw new Error(errorMsg);
        }

        return envBaseURL;
    }

    // Development/staging: fallback to '/api' if not configured
    const baseURL = envBaseURL || '/api';

    if (DEBUG_MODE && !envBaseURL) {
        console.warn('⚠️ VITE_API_BASE_URL not configured, using fallback: /api');
    }

    return baseURL;
};

// Create axios instance with enhanced configuration
export const apiClient = axios.create({
    baseURL: getBaseURL(),
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: REQUEST_TIMEOUT,
    // FIXED: Treat 4xx responses as errors so 405 handler works correctly
    validateStatus: (status: number) => status < 400,
}) as CustomAxiosInstance;

// Add convenience method for multipart/form-data POST requests
apiClient.postForm = function (url: string, data: any, config: AxiosRequestConfig = {}) {
    return this.post(url, objectToSnakeFormData(data), {
        ...config,
        skipTransform: true, // ADDED: Flag to prevent double transformation
        headers: {
            'Content-Type': 'multipart/form-data',
            ...config.headers
        },
    });
};

// Add convenience method for multipart/form-data PUT requests
apiClient.putForm = function (url: string, data: any, config: AxiosRequestConfig = {}) {
    return this.put(url, objectToSnakeFormData(data), {
        ...config,
        skipTransform: true, // ADDED: Flag to prevent double transformation
        headers: {
            'Content-Type': 'multipart/form-data',
            ...config.headers
        },
    });
};

// Token refresh management with proper typing
let refreshTokenPromise: Promise<string> | null = null;

export const refreshAuthToken = async (): Promise<string> => {
    // Prevent concurrent refresh attempts
    if (refreshTokenPromise) {
        return refreshTokenPromise;
    }

    refreshTokenPromise = (async () => {
        try {
            if (DEBUG_MODE) console.log('🔄 Refreshing authentication token');

            const refreshToken = secureTokenStorage.getRefreshToken();
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

            const response = await apiClient.post(
                API_ENDPOINTS.AUTH.REFRESH,
                { refresh: refreshToken },
                {
                    skipAuthRefresh: true,
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: undefined,
                    },
                } as any
            );

            // Enhanced response validation
            if (!response.data?.access) {
                throw new Error('Invalid refresh response: missing access token');
            }

            secureTokenStorage.updateAccessToken(response.data.access);

            if (DEBUG_MODE) console.log('✅ Token refreshed successfully');

            return response.data.access;
        } catch (error) {
            logWarning('Token refresh failed:', { error });

            // Clear stored tokens on refresh failure
            secureTokenStorage.clearAuthData();

            // Dispatch custom event for auth failure handling
            const authFailedEvent = new CustomEvent('auth:failed', {
                detail: { error, timestamp: new Date().toISOString() },
            });
            window.dispatchEvent(authFailedEvent);

            throw error;
        } finally {
            refreshTokenPromise = null;
        }
    })();

    return refreshTokenPromise;
};

// Enhanced data sanitization for logging
function sanitizeLogData(data: any): any {
    if (!data || typeof data !== 'object') return data;

    // Handle arrays
    if (Array.isArray(data)) {
        return data.map(item => sanitizeLogData(item));
    }

    const sanitized = { ...data };

    // Comprehensive list of sensitive fields
    const sensitiveFields = [
        'password', 'token', 'accessToken', 'refreshToken', 'access', 'refresh',
        'access_token', 'refresh_token', 'authorization', 'cardNumber', 'cvv', 'cvc',
        'expiry', 'code_verifier', 'secret', 'key', 'pin', 'otp',
        'verification_code', 'ssn', 'social_security'
    ];

    // IMPROVED: Mask email but preserve domain for debugging
    function maskEmail(email: string): string {
        if (!email || typeof email !== 'string') return email;
        const parts = email.split('@');
        if (parts.length !== 2) return '[REDACTED]';
        return `${parts[0].charAt(0)}***@${parts[1]}`;
    }

    // Recursively sanitize nested objects
    Object.keys(sanitized).forEach(key => {
        const lowerKey = key.toLowerCase();

        if (lowerKey.includes('email')) {
            // Handle email fields specially
            sanitized[key] = maskEmail(sanitized[key]);
        } else if (sensitiveFields.some(field => lowerKey.includes(field))) {
            sanitized[key] = '[REDACTED]';
        } else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
            sanitized[key] = sanitizeLogData(sanitized[key]);
        }
    });

    return sanitized;
}

// Enhanced request interceptor
apiClient.interceptors.request.use(
    (config: any) => {
        // Add request ID for debugging
        config.metadata = { requestId: Math.random().toString(36).substr(2, 9) };

        // Handle authentication
        if (!config.skipAuthRefresh) {
            const token = secureTokenStorage.getValidToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
                secureTokenStorage.refreshTokenExpiry();
            }
        }

        // FIXED: Skip transformation for form data (already handled by postForm/putForm)
        if (
            config.data &&
            typeof config.data === 'object' &&
            !(config.data instanceof FormData) &&
            !(config.data instanceof File) &&
            !(config.data instanceof Blob) &&
            !(config.data instanceof ArrayBuffer) &&
            !config.skipTransform
        ) {
            config.data = camelToSnake(config.data);
        }

        // Enhanced FormData handling
        if (config.data instanceof FormData && !config.skipTransform) {
            const isMultipart = config.headers?.['Content-Type']?.includes('multipart');
            if (isMultipart) {
                const transformedFormData = new FormData();
                config.data.forEach((value: any, key: string) => {
                    transformedFormData.append(camelToSnake(key), value);
                });
                config.data = transformedFormData;
            }
        }

        // Enhanced debug logging
        if (DEBUG_MODE) {
            const method = config.method?.toUpperCase() || 'GET';
            const logData = config.data
                ? sanitizeLogData(config.data)
                : config.params
                    ? sanitizeLogData(config.params)
                    : null;

            console.log(`📤 [${config.metadata.requestId}] ${method} ${config.url}`, logData || '');
        }

        return config;
    },
    (error: any) => {
        if (DEBUG_MODE) {
            console.error('❌ [API REQUEST ERROR]', error);
        }
        logError(error);
        return Promise.reject(error);
    }
);

// Enhanced response interceptor with 405 Method Not Allowed handling
apiClient.interceptors.response.use(
    (response: any) => {
        // Transform response data if it's a serializable object
        if (
            response.data &&
            typeof response.data === 'object' &&
            !(response.data instanceof Blob) &&
            !(response.data instanceof ArrayBuffer) &&
            !(response.data instanceof File)
        ) {
            response.data = snakeToCamel(response.data);
        }

        // Enhanced debug logging
        if (DEBUG_MODE) {
            const requestId = response.config?.metadata?.requestId || 'unknown';
            const logData = response.data ? sanitizeLogData(response.data) : null;
            console.log(`📥 [${requestId}] ${response.status} ${response.config?.url}`, logData || '');
        }

        return response;
    },
    async (error: any) => {
        const originalRequest = error.config;
        const requestId = originalRequest?.metadata?.requestId || 'unknown';

        // Handle 405 Method Not Allowed specifically
        if (error.response?.status === 405) {
            // IMPROVED: Check 'Allow' header to give more accurate guidance
            const allowHeader = error.response.headers?.allow || '';
            const methodsAllowed = allowHeader.split(',').map((m: string) => m.trim());
            const mustBeGet = methodsAllowed.includes('GET');
            const mustBePost = methodsAllowed.includes('POST');

            let userMessage: string;
            if (mustBeGet) {
                userMessage = 'This endpoint is read-only (use GET method).';
            } else if (mustBePost) {
                userMessage = 'This action requires a POST request.';
            } else if (methodsAllowed.length > 0) {
                userMessage = `This endpoint only accepts ${methodsAllowed.join(', ')} requests.`;
            } else {
                userMessage = 'Method not allowed for this endpoint.';
            }

            if (DEBUG_MODE) {
                console.error(`⚠️ [${requestId}] Method Not Allowed (405): ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`);
                console.log(`💡 ${userMessage}`);
            }

            // Enhance error with user-friendly message
            error.userMessage = userMessage;

            // Log as a warning rather than error for 405s
            logWarning(`Method Not Allowed (405): ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`);

            return Promise.reject(error);
        }

        // Enhanced error logging
        if (DEBUG_MODE) {
            if (!error.response) {
                console.error(
                    `❌ [${requestId}] NETWORK ERROR for ${originalRequest?.url || 'unknown URL'}`
                );
                console.log('🔍 Troubleshooting checklist:');
                console.log('   1. Backend server running?');
                console.log('   2. Vite proxy configuration correct?');
                console.log('   3. CORS settings configured properly?');
                console.log('   4. Network connectivity issues?');
            } else {
                const status = error.response?.status || 'Unknown';
                const url = originalRequest?.url || 'unknown';
                const errorData = error.response?.data || error.message;
                console.error(`❌ [${requestId}] ${status} ${url}`, errorData);
            }
        }

        // Prevent infinite retry loops
        if (
            originalRequest?._retry ||
            originalRequest?.skipAuthRefresh ||
            (originalRequest?.url && originalRequest.url.includes('token/refresh'))
        ) {
            return Promise.reject(error);
        }

        // Handle 401 Unauthorized with token refresh
        if (error.response?.status === 401) {
            originalRequest._retry = true;

            try {
                if (DEBUG_MODE) console.log(`🔄 [${requestId}] Attempting token refresh for retry`);

                const newToken = await refreshAuthToken();
                originalRequest.headers.Authorization = `Bearer ${newToken}`;

                if (DEBUG_MODE) console.log(`🔁 [${requestId}] Retrying request with new token`);

                return apiClient(originalRequest);
            } catch (refreshError) {
                // FIXED: Return original 401 error instead of refresh error
                // for better UX when there are network issues during refresh
                if (refreshError instanceof Error && refreshError.message.includes('network')) {
                    logWarning('Network error during token refresh, returning original 401 error');
                    return Promise.reject(error);
                }

                logError(refreshError as Error);
                if (DEBUG_MODE) console.error(`❌ [${requestId}] Token refresh failed, rejecting original request`);
                return Promise.reject(error);
            }
        }

        // Log non-401 errors
        if (error.response?.status >= 500) {
            logError(new Error(`Server error: ${error.response.status} - ${originalRequest?.url}`));
        }

        return Promise.reject(error);
    }
);

export default apiClient;
