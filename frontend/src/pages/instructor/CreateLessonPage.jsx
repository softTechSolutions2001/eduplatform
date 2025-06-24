/**
 * File: frontend/src/pages/instructor/CreateLessonPage.jsx
 * Version: 2.4.0 (Merged)
 * Date: 2025-06-20 15:48:11
 * Author: GitHub Copilot, Professor Santhanam
 * Last Modified: 2025-06-20 15:48:11 UTC
 * Merged By: sujibeautysalon
 *
 * Enhanced Create Lesson Page with Unified Access Level System
 *
 * MERGE RESOLUTION v2.4.0:
 * - Combined advanced tiered content system from HEAD (guest/registered/premium)
 * - Preserved simplified UI structure from branch (clean layout, basic forms)
 * - Unified access level terminology throughout the application
 * - Integrated comprehensive form validation and error handling
 * - Added rich text editing capabilities with TinyMCE
 * - Maintained resource management and assessment creation
 * - Enhanced breadcrumb navigation and user feedback
 * - Error boundary integration for production stability
 *
 * Key Features:
 * 1. Unified Access Level System (guest/registered/premium)
 * 2. Tiered Content Creation (different content for different user levels)
 * 3. Rich Text Editor Integration (TinyMCE for content creation)
 * 4. Comprehensive Resource Management (file uploads, external links)
 * 5. Assessment and Lab Exercise Integration
 * 6. Advanced Form Validation with Real-time Feedback
 * 7. Duration Input with Formatted Display
 * 8. Breadcrumb Navigation with Context
 * 9. Error Boundary Integration for Production Stability
 * 10. Auto-save Functionality Integration
 *
 * Access Levels (Unified Terminology):
 * - guest: Preview content for unregistered users
 * - registered: Standard content for logged-in users
 * - premium: Full content for paid subscribers
 *
 * Connected Files (Backend Integration):
 * - backend/instructor/api/v1/lessons/ (lesson CRUD operations)
 * - backend/courses/models.py (Lesson model with tiered content fields)
 * - backend/instructor/utils/permissions/ (instructor role validation)
 * - backend/accounts/models.py (User.is_instructor property)
 *
 * Frontend Integration:
 * - frontend/src/services/instructorService.js (v3.0.0 compatibility)
 * - frontend/src/utils/courseDataSync.js (unified access levels and validation)
 * - frontend/src/utils/validation.js (lesson validation logic)
 * - frontend/src/components/common/DurationInput.jsx (duration input component)
 */

import { Editor } from '@tinymce/tinymce-react';
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  Alert,
  Button,
  Card,
  Container,
  FormInput,
  Tabs,
} from '../../components/common';
import DurationInput from '../../components/common/DurationInput';
import { ContentCreationErrorBoundary } from '../../components/common/errorBoundaries';
import LoadingScreen from '../../components/common/LoadingScreen';
import { useAuth } from '../../contexts/AuthContext';
import instructorService from '../../services/instructorService';
import {
  ACCESS_LEVELS,
  ACCESS_LEVEL_LABELS,
  LESSON_TYPES,
  normalizeAccessLevel,
} from '../../utils/courseDataSync';
import { formatDuration } from '../../utils/formatDuration';
import { validateLessonData } from '../../utils/validation';

