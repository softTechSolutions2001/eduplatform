import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const UserCoursesPage = () => {
  const { currentUser } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('in-progress');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');

  // Current date and time from the provided information
  const currentDate = new Date('2025-04-20 09:52:10');

  // Current username
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);

        // In a real application, this would be an API call
        // const response = await api.get('/api/users/courses/');
        // setCourses(response.data);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));

        // Mock data for different course states
        const mockCourses = [
          {
            id: 1,
            title:
              'Advanced React and Redux: Building Scalable Web Applications',
            instructor: 'Alex Johnson',
            thumbnail:
              'https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Web Development',
            progress: 65,
            lastAccessed: '2025-04-18T10:30:00Z',
            status: 'in-progress',
            totalLessons: 42,
            completedLessons: 27,
            nextLesson: 'Advanced Redux Patterns',
            dueDate: '2025-05-10T23:59:59Z',
            certificateAvailable: false,
          },
          {
            id: 2,
            title: 'Machine Learning Fundamentals',
            instructor: 'Dr. Alan Wong',
            thumbnail:
              'https://images.unsplash.com/photo-1527474305487-b87b222841cc?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Data Science',
            progress: 100,
            lastAccessed: '2025-04-15T14:20:00Z',
            status: 'completed',
            totalLessons: 38,
            completedLessons: 38,
            completionDate: '2025-04-15T14:20:00Z',
            certificateAvailable: true,
            certificateId: 'ML-FUND-21325',
            grade: 'A',
          },
          {
            id: 3,
            title: 'Python Programming Masterclass',
            instructor: 'Jane Smith',
            thumbnail:
              'https://images.unsplash.com/photo-1526379879527-8559ecfcaec0?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Programming',
            progress: 35,
            lastAccessed: '2025-04-19T08:15:00Z',
            status: 'in-progress',
            totalLessons: 56,
            completedLessons: 19,
            nextLesson: 'Advanced List Comprehensions',
            dueDate: '2025-05-25T23:59:59Z',
            certificateAvailable: false,
          },
          {
            id: 4,
            title: 'Mobile App Development with Flutter',
            instructor: 'Sarah Wilson',
            thumbnail:
              'https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Mobile Development',
            progress: 100,
            lastAccessed: '2025-04-10T16:45:00Z',
            status: 'completed',
            totalLessons: 45,
            completedLessons: 45,
            completionDate: '2025-04-10T16:45:00Z',
            certificateAvailable: true,
            certificateId: 'FLUTTER-DEV-78965',
            grade: 'B+',
          },
          {
            id: 5,
            title: 'Data Analysis with Python and Pandas',
            instructor: 'Michael Brown',
            thumbnail:
              'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Data Science',
            progress: 82,
            lastAccessed: '2025-04-20T07:30:00Z',
            status: 'in-progress',
            totalLessons: 36,
            completedLessons: 29,
            nextLesson: 'Time Series Analysis',
            dueDate: '2025-05-05T23:59:59Z',
            certificateAvailable: false,
          },
          {
            id: 6,
            title: 'UI/UX Design Principles',
            instructor: 'David Lee',
            thumbnail:
              'https://images.unsplash.com/photo-1561070791-2526d30994b5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Design',
            progress: 100,
            lastAccessed: '2025-04-01T11:20:00Z',
            status: 'completed',
            totalLessons: 32,
            completedLessons: 32,
            completionDate: '2025-04-01T11:20:00Z',
            certificateAvailable: true,
            certificateId: 'UI-UX-DESIGN-54321',
            grade: 'A-',
          },
          {
            id: 7,
            title: 'DevOps for Beginners',
            instructor: 'Robert Johnson',
            thumbnail:
              'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'DevOps',
            progress: 15,
            lastAccessed: '2025-04-12T09:45:00Z',
            status: 'in-progress',
            totalLessons: 40,
            completedLessons: 6,
            nextLesson: 'Continuous Integration Setup',
            dueDate: '2025-06-15T23:59:59Z',
            certificateAvailable: false,
          },
          {
            id: 8,
            title: 'Blockchain Development Fundamentals',
            instructor: 'Linda Chen',
            thumbnail:
              'https://images.unsplash.com/photo-1639322537228-f710d846310a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            category: 'Blockchain',
            progress: 0,
            enrollmentDate: '2025-04-19T14:30:00Z',
            status: 'not-started',
            totalLessons: 28,
            completedLessons: 0,
            nextLesson: 'Introduction to Blockchain',
            dueDate: '2025-06-30T23:59:59Z',
            certificateAvailable: false,
          },
        ];

        setCourses(mockCourses);
      } catch (err) {
        console.error('Error fetching courses:', err);
        setError('Failed to load your courses. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  // Filter courses based on active tab and search query
  const filteredCourses = courses
    .filter(course => {
      const matchesTab = activeTab === 'all' || course.status === activeTab;
      const matchesSearch =
        course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.instructor.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.category.toLowerCase().includes(searchQuery.toLowerCase());

      return matchesTab && matchesSearch;
    })
    .sort((a, b) => {
      if (sortBy === 'recent') {
        return (
          new Date(b.lastAccessed || b.enrollmentDate) -
          new Date(a.lastAccessed || a.enrollmentDate)
        );
      } else if (sortBy === 'progress') {
        return b.progress - a.progress;
      } else if (sortBy === 'title-asc') {
        return a.title.localeCompare(b.title);
      } else {
        return a.title.localeCompare(b.title) * -1;
      }
    });

  // Calculate statistics
  const courseStats = {
    total: courses.length,
    completed: courses.filter(course => course.status === 'completed').length,
    inProgress: courses.filter(course => course.status === 'in-progress')
      .length,
    notStarted: courses.filter(course => course.status === 'not-started')
      .length,
  };

  const calculateDaysLeft = dueDate => {
    const due = new Date(dueDate);
    const diffTime = due - currentDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const formatDate = dateString => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-lg text-gray-600">
              Loading your courses...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mx-auto h-16 w-16 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h2 className="mt-4 text-2xl font-bold text-gray-900">Error</h2>
            <p className="mt-2 text-lg text-gray-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-primary-700 pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-white sm:text-3xl sm:truncate">
                My Learning
              </h1>
              <p className="mt-2 text-lg text-primary-200">
                Track your progress and manage your learning journey
              </p>
            </div>
            <div className="mt-4 flex md:mt-0">
              <Link
                to="/courses"
                className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white"
              >
                Browse More Courses
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-primary-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Courses
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseStats.total}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-green-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Completed
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseStats.completed}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-blue-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      In Progress
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseStats.inProgress}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-yellow-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Not Started
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseStats.notStarted}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="border-b border-gray-200 px-4 py-4 sm:px-6">
            <div className="flex flex-wrap items-center justify-between">
              <div className="flex flex-1 min-w-0">
                <div className="flex-1">
                  <div className="relative rounded-md shadow-sm w-full max-w-xs">
                    <input
                      type="text"
                      className="focus:ring-primary-500 focus:border-primary-500 block w-full pr-10 sm:text-sm border-gray-300 rounded-md"
                      placeholder="Search courses"
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <svg
                        className="h-5 w-5 text-gray-400"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center mt-3 sm:mt-0">
                <label
                  htmlFor="sort-by"
                  className="block text-sm font-medium text-gray-700 mr-2"
                >
                  Sort by:
                </label>
                <select
                  id="sort-by"
                  name="sort-by"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                >
                  <option value="recent">Recently Accessed</option>
                  <option value="progress">Progress</option>
                  <option value="title-asc">Title (A-Z)</option>
                  <option value="title-desc">Title (Z-A)</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <nav className="-mb-px flex">
                {['all', 'in-progress', 'completed', 'not-started'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`${
                      activeTab === tab
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } whitespace-nowrap py-2 px-4 border-b-2 font-medium text-sm capitalize`}
                  >
                    {tab === 'all'
                      ? 'All Courses'
                      : tab === 'in-progress'
                        ? 'In Progress'
                        : tab === 'completed'
                          ? 'Completed'
                          : 'Not Started'}
                    <span className="ml-1 text-gray-400">
                      (
                      {tab === 'all'
                        ? courseStats.total
                        : tab === 'in-progress'
                          ? courseStats.inProgress
                          : tab === 'completed'
                            ? courseStats.completed
                            : courseStats.notStarted}
                      )
                    </span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          <div className="px-4 py-5 sm:p-6">
            {filteredCourses.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No courses found
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {activeTab !== 'all'
                    ? `You don't have any ${activeTab.replace('-', ' ')} courses.`
                    : 'No courses match your search criteria.'}
                </p>
                {activeTab !== 'all' && (
                  <div className="mt-6">
                    <button
                      onClick={() => setActiveTab('all')}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      View All Courses
                    </button>
                  </div>
                )}
                {searchQuery && (
                  <div className="mt-6">
                    <button
                      onClick={() => setSearchQuery('')}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      Clear Search
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <ul className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {filteredCourses.map(course => (
                  <li
                    key={course.id}
                    className="col-span-1 bg-white rounded-lg shadow border border-gray-200 overflow-hidden"
                  >
                    <div className="h-40 overflow-hidden">
                      <img
                        className="w-full h-full object-cover"
                        src={course.thumbnail}
                        alt={course.title}
                      />
                    </div>
                    <div className="p-5">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3
                            className="text-lg font-medium text-gray-900 truncate"
                            title={course.title}
                          >
                            <Link
                              to={`/courses/${course.id}`}
                              className="hover:text-primary-600"
                            >
                              {course.title.length > 50
                                ? `${course.title.substring(0, 50)}...`
                                : course.title}
                            </Link>
                          </h3>
                          <p className="text-sm text-gray-500">
                            {course.instructor}
                          </p>
                        </div>
                        {course.status === 'completed' &&
                          course.certificateAvailable && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Certificate
                            </span>
                          )}
                      </div>

                      <div className="mt-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-700 font-medium">
                            Progress
                          </span>
                          <span className="text-gray-700">
                            {course.progress}%
                          </span>
                        </div>
                        <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              course.status === 'completed'
                                ? 'bg-green-500'
                                : course.progress > 60
                                  ? 'bg-primary-500'
                                  : course.progress > 30
                                    ? 'bg-yellow-500'
                                    : course.progress > 0
                                      ? 'bg-orange-500'
                                      : 'bg-gray-300'
                            }`}
                            style={{ width: `${course.progress}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="mt-5 border-t border-gray-200 pt-4">
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>
                            {course.status === 'completed'
                              ? 'Completed on:'
                              : course.status === 'not-started'
                                ? 'Enrolled on:'
                                : 'Last accessed:'}
                          </span>
                          <span>
                            {formatDate(
                              course.completionDate ||
                                course.lastAccessed ||
                                course.enrollmentDate
                            )}
                          </span>
                        </div>

                        {course.status === 'in-progress' && (
                          <div className="mt-2 text-xs text-gray-500 flex justify-between">
                            <span>Next:</span>
                            <span
                              title={course.nextLesson}
                              className="truncate"
                              style={{ maxWidth: '70%' }}
                            >
                              {course.nextLesson}
                            </span>
                          </div>
                        )}

                        {course.dueDate && course.status !== 'completed' && (
                          <div className="mt-2 text-xs flex justify-between">
                            <span className="text-gray-500">Due:</span>
                            <span
                              className={`${calculateDaysLeft(course.dueDate) < 7 ? 'text-red-600 font-medium' : 'text-gray-500'}`}
                            >
                              {formatDate(course.dueDate)}
                              {calculateDaysLeft(course.dueDate) < 7 && (
                                <span className="ml-1">
                                  ({calculateDaysLeft(course.dueDate)} days
                                  left)
                                </span>
                              )}
                            </span>
                          </div>
                        )}

                        {course.status === 'completed' && course.grade && (
                          <div className="mt-2 text-xs text-gray-500 flex justify-between">
                            <span>Grade:</span>
                            <span className="font-medium">{course.grade}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-4">
                        {course.status === 'completed' &&
                        course.certificateAvailable ? (
                          <div className="flex space-x-3">
                            <Link
                              to={`/dashboard/certificates/${course.certificateId}`}
                              className="flex-1 bg-green-100 py-2 px-4 border border-transparent rounded-md text-sm font-medium text-green-700 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 text-center"
                            >
                              View Certificate
                            </Link>
                            <Link
                              to={`/courses/${course.id}`}
                              className="flex-1 bg-gray-100 py-2 px-4 border border-transparent rounded-md text-sm font-medium text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 text-center"
                            >
                              Review
                            </Link>
                          </div>
                        ) : course.status === 'not-started' ? (
                          <Link
                            to={`/courses/${course.id}`}
                            className="block w-full bg-primary-600 py-2 px-4 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 text-center"
                          >
                            Start Learning
                          </Link>
                        ) : (
                          <Link
                            to={`/courses/${course.id}`}
                            className="block w-full bg-primary-600 py-2 px-4 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 text-center"
                          >
                            Continue Learning
                          </Link>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserCoursesPage;
