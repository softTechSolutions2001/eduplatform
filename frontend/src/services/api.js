/**
 * File: src/services/api.js
 * Version: 4.0.1
 * Last modified: 2025-05-30 17:13:23
 * Author: cadsanthanam
 * Modified by: sujibeautysalon
 *
 * Core API service for EduPlatform frontend
 * Includes enhanced social authentication with PKCE support
 * Updated subscription tier terminology for consistency
 */

import axios from 'axios';
import { logError, logWarning } from '../utils/logger';
import secureTokenStorage from '../utils/secureTokenStorage';
import {
  camelToSnake,
  objectToSnakeFormData,
  snakeToCamel,
} from '../utils/transformData';

// Use the base URL from environment in production, but rely on Vite proxy in development
const API_BASE_URL =
  process.env.NODE_ENV === 'production'
    ? import.meta.env.VITE_API_BASE_URL || '/api'
    : '/api';

if (!API_BASE_URL) {
  const errorMsg =
    'API_BASE_URL is not configured. Please set VITE_API_BASE_URL in your environment.';
  logError(new Error(errorMsg));
  throw new Error(errorMsg);
}

const TOKEN_STORAGE_KEYS = {
  ACCESS: 'accessToken',
  REFRESH: 'refreshToken',
  USER: 'user',
  PERSISTENCE: 'tokenPersistence',
};

const DEBUG_MODE =
  import.meta.env.VITE_DEBUG_API === 'true' ||
  process.env.NODE_ENV === 'development';
const ALLOW_MOCK_FALLBACK =
  import.meta.env.VITE_ALLOW_MOCK_FALLBACK === 'true' || false;
const REQUEST_TIMEOUT = 15000;
const CONTENT_CACHE_TTL = 60 * 60 * 1000;

