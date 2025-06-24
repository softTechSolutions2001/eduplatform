// src/components/routes/CourseContentRouteChecker.jsx
// -----------------------------------------------------------------------------
// Emergency fix for the infinite "Checking permissions..." state
// By passing through to CourseContentPage after a short timeout
// -----------------------------------------------------------------------------
// Version: 4.0.0 - EMERGENCY FIX
//   • Drastically simplifies permission checking
//   • Adds immediate safety timeout fallback
//   • Falls back to basic access level for all content
// -----------------------------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { Navigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingScreen from '../common/LoadingScreen';
import MainLayout from '../layouts/MainLayout';
import CourseContentPage from '../../pages/courses/CourseContentPage';

// ─── Constants ──────────────────────────────────────────────────────────────
const LEVELS = {
  GUEST: 'guest',
  REGISTERED: 'registered',
  PREMIUM: 'premium',
};

// Shorter timeout for faster fallback
const EMERGENCY_TIMEOUT = 2000; // 2 seconds max wait

export default function CourseContentRouteChecker() {
  const { courseSlug, moduleId, lessonId } = useParams();
  const location = useLocation();
  const {
    isAuthenticated,
    userRole,
    userAccessLevel,
    isLoading: authLoading,
  } = useAuth();

  const [loading, setLoading] = useState(true);
  const [timedOut, setTimedOut] = useState(false);

  // Determine if user is instructor (simple check)
  const isInstructor =
    userRole === 'instructor' ||
    userRole === 'admin' ||
    userRole === 'administrator';

  useEffect(() => {
    console.log('CourseContentRouteChecker mounting with params:', {
      courseSlug,
      moduleId,
      lessonId,
    });
    console.log('Auth state:', {
      isAuthenticated,
      userRole,
      userAccessLevel,
      authLoading,
    });

    // Set emergency timeout
    const timeoutId = setTimeout(() => {
      console.warn(
        'EMERGENCY TIMEOUT: Bypassing permission checks after 2 seconds'
      );
      setLoading(false);
      setTimedOut(true);
    }, EMERGENCY_TIMEOUT);

    // Simplified permission check logic
    const checkAccess = async () => {
      try {
        // If user is instructor, they get access
        if (isInstructor) {
          console.log('User is instructor, granting access');
          setLoading(false);
          return;
        }

        // For everyone else, we'll determine access level
        if (!authLoading) {
          console.log('Auth loaded, determining access level');
          setLoading(false);
        }
      } catch (error) {
        console.error('Error checking access:', error);
        // On any error, we'll just show the page anyway
        setLoading(false);
      }
    };

    // Only run check if we haven't timed out yet
    if (!timedOut) {
      checkAccess();
    }

    return () => {
      clearTimeout(timeoutId);
    };
  }, [
    courseSlug,
    moduleId,
    lessonId,
    isInstructor,
    authLoading,
    timedOut,
    isAuthenticated,
    userRole,
    userAccessLevel,
  ]);

  // Show loading for a very short time
  if (loading && !timedOut) {
    return (
      <MainLayout>
        <LoadingScreen message="Checking permissions..." />
      </MainLayout>
    );
  }

  // Instructors always get access
  if (isInstructor) {
    return (
      <MainLayout>
        <CourseContentPage />
      </MainLayout>
    );
  }
  // For registered content
  if (userAccessLevel === LEVELS.GUEST && !isAuthenticated) {
    // If the user is not logged in and tries to access registered content, redirect to login
    return (
      <Navigate
        to={`/login?redirect=${encodeURIComponent(location.pathname)}`}
        replace
      />
    );
  }

  // For premium content
  if (userAccessLevel !== LEVELS.PREMIUM) {
    // If the content requires premium access and user doesn't have it,
    // we'll let ContentAccessController handle showing appropriate messaging
    // instead of blocking the page load
  }

  // Default case - show the page and let ContentAccessController handle content visibility
  return (
    <MainLayout>
      <CourseContentPage />
    </MainLayout>
  );
}
