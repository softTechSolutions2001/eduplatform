/**
 * File: frontend/src/pages/dashboard/InstructorDashboard.jsx
 * Version: 2.2.0 (Merged)
 * Date: 2025-06-20 15:35:05
 * Author: mohithasanthanam, cadsanthanam
 * Last Modified: 2025-06-20 15:35:05 UTC
 * Merged By: sujibeautysalon
 *
 * Enhanced Instructor Dashboard with Comprehensive Course Management
 *
 * MERGE RESOLUTION v2.2.0:
 * - Combined advanced features from HEAD (comprehensive course creation options)
 * - Preserved enhanced authentication handling from branch
 * - Unified performance optimizations and state management
 * - Integrated multiple course creation methods (Traditional, Wizard, AI Builder, Drag-Drop)
 * - Maintained backward compatibility with existing API endpoints
 * - Added comprehensive error handling and loading states
 *
 * Key Features:
 * 1. Multiple Course Creation Methods (Traditional, Wizard, AI Builder, Drag-Drop Builder)
 * 2. Advanced Performance Optimization (debounced search, memoized components)
 * 3. Comprehensive Authentication Handling with Auto-redirect
 * 4. Enhanced UI/UX with Filtering, Sorting, and Search
 * 5. Real-time Statistics and Course Management
 * 6. Error Boundary Integration for Production Stability
 * 7. Accessibility Features (ARIA labels, keyboard navigation)
 * 8. Dark Mode Support Throughout
 * 9. Course Cleanup Feature for Large Instructor Accounts
 * 10. Smart Course Actions Based on Course Status
 *
 * Connected Files (Backend Integration):
 * - backend/instructor/api/v1/courses/ (course CRUD operations)
 * - backend/instructor/api/v1/statistics/ (dashboard statistics)
 * - backend/instructor/utils/permissions/ (instructor role validation)
 * - backend/accounts/models.py (User.is_instructor property)
 * - backend/courses/models.py (Course model with all tracked fields)
 *
 * Frontend Integration:
 * - frontend/src/services/instructorService.js (v3.0.0 compatibility)
 * - frontend/src/services/api.js (v4.0.1 compatibility)
 * - frontend/src/contexts/AuthContext.jsx (authentication state)
 * - frontend/src/components/layouts/MainLayout.jsx (layout wrapper)
 */

import React, {
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Alert from '../../components/common/Alert';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { InstructorErrorBoundary } from '../../components/common/errorBoundaries';
import LoadingScreen from '../../components/common/LoadingScreen';
import MainLayout from '../../components/layouts/MainLayout';
import { useAuth } from '../../contexts/AuthContext';
import { useDebounce } from '../../hooks/useDebounce';
import { cleanupDropdowns, initDropdowns } from '../../scripts/dropdown';
import api from '../../services/api';
import instructorService from '../../services/instructorService';
import '../../styles/dashboard-dropdown.css';

// Configuration constants
const VIEW_AS_OPTIONS = [
  { value: 'instructor', label: 'Instructor' },
  { value: 'registered', label: 'Registered learner' },
];

const SCOPE_OPTIONS = [
  { value: 'mine', label: 'My courses' },
  { value: 'all-published', label: 'All published' },
];

const SORT_OPTIONS = [
  { value: 'updated', label: 'Recently updated' },
  { value: 'students', label: 'Enrolled students' },
  { value: 'revenue', label: 'Total revenue' },
];

// Skeleton loading component
const SkeletonGrid = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
    {Array.from({ length: 6 }).map((_, i) => (
      <Card
        key={i}
        className="h-64 animate-pulse bg-gray-100 dark:bg-gray-800"
      />
    ))}
  </div>
);