const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/user/login/`,
    LOGOUT: `${API_BASE_URL}/user/logout/`,
    REFRESH: `${API_BASE_URL}/token/refresh/`,
    REGISTER: `${API_BASE_URL}/user/register/`,
    CURRENT_USER: `${API_BASE_URL}/user/me/`,
    VERIFY_EMAIL: `${API_BASE_URL}/user/email/verify/`,
    RESET_PASSWORD: `${API_BASE_URL}/user/password/reset/`,
    RESET_PASSWORD_REQUEST: `${API_BASE_URL}/user/reset-password-request/`,
    CONFIRM_RESET: `${API_BASE_URL}/user/password/reset/confirm/`,
    CHANGE_PASSWORD: `${API_BASE_URL}/user/password/change/`,
    // Enhanced social auth endpoints
    SOCIAL_AUTH: provider => `${API_BASE_URL}/user/social/${provider}/`,
    SOCIAL_AUTH_COMPLETE: () => `${API_BASE_URL}/user/social/complete/`,
  },
  COURSE: {
    BASE: `${API_BASE_URL}/courses/`,
    FEATURED: `${API_BASE_URL}/courses/featured/`,
    POPULAR: `${API_BASE_URL}/courses/popular/`,
    LATEST: `${API_BASE_URL}/courses/latest/`,
    SEARCH: `${API_BASE_URL}/courses/search/`,
    COURSE_BY_SLUG: slug => `${API_BASE_URL}/courses/${slug}/`,
    ENROLL: slug => `${API_BASE_URL}/courses/${slug}/enroll/`,
    MODULES: slug => `${API_BASE_URL}/courses/${slug}/modules/`,
    REVIEWS: slug => `${API_BASE_URL}/courses/${slug}/reviews/`,
    REVIEW: slug => `${API_BASE_URL}/courses/${slug}/review/`,
    UPDATE_REVIEW: (slug, reviewId) =>
      `${API_BASE_URL}/courses/${slug}/review/${reviewId}/`,
    CERTIFICATE: slug => `${API_BASE_URL}/courses/${slug}/certificate/`,
    DISCUSSIONS: slug => `${API_BASE_URL}/courses/${slug}/discussions/`,
    DISCUSSION: (slug, discussionId) =>
      `${API_BASE_URL}/courses/${slug}/discussions/${discussionId}/`,
    DISCUSSION_REPLIES: (slug, discussionId) =>
      `${API_BASE_URL}/courses/${slug}/discussions/${discussionId}/replies/`,
  },
  MODULE: {
    DETAILS: moduleId => `${API_BASE_URL}/modules/${moduleId}/`,
    LESSONS: moduleId => `${API_BASE_URL}/modules/${moduleId}/lessons/`,
  },
  LESSON: {
    DETAILS: lessonId => `${API_BASE_URL}/lessons/${lessonId}/`,
    COMPLETE: lessonId => `${API_BASE_URL}/lessons/${lessonId}/complete/`,
  },
  USER: {
    ME: `${API_BASE_URL}/user/me/`,
    UPDATE_PROFILE: `${API_BASE_URL}/user/profile/`,
    SUBSCRIPTION: {
      CURRENT: `${API_BASE_URL}/user/subscription/current/`,
      UPGRADE: `${API_BASE_URL}/user/subscription/upgrade/`,
      CANCEL: `${API_BASE_URL}/user/subscription/cancel/`,
    },
    PROGRESS: {
      BASE: `${API_BASE_URL}/user/progress/`,
      COURSE: courseId => `${API_BASE_URL}/user/progress/${courseId}/`,
      STATS: `${API_BASE_URL}/user/progress/stats/`,
    },
    ASSESSMENT_ATTEMPTS: `${API_BASE_URL}/user/assessment-attempts/`,
    ENROLLMENTS: `${API_BASE_URL}/enrollments/`,
  },
  ASSESSMENT: {
    BASE: `${API_BASE_URL}/assessments/`,
    DETAILS: assessmentId => `${API_BASE_URL}/assessments/${assessmentId}/`,
    START: assessmentId => `${API_BASE_URL}/assessments/${assessmentId}/start/`,
    ATTEMPTS: `${API_BASE_URL}/assessment-attempts/`,
    SUBMIT: attemptId =>
      `${API_BASE_URL}/assessment-attempts/${attemptId}/submit/`,
  },
  NOTE: {
    BASE: `${API_BASE_URL}/notes/`,
    DETAIL: noteId => `${API_BASE_URL}/notes/${noteId}/`,
  },
  LAB: {
    BASE: `${API_BASE_URL}/labs/`,
    DETAILS: labId => `${API_BASE_URL}/labs/${labId}/`,
    START: labId => `${API_BASE_URL}/labs/${labId}/start/`,
    SUBMIT: labId => `${API_BASE_URL}/labs/${labId}/submit/`,
  },
  CATEGORY: {
    BASE: `${API_BASE_URL}/categories/`,
    COURSES: categorySlug =>
      `${API_BASE_URL}/categories/${categorySlug}/courses/`,
  },
  CERTIFICATE: {
    BASE: `${API_BASE_URL}/certificates/`,
    VERIFY: code => `${API_BASE_URL}/certificates/verify/${code}/`,
  },
  BLOG: {
    POSTS: `${API_BASE_URL}/blog/posts/`,
    POST_BY_SLUG: slug => `${API_BASE_URL}/blog/posts/${slug}/`,
  },
  SYSTEM: {
    STATUS: `${API_BASE_URL}/system/status/`,
    DB_STATUS: `${API_BASE_URL}/system/db-status/`,
  },
  STATISTICS: {
    PLATFORM: `${API_BASE_URL}/statistics/platform/`,
    USER: `${API_BASE_URL}/statistics/user/`,
    INSTRUCTOR: `${API_BASE_URL}/statistics/instructor/`,
  },
  TESTIMONIAL: {
    BASE: `${API_BASE_URL}/testimonials/`,
    FEATURED: `${API_BASE_URL}/testimonials/featured/`,
  },
};

const apiClient = axios.create({
  // Don't set baseURL - let Vite proxy handle the routing
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: REQUEST_TIMEOUT,
});

// Add convenience method for multipart/form-data requests
apiClient.postForm = function (url, data, config = {}) {
  return this.post(url, objectToSnakeFormData(data), {
    headers: { 'Content-Type': 'multipart/form-data' },
    ...config
  });
};

// Add convenience method for multipart/form-data PUT requests
apiClient.putForm = function (url, data, config = {}) {
  return this.put(url, objectToSnakeFormData(data), {
    headers: { 'Content-Type': 'multipart/form-data' },
    ...config
  });
};

let refreshTokenPromise = null;

const refreshAuthToken = async () => {
  if (refreshTokenPromise) {
    return refreshTokenPromise;
  }

  refreshTokenPromise = (async () => {
    try {
      if (DEBUG_MODE) console.log('Refreshing authentication token');

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
        }
      );

      if (!response.data?.access) {
        throw new Error('No access token in refresh response');
      }

      secureTokenStorage.updateAccessToken(response.data.access);

      if (DEBUG_MODE) console.log('Token refreshed successfully');

      return response.data.access;
    } catch (error) {
      logWarning('Token refresh failed:', { error });

      secureTokenStorage.clearAuthData();

      const authFailedEvent = new CustomEvent('auth:failed', {
        detail: { error },
      });
      window.dispatchEvent(authFailedEvent);

      throw error;
    } finally {
      refreshTokenPromise = null;
    }
  })();

  return refreshTokenPromise;
};

function sanitizeLogData(data) {
  if (!data || typeof data !== 'object') return data;

  const sanitized = { ...data };

  const sensitiveFields = [
    'password',
    'token',
    'accessToken',
    'refreshToken',
    'access',
    'refresh',
    'access_token',
    'refresh_token',
    'authorization',
    'email',
    'phone',
    'credit_card',
    'cardNumber',
    'cvv',
    'cvc',
    'expiry',
    'code_verifier',
  ];

  sensitiveFields.forEach(field => {
    if (sanitized[field] !== undefined) {
      sanitized[field] = '[REDACTED]';
    }
  });

  return sanitized;
}

apiClient.interceptors.request.use(
  config => {
    if (!config.skipAuthRefresh) {
      const token = secureTokenStorage.getValidToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        secureTokenStorage.refreshTokenExpiry();
      }
    }

    // Skip FormData, File objects and handle them appropriately
    if (
      config.data &&
      typeof config.data === 'object' &&
      !(config.data instanceof FormData) &&
      !(config.data instanceof File)
    ) {
      config.data = camelToSnake(config.data);
    }

    // For FormData, handle case conversion if Content-Type is multipart
    if (
      config.data instanceof FormData &&
      config.headers?.['Content-Type']?.includes('multipart')
    ) {
      const fd = new FormData();
      config.data.forEach((value, key) => fd.append(camelToSnake(key), value));
      config.data = fd;
    }

    if (DEBUG_MODE) {
      console.log(
        `📤 [API REQUEST] ${config.method?.toUpperCase() || 'GET'} ${config.url}`,
        config.data
          ? sanitizeLogData(config.data)
          : config.params
            ? sanitizeLogData(config.params)
            : ''
      );
    }

    return config;
  },
  error => {
    if (DEBUG_MODE) {
      console.error('❌ [API REQUEST ERROR]', error);
    }
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  response => {
    // Skip handling for non-object responses (like blobs, text, etc.)
    if (
      response.data &&
      typeof response.data === 'object' &&
      !(response.data instanceof Blob) &&
      !(response.data instanceof ArrayBuffer)
    ) {
      response.data = snakeToCamel(response.data);
    }

    if (DEBUG_MODE) {
      console.log(
        `📥 [API RESPONSE] ${response.status} ${response.config.url}`,
        response.data ? sanitizeLogData(response.data) : ''
      );
    }

    return response;
  },
  async error => {
    const originalRequest = error.config;

    if (DEBUG_MODE) {
      if (!error.response) {
        console.error(
          `❌ [API NETWORK ERROR] for ${originalRequest?.url || 'unknown URL'}`,
          'This might be due to CORS, proxy configuration, or server being down'
        );
        console.log('Check:');
        console.log('1. Is your backend server running?');
        console.log('2. Does your Vite proxy configuration match the API URL?');
        console.log(
          '3. CORS settings in backend/educore/settings.py match frontend origin?'
        );
      } else {
        console.error(
          `❌ [API ERROR] ${error.response?.status || 'Unknown status'} ${originalRequest?.url || ''}`,
          error.response?.data ? error.response.data : error.message
        );
      }
    }

    if (
      originalRequest?._retry ||
      originalRequest?.skipAuthRefresh ||
      (originalRequest?.url && originalRequest.url.includes('token/refresh'))
    ) {
      return Promise.reject(error);
    }

    if (error.response && error.response.status === 401) {
      originalRequest._retry = true;

      try {
        const newToken = await refreshAuthToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

const handleRequest = async (apiCall, errorMessage) => {
  try {
    console.log(`📤 API request starting: ${errorMessage}`);
    const startTime = performance.now();

    const response = await apiCall();

    const duration = performance.now() - startTime;
    console.log(`📥 API response received in ${duration.toFixed(2)}ms`);

    return response.data;
  } catch (error) {
    if (error.name === 'AbortError' || error.message === 'canceled') {
      console.log(`Request aborted: ${errorMessage}`);
      throw error;
    }

    if (DEBUG_MODE) {
      if (!error.response) {
        console.error(`${errorMessage} (Network Error):`, error);
      } else {
        console.error(
          `${errorMessage}:`,
          error.response?.status,
          error.message
        );
        console.error(`Response data:`, error.response?.data);
      }
    }

    const formattedError = {
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        errorMessage,
      status: error.response?.status || 'network_error',
      details: error.response?.data || {},
      originalError: error,
      isNetworkError: !error.response && error.request,
    };

    throw formattedError;
  }
};

const contentCache = {
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

const authService = {
  login: async credentials => {
    try {
      console.log('Starting authentication process');

      secureTokenStorage.clearAuthData();

      const response = await axios.post(API_ENDPOINTS.AUTH.LOGIN, {
        email: credentials.email,
        password: credentials.password,
      });

      if (!response.data || !response.data.access) {
        console.error('No token in response', response.data);
        throw new Error('Invalid response from authentication server');
      }

      console.log('Authentication successful');

      secureTokenStorage.setAuthData(
        response.data.access,
        response.data.refresh,
        credentials.rememberMe
      );

      return response.data;
    } catch (error) {
      console.error('Authentication failed:', error);

      const errorMsg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        'Login failed. Please check your credentials.';

      throw new Error(errorMsg);
    }
  },

  register: async userData => {
    return handleRequest(
      async () => await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, userData),
      'Registration failed'
    );
  },

  verifyEmail: async token => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.AUTH.VERIFY_EMAIL, { token }),
      'Email verification failed'
    );
  },

  requestPasswordReset: async email => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD_REQUEST, {
          email,
        }),
      'Password reset request failed'
    );
  },

  resetPassword: async (token, password) => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
          token,
          password,
        }),
      'Password reset failed'
    );
  },

  refreshToken: async () => {
    try {
      return await refreshAuthToken();
    } catch (error) {
      throw error;
    }
  },

  logout: async navigate => {
    secureTokenStorage.clearAuthData();

    localStorage.removeItem(TOKEN_STORAGE_KEYS.ACCESS);
    localStorage.removeItem(TOKEN_STORAGE_KEYS.REFRESH);
    localStorage.removeItem(TOKEN_STORAGE_KEYS.USER);
    localStorage.removeItem(TOKEN_STORAGE_KEYS.PERSISTENCE);
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userProfile');
    localStorage.removeItem('subscription');

    // Clean up OAuth-related storage
    localStorage.removeItem('oauth_state');
    sessionStorage.removeItem('oauth_code_verifier');
    sessionStorage.removeItem('oauth_code');
    sessionStorage.removeItem('oauth_code_expiry');

    if (typeof navigate === 'function') {
      navigate('/login', { replace: true });
    } else {
      window.location.href = '/login';
    }
  },

  getCurrentUser: async cacheBuster => {
    console.log('Requesting user data from API');

    if (!secureTokenStorage.isTokenValid()) {
      console.log('No valid token available, skipping user profile request');
      return null;
    }

    const cacheBustParam = cacheBuster || `_cache_buster=${Date.now()}`;

    try {
      const response = await apiClient.get(
        `${API_ENDPOINTS.USER.ME}?${cacheBustParam}`
      );

      console.log('Successfully retrieved user data');
      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 401) {
        console.log('User not authenticated');
        return null;
      }

      console.error('Error fetching user data:', error);
      return null;
    }
  },

  updateProfile: async userData => {
    return handleRequest(
      async () =>
        await apiClient.put(API_ENDPOINTS.USER.UPDATE_PROFILE, userData),
      'Failed to update profile'
    );
  },

  changePassword: async passwordData => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, passwordData),
      'Failed to change password'
    );
  },

  isAuthenticated: () => {
    return secureTokenStorage.isTokenValid();
  },

  // Enhanced social authentication methods with PKCE and state parameter support
  getSocialAuthUrl: async (provider, codeChallenge, state) => {
    try {
      console.log(`Getting social auth URL for provider: ${provider}`);

      // Request authorization URL from backend with PKCE and state parameters
      const response = await apiClient.get(
        API_ENDPOINTS.AUTH.SOCIAL_AUTH(provider),
        {
          params: {
            code_challenge: codeChallenge,
            code_challenge_method: 'S256',
            state: state,
            redirect_uri: `${window.location.origin}/auth/social/${provider}/callback`,
          },
        }
      );

      // Check for authorizationUrl in both camelCase and snake_case formats
      if (
        response.data &&
        (response.data.authorizationUrl || response.data.authorization_url)
      ) {
        return {
          authorizationUrl:
            response.data.authorizationUrl || response.data.authorization_url,
          success: true,
        };
      } else {
        console.error(
          'Invalid response from social auth URL endpoint:',
          response
        );
        throw new Error('Invalid response format from authorization server');
      }
    } catch (error) {
      console.error(`Failed to get ${provider} auth URL:`, error);

      // Development fallback for testing when API is not available
      if (process.env.NODE_ENV === 'development') {
        console.warn('Using development fallback for social auth URL');

        // Get client IDs from environment variables if available
        const clientId =
          provider === 'google'
            ? import.meta.env.VITE_GOOGLE_CLIENT_ID ||
            '99067790447-go0pcefo3nt1b9d0udei65u0or6nb0a0.apps.googleusercontent.com'
            : import.meta.env.VITE_GITHUB_CLIENT_ID || 'your-github-client-id';

        const redirectUri = encodeURIComponent(
          `${window.location.origin}/auth/social/${provider}/callback`
        );
        const scope =
          provider === 'google'
            ? encodeURIComponent('email profile')
            : encodeURIComponent('user:email');

        // Build auth URL with PKCE and state
        let authUrl;
        if (provider === 'google') {
          authUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
        } else {
          authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
        }

        // Add PKCE parameters if provided
        if (codeChallenge) {
          authUrl += `&code_challenge=${codeChallenge}&code_challenge_method=S256`;
        }

        // Add state parameter if provided
        if (state) {
          authUrl += `&state=${state}`;
        }

        return {
          authorizationUrl: authUrl,
          success: true,
        };
      }

      throw error;
    }
  },

  processSocialAuth: async (provider, code, codeVerifier) => {
    try {
      // Only log part of the code for security
      if (DEBUG_MODE) {
        console.log(
          `Processing ${provider} auth with code length: ${code?.length || 0}`
        );
        console.log(`Code verifier provided: ${codeVerifier ? 'Yes' : 'No'}`);
      }

      // In development, if using the dev-verifier, adjust request accordingly
      const isDevelopment = process.env.NODE_ENV === 'development';
      const isUsingDevVerifier =
        isDevelopment && codeVerifier === 'dev-verifier';

      // Prepare request body - conditionally include code_verifier
      const requestBody = {
        code,
        provider,
        redirect_uri: `${window.location.origin}/auth/social/${provider}/callback`,
      };

      // Only include code_verifier if it exists and it's not a development fallback
      // or if we're specifically allowing dev verifier in debug mode
      if (
        codeVerifier &&
        (!isUsingDevVerifier || (isUsingDevVerifier && DEBUG_MODE))
      ) {
        requestBody.code_verifier = codeVerifier;
      }

      // Use the correct endpoint
      const response = await apiClient.post(
        API_ENDPOINTS.AUTH.SOCIAL_AUTH_COMPLETE(),
        requestBody
      );

      if (!response.data || !response.data.access) {
        console.error('No token in response', response.data);
        throw new Error('Invalid response from authentication server');
      }

      console.log(`${provider} authentication successful`);

      secureTokenStorage.setAuthData(
        response.data.access,
        response.data.refresh,
        true // Social logins typically remember the user
      );

      return response.data;
    } catch (error) {
      // Special handling for duplicate calls in development
      if (
        process.env.NODE_ENV === 'development' &&
        error.response?.status === 400 &&
        error.response?.data?.detail?.includes('code for token')
      ) {
        console.warn(
          `Development: ${provider} auth duplicate call detected, suppressing error`
        );
        // Return a fake success to keep the UI from showing errors in dev mode
        // This is only for development to avoid React StrictMode double-invocation errors
        if (window.localStorage.getItem('isAuthenticated') === 'true') {
          const cachedUser = JSON.parse(
            window.localStorage.getItem('currentUser') || '{}'
          );
          return {
            access: 'dev-mode-duplicate-call',
            refresh: 'dev-mode-duplicate-call',
            user: cachedUser,
          };
        }
      }

      console.error(`${provider} authentication failed:`, error);

      const errorMsg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        `${provider} login failed. Please try again.`;

      throw new Error(errorMsg);
    }
  },
};

const subscriptionService = {
  getCurrentSubscription: async () => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.get(API_ENDPOINTS.USER.SUBSCRIPTION.CURRENT),
        'Failed to retrieve subscription information'
      );
    } catch (error) {
      if (
        ALLOW_MOCK_FALLBACK &&
        error.response &&
        error.response.status === 404
      ) {
        logWarning('Subscription endpoint not available, using mock data');

        return {
          tier: 'guest',
          status: 'active',
          isActive: true,
          daysRemaining: 30,
          endDate: new Date(
            Date.now() + 30 * 24 * 60 * 60 * 1000
          ).toISOString(),
        };
      }

      throw error;
    }
  },

  upgradeSubscription: async subscriptionData => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.post(
            API_ENDPOINTS.USER.SUBSCRIPTION.UPGRADE,
            subscriptionData
          ),
        'Failed to upgrade subscription'
      );
    } catch (error) {
      if (
        ALLOW_MOCK_FALLBACK &&
        error.response &&
        error.response.status === 404
      ) {
        logWarning(
          'Subscription upgrade endpoint not available, using mock data'
        );

        return {
          tier: subscriptionData.tier,
          status: 'active',
          isActive: true,
          daysRemaining: 30,
          endDate: new Date(
            Date.now() + 30 * 24 * 60 * 60 * 1000
          ).toISOString(),
        };
      }

      throw error;
    }
  },

  cancelSubscription: async () => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.post(API_ENDPOINTS.USER.SUBSCRIPTION.CANCEL),
        'Failed to cancel subscription'
      );
    } catch (error) {
      if (
        ALLOW_MOCK_FALLBACK &&
        error.response &&
        error.response.status === 404
      ) {
        logWarning(
          'Subscription cancel endpoint not available, using mock data'
        );

        return {
          tier: 'guest',
          status: 'inactive',
          isActive: false,
          daysRemaining: 0,
          endDate: new Date().toISOString(),
        };
      }

      throw error;
    }
  },
};

const handlePublicRequest = async (url, errorMessage, options = {}) => {
  try {
    console.log(`Making public API request to: ${url}`);

    const requestOptions = {
      headers: {
        'Content-Type': 'application/json',
        Authorization: undefined,
      },
      ...options,
    };

    const response = await axios.get(url, requestOptions);

    const transformedData = snakeToCamel(response.data);
    console.log(`Public API request successful`);

    return transformedData;
  } catch (error) {
    if (error.name === 'AbortError' || error.message === 'canceled') {
      console.log(`Public request aborted: ${url}`);
      throw error;
    }

    console.error(`Public API error:`, error);

    const errorDetails =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      errorMessage ||
      'API request failed';

    throw new Error(errorDetails);
  }
};

const createFormData = data => {
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

const courseService = {
  getAllCourses: async (params = {}) => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.COURSE.BASE, { params }),
      'Failed to fetch courses'
    );
  },

  getCourseBySlug: async slug => {
    console.log(`Getting course by slug: ${slug}`);

    try {
      return await handleRequest(
        async () =>
          await apiClient.get(API_ENDPOINTS.COURSE.COURSE_BY_SLUG(slug)),
        `Failed to fetch course ${slug}`
      );
    } catch (error) {
      console.error(`Error fetching course: ${error.message}`);
      throw error;
    }
  },

  enrollInCourse: async slug => {
    return handleRequest(
      async () => await apiClient.post(API_ENDPOINTS.COURSE.ENROLL(slug)),
      `Failed to enroll in course ${slug}`
    );
  },

  createCourse: async (courseData, thumbnailFile) => {
    const formData = thumbnailFile
      ? prepareCourseFormData(courseData, thumbnailFile)
      : createFormData(courseData);

    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.COURSE.BASE, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }),
      'Failed to create course'
    );
  },

  updateCourse: async (slug, courseData, thumbnailFile) => {
    const formData = thumbnailFile
      ? prepareCourseFormData(courseData, thumbnailFile)
      : createFormData(courseData);

    return handleRequest(
      async () =>
        await apiClient.put(
          API_ENDPOINTS.COURSE.COURSE_BY_SLUG(slug),
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        ),
      `Failed to update course ${slug}`
    );
  },

  getCourseModules: async slug => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.COURSE.MODULES(slug)),
      `Failed to fetch modules for course ${slug}`
    );
  },

  getModuleDetails: async moduleId => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.MODULE.DETAILS(moduleId)),
      `Failed to fetch module details for module ${moduleId}`
    );
  },

  getModuleLessons: async moduleId => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.MODULE.LESSONS(moduleId)),
      `Failed to fetch lessons for module ${moduleId}`
    );
  },

  getLessonDetails: async (
    lessonId,
    isPublicContent = false,
    isAuthenticated = false,
    options = {}
  ) => {
    if (typeof isPublicContent === 'object') {
      options = isPublicContent;
      isPublicContent = options.isPublicContent || false;
      isAuthenticated = options.isAuthenticated || false;
    }

    const moduleData = options.moduleData || null;
    const moduleId = options.moduleId || null;
    const signal = options.signal || null;

    console.log(
      `Getting lesson details for ${lessonId}, isPublic: ${isPublicContent}, isAuth: ${isAuthenticated}, hasSignal: ${!!signal}`
    );

    const MAX_RETRIES = 2;
    const RETRY_DELAY = 1000;
    const useLocalStorage =
      typeof window !== 'undefined' && window.localStorage;

    const startTime = performance.now();
    let source = 'api';

    let cachedContent = null;
    let fallbackContent = null;

    if (useLocalStorage) {
      try {
        const contentCacheKey = `content_cache_lesson_${lessonId}`;
        cachedContent = contentCache.get(contentCacheKey);

        if (cachedContent) {
          fallbackContent = cachedContent;
          source = 'cache';
          console.log('Using cached lesson content');
        }

        if (!cachedContent && moduleId) {
          const moduleContentKey = `content_cache_module_${moduleId}`;
          const moduleCachedData = contentCache.get(moduleContentKey);

          if (moduleCachedData?.lessons) {
            const cachedLesson = moduleCachedData.lessons.find(
              l => l.id.toString() === lessonId.toString()
            );
            if (cachedLesson && cachedLesson.content) {
              console.log('Using cached lesson content from module cache');
              cachedContent = cachedLesson;
              fallbackContent = cachedLesson;
              source = 'module-cache';
            }
          }
        }
      } catch (error) {
        console.error('Error accessing cached lesson content:', error);
      }
    }

    const fetchWithRetry = async fetchFn => {
      let lastError = null;

      for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
        try {
          if (attempt > 0) {
            console.log(`Retry attempt ${attempt} for lesson ${lessonId}`);
            await new Promise(resolve =>
              setTimeout(resolve, RETRY_DELAY * attempt)
            );
          }

          return await fetchFn();
        } catch (error) {
          lastError = error;

          if (error.name === 'AbortError' || error.message === 'canceled') {
            console.log(`Lesson fetch aborted for ${lessonId}`);
            throw error;
          }

          console.error(
            `Attempt ${attempt} failed for lesson ${lessonId}:`,
            error
          );

          if (attempt === MAX_RETRIES) {
            if (fallbackContent) {
              console.warn(
                `Using fallback content after ${MAX_RETRIES + 1} failed attempts`
              );
              return fallbackContent;
            }
            throw error;
          }
        }
      }
    };

    try {
      if (isAuthenticated) {
        console.log('Using authenticated request for lesson content');

        const response = await fetchWithRetry(async () => {
          const result = await handleRequest(async () => {
            const requestOptions = {
              headers: {
                ...apiClient.defaults.headers,
                'X-Force-Auth': 'true',
              },
            };

            if (signal) {
              requestOptions.signal = signal;
            }

            return await apiClient.get(
              API_ENDPOINTS.LESSON.DETAILS(lessonId),
              requestOptions
            );
          }, `Failed to fetch lesson details for lesson ${lessonId}`);
          return result;
        });

        if (
          cachedContent?.content &&
          response.content &&
          cachedContent.content.length > response.content.length
        ) {
          console.log('Using cached content (longer than API response)');
          response.content = cachedContent.content;
          source = 'cache+api';
        } else {
          source = 'api';
        }

        if (DEBUG_MODE) {
          const duration = performance.now() - startTime;
          console.log(
            `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
          );
        }

        if (useLocalStorage && response.content) {
          const contentCacheKey = `content_cache_lesson_${lessonId}`;
          contentCache.set(contentCacheKey, response);
        }

        return response;
      }

      if (isPublicContent) {
        console.log('Using public request for freely accessible content');

        const publicOptions = {};
        if (signal) {
          publicOptions.signal = signal;
        }

        const response = await fetchWithRetry(async () => {
          return await handlePublicRequest(
            API_ENDPOINTS.LESSON.DETAILS(lessonId),
            `Failed to fetch public lesson details for lesson ${lessonId}`,
            publicOptions
          );
        });

        if (
          cachedContent?.content &&
          response.content &&
          cachedContent.content.length > response.content.length
        ) {
          console.log('Using cached content (longer than API response)');
          response.content = cachedContent.content;
          source = 'cache+public';
        } else {
          source = 'public';
        }

        if (DEBUG_MODE) {
          const duration = performance.now() - startTime;
          console.log(
            `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
          );
        }

        return response;
      }

      const defaultOptions = {};
      if (signal) {
        defaultOptions.signal = signal;
      }

      console.log('Using default API request for lesson content');

      const response = await fetchWithRetry(async () => {
        return await handleRequest(
          async () =>
            await apiClient.get(
              API_ENDPOINTS.LESSON.DETAILS(lessonId),
              defaultOptions
            ),
          `Failed to fetch lesson details for lesson ${lessonId}`
        );
      });

      if (DEBUG_MODE) {
        const duration = performance.now() - startTime;
        console.log(
          `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
        );
      }

      return response;
    } catch (error) {
      console.error(`Error fetching lesson ${lessonId}:`, error);

      if (DEBUG_MODE) {
        const duration = performance.now() - startTime;
        console.log(`Lesson content fetch FAILED (${duration.toFixed(2)}ms)`);
      }

      if (fallbackContent) {
        console.warn(`Using fallback content after API error`);
        return fallbackContent;
      }

      throw error;
    }
  },

  completeLesson: async (lessonId, timeSpent = 0) => {
    return handleRequest(
      async () =>
        await apiClient.put(API_ENDPOINTS.LESSON.COMPLETE(lessonId), {
          timeSpent,
        }),
      `Failed to mark lesson ${lessonId} as complete`
    );
  },

  getCourseReviews: async slug => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.COURSE.REVIEWS(slug)),
      `Failed to fetch reviews for course ${slug}`
    );
  },

  addCourseReview: async (slug, reviewData) => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.COURSE.REVIEW(slug), reviewData),
      `Failed to add review for course ${slug}`
    );
  },

  updateCourseReview: async (slug, reviewId, reviewData) => {
    return handleRequest(
      async () =>
        await apiClient.put(
          API_ENDPOINTS.COURSE.UPDATE_REVIEW(slug, reviewId),
          reviewData
        ),
      `Failed to update review ${reviewId}`
    );
  },

  deleteCourseReview: async (slug, reviewId) => {
    return handleRequest(
      async () =>
        await apiClient.delete(
          API_ENDPOINTS.COURSE.UPDATE_REVIEW(slug, reviewId)
        ),
      `Failed to delete review ${reviewId}`
    );
  },

  searchCourses: async query => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.COURSE.BASE, {
          params: { q: query },
        }),
      'Course search failed'
    );
  },

  getFeaturedCourses: async (limit = 3) => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.get(API_ENDPOINTS.COURSE.FEATURED, {
            params: { limit },
          }),
        'Failed to fetch featured courses'
      );
    } catch (error) {
      if (!ALLOW_MOCK_FALLBACK) {
        throw error;
      }

      logWarning('Falling back to mock featured courses data', { error });

      return [
        {
          id: 1,
          title: 'Introduction to Programming',
          instructor: 'John Smith',
          category: 'Computer Science',
          rating: 4.8,
          students: 1200,
          image: '/images/courses/programming-intro.jpg',
        },
        {
          id: 2,
          title: 'Web Development Bootcamp',
          instructor: 'Maria Johnson',
          category: 'Web Development',
          rating: 4.9,
          students: 2500,
          image: '/images/courses/web-dev.jpg',
        },
        {
          id: 3,
          title: 'Data Science Fundamentals',
          instructor: 'Robert Chen',
          category: 'Data Science',
          rating: 4.7,
          students: 1800,
          image: '/images/courses/data-science.jpg',
        },
      ];
    }
  },

  getAssessmentDetails: async assessmentId => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.ASSESSMENT.DETAILS(assessmentId)),
      `Failed to fetch assessment details for assessment ${assessmentId}`
    );
  },

  startAssessment: async assessmentId => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.ASSESSMENT.START(assessmentId)),
      `Failed to start assessment ${assessmentId}`
    );
  },

  submitAssessment: async (attemptId, answers) => {
    return handleRequest(
      async () =>
        await apiClient.put(
          API_ENDPOINTS.ASSESSMENT.SUBMIT(attemptId),
          answers
        ),
      `Failed to submit assessment attempt ${attemptId}`
    );
  },
};

