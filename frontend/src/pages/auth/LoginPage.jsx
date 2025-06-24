/**
 * File: frontend/src/pages/auth/LoginPage.jsx
 * Purpose: Production-ready login page with comprehensive auth features
 *
 * Features:
 * - Auto-redirect for already logged-in users
 * - Password visibility toggle
 * - Clear error messages for wrong credentials
 * - Multi-attempt tracking with forgot password suggestions
 * - Social login buttons integration with backend
 * - Fixed Enter key submission issue
 *
 * Updated: 2025-06-08 - Fixed Enter key submission by handling form submission explicitly
 */

import { useFormik } from 'formik';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router-dom';
import * as Yup from 'yup';
import Button from '../../components/common/Button';
import FormInput from '../../components/common/FormInput';
import Spinner from '../../components/common/Spinner';
import Footer from '../../components/layouts/Footer';
import Header from '../../components/layouts/Header';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api'; // Import the API service

// Centralized strings for i18n
const STRINGS = {
  TITLE: 'Sign in to your account',
  CREATE_ACCOUNT: 'Or',
  CREATE_ACCOUNT_LINK: 'create a new account',
  EMAIL_LABEL: 'Email Address',
  PASSWORD_LABEL: 'Password',
  REMEMBER_ME: 'Remember me',
  FORGOT_PASSWORD: 'Forgot your password?',
  SIGN_IN: 'Sign in',
  SIGNING_IN: 'Signing in...',
  CONTINUE_WITH: 'Or sign in with email',
  ERROR_TITLE: 'Unable to sign in',
  WRONG_PASSWORD: 'The email or password you entered is incorrect.',
  GOOGLE_LOGIN: 'Continue with Google',
  GITHUB_LOGIN: 'Continue with GitHub',
  FORGOT_PASSWORD_PROMPT:
    'Having trouble signing in? You can reset your password.',
  SHOW_PASSWORD: 'Show password',
  HIDE_PASSWORD: 'Hide password',
  SOCIAL_LOGIN_ERROR:
    'Social login failed. Please try again or use email login.',
};

