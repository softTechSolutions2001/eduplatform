/**
 * File: frontend/src/pages/courses/CourseLandingPage.jsx
 * Version: 3.2.0
 * Date: 2025-05-12 15:21:00
 * Author: cadsanthanam
 *
 * Course Landing Page component with enhanced course display and improved navigation
 *
 * This component:
 * 1. Displays detailed course information for prospective students
 * 2. Shows a structured curriculum with access level indicators
 * 3. Provides enrollment functionality for students
 * 4. Offers management options for instructors
 * 5. Integrates with CourseContentRouteChecker for access control
 *
 * Key features:
 * - Dual interfaces for students and instructors
 * - Visual indicators for content access levels (guest/registered/premium)
 * - Streamlined navigation to course content
 * - Responsive design with improved sidebar
 */

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  AnimatedElement,
  Badge,
  Button,
  Card,
  ErrorBoundary,
  Rating,
} from '../../components/common';
import { Header } from '../../components/layouts';
import { useAuth } from '../../contexts/AuthContext';
import { courseService } from '../../services/api';
import instructorService from '../../services/instructorService';

const CourseLandingPage = () => {
  const { courseSlug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, userRole } = useAuth();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [course, setCourse] = useState(null);
  const [enrolled, setEnrolled] = useState(false);
  const [isInstructorView, setIsInstructorView] = useState(false);

  // Determine if user is instructor or admin
  useEffect(() => {
    if (userRole === 'instructor' || userRole === 'administrator') {
      setIsInstructorView(true);
    }
  }, [userRole]);

  // Fetch course data
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true);
        console.log('Fetching course with slug:', courseSlug);

        let courseData = null;

        // For instructors or admins, use instructorService
        if (isInstructorView) {
          console.log('Using instructor service to fetch course');
          try {
            const instructorResponse =
              await instructorService.getCourseBySlug(courseSlug);
            // Check if we have data in the response or in response.data
            courseData = instructorResponse.data || instructorResponse;
            console.log(
              'Course fetched successfully via instructor service:',
              courseData
            );
          } catch (instructorError) {
            console.error(
              'Error fetching with instructorService:',
              instructorError
            );
            // Fall back to regular course service
            const regularResponse =
              await courseService.getCourseBySlug(courseSlug);
            courseData = regularResponse.data || regularResponse;
          }
        } else {
          // For regular users and students
          console.log('Using regular course service');
          const response = await courseService.getCourseBySlug(courseSlug);
          courseData = response.data || response;
        }

        if (!courseData) {
          setError('Course not found.');
          setCourse(null);
          setLoading(false);
          return;
        }

        // Ensure courseData has all expected properties to prevent rendering errors
        courseData = {
          title: 'Untitled Course',
          description: '',
          modules: [],
          instructors: [],
          skills: [],
          requirements: [],
          enrolled_students: 0,
          ...courseData,
        };

        console.log('Setting course data:', courseData);

        // Check for critical missing properties that might cause render errors
        if (!courseData.title) {
          console.warn('Course missing title:', courseData);
        }

        if (!courseData.instructors || !Array.isArray(courseData.instructors)) {
          console.warn('Course missing instructors array:', courseData);
          // Provide a default empty array to prevent rendering errors
          courseData.instructors = [];
        }

        // Ensure skills and requirements are arrays
        if (!Array.isArray(courseData.skills)) {
          courseData.skills = [];
        }

        if (!Array.isArray(courseData.requirements)) {
          courseData.requirements = [];
        }

        // Log the structure of the first instructor to help debug
        if (courseData.instructors && courseData.instructors.length > 0) {
          console.log('First instructor structure:', courseData.instructors[0]);
        }

        setCourse(courseData);
        setEnrolled(courseData.isEnrolled || courseData.is_enrolled || false);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load course data:', err);
        setError('Failed to load course information. Please try again later.');
        setLoading(false);
      }
    };

    fetchCourse();
  }, [courseSlug, isInstructorView]);

  // Toggle course publish status
  const handlePublishToggle = async () => {
    try {
      const identifier = course.slug || course.id;
      const newPublishState = !course.is_published;

      await instructorService.publishCourse(identifier, newPublishState);

      // Update local state with new publish status
      setCourse({
        ...course,
        is_published: newPublishState,
      });

      // Show success message
      alert(
        `Course ${newPublishState ? 'published' : 'unpublished'} successfully`
      );
    } catch (err) {
      console.error('Failed to toggle publish status:', err);
      alert(
        `Failed to ${course.is_published ? 'unpublish' : 'publish'} course. Please ensure all required fields are filled.`
      );
    }
  };

  // Helper function to redirect to login with current page as return URL
  const redirectToLogin = () => {
    navigate('/login', { state: { from: `/courses/${courseSlug}` } });
  };

  const handleEnroll = async () => {
    if (!isAuthenticated) {
      redirectToLogin();
      return;
    }

    try {
      await courseService.enrollInCourse(courseSlug);
      setEnrolled(true);
      // Show success message
      alert('Successfully enrolled in the course!');
    } catch (err) {
      console.error('Failed to enroll:', err);
      setError('Failed to enroll in the course. Please try again.');
    }
  };

  const handleStartLearning = () => {
    if (!course?.modules?.length) {
      console.warn('No modules available to start learning');
      return;
    }

    const firstModule = course.modules[0];
    const firstLesson = firstModule.lessons?.[0];

    if (firstLesson) {
      navigate(
        `/courses/${courseSlug}/content/${firstModule.id}/${firstLesson.id}`
      );
    } else if (firstModule.id) {
      navigate(`/courses/${courseSlug}/content/${firstModule.id}/1`);
    } else {
      console.warn('No valid lessons found to navigate to');
    }
  };

  // Add this new function to handle module clicks
  const handleModuleClick = moduleId => {
    if (!moduleId) {
      console.warn('No valid module ID to navigate to');
      return;
    }

    navigate(`/courses/${courseSlug}/modules/${moduleId}`);
  };

  // Simplified lesson click handler that delegates access control to CourseContentRouteChecker
  const handleLessonClick = (moduleId, lessonId) => {
    if (!moduleId || !lessonId) {
      console.warn('Invalid module or lesson ID');
      return;
    }

    // Simply navigate - CourseContentRouteChecker will handle access control
    navigate(`/courses/${courseSlug}/content/${moduleId}/${lessonId}`);
  };
  // Helper function to get access level icon
  const getAccessLevelIcon = accessLevel => {
    switch (accessLevel || 'guest') {
      case 'premium':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-3.5 h-3.5 text-amber-500"
            aria-label="Premium content"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        );
      case 'registered':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-3.5 h-3.5 text-blue-500"
            aria-label="Registered users"
          >
            <path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
            <path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
          </svg>
        );
      default: // guest
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-3.5 h-3.5 text-green-500"
            aria-label="Free content"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  // Debug lesson access levels
  useEffect(() => {
    if (course && course.modules) {
      console.log('=== LESSON ACCESS LEVELS DEBUG ===');
      course.modules.forEach(module => {
        if (module.lessons && module.lessons.length) {
          module.lessons.forEach(lesson => {
            // Log all possible property paths for access level
            console.log(`Lesson ${lesson.id}: ${lesson.title}`);
            console.log(`  - accessLevel: ${lesson.accessLevel}`);
            console.log(`  - access_level: ${lesson.access_level}`);
            console.log(
              `  - metadata?.accessLevel: ${lesson.metadata?.accessLevel}`
            );
            console.log(
              `  - metadata?.access_level: ${lesson.metadata?.access_level}`
            );
            console.log(`  - Raw lesson object:`, lesson);
          });
        }
      });
      console.log('=================================');
    }
  }, [course]);

  // Render different views for instructors vs students
  if (!loading && !error && course) {
    if (isInstructorView) {
      return (
        <div className="flex flex-col min-h-screen bg-gray-50">
          <Header />
          <div className="container mx-auto py-6 px-4">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold">{course.title}</h1>
              <div className="space-x-2">
                <Button
                  color="secondary"
                  onClick={() =>
                    navigate(`/instructor/courses/${course.id}/edit`)
                  }
                >
                  Edit Course
                </Button>
                <Button
                  color={course.is_published ? 'warning' : 'success'}
                  onClick={() => navigate(`/courses/${course.slug}`)}
                >
                  {course.is_published ? 'Manage Course' : 'Continue Setup'}
                </Button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div className="flex items-center mb-4">
                <span
                  className={`inline-block w-3 h-3 rounded-full mr-2 ${course.is_published ? 'bg-green-500' : 'bg-yellow-500'}`}
                ></span>
                <span className="font-medium">
                  {course.is_published ? 'Published' : 'Draft'}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Category
                  </h3>
                  <p>{course.category?.name || 'Uncategorized'}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Level
                  </h3>
                  <p className="capitalize">{course.level}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Price
                  </h3>
                  <p>${course.price}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Students Enrolled
                  </h3>
                  <p>{course.enrolled_students || 0}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Rating
                  </h3>
                  <div className="flex items-center">
                    <Rating value={course.rating || 0} readOnly size="small" />
                    <span className="ml-2">({course.rating || 0})</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">
                    Last Updated
                  </h3>
                  <p>{new Date(course.updated_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                  <h2 className="text-xl font-bold mb-4">Course Content</h2>
                  <div className="space-y-4">
                    {course.modules && course.modules.length > 0 ? (
                      course.modules.map((module, index) => (
                        <div
                          key={module.id}
                          className="border rounded-lg overflow-hidden"
                        >
                          <div
                            className="bg-gray-50 p-4 flex justify-between items-center cursor-pointer hover:bg-gray-100"
                            onClick={() => handleModuleClick(module.id)}
                          >
                            <h3 className="font-medium">
                              Module {index + 1}: {module.title}
                            </h3>
                            <div className="text-sm text-gray-500">
                              {module.lessons?.length || 0} lessons
                            </div>
                          </div>
                          <div className="p-4">
                            <p className="text-gray-600">
                              {module.description}
                            </p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-500">No modules created yet.</p>
                        <Button
                          color="primary"
                          className="mt-4"
                          onClick={() =>
                            navigate(`/courses/${course.slug}/modules/create`)
                          }
                        >
                          Create First Module
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div>
                <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                  <h2 className="text-xl font-bold mb-4">Course Completion</h2>

                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">
                      Content Completion
                    </h3>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{
                          width: `${calculateCompletionPercentage(course)}%`,
                        }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {calculateCompletionPercentage(course)}% complete
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div
                      className={`flex items-center ${course.modules?.length ? 'text-green-600' : 'text-gray-400'}`}
                    >
                      <i
                        className={`fas fa-${course.modules?.length ? 'check-circle' : 'circle'} mr-2`}
                      ></i>
                      <span>Add modules ({course.modules?.length || 0})</span>
                    </div>
                    <div
                      className={`flex items-center ${hasLessons(course) ? 'text-green-600' : 'text-gray-400'}`}
                    >
                      <i
                        className={`fas fa-${hasLessons(course) ? 'check-circle' : 'circle'} mr-2`}
                      ></i>
                      <span>Add lessons</span>
                    </div>
                    <div
                      className={`flex items-center ${course.thumbnail ? 'text-green-600' : 'text-gray-400'}`}
                    >
                      <i
                        className={`fas fa-${course.thumbnail ? 'check-circle' : 'circle'} mr-2`}
                      ></i>
                      <span>Upload thumbnail</span>
                    </div>
                    <div
                      className={`flex items-center ${course.price ? 'text-green-600' : 'text-gray-400'}`}
                    >
                      <i
                        className={`fas fa-${course.price ? 'check-circle' : 'circle'} mr-2`}
                      ></i>
                      <span>Set pricing</span>
                    </div>
                  </div>

                  <div className="mt-6">
                    <Button
                      color={course.is_published ? 'warning' : 'success'}
                      className="w-full"
                      onClick={() => handlePublishToggle()}
                    >
                      {course.is_published
                        ? 'Unpublish Course'
                        : 'Publish Course'}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Student view - with updated sidebar and visual indicators
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        {/* Hero Section - Full width with contained content */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-16 w-full">
          <div className="w-full px-4 md:px-8">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="md:w-3/5 mb-8 md:mb-0">
                <h1 className="text-3xl md:text-4xl font-bold mb-4 font-display">
                  {course?.title}
                </h1>
                <p className="text-lg md:text-xl mb-6 text-blue-100">
                  {course?.subtitle}
                </p>
                <div className="flex items-center mb-6">
                  <Rating value={course?.rating || 0} />
                  <span className="ml-2 text-blue-100">
                    ({course?.rating || 0}) • {course?.enrolled_students || 0}{' '}
                    students
                  </span>
                </div>
                <div className="space-y-2 mb-6">
                  <div className="flex items-center">
                    <i className="fas fa-user-graduate mr-3 text-blue-300"></i>
                    <span>
                      Created by{' '}
                      {course?.instructors
                        ?.map(
                          i =>
                            i.instructor.first_name +
                            ' ' +
                            i.instructor.last_name
                        )
                        .join(', ')}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <i className="fas fa-clock mr-3 text-blue-300"></i>
                    <span>
                      {course?.duration_display || 'Duration not specified'}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <i className="fas fa-signal mr-3 text-blue-300"></i>
                    <span>{course?.level}</span>
                  </div>
                  {course?.has_certificate && (
                    <div className="flex items-center">
                      <i className="fas fa-certificate mr-3 text-blue-300"></i>
                      <span>Certificate of completion</span>
                    </div>
                  )}
                </div>
                <div>
                  {enrolled ? (
                    <Button
                      color="secondary"
                      size="large"
                      onClick={handleStartLearning}
                    >
                      Continue Learning
                    </Button>
                  ) : (
                    <Button
                      color="secondary"
                      size="large"
                      onClick={handleEnroll}
                    >
                      Enroll Now
                    </Button>
                  )}
                </div>
              </div>
              <div className="md:w-2/5">
                <Card className="overflow-hidden">
                  <div className="aspect-w-16 aspect-h-9 bg-gray-300">
                    {course?.thumbnail ? (
                      <img
                        src={course.thumbnail}
                        alt={course.title}
                        className="object-cover w-full h-full"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500">
                        <span>Course Preview</span>
                      </div>
                    )}
                  </div>
                  <div className="p-6">
                    <div className="flex justify-between items-center mb-4">
                      <div>
                        <span className="text-2xl font-bold">
                          ${course?.discount_price || course?.price}
                        </span>
                        {course?.discount_price && (
                          <span className="text-gray-400 line-through ml-2">
                            ${course?.price}
                          </span>
                        )}
                      </div>
                      {course?.discount_price && (
                        <Badge variant="secondary">
                          {Math.round(
                            (1 - course.discount_price / course.price) * 100
                          )}
                          % OFF
                        </Badge>
                      )}
                    </div>
                    <div className="space-y-4">
                      <p className="flex items-center text-sm">
                        <i className="fas fa-infinity mr-3 text-gray-600"></i>
                        <span>Full lifetime access</span>
                      </p>
                      <p className="flex items-center text-sm">
                        <i className="fas fa-mobile-alt mr-3 text-gray-600"></i>
                        <span>Access on mobile and desktop</span>
                      </p>
                      {course?.has_certificate && (
                        <p className="flex items-center text-sm">
                          <i className="fas fa-certificate mr-3 text-gray-600"></i>
                          <span>Certificate of completion</span>
                        </p>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content with Sidebar - Full width with contained content */}
        <div className="w-full py-12">
          <div className="w-full px-4 md:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Sidebar with course structure - REDUCED WIDTH */}
              <aside className="md:col-span-1">
                <AnimatedElement type="fade-in" delay={100}>
                  <section className="mb-8">
                    <h3 className="text-xl font-bold mb-4 font-display">
                      Course Curriculum
                    </h3>
                    {/* Reduced width sidebar */}
                    <div className="bg-white p-4 rounded-xl shadow-sm max-w-xs">
                      {course?.modules?.length > 0 ? (
                        <ul className="space-y-2">
                          {course.modules.map((module, mIdx) => {
                            const moduleAccessLevel =
                              module.accessLevel ||
                              module.access_level ||
                              'basic';

                            return (
                              <li key={module.id}>
                                <details open={mIdx === 0} className="mb-2">
                                  <summary className="cursor-pointer font-medium text-primary-700 flex items-center justify-between p-2 rounded hover:bg-gray-50">
                                    <div className="flex items-center">
                                      {/* Module access level icon */}
                                      {getAccessLevelIcon(moduleAccessLevel)}
                                      <span className="ml-2 flex-1">
                                        {module.title}
                                      </span>
                                    </div>
                                  </summary>

                                  <ul className="mt-2 space-y-1 border-l-2 border-gray-100 pl-3 ml-2">
                                    {module.lessons &&
                                      module.lessons.map((lesson, lIdx) => {
                                        // Enhanced access level determination - check all possible property paths
                                        // console.log("Lesson data:", lesson);

                                        // Try multiple property paths for access level, camelCase takes precedence
                                        const lessonAccessLevel =
                                          lesson.accessLevel ||
                                          lesson.access_level ||
                                          (lesson.metadata &&
                                            (lesson.metadata.accessLevel ||
                                              lesson.metadata.access_level)) ||
                                          moduleAccessLevel ||
                                          'basic';

                                        // Log access level for debugging
                                        console.debug(
                                          `Rendering lesson ${lesson.id}: ${lesson.title} - Access Level: ${lessonAccessLevel}`
                                        );

                                        return (
                                          <li key={lesson.id}>
                                            <button
                                              className="w-full text-left px-2 py-1.5 rounded hover:bg-primary-50 flex items-center group"
                                              onClick={() =>
                                                handleLessonClick(
                                                  module.id,
                                                  lesson.id
                                                )
                                              }
                                            >
                                              {/* Lesson access level bullet indicator */}
                                              {getAccessLevelIcon(
                                                lessonAccessLevel
                                              )}
                                              <span className="ml-2 flex-1 text-sm truncate">
                                                {lesson.title}
                                              </span>
                                            </button>
                                          </li>
                                        );
                                      })}
                                  </ul>
                                </details>
                              </li>
                            );
                          })}
                        </ul>
                      ) : (
                        <div className="text-gray-500 text-center py-8">
                          No modules available yet.
                        </div>
                      )}
                    </div>

                    {/* Access level legend */}
                    <div className="mt-4 bg-gray-50 p-3 rounded-lg max-w-xs">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Content Access Levels:
                      </p>
                      <div className="space-y-2 text-sm">
                        {' '}
                        <div className="flex items-center">
                          {getAccessLevelIcon('guest')}
                          <span className="ml-2 text-gray-600">
                            Free Content
                          </span>
                        </div>
                        <div className="flex items-center">
                          {getAccessLevelIcon('registered')}
                          <span className="ml-2 text-gray-600">
                            Requires Registration
                          </span>
                        </div>
                        <div className="flex items-center">
                          {getAccessLevelIcon('premium')}
                          <span className="ml-2 text-gray-600">
                            Premium Content
                          </span>
                        </div>
                      </div>
                    </div>
                  </section>
                </AnimatedElement>

                {/* Instructor Card */}
                <AnimatedElement type="fade-in" delay={200}>
                  <section className="mb-8">
                    <h3 className="text-xl font-bold mb-4 font-display">
                      Instructor
                    </h3>
                    <div className="bg-white p-6 rounded-xl shadow-sm max-w-xs">
                      {course?.instructors?.map(instructor => (
                        <div
                          key={instructor?.instructor?.id || Math.random()}
                          className="mb-4 last:mb-0"
                        >
                          <div className="flex items-center mb-3">
                            <div className="w-12 h-12 rounded-full bg-gray-200 mr-4 flex items-center justify-center text-gray-500 overflow-hidden">
                              {instructor?.instructor?.first_name?.[0] || '?'}
                              {instructor?.instructor?.last_name?.[0] || '?'}
                            </div>
                            <div>
                              <h4 className="font-medium">
                                {instructor?.instructor?.first_name ||
                                  'Unknown'}{' '}
                                {instructor?.instructor?.last_name ||
                                  'Instructor'}
                              </h4>
                              <p className="text-sm text-gray-500">
                                {instructor?.title || 'Instructor'}
                              </p>
                            </div>
                          </div>
                          {instructor?.bio && (
                            <p className="text-gray-600 text-sm">
                              {instructor?.bio}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                </AnimatedElement>

                {/* Take Action Card */}
                <AnimatedElement type="fade-in" delay={300}>
                  <section>
                    <div className="sticky top-6 bg-white p-6 rounded-xl shadow-sm border-t-4 border-primary-500 max-w-xs">
                      <h3 className="text-xl font-bold mb-4 font-display">
                        Ready to Start Learning?
                      </h3>
                      <p className="text-gray-600 mb-6">
                        Join {course?.enrolled_students || 0} students who are
                        already taking this course.
                      </p>
                      {enrolled ? (
                        <Button
                          color="primary"
                          size="large"
                          className="w-full"
                          onClick={handleStartLearning}
                        >
                          Continue Learning
                        </Button>
                      ) : (
                        <Button
                          color="primary"
                          size="large"
                          className="w-full"
                          onClick={handleEnroll}
                        >
                          Enroll Now
                        </Button>
                      )}
                    </div>
                  </section>
                </AnimatedElement>
              </aside>

              {/* Main Content Area */}
              <main className="md:col-span-2">
                {/* About This Course */}
                <AnimatedElement type="fade-in">
                  <section className="mb-12">
                    <h2 className="text-2xl font-bold mb-6 font-display">
                      About This Course
                    </h2>
                    <div
                      className="prose prose-blue max-w-none"
                      dangerouslySetInnerHTML={{ __html: course?.description }}
                    />
                  </section>
                </AnimatedElement>
                {/* What You'll Learn */}
                {course?.skills?.length > 0 && (
                  <AnimatedElement type="fade-in" delay={100}>
                    <section className="mb-12">
                      <h2 className="text-2xl font-bold mb-6 font-display">
                        What You'll Learn
                      </h2>
                      <div className="bg-white p-6 rounded-xl shadow-sm">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {course.skills.map((skill, index) => (
                            <div key={index} className="flex items-start">
                              <i className="fas fa-check text-green-500 mt-1 mr-3"></i>
                              <span>{skill}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </section>
                  </AnimatedElement>
                )}
                {/* Requirements */}
                {course?.requirements?.length > 0 && (
                  <AnimatedElement type="fade-in" delay={200}>
                    <section className="mb-12">
                      <h2 className="text-2xl font-bold mb-6 font-display">
                        Requirements
                      </h2>
                      <div className="bg-white p-6 rounded-xl shadow-sm">
                        <ul className="space-y-2">
                          {course.requirements.map((req, index) => (
                            <li key={index} className="flex items-start">
                              <i className="fas fa-circle text-xs text-primary-500 mt-1.5 mr-3"></i>
                              <span>{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </section>
                  </AnimatedElement>
                )}
              </main>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Loading and error states
  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <div className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto mb-4"></div>
            <p className="text-primary-700 font-medium">
              Loading course information...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <div className="flex-grow flex items-center justify-center">
          <div className="text-center max-w-md mx-auto">
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
              <p className="text-red-700">{error}</p>
            </div>
            <Button color="primary" onClick={() => navigate('/courses')}>
              Back to Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return <div>No course data available.</div>;
};

// Helper functions for instructor view
function calculateCompletionPercentage(course) {
  let total = 0;
  let completed = 0;

  // Check if modules exist
  if (course.modules?.length) {
    total++;
    completed++;
  }

  // Check if lessons exist
  if (hasLessons(course)) {
    total++;
    completed++;
  }

  // Check thumbnail
  total++;
  if (course.thumbnail) completed++;

  // Check pricing
  total++;
  if (course.price) completed++;

  return total > 0 ? Math.round((completed / total) * 100) : 0;
}

function hasLessons(course) {
  if (!course.modules) return false;

  for (const module of course.modules) {
    if (module.lessons?.length) {
      return true;
    }
  }

  return false;
}

export default function CourseLandingPageWithErrorBoundary() {
  const navigate = useNavigate();

  const handleError = (error, errorInfo) => {
    console.error('Course Landing Page Error:', error, errorInfo);
  };

  const handleNavigateHome = () => {
    navigate('/courses');
  };

  return (
    <ErrorBoundary onError={handleError}>
      <CourseLandingPage />
    </ErrorBoundary>
  );
}