const assessmentService = {
  getUserAssessmentAttempts: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.USER.ASSESSMENT_ATTEMPTS),
      'Failed to fetch assessment attempts'
    );
  },
};

const progressService = {
  getUserEnrollments: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.USER.ENROLLMENTS),
      'Failed to fetch enrollments'
    );
  },

  getUserProgress: async courseId => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.USER.PROGRESS.COURSE(courseId)),
      `Failed to fetch progress for course ${courseId}`
    );
  },

  getUserProgressStats: async () => {
    try {
      return await handleRequest(
        async () => await apiClient.get(API_ENDPOINTS.USER.PROGRESS.STATS),
        'Failed to fetch progress statistics'
      );
    } catch (error) {
      if (!ALLOW_MOCK_FALLBACK) {
        throw error;
      }

      logWarning('Falling back to mock progress statistics data', { error });
      return {
        totalCourses: 0,
        coursesInProgress: 0,
        coursesCompleted: 0,
        totalLessons: 0,
        completedLessons: 0,
        completionPercentage: 0,
        hoursSpent: 0,
        assessmentsCompleted: 0,
        completedAssessments: 0,
        recentActivity: [],
      };
    }
  },
};

const noteService = {
  getUserNotes: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.NOTE.BASE),
      'Failed to fetch notes'
    );
  },

  getNotesForLesson: async lessonId => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.NOTE.BASE, {
          params: { lesson: lessonId },
        }),
      `Failed to fetch notes for lesson ${lessonId}`
    );
  },

  createNote: async noteData => {
    return handleRequest(
      async () => await apiClient.post(API_ENDPOINTS.NOTE.BASE, noteData),
      'Failed to create note'
    );
  },

  updateNote: async (noteId, noteData) => {
    return handleRequest(
      async () =>
        await apiClient.put(API_ENDPOINTS.NOTE.DETAIL(noteId), noteData),
      `Failed to update note ${noteId}`
    );
  },

  deleteNote: async noteId => {
    return handleRequest(
      async () => await apiClient.delete(API_ENDPOINTS.NOTE.DETAIL(noteId)),
      `Failed to delete note ${noteId}`
    );
  },
};

