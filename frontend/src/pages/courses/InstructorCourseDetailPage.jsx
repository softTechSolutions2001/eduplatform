/**
 * File: frontend/src/pages/courses/InstructorCourseDetailPage.jsx
 * Purpose: Instructor-specific course detail page for managing modules and lessons
 *
 * This component:
 * 1. Shows course details for instructors
 * 2. Lists all modules in the course
 * 3. Provides module management functionality
 * 4. Allows navigation to lesson creation
 * 5. Includes course settings management
 *
 * Access Level: Instructors only
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-05-04, 16:33:37
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Alert, Button, Card, Container, Tabs } from '../../components/common';
import { InstructorErrorBoundary } from '../../components/common/errorBoundaries';
import { useAuth } from '../../contexts/AuthContext';
import instructorService from '../../services/instructorService';
import CourseLandingPage from './CourseLandingPage';

const InstructorCourseDetailPage = () => {
  const { courseIdentifier } = useParams();
  const courseSlug = courseIdentifier; // For backward compatibility
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [activeTab, setActiveTab] = useState('modules');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is an instructor
  useEffect(() => {
    if (
      currentUser &&
      currentUser.role !== 'instructor' &&
      currentUser.role !== 'administrator' &&
      currentUser.role !== 'admin'
    ) {
      navigate('/forbidden');
    }
  }, [currentUser, navigate]); // Fetch course and modules
  useEffect(() => {
    const abortController = new AbortController();
    const signal = abortController.signal;

    const fetchCourseData = async () => {
      try {
        setLoading(true);
        console.log('Fetching course with identifier:', courseIdentifier);

        let courseResponse;
        let fetchByIdFirst = !isNaN(courseIdentifier);
        let firstMethodFailed = false;

        // Log the strategy we're using
        console.log(
          `Using fetch strategy: ${fetchByIdFirst ? 'ID first, then slug' : 'slug first, then ID'}`
        );

        // First attempt
        try {
          if (fetchByIdFirst) {
            console.log('Attempting to fetch by ID:', courseIdentifier);
            courseResponse = await instructorService.getCourse(
              courseIdentifier,
              { signal }
            );
          } else {
            console.log('Attempting to fetch by slug:', courseIdentifier);
            courseResponse = await instructorService.getCourseBySlug(
              courseIdentifier,
              { signal }
            );
          }
        } catch (initialError) {
          // Ignore if aborted
          if (signal.aborted) throw initialError;

          console.warn(
            'Initial fetch attempt failed:',
            initialError.message || initialError
          );
          firstMethodFailed = true;

          // Second attempt with the alternate method
          try {
            if (fetchByIdFirst) {
              console.log(
                'First attempt failed. Trying as slug:',
                courseIdentifier
              );
              courseResponse = await instructorService.getCourseBySlug(
                courseIdentifier,
                { signal }
              );
            } else {
              console.log(
                'First attempt failed. Trying as ID:',
                courseIdentifier
              );
              courseResponse = await instructorService.getCourse(
                courseIdentifier,
                { signal }
              );
            }
          } catch (fallbackError) {
            // Ignore if aborted
            if (signal.aborted) throw fallbackError;

            console.error('Both fetch attempts failed:', {
              initialError: initialError.message || initialError,
              fallbackError: fallbackError.message || fallbackError,
            });

            // Final attempt: try a generic course list and filter
            try {
              console.log(
                'Attempting last-resort fetch by filtering course list'
              );
              const allCourses = await instructorService.getCourses({ signal });

              // Try to find by exact match first (case insensitive)
              let matchingCourse = allCourses.find(
                c =>
                  (c.slug &&
                    c.slug.toLowerCase() === courseIdentifier.toLowerCase()) ||
                  (c.id && String(c.id) === String(courseIdentifier))
              );

              // If no exact match, try partial match
              if (!matchingCourse) {
                matchingCourse = allCourses.find(
                  c =>
                    (c.slug &&
                      c.slug
                        .toLowerCase()
                        .includes(courseIdentifier.toLowerCase())) ||
                    c.title
                      .toLowerCase()
                      .includes(courseIdentifier.toLowerCase())
                );
              }

              if (matchingCourse) {
                console.log(
                  'Found course through list filtering:',
                  matchingCourse
                );
                courseResponse = matchingCourse;
              } else {
                throw new Error('Course not found with any approach');
              }
            } catch (finalError) {
              console.error('All fetch attempts failed:', finalError);
              throw new Error(
                'Course not found. Please check the URL and try again.'
              );
            }
          }
        }

        // Ignore further processing if aborted
        if (signal.aborted) return;

        const courseData = Array.isArray(courseResponse)
          ? courseResponse[0]
          : courseResponse;
        if (!courseData) {
          throw new Error('Course not found');
        }

        console.log('Retrieved course data:', courseData);
        setCourse(courseData);

        // Fetch course modules using the definitive course ID
        const modulesResponse = await instructorService.getModules(
          courseData.id,
          { signal }
        );

        // Ignore further processing if aborted
        if (signal.aborted) return;
        setModules(modulesResponse || []);
        setLoading(false);
      } catch (err) {
        // Ignore if aborted
        if (signal?.aborted) return;

        console.error('Failed to fetch course details:', err);
        setError('Failed to load course details. Please try again.');
        setLoading(false);
      }
    };

    fetchCourseData();

    // Cleanup function to abort any pending requests when unmounting
    return () => {
      abortController.abort();
    };

    // Cleanup function to abort any pending requests when unmounting
    return () => {
      abortController.abort();
    };
  }, [courseIdentifier]);

  // Handler to publish the course
  const handlePublish = async () => {
    try {
      await instructorService.publishCourse(course.slug || course.id, true);
      setCourse({ ...course, is_published: true });
    } catch (err) {
      alert(
        'Failed to publish course. Please ensure all required fields are filled.'
      );
    }
  };

  // Handler to unpublish the course
  const handleUnpublish = async () => {
    try {
      await instructorService.publishCourse(course.slug || course.id, false);
      setCourse({ ...course, is_published: false });
    } catch (err) {
      alert('Failed to unpublish course.');
    }
  };

  if (loading) {
    return (
      <Container>
        <div className="py-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading course details...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert type="error" className="my-8">
          {error}
        </Alert>
        <Button
          onClick={() => navigate('/instructor/dashboard')}
          variant="contained"
          color="primary"
        >
          Return to Dashboard
        </Button>
      </Container>
    );
  }

  if (!course) {
    return (
      <Container>
        <div className="py-12 text-center">Course not found</div>
        <Button
          onClick={() => navigate('/instructor/dashboard')}
          variant="contained"
          color="primary"
        >
          Return to Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <div className="py-8">
      <Container>
        <div className="mb-6">
          <div className="flex items-center mb-1">
            <Link
              to="/instructor/dashboard"
              className="text-blue-600 hover:underline text-sm"
            >
              Dashboard
            </Link>
            <span className="mx-2 text-gray-500">/</span>
            <span className="text-sm font-medium">Course Details</span>
          </div>

          <div className="flex justify-between items-start">
            <h1 className="text-3xl font-bold">{course.title}</h1>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => navigate(`/instructor/courses/${courseSlug}/edit`)}
            >
              Edit Course
            </Button>
          </div>

          <p className="text-gray-600 mt-2">
            {course.description || course.subtitle}
          </p>
        </div>

        <div className="mb-6">
          <Tabs
            tabs={[
              { id: 'modules', label: 'Modules' },
              { id: 'lessons', label: 'Lessons' },
              { id: 'resources', label: 'Resources' },
              { id: 'assessments', label: 'Assessments' },
              { id: 'preview', label: 'Preview as Student' },
              { id: 'settings', label: 'Settings' },
            ]}
            activeTab={activeTab}
            onChange={setActiveTab}
          />
        </div>

        {activeTab === 'modules' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Course Modules</h2>
              <Button
                variant="contained"
                color="primary"
                onClick={() =>
                  navigate(`/courses/${courseSlug}/modules/create`)
                }
              >
                Add New Module
              </Button>
            </div>

            {modules.length > 0 ? (
              <div className="space-y-4">
                {modules.map(module => (
                  <Card key={module.id} className="overflow-visible">
                    <div className="p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold">
                            {module.title}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {module.lessons?.length || 0} lessons ·{' '}
                            {module.duration_display || 'No duration set'}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outlined"
                            color="secondary"
                            size="small"
                            onClick={() =>
                              navigate(`/courses/modules/${module.id}/edit`)
                            }
                          >
                            Edit Module
                          </Button>
                          <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            onClick={() =>
                              navigate(
                                `/courses/${courseSlug}/modules/${module.id}/lessons/create`
                              )
                            }
                          >
                            Add Lesson
                          </Button>
                        </div>
                      </div>

                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Lessons:</h4>
                        {module.lessons && module.lessons.length > 0 ? (
                          <ul className="divide-y divide-gray-200 border border-gray-200 rounded-md overflow-hidden">
                            {module.lessons.map(lesson => (
                              <li
                                key={lesson.id}
                                className="p-3 hover:bg-gray-50"
                              >
                                <div className="flex justify-between items-center">
                                  <div>
                                    <span className="font-medium">
                                      {lesson.title}
                                    </span>
                                    <span className="ml-2 text-sm text-gray-600">
                                      ({lesson.type},{' '}
                                      {lesson.duration_display || 'No duration'}
                                      )
                                    </span>
                                  </div>
                                  <div className="space-x-2">
                                    <Button
                                      variant="text"
                                      color="primary"
                                      size="small"
                                      onClick={() =>
                                        navigate(
                                          `/courses/${courseSlug}/content/${module.id}/${lesson.id}`
                                        )
                                      }
                                    >
                                      View
                                    </Button>
                                    <Button
                                      variant="text"
                                      color="secondary"
                                      size="small"
                                      onClick={() =>
                                        navigate(
                                          `/courses/lessons/${lesson.id}/edit`
                                        )
                                      }
                                    >
                                      Edit
                                    </Button>
                                  </div>
                                </div>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-500 italic p-3 bg-gray-50 rounded">
                            No lessons in this module yet.
                            <button
                              className="ml-2 text-blue-600 hover:underline"
                              onClick={() =>
                                navigate(
                                  `/courses/${courseSlug}/modules/${module.id}/lessons/create`
                                )
                              }
                            >
                              Add your first lesson
                            </button>
                          </p>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <p className="text-gray-600 mb-4">
                  This course doesn't have any modules yet.
                </p>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() =>
                    navigate(`/courses/${courseSlug}/modules/create`)
                  }
                >
                  Create Your First Module
                </Button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'lessons' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">All Lessons</h2>
            {modules.length === 0 ? (
              <div className="text-gray-600">
                No modules found. Please add a module first.
              </div>
            ) : (
              modules.map(module => (
                <Card key={module.id} className="mb-4">
                  <div className="p-4">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-medium">Module: {module.title}</h3>
                      <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        onClick={() =>
                          navigate(
                            `/courses/${courseSlug}/modules/${module.id}/lessons/create`
                          )
                        }
                      >
                        Add Lesson
                      </Button>
                    </div>
                    {module.lessons && module.lessons.length > 0 ? (
                      <ul className="divide-y divide-gray-200 border border-gray-200 rounded-md overflow-hidden">
                        {module.lessons.map(lesson => (
                          <li
                            key={lesson.id}
                            className="p-3 hover:bg-gray-50 flex justify-between items-center"
                          >
                            <div>
                              <span className="font-medium">
                                {lesson.title}
                              </span>
                              <span className="ml-2 text-sm text-gray-600">
                                ({lesson.type},{' '}
                                {lesson.duration_display || 'No duration'})
                              </span>
                            </div>
                            <div className="space-x-2">
                              <Button
                                variant="text"
                                color="primary"
                                size="small"
                                onClick={() =>
                                  navigate(
                                    `/courses/${courseSlug}/content/${module.id}/${lesson.id}`
                                  )
                                }
                              >
                                View
                              </Button>
                              <Button
                                variant="text"
                                color="secondary"
                                size="small"
                                onClick={() =>
                                  navigate(`/courses/lessons/${lesson.id}/edit`)
                                }
                              >
                                Edit
                              </Button>
                              <Button
                                variant="text"
                                color="danger"
                                size="small"
                                onClick={() => {
                                  /* implement delete handler */
                                }}
                              >
                                Delete
                              </Button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-gray-500 italic">
                        No lessons in this module yet.
                      </div>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'resources' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">All Resources</h2>
            {modules.length === 0 ? (
              <div className="text-gray-600">
                No modules found. Please add a module first.
              </div>
            ) : (
              modules.map(module => (
                <Card key={module.id} className="mb-4">
                  <div className="p-4">
                    <h3 className="font-medium mb-2">Module: {module.title}</h3>
                    {module.lessons && module.lessons.length > 0 ? (
                      module.lessons.map(lesson => (
                        <div key={lesson.id} className="mb-2">
                          <div className="font-medium">
                            Lesson: {lesson.title}
                          </div>
                          {/* List resources for this lesson */}
                          {lesson.resources && lesson.resources.length > 0 ? (
                            <ul className="ml-4 list-disc">
                              {lesson.resources.map(res => (
                                <li
                                  key={res.id}
                                  className="flex justify-between items-center"
                                >
                                  <span>
                                    {res.title} ({res.type})
                                  </span>
                                  {/* Add edit/delete actions if needed */}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="ml-4 text-gray-500 italic">
                              No resources for this lesson.
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 italic">
                        No lessons in this module yet.
                      </div>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'assessments' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">All Assessments</h2>
            {modules.length === 0 ? (
              <div className="text-gray-600">
                No modules found. Please add a module first.
              </div>
            ) : (
              modules.map(module => (
                <Card key={module.id} className="mb-4">
                  <div className="p-4">
                    <h3 className="font-medium mb-2">Module: {module.title}</h3>
                    {module.lessons && module.lessons.length > 0 ? (
                      module.lessons.map(lesson => (
                        <div key={lesson.id} className="mb-2">
                          <div className="font-medium">
                            Lesson: {lesson.title}
                          </div>
                          {/* List assessments for this lesson */}
                          {lesson.assessments &&
                          lesson.assessments.length > 0 ? (
                            <ul className="ml-4 list-disc">
                              {lesson.assessments.map(assess => (
                                <li
                                  key={assess.id}
                                  className="flex justify-between items-center"
                                >
                                  <span>{assess.title}</span>
                                  {/* Add edit/delete actions if needed */}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="ml-4 text-gray-500 italic">
                              No assessments for this lesson.
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 italic">
                        No lessons in this module yet.
                      </div>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'preview' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Preview as Student</h2>
            <CourseLandingPage courseSlug={courseSlug} previewMode={true} />
          </div>
        )}

        {activeTab === 'settings' && (
          <div>
            <Card className="mb-4">
              <h3 className="font-semibold mb-2">Publishing Options</h3>
              <p className="text-sm text-gray-600 mb-4">
                Current status:{' '}
                <span
                  className={
                    course.is_published ? 'text-green-600' : 'text-yellow-600'
                  }
                >
                  {course.is_published ? 'Published' : 'Draft'}
                </span>
              </p>
              <div className="flex space-x-3">
                {!course.is_published && (
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handlePublish}
                  >
                    Publish Course
                  </Button>
                )}
                {course.is_published && (
                  <Button
                    variant="outlined"
                    color="warning"
                    onClick={handleUnpublish}
                  >
                    Unpublish Course
                  </Button>
                )}
              </div>
            </Card>
          </div>
        )}
      </Container>
    </div>
  );
};

export default function InstructorCourseDetailPageWithErrorBoundary() {
  const navigate = useNavigate();

  const handleNavigateHome = () => {
    navigate('/instructor/dashboard');
  };

  const handleContactSupport = () => {
    navigate('/support');
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Instructor Course Detail Error:', {
      error,
      errorInfo,
      context,
    });
    // Could send to error tracking service here
  };

  return (
    <InstructorErrorBoundary
      onNavigateHome={handleNavigateHome}
      onContactSupport={handleContactSupport}
      onError={handleError}
    >
      <InstructorCourseDetailPage />
    </InstructorErrorBoundary>
  );
}
