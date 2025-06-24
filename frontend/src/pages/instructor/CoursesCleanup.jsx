import Alert from '@/components/common/Alert';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import LoadingScreen from '@/components/common/LoadingScreen';
import MainLayout from '@/components/layouts/MainLayout';
import { useAuth } from '@/contexts/AuthContext';
import {
  deleteAllCourses,
  deleteCoursesBatch,
  getAllCourses,
} from '@/scripts/cleanupCourses';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const CoursesCleanup = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [stats, setStats] = useState(null);
  const [batchSize, setBatchSize] = useState(50);
  const { isAuthenticated, isInstructor } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Check user permissions
    if (isAuthenticated === false) {
      navigate('/login?redirect=/instructor/cleanup');
    } else if (isAuthenticated === true && !isInstructor()) {
      navigate('/');
    }
  }, [isAuthenticated, isInstructor, navigate]);

  // Load course data
  useEffect(() => {
    const fetchCourses = async () => {
      if (isAuthenticated === null) return;
      if (!isInstructor()) return;

      try {
        setLoading(true);
        const coursesData = await getAllCourses();
        setCourses(coursesData);
      } catch (err) {
        console.error('Error loading courses:', err);
        setError('Failed to load courses. Please refresh and try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [isAuthenticated, isInstructor]);

  // Handle course deletion - all at once
  const handleDeleteAll = async () => {
    if (
      !window.confirm(
        'WARNING! This will delete ALL courses. This action cannot be undone. Are you absolutely sure?'
      )
    ) {
      return;
    }

    // Double confirmation for large deletions
    if (courses.length > 50) {
      if (
        !window.confirm(
          `You are about to delete ${courses.length} courses. This is a lot! Please confirm again.`
        )
      ) {
        return;
      }
    }

    try {
      setDeleting(true);
      setError(null);
      setSuccess(null);

      const result = await deleteAllCourses();
      if (result.success) {
        setSuccess(`Successfully deleted ${result.results.deleted} courses.`);
        setStats(result.results);
        // Reload the remaining courses
        const remainingCourses = await getAllCourses();
        setCourses(remainingCourses);
      } else {
        setError(`Operation failed: ${result.message}`);
      }
    } catch (err) {
      console.error('Error during deletion:', err);
      setError('Failed to delete courses. See console for details.');
    } finally {
      setDeleting(false);
    }
  };

  // Handle batch deletion
  const handleDeleteBatch = async () => {
    if (
      !window.confirm(
        `This will delete courses in batches of ${batchSize}. Continue?`
      )
    ) {
      return;
    }

    try {
      setDeleting(true);
      setError(null);
      setSuccess(null);

      const result = await deleteCoursesBatch(batchSize);
      if (result.success) {
        setSuccess(`Successfully deleted ${result.results.deleted} courses.`);
        setStats(result.results);
        // Reload the remaining courses
        const remainingCourses = await getAllCourses();
        setCourses(remainingCourses);
      } else {
        setError(`Operation failed: ${result.message}`);
      }
    } catch (err) {
      console.error('Error during batch deletion:', err);
      setError('Failed to delete courses. See console for details.');
    } finally {
      setDeleting(false);
    }
  };

  if (isAuthenticated === null || loading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading courses data..." />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center mb-8">
          <h1 className="text-3xl font-bold mb-4 md:mb-0">
            Course Cleanup Utility
          </h1>
          <Button
            variant="outline"
            onClick={() => navigate('/instructor/dashboard')}
          >
            Back to Dashboard
          </Button>
        </div>

        {error && (
          <Alert type="error" className="mb-6">
            {error}
          </Alert>
        )}

        {success && (
          <Alert type="success" className="mb-6">
            {success}
          </Alert>
        )}

        {stats && (
          <Card className="mb-6 p-6 bg-blue-50">
            <h3 className="text-lg font-semibold mb-3">Operation Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Courses</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <div>
                <p className="text-sm text-green-600">Successfully Deleted</p>
                <p className="text-2xl font-bold text-green-700">
                  {stats.deleted}
                </p>
              </div>
              <div>
                <p className="text-sm text-red-600">Failed</p>
                <p className="text-2xl font-bold text-red-700">
                  {stats.failed}
                </p>
              </div>
            </div>
            {stats.failed > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-red-600 mb-2">
                  Failed Courses:
                </p>
                <ul className="text-sm text-red-700 list-disc pl-5">
                  {stats.failedCourses.slice(0, 10).map((course, index) => (
                    <li
                      key={course.id || course.slug || `failed-course-${index}`}
                    >
                      {course.title} ({course.slug || course.id})
                    </li>
                  ))}
                  {stats.failedCourses.length > 10 && (
                    <li key="more-courses">
                      ...and {stats.failedCourses.length - 10} more
                    </li>
                  )}
                </ul>
              </div>
            )}
          </Card>
        )}

        <Card className="p-6">
          <div className="flex flex-col md:flex-row justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold">
                Total Courses: {courses.length}
              </h2>
              <p className="text-gray-600 mt-1">
                Use the controls below to delete courses in batches or all at
                once.
              </p>
            </div>
          </div>

          <div className="bg-yellow-50 border-yellow-200 border p-4 rounded-md mb-6">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">
              Warning
            </h3>
            <p className="text-yellow-700 mb-2">
              Deleting courses is permanent and cannot be undone. Please be
              careful.
            </p>
            <p className="text-yellow-700">
              If you have a large number of courses to delete, it's recommended
              to use the batch delete option to avoid timeout issues.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border p-4 rounded-md">
              <h3 className="font-medium mb-4">Batch Delete</h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Batch Size
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={batchSize}
                  onChange={e =>
                    setBatchSize(Math.max(1, parseInt(e.target.value) || 10))
                  }
                  className="w-full p-2 border rounded-md"
                />
              </div>
              <Button
                variant="primary"
                className="w-full"
                onClick={handleDeleteBatch}
                disabled={deleting || courses.length === 0}
              >
                {deleting ? 'Deleting...' : `Delete in Batches of ${batchSize}`}
              </Button>
            </div>

            <div className="border p-4 rounded-md">
              <h3 className="font-medium mb-4">Delete All Courses</h3>
              <p className="text-red-600 text-sm mb-4">
                This will attempt to delete all courses at once. For large
                numbers, this might timeout.
              </p>
              <Button
                variant="danger"
                className="w-full"
                onClick={handleDeleteAll}
                disabled={deleting || courses.length === 0}
              >
                {deleting
                  ? 'Deleting...'
                  : `Delete All ${courses.length} Courses`}
              </Button>
            </div>
          </div>

          {courses.length > 0 && (
            <div className="mt-8">
              <h3 className="font-medium mb-3">Current Courses</h3>
              <div className="max-h-96 overflow-y-auto border rounded-md">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ID/Slug
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {courses.slice(0, 100).map((course, index) => (
                      <tr key={course.id || course.slug || `course-${index}`}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {course.title}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {course.is_published ? 'Published' : 'Draft'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {course.slug || course.id}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {courses.length > 100 && (
                  <div className="px-6 py-3 bg-gray-50 text-center text-sm text-gray-500">
                    Showing 100 of {courses.length} courses
                  </div>
                )}
              </div>
            </div>
          )}
        </Card>
      </div>
    </MainLayout>
  );
};

export default CoursesCleanup;
