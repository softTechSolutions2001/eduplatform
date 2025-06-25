/**
 * File: src/services/utils/handleRequest.ts
 * Version: 2.1.0
 * Date: 2025-06-25
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 UTC
 *
 * Enhanced Centralized API Request Handler - Merged Version
 *
 * Unified implementation combining authentication, caching, error handling,
 * retry logic, and performance monitoring with full TypeScript support
 * Incorporates all features from both v1.1.0 and v2.0.0
 */

import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import secureTokenStorage from '../../utils/secureTokenStorage';
import { snakeToCamel } from '../../utils/transformData';
import api from '../api';
import { DEBUG_MODE } from '../http/constants';
import {
    authState,
    DEBUG,
    getCacheKey,
    limitCacheSize,
    log,
    logError,
    pendingRequests,
    redirectToLogin,
    requestCache,
    validateToken
} from '../instructor/helpers';

// Type definitions
export interface FormattedError {
    message: string;
    status: number | string;
    details: any;
    originalError: Error | AxiosError;
    isNetworkError: boolean;
    timestamp: string;
    requestUrl?: string;
}

export interface RequestOptions extends AxiosRequestConfig {
    enableCache?: boolean;
    cacheTime?: number;
    abortController?: AbortController;
    skipAuthCheck?: boolean;
    url?: string;
    returnRawResponse?: boolean;
    explicitUrl?: string;
    params?: any;
    timeout?: number;
    retries?: number;
    retryDelay?: number;
    transformResponse?: boolean;
}

export type ApiCall<T = any> = (options?: any) => Promise<AxiosResponse<T>>;

// Cross-environment timing support
const getTimestamp = (): number => {
    return typeof performance !== 'undefined' ? performance.now() : Date.now();
};

// Enhanced debug logging with request ID tracking
const createRequestId = (): string => Math.random().toString(36).substr(2, 9);

const debugLog = (requestId: string, message: string, data?: any): void => {
    if (DEBUG || DEBUG_MODE) {
        if (data) {
            console.log(`[${requestId}] ${message}`, data);
        } else {
            console.log(`[${requestId}] ${message}`);
        }
    }
    // Fallback to original log function for compatibility
    log(message, data);
};

const debugError = (requestId: string, message: string, error: any): void => {
    if (DEBUG || DEBUG_MODE) {
        console.error(`❌ [${requestId}] ${message}`, error);
    }
    // Fallback to original logError function for compatibility
    logError(message, error);
};

// Centralized token refresh logic with enhanced error handling
const performTokenRefresh = async (requestId?: string): Promise<boolean> => {
    const logPrefix = requestId ? `[${requestId}]` : '';

    if (authState.refreshFailedUntilReload) {
        const msg = 'Circuit breaker active: refresh previously failed, redirecting to login';
        if (requestId) {
            debugLog(requestId, msg);
        } else {
            log(msg);
        }
        redirectToLogin();
        throw new Error('Authentication failed - circuit breaker active');
    }

    if (authState.refreshPromise) {
        const msg = 'Token refresh already in progress globally, waiting...';
        if (requestId) {
            debugLog(requestId, msg);
        } else {
            log(msg);
        }
        return await authState.refreshPromise;
    }

    let refreshPromise: Promise<boolean>;
    try {
        const msg = 'Starting global token refresh...';
        if (requestId) {
            debugLog(requestId, msg);
        } else {
            log(msg);
        }

        // Create the refresh promise
        refreshPromise = api.auth.refreshToken().then(() => {
            if (secureTokenStorage.isTokenValid()) {
                const successMsg = 'Global token refresh successful and verified';
                if (requestId) {
                    debugLog(requestId, successMsg);
                } else {
                    log(successMsg);
                }
                return true;
            } else {
                throw new Error('Token refresh verification failed');
            }
        });

        authState.refreshPromise = refreshPromise;
        return await refreshPromise;
    } catch (error) {
        const errorMsg = 'Global token refresh failed:';
        if (requestId) {
            debugError(requestId, errorMsg, error);
        } else {
            logError(errorMsg, error);
        }
        authState.refreshFailedUntilReload = true;
        throw error;
    } finally {
        authState.refreshPromise = null;
    }
};

// Enhanced error formatting with better type safety
const formatError = (
    error: AxiosError | Error,
    errorMessage: string,
    requestUrl?: string,
    requestId?: string
): FormattedError => {
    const axiosError = error as AxiosError;
    const isAxiosError = axiosError.response !== undefined || axiosError.request !== undefined;

    const formattedError: FormattedError = {
        message:
            axiosError.response?.data?.detail ||
            axiosError.response?.data?.message ||
            error.message ||
            errorMessage,
        status: axiosError.response?.status || (isAxiosError ? 'network_error' : 'unknown_error'),
        details: axiosError.response?.data || {},
        originalError: error,
        isNetworkError: isAxiosError && !axiosError.response && !!axiosError.request,
        timestamp: new Date().toISOString(),
        requestUrl,
    };

    // Enhanced logging for validation errors
    if (axiosError.response?.status === 400) {
        const errorDetails = {
            url: requestUrl,
            status: axiosError.response.status,
            data: axiosError.response.data,
            timestamp: formattedError.timestamp,
        };

        if (requestId) {
            debugError(requestId, 'Validation error details:', errorDetails);
        } else {
            logError('Validation error details:', errorDetails);
        }
    }

    return formattedError;
};

