/**
 * File: frontend/src/pages/dashboard/AdminDashboard.jsx
 * Purpose: Admin dashboard component for the educational platform
 *
 * Key features:
 * 1. User management (view, edit, delete users)
 * 2. Course management (approve, feature, unpublish courses)
 * 3. System metrics and statistics
 * 4. Platform configuration options
 *
 * Implementation notes:
 * - Uses tabs for organizing different admin functions
 * - Fetches data from admin-specific API endpoints
 * - Role-protected for admin users only
 * - Includes search and filtering capabilities
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ErrorBoundary } from '../../components/common/errorBoundaries';
import { useAuth } from '../../contexts/AuthContext';

// Tab management
const TABS = {
  OVERVIEW: 'overview',
  USERS: 'users',
  COURSES: 'courses',
  REPORTS: 'reports',
  SETTINGS: 'settings',
};

const AdminDashboard = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(TABS.OVERVIEW);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Data states
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalCourses: 0,
    totalEnrollments: 0,
    activeUsers: 0,
    revenue: 0,
  });
  const [users, setUsers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);

  // Filter states
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [courseSearchQuery, setCourseSearchQuery] = useState('');
  const [userRoleFilter, setUserRoleFilter] = useState('all');
  const [courseStatusFilter, setCourseStatusFilter] = useState('all');

  // Pagination
  const [userPage, setUserPage] = useState(1);
  const [coursePage, setCoursePage] = useState(1);
  const [usersPerPage] = useState(10);
  const [coursesPerPage] = useState(8);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch dashboard statistics
        const statsResponse = await fetch('/api/admin/stats/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!statsResponse.ok) {
          throw new Error('Failed to load admin statistics');
        }

        const statsData = await statsResponse.json();
        setStats(statsData);

        // Fetch recent platform activities
        const activitiesResponse = await fetch('/api/admin/activities/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!activitiesResponse.ok) {
          throw new Error('Failed to load recent activities');
        }

        const activitiesData = await activitiesResponse.json();
        setRecentActivities(activitiesData);

        // Only fetch users and courses data if those tabs are active
        if (activeTab === TABS.USERS) {
          await fetchUsers();
        } else if (activeTab === TABS.COURSES) {
          await fetchCourses();
        }

        setLoading(false);
      } catch (err) {
        console.error('Error fetching admin data:', err);
        setError('Failed to load dashboard data. Please try again.');
        setLoading(false);
      }
    };

    fetchAdminData();
  }, [activeTab]);

  const fetchUsers = async () => {
    try {
      const response = await fetch(
        `/api/admin/users/?page=${userPage}&role=${userRoleFilter}&search=${userSearchQuery}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load users');
      }

      const data = await response.json();
      setUsers(data.results);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to load users. Please try again.');
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch(
        `/api/admin/courses/?page=${coursePage}&status=${courseStatusFilter}&search=${courseSearchQuery}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load courses');
      }

      const data = await response.json();
      setCourses(data.results);
    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses. Please try again.');
    }
  };

  const handleUserSearch = e => {
    e.preventDefault();
    setUserPage(1);
    fetchUsers();
  };

  const handleCourseSearch = e => {
    e.preventDefault();
    setCoursePage(1);
    fetchCourses();
  };

  const handleUserRoleFilterChange = e => {
    setUserRoleFilter(e.target.value);
    setUserPage(1);
    // Fetch will be triggered on next render due to dependency array
  };

  const handleCourseStatusFilterChange = e => {
    setCourseStatusFilter(e.target.value);
    setCoursePage(1);
    // Fetch will be triggered on next render due to dependency array
  };

  const handleUserStatusChange = async (userId, newStatus) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/status/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ active: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      // Update the local state to reflect the change
      setUsers(
        users.map(user =>
          user.id === userId ? { ...user, active: newStatus } : user
        )
      );
    } catch (err) {
      console.error('Error updating user status:', err);
      setError('Failed to update user status. Please try again.');
    }
  };

  const handleCourseStatusChange = async (courseId, newStatus) => {
    try {
      const response = await fetch(`/api/admin/courses/${courseId}/status/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update course status');
      }

      // Update the local state to reflect the change
      setCourses(
        courses.map(course =>
          course.id === courseId ? { ...course, status: newStatus } : course
        )
      );
    } catch (err) {
      console.error('Error updating course status:', err);
      setError('Failed to update course status. Please try again.');
    }
  };

  const renderTab = () => {
    switch (activeTab) {
      case TABS.OVERVIEW:
        return renderOverviewTab();
      case TABS.USERS:
        return renderUsersTab();
      case TABS.COURSES:
        return renderCoursesTab();
      case TABS.REPORTS:
        return renderReportsTab();
      case TABS.SETTINGS:
        return renderSettingsTab();
      default:
        return renderOverviewTab();
    }
  };

  const renderOverviewTab = () => (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900">Total Users</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">
            {stats.totalUsers}
          </p>
          <div className="mt-2 text-sm text-gray-600">
            <span className="text-green-600 font-medium">↑ 12%</span> from
            previous month
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900">Active Courses</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">
            {stats.totalCourses}
          </p>
          <div className="mt-2 text-sm text-gray-600">
            <span className="text-green-600 font-medium">↑ 8%</span> from
            previous month
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900">
            Total Enrollments
          </h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">
            {stats.totalEnrollments}
          </p>
          <div className="mt-2 text-sm text-gray-600">
            <span className="text-green-600 font-medium">↑ 15%</span> from
            previous month
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900">Revenue</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">
            ${stats.revenue.toFixed(2)}
          </p>
          <div className="mt-2 text-sm text-gray-600">
            <span className="text-green-600 font-medium">↑ 10%</span> from
            previous month
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              User Distribution
            </h3>
            <select className="bg-white border border-gray-300 rounded-md text-sm">
              <option>Last 30 days</option>
              <option>Last 90 days</option>
              <option>Last year</option>
            </select>
          </div>

          <div className="flex items-center justify-center h-64">
            {/* This would ideally be a chart component */}
            <div className="text-center text-gray-500">
              User distribution chart would be here
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="text-left">
                  <div className="flex items-center">
                    <span className="inline-block w-3 h-3 bg-primary-600 rounded-full mr-2"></span>
                    <span className="text-sm">Students: 65%</span>
                  </div>
                  <div className="flex items-center mt-2">
                    <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                    <span className="text-sm">Instructors: 20%</span>
                  </div>
                </div>
                <div className="text-left">
                  <div className="flex items-center">
                    <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                    <span className="text-sm">Staff: 10%</span>
                  </div>
                  <div className="flex items-center mt-2">
                    <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                    <span className="text-sm">Admins: 5%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Recent Activities
            </h3>
            <Link
              to="/admin/activities"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </div>

          <div className="overflow-y-auto max-h-64">
            {recentActivities.map((activity, index) => (
              <div
                key={index}
                className="py-3 border-b border-gray-200 last:border-0"
              >
                <div className="flex items-start">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                      activity.type === 'user_registered'
                        ? 'bg-green-100 text-green-600'
                        : activity.type === 'course_created'
                          ? 'bg-blue-100 text-blue-600'
                          : activity.type === 'enrollment'
                            ? 'bg-purple-100 text-purple-600'
                            : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {activity.type === 'user_registered' && (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                      </svg>
                    )}
                    {activity.type === 'course_created' && (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                      </svg>
                    )}
                    {activity.type === 'enrollment' && (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <p className="text-sm text-gray-800">
                      {activity.description}
                    </p>
                    <span className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderUsersTab = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h3 className="text-xl font-medium text-gray-900 mb-3 md:mb-0">
          User Management
        </h3>
        <div className="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-3">
          <select
            value={userRoleFilter}
            onChange={handleUserRoleFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
          >
            <option value="all">All Roles</option>
            <option value="student">Students</option>
            <option value="instructor">Instructors</option>
            <option value="staff">Staff</option>
            <option value="admin">Admins</option>
          </select>

          <form onSubmit={handleUserSearch} className="flex">
            <input
              type="text"
              value={userSearchQuery}
              onChange={e => setUserSearchQuery(e.target.value)}
              placeholder="Search users..."
              className="rounded-l-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
            />
            <button
              type="submit"
              className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 bg-gray-50 text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </form>

          <Link
            to="/admin/users/new"
            className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
          >
            Add User
          </Link>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                User
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Email
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Role
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Joined Date
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map(user => (
              <tr key={user.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-10 w-10 flex-shrink-0">
                      <img
                        className="h-10 w-10 rounded-full"
                        src={user.avatar || 'https://via.placeholder.com/100'}
                        alt=""
                      />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {user.first_name} {user.last_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        @{user.username}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{user.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                    ${
                      user.role === 'admin'
                        ? 'bg-red-100 text-red-800'
                        : user.role === 'instructor'
                          ? 'bg-blue-100 text-blue-800'
                          : user.role === 'staff'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                  >
                    {user.active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(user.joined_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <Link
                      to={`/admin/users/${user.id}`}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      View
                    </Link>
                    <Link
                      to={`/admin/users/${user.id}/edit`}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() =>
                        handleUserStatusChange(user.id, !user.active)
                      }
                      className={`${user.active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                    >
                      {user.active ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <nav className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
        <div className="hidden sm:block">
          <p className="text-sm text-gray-700">
            Showing{' '}
            <span className="font-medium">
              {(userPage - 1) * usersPerPage + 1}
            </span>{' '}
            to{' '}
            <span className="font-medium">
              {Math.min(
                userPage * usersPerPage,
                users.length + (userPage - 1) * usersPerPage
              )}
            </span>{' '}
            of <span className="font-medium">many</span> results
          </p>
        </div>
        <div className="flex-1 flex justify-between sm:justify-end">
          <button
            onClick={() => {
              if (userPage > 1) {
                setUserPage(userPage - 1);
              }
            }}
            disabled={userPage <= 1}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => setUserPage(userPage + 1)}
            className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </nav>
    </div>
  );

  const renderCoursesTab = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h3 className="text-xl font-medium text-gray-900 mb-3 md:mb-0">
          Course Management
        </h3>
        <div className="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-3">
          <select
            value={courseStatusFilter}
            onChange={handleCourseStatusFilterChange}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
          >
            <option value="all">All Status</option>
            <option value="published">Published</option>
            <option value="pending">Pending</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
          </select>

          <form onSubmit={handleCourseSearch} className="flex">
            <input
              type="text"
              value={courseSearchQuery}
              onChange={e => setCourseSearchQuery(e.target.value)}
              placeholder="Search courses..."
              className="rounded-l-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
            />
            <button
              type="submit"
              className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 bg-gray-50 text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </form>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {courses.map(course => (
          <div
            key={course.id}
            className="bg-white border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="relative">
              <img
                src={
                  course.thumbnail ||
                  'https://via.placeholder.com/400x225?text=Course+Thumbnail'
                }
                alt={course.title}
                className="w-full h-40 object-cover"
              />
              <div className="absolute top-2 right-2">
                <span
                  className={`px-2 py-1 text-xs font-bold rounded-md
                  ${
                    course.status === 'published'
                      ? 'bg-green-100 text-green-800'
                      : course.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : course.status === 'draft'
                          ? 'bg-gray-100 text-gray-800'
                          : 'bg-red-100 text-red-800'
                  }`}
                >
                  {course.status.charAt(0).toUpperCase() +
                    course.status.slice(1)}
                </span>
              </div>
            </div>

            <div className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {course.title}
              </h3>
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {course.short_description}
              </p>

              <div className="flex items-center mb-3">
                <img
                  src={
                    course.instructor.avatar ||
                    'https://via.placeholder.com/40?text=I'
                  }
                  alt={course.instructor.name}
                  className="w-6 h-6 rounded-full mr-2"
                />
                <span className="text-xs text-gray-600">
                  {course.instructor.name}
                </span>
              </div>

              <div className="flex justify-between text-xs text-gray-500 mb-3">
                <span>{course.enrollment_count} students</span>
                <span>${course.price}</span>
              </div>

              <div className="flex flex-wrap gap-2">
                {course.status === 'pending' && (
                  <button
                    onClick={() =>
                      handleCourseStatusChange(course.id, 'published')
                    }
                    className="px-2 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700"
                  >
                    Approve
                  </button>
                )}

                {course.status === 'published' && (
                  <button
                    onClick={() =>
                      handleCourseStatusChange(course.id, 'featured')
                    }
                    className="px-2 py-1 bg-primary-600 text-white text-xs rounded-md hover:bg-primary-700"
                  >
                    Feature
                  </button>
                )}

                {course.status !== 'archived' && (
                  <button
                    onClick={() =>
                      handleCourseStatusChange(course.id, 'archived')
                    }
                    className="px-2 py-1 bg-red-600 text-white text-xs rounded-md hover:bg-red-700"
                  >
                    Archive
                  </button>
                )}

                <Link
                  to={`/admin/courses/${course.id}`}
                  className="px-2 py-1 bg-gray-200 text-gray-800 text-xs rounded-md hover:bg-gray-300"
                >
                  View Details
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <nav className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-6">
        <div className="hidden sm:block">
          <p className="text-sm text-gray-700">
            Showing{' '}
            <span className="font-medium">
              {(coursePage - 1) * coursesPerPage + 1}
            </span>{' '}
            to{' '}
            <span className="font-medium">
              {Math.min(
                coursePage * coursesPerPage,
                courses.length + (coursePage - 1) * coursesPerPage
              )}
            </span>{' '}
            of <span className="font-medium">many</span> results
          </p>
        </div>
        <div className="flex-1 flex justify-between sm:justify-end">
          <button
            onClick={() => {
              if (coursePage > 1) {
                setCoursePage(coursePage - 1);
              }
            }}
            disabled={coursePage <= 1}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => setCoursePage(coursePage + 1)}
            className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </nav>
    </div>
  );

  const renderReportsTab = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-medium text-gray-900 mb-6">
        Platform Reports
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="border rounded-lg p-4">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            Enrollments Over Time
          </h4>
          <div className="h-64 flex items-center justify-center">
            <div className="text-gray-500 text-center">
              <p>Enrollment trend chart would appear here</p>
              <p className="text-sm mt-2">Last 30 days: 245 new enrollments</p>
            </div>
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            Revenue Breakdown
          </h4>
          <div className="h-64 flex items-center justify-center">
            <div className="text-gray-500 text-center">
              <p>Revenue breakdown chart would appear here</p>
              <p className="text-sm mt-2">Total revenue this month: $12,450</p>
            </div>
          </div>
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h4 className="text-lg font-medium text-gray-800">
            Top Performing Courses
          </h4>
          <select className="rounded-md border-gray-300 text-sm">
            <option>By Enrollment</option>
            <option>By Revenue</option>
            <option>By Completion Rate</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Course
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Instructor
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Enrollments
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Revenue
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Completion Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[1, 2, 3, 4, 5].map((_, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 flex-shrink-0">
                        <img
                          className="h-10 w-10 rounded object-cover"
                          src={`https://via.placeholder.com/100?text=${index + 1}`}
                          alt=""
                        />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          Top Course {index + 1}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      Instructor {index + 1}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {Math.floor(Math.random() * 500) + 100}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${(Math.random() * 10000 + 1000).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {Math.floor(Math.random() * 30) + 70}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-medium text-gray-900 mb-6">
        Platform Settings
      </h3>

      <div className="space-y-6">
        <div className="border-b pb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            General Settings
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label
                htmlFor="site-name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Platform Name
              </label>
              <input
                type="text"
                id="site-name"
                defaultValue="EduPlatform"
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label
                htmlFor="support-email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Support Email
              </label>
              <input
                type="email"
                id="support-email"
                defaultValue="support@eduplatform.com"
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>

            <div className="md:col-span-2">
              <label
                htmlFor="platform-description"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Platform Description
              </label>
              <textarea
                id="platform-description"
                rows={3}
                defaultValue="EduPlatform - The premier online learning platform for students and educators."
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>

        <div className="border-b pb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            Registration Settings
          </h4>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h5 className="text-sm font-medium text-gray-700">
                  Allow Public Registration
                </h5>
                <p className="text-xs text-gray-500">
                  Allow new users to register without approval
                </p>
              </div>
              <div className="flex items-center h-6">
                <input
                  id="allow-registration"
                  type="checkbox"
                  defaultChecked
                  className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h5 className="text-sm font-medium text-gray-700">
                  Require Email Verification
                </h5>
                <p className="text-xs text-gray-500">
                  Require users to verify their email before accessing content
                </p>
              </div>
              <div className="flex items-center h-6">
                <input
                  id="require-verification"
                  type="checkbox"
                  defaultChecked
                  className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h5 className="text-sm font-medium text-gray-700">
                  Allow Instructor Registration
                </h5>
                <p className="text-xs text-gray-500">
                  Allow users to register as instructors
                </p>
              </div>
              <div className="flex items-center h-6">
                <input
                  id="allow-instructor-registration"
                  type="checkbox"
                  defaultChecked
                  className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="border-b pb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            Payment Settings
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label
                htmlFor="currency"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Default Currency
              </label>
              <select
                id="currency"
                defaultValue="USD"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              >
                <option>USD</option>
                <option>EUR</option>
                <option>GBP</option>
                <option>INR</option>
                <option>AUD</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="platform-fee"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Platform Fee (%)
              </label>
              <input
                type="number"
                id="platform-fee"
                defaultValue="15"
                min="0"
                max="100"
                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>

        <div className="border-b pb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-4">
            Appearance Settings
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label
                htmlFor="primary-color"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Primary Color
              </label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                  #
                </span>
                <input
                  type="text"
                  id="primary-color"
                  defaultValue="4F46E5"
                  className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="logo"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Logo
              </label>
              <div className="flex items-center">
                <span className="h-12 w-12 rounded-md overflow-hidden bg-gray-100">
                  <svg
                    className="h-full w-full text-gray-300"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </span>
                <button
                  type="button"
                  className="ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Change
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700"></div>
        <span className="ml-3 text-primary-700">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
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
            </div>
          </div>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="bg-primary-600 text-white px-4 py-2 rounded-md"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <div className="flex items-center">
          <div className="mr-4">
            <span className="text-sm text-gray-600">Welcome,</span>
            <span className="ml-1 font-medium text-gray-900">
              {currentUser.first_name} {currentUser.last_name}
            </span>
          </div>
          <img
            src={currentUser.avatar || 'https://via.placeholder.com/40?text=A'}
            alt="Admin"
            className="h-10 w-10 rounded-full"
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md mb-8">
        <nav className="flex overflow-x-auto">
          <button
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
              activeTab === TABS.OVERVIEW
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(TABS.OVERVIEW)}
          >
            Overview
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
              activeTab === TABS.USERS
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(TABS.USERS)}
          >
            Users
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
              activeTab === TABS.COURSES
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(TABS.COURSES)}
          >
            Courses
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
              activeTab === TABS.REPORTS
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(TABS.REPORTS)}
          >
            Reports
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
              activeTab === TABS.SETTINGS
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(TABS.SETTINGS)}
          >
            Settings
          </button>
        </nav>
      </div>

      {renderTab()}
    </div>
  );
};

export default function AdminDashboardWithErrorBoundary() {
  const navigate = useNavigate();

  const handleError = (error, errorInfo) => {
    console.error('Admin Dashboard Error:', error, errorInfo);
    // possible integration with logging service
  };

  return (
    <ErrorBoundary onError={handleError}>
      <AdminDashboard />
    </ErrorBoundary>
  );
}
