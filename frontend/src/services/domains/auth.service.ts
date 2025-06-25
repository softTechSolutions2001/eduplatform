/**
 * File: src/services/domains/auth.service.ts
 * Version: 1.0.1
 * Modified: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Authentication service for user login, registration, and token management
 * Enhanced with better error handling, type safety, and additional features
 */

import axios from 'axios';
import { logWarning } from '../../utils/logger'; // Added missing import
import secureTokenStorage from '../../utils/secureTokenStorage';
import { apiClient, refreshAuthToken } from '../http/apiClient';
import { DEBUG_MODE, TOKEN_STORAGE_KEYS } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

// Type definitions for better type safety
interface LoginCredentials {
    email: string;
    password: string;
    rememberMe?: boolean;
}

interface UserData {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
    [key: string]: any;
}

interface PasswordData {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
}

interface AuthResponse {
    access: string;
    refresh: string;
    user?: any;
}

interface SocialAuthResponse {
    authorizationUrl: string;
    success: boolean;
}

export const authService = {
    /**
     * Authenticate user with email and password
     */
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        try {
            console.log('Starting authentication process');

            // Validate input
            if (!credentials?.email || !credentials?.password) {
                throw new Error('Email and password are required');
            }

            // Clear any existing auth data
            secureTokenStorage.clearAuthData();

            const response = await axios.post(API_ENDPOINTS.AUTH.LOGIN, {
                email: credentials.email.toLowerCase().trim(), // Normalize email
                password: credentials.password,
            });

            if (!response.data || !response.data.access) {
                console.error('No token in response', response.data);
                throw new Error('Invalid response from authentication server');
            }

            console.log('Authentication successful');

            // Store auth data securely
            secureTokenStorage.setAuthData(
                response.data.access,
                response.data.refresh,
                credentials.rememberMe || false
            );

            return response.data;
        } catch (error: any) {
            console.error('Authentication failed:', error);

            const errorMsg =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                'Login failed. Please check your credentials.';

            throw new Error(errorMsg);
        }
    },

    /**
     * Register new user
     */
    register: async (userData: UserData) => {
        // Validate required fields
        if (!userData?.email || !userData?.password) {
            throw new Error('Email and password are required');
        }

        // Normalize email
        const normalizedData = {
            ...userData,
            email: userData.email.toLowerCase().trim()
        };

        return handleRequest(
            async () => await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, normalizedData),
            'Registration failed'
        );
    },

    /**
     * Verify user email with token
     */
    verifyEmail: async (token: string) => {
        if (!token) {
            throw new Error('Verification token is required');
        }

        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.AUTH.VERIFY_EMAIL, { token }),
            'Email verification failed'
        );
    },

    /**
     * Request password reset
     */
    requestPasswordReset: async (email: string) => {
        if (!email) {
            throw new Error('Email is required');
        }

        const normalizedEmail = email.toLowerCase().trim();

        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD_REQUEST, {
                    email: normalizedEmail,
                }),
            'Password reset request failed'
        );
    },

    /**
     * Reset password with token
     */
    resetPassword: async (token: string, password: string) => {
        if (!token || !password) {
            throw new Error('Token and new password are required');
        }

        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
                    token,
                    password,
                }),
            'Password reset failed'
        );
    },

    /**
     * Refresh authentication token
     */
    refreshToken: async () => {
        try {
            return await refreshAuthToken();
        } catch (error) {
            console.error('Token refresh failed:', error);
            throw error;
        }
    },

    /**
     * Logout user and clean up storage
     */
    logout: async (navigate?: Function) => {
        try {
            // Clear secure token storage
            secureTokenStorage.clearAuthData();

            // Clear all auth-related localStorage items
            const authKeys = [
                TOKEN_STORAGE_KEYS.ACCESS,
                TOKEN_STORAGE_KEYS.REFRESH,
                TOKEN_STORAGE_KEYS.USER,
                TOKEN_STORAGE_KEYS.PERSISTENCE,
                'currentUser',
                'userRole',
                'userProfile',
                'subscription',
                'oauth_state',
                'isAuthenticated'
            ];

            authKeys.forEach(key => {
                localStorage.removeItem(key);
            });

            // Clear OAuth-related sessionStorage
            const sessionKeys = [
                'oauth_code_verifier',
                'oauth_code',
                'oauth_code_expiry'
            ];

            sessionKeys.forEach(key => {
                sessionStorage.removeItem(key);
            });

            console.log('Logout completed, storage cleared');

            // Navigate to login page
            if (typeof navigate === 'function') {
                navigate('/login', { replace: true });
            } else if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error during logout:', error);
            // Still try to navigate even if cleanup fails
            if (typeof navigate === 'function') {
                navigate('/login', { replace: true });
            }
        }
    },

    /**
     * Added missing method: Logout from all devices
     */
    logoutFromAllDevices: async () => {
        return handleRequest(
            async () => await apiClient.post(`${API_ENDPOINTS.AUTH.LOGOUT}all/`),
            'Failed to logout from all devices'
        );
    },

    /**
     * Get current user data
     */
    getCurrentUser: async (cacheBuster?: string) => {
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
        } catch (error: any) {
            if (error.response?.status === 401) {
                console.log('User not authenticated');
                // Clear invalid tokens
                secureTokenStorage.clearAuthData();
                return null;
            }

            console.error('Error fetching user data:', error);
            return null;
        }
    },

    /**
     * Update user profile
     */
    updateProfile: async (userData: Partial<UserData>) => {
        if (!userData || Object.keys(userData).length === 0) {
            throw new Error('Profile data is required');
        }

        return handleRequest(
            async () =>
                await apiClient.put(API_ENDPOINTS.USER.UPDATE_PROFILE, userData),
            'Failed to update profile'
        );
    },

    /**
     * Change user password
     */
    changePassword: async (passwordData: PasswordData) => {
        // Validate password data
        if (!passwordData.currentPassword || !passwordData.newPassword) {
            throw new Error('Current password and new password are required');
        }

        if (passwordData.newPassword !== passwordData.confirmPassword) {
            throw new Error('New password and confirmation do not match');
        }

        if (passwordData.newPassword.length < 8) {
            throw new Error('New password must be at least 8 characters long');
        }

        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, passwordData),
            'Failed to change password'
        );
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: (): boolean => {
        return secureTokenStorage.isTokenValid();
    },

    /**
     * Get social authentication URL with enhanced PKCE and state parameter support
     */
    getSocialAuthUrl: async (
        provider: string,
        codeChallenge: string,
        state: string
    ): Promise<SocialAuthResponse> => {
        try {
            console.log(`Getting social auth URL for provider: ${provider}`);

            // Validate inputs
            if (!provider) {
                throw new Error('Provider is required');
            }

            if (!['google', 'github', 'facebook'].includes(provider.toLowerCase())) {
                throw new Error(`Unsupported provider: ${provider}`);
            }

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
            const authUrl = response.data?.authorizationUrl || response.data?.authorization_url;

            if (!authUrl) {
                console.error('Invalid response from social auth URL endpoint:', response);
                throw new Error('Invalid response format from authorization server');
            }

            return {
                authorizationUrl: authUrl,
                success: true,
            };
        } catch (error: any) {
            console.error(`Failed to get ${provider} auth URL:`, error);

            // Development fallback for testing when API is not available
            if (process.env.NODE_ENV === 'development') {
                logWarning('Using development fallback for social auth URL');

                try {
                    const fallbackUrl = this.buildFallbackSocialAuthUrl(provider, codeChallenge, state);
                    return {
                        authorizationUrl: fallbackUrl,
                        success: true,
                    };
                } catch (fallbackError) {
                    console.error('Fallback URL generation failed:', fallbackError);
                }
            }

            throw error;
        }
    },

    /**
     * Build fallback social auth URL for development
     */
    buildFallbackSocialAuthUrl: (
        provider: string,
        codeChallenge?: string,
        state?: string
    ): string => {
        // Get client IDs from environment variables
        const clientId = provider === 'google'
            ? import.meta.env.VITE_GOOGLE_CLIENT_ID ||
            '99067790447-go0pcefo3nt1b9d0udei65u0or6nb0a0.apps.googleusercontent.com'
            : provider === 'github'
                ? import.meta.env.VITE_GITHUB_CLIENT_ID || 'your-github-client-id'
                : import.meta.env.VITE_FACEBOOK_CLIENT_ID || 'your-facebook-client-id';

        const redirectUri = encodeURIComponent(
            `${window.location.origin}/auth/social/${provider}/callback`
        );

        let authUrl: string;
        let scope: string;

        switch (provider.toLowerCase()) {
            case 'google':
                scope = encodeURIComponent('email profile');
                authUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
                break;
            case 'github':
                scope = encodeURIComponent('user:email');
                authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
                break;
            case 'facebook':
                scope = encodeURIComponent('email');
                authUrl = `https://www.facebook.com/v12.0/dialog/oauth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
                break;
            default:
                throw new Error(`Unsupported provider for fallback: ${provider}`);
        }

        // Add PKCE parameters if provided
        if (codeChallenge) {
            authUrl += `&code_challenge=${codeChallenge}&code_challenge_method=S256`;
        }

        // Add state parameter if provided
        if (state) {
            authUrl += `&state=${state}`;
        }

        return authUrl;
    },

    /**
     * Process social authentication callback
     */
    processSocialAuth: async (
        provider: string,
        code: string,
        codeVerifier?: string
    ): Promise<AuthResponse> => {
        try {
            // Validate inputs
            if (!provider || !code) {
                throw new Error('Provider and authorization code are required');
            }

            // Only log part of the code for security
            if (DEBUG_MODE) {
                console.log(
                    `Processing ${provider} auth with code length: ${code?.length || 0}`
                );
                console.log(`Code verifier provided: ${codeVerifier ? 'Yes' : 'No'}`);
            }

            const isDevelopment = process.env.NODE_ENV === 'development';
            const isUsingDevVerifier = isDevelopment && codeVerifier === 'dev-verifier';

            // Prepare request body
            const requestBody: any = {
                code,
                provider: provider.toLowerCase(),
                redirect_uri: `${window.location.origin}/auth/social/${provider}/callback`,
            };

            // Only include code_verifier if it exists and it's not a development fallback
            if (codeVerifier && (!isUsingDevVerifier || (isUsingDevVerifier && DEBUG_MODE))) {
                requestBody.code_verifier = codeVerifier;
            }

            const response = await apiClient.post(
                API_ENDPOINTS.AUTH.SOCIAL_AUTH_COMPLETE(),
                requestBody
            );

            if (!response.data || !response.data.access) {
                console.error('No token in response', response.data);
                throw new Error('Invalid response from authentication server');
            }

            console.log(`${provider} authentication successful`);

            // Store auth data (social logins typically remember the user)
            secureTokenStorage.setAuthData(
                response.data.access,
                response.data.refresh,
                true
            );

            return response.data;
        } catch (error: any) {
            // Special handling for duplicate calls in development
            if (this.handleDevelopmentDuplicateCall(error, provider)) {
                const cachedUser = JSON.parse(
                    window.localStorage.getItem('currentUser') || '{}'
                );
                return {
                    access: 'dev-mode-duplicate-call',
                    refresh: 'dev-mode-duplicate-call',
                    user: cachedUser,
                };
            }

            console.error(`${provider} authentication failed:`, error);

            const errorMsg =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                `${provider} login failed. Please try again.`;

            throw new Error(errorMsg);
        }
    },

    /**
     * Handle development duplicate call scenario
     */
    handleDevelopmentDuplicateCall: (error: any, provider: string): boolean => {
        return (
            process.env.NODE_ENV === 'development' &&
            error.response?.status === 400 &&
            error.response?.data?.detail?.includes('code for token') &&
            window.localStorage.getItem('isAuthenticated') === 'true'
        );
    },

    /**
     * Validate token without making API call
     */
    validateTokenLocally: (): boolean => {
        try {
            return secureTokenStorage.isTokenValid();
        } catch (error) {
            console.error('Error validating token locally:', error);
            return false;
        }
    },

    /**
     * Get stored user data without API call
     */
    getCachedUser: () => {
        try {
            const userData = localStorage.getItem('currentUser');
            return userData ? JSON.parse(userData) : null;
        } catch (error) {
            console.error('Error getting cached user:', error);
            return null;
        }
    },

    /**
     * Check if user has specific role
     */
    hasRole: (role: string): boolean => {
        try {
            const userRole = localStorage.getItem('userRole');
            return userRole === role;
        } catch (error) {
            console.error('Error checking user role:', error);
            return false;
        }
    },
};
