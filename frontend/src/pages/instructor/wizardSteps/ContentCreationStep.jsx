/**
 * File: frontend/src/pages/instructor/wizardSteps/ContentCreationStep.jsx
 * Version: 2.3.0
 * Date: 2025-05-30 17:07:22
 * Author: mohithasanthanam
 * Last Modified: 2025-05-30 17:07:22 UTC
 * Modified by: sujibeautysalon
 *
 * Content Creation Step Component - Updated Subscription Terminology
 *
 * IMPROVEMENTS BASED ON TECHNICAL REVIEW:
 * 1. ADDED: Pre-save validation for guest access level content (suggestion 7-A)
 * 2. IMPROVED: Error handling with user-friendly messages and visual feedback
 * 3. ADDED: Validation to ensure guestContent is provided when access_level is 'guest'
 * 4. ENHANCED: Better form state management with error clearing
 * 5. IMPROVED: User experience with contextual warnings and help text
 * 6. PREPARED: Foundation for resource upload progress bar component (suggestion 7-B)
 * 7. UPDATED: Terminology from 'basic' → 'guest', 'intermediate' → 'registered' for consistency
 *
 * Step 4 of the Course Creation Wizard allows instructors to:
 * - Create lessons with tiered content (guest/registered/premium)
 * - Set access levels for different tiers with proper validation
 * - Add lesson details like duration and type
 * - Properly validate content requirements based on access level
 *
 * Connected Components:
 * - CourseWizardContext.jsx - State management and lesson operations
 * - Card.jsx - Container component
 * - Button.jsx - Interactive button component
 * - Alert.jsx - Error and warning display component
 * - FormInput.jsx - Form input component
 * - Tabs.jsx - Tab navigation component
 * - @tinymce/tinymce-react - Rich text editor
 */

// fmt: off
// isort: skip_file
// Timestamp: 2025-05-30 17:07:22 - Content Creation Step (Step 4) of Course Creation Wizard

import React, { useState } from 'react';
import { useCourseWizard } from '../CourseWizardContext';
// Direct imports to avoid casing issues
import Card from '../../../components/common/Card';
import Button from '../../../components/common/Button';
import Alert from '../../../components/common/Alert';
import FormInput from '../../../components/common/FormInput';
import Tabs from '../../../components/common/Tabs';
import { Editor } from '@tinymce/tinymce-react';
import { validateLessonData } from '../../../utils/validation';
import {
  ACCESS_LEVELS,
  ACCESS_LEVEL_LABELS,
  LESSON_TYPES,
  normalizeAccessLevel,
} from '../../../utils/courseDataSync';

/**
 * Step 4: Content Creation
 *
 * Allows instructors to add lessons to each module:
 * - Create lessons with tiered content (guest/registered/premium)
 * - Set access levels for different tiers with validation
 * - Add lesson details like duration and type
 * - Validate content requirements based on access level
 */
