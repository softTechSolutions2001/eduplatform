/**
 * File: frontend/src/utils/authPersist.js
 * Version: 1.1.1
 * Date: 2025-05-25 (merged with backward compatibility)
 * Author: nanthiniSanthanam, cadsanthanam (bugfix), mohithasanthanam (token format fix)
 * Last Modified: 2025-05-25 UTC
 *
 * Comprehensive token management system that solves login persistence issues by:
 * 1. Storing tokens with explicit expiration times
 * 2. Adding mechanisms to refresh and validate tokens
 * 3. Providing consistent storage/retrieval API for auth data
 * 4. Supporting both session and permanent storage models
 *
 * CRITICAL FIXES APPLIED:
 * 1. EXPORTED missing constants (DEFAULT_EXPIRY_HOURS, INSTRUCTOR_EXPIRY_HOURS)
 * 2. Added compatibility functions (setAuthData wrapper)
 * 3. Fixed null safety in isTokenValid function
 * 4. Added all constants to default export
 * 5. ADDED backward compatibility alias getToken() -> getValidToken()
 *
 * This utility works in conjunction with AuthContext to ensure users remain
 * authenticated across page refreshes and browser sessions, especially important
 * for instructor workflows that may span multiple days.
 *
 * Fixed token expiry format to ensure compatibility with secureTokenStorage.js
 *
 * Connected files:
 * - frontend/src/utils/secureTokenStorage.js - Also handles token storage
 * - frontend/src/contexts/AuthContext.jsx - Uses these utilities for auth state
 * - frontend/src/services/api.js - Uses tokens for request authorization
 *
 * Variables to modify:
 * - DEFAULT_EXPIRY_HOURS: Change default session length (24 hours)
 * - INSTRUCTOR_EXPIRY_HOURS: Extended session for instructors (48 hours)
 */

// Storage keys for authentication data
const TOKEN_EXPIRY_KEY = 'tokenExpiry';
const TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const USER_DATA_KEY = 'userData';
const USER_ROLE_KEY = 'userRole';

// FIXED: Export constants so they can be accessed by AuthContext
export const DEFAULT_EXPIRY_HOURS = 24;
export const INSTRUCTOR_EXPIRY_HOURS = 48;

/**
 * Store authentication data with expiration
 * @param {Object} authData - Authentication data including token and user info
 * @param {number} expiryHours - Hours until token expiration
 */
export const storeAuthData = (authData, expiryHours = DEFAULT_EXPIRY_HOURS) => {
  if (!authData || !authData.token) {
    console.error('Invalid authentication data');
    return;
  }

  try {
    // Calculate expiration time
    const expiryTime = new Date();
    expiryTime.setHours(expiryTime.getHours() + expiryHours);

    // Store token with expiration
    localStorage.setItem(TOKEN_KEY, authData.token);

    // FIXED: Store expiry as milliseconds timestamp (not ISO string)
    // to match secureTokenStorage.js expectations
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.getTime().toString());

    // Store refresh token if available
    if (authData.refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, authData.refreshToken);
    }

    // Store user data if available
    if (authData.user) {
      localStorage.setItem(USER_DATA_KEY, JSON.stringify(authData.user));

      // Extract and store role separately for easier access
      if (authData.user.role) {
        localStorage.setItem(USER_ROLE_KEY, authData.user.role);
      }
    }

    console.log(`Authentication data stored. Expires: ${expiryTime}`);
  } catch (error) {
    console.error('Error storing authentication data:', error);
  }
};

/**
 * Check if stored token is still valid
 * @returns {boolean} - Whether the token is valid
 */
export const isTokenValid = () => {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const expiryString = localStorage.getItem(TOKEN_EXPIRY_KEY);

    // No token or expiry means token is invalid
    if (!token || !expiryString) {
      return false;
    }

    // FIXED: Handle both formats for future compatibility + null safety
    let expiryMs;
    if (expiryString && expiryString.includes('-')) {
      // Handle ISO date string format
      expiryMs = new Date(expiryString).getTime();
    } else {
      // Handle millisecond timestamp format
      expiryMs = parseInt(expiryString, 10);
    }

    // Check if token is expired
    return Date.now() < expiryMs && !!token;
  } catch (error) {
    console.error('Error checking token validity:', error);
    return false;
  }
};

