/**
 * File: frontend/src/pages/instructor/CreateModulePage.jsx
 * Version: 2.3.0 (Merged)
 * Date: 2025-06-20 15:41:31
 * Author: mohithasanthanam, Professor Santhanam
 * Last Modified: 2025-06-20 15:41:31 UTC
 * Merged By: sujibeautysalon
 *
 * Enhanced Create Module Page with Comprehensive Form Validation and Error Handling
 *
 * MERGE RESOLUTION v2.3.0:
 * - Combined advanced form features from HEAD (comprehensive validation, duration input)
 * - Preserved simplified UI patterns from branch (clean layout, basic validation)
 * - Unified authentication handling and course data fetching
 * - Integrated error boundary for production stability
 * - Added comprehensive accessibility features
 * - Maintained backward compatibility with existing API endpoints
 *
 * Key Features:
 * 1. Advanced Form Validation with Real-time Feedback
 * 2. Comprehensive Error Handling and User Feedback
 * 3. Duration Input with Formatted Display
 * 4. Access Level Control for Module Content
 * 5. Publication Status Management
 * 6. Breadcrumb Navigation with Context
 * 7. Error Boundary Integration for Production Stability
 * 8. Responsive Design with Mobile Support
 * 9. Accessibility Features (ARIA labels, proper form structure)
 * 10. Auto-save Functionality Integration
 *
 * Connected Files (Backend Integration):
 * - backend/instructor/api/v1/modules/ (module CRUD operations)
 * - backend/courses/models.py (Module model with all tracked fields)
 * - backend/instructor/utils/permissions/ (instructor role validation)
 * - backend/accounts/models.py (User.is_instructor property)
 *
 * Frontend Integration:
 * - frontend/src/services/instructorService.js (v3.0.0 compatibility)
 * - frontend/src/utils/courseDataSync.js (access levels and validation)
 * - frontend/src/utils/validation.js (module validation logic)
 * - frontend/src/components/common/FormInput.jsx (form input components)
 * - frontend/src/components/common/DurationInput.jsx (duration input component)
 */

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Alert from '../../components/common/Alert';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Container from '../../components/common/Container';
import DurationInput from '../../components/common/DurationInput';
import { ContentCreationErrorBoundary } from '../../components/common/errorBoundaries';
import FormInput from '../../components/common/FormInput';
import LoadingScreen from '../../components/common/LoadingScreen';
import { useAuth } from '../../contexts/AuthContext';
import instructorService from '../../services/instructorService';
import { ACCESS_LEVELS, ACCESS_LEVEL_LABELS } from '../../utils/courseDataSync';
import { formatDuration } from '../../utils/formatDuration';
import { validateModule } from '../../utils/validation';

