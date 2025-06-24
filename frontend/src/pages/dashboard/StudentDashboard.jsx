/**
 * File: frontend/src/pages/dashboard/StudentDashboard.jsx
 * Purpose: Dashboard specifically for students
 * Version: 1.2.2
 * Date: 2025-06-23 16:29:53
 * Author: saiacupuncture
 * Last Modified: 2025-06-23 16:29:53 UTC
 *
 * FIXED: Added condition to minHeight style to prevent flickering
 * FIXED: Added useRef guards to prevent duplicate API calls and eliminate flickering
 * FIXED: Fixed SVG path syntax error in error message component
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, ResumeButton } from '../../components/common';
import { useAuth } from '../../contexts/AuthContext';
import { courseService, progressService } from '../../services/api';

// Skeleton component for loading state
const CourseCardSkeleton = ({ count = 3 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
          <div className="w-full h-48 bg-gray-300"></div>
          <div className="p-4">
            <div className="h-4 bg-gray-300 rounded mb-2"></div>
            <div className="h-3 bg-gray-300 rounded mb-2 w-3/4"></div>
            <div className="h-2 bg-gray-300 rounded mb-4"></div>
            <div className="h-8 bg-gray-300 rounded"></div>
          </div>
        </div>
      ))}
    </>
  );
};

const StudentDashboard = () => {
  const { currentUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Prevent duplicate fetchDashboardData calls
  const didFetchRef = useRef(false);

  // Consolidated state to prevent multiple re-renders
  const [dashboardState, setDashboardState] = useState({
    enrolledCourses: [],
    recommendations: [],
    progressStats: null,
    loading: true,
    error: null,
    dataLoaded: false
  });

  // FIXED: Compute dynamic grid height to prevent flickering after loading
  const gridMinHeight = dashboardState.loading ? '200px' : 'auto';

  // Memoize default progress stats to prevent object recreation
  const defaultProgressStats = useMemo(() => ({
    totalCourses: 0,
    coursesInProgress: 0,
    coursesCompleted: 0,
    totalLessons: 0,
    completedLessons: 0,
    completionPercentage: 0,
    hoursSpent: 0,
    assessmentsCompleted: 0,
    certificatesEarned: 0
  }), []);

  // Handle unauthorized access with useCallback to prevent re-creation
  const handleUnauthorized = useCallback(() => {
    navigate('/login', {
      replace: true,
      state: {
        from: '/dashboard',
        message: 'Session expired. Please log in again.'
      }
    });
  }, [navigate]);

  // Stabilized data fetching function with ref guard
  const fetchDashboardData = useCallback(async () => {
    if (!isAuthenticated || didFetchRef.current) {
      return;
    }

    didFetchRef.current = true;

    try {
      // Set loading state only once at the beginning
      setDashboardState(prev => ({
        ...prev,
        loading: true,
        error: null
      }));

      // Fetch all data concurrently to reduce loading time
      const [enrollmentsResult, statsResult, recommendationsResult] = await Promise.allSettled([
        progressService.getUserEnrollments(),
        progressService.getUserProgressStats(),
        courseService.getAllCourses({ recommended: true, limit: 3 })
      ]);

      // Process enrollments
      let enrolledCourses = [];
      if (enrollmentsResult.status === 'fulfilled') {
        const enrollmentsResponse = enrollmentsResult.value;
        if (Array.isArray(enrollmentsResponse)) {
          enrolledCourses = enrollmentsResponse;
        } else if (enrollmentsResponse && Array.isArray(enrollmentsResponse.results)) {
          enrolledCourses = enrollmentsResponse.results;
        }
      } else {
        console.error('Error fetching enrollments:', enrollmentsResult.reason);
        // Check for auth errors
        if (enrollmentsResult.reason?.response?.status === 401) {
          handleUnauthorized();
          return;
        }
      }

      // Process progress stats
      let progressStats = defaultProgressStats;
      if (statsResult.status === 'fulfilled') {
        const statsResponse = statsResult.value;
        if (statsResponse && typeof statsResponse === 'object') {
          progressStats = {
            totalCourses: statsResponse.totalCourses || 0,
            coursesInProgress: statsResponse.coursesInProgress || 0,
            coursesCompleted: statsResponse.coursesCompleted || 0,
            totalLessons: statsResponse.totalLessons || 0,
            completedLessons: statsResponse.completedLessons || 0,
            completionPercentage: statsResponse.completionPercentage || 0,
            hoursSpent: statsResponse.hoursSpent || 0,
            assessmentsCompleted: statsResponse.assessmentsCompleted || 0,
            certificatesEarned: statsResponse.certificatesEarned || 0
          };
        }
      } else {
        console.error('Error fetching progress stats:', statsResult.reason);
      }

      // Process recommendations
      let recommendations = [];
      if (recommendationsResult.status === 'fulfilled') {
        const recommendationsResponse = recommendationsResult.value;
        if (Array.isArray(recommendationsResponse)) {
          recommendations = recommendationsResponse;
        } else if (recommendationsResponse && Array.isArray(recommendationsResponse.results)) {
          recommendations = recommendationsResponse.results;
        }
      } else {
        console.error('Error fetching recommendations:', recommendationsResult.reason);
      }

      // Update all state in one go to prevent multiple re-renders
      setDashboardState({
        enrolledCourses,
        recommendations,
        progressStats,
        loading: false,
        error: null,
        dataLoaded: true
      });

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setDashboardState(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load dashboard data. Please try again.',
        dataLoaded: false
      }));
      // Reset the ref so retry can work
      didFetchRef.current = false;
    }
  }, [isAuthenticated, handleUnauthorized, defaultProgressStats]);

  // Handle authentication check
  useEffect(() => {
    if (!isAuthenticated && dashboardState.dataLoaded) {
      navigate('/login', {
        replace: true,
        state: { from: '/dashboard' }
      });
    }
  }, [isAuthenticated, dashboardState.dataLoaded, navigate]);

  // Fetch data only when authenticated - with ref guard
  useEffect(() => {
    if (isAuthenticated && !didFetchRef.current) {
      fetchDashboardData();
    }
  }, [isAuthenticated, fetchDashboardData]);

  // Retry function
  const handleRetry = useCallback(() => {
    didFetchRef.current = false;
    setDashboardState(prev => ({ ...prev, dataLoaded: false, loading: true }));
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Loading state with skeleton and min-height
  if (dashboardState.loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="h-8 bg-gray-300 rounded w-1/3 mb-2 animate-pulse"></div>
          <div className="h-4 bg-gray-300 rounded w-1/4 animate-pulse"></div>
        </div>

        {/* Progress Summary Skeleton */}
        <div className="mb-8 bg-white rounded-lg shadow-md p-6">
          <div className="h-6 bg-gray-300 rounded w-1/4 mb-4 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <div className="h-3 bg-gray-300 rounded mb-2 animate-pulse"></div>
                <div className="h-8 bg-gray-300 rounded w-1/2 animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>

        {/* My Courses Skeleton */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div className="h-6 bg-gray-300 rounded w-1/6 animate-pulse"></div>
            <div className="h-4 bg-gray-300 rounded w-1/8 animate-pulse"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ minHeight: '200px' }}>
            <CourseCardSkeleton count={3} />
          </div>
        </div>

        {/* Recommendations Skeleton */}
        <div>
          <div className="h-6 bg-gray-300 rounded w-1/5 mb-4 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ minHeight: '200px' }}>
            <CourseCardSkeleton count={3} />
          </div>
        </div>
      </div>
    );
  }

  // Not authenticated state
  if (!isAuthenticated) {
    return null;
  }

  const { enrolledCourses, recommendations, progressStats, error } = dashboardState;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {currentUser?.first_name || 'Student'}!
        </h1>
        <p className="mt-2 text-gray-600">Continue your learning journey</p>
      </div>

      {/* Error message - stable rendering */}
      {error && (
        <div className="mb-8 bg-red-50 border-l-4 border-red-500 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={handleRetry}
                className="mt-2 text-sm font-medium text-red-700 hover:text-red-600"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Progress Summary - stable rendering */}
      <div className="mb-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Your Learning Progress
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500">Enrolled Courses</p>
            <p className="text-2xl font-bold">
              {progressStats?.totalCourses ?? enrolledCourses.length ?? 0}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500">Completed Courses</p>
            <p className="text-2xl font-bold">
              {progressStats?.coursesCompleted ?? 0}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500">Hours Spent</p>
            <p className="text-2xl font-bold">
              {typeof progressStats?.hoursSpent === 'number'
                ? progressStats.hoursSpent.toFixed(1)
                : '0.0'}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500">Assessments Completed</p>
            <p className="text-2xl font-bold">
              {progressStats?.assessmentsCompleted ?? 0}
            </p>
          </div>
        </div>
      </div>

      {/* Enrolled Courses - FIXED: Dynamic min-height to prevent flickering */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">My Courses</h2>
          <Link
            to="/courses"
            className="text-primary-600 hover:text-primary-700"
          >
            Browse All Courses
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ minHeight: gridMinHeight }}>
          {enrolledCourses.length > 0 ? (
            enrolledCourses.map(enrollment => (
              <div
                key={enrollment.id || `enrollment-${Math.random().toString(36).substr(2, 9)}`}
                className="bg-white rounded-lg shadow-md overflow-hidden"
              >
                <img
                  src={enrollment.course?.thumbnail || '/default-course.jpg'}
                  alt={enrollment.course?.title || 'Course'}
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/default-course.jpg';
                  }}
                />
                <div className="p-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {enrollment.course?.title || 'Untitled Course'}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {typeof enrollment.progress === 'number' ? enrollment.progress : 0}% complete
                  </p>

                  {/* Progress bar - stable rendering */}
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-primary-600 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                      style={{ width: `${typeof enrollment.progress === 'number' ? enrollment.progress : 0}%` }}
                    ></div>
                  </div>

                  {/* Course action buttons - stable rendering */}
                  <div className="mt-4 space-y-2">
                    <div className="flex space-x-2">
                      {enrollment.course?.slug && (
                        <ResumeButton
                          courseSlug={enrollment.course.slug}
                          size="small"
                          className="flex-1"
                        />
                      )}
                      <Button
                        variant="outline"
                        size="small"
                        onClick={() => navigate(`/courses/${enrollment.course?.slug || ''}`)}
                        disabled={!enrollment.course?.slug}
                        className="flex-1"
                      >
                        Course Details
                      </Button>
                    </div>

                    <Link
                      to={`/courses/${enrollment.course?.slug || ''}/content/${enrollment.current_module_id || 1}/${enrollment.current_lesson_id || 1}`}
                      className="block w-full bg-primary-600 text-center text-white py-2 rounded hover:bg-primary-700 transition-colors duration-200"
                    >
                      {typeof enrollment.progress === 'number' && enrollment.progress > 0
                        ? 'Continue Learning'
                        : 'Start Learning'}
                    </Link>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full bg-white rounded-lg shadow-md p-6 text-center">
              <p className="text-gray-600 mb-4">
                You haven't enrolled in any courses yet.
              </p>
              <Link
                to="/courses"
                className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700 transition-colors duration-200"
              >
                Browse Courses
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recommended Courses - FIXED: Dynamic min-height to prevent flickering */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Recommended For You
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ minHeight: gridMinHeight }}>
          {recommendations.length > 0 ? (
            recommendations.map(course => (
              <div
                key={course.id || `course-${Math.random().toString(36).substr(2, 9)}`}
                className="bg-white rounded-lg shadow-md overflow-hidden"
              >
                <img
                  src={course.thumbnail || '/default-course.jpg'}
                  alt={course.title || 'Course'}
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/default-course.jpg';
                  }}
                />
                <div className="p-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {course.title || 'Untitled Course'}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                    {course.short_description || course.description || 'No description available'}
                  </p>

                  <div className="mt-2 flex items-center">
                    <span className="text-sm text-gray-600">
                      By {course.instructor_name || 'Unknown Instructor'}
                    </span>
                  </div>

                  <div className="mt-4 flex justify-between items-center">
                    <div className="flex items-center">
                      <svg
                        className="w-4 h-4 text-yellow-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                      </svg>
                      <span className="ml-1 text-sm text-gray-600">
                        {typeof course.avg_rating === 'number'
                          ? course.avg_rating.toFixed(1)
                          : '0.0'} (
                        {course.reviews_count || 0})
                      </span>
                    </div>
                    <span className="text-sm font-semibold">
                      {course.price === 0 || course.is_free ? 'Free' : `$${typeof course.price === 'number' ? course.price.toFixed(2) : '0.00'}`}
                    </span>
                  </div>

                  <div className="mt-4">
                    <Link
                      to={`/courses/${course.slug || ''}`}
                      className="block w-full bg-primary-600 text-center text-white py-2 rounded hover:bg-primary-700 transition-colors duration-200"
                    >
                      View Course
                    </Link>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full bg-white rounded-lg shadow-md p-6 text-center">
              <p className="text-gray-600">
                No recommendations available at this time.
              </p>
              <Link
                to="/courses"
                className="mt-4 inline-block bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700 transition-colors duration-200"
              >
                Browse All Courses
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
