/**
 * File: frontend/src/pages/courses/CoursesListPage.jsx
 * Purpose: Course listing page component for the educational platform
 *
 * This component:
 * 1. Displays a paginated, filterable list of all courses
 * 2. Provides search, filtering by category and level, and sorting options
 * 3. Shows course cards with details and links to individual course pages
 * 4. Handles pagination for large course collections
 *
 * Key Updates (2025-06-21):
 * - Updated to handle DRF paginated response format (results array)
 * - Added defensive data handling for API response compatibility
 * - Fixed filtering and sorting functions to handle various data formats
 * - Added more robust error handling for API failures
 * - Updated to match the refactored backend API structure
 *
 * API Endpoints Used:
 * - GET /courses/ - List all courses with optional filters
 * - GET /categories/ - List all course categories
 *
 * URL Structure:
 * - Course list: /courses
 * - Individual course: /courses/:slug (not /courses/:id)
 *
 * Variables to modify for customization:
 * - coursesPerPage: Number of courses to display per page
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-06-21 16:36:44
 * Updated by: sujibeautysalon
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { categoryService, courseService } from '../../services/api';

const CoursesListPage = () => {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('popular');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });
  const coursesPerPage = 9;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Make real API calls to fetch data
        const [coursesResponse, categoriesResponse] = await Promise.all([
          courseService.getAllCourses(),
          categoryService.getAllCategories(),
        ]);

        // Handle DRF paginated response format
        if (coursesResponse && typeof coursesResponse === 'object') {
          // If response is paginated (has 'results' array)
          if (Array.isArray(coursesResponse.results)) {
            setCourses(coursesResponse.results);
            setPagination({
              count: coursesResponse.count || 0,
              next: coursesResponse.next,
              previous: coursesResponse.previous
            });
          }
          // If response is an array directly
          else if (Array.isArray(coursesResponse)) {
            setCourses(coursesResponse);
          }
          // If none of the above, try to extract courses from the object
          else {
            console.warn('Unexpected API response format for courses');
            // Check if there's any array property in the object
            const possibleCourseArrays = Object.values(coursesResponse)
              .filter(value => Array.isArray(value));

            if (possibleCourseArrays.length > 0) {
              // Use the first array found
              setCourses(possibleCourseArrays[0]);
            } else {
              // As a last resort, convert the object to an empty array
              setCourses([]);
              setError('Unable to parse courses data');
            }
          }
        } else {
          setCourses([]);
          setError('Invalid courses data received from API');
        }

        // Handle categories - similar pattern
        if (categoriesResponse) {
          if (Array.isArray(categoriesResponse.results)) {
            setCategories(categoriesResponse.results);
          } else if (Array.isArray(categoriesResponse)) {
            setCategories(categoriesResponse);
          } else {
            const possibleCategoryArrays = Object.values(categoriesResponse)
              .filter(value => Array.isArray(value));

            if (possibleCategoryArrays.length > 0) {
              setCategories(possibleCategoryArrays[0]);
            } else {
              setCategories([]);
            }
          }
        } else {
          setCategories([]);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load courses. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Safely filter courses with defensive coding
  const getFilteredCourses = () => {
    // Guard against courses not being an array
    if (!Array.isArray(courses)) {
      console.error('Courses is not an array:', courses);
      return [];
    }

    return courses
      .filter(course => {
        if (!course) return false;

        // Category filtering with safe handling of different data structures
        const matchesCategory =
          selectedCategory === 'all' ||
          (course.category && (
            // Handle both ID and slug formats
            (course.category.id && course.category.id.toString() === selectedCategory.toString()) ||
            (course.category.slug && course.category.slug === selectedCategory) ||
            (typeof course.category === 'string' && course.category === selectedCategory)
          ));

        // Level filtering with null safety
        const courseLevel = course.level ? course.level.toLowerCase() : '';
        const matchesLevel =
          selectedLevel === 'all' ||
          courseLevel === selectedLevel.toLowerCase();

        // Search with null safety
        const title = course.title || '';
        const description = course.description || course.subtitle || '';
        const matchesSearch =
          searchQuery === '' ||
          title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          description.toLowerCase().includes(searchQuery.toLowerCase());

        return matchesCategory && matchesLevel && matchesSearch;
      })
      .sort((a, b) => {
        // Null-safe sorting
        if (!a || !b) return 0;

        if (sortBy === 'newest') {
          const dateA = new Date(a.updated_at || a.created_at || 0);
          const dateB = new Date(b.updated_at || b.created_at || 0);
          return dateB - dateA;
        } else if (sortBy === 'highest-rated') {
          const ratingA = parseFloat(a.rating || a.avg_rating || 0);
          const ratingB = parseFloat(b.rating || b.avg_rating || 0);
          return ratingB - ratingA;
        } else if (sortBy === 'lowest-price') {
          const priceA = parseFloat(a.price || 0);
          const priceB = parseFloat(b.price || 0);
          return priceA - priceB;
        } else if (sortBy === 'highest-price') {
          const priceA = parseFloat(a.price || 0);
          const priceB = parseFloat(b.price || 0);
          return priceB - priceA;
        } else {
          // Default: most popular (by enrolled count)
          const enrolledA = parseInt(a.enrolled_students || a.enrolled_students_count || 0);
          const enrolledB = parseInt(b.enrolled_students || b.enrolled_students_count || 0);
          return enrolledB - enrolledA;
        }
      });
  };

  const filteredCourses = getFilteredCourses();

  // Pagination logic
  const indexOfLastCourse = currentPage * coursesPerPage;
  const indexOfFirstCourse = indexOfLastCourse - coursesPerPage;
  const currentCourses = filteredCourses.slice(
    indexOfFirstCourse,
    indexOfLastCourse
  );
  const totalPages = Math.ceil(filteredCourses.length / coursesPerPage);

  const handleCategoryChange = e => {
    setSelectedCategory(e.target.value);
    setCurrentPage(1);
  };

  const handleLevelChange = e => {
    setSelectedLevel(e.target.value);
    setCurrentPage(1);
  };

  const handleSortChange = e => {
    setSortBy(e.target.value);
    setCurrentPage(1);
  };

  const handleSearchChange = e => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleSearchSubmit = e => {
    e.preventDefault();
    // You could add additional logic here if needed
  };

  const paginate = pageNumber => setCurrentPage(pageNumber);

  // Helper function to safely get image URL or fallback
  const getImageUrl = (course) => {
    if (!course) return '/images/course-placeholder.jpg';

    if (typeof course.thumbnail === 'string' && course.thumbnail) {
      return course.thumbnail;
    } else if (course.thumbnail?.url) {
      return course.thumbnail.url;
    } else if (course.image) {
      return course.image;
    }

    return '/images/course-placeholder.jpg';
  };

  // Helper function to safely get instructor name
  const getInstructorName = (course) => {
    if (!course) return 'Unknown Instructor';

    if (course.instructor) {
      return course.instructor;
    } else if (course.instructor_name) {
      return course.instructor_name;
    } else if (course.instructors && course.instructors.length > 0) {
      const instructor = course.instructors[0];
      if (instructor.instructor) {
        const firstName = instructor.instructor.first_name || '';
        const lastName = instructor.instructor.last_name || '';
        if (firstName || lastName) return `${firstName} ${lastName}`.trim();
        return instructor.instructor.username || 'Unknown Instructor';
      }
      return instructor.name || 'Unknown Instructor';
    }

    return 'Unknown Instructor';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-lg text-gray-600">Loading courses...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
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
      {/* Header */}
      <div className="bg-primary-700 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-extrabold text-white sm:text-4xl">
                Courses
              </h1>
              <p className="mt-2 text-lg text-primary-200">
                Expand your knowledge with our range of courses taught by
                industry experts
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-sm rounded-lg p-6">
          <form onSubmit={handleSearchSubmit}>
            <div className="grid gap-6 md:grid-cols-4">
              <div className="col-span-4 md:col-span-2">
                <label
                  htmlFor="search"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Search Courses
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="search"
                    name="search"
                    placeholder="Search by title or description..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md"
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

              <div>
                <label
                  htmlFor="category"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Category
                </label>
                <select
                  id="category"
                  name="category"
                  value={selectedCategory}
                  onChange={handleCategoryChange}
                  className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option
                      key={category.id || category.slug}
                      value={category.slug || category.id}
                    >
                      {category.name} (
                      {category.count || category.courses_count || 0})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="level"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Level
                </label>
                <select
                  id="level"
                  name="level"
                  value={selectedLevel}
                  onChange={handleLevelChange}
                  className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="col-span-4 md:col-span-2">
                <label
                  htmlFor="sort"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Sort By
                </label>
                <select
                  id="sort"
                  name="sort"
                  value={sortBy}
                  onChange={handleSortChange}
                  className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md"
                >
                  <option value="popular">Most Popular</option>
                  <option value="newest">Newest</option>
                  <option value="highest-rated">Highest Rated</option>
                  <option value="lowest-price">Lowest Price</option>
                  <option value="highest-price">Highest Price</option>
                </select>
              </div>

              <div className="col-span-4 md:col-span-2 flex items-end">
                <span className="text-sm text-gray-600">
                  Showing{' '}
                  <span className="font-medium">{filteredCourses.length}</span>{' '}
                  result{filteredCourses.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Course List */}
      <div className="max-w-7xl mx-auto pb-12 px-4 sm:px-6 lg:px-8">
        {currentCourses.length === 0 ? (
          <div className="bg-white shadow-sm rounded-lg p-12 text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">
              No courses found
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or search term.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {currentCourses.map(course => (
                <div
                  key={course.id || course.slug}
                  className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 transition-all hover:shadow-md"
                >
                  <div className="relative">
                    <img
                      className="h-48 w-full object-cover"
                      src={getImageUrl(course)}
                      alt={course.title}
                    />
                    <div className="absolute top-2 right-2 flex flex-col space-y-1">
                      {course.is_free || parseFloat(course.price) === 0 ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-green-100 text-green-800">
                          Free
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                          $
                          {typeof course.price === 'number'
                            ? course.price.toFixed(2)
                            : parseFloat(course.price).toFixed(2) || 'Paid'}
                        </span>
                      )}
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                        {course.level || 'All Levels'}
                      </span>
                    </div>
                  </div>

                  <div className="p-6">
                    <div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                        {course.category?.name || 'Uncategorized'}
                      </span>
                      <h3 className="mt-2 text-lg font-medium text-gray-900">
                        {/* Use slug for URL for better SEO and UX */}
                        <Link
                          to={`/courses/${course.slug}`}
                          className="hover:text-primary-600"
                        >
                          {course.title}
                        </Link>
                      </h3>
                      <p className="mt-1 text-sm text-gray-500">
                        By {getInstructorName(course)}
                      </p>
                      <p className="mt-3 text-sm text-gray-600 line-clamp-3">
                        {course.description ||
                          course.subtitle ||
                          'No description available.'}
                      </p>
                    </div>

                    <div className="mt-6 flex items-center">
                      <div className="flex items-center">
                        {[0, 1, 2, 3, 4].map(rating => (
                          <svg
                            key={rating}
                            className={`h-4 w-4 ${rating < Math.floor(course.rating || course.avg_rating || 0) ? 'text-yellow-400' : 'text-gray-300'}`}
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <p className="ml-2 text-xs text-gray-600">
                        {course.rating || course.avg_rating || 0} (
                        {course.enrolled_count ||
                          course.enrolled_students ||
                          course.enrolled_students_count || 0}{' '}
                        students)
                      </p>
                    </div>

                    <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center">
                        <svg
                          className="h-4 w-4 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        {course.duration_display ||
                          course.duration ||
                          'Self-paced'}
                      </div>
                      <div className="flex items-center">
                        <svg
                          className="h-4 w-4 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        Last updated:{' '}
                        {new Date(
                          course.updated_at || course.created_at || new Date()
                        ).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="mt-6">
                      <Link
                        to={`/courses/${course.slug}`}
                        className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-8 rounded-lg">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() =>
                      paginate(currentPage > 1 ? currentPage - 1 : 1)
                    }
                    disabled={currentPage === 1}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                  >
                    Previous
                  </button>
                  <button
                    onClick={() =>
                      paginate(
                        currentPage < totalPages ? currentPage + 1 : totalPages
                      )
                    }
                    disabled={currentPage === totalPages}
                    className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing{' '}
                      <span className="font-medium">
                        {indexOfFirstCourse + 1}
                      </span>{' '}
                      to{' '}
                      <span className="font-medium">
                        {Math.min(indexOfLastCourse, filteredCourses.length)}
                      </span>{' '}
                      of{' '}
                      <span className="font-medium">
                        {filteredCourses.length}
                      </span>{' '}
                      results
                    </p>
                  </div>
                  <div>
                    <nav
                      className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                      aria-label="Pagination"
                    >
                      <button
                        onClick={() =>
                          paginate(currentPage > 1 ? currentPage - 1 : 1)
                        }
                        disabled={currentPage === 1}
                        className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-500 hover:bg-gray-50'}`}
                      >
                        <span className="sr-only">Previous</span>
                        <svg
                          className="h-5 w-5"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>

                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                        number => (
                          <button
                            key={number}
                            onClick={() => paginate(number)}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${currentPage === number
                              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                              }`}
                          >
                            {number}
                          </button>
                        )
                      )}

                      <button
                        onClick={() =>
                          paginate(
                            currentPage < totalPages
                              ? currentPage + 1
                              : totalPages
                          )
                        }
                        disabled={currentPage === totalPages}
                        className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-500 hover:bg-gray-50'}`}
                      >
                        <span className="sr-only">Next</span>
                        <svg
                          className="h-5 w-5"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CoursesListPage;