// Number formatting utility
function numberFormat(value) {
  if (!value) return '$0';

  try {
    return new Intl.NumberFormat(navigator.language || 'en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  } catch {
    return `$${Number(value).toLocaleString()}`;
  }
}

/**
 * Custom hook for filtering and sorting courses with performance optimization
 */
function useVisibleCourses({
  courses,
  debouncedSearch,
  sortKey,
  activeFilter,
  statusFilter,
}) {
  const updatedCache = useRef({});

  return useMemo(() => {
    let list = [...courses];

    // Search (debounced)
    if (debouncedSearch.trim()) {
      const t = debouncedSearch.toLowerCase();
      list = list.filter(
        c => c.title?.toLowerCase().includes(t) || c.slug?.includes(t)
      );
    }

    // Sort with cached date parsing for performance
    switch (sortKey) {
      case 'students':
        list.sort(
          (a, b) => (b.enrolledStudents || 0) - (a.enrolledStudents || 0)
        );
        break;
      case 'revenue':
        list.sort((a, b) => (b.totalRevenue || 0) - (a.totalRevenue || 0));
        break;
      default:
        list.sort((a, b) => {
          const toMs = (d, c) => {
            if (!d) return 0;
            if (!c.current[d]) c.current[d] = new Date(d).getTime();
            return c.current[d];
          };
          return (
            toMs(b.updatedDate, updatedCache) -
            toMs(a.updatedDate, updatedCache)
          );
        });
    }

    // Method/status filter
    return list.filter(course => {
      if (activeFilter !== 'all' && course.creation_method !== activeFilter)
        return false;
      if (statusFilter !== 'all' && course.completion_status !== statusFilter)
        return false;
      return true;
    });
  }, [courses, debouncedSearch, sortKey, activeFilter, statusFilter]);
}

const InstructorDashboard = () => {
  // UI state (persisted in localStorage for better UX)
  const [viewAs, setViewAs] = useState(
    () => localStorage.getItem('viewAs') || 'instructor'
  );
  const [scope, setScope] = useState(
    () => localStorage.getItem('scope') || 'mine'
  );
  const [sortKey, setSortKey] = useState(
    () => localStorage.getItem('sortKey') || 'updated'
  );
  const [rawSearch, setRawSearch] = useState(
    () => localStorage.getItem('search') || ''
  );
  const debouncedSearch = useDebounce(rawSearch, 300);

  // Dashboard state
  const [courses, setCourses] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeFilter, setActiveFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [fetchingCourses, setFetchingCourses] = useState(false);

  const navigate = useNavigate();
  const { isAuthenticated, isInstructor } = useAuth();
  const abortControllerRef = useRef(null);

  // Persist UI state including search
  useEffect(() => {
    localStorage.setItem('viewAs', viewAs);
    localStorage.setItem('scope', scope);
    localStorage.setItem('sortKey', sortKey);
  }, [viewAs, scope, sortKey]);

  useEffect(() => {
    localStorage.setItem('search', rawSearch);
  }, [rawSearch]);

  // Refresh data function
  const refreshData = useCallback(() => {
    setRefreshKey(prevKey => prevKey + 1);
  }, []);

  // Check authentication status before API calls
  const checkAuthBeforeFetch = useCallback(async () => {
    if (isAuthenticated === null) return false;
    if (!isAuthenticated) {
      navigate('/login?redirect=/instructor/dashboard');
      return false;
    }
    if (!isInstructor()) {
      navigate('/');
      return false;
    }
    if (!api.isAuthenticated()) {
      try {
        await api.auth.refreshToken();
        return true;
      } catch {
        navigate('/login?redirect=/instructor/dashboard');
        return false;
      }
    }
    return true;
  }, [isAuthenticated, isInstructor, navigate]);

  // Unified fetchCourses logic with abort controller for throttling
  const fetchCourses = useCallback(async () => {
    // Abort previous request if still running
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    setFetchingCourses(true);
    setError(null);

    try {
      const isAuthorized = await checkAuthBeforeFetch();
      if (!isAuthorized) return;

      // Check if request was aborted
      if (signal.aborted) return;

      // 1. Fetch instructor courses (includes drafts & published)
      let mine = [];
      try {
        const mineResp = await instructorService.getAllCourses();
        if (signal.aborted) return;
        mine = Array.isArray(mineResp) ? mineResp : (mineResp?.results ?? []);
      } catch (error) {
        if (signal.aborted) return;
        throw new Error('Failed to fetch your courses');
      }

      // 2. Optional "all-published" list
      let published = [];
      if (scope === 'all-published') {
        try {
          const publicResp = await api.course.list({
            params: { ordering: '-updated_date' },
          });
          if (signal.aborted) return;
          published = publicResp.results ?? publicResp;
        } catch {
          // Fallback: ignore if public fetch fails, show only mine
        }
      }

      if (signal.aborted) return;

      // Merge & deduplicate by slug
      const merged = [...mine, ...published].reduce((acc, c) => {
        acc[c.slug] = c;
        return acc;
      }, {});

      setCourses(prev => {
        const newArr = Object.values(merged);
        // Shallow equality check for performance
        if (
          prev.length === newArr.length &&
          prev.every((c, i) => c.slug === newArr[i].slug)
        )
          return prev;
        return newArr;
      });

      // Compute statistics in JS for performance
      const coursesArr = Object.values(merged);
      setStatistics({
        totalCourses: coursesArr.length,
        totalStudents: coursesArr.reduce(
          (sum, c) => sum + (c.enrolledStudents || 0),
          0
        ),
        totalRevenue: coursesArr.reduce(
          (sum, c) => sum + (c.totalRevenue || 0),
          0
        ),
        recentEnrollments: coursesArr.reduce(
          (sum, c) => sum + (c.recentEnrollments || 0),
          0
        ),
        coursesByMethod: {
          builder: coursesArr.filter(c => c.creation_method === 'builder').length,
          wizard: coursesArr.filter(c => c.creation_method === 'wizard').length,
          ai: coursesArr.filter(c => c.creation_method === 'ai').length,
          traditional: coursesArr.filter(c => c.creation_method === 'traditional').length,
        },
        coursesByStatus: {
          not_started: coursesArr.filter(c => c.completion_status === 'not_started').length,
          partial: coursesArr.filter(c => c.completion_status === 'partial').length,
          complete: coursesArr.filter(c => c.completion_status === 'complete').length,
          published: coursesArr.filter(c => c.completion_status === 'published').length,
        },
      });
    } catch (error) {
      if (signal.aborted) return;
      setError(error.message || 'Failed to load dashboard data');
      setCourses([]);
      setStatistics(null);
    } finally {
      if (!signal.aborted) {
        setLoading(false);
        setFetchingCourses(false);
      }
    }
  }, [scope, checkAuthBeforeFetch]);

  useEffect(() => {
    if (isAuthenticated !== null) {
      fetchCourses();
    }
  }, [fetchCourses, refreshKey, isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated === null) return;
    if (isAuthenticated === false)
      navigate('/login?redirect=/instructor/dashboard');
    else if (isAuthenticated === true && !isInstructor()) navigate('/');
  }, [isAuthenticated, isInstructor, navigate]);

  useEffect(() => {
    const timer = setTimeout(() => {
      initDropdowns();
    }, 100);
    return () => {
      clearTimeout(timer);
      cleanupDropdowns();
      // Cleanup abort controller on unmount
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [courses]);

  // Course creation/edit handlers, useCallback for stability
  const handleCreateNewCourse = useCallback(() => {
    // Check if user has a preferred editor mode
    const preferredMode = localStorage.getItem('editorMode') || 'options';

    if (preferredMode === 'wizard') {
      navigate('/instructor/courses/wizard');
    } else if (preferredMode === 'traditional') {
      navigate('/instructor/courses/traditional/new');
    } else {
      navigate('/instructor/courses/new'); // Course creation options page
    }
  }, [navigate]);

  const handleCreateWithBuilder = useCallback(
    () => navigate('/instructor/courses/builder'),
    [navigate]
  );

  const handleCreateWithWizard = useCallback(() => {
    localStorage.setItem('editorMode', 'wizard');
    navigate('/instructor/courses/wizard');
  }, [navigate]);

  const handleCreateTraditional = useCallback(() => {
    localStorage.setItem('editorMode', 'traditional');
    navigate('/instructor/courses/traditional/new');
  }, [navigate]);

  const handleCreateAICourse = useCallback(
    courseSlug => {
      if (courseSlug) navigate(`/instructor/courses/ai-builder/${courseSlug}`);
      else navigate('/instructor/courses/ai-builder');
    },
    [navigate]
  );

  const handleCleanupCourses = useCallback(
    () => navigate('/instructor/cleanup'),
    [navigate]
  );

  const handleWizardEdit = useCallback(
    courseSlug => navigate(`/instructor/courses/wizard/${courseSlug}`),
    [navigate]
  );

  const handleBuilderEdit = useCallback(
    courseSlug => navigate(`/instructor/courses/builder/${courseSlug}`),
    [navigate]
  );

  const handleDeleteCourse = useCallback(async (courseSlug) => {
    if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      return;
    }

    try {
      await instructorService.deleteCourse(courseSlug);
      refreshData();
      // Toast notification would go here if available
      console.log('Course deleted successfully');
    } catch (error) {
      console.error('Failed to delete course:', error);
      alert(`Failed to delete course: ${error.message || 'Unknown error'}`);
    }
  }, [refreshData]);

  // Filtering, search & sort helpers
  const visibleCourses = useVisibleCourses({
    courses,
    debouncedSearch,
    sortKey,
    activeFilter,
    statusFilter,
  });

  // Show loading screen while auth state is being determined or data is loading
  if (isAuthenticated === null || loading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading instructor dashboard..." />
      </MainLayout>
    );
  }

  // Top-bar controls with accessibility
  const renderTopBarControls = () => (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-6">
      <div className="flex gap-2 items-center">
        {/* View-As dropdown */}
        <select
          value={viewAs}
          onChange={e => setViewAs(e.target.value)}
          className="input input-sm font-medium dark:bg-gray-800 dark:text-white"
          aria-label="View as"
        >
          {VIEW_AS_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Data scope dropdown */}
        <select
          value={scope}
          onChange={e => setScope(e.target.value)}
          className="input input-sm font-medium dark:bg-gray-800 dark:text-white"
          disabled={fetchingCourses}
          aria-label="Course scope"
        >
          {SCOPE_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Search box with proper label */}
        <div className="relative">
          <label htmlFor="course-search" className="sr-only">
            Search courses
          </label>
          <input
            id="course-search"
            type="search"
            placeholder="Search courses…"
            value={rawSearch}
            onChange={e => setRawSearch(e.target.value)}
            className="input input-sm dark:bg-gray-800 dark:text-white"
            aria-label="Search courses"
          />
        </div>

        {/* Sort key */}
        <select
          value={sortKey}
          onChange={e => setSortKey(e.target.value)}
          className="input input-sm font-medium dark:bg-gray-800 dark:text-white"
          aria-label="Sort by"
        >
          {SORT_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );

  // Memoized Actions component to prevent unnecessary re-renders
  const Actions = React.memo(({ course }) => {
    const onPreview = () =>
      window.open(`/courses/${course.slug}/preview/`, '_blank');

    if (viewAs === 'registered') {
      // Hide preview for drafts
      if (course.is_draft) return null;
      return (
        <Button
          size="sm"
          onClick={onPreview}
          aria-label={`Preview ${course.title}`}
        >
          Preview
        </Button>
      );
    }

    // Instructor mode - comprehensive actions
    return (
      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {course.is_draft ? (
          <Button
            size="sm"
            onClick={() => handleBuilderEdit(course.slug)}
            aria-label={`Resume editing ${course.title}`}
          >
            Resume
          </Button>
        ) : (
          <>
            <Button
              size="sm"
              onClick={() => handleBuilderEdit(course.slug)}
              aria-label={`Edit ${course.title}`}
            >
              Edit
            </Button>
            <Link to={`/instructor/courses/wizard/${course.slug}`}>
              <Button
                size="sm"
                variant="outline"
                aria-label={`Edit ${course.title} with wizard`}
              >
                Wizard
              </Button>
            </Link>
          </>
        )}
        <Button
          size="sm"
          variant="outline"
          onClick={onPreview}
          aria-label={`Preview ${course.title}`}
        >
          Preview
        </Button>
        <Button
          size="sm"
          variant="danger"
          onClick={() => handleDeleteCourse(course.slug)}
          aria-label={`Delete ${course.title}`}
        >
          Delete
        </Button>
      </div>
    );
  });

  // Main render
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center mb-8">
          <h1 className="text-3xl font-bold mb-4 md:mb-0 dark:text-white">
            Instructor Dashboard
          </h1>

          {/* Enhanced Course Creation Actions */}
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <Button
              variant="outline"
              onClick={handleCreateNewCourse}
              className="flex items-center"
              data-testid="create-course-btn"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Create Course
            </Button>

            <Button
              variant="primary"
              className="flex items-center"
              onClick={handleCreateWithBuilder}
              data-testid="course-creation-options-btn"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
              Drag & Drop Builder
            </Button>

            <Button
              variant="secondary"
              className="flex items-center"
              onClick={handleCreateWithWizard}
              data-testid="wizard-btn"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
              Step-by-Step Wizard
            </Button>

            <Button
              variant="outline"
              onClick={handleCreateTraditional}
              className="flex items-center"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Traditional Editor
            </Button>

            <Button
              variant="primary"
              className="flex items-center bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              onClick={handleCreateAICourse}
              data-testid="ai-builder-btn"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              AI-Powered Builder
            </Button>

            {statistics && statistics.totalCourses > 15 && (
              <Button
                variant="danger"
                onClick={handleCleanupCourses}
                className="flex items-center bg-yellow-500 hover:bg-yellow-600 text-white"
                data-testid="cleanup-btn"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                Cleanup Courses ({statistics.totalCourses})
              </Button>
            )}
          </div>
        </div>

        {renderTopBarControls()}

        {error && (
          <Alert type="error" className="mb-6">
            {error}
            <div className="mt-2">
              <Button size="small" variant="outline" onClick={refreshData}>
                Try Again
              </Button>
            </div>
          </Alert>
        )}

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="p-6 bg-primary-50 dark:bg-gray-900">
              <h3 className="text-lg font-medium text-primary-700 dark:text-gray-100 mb-2">
                Total Courses
              </h3>
              <p className="text-3xl font-bold text-primary-900 dark:text-white">
                {statistics.totalCourses || 0}
              </p>
            </Card>
            <Card className="p-6 bg-secondary-50 dark:bg-gray-900">
              <h3 className="text-lg font-medium text-secondary-700 dark:text-gray-100 mb-2">
                Total Students
              </h3>
              <p className="text-3xl font-bold text-secondary-900 dark:text-white">
                {statistics.totalStudents || 0}
              </p>
            </Card>
            <Card className="p-6 bg-tertiary-50 dark:bg-gray-900">
              <h3 className="text-lg font-medium text-tertiary-700 dark:text-gray-100 mb-2">
                Total Revenue
              </h3>
              <p className="text-3xl font-bold text-tertiary-900 dark:text-white">
                {numberFormat(statistics.totalRevenue || 0)}
              </p>
            </Card>
            <Card className="p-6 bg-green-50 dark:bg-gray-900">
              <h3 className="text-lg font-medium text-green-700 dark:text-gray-100 mb-2">
                Recent Enrollments
              </h3>
              <p className="text-3xl font-bold text-green-900 dark:text-white">
                {statistics.recentEnrollments || 0}
              </p>
            </Card>
          </div>
        )}

        {/* Courses Grid */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4 dark:text-white">
            Your Courses
          </h2>
          <Suspense fallback={<SkeletonGrid />}>
            {loading ? (
              <SkeletonGrid />
            ) : visibleCourses.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-6">
                  {rawSearch.trim()
                    ? 'No courses found matching your search.'
                    : "You haven't created any courses yet."}
                </p>
                {!rawSearch.trim() && (
                  <div className="flex justify-center space-x-3">
                    <Button
                      variant="primary"
                      onClick={handleCreateWithWizard}
                    >
                      Create with Wizard
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleCreateTraditional}
                    >
                      Create Traditionally
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {visibleCourses.map(course => (
                  <div
                    key={course.id || course.slug}
                    className="overflow-hidden flex flex-col shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all ease-out duration-200 group relative bg-white dark:bg-gray-800 rounded"
                  >
                    {/* Course thumbnail with preview functionality */}
                    <button
                      type="button"
                      className="block w-full h-40 bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-900 dark:to-gray-800 overflow-hidden group focus:outline-none"
                      onClick={() =>
                        !course.is_draft &&
                        window.open(
                          `/courses/${course.slug}/preview/`,
                          '_blank'
                        )
                      }
                      aria-label={`Preview ${course.title}`}
                      tabIndex={0}
                    >
                      {course.thumbnail ? (
                        <img
                          src={course.thumbnail}
                          alt={course.title}
                          className="w-full h-40 object-cover group-hover:opacity-80"
                          onError={e => {
                            e.target.onerror = null;
                            e.target.src =
                              'https://via.placeholder.com/800x450?text=Course+Thumbnail';
                          }}
                        />
                      ) : (
                        <div className="flex items-center justify-center w-full h-full">
                          <svg
                            className="w-12 h-12 text-gray-400 dark:text-gray-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <title>Placeholder graphic</title>
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                        </div>
                      )}

                      {/* Preview icon overlay */}
                      {!course.is_draft && (
                        <span className="absolute bottom-2 right-2 bg-white/60 dark:bg-gray-900/70 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-all">
                          <svg
                            className="w-6 h-6 text-blue-700 dark:text-blue-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                            />
                          </svg>
                        </span>
                      )}

                      {/* Version/draft badge */}
                      <span className="absolute top-2 left-2 text-xs ml-1 px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                        v{course.version}
                        {course.is_draft && ' • draft'}
                      </span>
                    </button>

                    {/* Course details */}
                    <div className="p-4 flex-grow flex flex-col">
                      <h3
                        className="font-medium text-lg mb-1 line-clamp-1 dark:text-white"
                        title={course.title}
                      >
                        {course.title}
                      </h3>
                      <p
                        className="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2"
                        title={course.description || 'No description provided.'}
                      >
                        {course.description || 'No description provided.'}
                      </p>

                      {/* Course statistics */}
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                        <span className="mr-4">
                          {course.student_count || 0} students
                        </span>
                        <span>
                          {numberFormat(course.revenue || 0)} revenue
                        </span>
                      </div>

                      {/* Draft progress bar */}
                      {course.is_draft && (
                        <div className="mb-2">
                          <progress
                            className="w-full h-1 accent-blue-600 dark:accent-blue-400"
                            value={Math.min(
                              course.completion_percentage || 0,
                              100
                            )}
                            max={100}
                          />
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {Math.min(course.completion_percentage || 0, 100)}%
                            to publish
                          </span>
                        </div>
                      )}

                      <div className="mt-auto pt-2 flex flex-wrap gap-2">
                        <Actions course={course} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Suspense>
        </Card>
      </div>
    </MainLayout>
  );
};

// Export with Error Boundary wrapper for production stability
export default function InstructorDashboardWithErrorBoundary() {
  const navigate = useNavigate();

  const handleNavigateHome = () => {
    navigate('/');
  };

  const handleContactSupport = () => {
    navigate('/support');
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Instructor Dashboard Error:', { error, errorInfo, context });
  };

  return (
    <InstructorErrorBoundary
      onNavigateHome={handleNavigateHome}
      onContactSupport={handleContactSupport}
      onError={handleError}
    >
      <InstructorDashboard />
    </InstructorErrorBoundary>
  );
}