/**
 * Get the stored authentication token if valid
 * @returns {string|null} - The token if valid, null otherwise
 */
export const getValidToken = () => {
  return isTokenValid() ? localStorage.getItem(TOKEN_KEY) : null;
};

/**
 * Get stored user data
 * @returns {Object|null} - User data or null if not found
 */
export const getUserData = () => {
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error getting user data:', error);
    return null;
  }
};

/**
 * Get stored user role
 * @returns {string|null} - User role or null if not found
 */
export const getUserRole = () => {
  return localStorage.getItem(USER_ROLE_KEY);
};

/**
 * Clear all authentication data
 */
export const clearAuthData = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
  localStorage.removeItem(USER_DATA_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
};

/**
 * Refresh token expiration (extend session)
 * @param {number} expiryHours - Hours until token expiration
 */
export const refreshTokenExpiry = (expiryHours = DEFAULT_EXPIRY_HOURS) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return;

  const expiryTime = new Date();
  expiryTime.setHours(expiryTime.getHours() + expiryHours);

  // FIXED: Store expiry as milliseconds timestamp
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.getTime().toString());

  console.log(`Token expiry extended to: ${expiryTime}`);
};

/**
 * Store new access token while maintaining other auth data
 * @param {string} accessToken - New access token
 */
export const updateAccessToken = accessToken => {
  if (!accessToken) {
    console.error('Invalid access token for update');
    return;
  }

  localStorage.setItem(TOKEN_KEY, accessToken);

  // Refresh expiry time
  refreshTokenExpiry();
};

/**
 * Store new refresh token
 * @param {string} refreshToken - New refresh token
 */
export const updateRefreshToken = refreshToken => {
  if (!refreshToken) {
    console.error('Invalid refresh token for update');
    return;
  }

  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

/**
 * Get stored refresh token
 * @returns {string|null} - Refresh token or null if not found
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Determine if user should have extended session (for instructors)
 * @param {Object} userData - User data with role information
 * @returns {boolean} - Whether user should have extended session
 */
export const shouldHaveExtendedSession = userData => {
  if (!userData) return false;

  // Check user role for instructor or admin
  const role = userData.role?.toLowerCase() || '';
  return role === 'instructor' || role === 'administrator' || role === 'admin';
};

/**
 * Calculate appropriate session duration based on user role
 * @param {Object} userData - User data with role information
 * @returns {number} - Session duration in hours
 */
export const getSessionDuration = userData => {
  return shouldHaveExtendedSession(userData)
    ? INSTRUCTOR_EXPIRY_HOURS
    : DEFAULT_EXPIRY_HOURS;
};

/**
 * FIXED: Added compatibility function for secureTokenStorage API
 * Set authentication data from JWT tokens
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 * @param {boolean} rememberMe - Whether to persist tokens across sessions
 */
export const setAuthData = (accessToken, refreshToken, rememberMe = false) => {
  if (!accessToken) {
    console.error('Invalid access token');
    return;
  }

  try {
    // Store tokens
    localStorage.setItem(TOKEN_KEY, accessToken);

    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }

    // Set token expiry (default 24 hours from now)
    const expiryTime = new Date();
    expiryTime.setHours(expiryTime.getHours() + DEFAULT_EXPIRY_HOURS);

    // FIXED: Store expiry as milliseconds timestamp
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.getTime().toString());

    console.log(`Auth data stored successfully. Expires: ${expiryTime}`);
  } catch (error) {
    console.error('Failed to store auth data:', error);
  }
};

// ──────── BACKWARD COMPATIBILITY ALIAS ────────
/**
 * Legacy alias for getValidToken() - kept for backward compatibility
 * @deprecated Use getValidToken() instead
 * @returns {string|null} - The token if valid, null otherwise
 */
export const getToken = () => getValidToken();

// FIXED: Added default export with ALL required functions and constants
export default {
  storeAuthData,
  isTokenValid,
  getValidToken,
  getUserData,
  getUserRole,
  clearAuthData,
  refreshTokenExpiry,
  updateAccessToken,
  updateRefreshToken,
  getRefreshToken,
  shouldHaveExtendedSession,
  getSessionDuration,
  setAuthData,
  // FIXED: Added backward compatibility alias to default export
  getToken,
  // FIXED: Added missing constants to default export
  DEFAULT_EXPIRY_HOURS,
  INSTRUCTOR_EXPIRY_HOURS,
};