const forumService = {
  getCourseDiscussions: async courseSlug => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.COURSE.DISCUSSIONS(courseSlug)),
      `Failed to fetch discussions for course ${courseSlug}`
    );
  },

  getDiscussion: async (courseSlug, discussionId) => {
    return handleRequest(
      async () =>
        await apiClient.get(
          API_ENDPOINTS.COURSE.DISCUSSION(courseSlug, discussionId)
        ),
      `Failed to fetch discussion ${discussionId}`
    );
  },

  createDiscussion: async (courseSlug, discussionData) => {
    return handleRequest(
      async () =>
        await apiClient.post(
          API_ENDPOINTS.COURSE.DISCUSSIONS(courseSlug),
          discussionData
        ),
      'Failed to create discussion'
    );
  },

  addDiscussionReply: async (courseSlug, discussionId, replyData) => {
    return handleRequest(
      async () =>
        await apiClient.post(
          API_ENDPOINTS.COURSE.DISCUSSION_REPLIES(courseSlug, discussionId),
          replyData
        ),
      `Failed to add reply to discussion ${discussionId}`
    );
  },
};

const virtualLabService = {
  getLabDetails: async labId => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.LAB.DETAILS(labId)),
      `Failed to fetch lab ${labId}`
    );
  },

  startLabSession: async labId => {
    return handleRequest(
      async () => await apiClient.post(API_ENDPOINTS.LAB.START(labId)),
      `Failed to start lab ${labId}`
    );
  },

  submitLabSolution: async (labId, solutionData) => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.LAB.SUBMIT(labId), solutionData),
      `Failed to submit solution for lab ${labId}`
    );
  },
};

