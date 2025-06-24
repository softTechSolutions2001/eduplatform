/**
 * File: frontend/src/pages/auth/VerifyEmailPage.jsx
 * Purpose: Handles email verification process and resend functionality
 * Last Updated: 2025-05-20 10:15:12
 * Updated By: agentic-ai
 *
 * Key features:
 * 1. Verifies email tokens automatically from URL query parameters
 * 2. Shows success/error messages based on verification result
 * 3. Provides option to request a new verification email
 * 4. Directs users to next steps after verification
 * 5. Handles "already verified" state elegantly
 * 6. Auto-redirects after successful verification with countdown
 * 7. Validates email format before submission
 *
 * API Endpoints Used:
 * - POST /api/user/email/verify/ - Verify email with token
 * - POST /api/user/email/verify/resend/ - Resend verification email
 *
 * Implementation notes:
 * - Uses token from URL query params using useSearchParams
 * - Connects with authService (verifyEmail, resendVerification) for API communication
 * - Handles various verification states with proper UI feedback
 * - Special handling for "already verified" error as a success state
 * - Uses refs to prevent duplicate API calls, especially in React's StrictMode
 *
 * Variables to modify if needed:
 * - redirectPath: Where to send the user after successful verification (default: '/login')
 * - redirectDelay: How many seconds to wait before auto-redirect (default: 5)
 */