const CreateLessonPage = () => {
  const { currentUser, isAuthenticated, isInstructor } = useAuth();
  const navigate = useNavigate();
  const { courseSlug, moduleId } = useParams();

  // Form state with unified terminology
  const [lessonForm, setLessonForm] = useState({
    title: '',
    duration: '',
    duration_minutes: 0,
    type: LESSON_TYPES?.VIDEO || 'video',
    content: '', // Premium content (full content)
    guest_content: '', // Guest preview content
    registered_content: '', // Registered user content
    basic_content: '', // Backward compatibility
    intermediate_content: '', // Backward compatibility
    access_level: ACCESS_LEVELS?.REGISTERED || 'intermediate',
    is_free_preview: false,
    order: 1,
  });

  // Additional lesson options
  const [hasAssessment, setHasAssessment] = useState(false);
  const [hasLab, setHasLab] = useState(false);

  // Resources state
  const [resources, setResources] = useState([]);
  const [newResource, setNewResource] = useState({
    title: '',
    type: 'Document',
    description: '',
    file: null,
    url: '',
    premium: false,
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formError, setFormError] = useState('');
  const [success, setSuccess] = useState(false);
  const [currentTab, setCurrentTab] = useState('basic');
  const [moduleDetails, setModuleDetails] = useState(null);
  const [courseDetails, setCourseDetails] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);

  // Access level options using unified constants
  const accessLevelOptions = ACCESS_LEVELS
    ? [
      {
        value: ACCESS_LEVELS.GUEST,
        label: ACCESS_LEVEL_LABELS[ACCESS_LEVELS.GUEST],
      },
      {
        value: ACCESS_LEVELS.REGISTERED,
        label: ACCESS_LEVEL_LABELS[ACCESS_LEVELS.REGISTERED],
      },
      {
        value: ACCESS_LEVELS.PREMIUM,
        label: ACCESS_LEVEL_LABELS[ACCESS_LEVELS.PREMIUM],
      },
    ]
    : [
      { value: 'basic', label: 'Basic (Unregistered Users)' },
      { value: 'intermediate', label: 'Intermediate (Registered Users)' },
      { value: 'advanced', label: 'Advanced (Paid Users)' },
    ];

  const lessonTypeOptions = LESSON_TYPES
    ? [
      { value: LESSON_TYPES.VIDEO, label: 'Video' },
      { value: LESSON_TYPES.READING, label: 'Reading Material' },
      { value: LESSON_TYPES.INTERACTIVE, label: 'Interactive Content' },
      { value: LESSON_TYPES.QUIZ, label: 'Quiz' },
      { value: LESSON_TYPES.LAB, label: 'Lab Exercise' },
    ]
    : [
      { value: 'video', label: 'Video' },
      { value: 'reading', label: 'Reading' },
      { value: 'interactive', label: 'Interactive' },
      { value: 'quiz', label: 'Quiz' },
      { value: 'lab', label: 'Lab Exercise' },
    ];

  const tabOptions = [
    { id: 'basic', label: 'Basic Info' },
    { id: 'content', label: 'Content' },
    { id: 'resources', label: 'Resources' },
    { id: 'options', label: 'Options' },
  ];

  // Check authentication and authorization
  useEffect(() => {
    if (isAuthenticated === false) {
      navigate('/login?redirect=' + encodeURIComponent(window.location.pathname));
      return;
    }

    if (isAuthenticated === true && !isInstructor()) {
      navigate('/forbidden');
      return;
    }
  }, [isAuthenticated, isInstructor, navigate]);

  // Enhanced form change handler with error clearing
  const handleFormChange = (field, value) => {
    setFormError(''); // Clear any previous validation errors
    setLessonForm({
      ...lessonForm,
      [field]: value,
    });
  };

  // Enhanced editor change handler with error clearing
  const handleEditorChange = (field, content) => {
    setFormError(''); // Clear any previous validation errors
    setLessonForm({
      ...lessonForm,
      [field]: content,
    });
  };

  // Fetch module and course details
  useEffect(() => {
    const fetchDetails = async () => {
      if (!moduleId || !isAuthenticated) return;

      try {
        setInitialLoading(true);
        setError(null);

        // Fetch module details
        if (moduleId) {
          const moduleResponse = await instructorService.getModule(moduleId);
          const moduleData = moduleResponse.data || moduleResponse;
          setModuleDetails(moduleData);

          // Get existing lessons to determine order
          try {
            const lessonsResponse = await instructorService.getLessons(moduleId);
            const existingLessons = lessonsResponse.data || lessonsResponse;
            setLessonForm(prev => ({
              ...prev,
              order: Array.isArray(existingLessons)
                ? existingLessons.length + 1
                : 1,
            }));
          } catch (err) {
            console.error('Failed to fetch lessons for order:', err);
            // Continue with default order = 1
          }
        }

        // Fetch course details if courseSlug is provided
        if (courseSlug) {
          try {
            const courseResponse = await instructorService.getCourseBySlug(courseSlug);
            const courseData = courseResponse.data || courseResponse;
            setCourseDetails(Array.isArray(courseData) ? courseData[0] : courseData);
          } catch (err) {
            console.error('Failed to fetch course details:', err);
            // Continue without course details
          }
        }
      } catch (error) {
        console.error('Error fetching details:', error);
        setError('Failed to load course/module details');
      } finally {
        setInitialLoading(false);
      }
    };

    fetchDetails();
  }, [moduleId, courseSlug, isAuthenticated]);

  // Enhanced form submission with unified validation
  const handleSubmit = async e => {
    e.preventDefault();

    // Clear any previous validation errors
    setFormError('');
    setError(null);

    // Basic validation
    if (!lessonForm.title.trim()) {
      setFormError('Lesson title is required');
      return;
    }

    if (!lessonForm.content && !lessonForm.registered_content && !lessonForm.intermediate_content) {
      setFormError('At least one content field is required');
      return;
    }

    // Use unified validation logic if available
    if (validateLessonData) {
      const validationResult = validateLessonData(lessonForm);
      if (!validationResult.isValid) {
        const firstError = Object.values(validationResult.errors)[0];
        setFormError(firstError);
        return;
      }
    }

    try {
      setLoading(true);

      // Prepare lesson data with normalized access level
      const lessonData = {
        module: moduleId,
        title: lessonForm.title.trim(),
        content: lessonForm.content || lessonForm.intermediate_content || '',
        basic_content: lessonForm.guest_content || lessonForm.basic_content || '',
        intermediate_content: lessonForm.registered_content || lessonForm.intermediate_content || '',
        access_level: normalizeAccessLevel ? normalizeAccessLevel(lessonForm.access_level) : lessonForm.access_level,
        duration: lessonForm.duration || '',
        duration_minutes: lessonForm.duration_minutes || 0,
        type: lessonForm.type,
        order: lessonForm.order,
        has_assessment: hasAssessment,
        has_lab: hasLab,
        is_free_preview: lessonForm.is_free_preview,
      };

      // Create the lesson
      const response = await instructorService.createLesson(lessonData);
      const newLessonId = response.data?.id || response.id;

      // Upload resources if any
      if (resources.length > 0 && newLessonId) {
        await Promise.all(
          resources.map(async resource => {
            const formData = new FormData();
            formData.append('lesson', newLessonId);
            formData.append('title', resource.title);
            formData.append('type', resource.type);
            formData.append('description', resource.description);
            formData.append('premium', resource.premium);

            if (resource.file) {
              formData.append('file', resource.file);
            }

            if (resource.url) {
              formData.append('url', resource.url);
            }

            return instructorService.createResource(formData);
          })
        );
      }

      // Create assessment if needed
      if (hasAssessment && newLessonId) {
        await instructorService.createAssessment({
          lesson: newLessonId,
          title: `${lessonForm.title} Assessment`,
          description: `Assessment for ${lessonForm.title}`,
          time_limit: 0, // No time limit by default
          passing_score: 70, // Default passing score
        });
      }

      setSuccess(true);

      // Redirect after successful creation
      setTimeout(() => {
        if (courseSlug) {
          navigate(`/instructor/courses/${courseSlug}/curriculum`);
        } else {
          navigate(`/instructor/modules/${moduleId}/lessons`);
        }
      }, 2000);
    } catch (error) {
      console.error('Error creating lesson:', error);
      const errorMessage =
        error.details || error.message || 'Failed to create lesson';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle adding a new resource
  const handleAddResource = () => {
    if (!newResource.title || (!newResource.file && !newResource.url)) {
      setError('Resource title and either file or URL are required.');
      return;
    }

    setResources([...resources, { ...newResource, id: Date.now() }]);
    setNewResource({
      title: '',
      type: 'Document',
      description: '',
      file: null,
      url: '',
      premium: false,
    });
    setError(null);
  };

  // Handle removing a resource
  const handleRemoveResource = resourceId => {
    setResources(resources.filter(resource => resource.id !== resourceId));
  };

  // Handle file selection
  const handleFileChange = e => {
    setNewResource({ ...newResource, file: e.target.files[0] });
  };

  // Show loading screen while authentication is being determined or initial data is loading
  if (isAuthenticated === null || initialLoading) {
    return (
      <Container>
        <LoadingScreen message="Loading lesson creation page..." />
      </Container>
    );
  }

  return (
    <div className="py-8">
      <Container>
        {/* Breadcrumbs */}
        <div className="mb-6">
          <nav className="text-sm breadcrumbs mb-4">
            <ol className="flex space-x-2 text-gray-500">
              <li>
                <Link
                  to="/instructor/dashboard"
                  className="hover:text-blue-600"
                >
                  Dashboard
                </Link>
              </li>
              <li className="before:content-['/'] before:mx-2">
                {courseDetails ? (
                  <Link
                    to={`/instructor/courses/${courseSlug}/curriculum`}
                    className="hover:text-blue-600"
                  >
                    {courseDetails.title}
                  </Link>
                ) : (
                  <span>Course</span>
                )}
              </li>
              <li className="before:content-['/'] before:mx-2">
                {moduleDetails ? (
                  <span className="text-gray-700">{moduleDetails.title}</span>
                ) : (
                  <span>Module</span>
                )}
              </li>
              <li className="before:content-['/'] before:mx-2">
                <span className="text-blue-600 font-medium">Create Lesson</span>
              </li>
            </ol>
          </nav>

          <h1 className="text-3xl font-bold mb-2">Create New Lesson</h1>
          {moduleDetails && (
            <p className="text-gray-600">
              Adding lesson to module: <strong>{moduleDetails.title}</strong>
            </p>
          )}
        </div>

        {/* Error and Success Messages */}
        {error && (
          <Alert type="error" className="mb-6">
            {error}
          </Alert>
        )}

        {formError && (
          <Alert type="warning" className="mb-6">
            {formError}
          </Alert>
        )}

        {success && (
          <Alert type="success" className="mb-6">
            Lesson created successfully! Redirecting...
          </Alert>
        )}

        {/* Main Form */}
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main content area */}
            <div className="lg:col-span-3">
              <Card className="overflow-visible">
                <Tabs
                  activeTab={currentTab}
                  onTabChange={setCurrentTab}
                  tabs={tabOptions}
                />

                <div className="mt-6">
                  {/* Basic Information Tab */}
                  {currentTab === 'basic' && (
                    <div className="space-y-4">
                      <FormInput
                        label="Lesson Title"
                        id="lesson-title"
                        name="title"
                        value={lessonForm.title}
                        onChange={e =>
                          handleFormChange('title', e.target.value)
                        }
                        required
                        placeholder="e.g., Introduction to React Components"
                      />

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-gray-700 font-medium mb-1">
                            Lesson Type
                          </label>
                          <select
                            value={lessonForm.type}
                            onChange={e =>
                              handleFormChange('type', e.target.value)
                            }
                            className="w-full p-2 border border-gray-300 rounded-md"
                          >
                            {lessonTypeOptions.map(option => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <FormInput
                            label="Duration (text)"
                            id="duration"
                            name="duration"
                            value={lessonForm.duration}
                            onChange={e =>
                              handleFormChange('duration', e.target.value)
                            }
                            placeholder="e.g., 30 min"
                          />

                          {/* Advanced duration input if component is available */}
                          {DurationInput && (
                            <div className="mt-2">
                              <DurationInput
                                label="Precise Duration"
                                value={lessonForm.duration_minutes || 0}
                                onChange={minutes =>
                                  handleFormChange('duration_minutes', minutes)
                                }
                                placeholder="Select lesson duration"
                              />
                              {lessonForm.duration_minutes > 0 && (
                                <p className="mt-1 text-sm text-gray-500">
                                  Duration:{' '}
                                  {formatDuration ? formatDuration(lessonForm.duration_minutes) : `${lessonForm.duration_minutes} minutes`}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-gray-700 font-medium mb-1">
                            Access Level
                          </label>
                          <select
                            value={lessonForm.access_level}
                            onChange={e =>
                              handleFormChange('access_level', e.target.value)
                            }
                            className="w-full p-2 border border-gray-300 rounded-md"
                          >
                            {accessLevelOptions.map(option => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <p className="mt-1 text-sm text-gray-500">
                            Determines which users can access this lesson
                          </p>
                        </div>

                        <FormInput
                          label="Order"
                          id="lesson-order"
                          type="number"
                          value={lessonForm.order}
                          onChange={e =>
                            handleFormChange('order', Number(e.target.value))
                          }
                          required
                          min="1"
                        />
                      </div>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="is_free_preview"
                          checked={lessonForm.is_free_preview}
                          onChange={e =>
                            handleFormChange(
                              'is_free_preview',
                              e.target.checked
                            )
                          }
                          className="mr-2"
                        />
                        <label
                          htmlFor="is_free_preview"
                          className="text-gray-700"
                        >
                          Mark as free preview lesson
                        </label>
                      </div>
                    </div>
                  )}

                  {/* Content Tab */}
                  {currentTab === 'content' && (
                    <div className="space-y-6">
                      {/* Guest/Basic Content */}
                      <div>
                        <label className="block text-gray-700 font-medium mb-2">
                          Guest/Basic Content (Preview for Unregistered Users)
                        </label>
                        <p className="text-sm text-gray-500 mb-2">
                          This content is visible to all users as a preview
                        </p>
                        {Editor ? (
                          <Editor
                            apiKey="your-tinymce-api-key"
                            value={lessonForm.guest_content || lessonForm.basic_content || ''}
                            onEditorChange={content =>
                              handleEditorChange('guest_content', content)
                            }
                            init={{
                              height: 200,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
                            }}
                          />
                        ) : (
                          <textarea
                            rows={5}
                            className="w-full p-3 border border-gray-300 rounded-md"
                            value={lessonForm.guest_content || lessonForm.basic_content || ''}
                            onChange={e => handleFormChange('guest_content', e.target.value)}
                            placeholder="Enter preview content for unregistered users"
                          />
                        )}
                      </div>

                      {/* Registered/Intermediate Content */}
                      <div>
                        <label className="block text-gray-700 font-medium mb-2">
                          Registered/Intermediate Content (Standard Content for Logged-in Users)
                        </label>
                        <p className="text-sm text-gray-500 mb-2">
                          This content is visible to registered users
                        </p>
                        {Editor ? (
                          <Editor
                            apiKey="your-tinymce-api-key"
                            value={lessonForm.registered_content || lessonForm.intermediate_content || ''}
                            onEditorChange={content =>
                              handleEditorChange('registered_content', content)
                            }
                            init={{
                              height: 250,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
                            }}
                          />
                        ) : (
                          <textarea
                            rows={5}
                            className="w-full p-3 border border-gray-300 rounded-md"
                            value={lessonForm.registered_content || lessonForm.intermediate_content || ''}
                            onChange={e => handleFormChange('registered_content', e.target.value)}
                            placeholder="Enter content for registered users"
                          />
                        )}
                      </div>

                      {/* Premium/Advanced Content */}
                      <div>
                        <label className="block text-gray-700 font-medium mb-2">
                          Premium/Advanced Content (Full Content for Paid Subscribers)
                        </label>
                        <p className="text-sm text-gray-500 mb-2">
                          This is the complete lesson content for premium users
                        </p>
                        {Editor ? (
                          <Editor
                            apiKey="your-tinymce-api-key"
                            value={lessonForm.content}
                            onEditorChange={content =>
                              handleEditorChange('content', content)
                            }
                            init={{
                              height: 300,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
                            }}
                          />
                        ) : (
                          <textarea
                            rows={6}
                            className="w-full p-3 border border-gray-300 rounded-md"
                            value={lessonForm.content}
                            onChange={e => handleFormChange('content', e.target.value)}
                            placeholder="Enter full content for paid users"
                          />
                        )}
                      </div>
                    </div>
                  )}

                  {/* Resources Tab */}
                  {currentTab === 'resources' && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-semibold">
                        Lesson Resources
                      </h3>

                      {/* Add Resource Form */}
                      <div className="border rounded-lg p-4 bg-gray-50">
                        <h4 className="font-medium mb-3">Add New Resource</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <FormInput
                            label="Resource Title"
                            value={newResource.title}
                            onChange={e =>
                              setNewResource({
                                ...newResource,
                                title: e.target.value,
                              })
                            }
                            placeholder="e.g., Course Slides"
                          />

                          <div>
                            <label className="block text-gray-700 font-medium mb-1">
                              Resource Type
                            </label>
                            <select
                              value={newResource.type}
                              onChange={e =>
                                setNewResource({
                                  ...newResource,
                                  type: e.target.value,
                                })
                              }
                              className="w-full p-2 border border-gray-300 rounded-md"
                            >
                              <option value="Document">Document</option>
                              <option value="Video">Video</option>
                              <option value="Audio">Audio</option>
                              <option value="Image">Image</option>
                              <option value="Link">External Link</option>
                            </select>
                          </div>
                        </div>

                        <div className="mt-4">
                          <FormInput
                            label="Description"
                            value={newResource.description}
                            onChange={e =>
                              setNewResource({
                                ...newResource,
                                description: e.target.value,
                              })
                            }
                            placeholder="Brief description of this resource"
                          />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                          <div>
                            <label className="block text-gray-700 font-medium mb-1">
                              Upload File
                            </label>
                            <input
                              type="file"
                              onChange={handleFileChange}
                              className="w-full p-2 border border-gray-300 rounded-md"
                            />
                          </div>

                          <FormInput
                            label="Or URL"
                            value={newResource.url}
                            onChange={e =>
                              setNewResource({
                                ...newResource,
                                url: e.target.value,
                              })
                            }
                            placeholder="https://example.com/resource"
                          />
                        </div>

                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              id="premium-resource"
                              checked={newResource.premium}
                              onChange={e =>
                                setNewResource({
                                  ...newResource,
                                  premium: e.target.checked,
                                })
                              }
                              className="mr-2"
                            />
                            <label
                              htmlFor="premium-resource"
                              className="text-gray-700"
                            >
                              Premium Resource (only for paid subscribers)
                            </label>
                          </div>

                          <Button
                            type="button"
                            onClick={handleAddResource}
                            size="small"
                          >
                            Add Resource
                          </Button>
                        </div>
                      </div>

                      {/* Resources List */}
                      {resources.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-3">Added Resources</h4>
                          <div className="space-y-2">
                            {resources.map(resource => (
                              <div
                                key={resource.id}
                                className="flex items-center justify-between p-3 border rounded-md"
                              >
                                <div>
                                  <span className="font-medium">
                                    {resource.title}
                                  </span>
                                  <span className="text-gray-500 ml-2">
                                    ({resource.type})
                                  </span>
                                  {resource.premium && (
                                    <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                                      Premium
                                    </span>
                                  )}
                                </div>
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="small"
                                  onClick={() =>
                                    handleRemoveResource(resource.id)
                                  }
                                >
                                  Remove
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Options Tab */}
                  {currentTab === 'options' && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-semibold">Lesson Options</h3>

                      <div className="space-y-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="has-assessment"
                            checked={hasAssessment}
                            onChange={e => setHasAssessment(e.target.checked)}
                            className="mr-2"
                          />
                          <label
                            htmlFor="has-assessment"
                            className="text-gray-700 font-medium"
                          >
                            Include Assessment/Quiz
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="has-lab"
                            checked={hasLab}
                            onChange={e => setHasLab(e.target.checked)}
                            className="mr-2"
                          />
                          <label
                            htmlFor="has-lab"
                            className="text-gray-700 font-medium"
                          >
                            Include Lab Exercise
                          </label>
                        </div>
                      </div>

                      {hasAssessment && (
                        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                          <p className="text-sm text-blue-700">
                            An assessment will be created for this lesson with
                            default settings. You can customize it later from
                            the lesson management page.
                          </p>
                        </div>
                      )}

                      {hasLab && (
                        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                          <p className="text-sm text-green-700">
                            This lesson will be marked as having a lab exercise.
                            Students will see lab instructions in the lesson
                            content.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <Card className="sticky top-6">
                <h3 className="text-lg font-semibold mb-4">Lesson Actions</h3>

                <div className="space-y-3">
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading || !lessonForm.title.trim()}
                    className="w-full"
                  >
                    {loading ? 'Creating Lesson...' : 'Create Lesson'}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      if (courseSlug) {
                        navigate(
                          `/instructor/courses/${courseSlug}/curriculum`
                        );
                      } else {
                        navigate(`/instructor/modules/${moduleId}/lessons`);
                      }
                    }}
                    className="w-full"
                  >
                    Cancel
                  </Button>
                </div>

                {/* Progress indicator */}
                <div className="mt-6 p-3 bg-gray-50 rounded-md">
                  <h4 className="font-medium text-sm mb-2">
                    Completion Progress
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Title</span>
                      <span
                        className={
                          lessonForm.title ? 'text-green-600' : 'text-gray-400'
                        }
                      >
                        {lessonForm.title ? '✓' : '○'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Content</span>
                      <span
                        className={
                          lessonForm.content ||
                            lessonForm.registered_content ||
                            lessonForm.intermediate_content ||
                            lessonForm.guest_content ||
                            lessonForm.basic_content
                            ? 'text-green-600'
                            : 'text-gray-400'
                        }
                      >
                        {lessonForm.content ||
                          lessonForm.registered_content ||
                          lessonForm.intermediate_content ||
                          lessonForm.guest_content ||
                          lessonForm.basic_content
                          ? '✓'
                          : '○'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Access Level</span>
                      <span
                        className={
                          lessonForm.access_level
                            ? 'text-green-600'
                            : 'text-gray-400'
                        }
                      >
                        {lessonForm.access_level ? '✓' : '○'}
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </form>
      </Container>
    </div>
  );
};

// Export with Error Boundary wrapper for production stability
export default function CreateLessonPageWithErrorBoundary() {
  const navigate = useNavigate();

  const handleNavigateBack = () => {
    navigate(-1); // Go back to previous page
  };

  const handleSaveContent = () => {
    // Trigger auto-save functionality if available
    const event = new CustomEvent('triggerAutoSave');
    window.dispatchEvent(event);
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Lesson Creation Error:', { error, errorInfo, context });
    // Could send to error tracking service here
  };

  return (
    <ContentCreationErrorBoundary
      onNavigateBack={handleNavigateBack}
      onSaveContent={handleSaveContent}
      onError={handleError}
    >
      <CreateLessonPage />
    </ContentCreationErrorBoundary>
  );
}
