import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
// Direct imports to avoid casing issues
import Alert from '../../components/common/Alert';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import DurationInput from '../../components/common/DurationInput';
import FormInput from '../../components/common/FormInput';
import LoadingScreen from '../../components/common/LoadingScreen';
import MainLayout from '../../components/layouts/MainLayout';
import instructorService from '../../services/instructorService';
import authPersist from '../../utils/authPersist';
import { formatDuration } from '../../utils/formatDuration';
// Enhanced data synchronization utilities
import {
  ACCESS_LEVELS,
  ACCESS_LEVEL_LABELS,
  DIFFICULTY_LEVELS,
  EDITOR_MODES,
  createModeSwitcher,
  normalizeAccessLevel,
  normalizeCourseData,
} from '../../utils/courseDataSync';

const EditCoursePage = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [courseData, setCourseData] = useState(null);
  const [editorMode, setEditorMode] = useState(EDITOR_MODES.TRADITIONAL);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const courseSlugState = authPersist.getCourseSlug();
  // Fetch course data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await instructorService.getCourseById(courseId);

        // Normalize the course data using our unified utilities
        const normalizedData = normalizeCourseData({
          courseData: data,
          modules: data.modules || [],
        });

        setCourseData(normalizedData.courseData);
        setEditorMode(data.editorMode || EDITOR_MODES.TRADITIONAL);
      } catch (err) {
        console.error('Failed to fetch course data:', err);
        setError(err.message || 'Failed to load course data');
      } finally {
        setIsLoading(false);
      }
    };

    if (courseId) {
      fetchData();
    }
  }, [courseId]);

  // Enhanced mode switching and data synchronization
  const modeSwitcher = createModeSwitcher({
    currentData: {
      courseData: courseData,
      modules: [], // Traditional editor doesn't handle modules directly
    },
    onModeSwitch: (newMode, synchronizedData) => {
      // Update course data with normalized data
      setCourseData(prev => ({
        ...prev,
        ...synchronizedData.courseData,
      }));
    },
  });
  // Switch to wizard mode with data synchronization
  const switchToWizardMode = async () => {
    if (!courseData) {
      setError('No course data available to switch modes');
      return;
    }

    if (
      window.confirm(
        'Switch to wizard mode? Your current changes will be saved first.'
      )
    ) {
      try {
        setIsLoading(true);

        // First, save current progress
        const normalizedData = normalizeCourseData({
          courseData: courseData,
          modules: [],
        });

        await instructorService.updateCourse(
          courseId,
          normalizedData.courseData
        );

        // Then switch modes using our mode switcher utility
        modeSwitcher.switchMode(EDITOR_MODES.WIZARD, normalizedData);
        localStorage.setItem('editorMode', 'wizard');

        // Navigate to wizard
        if (courseData.slug) {
          navigate(`/instructor/courses/wizard/${courseData.slug}`);
        } else {
          navigate(`/instructor/courses/wizard`);
        }
      } catch (err) {
        console.error('Failed to save before switching modes:', err);
        // Still allow switch if user confirms
        if (window.confirm('Failed to save current changes. Switch anyway?')) {
          localStorage.setItem('editorMode', 'wizard');
          if (courseData.slug) {
            navigate(`/instructor/courses/wizard/${courseData.slug}`);
          } else {
            navigate(`/instructor/courses/wizard`);
          }
        }
      } finally {
        setIsLoading(false);
      }
    }
  }; // Form validation
  const validateForm = () => {
    const errors = {};

    if (!courseData?.title || courseData.title.trim() === '') {
      errors.title = 'Course title is required';
    } else if (courseData.title.length > 100) {
      errors.title = 'Course title must be 100 characters or less';
    }

    if (!courseData?.description || courseData.description.trim() === '') {
      errors.description = 'Course description is required';
    }

    if (
      courseData?.price &&
      (isNaN(parseFloat(courseData.price)) || parseFloat(courseData.price) < 0)
    ) {
      errors.price = 'Price must be a valid number greater than or equal to 0';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async e => {
    e.preventDefault();

    if (!courseData) {
      setError('No course data to save');
      return;
    }

    // Validate form before submission
    if (!validateForm()) {
      setError('Please fix the errors below before saving');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Normalize the course data before sending
      const normalizedData = normalizeCourseData({
        courseData: courseData,
        modules: [],
      });

      // Update the course
      await instructorService.updateCourse(courseId, normalizedData.courseData);

      // Show success and redirect
      setTimeout(() => {
        if (courseData.slug) {
          navigate(`/courses/${courseData.slug}`);
        } else {
          navigate(`/instructor/dashboard`);
        }
      }, 1000);
    } catch (err) {
      console.error('Failed to update course:', err);
      setError(err.message || 'Failed to save changes. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (error) {
    return <Alert message={error} type="error" />;
  }
  return (
    <MainLayout>
      <div className="py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="mb-6">
            <h1 className="text-3xl font-bold">Edit Course</h1>
            <p className="text-gray-600 mt-2">
              Update your course information and settings
            </p>
          </div>

          {/* Editor mode switch button */}
          <div className="flex justify-end mb-4">
            <Button
              color="primary"
              variant="outlined"
              onClick={switchToWizardMode}
            >
              Switch to Wizard Mode
            </Button>
          </div>

          {error && (
            <Alert type="error" className="mb-4">
              {error}
            </Alert>
          )}

          <Card className="p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {' '}
              {/* Course Title */}
              <FormInput
                label="Course Title"
                id="course-title"
                value={courseData?.title || ''}
                onChange={e =>
                  setCourseData({ ...courseData, title: e.target.value })
                }
                required
                placeholder="e.g., Complete Web Development Bootcamp"
                maxLength={100}
                helpText="Clear, specific titles perform better. (max 100 characters)"
                error={formErrors.title}
              />
              {/* Course Subtitle */}
              <FormInput
                label="Course Subtitle"
                id="course-subtitle"
                value={courseData?.subtitle || ''}
                onChange={e =>
                  setCourseData({ ...courseData, subtitle: e.target.value })
                }
                placeholder="e.g., Learn HTML, CSS, JavaScript, React, Node.js and more!"
                maxLength={150}
                helpText="A brief, compelling description of what students will learn. (max 150 characters)"
              />
              {/* Course Description */}
              <FormInput
                label="Description"
                id="description"
                value={courseData?.description || ''}
                onChange={e =>
                  setCourseData({ ...courseData, description: e.target.value })
                }
                required
                placeholder="Describe what students will learn in this course"
                multiline
                rows={4}
                helpText="Provide a detailed description of your course content and what students will achieve"
                error={formErrors.description}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Course Level with Unified Terminology */}
                <div>
                  <label
                    htmlFor="level"
                    className="block text-gray-700 font-medium mb-1"
                  >
                    Course Level
                  </label>
                  <select
                    id="level"
                    value={courseData?.level || 'beginner'}
                    onChange={e =>
                      setCourseData({ ...courseData, level: e.target.value })
                    }
                    className="w-full p-3 rounded-md border border-gray-300"
                  >
                    {DIFFICULTY_LEVELS.map(level => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Setting the right level helps students find your course
                  </p>
                </div>

                {/* Default Access Level with Unified Terminology */}
                <div>
                  <label
                    htmlFor="access_level"
                    className="block text-gray-700 font-medium mb-1"
                  >
                    Default Access Level
                  </label>
                  <select
                    id="access_level"
                    value={
                      normalizeAccessLevel(courseData?.access_level) || 'guest'
                    }
                    onChange={e =>
                      setCourseData({
                        ...courseData,
                        access_level: e.target.value,
                      })
                    }
                    className="w-full p-3 rounded-md border border-gray-300"
                  >
                    {ACCESS_LEVELS.map(level => (
                      <option key={level.value} value={level.value}>
                        {ACCESS_LEVEL_LABELS[level.value] || level.label}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-sm text-gray-500">
                    Set the default access level for new lessons in this course
                  </p>
                </div>
                {/* Price */}
                <div>
                  <label
                    htmlFor="price"
                    className="block text-gray-700 font-medium mb-1"
                  >
                    Price (USD)
                  </label>
                  <input
                    id="price"
                    name="price"
                    type="number"
                    min="0"
                    step="0.01"
                    value={courseData?.price || ''}
                    onChange={e =>
                      setCourseData({ ...courseData, price: e.target.value })
                    }
                    className={`w-full p-3 rounded-md border ${
                      formErrors.price ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="0.00"
                  />
                  {formErrors.price && (
                    <p className="mt-1 text-sm text-red-500">
                      {formErrors.price}
                    </p>
                  )}
                  <p className="mt-1 text-sm text-gray-500">
                    Set to 0 for free courses
                  </p>
                </div>

                {/* Duration */}
                <DurationInput
                  label="Estimated Duration"
                  value={courseData?.duration_minutes || 0}
                  onChange={minutes =>
                    setCourseData({ ...courseData, duration_minutes: minutes })
                  }
                  placeholder="Select course duration"
                />
                {courseData?.duration_minutes > 0 && (
                  <p className="mt-1 text-sm text-gray-500">
                    Duration: {formatDuration(courseData.duration_minutes)}
                  </p>
                )}
              </div>
              {/* Certificate Option */}
              <div className="flex items-center">
                <input
                  id="has_certificate"
                  name="has_certificate"
                  type="checkbox"
                  checked={courseData?.has_certificate || false}
                  onChange={e =>
                    setCourseData({
                      ...courseData,
                      has_certificate: e.target.checked,
                    })
                  }
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="has_certificate" className="ml-2 text-gray-700">
                  This course offers a completion certificate
                </label>
              </div>
              {/* Publishing Status */}
              <div className="flex items-center">
                <input
                  id="is_published"
                  name="is_published"
                  type="checkbox"
                  checked={courseData?.is_published || false}
                  onChange={e =>
                    setCourseData({
                      ...courseData,
                      is_published: e.target.checked,
                    })
                  }
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="is_published" className="ml-2 text-gray-700">
                  Publish this course (make it visible to students)
                </label>
              </div>
              {/* Form Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 mt-6">
                <Button
                  type="button"
                  variant="outlined"
                  color="secondary"
                  onClick={() =>
                    navigate(`/courses/${courseData?.slug || courseId}`)
                  }
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default EditCoursePage;