// Sleep utility for retry delays
const sleep = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms));

// Check if error should trigger a retry
const shouldRetryOnError = (error: AxiosError): boolean => {
    return (
        error.code === 'ECONNABORTED' ||
        error.message?.includes('timeout') ||
        error.message?.includes('Network Error') ||
        error.message?.includes('ETIMEDOUT') ||
        error.message?.includes('ECONNRESET') ||
        (error.response?.status && error.response.status >= 500)
    );
};

// Main request handler with comprehensive features
export const handleRequest = async <T = any>(
    apiCall: ApiCall<T>,
    errorMessage: string,
    options: RequestOptions = {}
): Promise<T> => {
    const requestId = createRequestId();
    const {
        enableCache = false,
        cacheTime = 30000,
        abortController = null,
        skipAuthCheck = false,
        url = '',
        returnRawResponse = false,
        explicitUrl = '',
        retries = 3,
        retryDelay = 1000,
        transformResponse = false,
        timeout = 10000,
        ...axiosOptions
    } = options;

    const requestUrl = url || explicitUrl || '';

    debugLog(requestId, `📤 API request starting: ${errorMessage}`, { url: requestUrl });

    // Cache handling
    let cacheKey: string | null = null;
    if (enableCache && requestUrl) {
        cacheKey = getCacheKey(apiCall.name || 'unknown', requestUrl, options.params);

        const cached = requestCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < cacheTime) {
            debugLog(requestId, `📋 Returning cached response for: ${cacheKey}`);
            return cached.data;
        }

        if (pendingRequests.has(cacheKey)) {
            debugLog(requestId, `⏳ Request already pending, waiting for result: ${cacheKey}`);
            return await pendingRequests.get(cacheKey);
        }
    }

    // Main execution function with retry logic
    const executeRequest = async (attempt: number = 1): Promise<T> => {
        const startTime = getTimestamp();

        try {
            // Authentication check
            if (!skipAuthCheck) {
                const isValid = validateToken();
                if (!isValid) {
                    debugLog(requestId, 'Token appears invalid, but proceeding with request (401 will trigger refresh if needed)');
                }
            }

            // Execute API call with timeout and abort signal
            let response: AxiosResponse<T>;
            const callOptions = {
                timeout,
                signal: abortController?.signal,
                ...axiosOptions,
            };

            try {
                response = await apiCall(callOptions);
            } catch (apiError) {
                const axiosError = apiError as AxiosError;

                // Handle network errors with retry logic (from v1.1.0)
                if (shouldRetryOnError(axiosError) && attempt <= retries) {
                    // Calculate backoff with cap (from v1.1.0)
                    const backoff = Math.min(Math.pow(1.5, attempt - 1) * retryDelay, retryDelay * 10);
                    debugLog(requestId, `Request failed with ${axiosError.message}, retrying in ${backoff}ms (attempt ${attempt}/${retries})`);
                    await sleep(backoff);
                    return executeRequest(attempt + 1);
                }

                debugError(requestId, 'API call failed with error:', axiosError);
                throw axiosError;
            }

            const endTime = getTimestamp();
            debugLog(requestId, `📥 API response received in ${(endTime - startTime).toFixed(2)}ms`);

            // Handle raw response return
            if (returnRawResponse) {
                return response as unknown as T;
            }

            // Transform response data if requested
            let data = response.data;
            if (transformResponse) {
                data = snakeToCamel(data);
            }

            // Cache successful response
            if (enableCache && cacheKey) {
                requestCache.set(cacheKey, {
                    data,
                    timestamp: Date.now(),
                    url: requestUrl,
                });

                // Limit cache size (from v1.1.0)
                limitCacheSize();

                setTimeout(() => {
                    if (requestCache.has(cacheKey)) {
                        requestCache.delete(cacheKey);
                    }
                }, cacheTime);
            }

            return data;
        } catch (error) {
            // Handle request cancellation
            if (error.name === 'AbortError' || abortController?.signal?.aborted) {
                debugLog(requestId, '🚫 Request was aborted');
                throw error;
            }

            const axiosError = error as AxiosError;

            // Handle 401 unauthorized with token refresh
            if (axiosError.response?.status === 401 && !skipAuthCheck) {
                debugLog(requestId, '🔄 Received 401 response, attempting global token refresh and retry');

                try {
                    await performTokenRefresh(requestId);
                    debugLog(requestId, '✅ Global token refresh successful, retrying original request');

                    // Retry the original request
                    let retryResponse: AxiosResponse<T>;
                    const retryOptions = {
                        timeout,
                        signal: abortController?.signal?.aborted ? undefined : abortController?.signal,
                        ...axiosOptions,
                    };

                    if (abortController?.signal?.aborted) {
                        throw new Error('Request aborted during retry');
                    }

                    retryResponse = await apiCall(retryOptions);

                    if (returnRawResponse) {
                        return retryResponse as unknown as T;
                    }

                    let retryData = retryResponse.data;
                    if (transformResponse) {
                        retryData = snakeToCamel(retryData);
                    }

                    return retryData;
                } catch (refreshError) {
                    if (refreshError.name === 'AbortError') {
                        throw refreshError;
                    }

                    debugError(requestId, 'Global token refresh failed, redirecting to login:', refreshError);

                    // Attempt logout
                    try {
                        if (api.logout && typeof api.logout === 'function') {
                            await api.logout();
                        }
                    } catch (logoutError) {
                        if (DEBUG || DEBUG_MODE) {
                            console.warn('Logout failed:', logoutError);
                        }
                    }

                    redirectToLogin();
                    throw new Error('Authentication failed - redirecting to login');
                }
            }

            // Handle retry logic for non-auth errors (enhanced from both versions)
            if (retries > 0 && attempt <= retries) {
                // Don't retry for client errors (4xx) except 401 (handled above)
                if (axiosError.response?.status && axiosError.response.status >= 400 && axiosError.response.status < 500) {
                    throw formatError(axiosError, errorMessage, requestUrl, requestId);
                }

                // Check if error should be retried
                if (shouldRetryOnError(axiosError)) {
                    const nextAttempt = attempt + 1;
                    const delay = Math.min(retryDelay * Math.pow(1.5, attempt - 1), retryDelay * 10);

                    debugLog(requestId, `⏳ Retrying request in ${delay}ms (Attempt ${nextAttempt}/${retries + 1})`);
                    await sleep(delay);

                    return executeRequest(nextAttempt);
                }
            }

            // Format and throw error
            throw formatError(axiosError, errorMessage, requestUrl, requestId);
        }
    };

    // Execute with cache handling
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