const categoryService = {
  getAllCategories: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.CATEGORY.BASE),
      'Failed to fetch categories'
    );
  },

  getCoursesByCategory: async categorySlug => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.CATEGORY.COURSES(categorySlug)),
      `Failed to fetch courses for category ${categorySlug}`
    );
  },
};

const certificateService = {
  getUserCertificates: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.CERTIFICATE.BASE),
      'Failed to fetch certificates'
    );
  },

  generateCertificate: async courseSlug => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.COURSE.CERTIFICATE(courseSlug)),
      `Failed to generate certificate for course ${courseSlug}`
    );
  },

  verifyCertificate: async verificationCode => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.CERTIFICATE.VERIFY(verificationCode)),
      'Certificate verification failed'
    );
  },
};

const blogService = {
  getLatestPosts: async (limit = 3) => {
    return handleRequest(
      async () =>
        await apiClient.get(API_ENDPOINTS.BLOG.POSTS, { params: { limit } }),
      'Failed to fetch latest blog posts'
    );
  },

  getPostBySlug: async slug => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.BLOG.POST_BY_SLUG(slug)),
      `Failed to fetch blog post ${slug}`
    );
  },
};

const systemService = {
  checkApiStatus: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.SYSTEM.STATUS),
      'API status check failed'
    );
  },

  checkDbStatus: async () => {
    return handleRequest(
      async () => await apiClient.get(API_ENDPOINTS.SYSTEM.DB_STATUS),
      'Database status check failed'
    );
  },
};

