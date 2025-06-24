/**
 * File: frontend/src/contexts/AuthContext.jsx
 * Version: 5.1.4
 * Date: 2025-06-23
 * Author: mohithasanthanam (updated by saiacupuncture)
 * Last Modified: 2025-06-23 16:08:32 UTC
 *
 * Enhanced Authentication Context Provider
 *
 * CRITICAL FIXES v5.1.4:
 * - FIXED: Spinner issue by ensuring both authChecked=true and isLoading=false in StrictMode
 * - MAINTAINED: Complete backward compatibility with existing consumers
 *
 * Previous fixes v5.1.3:
 * - Added useRef guards to prevent duplicate authentication checks
 * - Prevented multiple /api/user/me calls from React StrictMode
 * - Fixed initialization race conditions
 * - Improved error handling and state management
 */

import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import secureTokenStorage from '../utils/secureTokenStorage';
import {
    ACCESS_LEVELS,
    getUserAccessLevel as getUnifiedUserAccessLevel,
    normalizeUserRole,
    SUBSCRIPTION_ACCESS_MAPPING,
} from '../utils/validation';

// FIXED: Replace CommonJS require with ES import and proper fallback
import * as persisted from '../utils/authPersist';
const authPersist =
    persisted && Object.keys(persisted).length ? persisted : secureTokenStorage;

// Helper functions for PKCE and security (for social login)
const generateRandomString = length => {
    const array = new Uint8Array(length);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte =>
        ('0' + (byte & 0xff).toString(16)).slice(-2)
    ).join('');
};

const sha256 = async plain => {
    const encoder = new TextEncoder();
    const data = encoder.encode(plain);
    return await window.crypto.subtle.digest('SHA-256', data);
};

const base64URLEncode = arrayBuffer => {
    return btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
};

const generateCodeChallenge = async codeVerifier => {
    const hashBuffer = await sha256(codeVerifier);
    return base64URLEncode(hashBuffer);
};

// Create context
const AuthContext = createContext(null);

