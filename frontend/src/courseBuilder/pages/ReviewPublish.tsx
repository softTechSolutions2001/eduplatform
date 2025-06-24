import React from 'react';
import { useNavigate } from 'react-router-dom';
import courseBuilderAPI from '../api/courseBuilderAPI';
import { useDirtyPrompt } from '../hooks/useDirtyPrompt';
import { useCourseStore } from '../store/courseSlice';

interface CourseValidationError {
  field: string;
  message: string;
}

/**
 * Function to perform an immediate synchronous save
 * This doesn't use debouncing like the regular autosave
 */
const saveImmediately = async (course: any) => {
  if (!course || !course.slug) {
    throw new Error('Course slug is required for saving');
  }

  // Prepare course data for update
  const courseData = new FormData();
  courseData.append('title', course.title || '');
  courseData.append('description', course.description || '');

  if (course.image instanceof File) {
    courseData.append('image', course.image);
  }

  // Add other course fields as needed
  if (course.category)
    courseData.append('category_id', course.category.toString());
  if (course.price) courseData.append('price', course.price.toString());
  if (course.skillLevel) courseData.append('level', course.skillLevel);

  // Stringify the modules array with proper nesting
  courseData.append('modules_json', JSON.stringify(course.modules));

  // Send course data to server
  return await courseBuilderAPI.updateCourse(course.slug, courseData);
};