const LoginPage = () => {
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [loginError, setLoginError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [showForgotPrompt, setShowForgotPrompt] = useState(false);
  const isMounted = useRef(true);

  // Get the return URL from location state or default to dashboard
  const from = location.state?.from?.pathname || '/dashboard';

  // Check for error param in URL (e.g., from social auth callback)
  useEffect(() => {
    const errorParam = searchParams.get('error');
    if (errorParam) {
      setLoginError(decodeURIComponent(errorParam));
    }

    // Also check for error from AuthContext
    if (auth.error) {
      setLoginError(auth.error);
    }
  }, [searchParams, auth.error]);

  // Auto-redirect if already logged in
  useEffect(() => {
    if (auth.isAuthenticated && auth.currentUser) {
      const dashboardRoute = getDashboardRoute(
        auth.currentUser.role || 'student'
      );
      navigate(dashboardRoute, { replace: true });
    }
  }, [auth.isAuthenticated, auth.currentUser]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Track login attempts and show forgot password prompt
  useEffect(() => {
    if (loginAttempts >= 2) {
      setShowForgotPrompt(true);
    }
  }, [loginAttempts]);

  // Function to determine appropriate dashboard based on user role
  const getDashboardRoute = useCallback(userRole => {
    switch (userRole) {
      case 'instructor':
        return '/instructor/dashboard';
      case 'admin':
        return '/admin/dashboard';
      case 'student':
        return '/student/dashboard';
      default:
        return '/dashboard';
    }
  }, []);

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  // Handle social login - Updated implementation with direct client ID for testing
  const handleSocialLogin = async provider => {
    try {
      // Clear previous errors
      setLoginError(null);

      // Show loading state
      formik.setSubmitting(true);

      console.log(`Initiating ${provider} login...`);

      // For Google login, use direct URL with client ID for testing
      if (provider === 'google') {
        const clientId =
          '99067790447-go0pcefo3nt1b9d0udei65u0or6nb0a0.apps.googleusercontent.com'; // Replace with your real client ID
        const redirectUri = encodeURIComponent(
          `${window.location.origin}/auth/social/google/callback`
        );
        const scope = encodeURIComponent('email profile');
        const state = encodeURIComponent(
          Math.random().toString(36).substring(2)
        );

        // Store state in localStorage to prevent CSRF attacks
        localStorage.setItem('oauth_state', state);

        const authUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;

        console.log(`Redirecting to Google login page (direct URL)...`);
        window.location.href = authUrl;
        return;
      }

      // For other providers, use the API method
      const authUrlResponse = await api.auth.getSocialAuthUrl(provider);

      if (authUrlResponse && authUrlResponse.authorization_url) {
        console.log(`Redirecting to ${provider} login page...`);

        // Redirect to OAuth provider
        window.location.href = authUrlResponse.authorization_url;
      } else {
        throw new Error(`Could not get authorization URL for ${provider}`);
      }
    } catch (error) {
      console.error(`${provider} login error:`, error);
      setLoginError(
        error.message ||
          `${provider} login failed. Please try again or use email login.`
      );
      formik.setSubmitting(false);
    }
  };

  // Validation schema
  const loginSchema = Yup.object({
    email: Yup.string()
      .email('Please enter a valid email address')
      .required('Email is required'),
    password: Yup.string().required('Password is required'),
    rememberMe: Yup.boolean(),
  });

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
    validationSchema: loginSchema,
    validateOnChange: true, // Enable real-time validation
    validateOnBlur: true, // Keep blur validation too
    onSubmit: async (values, { setSubmitting }) => {
      console.log('[LoginPage] submitting', values); // Debug log
      setLoginError(null);

      try {
        const userData = await auth.login(
          values.email,
          values.password,
          values.rememberMe
        );

        // Only proceed if component is still mounted
        if (!isMounted.current) return;

        // Check if we have a specific path to return to
        if (from && from !== '/dashboard') {
          navigate(from, { replace: true });
          return;
        }

        // Otherwise, use role-based dashboard redirection
        const userRole = userData?.role || 'student';
        const dashboardRoute = getDashboardRoute(userRole);
        navigate(dashboardRoute, { replace: true });
      } catch (error) {
        // Only set error if component is still mounted
        if (isMounted.current) {
          // Increment login attempts on failure
          setLoginAttempts(prev => prev + 1);

          // Ensure we display a clear error message
          setLoginError(error.message || STRINGS.WRONG_PASSWORD);
        }
      } finally {
        // Only update form state if component is still mounted
        if (isMounted.current) {
          setSubmitting(false);
        }
      }
    },
  });

  // Fixed: Simplified disabled state - only disable during submission
  // This allows Enter key to work properly while typing
  const isSubmitDisabled = formik.isSubmitting;

  // Handle form submission explicitly to prevent HTML5 validation from blocking Formik
  const handleFormSubmit = e => {
    e.preventDefault(); // Stop native submission
    formik.handleSubmit(e); // Let Formik handle it
  };

  // Handle Ctrl+Enter submission from anywhere in the form
  const handleFormKeyDown = e => {
    if (e.ctrlKey && e.key === 'Enter' && !isSubmitDisabled) {
      e.preventDefault();
      formik.submitForm();
    }
  };

  // Focus the email input on mount
  useEffect(() => {
    const emailInput = document.getElementById('email');
    if (emailInput) {
      emailInput.focus();
    }
  }, []);

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {STRINGS.TITLE}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {STRINGS.CREATE_ACCOUNT}{' '}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              {STRINGS.CREATE_ACCOUNT_LINK}
            </Link>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {/* Social login buttons at the top */}
            <div className="space-y-3 mb-6">
              <button
                type="button"
                onClick={() => handleSocialLogin('google')}
                className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                aria-label={STRINGS.GOOGLE_LOGIN}
                disabled={formik.isSubmitting}
              >
                <svg
                  className="w-5 h-5 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                </svg>
                {STRINGS.GOOGLE_LOGIN}
              </button>
              <button
                type="button"
                onClick={() => handleSocialLogin('github')}
                className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                aria-label={STRINGS.GITHUB_LOGIN}
                disabled={formik.isSubmitting}
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.87 8.17 6.84 9.5.5.09.68-.22.68-.48v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.9-.61.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.9 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.28.1-2.66 0 0 .84-.27 2.75 1.02A9.58 9.58 0 0110 2.8c.85 0 1.72.11 2.5.34 1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.41.1 2.66.64.7 1.03 1.59 1.03 2.68 0 3.82-2.34 4.67-4.57 4.92.36.31.68.92.68 1.85V19c0 .27.18.58.69.48A10.01 10.01 0 0020 10C20 4.477 15.523 0 10 0z"
                    clipRule="evenodd"
                  />
                </svg>
                {STRINGS.GITHUB_LOGIN}
              </button>
            </div>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  {STRINGS.CONTINUE_WITH}
                </span>
              </div>
            </div>

            {loginError && (
              <div
                className="mb-4 bg-red-50 border-l-4 border-red-500 p-4"
                role="alert"
                aria-labelledby="error-title"
              >
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-red-500"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3
                      id="error-title"
                      className="text-sm font-medium text-red-800"
                    >
                      {STRINGS.ERROR_TITLE}
                    </h3>
                    <p className="mt-1 text-sm text-red-700">{loginError}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Show forgot password suggestion after multiple failed attempts */}
            {showForgotPrompt && !loginError && (
              <div className="mb-4 bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-blue-500"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700">
                      {STRINGS.FORGOT_PASSWORD_PROMPT}{' '}
                      <Link
                        to="/forgot-password"
                        className="font-medium underline"
                      >
                        Reset your password
                      </Link>
                    </p>
                  </div>
                </div>
              </div>
            )}

            <form
              className="space-y-6"
              onSubmit={handleFormSubmit}
              onKeyDown={handleFormKeyDown}
              aria-busy={formik.isSubmitting}
              noValidate
            >
              {/* Hidden submit input for belt-and-braces Enter key support */}
              <input type="submit" className="hidden" />

              <FormInput
                id="email"
                label={STRINGS.EMAIL_LABEL}
                name="email"
                type="email"
                autoComplete="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.email && formik.errors.email}
                required
                aria-required="true"
              />

              <div className="relative">
                <FormInput
                  id="password"
                  label={STRINGS.PASSWORD_LABEL}
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={formik.values.password}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.password && formik.errors.password}
                  required
                  aria-required="true"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-2 top-9 text-gray-500 hover:text-gray-700 focus:outline-none"
                  aria-label={
                    showPassword ? STRINGS.HIDE_PASSWORD : STRINGS.SHOW_PASSWORD
                  }
                >
                  {showPassword ? (
                    // Eye-slash icon
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z"
                        clipRule="evenodd"
                      />
                      <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                    </svg>
                  ) : (
                    // Eye icon
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path
                        fillRule="evenodd"
                        d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="rememberMe"
                    name="rememberMe"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    checked={formik.values.rememberMe}
                    onChange={formik.handleChange}
                    aria-label={STRINGS.REMEMBER_ME}
                  />
                  <label
                    htmlFor="rememberMe"
                    className="ml-2 block text-sm text-gray-900"
                  >
                    {STRINGS.REMEMBER_ME}
                  </label>
                </div>

                <div className="text-sm">
                  <Link
                    to="/forgot-password"
                    className="font-medium text-primary-600 hover:text-primary-500"
                  >
                    {STRINGS.FORGOT_PASSWORD}
                  </Link>
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  fullWidth
                  disabled={isSubmitDisabled}
                  aria-busy={formik.isSubmitting}
                >
                  {formik.isSubmitting ? (
                    <span className="flex items-center justify-center">
                      <Spinner className="mr-2" />
                      {STRINGS.SIGNING_IN}
                    </span>
                  ) : (
                    STRINGS.SIGN_IN
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default LoginPage;
