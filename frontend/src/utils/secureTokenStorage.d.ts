/**
 * TypeScript declarations for secureTokenStorage.js
 * Version: 2.3.0
 * Date: 2025-05-24 18:21:41
 *
 * This file provides TypeScript definitions for the secure token storage utility
 * that handles authentication tokens with memory-first storage and proper expiration handling.
 */

/**
 * User data interface - adjust properties based on your actual user object structure
 */
export interface UserData {
  id: string | number;
  email?: string;
  name?: string;
  role?: string;
  [key: string]: any; // Allow additional properties
}

/**
 * Arguments for storeAuthData compatibility function
 */
export interface StoreAuthDataArgs {
  token: string;
  refreshToken?: string;
  user?: UserData;
}

/**
 * Main secure token storage interface
 */
export interface SecureTokenStorage {
  /**
   * Get access token from storage (backward compatibility)
   * @returns Access token or null
   */
  getAccessToken(): string | null;

  /**
   * Get refresh token from storage (backward compatibility)
   * @returns Refresh token or null
   */
  getRefreshToken(): string | null;

  /**
   * Store complete auth data with enhanced security
   * @param accessToken - JWT access token
   * @param refreshToken - JWT refresh token
   * @param rememberMe - Whether to persist tokens (default: false)
   */
  setAuthData(
    accessToken: string,
    refreshToken?: string,
    rememberMe?: boolean
  ): void;

  /**
   * Update access token (e.g., after refresh)
   * @param accessToken - New JWT access token
   */
  updateAccessToken(accessToken: string): void;

  /**
   * Update refresh token (when rotation is enabled)
   * @param refreshToken - New JWT refresh token
   */
  updateRefreshToken(refreshToken: string): void;

  /**
   * Clear all authentication data
   */
  clearAuthData(): void;

  /**
   * Check if access token is valid and not expired
   * @returns True if token is valid
   */
  isTokenValid(): boolean;

  /**
   * Check if token will expire soon (within 5 minutes)
   * @returns True if token will expire soon
   */
  willTokenExpireSoon(): boolean;

  /**
   * Check if user has chosen to persist tokens
   * @returns True if persistence is enabled
   */
  isPersistenceEnabled(): boolean;

  /**
   * Get valid token, with enhanced format compatibility
   * @returns Valid token or null
   */
  getValidToken(): string | null;

  /**
   * Refreshes token expiry to maintain session
   */
  refreshTokenExpiry(): void;

  /**
   * Store user data with memory-first approach
   * @param userData - User data to store
   */
  setUserData(userData: UserData): void;

  /**
   * Get user data from storage with memory-first approach
   * @returns User data or null
   */
  getUserData(): UserData | null;

  /**
   * COMPATIBILITY: Legacy function expected by AuthContext
   * Store authentication data with object-style parameters
   * @param args - Object containing token, refreshToken, and user data
   */
  storeAuthData(args: StoreAuthDataArgs): void;

  /**
   * COMPATIBILITY: Legacy function expected by AuthContext
   * Get access token (alias for getValidToken for backward compatibility)
   * @returns Access token or null
   */
  getToken(): string | null;
}

// Individual function exports
export declare function getAccessToken(): string | null;
export declare function getRefreshToken(): string | null;
export declare function setAuthData(
  accessToken: string,
  refreshToken?: string,
  rememberMe?: boolean
): void;
export declare function updateAccessToken(accessToken: string): void;
export declare function updateRefreshToken(refreshToken: string): void;
export declare function clearAuthData(): void;
export declare function isTokenValid(): boolean;
export declare function willTokenExpireSoon(): boolean;
export declare function isPersistenceEnabled(): boolean;
export declare function getValidToken(): string | null;
export declare function refreshTokenExpiry(): void;
export declare function setUserData(userData: UserData): void;
export declare function getUserData(): UserData | null;
export declare function storeAuthData(args: StoreAuthDataArgs): void;
export declare function getToken(): string | null;

// Default export
declare const secureTokenStorage: SecureTokenStorage;
export default secureTokenStorage;