const CreateModulePage = () => {
  const navigate = useNavigate();
  const { courseSlug, courseIdentifier } = useParams();
  const { currentUser, isAuthenticated, isInstructor } = useAuth();

  // Use courseSlug if available, otherwise use courseIdentifier
  const coursePath = courseSlug || courseIdentifier;

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    order: 1,
    duration: '',
    duration_minutes: 0,
    access_level: ACCESS_LEVELS.REGISTERED,
    is_published: false,
  });

  // UI state
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);
  const [courseLoading, setCourseLoading] = useState(true);
  const [courseData, setCourseData] = useState(null);

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

  // Validate course identifier
  useEffect(() => {
    if (!coursePath) {
      navigate('/instructor/courses');
    }
  }, [coursePath, navigate]);

  // Fetch course data and set initial values
  useEffect(() => {
    const fetchCourse = async () => {
      if (!coursePath || !isAuthenticated) return;

      try {
        setCourseLoading(true);
        setSubmitError('');

        // Get course by slug or identifier
        const response = await instructorService.getCourseBySlug(coursePath);

        // Handle different response formats
        let courseData;
        if (response.data) {
          courseData = Array.isArray(response.data) ? response.data[0] : response.data;
        } else {
          courseData = Array.isArray(response) ? response[0] : response;
        }

        if (!courseData) {
          throw new Error("Course not found");
        }

        console.log("CreateModulePage: Loaded course data:", courseData);
        setCourseData(courseData);

        // Set initial order based on existing modules
        try {
          const modulesResponse = await instructorService.getModules(courseData.id);
          const moduleCount = modulesResponse.data?.length || modulesResponse.length || 0;
          setFormData(prev => ({
            ...prev,
            order: moduleCount + 1,
          }));
        } catch (err) {
          console.error("Failed to fetch modules for order calculation:", err);
          // Continue with default order = 1
        }

      } catch (err) {
        console.error("Failed to fetch course:", err);
        setSubmitError(
          err.message || "Failed to load course data. Please try again."
        );
      } finally {
        setCourseLoading(false);
      }
    };

    fetchCourse();
  }, [coursePath, isAuthenticated]);

  // Handle form input changes
  const handleInputChange = e => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;

    setFormData(prev => ({
      ...prev,
      [name]: newValue,
    }));

    // Clear field-specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }

    // Clear success message when user makes changes
    if (success) {
      setSuccess(false);
    }
  };

  // Handle duration input change
  const handleDurationChange = (minutes) => {
    setFormData(prev => ({
      ...prev,
      duration_minutes: minutes,
    }));

    // Clear duration error
    if (errors.duration_minutes) {
      setErrors(prev => ({
        ...prev,
        duration_minutes: '',
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async e => {
    e.preventDefault();

    if (!formData.title.trim()) {
      setErrors({ title: "Module title is required" });
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');
    setErrors({});

    try {
      // Validate form data
      const validationErrors = validateModule(formData);
      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        setIsSubmitting(false);
        return;
      }

      // Prepare module data for API
      const moduleData = {
        course: courseData.id,
        title: formData.title.trim(),
        description: formData.description.trim(),
        order: parseInt(formData.order) || 1,
        duration: formData.duration || null,
        duration_minutes: formData.duration_minutes || 0,
        access_level: formData.access_level,
        is_published: formData.is_published,
      };

      // Create module
      const response = await instructorService.createModule(moduleData);

      setSuccess(true);

      // Navigate to course detail page with success message
      setTimeout(() => {
        if (response?.id) {
          navigate(`/instructor/courses/${coursePath}`, {
            state: {
              message: `Module "${formData.title}" created successfully!`,
              messageType: 'success',
            },
          });
        } else {
          navigate(`/instructor/courses/${coursePath}`);
        }
      }, 2000);

    } catch (error) {
      console.error('Error creating module:', error);

      if (error.response?.data) {
        // Handle validation errors from backend
        if (
          typeof error.response.data === 'object' &&
          error.response.data.errors
        ) {
          // Backend validation errors in standard format
          setErrors(error.response.data.errors);
        } else if (typeof error.response.data === 'object') {
          // Field-specific errors from Django serializer
          setErrors(error.response.data);
        } else {
          setSubmitError(
            error.response.data.message ||
            error.response.data ||
            'Failed to create module. Please try again.'
          );
        }
      } else if (error.message) {
        setSubmitError(error.message);
      } else {
        setSubmitError(
          'Network error. Please check your connection and try again.'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle cancel action
  const handleCancel = () => {
    navigate(`/instructor/courses/${coursePath}`);
  };

  // Show loading screen while authentication is being determined or course is loading
  if (isAuthenticated === null || courseLoading) {
    return (
      <Container>
        <LoadingScreen message="Loading course data..." />
      </Container>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Container>
        {/* Breadcrumb Navigation */}
        <nav className="flex mb-8" aria-label="Breadcrumb">
          <ol className="flex items-center space-x-4 flex-wrap">
            <li>
              <button
                onClick={() => navigate('/instructor/dashboard')}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                Dashboard
              </button>
            </li>
            <li>
              <span className="text-gray-400">/</span>
            </li>
            <li>
              <button
                onClick={() => navigate('/instructor/courses')}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                Courses
              </button>
            </li>
            <li>
              <span className="text-gray-400">/</span>
            </li>
            <li>
              <button
                onClick={() => navigate(`/instructor/courses/${coursePath}`)}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                {courseData?.title || coursePath}
              </button>
            </li>
            <li>
              <span className="text-gray-400">/</span>
            </li>
            <li className="text-gray-900 font-medium">New Module</li>
          </ol>
        </nav>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Create New Module
          </h1>
          {courseData && (
            <p className="mt-2 text-gray-600">
              Adding module to course: <strong>{courseData.title}</strong>
            </p>
          )}
          <p className="mt-1 text-gray-600">
            Add a new module to organize your course content into logical sections.
          </p>
        </div>

        {/* Error Alert */}
        {submitError && (
          <Alert type="error" className="mb-6">
            {submitError}
          </Alert>
        )}

        {/* Success Alert */}
        {success && (
          <Alert type="success" className="mb-6">
            Module created successfully! Redirecting to course page...
          </Alert>
        )}

        {/* Validation Errors Summary */}
        {Object.keys(errors).length > 0 && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-yellow-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Please fix the following issues:
                </h3>
                <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
                  {Object.entries(errors).map(([field, message]) => (
                    <li key={field}>{message}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Main Form */}
        <Card className="max-w-4xl mx-auto">
          <div className="px-6 py-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Module Title */}
              <FormInput
                id="title"
                name="title"
                label="Module Title *"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Enter a descriptive title for your module"
                error={errors.title}
                helperText={`${formData.title.length}/200 characters`}
                required
                maxLength={200}
              />

              {/* Module Description */}
              <div className="form-group">
                <label htmlFor="description" className="block text-gray-700 font-medium mb-1">
                  Module Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows={4}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Provide a brief description of what this module covers"
                  maxLength={1000}
                />
                <p className="mt-1 text-sm text-gray-500">
                  {formData.description.length}/1000 characters
                </p>
                {errors.description && (
                  <p className="mt-1 text-sm text-red-500">{errors.description}</p>
                )}
              </div>

              {/* Module Order and Duration Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Module Order */}
                <FormInput
                  id="order"
                  name="order"
                  type="number"
                  label="Module Order"
                  value={formData.order}
                  onChange={handleInputChange}
                  min="1"
                  placeholder="1"
                  error={errors.order}
                  helperText="Position of this module in the course sequence"
                />

                {/* Estimated Duration */}
                <div>
                  <label className="block text-gray-700 font-medium mb-1">
                    Estimated Duration
                  </label>
                  <div className="space-y-2">
                    {/* Simple duration input for backward compatibility */}
                    <FormInput
                      id="duration"
                      name="duration"
                      value={formData.duration}
                      onChange={handleInputChange}
                      placeholder="e.g., 2 hours"
                      error={errors.duration}
                    />

                    {/* Advanced duration input if component is available */}
                    {DurationInput && (
                      <DurationInput
                        id="duration_minutes"
                        name="duration_minutes"
                        label="Precise Duration (minutes)"
                        value={formData.duration_minutes}
                        onChange={handleDurationChange}
                        error={errors.duration_minutes}
                        helperText="How long students should expect to spend on this module"
                      />
                    )}

                    {formData.duration_minutes > 0 && (
                      <p className="text-sm text-gray-500">
                        Duration: {formatDuration ? formatDuration(formData.duration_minutes) : `${formData.duration_minutes} minutes`}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Access Level */}
              {ACCESS_LEVELS && (
                <div className="form-group">
                  <label htmlFor="access_level" className="block text-gray-700 font-medium mb-1">
                    Access Level
                  </label>
                  <select
                    id="access_level"
                    name="access_level"
                    value={formData.access_level}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value={ACCESS_LEVELS.GUEST}>
                      {ACCESS_LEVEL_LABELS[ACCESS_LEVELS.GUEST]}
                    </option>
                    <option value={ACCESS_LEVELS.REGISTERED}>
                      {ACCESS_LEVEL_LABELS[ACCESS_LEVELS.REGISTERED]}
                    </option>
                    <option value={ACCESS_LEVELS.PREMIUM}>
                      {ACCESS_LEVEL_LABELS[ACCESS_LEVELS.PREMIUM]}
                    </option>
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Who can access this module content
                  </p>
                  {errors.access_level && (
                    <p className="mt-1 text-sm text-red-500">{errors.access_level}</p>
                  )}
                </div>
              )}

              {/* Publish Status */}
              <div className="form-group">
                <label className="block text-gray-700 font-medium mb-1">
                  Publish Status
                </label>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_published"
                    name="is_published"
                    checked={formData.is_published}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label
                    htmlFor="is_published"
                    className="ml-2 block text-sm text-gray-700"
                  >
                    Publish immediately
                  </label>
                </div>
                <p className="mt-1 text-sm text-gray-500">
                  If unchecked, this module will be saved as a draft
                </p>
                {errors.is_published && (
                  <p className="mt-1 text-sm text-red-500">
                    {errors.is_published}
                  </p>
                )}
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSubmitting || !formData.title.trim()}
                  isLoading={isSubmitting}
                >
                  {isSubmitting ? 'Creating Module...' : 'Create Module'}
                </Button>
              </div>

              {/* Form Help Text */}
              <div className="text-center mt-4">
                <p className="text-sm text-gray-500">
                  Modules are containers for lessons and other content in your course.
                  Good modules have clear titles and logical organization.
                </p>
              </div>
            </form>
          </div>
        </Card>
      </Container>
    </div>
  );
};

// Export with Error Boundary wrapper for production stability
export default function CreateModulePageWithErrorBoundary() {
  const navigate = useNavigate();

  const handleNavigateBack = () => {
    navigate(-1); // Go back to previous page
  };

  const handleSaveContent = () => {
    // Trigger auto-save functionality if available
    const event = new CustomEvent('triggerModuleAutoSave');
    window.dispatchEvent(event);
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Module Creation Error:', { error, errorInfo, context });
    // Could send to error tracking service here
  };

  return (
    <ContentCreationErrorBoundary
      onNavigateBack={handleNavigateBack}
      onSaveContent={handleSaveContent}
      onError={handleError}
    >
      <CreateModulePage />
    </ContentCreationErrorBoundary>
  );
}