const statisticsService = {
  getPlatformStats: async () => {
    try {
      return await handleRequest(
        async () => await apiClient.get(API_ENDPOINTS.STATISTICS.PLATFORM),
        'Failed to fetch platform statistics'
      );
    } catch (error) {
      if (
        !ALLOW_MOCK_FALLBACK ||
        !(error.response && error.response.status === 404)
      ) {
        throw error;
      }

      logWarning('Statistics endpoint not available, using mock data', {
        error,
      });
      return {
        totalCourses: 150,
        totalStudents: 12500,
        totalInstructors: 48,
      };
    }
  },

  getUserLearningStats: async () => {
    try {
      return await handleRequest(
        async () => await apiClient.get(API_ENDPOINTS.STATISTICS.USER),
        'Failed to fetch user learning statistics'
      );
    } catch (error) {
      if (
        !ALLOW_MOCK_FALLBACK ||
        !(error.response && error.response.status === 404)
      ) {
        throw error;
      }

      logWarning('User statistics endpoint not available, using mock data', {
        error,
      });
      return {
        coursesCompleted: 0,
        hoursSpent: 0,
        averageScore: 0,
      };
    }
  },

  getInstructorTeachingStats: async () => {
    try {
      return await handleRequest(
        async () => await apiClient.get(API_ENDPOINTS.STATISTICS.INSTRUCTOR),
        'Failed to fetch instructor teaching statistics'
      );
    } catch (error) {
      if (
        !ALLOW_MOCK_FALLBACK ||
        !(error.response && error.response.status === 404)
      ) {
        throw error;
      }

      logWarning(
        'Instructor statistics endpoint not available, using mock data',
        { error }
      );
      return {
        totalStudents: 0,
        coursesCreated: 0,
        averageRating: 0,
      };
    }
  },
};