/**
 * Handle public API requests with transformation and enhanced error handling
 * @param url - API endpoint URL
 * @param errorMessage - Custom error message for logging
 * @param options - Request configuration options
 * @returns Promise resolving to transformed response data
 */
export const handlePublicRequest = async <T = any>(
    url: string,
    errorMessage?: string,
    options: RequestOptions = {}
): Promise<T> => {
    const requestId = createRequestId();
    const defaultErrorMessage = errorMessage || `Public API request to ${url}`;

    debugLog(requestId, `🌐 Making public API request to: ${url}`);

    const publicApiCall: ApiCall<T> = async (callOptions = {}) => {
        const requestOptions: AxiosRequestConfig = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            timeout: options.timeout || 10000,
            ...options,
            ...callOptions,
        };

        // Ensure no Authorization header for public requests
        if (requestOptions.headers) {
            delete requestOptions.headers.Authorization;
        }

        return axios.get<T>(url, requestOptions);
    };

    try {
        const result = await handleRequest<T>(
            publicApiCall,
            defaultErrorMessage,
            {
                ...options,
                skipAuthCheck: true,
                transformResponse: true,
                url,
            }
        );

        debugLog(requestId, '✅ Public API request successful');
        return result;
    } catch (error) {
        // Simplify error for public requests
        if (error.name === 'AbortError' || error.message === 'canceled') {
            debugLog(requestId, `🚫 Public request aborted: ${url}`);
            throw error;
        }

        const errorDetails = error.message || defaultErrorMessage || 'API request failed';
        throw new Error(errorDetails);
    }
};

/**
 * Utility function to create a request with automatic retry logic
 * @param apiCall - Function that returns a Promise of AxiosResponse
 * @param errorMessage - Custom error message for logging
 * @param maxRetries - Maximum number of retry attempts
 * @param retryDelay - Delay between retries in milliseconds
 * @returns Promise resolving to response data
 */
export const handleRequestWithRetry = async <T = any>(
    apiCall: ApiCall<T>,
    errorMessage: string,
    maxRetries: number = 3,
    retryDelay: number = 1000
): Promise<T> => {
    return handleRequest<T>(apiCall, errorMessage, {
        retries: maxRetries,
        retryDelay,
    });
};

/**
 * Backwards compatibility wrapper for the original handleRequest signature
 * Maintains compatibility with v1.1.0 usage patterns
 */
export const handleLegacyRequest = async (
    apiCall: (options?: any) => Promise<any>,
    errorMessage: string,
    options: any = {}
): Promise<any> => {
    return handleRequest(apiCall, errorMessage, options);
};

// Backward compatibility exports
export default handleRequest;