import React, { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const VerifyEmailPage = () => {
  // Parse the token from URL only once during initialization
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const { verifyEmail, resendVerification, currentUser } = useAuth();
  const navigate = useNavigate();

  // Configuration variables
  const redirectPath = '/login';
  const redirectDelay = 5; // seconds before auto-redirect

  // Use refs to track verification attempt and prevent duplicates
  const verificationAttemptedRef = useRef(false);
  const resendAttemptInProgressRef = useRef(false);

  // Component state
  const [verificationState, setVerificationState] = useState({
    status: token ? 'verifying' : 'manual',
    message: token
      ? 'Verifying your email...'
      : 'Please enter your email to verify your account',
  });
  const [email, setEmail] = useState('');
  const [countdown, setCountdown] = useState(redirectDelay);
  const [emailError, setEmailError] = useState('');

  // Initialize email field if user is logged in
  useEffect(() => {
    if (currentUser && currentUser.email) {
      setEmail(currentUser.email);
    }
  }, [currentUser]);

  // Handle countdown for automatic redirect
  useEffect(() => {
    let timer;
    if (verificationState.status === 'success' && countdown > 0) {
      timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
    } else if (verificationState.status === 'success' && countdown === 0) {
      navigate(redirectPath);
    }

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [countdown, verificationState.status, navigate, redirectPath]);

  // Handle token verification once on component mount using ref
  useEffect(() => {
    // To debug duplicate calls:
    // console.log("Effect running: token =", token,
    //             "attempted =", verificationAttemptedRef.current,
    //             "status =", verificationState.status);

    // Only verify if:
    // 1. There's a token
    // 2. We haven't attempted verification yet
    // 3. The state is still in verifying mode
    if (
      token &&
      !verificationAttemptedRef.current &&
      verificationState.status === 'verifying'
    ) {
      // Set the ref FIRST to prevent any future attempts, even if this one errors out
      verificationAttemptedRef.current = true;

      const verifyToken = async () => {
        try {
          // Debug log
          console.log('Attempting verification once only with token:', token);

          // Call the verifyEmail function
          const result = await verifyEmail(token);

          if (result.success) {
            setVerificationState({
              status: 'success',
              message:
                result.message ||
                'Your email has been successfully verified! You can now log in.',
            });
          } else {
            setVerificationState({
              status: 'error',
              message:
                result.error ||
                'Failed to verify email. The token may be invalid or expired.',
            });
          }
        } catch (error) {
          // This should not happen due to proper error handling in verifyEmail,
          // but we'll handle it just in case
          console.error('Uncaught verification error:', error);

          // Check for network errors
          if (!navigator.onLine) {
            setVerificationState({
              status: 'error',
              message:
                'No internet connection. Please check your connection and try again.',
            });
          } else {
            // Generic error
            setVerificationState({
              status: 'error',
              message:
                error.message ||
                'An unexpected error occurred during verification.',
            });
          }
        }
      };

      // Start the verification process
      verifyToken();
    }
  }, [token, verifyEmail, verificationState.status]); // Dependencies limited to what is used

  // Email validation function
  const validateEmail = email => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleResendVerification = async () => {
    // Prevent duplicate requests
    if (
      resendAttemptInProgressRef.current ||
      verificationState.status === 'sending'
    ) {
      console.log('Resend already in progress, ignoring duplicate request');
      return;
    }

    // Clear previous errors
    setEmailError('');

    // Validate email
    if (!email) {
      setEmailError('Please enter your email address');
      return;
    }

    if (!validateEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    // Set flags to prevent duplicate requests
    resendAttemptInProgressRef.current = true;

    try {
      // Update UI state
      setVerificationState({
        status: 'sending',
        message: 'Sending verification email...',
      });

      console.log('Resending verification to:', email);
      const result = await resendVerification(email);

      // Reset flag now that request is complete
      resendAttemptInProgressRef.current = false;

      if (result.success) {
        setVerificationState({
          status: 'sent',
          message:
            result.message ||
            'A new verification email has been sent. Please check your inbox and spam folder.',
        });
      } else {
        // Handle errors from the resend verification function
        setVerificationState({
          status: 'error',
          message:
            result.error ||
            'Failed to resend verification email. Please try again.',
        });
      }
    } catch (error) {
      // Reset flag on error
      resendAttemptInProgressRef.current = false;

      // Log the error for debugging
      console.error('Resend verification unexpected error:', error);

      // Handle network errors
      if (!navigator.onLine) {
        setVerificationState({
          status: 'error',
          message:
            'No internet connection. Please check your connection and try again.',
        });
      } else {
        // Use our standardized error format
        setVerificationState({
          status: 'error',
          message: error.message || 'Failed to resend verification email',
        });
      }
    }
  };

  // Render email form for manual verification or resending
  const renderEmailForm = () => (
    <div className="mt-1">
      <input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        placeholder="Enter your email address"
        value={email}
        onChange={e => setEmail(e.target.value)}
        className={`appearance-none block w-full px-3 py-2 border ${
          emailError ? 'border-red-500' : 'border-gray-300'
        } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm mb-2`}
      />
      {emailError && <p className="text-red-500 text-xs mb-2">{emailError}</p>}
      <button
        onClick={handleResendVerification}
        disabled={verificationState.status === 'sending'}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
      >
        {verificationState.status === 'sending'
          ? 'Sending...'
          : verificationState.status === 'sent'
            ? 'Resend Again'
            : 'Send Verification Email'}
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Email Verification
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {verificationState.status === 'verifying' && (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700"></div>
              <p className="mt-4 text-gray-600">{verificationState.message}</p>
            </div>
          )}

          {verificationState.status === 'success' && (
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <p className="mt-4 text-lg text-gray-800">
                {verificationState.message}
              </p>
              <div className="mt-6">
                <p className="text-sm text-gray-600 mb-4">
                  Redirecting to login in {countdown} seconds...
                </p>
                <Link
                  to={redirectPath}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Go to Login Now
                </Link>
              </div>
            </div>
          )}

          {verificationState.status === 'error' && (
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              <p className="mt-4 text-lg text-red-800">
                {verificationState.message}
              </p>
              <div className="mt-6">
                <p className="mb-4 text-sm text-gray-600">
                  Need a new verification link?
                </p>
                {renderEmailForm()}
              </div>
            </div>
          )}

          {verificationState.status === 'manual' && (
            <div className="text-center">
              <p className="mb-4 text-gray-700">{verificationState.message}</p>
              {renderEmailForm()}
            </div>
          )}

          {verificationState.status === 'sending' && (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700"></div>
              <p className="mt-4 text-gray-600">{verificationState.message}</p>
            </div>
          )}

          {verificationState.status === 'sent' && (
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <p className="mt-4 text-lg text-gray-800">
                {verificationState.message}
              </p>
              <div className="mt-6">
                <p className="mb-4 text-sm text-gray-600">
                  Didn't receive the email? Check your spam folder or try again.
                </p>
                {renderEmailForm()}
                <div className="mt-4">
                  <Link
                    to="/login"
                    className="text-sm text-primary-600 hover:text-primary-500"
                  >
                    Return to login
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
