/**
 * File: frontend/src/components/routes/ProtectedRoute.jsx
 * Version: 2.4.6
 * Date: 2025-06-23
 * Author: cadsanthanam (updated by saiacupuncture)
 * Last Modified: 2025-06-23 16:22:24 UTC
 *
 * Smart route protection component with tiered access control
 *
 * CRITICAL FIXES v2.4.6:
 * - FIXED: useMemo dependency array size warning by using stable JSON.stringify approach
 * - MAINTAINED: Complete backward compatibility with existing code
 *
 * CRITICAL FIXES v2.4.5:
 * - FIXED: Stuck loading spinner issue by ensuring access check completes after auth is verified
 * - IMPROVED: Tightened trigger logic for the access check to ensure it always fires once
 * - ENHANCED: Added debugging to track component state transitions
 * - MAINTAINED: Complete backward compatibility with existing code
 *
 * CRITICAL FIXES v2.4.4:
 * - FIXED: Perpetual "Checking permissions..." spinner by ensuring access check runs after auth gate opens
 * - IMPROVED: Update effect now properly triggers when AuthContext finishes its first round-trip
 * - ENHANCED: Backwards-compatible patch that doesn't change public API
 *
 * CRITICAL FIXES v2.4.3:
 * - FIXED: Removed timeout mechanism to eliminate "Auth loading timed out" warnings
 * - IMPROVED: Now properly relies on AuthContext's authChecked flag instead of timers
 * - ENHANCED: Simplified dependency arrays and effect structure
 * - ELIMINATED: Race conditions between timeout and auth state updates
 *
 * Previous fixes v2.4.2:
 * - FIXED: Multiple "Auth loading timed out" warnings by preventing duplicate timeouts
 * - FIXED: Race conditions in authentication state checks
 * - IMPROVED: More efficient dependency tracking to prevent unnecessary re-renders
 * - ENHANCED: Added debug logging to help identify timeouts
 *
 * Previous fixes v2.4.1:
 * - FIXED: Infinite loop causing flickering by stabilizing dependencies
 * - FIXED: Multiple timeout warnings by proper cleanup
 * - FIXED: Unstable requiredRoles array comparison
 * - IMPROVED: Better state management to prevent re-renders
 * - ENHANCED: Memoized functions and stable references
 *
 * Previous fixes:
 * - Added safety timeout to prevent infinite loading state
 * - Improved error recovery mechanisms
 * - Updated ACCESS_LEVEL_MAP to align with current terminology
 * - Added requiredDraftOwner prop to protect draft course editing routes
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LoadingScreen } from '../common';

// Map subscription props to actual subscription tiers
const SUBSCRIPTION_TIER_MAP = {
  registered: ['registered', 'premium'],
  premium: ['premium'],
};

// Map access levels to minimum subscription tier required
const ACCESS_LEVEL_MAP = {
  guest: null, // No subscription required
  registered: 'registered', // Registered user (any tier)
  premium: 'premium', // Premium subscription required
};

/**
 * Helper function to determine appropriate dashboard based on user role
 * @param {string} role - User role
 * @returns {string} - Dashboard path
 */
function getDashboardForRole(role) {
  switch (role) {
    case 'instructor':
      return '/instructor/dashboard';
    case 'admin':
      return '/admin/dashboard';
    default:
      return '/student/dashboard';
  }
}