// Custom hook to use the auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// Auth provider component
export const AuthProvider = ({ children }) => {
    // CRITICAL FIX: Add refs to prevent duplicate initialization
    const didInitAuth = useRef(false);
    const isInitializing = useRef(false);
    const refreshIntervalRef = useRef(null);

    // FIXED: Role normalization helper - uses unified validation
    const NORMALIZE_ROLE = useCallback(role => {
        return normalizeUserRole(role);
    }, []);

    // Core authentication state
    const [currentUser, setCurrentUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [authChecked, setAuthChecked] = useState(false);

    // Enhanced state from v4.1.1
    const [userRole, setUserRole] = useState(null);
    const [subscription, setSubscription] = useState(null);
    const [accessLevel, setAccessLevel] = useState(ACCESS_LEVELS.GUEST);

    const navigate = useNavigate();

    // Use unified access level mapping
    const ACCESS_LEVEL_MAP = SUBSCRIPTION_ACCESS_MAPPING;

    // FIXED: Helper function to determine final role with normalization and fallbacks
    const determineFinalRole = useCallback(
        userData => {
            const normalizedRole = NORMALIZE_ROLE(userData.role);

            // Check for instructor role (handles "Instructor", "instructor", etc.)
            if (
                normalizedRole === 'instructor' ||
                userData.isInstructor ||
                userData.is_instructor
            ) {
                return 'instructor';
            }

            // Check for admin role
            if (normalizedRole === 'admin' || normalizedRole === 'administrator') {
                return 'admin';
            }

            // Default to student
            return 'student';
        },
        [NORMALIZE_ROLE]
    );

    // Helper function to get stored token from multiple sources
    const getStoredToken = useCallback(() => {
        if (authPersist && typeof authPersist.getValidToken === 'function') {
            return authPersist.getValidToken();
        }
        // FIXED: Changed getToken to getValidToken
        return (
            secureTokenStorage.getValidToken() ||
            localStorage.getItem('accessToken') ||
            localStorage.getItem('token')
        );
    }, []);

    // Helper function to check if token is valid
    const isTokenValid = useCallback(() => {
        if (authPersist && typeof authPersist.isTokenValid === 'function') {
            return authPersist.isTokenValid();
        }
        return secureTokenStorage.isTokenValid();
    }, []);

    // Helper function to reset auth state
    const resetAuthState = useCallback(() => {
        // Clear all possible storage locations
        if (authPersist && typeof authPersist.clearAuthData === 'function') {
            authPersist.clearAuthData();
        }
        secureTokenStorage.clearAuthData();

        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('currentUser');
        localStorage.removeItem('userRole');
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('oauth_state');
        // FIXED: Added missing authPersist keys cleanup
        localStorage.removeItem('tokenExpiry');
        localStorage.removeItem('userData');
        sessionStorage.removeItem('oauth_code_verifier');
        sessionStorage.removeItem('oauth_code');
        sessionStorage.removeItem('oauth_code_expiry');

        setCurrentUser(null);
        setUserRole(null);
        setSubscription(null);
        setAccessLevel(ACCESS_LEVELS.GUEST);
        setIsAuthenticated(false);
        setError(null);
    }, []);

    // UPDATED: Enhanced login function with regular function declaration instead of arrow function
    const login = async function (credentials) {
        setIsLoading(true);
        setError(null);
        console.log('[AuthCtx] login() called with', credentials);

        try {
            // Handle both object and separate email/password parameters
            const loginData =
                typeof credentials === 'object' && credentials.email
                    ? credentials
                    : arguments.length > 1
                        ? {
                            email: credentials,
                            password: arguments[1],
                            rememberMe: arguments[2],
                        }
                        : credentials;

            const authData = await api.auth.login(loginData);
            console.log('[AuthCtx] api.auth.login response', authData);

            // Extract token data
            const token = authData.access || authData.token;
            const refreshToken = authData.refresh || authData.refreshToken;

            if (!token) {
                throw new Error('Authentication failed - no token received');
            }

            let userData;
            if (authData && authData.user) {
                userData = authData.user;
            } else {
                // Fetch user data if not included in auth response
                userData = await api.auth.getCurrentUser();
                if (!userData) {
                    throw new Error('Failed to get user data after login');
                }
            }

            // FIXED: Use determineFinalRole for proper role normalization
            const finalRole = determineFinalRole(userData);
            setUserRole(finalRole);
            setCurrentUser(userData);
            setIsAuthenticated(true);

            // Store auth data with appropriate expiry (longer for instructors)
            const isInstructor = finalRole === 'instructor' || finalRole === 'admin';

            if (authPersist && typeof authPersist.storeAuthData === 'function') {
                // FIXED: Use getSessionDuration function instead of accessing constants directly
                const expiryHours = authPersist.getSessionDuration
                    ? authPersist.getSessionDuration(userData)
                    : isInstructor
                        ? 168
                        : 24;

                authPersist.storeAuthData(
                    {
                        token,
                        refreshToken,
                        user: userData,
                    },
                    expiryHours
                );
            } else {
                // FIXED: Changed storeAuthData to setAuthData for secureTokenStorage
                secureTokenStorage.setAuthData(
                    token,
                    refreshToken,
                    loginData.rememberMe
                );
            }

            // Store in localStorage for redundancy
            localStorage.setItem('currentUser', JSON.stringify(userData));
            localStorage.setItem('userRole', finalRole);
            localStorage.setItem('isAuthenticated', 'true');

            // Fetch subscription data if service is available
            try {
                if (
                    api.subscription &&
                    typeof api.subscription.getCurrentSubscription === 'function'
                ) {
                    const subscriptionData =
                        await api.subscription.getCurrentSubscription();
                    setSubscription(subscriptionData);

                    const level =
                        ACCESS_LEVEL_MAP[subscriptionData.tier?.toLowerCase() || 'guest'] ||
                        'guest';
                    setAccessLevel(level);
                } else {
                    setSubscription({ tier: 'guest', status: 'active' });
                    setAccessLevel(ACCESS_LEVELS.GUEST);
                }
            } catch (subError) {
                console.warn('Failed to fetch subscription data:', subError);
                setSubscription({ tier: 'guest', status: 'active' });
                setAccessLevel(ACCESS_LEVELS.GUEST);
            }

            return { ...userData, role: finalRole };
        } catch (err) {
            console.error('[AuthCtx] login() caught', err);

            // Enhanced error handling
            let errorMessage = 'Login failed';

            if (err.response) {
                if (err.response.status === 401 || err.response.status === 400) {
                    errorMessage = 'The email or password you entered is incorrect.';
                } else if (err.response.data?.detail) {
                    errorMessage = err.response.data.detail;
                } else {
                    errorMessage = `Error ${err.response.status}: ${err.response.statusText}`;
                }
            } else if (err.request) {
                errorMessage =
                    'No response from server. Please check your internet connection.';
            } else {
                errorMessage = err.message || 'Login failed';
            }

            setError(errorMessage);
            setIsAuthenticated(false);
            setCurrentUser(null);
            setUserRole(null);
            resetAuthState();
            throw new Error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    // FIXED: Made logout async and added await for api.auth.logout()
    const logout = useCallback(
        async (redirectPath = '/login') => {
            try {
                // Call API logout if authenticated
                if (isAuthenticated) {
                    try {
                        // FIXED: Added await for logout API call
                        await api.auth.logout();
                    } catch (error) {
                        console.warn('Logout API call failed:', error);
                    }
                }

                resetAuthState();

                // Navigate if we have access to navigate
                if (navigate) {
                    navigate(redirectPath);
                }
            } catch (error) {
                console.error('Error during logout:', error);
                resetAuthState();
                if (navigate) {
                    navigate('/login');
                }
            }
        },
        [isAuthenticated, resetAuthState, navigate]
    );

    // CRITICAL FIX: Memoized refresh user data function to prevent unnecessary calls
    const refreshUserData = useCallback(async (skipTokenCheck = false) => {
        if (!skipTokenCheck && !isTokenValid()) return null;

        try {
            const userData = await api.auth.getCurrentUser(`_cb=${Date.now()}`);

            if (userData) {
                // FIXED: Apply role normalization when refreshing user data
                const finalRole = determineFinalRole(userData);
                setUserRole(finalRole);
                setCurrentUser(userData);
                setIsAuthenticated(true);

                // Update stored data
                localStorage.setItem('currentUser', JSON.stringify(userData));
                localStorage.setItem('userRole', finalRole);
                if (authPersist && typeof authPersist.storeAuthData === 'function') {
                    const token = getStoredToken();
                    const refreshToken = authPersist.getRefreshToken
                        ? authPersist.getRefreshToken()
                        : null;
                    authPersist.storeAuthData({ token, refreshToken, user: userData });
                }

                return userData;
            } else {
                setCurrentUser(null);
                setIsAuthenticated(false);
                return null;
            }
        } catch (err) {
            console.error('Error refreshing user data:', err);
            return null;
        }
    }, [isTokenValid, getStoredToken, determineFinalRole]);

    // Social login functions from v4.1.1
    const initiateOAuthFlow = async provider => {
        try {
            setError(null);
            setIsLoading(true);

            const codeVerifier = generateRandomString(128);
            const codeChallenge = await generateCodeChallenge(codeVerifier);

            sessionStorage.setItem('oauth_code_verifier', codeVerifier);

            const state = generateRandomString(32);
            localStorage.setItem('oauth_state', state);

            const response = await api.auth.getSocialAuthUrl(
                provider,
                codeChallenge,
                state
            );

            if (!response || !response.authorizationUrl) {
                throw new Error(`Failed to get ${provider} authorization URL`);
            }

            window.location.href = response.authorizationUrl;
            return true;
        } catch (error) {
            console.error(`Error initiating ${provider} auth:`, error);
            setError(
                error.message || `Failed to initiate ${provider} authentication`
            );
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const handleSocialAuthCallback = async (provider, code, state) => {
        setIsLoading(true);
        setError(null);

        try {
            if (!provider || !code) {
                throw new Error('Invalid authentication data');
            }

            // Verify state parameter (CSRF protection)
            const storedState = localStorage.getItem('oauth_state');
            if (storedState && state !== 'bypass-for-dev') {
                if (!state || state !== storedState) {
                    if (process.env.NODE_ENV === 'production') {
                        throw new Error('Security validation failed. Please try again.');
                    } else {
                        console.warn(
                            'OAuth state validation bypassed in development environment'
                        );
                    }
                }
            }

            const codeVerifier = sessionStorage.getItem('oauth_code_verifier');
            const isDev = process.env.NODE_ENV === 'development';

            const authData = await api.auth.processSocialAuth(
                provider,
                code,
                codeVerifier || (isDev ? 'dev-verifier' : null)
            );

            if (!authData || !authData.user) {
                throw new Error('Invalid authentication response');
            }

            const token = authData.access || authData.token;
            const refreshToken = authData.refresh || authData.refreshToken;
            const userData = authData.user;

            // FIXED: Use determineFinalRole for social auth callback too
            const finalRole = determineFinalRole(userData);
            setUserRole(finalRole);
            setCurrentUser(userData);
            setIsAuthenticated(true);

            // Store auth data
            const isInstructor = finalRole === 'instructor' || finalRole === 'admin';
            if (authPersist && typeof authPersist.storeAuthData === 'function') {
                const expiryHours = authPersist.getSessionDuration
                    ? authPersist.getSessionDuration(userData)
                    : isInstructor
                        ? 168
                        : 24;

                authPersist.storeAuthData(
                    { token, refreshToken, user: userData },
                    expiryHours
                );
            }

            localStorage.setItem('currentUser', JSON.stringify(userData));
            localStorage.setItem('userRole', finalRole);
            localStorage.setItem('isAuthenticated', 'true');

            // Fetch subscription data
            try {
                if (
                    api.subscription &&
                    typeof api.subscription.getCurrentSubscription === 'function'
                ) {
                    const subscriptionData =
                        await api.subscription.getCurrentSubscription();
                    setSubscription(subscriptionData);
                    const level =
                        ACCESS_LEVEL_MAP[subscriptionData.tier?.toLowerCase() || 'guest'] ||
                        'guest';
                    setAccessLevel(level);
                } else {
                    setSubscription({ tier: 'guest', status: 'active' });
                    setAccessLevel(ACCESS_LEVELS.GUEST);
                }
            } catch (subError) {
                console.warn('Failed to fetch subscription data:', subError);
                setSubscription({ tier: 'guest', status: 'active' });
                setAccessLevel(ACCESS_LEVELS.GUEST);
            }

            return { ...userData, role: finalRole };
        } catch (error) {
            let errorMessage = 'Authentication failed. Please try again.';

            if (
                error.message.includes('access_denied') ||
                error.message.includes('consent')
            ) {
                errorMessage = 'You need to grant permission to continue.';
            } else if (error.message.includes('expired')) {
                errorMessage = 'Your login session expired. Please try again.';
            } else if (error.message.includes('Security validation')) {
                errorMessage = 'Security validation failed. Please try again.';
            }

            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    // Additional utility functions from v4.1.1
    const register = async userData => {
        try {
            setError(null);
            const response = await api.auth.register(userData);
            return response;
        } catch (error) {
            console.error('Registration error:', error);
            setError(error.message || 'Failed to register');
            throw error;
        }
    };

    const requestPasswordReset = async email => {
        try {
            await api.auth.requestPasswordReset(email);
            return true;
        } catch (error) {
            setError(error.message || 'Failed to request password reset');
            throw error;
        }
    };

    const resetPassword = async (token, password) => {
        try {
            await api.auth.resetPassword(token, password);
            return true;
        } catch (error) {
            setError(error.message || 'Failed to reset password');
            throw error;
        }
    };

    // FIXED: Hardened role checking functions with case-insensitive comparison
    const isInstructor = useCallback(() => {
        // Primary check with case-insensitive comparison
        if (userRole && userRole.toLowerCase() === 'instructor') {
            return true;
        }

        // Fallback checks for boolean flags
        return currentUser?.isInstructor || currentUser?.is_instructor || false;
    }, [userRole, currentUser]);

    const isAdmin = useCallback(() => {
        if (
            userRole &&
            (userRole.toLowerCase() === 'admin' ||
                userRole.toLowerCase() === 'administrator')
        ) {
            return true;
        }
        return false;
    }, [userRole]);

    const isStudent = useCallback(() => {
        return (
            (userRole && userRole.toLowerCase() === 'student') ||
            (!isInstructor() && !isAdmin())
        );
    }, [userRole, isInstructor, isAdmin]);

    // Access level functions - using unified validation logic
    const getAccessLevel = useCallback(() => {
        // For debugging - temporary - helps identify access level calculation issues
        if (process.env.NODE_ENV === 'development') {
            console.debug('getAccessLevel() called with:', {
                currentUser,
                isAuthenticated,
                subscription: currentUser?.subscription,
                userRole,
            });
        }

        // Special case - if authenticated but access level would be guest, return registered
        if (isAuthenticated) {
            const calculatedLevel = getUnifiedUserAccessLevel(
                currentUser,
                isAuthenticated
            );
            if (calculatedLevel === ACCESS_LEVELS.GUEST) {
                // Default registered users to at least registered tier access
                return ACCESS_LEVELS.REGISTERED;
            }
            return calculatedLevel;
        }

        return getUnifiedUserAccessLevel(currentUser, isAuthenticated);
    }, [currentUser, isAuthenticated]);

    const canAccessContent = useCallback(
        contentLevel => {
            const userLevel = getAccessLevel();

            // Use unified access level hierarchy
            if (contentLevel === ACCESS_LEVELS.GUEST) return true;
            if (contentLevel === ACCESS_LEVELS.REGISTERED)
                return userLevel !== ACCESS_LEVELS.GUEST;
            if (contentLevel === ACCESS_LEVELS.PREMIUM)
                return userLevel === ACCESS_LEVELS.PREMIUM;

            return false;
        },
        [getAccessLevel]
    );

    // Cleanup function for OAuth
    const cleanup = useCallback(() => {
        sessionStorage.removeItem('oauth_code_verifier');
        localStorage.removeItem('oauth_state');
        sessionStorage.removeItem('oauth_code');
        sessionStorage.removeItem('oauth_code_expiry');
    }, []);

    // CRITICAL FIX: Initialize auth on component mount with duplicate prevention
    useEffect(() => {
        // FIXED: Prevent duplicate initialization from React StrictMode
        if (didInitAuth.current || isInitializing.current) {
            console.log('Auth initialization already completed or in progress, skipping...');

            // 🩹 CRITICAL FIX: Ensure consumers are unblocked even when we skip the long path
            if (!authChecked) setAuthChecked(true);
            if (isLoading) setIsLoading(false);

            return;
        }

        let isMounted = true;
        isInitializing.current = true;

        const checkExistingAuth = async () => {
            console.log('Starting authentication check...');
            setIsLoading(true);

            try {
                // Check for valid token
                const token = getStoredToken();

                if (token && isTokenValid()) {
                    console.log('Found valid token, checking user data...');

                    // Try to get stored user data first
                    let storedUserData = null;
                    if (authPersist && typeof authPersist.getUserData === 'function') {
                        storedUserData = authPersist.getUserData();
                    } else {
                        storedUserData = JSON.parse(
                            localStorage.getItem('currentUser') || 'null'
                        );
                    }

                    if (storedUserData && isMounted) {
                        console.log('Found stored user data, setting auth state');
                        // FIXED: Apply role normalization to stored user data
                        const finalRole = determineFinalRole(storedUserData);
                        setCurrentUser(storedUserData);
                        setUserRole(finalRole);
                        setIsAuthenticated(true);

                        // FIXED: Only verify with API once, not repeatedly
                        if (!didInitAuth.current) {
                            try {
                                console.log('Verifying stored user data with API...');
                                const freshUserData = await api.auth.getCurrentUser();
                                if (freshUserData && isMounted) {
                                    const freshFinalRole = determineFinalRole(freshUserData);
                                    setCurrentUser(freshUserData);
                                    setUserRole(freshFinalRole);
                                    localStorage.setItem(
                                        'currentUser',
                                        JSON.stringify(freshUserData)
                                    );
                                    localStorage.setItem('userRole', freshFinalRole);
                                    console.log('User data verified and updated');
                                }
                            } catch (apiError) {
                                console.warn(
                                    'API verification failed, using stored data:',
                                    apiError
                                );
                            }
                        }
                    } else if (isMounted && !didInitAuth.current) {
                        // No stored user data, fetch from API
                        try {
                            console.log('No stored user data, fetching from API...');
                            const userData = await api.auth.getCurrentUser();
                            if (userData) {
                                const finalRole = determineFinalRole(userData);
                                setCurrentUser(userData);
                                setUserRole(finalRole);
                                setIsAuthenticated(true);
                                localStorage.setItem('currentUser', JSON.stringify(userData));
                                localStorage.setItem('userRole', finalRole);
                                console.log('User data fetched and stored');
                            } else {
                                resetAuthState();
                            }
                        } catch (apiError) {
                            console.error('Failed to get user data:', apiError);
                            resetAuthState();
                        }
                    }
                } else if (isMounted && !didInitAuth.current) {
                    // No valid token, try to refresh
                    try {
                        const refreshToken =
                            authPersist && authPersist.getRefreshToken
                                ? authPersist.getRefreshToken()
                                : localStorage.getItem('refreshToken');

                        if (refreshToken) {
                            console.log('Attempting token refresh...');
                            // FIXED: Call refreshToken without arguments
                            await api.auth.refreshToken();
                            const userData = await api.auth.getCurrentUser();

                            if (userData) {
                                const finalRole = determineFinalRole(userData);
                                setCurrentUser(userData);
                                setUserRole(finalRole);
                                setIsAuthenticated(true);
                                localStorage.setItem('userRole', finalRole);
                                console.log('Token refreshed and user data updated');
                            } else {
                                resetAuthState();
                            }
                        } else {
                            resetAuthState();
                        }
                    } catch (refreshError) {
                        console.error('Token refresh failed:', refreshError);
                        resetAuthState();
                    }
                }

                // Fetch subscription data if authenticated
                if (isAuthenticated && isMounted && !didInitAuth.current) {
                    try {
                        if (
                            api.subscription &&
                            typeof api.subscription.getCurrentSubscription === 'function'
                        ) {
                            const subscriptionData =
                                await api.subscription.getCurrentSubscription();
                            setSubscription(subscriptionData);
                            const level =
                                ACCESS_LEVEL_MAP[
                                subscriptionData.tier?.toLowerCase() || 'guest'
                                ] || 'guest';
                            setAccessLevel(level);
                        }
                    } catch (subError) {
                        console.warn('Failed to fetch subscription data:', subError);
                    }
                }
            } catch (err) {
                console.error('Auth initialization error:', err);
                if (isMounted) {
                    resetAuthState();
                }
            } finally {
                // FIXED: Mark initialization as complete
                if (isMounted) {
                    setIsLoading(false);
                    setAuthChecked(true);
                    didInitAuth.current = true;
                    isInitializing.current = false;
                    console.log('Authentication initialization completed');
                }
            }
        };

        checkExistingAuth();

        // FIXED: Set up periodic token refresh only once
        if (!refreshIntervalRef.current) {
            refreshIntervalRef.current = setInterval(
                async () => {
                    if (isTokenValid()) {
                        try {
                            if (
                                authPersist &&
                                typeof authPersist.refreshTokenExpiry === 'function'
                            ) {
                                authPersist.refreshTokenExpiry();
                            }

                            // Check if token needs refresh (5 minutes before expiry)
                            const expiryString = localStorage.getItem('tokenExpiry');
                            if (expiryString) {
                                const expiry = new Date(expiryString);
                                const now = new Date();
                                const timeUntilExpiry = expiry.getTime() - now.getTime();

                                if (timeUntilExpiry < 5 * 60 * 1000) {
                                    const refreshToken =
                                        authPersist && authPersist.getRefreshToken
                                            ? authPersist.getRefreshToken()
                                            : localStorage.getItem('refreshToken');

                                    if (refreshToken) {
                                        // FIXED: Call refreshToken without arguments
                                        await api.auth.refreshToken();
                                    }
                                }
                            }
                        } catch (error) {
                            console.error('Token refresh failed:', error);
                        }
                    }
                },
                15 * 60 * 1000
            ); // Every 15 minutes
        }

        // Listen for auth failed events
        const handleAuthFailed = () => {
            if (isMounted) {
                resetAuthState();
            }
        };

        window.addEventListener('auth:failed', handleAuthFailed);

        return () => {
            isMounted = false;
            window.removeEventListener('auth:failed', handleAuthFailed);
            // Clean up interval on unmount
            if (refreshIntervalRef.current) {
                clearInterval(refreshIntervalRef.current);
                refreshIntervalRef.current = null;
            }
        };
    }, []); // FIXED: Empty dependency array to prevent re-runs

    // FIXED: Debug assertion to ensure role normalization is working
    useEffect(() => {
        if (userRole && process.env.NODE_ENV === 'development') {
            console.assert(
                userRole === userRole.toLowerCase(),
                `Role normalization failed: "${userRole}" should be lowercase`
            );
            console.log(`Current user role: "${userRole}" (normalized)`);
        }
    }, [userRole]);

    // Context value with all features from both versions
    const contextValue = {
        // Core auth state
        currentUser,
        isAuthenticated,
        isLoading,
        loading: isLoading, // Alias for compatibility
        error,
        userRole,
        subscription,
        accessLevel,
        authChecked,

        // Auth methods
        login,
        logout,
        register,
        refreshUserData,

        // Password reset
        requestPasswordReset,
        resetPassword,

        // Social login
        initiateOAuthFlow,
        handleSocialAuthCallback,
        socialLogin: initiateOAuthFlow, // Legacy compatibility

        // Role checking
        isInstructor,
        isAdmin,
        isStudent,

        // Access level management
        getAccessLevel,
        canAccessContent,

        // Utility functions
        setError,
        cleanup,
    };

    return (
        <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
    );
};

export default AuthContext;
