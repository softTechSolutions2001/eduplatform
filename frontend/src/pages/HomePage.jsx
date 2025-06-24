/**
 * File: C:\Users\Santhanam\OneDrive\Personal\Full stack web development\eduplatform\frontend\src\pages\HomePage.jsx
 * Purpose: Homepage component for the educational platform
 * Date: 2025-07-24 17:22:43
 *
 * This component:
 * 1. Serves as the landing page for the platform
 * 2. Showcases featured courses and key platform features
 * 3. Provides quick navigation to important sections
 * 4. Includes testimonials and statistics about the platform
 *
 * Fixed Layout Issues:
 * - Removed MainLayout import and wrapper
 * - Layout is now provided by App.jsx
 * - Ensures full-width content by using proper container and width classes
 * - Improved API response handling with fallbacks
 *
 * Variables to modify:
 * - FEATURED_COURSES: Update with your actual featured courses
 * - PLATFORM_FEATURES: Update with your main platform features
 * - TESTIMONIALS: Update with real user testimonials
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-07-24 17:22:43
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
// Removed MainLayout import since it's now handled in App.jsx
import { Button, Card } from '../components/common';
import {
  courseService,
  testimonialService,
  statisticsService,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Sample featured courses (replace with API data)
const FEATURED_COURSES = [
  {
    id: 1,
    title: 'Introduction to Programming',
    instructor: 'John Smith',
    category: 'Computer Science',
    rating: 4.8,
    students: 1200,
    image: '/images/courses/programming-intro.jpg',
  },
  {
    id: 2,
    title: 'Web Development Bootcamp',
    instructor: 'Maria Johnson',
    category: 'Web Development',
    rating: 4.9,
    students: 2500,
    image: '/images/courses/web-dev.jpg',
  },
  {
    id: 3,
    title: 'Data Science Fundamentals',
    instructor: 'Robert Chen',
    category: 'Data Science',
    rating: 4.7,
    students: 1800,
    image: '/images/courses/data-science.jpg',
  },
];

// Platform features
const PLATFORM_FEATURES = [
  {
    title: 'Interactive Learning',
    description:
      'Engage with dynamic content designed to enhance your learning experience',
    icon: (
      <svg
        className="h-8 w-8 text-primary-600"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
        />
      </svg>
    ),
  },
  {
    title: 'Expert Instructors',
    description:
      'Learn from industry professionals with years of practical experience',
    icon: (
      <svg
        className="h-8 w-8 text-primary-600"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
        />
      </svg>
    ),
  },
  {
    title: 'Flexible Learning',
    description: 'Study at your own pace, anywhere, anytime on any device',
    icon: (
      <svg
        className="h-8 w-8 text-primary-600"
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
    ),
  },
];

const HomePage = () => {
  const { isAuthenticated, currentUser } = useAuth();
  const [featuredCourses, setFeaturedCourses] = useState(FEATURED_COURSES);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCourses: 150,
    totalStudents: 12500,
    totalInstructors: 48,
  });
  const [testimonials, setTestimonials] = useState([
    {
      id: 1,
      name: 'Jane Smith',
      role: 'Software Engineer',
      content:
        'This platform helped me transition from a junior to senior developer in just 6 months.',
      rating: 5,
      avatar: '/images/avatars/avatar-1.jpg',
    },
    {
      id: 2,
      name: 'Michael Johnson',
      role: 'Data Scientist',
      content:
        'The data science courses here are comprehensive and practical. I use what I learned daily.',
      rating: 5,
      avatar: '/images/avatars/avatar-2.jpg',
    },
    {
      id: 3,
      name: 'Sarah Williams',
      role: 'UX Designer',
      content:
        'The design courses completely changed how I approach user experience. Highly recommended!',
      rating: 4,
      avatar: '/images/avatars/avatar-3.jpg',
    },
  ]);
  const [testimonialError, setTestimonialError] = useState(null);
  const [featuredCoursesError, setFeaturedCoursesError] = useState(null);

  // Load featured courses and other data from API
  useEffect(() => {
    const loadFeaturedCourses = async () => {
      try {
        const response = await courseService.getFeaturedCourses();

        // Check if we got a valid response with courses
        if (response) {
          // Handle different response formats
          let courses = response;

          // If response is an object with a data property that's an array
          if (!Array.isArray(response) && response.data) {
            courses = response.data;
          }

          // If response is an object with results property that's an array (DRF pagination)
          if (!Array.isArray(response) && response.results) {
            courses = response.results;
          }

          // Only update state if we have course data
          if (Array.isArray(courses) && courses.length > 0) {
            setFeaturedCourses(courses);
          }
        }
      } catch (error) {
        console.error('Error loading featured courses:', error);
        setFeaturedCoursesError(error);
        // Keep using default courses on error
      } finally {
        setLoading(false);
      }
    };

    const loadPlatformStats = async () => {
      try {
        const response = await statisticsService.getPlatformStats();
        if (response) {
          const statsData = response.data || response;
          if (statsData) {
            setStats({
              totalCourses:
                statsData.total_courses ||
                statsData.courses_count ||
                stats.totalCourses,
              totalStudents:
                statsData.total_students ||
                statsData.students_count ||
                stats.totalStudents,
              totalInstructors:
                statsData.total_instructors ||
                statsData.instructors_count ||
                stats.totalInstructors,
            });
          }
        }
      } catch (error) {
        console.error('Error loading platform stats:', error);
        // Keep using default stats on error
      }
    };

    const loadTestimonials = async () => {
      try {
        const response = await testimonialService.getAllTestimonials();
        if (response) {
          // Handle different response formats
          let testimonialData = response;

          if (!Array.isArray(response) && response.data) {
            testimonialData = response.data;
          }

          if (!Array.isArray(response) && response.results) {
            testimonialData = response.results;
          }

          if (Array.isArray(testimonialData) && testimonialData.length > 0) {
            setTestimonials(testimonialData);
          }
        }
      } catch (error) {
        console.error('Error loading testimonials:', error);
        setTestimonialError(error);
        // Keep using default testimonials on error
      }
    };

    // Load featured courses
    loadFeaturedCourses();

    // Try to load stats and testimonials, but don't break if endpoints aren't available yet
    try {
      loadPlatformStats();
    } catch (error) {
      console.error('Statistics API not available yet:', error);
    }

    try {
      loadTestimonials();
    } catch (error) {
      console.error('Testimonials API not available yet:', error);
    }
  }, []);

  return (
    <>
      {' '}
      {/* No MainLayout wrapper here since it's provided in App.jsx */}
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white w-full">
        <div className="container mx-auto px-4 py-20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
                Your Journey to Knowledge and Excellence
              </h1>
              <p className="text-xl mb-8">
                Discover a learning ecosystem where knowledge, innovation, and
                community converge to empower your educational journey.
              </p>
              <div className="flex flex-wrap gap-4">
                {!isAuthenticated && (
                  <>
                    <Link
                      to="/register"
                      className="px-8 py-3 text-lg font-medium text-white bg-primary-600 rounded-full hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 shadow-lg transition-all duration-300 transform hover:-translate-y-1"
                    >
                      Get Started for Free
                    </Link>
                    <Link
                      to="/pricing"
                      className="px-8 py-3 text-lg font-medium text-primary-700 bg-white border-2 border-primary-600 rounded-full hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 shadow-md transition-all duration-300 transform hover:-translate-y-1"
                    >
                      View Plans
                    </Link>
                  </>
                )}
                {isAuthenticated && (
                  <>
                    <Link
                      to="/courses"
                      className="px-8 py-3 text-lg font-medium text-white bg-primary-600 rounded-full hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 shadow-lg transition-all duration-300 transform hover:-translate-y-1"
                    >
                      Explore Courses
                    </Link>
                    <Link
                      to="/dashboard"
                      className="px-8 py-3 text-lg font-medium text-primary-700 bg-white border-2 border-primary-600 rounded-full hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 shadow-md transition-all duration-300 transform hover:-translate-y-1"
                    >
                      My Dashboard
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="hidden md:block">
              <div className="relative">
                <div className="bg-white rounded-lg shadow-xl p-6 w-full h-80">
                  <h3 className="text-center text-xl text-gray-700 mb-4">
                    Interactive Learning Platform
                  </h3>
                  {/* Sample interactive element or screenshot */}
                  <div className="flex items-center justify-center h-48 bg-gray-100 rounded">
                    {/* This is where you would put a preview image or interactive element */}
                    <span className="text-gray-500">Platform Preview</span>
                  </div>
                </div>

                {/* Example of notification bubble */}
                <div className="absolute -top-6 -right-6 bg-amber-500 text-white rounded-full px-4 py-2 shadow-lg flex items-center">
                  <svg
                    className="h-6 w-6 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Certificate Earned!
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Statistics Section */}
      <div className="bg-gray-100 py-12 w-full">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="bg-white p-8 rounded-lg shadow">
              <div className="text-4xl font-bold text-primary-600 mb-2">
                {stats.totalCourses}+
              </div>
              <div className="text-gray-600 text-lg">Courses Available</div>
            </div>
            <div className="bg-white p-8 rounded-lg shadow">
              <div className="text-4xl font-bold text-primary-600 mb-2">
                {stats.totalStudents}+
              </div>
              <div className="text-gray-600 text-lg">Active Learners</div>
            </div>
            <div className="bg-white p-8 rounded-lg shadow">
              <div className="text-4xl font-bold text-primary-600 mb-2">
                {stats.totalInstructors}+
              </div>
              <div className="text-gray-600 text-lg">Expert Instructors</div>
            </div>
          </div>
        </div>
      </div>
      {/* Featured Courses Section */}
      <div className="py-16 w-full">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Courses</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Explore our most popular courses and start your learning journey
              today
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {loading
              ? // Loading placeholders
                Array(3)
                  .fill()
                  .map((_, index) => (
                    <Card key={index} className="animate-pulse">
                      <div className="h-48 bg-gray-200 rounded mb-4"></div>
                      <div className="h-6 bg-gray-200 rounded mb-2 w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded mb-2 w-1/2"></div>
                      <div className="h-4 bg-gray-200 rounded mb-4 w-2/3"></div>
                      <div className="h-8 bg-gray-200 rounded w-full"></div>
                    </Card>
                  ))
              : // Actual courses
                featuredCourses.map(course => (
                  <Card key={course.id} className="overflow-hidden">
                    <div
                      className="h-48 bg-cover bg-center"
                      style={{
                        backgroundImage: `url(${course.image || course.thumbnail || course.cover_image || `/images/course-placeholder.jpg`})`,
                      }}
                    ></div>
                    <div className="p-6">
                      <h3 className="font-semibold text-lg mb-2">
                        {course.title}
                      </h3>
                      <p className="text-gray-600 mb-1">
                        {course.instructor ||
                          course.instructor_name ||
                          course.teacher ||
                          'Expert Instructor'}
                      </p>
                      <div className="flex items-center mb-4">
                        <span className="text-amber-500 flex items-center">
                          <svg
                            className="h-4 w-4"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="ml-1">
                            {course.rating ||
                              course.average_rating ||
                              course.avg_rating ||
                              4.5}
                          </span>
                        </span>
                        <span className="text-gray-500 mx-2">•</span>
                        <span className="text-gray-500">
                          {course.students ||
                            course.enrolled_students ||
                            course.num_students ||
                            course.students_count ||
                            0}{' '}
                          students
                        </span>
                      </div>
                      <Link to={`/courses/${course.slug || course.id}`}>
                        <Button color="primary" fullWidth>
                          View Course
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
          </div>

          <div className="text-center mt-10">
            <Link to="/courses">
              <Button color="secondary" size="large">
                View All Courses
              </Button>
            </Link>
          </div>
        </div>
      </div>
      {/* Features Section */}
      <div className="bg-gray-50 py-16 w-full">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose Our Platform</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              We provide a comprehensive learning experience designed to help
              you succeed
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {PLATFORM_FEATURES.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-lg shadow-md">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* CTA Section */}
      <div className="bg-primary-700 text-white py-16 w-full">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Learning?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of students who are already transforming their
            careers with our courses
          </p>
          {!isAuthenticated ? (
            <div className="mt-8 flex justify-center">
              <Link
                to="/register"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Sign Up Now
              </Link>
            </div>
          ) : (
            <div className="mt-8 flex justify-center">
              <Link
                to="/courses"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Browse Courses
              </Link>
            </div>
          )}
        </div>
      </div>
      {/* Testimonials Section */}
      <div className="py-16 bg-gray-50 w-full">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Our Students Say</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Hear from our community of learners about their experience with
              our platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map(testimonial => (
              <div
                key={testimonial.id}
                className="bg-white p-6 rounded-lg shadow-md"
              >
                <div className="flex items-center mb-4">
                  <div className="h-12 w-12 rounded-full overflow-hidden bg-gray-200 mr-4">
                    {testimonial.avatar ? (
                      <img
                        src={testimonial.avatar}
                        alt={testimonial.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center bg-primary-100 text-primary-600">
                        {testimonial.name.charAt(0)}
                      </div>
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold">{testimonial.name}</h3>
                    <p className="text-gray-600 text-sm">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-700 mb-3">{testimonial.content}</p>
                <div className="flex text-amber-500">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`h-5 w-5 ${i < testimonial.rating ? 'text-amber-500' : 'text-gray-300'}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default HomePage;
