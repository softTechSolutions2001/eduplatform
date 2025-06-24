/**
 * File: src/pages/auth/SocialAuthCallback.jsx
 * Purpose: Handle OAuth callback from social providers
 *
 * This component:
 * 1. Captures the authorization code from the OAuth provider
 * 2. Uses AuthContext's handleSocialAuthCallback method
 * 3. Redirects to appropriate dashboard on success
 * 4. Implements security features: CSRF protection, code expiration, duplicate processing prevention
 *
 * Last modified: 2025-05-22 16:22:29 UTC
 * Modified by: mohithasanthanam
 */

import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Spinner from '../../components/common/Spinner';

const SocialAuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { provider } = useParams();
  const auth = useAuth();
  const [status, setStatus] = useState('Processing your login...');
  const [error, setError] = useState(null);
  // Use useRef instead of local variable to prevent duplicate processing
  // during React Strict Mode's double-invocation of effects
  const processedRef = useRef(false);

  useEffect(() => {
    const processCallback = async () => {
      // If already processed, skip to prevent duplicate API calls
      if (processedRef.current) {
        console.log(
          'OAuth callback already processed, skipping duplicate call'
        );
        return;
      }

      try {
        // Mark as processing to prevent duplicate API calls
        processedRef.current = true;
        console.log('SocialAuthCallback: Starting OAuth callback processing');

        // Parse query parameters from URL
        const query = new URLSearchParams(location.search);
        const code = query.get('code');
        const state = query.get('state'); // For CSRF protection
        const errorParam = query.get('error');
        const errorDescription = query.get('error_description');

        // Log the received OAuth parameters (for debugging)
        console.log(
          'Received code:',
          code ? `${code.substring(0, 8)}...` : 'none'
        );
        console.log('Received state:', state);
        console.log('Stored state:', localStorage.getItem('oauth_state'));

        // Handle error in the callback
        if (errorParam) {
          const errorMsg = errorDescription || errorParam;
          setError(`Authentication error: ${errorMsg}`);
          setTimeout(() => {
            navigate(`/login?error=${encodeURIComponent(errorMsg)}`, {
              replace: true,
            });
          }, 3000);
          return;
        }

        // Ensure we have an authorization code
        if (!code) {
          setError('No authorization code received');
          setTimeout(() => {
            navigate('/login?error=no_code', { replace: true });
          }, 3000);
          return;
        }

        // Check for already processed code to avoid duplicate processing
        const storedCode = sessionStorage.getItem('oauth_code');
        const expiry = sessionStorage.getItem('oauth_code_expiry');

        if (
          storedCode === code &&
          expiry &&
          Date.now() < parseInt(expiry, 10)
        ) {
          console.log(
            'OAuth code already processed, skipping duplicated processing'
          );
          // Already processed this code and it's not expired
          if (auth.isAuthenticated && auth.currentUser) {
            // Already authenticated, redirect to dashboard
            const dashboardPath = getRedirectPath(auth.currentUser.role);
            navigate(dashboardPath, { replace: true });
            // Clean up after navigation to prevent stale OAuth data
            auth.cleanup();
          } else {
            // Not authenticated, retry login by clearing stored code
            sessionStorage.removeItem('oauth_code');
            sessionStorage.removeItem('oauth_code_expiry');
          }
          return;
        }

        // Store code with expiration to prevent reuse
        sessionStorage.setItem('oauth_code', code);
        sessionStorage.setItem(
          'oauth_code_expiry',
          (Date.now() + 5 * 60 * 1000).toString()
        ); // 5 minutes

        setStatus(`Completing ${provider} authentication...`);
        console.log(
          `Processing ${provider} callback with code: ${code.substring(0, 10)}...`
        );

        // If state is missing but we need it for security validation
        if (!state && localStorage.getItem('oauth_state')) {
          console.warn('OAuth state parameter is missing from callback URL');

          // Use a bypass state for development environment
          const bypassState =
            process.env.NODE_ENV === 'development' ? 'bypass-for-dev' : state;

          // Process social auth with state parameter for CSRF protection
          const userData = await auth.handleSocialAuthCallback(
            provider,
            code,
            bypassState
          );

          setStatus('Authentication successful! Redirecting...');

          // Determine where to redirect based on user role
          const dashboardPath = getRedirectPath(userData.role);

          // Short delay before redirect for better UX
          setTimeout(() => {
            navigate(dashboardPath, { replace: true });
            // Clean up after navigation to prevent stale OAuth data
            auth.cleanup();
          }, 1000);
        } else {
          // Normal flow with state parameter
          const userData = await auth.handleSocialAuthCallback(
            provider,
            code,
            state
          );

          setStatus('Authentication successful! Redirecting...');

          // Determine where to redirect based on user role
          const dashboardPath = getRedirectPath(userData.role);

          // Short delay before redirect for better UX
          setTimeout(() => {
            navigate(dashboardPath, { replace: true });
            // Clean up after navigation to prevent stale OAuth data
            auth.cleanup();
          }, 1000);
        }
      } catch (error) {
        console.error('Social auth callback error:', error);

        // Clean up stored code on error
        sessionStorage.removeItem('oauth_code');
        sessionStorage.removeItem('oauth_code_expiry');

        setError(error.message || 'Authentication failed');

        // Redirect to login with error after a delay
        setTimeout(() => {
          navigate(
            `/login?error=${encodeURIComponent(error.message || 'Authentication failed')}`,
            { replace: true }
          );
          // Clean up even on error to prevent stale OAuth data
          auth.cleanup();
        }, 3000);
      }
    };

    processCallback();

    // No cleanup function needed now that we use useRef for process tracking
  }, [location, provider, navigate, auth]); // Keep dependencies to ensure effect runs when route params change

  // Helper function to get dashboard path
  function getRedirectPath(role) {
    switch (role) {
      case 'instructor':
        return '/instructor/dashboard';
      case 'admin':
        return '/admin/dashboard';
      default:
        return '/student/dashboard';
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      {error ? (
        <div className="text-center p-8 max-w-md">
          <div className="mb-4 text-red-600 text-lg font-medium">
            Authentication Failed
          </div>
          <div className="mb-6 text-gray-600">{error}</div>
          <div className="text-sm text-gray-500">
            Redirecting to login page...
          </div>
        </div>
      ) : (
        <div className="text-center p-8">
          <Spinner className="mx-auto mb-4 h-10 w-10 text-primary-600" />
          <div className="mt-4 text-xl font-semibold text-gray-700">
            {status}
          </div>
          <div className="mt-2 text-gray-500">
            Please wait while we complete your sign in...
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialAuthCallback;