const ContentCreationStep = () => {
  const { modules, errors, addLesson, updateLesson, removeLesson } =
    useCourseWizard();
  const [selectedModule, setSelectedModule] = useState(
    modules.length > 0 ? modules[0].id : null
  );
  const [editingLesson, setEditingLesson] = useState(null);
  // ADDED: Form error state for validation feedback
  const [formError, setFormError] = useState('');
  const [lessonForm, setLessonForm] = useState({
    title: '',
    duration: '',
    type: LESSON_TYPES.VIDEO,
    content: '', // Premium (paid) content
    guest_content: '', // Guest preview content
    registered_content: '', // Registered user content
    access_level: ACCESS_LEVELS.REGISTERED,
    is_free_preview: false,
  });
  // Access level options using unified constants from courseDataSync
  const accessLevelOptions = [
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
  ];

  const lessonTypeOptions = [
    { value: LESSON_TYPES.VIDEO, label: 'Video' },
    { value: LESSON_TYPES.READING, label: 'Reading Material' },
    { value: LESSON_TYPES.INTERACTIVE, label: 'Interactive Content' },
    { value: LESSON_TYPES.QUIZ, label: 'Quiz' },
    { value: LESSON_TYPES.LAB, label: 'Lab Exercise' },
  ];

  // IMPROVED: Enhanced form change handler with error clearing
  const handleFormChange = (field, value) => {
    setFormError(''); // Clear any previous validation errors
    setLessonForm({
      ...lessonForm,
      [field]: value,
    });
  };

  // IMPROVED: Enhanced editor change handler with error clearing
  const handleEditorChange = (field, content) => {
    setFormError(''); // Clear any previous validation errors
    setLessonForm({
      ...lessonForm,
      [field]: content,
    });
  };
  // IMPROVED: Enhanced form reset with error clearing and unified constants
  const resetForm = () => {
    setFormError(''); // Clear any validation errors
    setLessonForm({
      title: '',
      duration: '',
      type: LESSON_TYPES.VIDEO,
      content: '',
      guest_content: '',
      registered_content: '',
      access_level: ACCESS_LEVELS.REGISTERED,
      is_free_preview: false,
    });
    setEditingLesson(null);
  };

  // ENHANCED: Improved lesson save handler with unified validation
  const handleSaveLesson = () => {
    // Clear any previous validation errors
    setFormError('');

    // Use unified validation logic
    const validationErrors = validateLessonData(lessonForm);
    if (validationErrors.length > 0) {
      setFormError(validationErrors[0]); // Show first error
      return;
    }

    // Validate module selection
    const module = modules.find(m => m.id === selectedModule);
    if (!module) {
      setFormError('No module selected');
      return;
    }
    // Prepare lesson data for saving with normalized access level
    const lessonData = {
      ...lessonForm,
      access_level: normalizeAccessLevel(lessonForm.access_level), // Ensure unified terminology
      order: module.lessons ? module.lessons.length + 1 : 1,
    };

    try {
      if (editingLesson) {
        // Update existing lesson
        updateLesson(selectedModule, editingLesson, lessonData);
      } else {
        // Create new lesson
        addLesson(selectedModule, lessonData);
      }

      // Reset form on successful save
      resetForm();
    } catch (error) {
      setFormError('Failed to save lesson. Please try again.');
      console.error('Error saving lesson:', error);
    }
  };
  // IMPROVED: Enhanced edit lesson handler with unified terminology and error clearing
  const handleEditLesson = lesson => {
    setFormError(''); // Clear any previous errors
    setEditingLesson(lesson.id);
    setLessonForm({
      title: lesson.title || '',
      duration: lesson.duration || '',
      type: lesson.type || LESSON_TYPES.VIDEO,
      content: lesson.content || '',
      guest_content: lesson.guest_content || lesson.basic_content || '', // Handle both naming conventions
      registered_content:
        lesson.registered_content || lesson.intermediate_content || '', // Handle both naming conventions
      access_level:
        normalizeAccessLevel(lesson.access_level) || ACCESS_LEVELS.REGISTERED, // Normalize access level
      is_free_preview: lesson.is_free_preview || false,
    });
  };

  // Delete a lesson with confirmation
  const handleDeleteLesson = lessonId => {
    if (window.confirm('Are you sure you want to delete this lesson?')) {
      removeLesson(selectedModule, lessonId);
      if (editingLesson === lessonId) {
        resetForm();
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold">Content Creation</h2>
        <p className="text-gray-600 mt-1">
          Add lessons, content tiers, and resources to your modules
        </p>
      </div>

      {/* Global Error Display */}
      {errors.lessons && <Alert type="error">{errors.lessons}</Alert>}

      {/* ADDED: Form validation error display */}
      {formError && <Alert type="error">{formError}</Alert>}

      {/* Main Content */}
      {modules.length === 0 ? (
        <Alert type="warning">
          You need to create modules first before adding content. Please go back
          to the previous step.
        </Alert>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left panel - Module selector and lessons list (1/3 width) */}
          <div className="md:col-span-1 space-y-4">
            {/* Module Selector */}
            <Card>
              <h3 className="font-medium mb-3">Modules</h3>
              <div className="space-y-2">
                {modules.map(module => (
                  <button
                    key={module.id}
                    onClick={() => setSelectedModule(module.id)}
                    className={`w-full text-left p-3 rounded-md transition-colors ${
                      selectedModule === module.id
                        ? 'bg-primary-50 border border-primary-200'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="font-medium">{module.title}</div>
                    <div className="text-sm text-gray-500">
                      {module.lessons && module.lessons.length > 0
                        ? `${module.lessons.length} lessons`
                        : 'No lessons yet'}
                    </div>
                  </button>
                ))}
              </div>
            </Card>

            {/* Lessons List */}
            {selectedModule && (
              <Card>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-medium">Lessons</h3>
                  <Button
                    color="primary"
                    size="small"
                    onClick={() => {
                      resetForm();
                      setEditingLesson(null);
                    }}
                  >
                    + Add Lesson
                  </Button>
                </div>

                {modules.find(m => m.id === selectedModule)?.lessons?.length >
                0 ? (
                  <div className="space-y-2">
                    {modules
                      .find(m => m.id === selectedModule)
                      .lessons.sort((a, b) => a.order - b.order)
                      .map(lesson => (
                        <div
                          key={lesson.id}
                          className={`p-3 rounded-md border transition-colors ${
                            editingLesson === lesson.id
                              ? 'border-primary-300 bg-primary-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex justify-between">
                            <div className="flex-1">
                              <div className="font-medium">{lesson.title}</div>
                              <div className="text-sm text-gray-500">
                                {lesson.type}{' '}
                                {lesson.duration && `• ${lesson.duration}`}
                              </div>
                              {lesson.is_free_preview && (
                                <span className="text-xs bg-green-100 text-green-800 rounded-full px-2 py-0.5 mt-1 inline-block">
                                  Free Preview
                                </span>
                              )}
                              {/* ADDED: Display access level information */}
                              <div className="text-xs mt-1 text-gray-500">
                                Access:{' '}
                                {accessLevelOptions
                                  .find(o => o.value === lesson.access_level)
                                  ?.label.split(' - ')[0] ||
                                  lesson.access_level}
                              </div>
                            </div>
                            <div className="flex space-x-1">
                              <button
                                onClick={() => handleEditLesson(lesson)}
                                className="p-1 text-gray-500 hover:text-primary-500 transition-colors"
                                title="Edit lesson"
                              >
                                <svg
                                  className="h-4 w-4"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                  />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDeleteLesson(lesson.id)}
                                className="p-1 text-gray-500 hover:text-red-500 transition-colors"
                                title="Delete lesson"
                              >
                                <svg
                                  className="h-4 w-4"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                  />
                                </svg>
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    No lessons created yet
                  </div>
                )}
              </Card>
            )}
          </div>

          {/* Right panel - Lesson editor (2/3 width) */}
          <div className="md:col-span-2">
            {selectedModule ? (
              <Card>
                <h3 className="font-medium mb-4">
                  {editingLesson ? 'Edit Lesson' : 'Create New Lesson'}
                </h3>

                <div className="space-y-4">
                  {/* Lesson Title */}
                  <FormInput
                    label="Lesson Title"
                    id="lesson-title"
                    value={lessonForm.title}
                    onChange={e => handleFormChange('title', e.target.value)}
                    placeholder="Enter lesson title"
                    required
                  />

                  {/* Lesson Type and Duration */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-700 font-medium mb-1">
                        Lesson Type
                      </label>
                      <select
                        value={lessonForm.type}
                        onChange={e => handleFormChange('type', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-500"
                      >
                        {lessonTypeOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <FormInput
                      label="Duration"
                      id="lesson-duration"
                      value={lessonForm.duration}
                      onChange={e =>
                        handleFormChange('duration', e.target.value)
                      }
                      placeholder="e.g., 15 minutes"
                    />
                  </div>

                  {/* Access Level Selection */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-1">
                      Access Level
                    </label>
                    <select
                      value={lessonForm.access_level}
                      onChange={e =>
                        handleFormChange('access_level', e.target.value)
                      }
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-500"
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
                    {/* ADDED: Contextual warning for guest access level */}
                    {lessonForm.access_level === ACCESS_LEVELS.GUEST && (
                      <p className="mt-1 text-sm text-amber-600 bg-amber-50 p-2 rounded border border-amber-200">
                        <strong>Note:</strong> Guest access level requires Guest
                        Content to be provided
                      </p>
                    )}
                  </div>

                  {/* Free Preview Checkbox */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_free_preview"
                      checked={lessonForm.is_free_preview}
                      onChange={e =>
                        handleFormChange('is_free_preview', e.target.checked)
                      }
                      className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <label
                      htmlFor="is_free_preview"
                      className="ml-2 text-gray-700"
                    >
                      Make this a free preview lesson (available to all users)
                    </label>
                  </div>

                  {/* ENHANCED: Tiered content editors with improved tab handling */}
                  <div className="mt-4">
                    <Tabs
                      tabs={[
                        { id: 'premium', label: 'Premium Content' },
                        { id: 'registered', label: 'Registered Content' },
                        { id: 'guest', label: 'Guest Content' },
                      ]}
                      // IMPROVED: Set initial tab based on access level
                      initialTab={
                        lessonForm.access_level === ACCESS_LEVELS.GUEST
                          ? 'guest'
                          : 'premium'
                      }
                    >
                      {/* Premium Content Tab */}
                      <Tabs.Panel id="premium">
                        <div className="mb-2">
                          <div className="flex justify-between mb-1">
                            <label className="block text-gray-700 font-medium">
                              Premium Content (Paid Subscribers)
                            </label>
                          </div>
                          <Editor
                            apiKey="your-tinymce-api-key" // Replace with your TinyMCE API key
                            value={lessonForm.content}
                            init={{
                              height: 300,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | \
                                alignleft aligncenter alignright alignjustify | \
                                bullist numlist outdent indent | removeformat | help',
                            }}
                            onEditorChange={content =>
                              handleEditorChange('content', content)
                            }
                          />
                        </div>
                      </Tabs.Panel>

                      {/* Registered Content Tab */}
                      <Tabs.Panel id="registered">
                        <div className="mb-2">
                          <div className="flex justify-between mb-1">
                            <label className="block text-gray-700 font-medium">
                              Registered Content (Logged-in Users)
                            </label>
                          </div>
                          <Editor
                            apiKey="your-tinymce-api-key"
                            value={lessonForm.registered_content}
                            init={{
                              height: 300,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | \
                                alignleft aligncenter alignright alignjustify | \
                                bullist numlist outdent indent | removeformat | help',
                            }}
                            onEditorChange={content =>
                              handleEditorChange('registered_content', content)
                            }
                          />
                        </div>
                      </Tabs.Panel>

                      {/* Guest Content Tab */}
                      <Tabs.Panel id="guest">
                        <div className="mb-2">
                          <div className="flex justify-between mb-1">
                            <label className="block text-gray-700 font-medium">
                              Guest Content (Preview for All Users)
                              {/* ADDED: Required indicator for guest access level */}
                              {lessonForm.access_level ===
                                ACCESS_LEVELS.GUEST && (
                                <span className="text-red-500 ml-1">*</span>
                              )}
                            </label>
                          </div>
                          <Editor
                            apiKey="your-tinymce-api-key"
                            value={lessonForm.guest_content}
                            init={{
                              height: 300,
                              menubar: false,
                              plugins: [
                                'advlist autolink lists link image charmap print preview anchor',
                                'searchreplace visualblocks code fullscreen',
                                'insertdatetime media table paste code help wordcount',
                              ],
                              toolbar:
                                'undo redo | formatselect | bold italic backcolor | \
                                alignleft aligncenter alignright alignjustify | \
                                bullist numlist outdent indent | removeformat | help',
                            }}
                            onEditorChange={content =>
                              handleEditorChange('guest_content', content)
                            }
                          />
                          {/* ADDED: Help text for guest content validation */}
                          {lessonForm.access_level === ACCESS_LEVELS.GUEST && (
                            <p className="mt-1 text-sm text-red-500">
                              Required for Guest access level
                            </p>
                          )}
                        </div>
                      </Tabs.Panel>
                    </Tabs>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-end space-x-3 mt-6">
                    <Button
                      variant="outlined"
                      color="secondary"
                      onClick={resetForm}
                    >
                      Cancel
                    </Button>

                    <Button
                      variant="contained"
                      color="primary"
                      disabled={!lessonForm.title}
                      onClick={handleSaveLesson}
                    >
                      {editingLesson ? 'Update Lesson' : 'Add Lesson'}
                    </Button>
                  </div>
                </div>
              </Card>
            ) : (
              /* No Module Selected State */
              <Card>
                <div className="text-center py-10">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    Select a module
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Choose a module from the list to add or edit lessons
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentCreationStep;