const testimonialService = {
  getFeaturedTestimonials: async (limit = 3) => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.get(API_ENDPOINTS.TESTIMONIAL.FEATURED, {
            params: { limit },
          }),
        'Failed to fetch featured testimonials'
      );
    } catch (error) {
      if (
        !ALLOW_MOCK_FALLBACK ||
        !(error.response && error.response.status === 404)
      ) {
        throw error;
      }

      logWarning('Testimonials endpoint not available, using mock data', {
        error,
      });
      return [
        {
          id: 1,
          name: 'Jane Smith',
          role: 'Software Engineer',
          content:
            'This platform helped me transition from a junior to senior developer in just 6 months.',
          rating: 5,
          avatar: '/images/avatars/avatar-1.jpg',
        },
        {
          id: 2,
          name: 'Michael Johnson',
          role: 'Data Scientist',
          content:
            'The data science courses here are comprehensive and practical. I use what I learned daily.',
          rating: 5,
          avatar: '/images/avatars/avatar-2.jpg',
        },
        {
          id: 3,
          name: 'Sarah Williams',
          role: 'UX Designer',
          content:
            'The design courses completely changed how I approach user experience. Highly recommended!',
          rating: 4,
          avatar: '/images/avatars/avatar-3.jpg',
        },
      ];
    }
  },

  getAllTestimonials: async (params = {}) => {
    try {
      return await handleRequest(
        async () =>
          await apiClient.get(API_ENDPOINTS.TESTIMONIAL.BASE, { params }),
        'Failed to fetch testimonials'
      );
    } catch (error) {
      if (
        !ALLOW_MOCK_FALLBACK ||
        !(error.response && error.response.status === 404)
      ) {
        throw error;
      }

      logWarning('Testimonials endpoint not available, using mock data', {
        error,
      });
      return [
        {
          id: 1,
          name: 'Jane Smith',
          role: 'Software Engineer',
          content:
            'This platform helped me transition from a junior to senior developer in just 6 months.',
          rating: 5,
          avatar: '/images/avatars/avatar-1.jpg',
        },
        {
          id: 2,
          name: 'Michael Johnson',
          role: 'Data Scientist',
          content:
            'The data science courses here are comprehensive and practical. I use what I learned daily.',
          rating: 5,
          avatar: '/images/avatars/avatar-2.jpg',
        },
        {
          id: 3,
          name: 'Sarah Williams',
          role: 'UX Designer',
          content:
            'The design courses completely changed how I approach user experience. Highly recommended!',
          rating: 4,
          avatar: '/images/avatars/avatar-3.jpg',
        },
      ];
    }
  },

  submitTestimonial: async testimonialData => {
    return handleRequest(
      async () =>
        await apiClient.post(API_ENDPOINTS.TESTIMONIAL.BASE, testimonialData),
      'Failed to submit testimonial'
    );
  },
};

const apiUtils = {
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

const api = {
  auth: authService,
  subscription: subscriptionService,
  course: courseService,
  assessment: assessmentService,
  progress: progressService,
  note: noteService,
  forum: forumService,
  virtualLab: virtualLabService,
  category: categoryService,
  certificate: certificateService,
  blog: blogService,
  system: systemService,
  statistics: statisticsService,
  testimonial: testimonialService,

  login: authService.login,
  register: authService.register,
  getCurrentUser: authService.getCurrentUser,
  logout: authService.logout,
  isAuthenticated: authService.isAuthenticated,

  utils: apiUtils,
};

export {
  apiClient,
  apiUtils,
  assessmentService,
  authService,
  blogService,
  categoryService,
  certificateService,
  courseService,
  forumService,
  noteService,
  progressService,
  statisticsService,
  subscriptionService,
  systemService,
  testimonialService,
  virtualLabService
};

export default api;