const ReviewPublishPage: React.FC = () => {
  const course = useCourseStore(state => state.course);
  const navigate = useNavigate();
  const [isPublishing, setIsPublishing] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);
  const [errors, setErrors] = React.useState<CourseValidationError[]>([]);

  // Get necessary store actions
  const { markClean, setLastSaved, setCourse } = useCourseStore();

  // Reset dirty prompt when publishing
  const { resetDirtyState } = useDirtyPrompt({
    bypassConditions: () => isPublishing || isSaving,
  });

  if (!course) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-4">No course loaded</h2>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => navigate(-1)}
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const validateCourse = () => {
    const validationErrors: CourseValidationError[] = [];

    // Basic course validation
    if (!course.title || course.title.trim() === '') {
      validationErrors.push({
        field: 'title',
        message: 'Course title is required',
      });
    }

    if (!course.description || course.description.trim() === '') {
      validationErrors.push({
        field: 'description',
        message: 'Course description is required',
      });
    }

    // Modules validation
    if (!course.modules || course.modules.length === 0) {
      validationErrors.push({
        field: 'modules',
        message: 'At least one module is required',
      });
    } else {
      // Check each module
      course.modules.forEach((module, moduleIndex) => {
        if (!module.title || module.title.trim() === '') {
          validationErrors.push({
            field: `modules[${moduleIndex}].title`,
            message: `Module ${moduleIndex + 1} must have a title`,
          });
        }

        // Lessons validation
        if (!module.lessons || module.lessons.length === 0) {
          validationErrors.push({
            field: `modules[${moduleIndex}].lessons`,
            message: `Module "${module.title || moduleIndex + 1}" must have at least one lesson`,
          });
        } else {
          // Check each lesson
          module.lessons.forEach((lesson, lessonIndex) => {
            if (!lesson.title || lesson.title.trim() === '') {
              validationErrors.push({
                field: `modules[${moduleIndex}].lessons[${lessonIndex}].title`,
                message: `Lesson ${lessonIndex + 1} in module "${module.title || moduleIndex + 1}" must have a title`,
              });
            }
          });
        }
      });
    }

    return validationErrors;
  };

  const handlePublish = async () => {
    const validationErrors = validateCourse();
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      window.scrollTo(0, 0);
      return;
    }

    try {
      setIsPublishing(true);

      // Ensure course is saved before publishing
      if (useCourseStore.getState().isDirty) {
        try {
          setIsSaving(true);
          console.log('Saving course changes before publishing...');
          const updatedCourse = await saveImmediately(course);

          // Update course in store with latest data from server
          setCourse(updatedCourse);

          // Mark as clean and update last saved timestamp
          setLastSaved(new Date());
          markClean();

          console.log('Course saved successfully before publishing');
        } catch (saveError) {
          console.error('Error saving course before publishing:', saveError);
          setErrors([
            {
              field: 'general',
              message:
                'Failed to save course changes before publishing. Please try again.',
            },
          ]);
          setIsPublishing(false);
          setIsSaving(false);
          return;
        } finally {
          setIsSaving(false);
        }
      }

      // Now that we've ensured the course is saved, we can publish it
      if (course.slug) {
        await courseBuilderAPI.publish(course.slug);
        resetDirtyState();
        navigate(`/instructor/courses/${course.slug}`);
      } else {
        throw new Error('Course slug is required for publishing');
      }
    } catch (error) {
      console.error('Publishing error:', error);
      setErrors([
        {
          field: 'general',
          message: 'An error occurred while publishing the course',
        },
      ]);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 mt-8 mb-16">
      <h1 className="text-3xl font-bold mb-6">Review &amp; Publish Course</h1>

      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <h3 className="text-red-800 font-medium mb-2">
            Please fix the following issues:
          </h3>
          <ul className="list-disc pl-5 space-y-1">
            {errors.map((error, index) => (
              <li key={index} className="text-red-700">
                {error.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-semibold mb-4">Course Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="block text-gray-500 text-sm">Title</span>
            <span className="font-medium">{course.title}</span>
          </div>
          <div>
            <span className="block text-gray-500 text-sm">Price</span>
            <span className="font-medium">
              {course.price ? `$${course.price}` : 'Free'}
            </span>
          </div>
          <div>
            <span className="block text-gray-500 text-sm">Category</span>
            <span className="font-medium">
              {course.category || 'Uncategorized'}
            </span>
          </div>
          <div>
            <span className="block text-gray-500 text-sm">Skill Level</span>
            <span className="font-medium capitalize">
              {course.skillLevel || 'All levels'}
            </span>
          </div>
        </div>

        <div className="mt-4">
          <span className="block text-gray-500 text-sm">Description</span>
          <p className="whitespace-pre-wrap">{course.description}</p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-semibold mb-4">Course Structure</h2>
        <div className="space-y-4">
          {course.modules?.map((module, moduleIndex) => (
            <div
              key={module.id}
              className="border border-gray-200 rounded-lg p-4"
            >
              <h3 className="text-xl font-medium mb-2">
                Module {moduleIndex + 1}: {module.title}
              </h3>
              <div className="ml-4 space-y-2">
                {module.lessons?.map((lesson, lessonIndex) => (
                  <div
                    key={lesson.id}
                    className="p-2 border-l-2 border-blue-200"
                  >
                    <p className="font-medium">
                      Lesson {lessonIndex + 1}: {lesson.title}
                    </p>
                    {lesson.resources && lesson.resources.length > 0 && (
                      <div className="ml-4 mt-1">
                        <span className="text-sm text-gray-500">
                          Resources:
                        </span>
                        <ul className="list-disc ml-5">
                          {lesson.resources.map(resource => (
                            <li key={resource.id} className="text-sm">
                              {resource.title}
                              {resource.premium && (
                                <span className="ml-1 px-1 bg-amber-100 text-amber-800 text-xs rounded">
                                  Premium
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-between items-center mt-8">
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 border border-gray-300 rounded text-gray-600 hover:bg-gray-100"
          disabled={isPublishing || isSaving}
        >
          Back to Editor
        </button>

        <div className="flex space-x-4">
          <button
            onClick={handlePublish}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center"
            disabled={isPublishing || isSaving}
          >
            {isPublishing ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                {isSaving ? 'Saving...' : 'Publishing...'}
              </>
            ) : (
              'Publish Course'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewPublishPage;