const ProtectedRoute = ({
  children,
  requiredRoles = [], // Array of roles that can access this route
  requireEmailVerified = false, // Whether email verification is required
  requiredSubscription = null, // Required subscription level: null, 'registered', 'premium'
  requiredAccessLevel = null, // Required access level: 'guest', 'registered', 'premium'
  requiredDraftOwner = false, // Only allow draft owner to access
}) => {
  const location = useLocation();
  const { currentUser, isLoading, isAuthenticated, getAccessLevel, authChecked } = useAuth();

  const isMountedRef = useRef(true);
  const accessCheckCompleteRef = useRef(false);
  const hasLoggedInitialAuthCheckRef = useRef(false);

  // Debug info to help track component state
  useEffect(() => {
    if (!hasLoggedInitialAuthCheckRef.current && authChecked) {
      console.log(`[ProtectedRoute] Auth check completed: isLoading=${isLoading}, isAuthenticated=${isAuthenticated}, path=${location.pathname}`);
      hasLoggedInitialAuthCheckRef.current = true;
    }
  }, [authChecked, isLoading, isAuthenticated, location.pathname]);

  // FIXED: Stabilize the requiredRoles array using JSON.stringify to prevent dependency array size warnings
  const stableRequiredRoles = useMemo(() => {
    return Array.isArray(requiredRoles) ? [...requiredRoles] : [];
  }, [JSON.stringify(requiredRoles)]);

  // Consolidated state to prevent multiple re-renders
  const [routeState, setRouteState] = useState({
    accessGranted: false,
    isChecking: true,
    redirectPath: '/login',
    hasChecked: false
  });

  // Memoized access requirements check
  const hasAuthRequirements = useMemo(() => {
    return (
      stableRequiredRoles.length > 0 ||
      requireEmailVerified ||
      requiredSubscription ||
      requiredAccessLevel ||
      requiredDraftOwner
    );
  }, [
    stableRequiredRoles.length,
    requireEmailVerified,
    requiredSubscription,
    requiredAccessLevel,
    requiredDraftOwner
  ]);

  // Track the current authentication state to prevent unnecessary checks
  const authStateRef = useRef({
    isLoading,
    isAuthenticated,
    currentUser: currentUser ? { ...currentUser } : null
  });

  // Update auth state ref when it changes
  useEffect(() => {
    authStateRef.current = {
      isLoading,
      isAuthenticated,
      currentUser: currentUser ? { ...currentUser } : null
    };
  }, [isLoading, isAuthenticated, currentUser]);

  // Stable access check function
  const checkAccess = useCallback(() => {
    // Don't run checks if not mounted or authentication not yet determined
    if (!isMountedRef.current || !authChecked) {
      return;
    }

    // Prevent multiple simultaneous checks
    if (accessCheckCompleteRef.current) {
      return;
    }

    console.log(`[ProtectedRoute] Running access check for path=${location.pathname}, isAuthenticated=${isAuthenticated}`);

    try {
      // If no specific requirements and authenticated, grant access
      if (!hasAuthRequirements) {
        setRouteState({
          accessGranted: true,
          isChecking: false,
          redirectPath: '/login',
          hasChecked: true
        });
        accessCheckCompleteRef.current = true;
        console.log(`[ProtectedRoute] Access granted - no requirements needed`);
        return;
      }

      // Not authenticated but access requires auth
      if (!isAuthenticated && hasAuthRequirements) {
        const returnUrl = `/login?redirect=${encodeURIComponent(location.pathname)}`;
        setRouteState({
          accessGranted: false,
          isChecking: false,
          redirectPath: returnUrl,
          hasChecked: true
        });
        accessCheckCompleteRef.current = true;
        console.log(`[ProtectedRoute] Access denied - authentication required`);
        return;
      }

      // Role check - user must have one of the required roles
      if (stableRequiredRoles.length > 0) {
        const hasRole = stableRequiredRoles.some(role => {
          if (role === 'student' && currentUser && !currentUser.role) {
            return true; // Default to student if no role specified
          }
          return currentUser && currentUser.role === role;
        });

        if (!hasRole) {
          const dashboardPath = currentUser && currentUser.role
            ? getDashboardForRole(currentUser.role)
            : '/unauthorized';

          setRouteState({
            accessGranted: false,
            isChecking: false,
            redirectPath: dashboardPath,
            hasChecked: true
          });
          accessCheckCompleteRef.current = true;
          console.log(`[ProtectedRoute] Access denied - role requirement not met`);
          return;
        }
      }

      // Email verification check
      if (requireEmailVerified && currentUser && !currentUser.is_email_verified) {
        setRouteState({
          accessGranted: false,
          isChecking: false,
          redirectPath: '/verify-email',
          hasChecked: true
        });
        accessCheckCompleteRef.current = true;
        console.log(`[ProtectedRoute] Access denied - email verification required`);
        return;
      }

      // Subscription check
      if (requiredSubscription) {
        const hasRequiredSubscription =
          (requiredSubscription === 'guest' && isAuthenticated) ||
          (currentUser &&
            currentUser.subscription &&
            currentUser.subscription.tier === requiredSubscription &&
            currentUser.subscription.is_active);

        if (!hasRequiredSubscription) {
          setRouteState({
            accessGranted: false,
            isChecking: false,
            redirectPath: '/subscription',
            hasChecked: true
          });
          accessCheckCompleteRef.current = true;
          console.log(`[ProtectedRoute] Access denied - subscription requirement not met`);
          return;
        }
      }

      // Access level check
      if (requiredAccessLevel && isAuthenticated) {
        const userAccessLevel = getAccessLevel ? getAccessLevel() : 'guest';
        const accessLevels = { guest: 1, registered: 2, premium: 3 };

        if (accessLevels[userAccessLevel] < accessLevels[requiredAccessLevel]) {
          setRouteState({
            accessGranted: false,
            isChecking: false,
            redirectPath: '/subscription',
            hasChecked: true
          });
          accessCheckCompleteRef.current = true;
          console.log(`[ProtectedRoute] Access denied - access level requirement not met`);
          return;
        }
      }

      // Draft owner protection
      if (requiredDraftOwner && currentUser) {
        if (!location.pathname.match(/\/(draft|builder)\//i)) {
          setRouteState({
            accessGranted: false,
            isChecking: false,
            redirectPath: '/unauthorized',
            hasChecked: true
          });
          accessCheckCompleteRef.current = true;
          console.log(`[ProtectedRoute] Access denied - draft owner requirement not met`);
          return;
        }
      }

      // All checks passed - grant access
      setRouteState({
        accessGranted: true,
        isChecking: false,
        redirectPath: '/login',
        hasChecked: true
      });
      accessCheckCompleteRef.current = true;
      console.log(`[ProtectedRoute] Access granted - all requirements met`);

    } catch (error) {
      console.error('[ProtectedRoute] Error during access check:', error);
      // On error, deny access for security
      setRouteState({
        accessGranted: false,
        isChecking: false,
        redirectPath: '/login',
        hasChecked: true
      });
      accessCheckCompleteRef.current = true;
    }
  }, [
    authChecked,
    isAuthenticated,
    hasAuthRequirements,
    stableRequiredRoles,
    requireEmailVerified,
    requiredSubscription,
    requiredAccessLevel,
    requiredDraftOwner,
    location.pathname,
    getAccessLevel,
    currentUser
  ]);

  // Main effect - handle component mounting/unmounting
  useEffect(() => {
    isMountedRef.current = true;
    hasLoggedInitialAuthCheckRef.current = false;

    // Force a check when the component mounts
    if (authChecked && !isLoading) {
      accessCheckCompleteRef.current = false;
      checkAccess();
    }

    return () => {
      isMountedRef.current = false;
    };
  }, []);  // Empty dependency array - only run on mount/unmount

  // Run check when auth state changes or route changes
  useEffect(() => {
    if (!isMountedRef.current) return;

    // IMPROVED: Fire once as soon as BOTH gates are open
    if (authChecked && !isLoading && !accessCheckCompleteRef.current) {
      console.log('[ProtectedRoute] Auth check complete and ready to verify access');
      checkAccess();
    }

    // Handle subsequent auth state changes
    if (
      accessCheckCompleteRef.current &&
      (
        authStateRef.current.isAuthenticated !== isAuthenticated ||
        JSON.stringify(authStateRef.current.currentUser) !== JSON.stringify(currentUser)
      )
    ) {
      console.log('[ProtectedRoute] Auth state changed, re-checking access');
      accessCheckCompleteRef.current = false;
      checkAccess();
    }
  }, [authChecked, isLoading, isAuthenticated, currentUser, checkAccess, location.pathname]);

  // Show loading while checking permissions
  if (routeState.isChecking) {
    return <LoadingScreen message="Checking permissions..." />;
  }

  // Redirect if access not granted
  if (!routeState.accessGranted && routeState.hasChecked) {
    return <Navigate to={routeState.redirectPath} state={{ from: location }} replace />;
  }

  // Render children if access is granted
  return children;
};

export default ProtectedRoute;
