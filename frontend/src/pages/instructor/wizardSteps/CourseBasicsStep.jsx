/**
 * File: frontend/src/pages/instructor/wizardSteps/CourseBasicsStep.jsx
 * Version: 2.3.0
 * Date: 2025-05-30 17:44:33
 * Author: mohithasanthanam (updated by sujibeautysalon)
 * Last Modified: 2025-05-30 17:44:33 UTC
 *
 * Course Basics Step Component - Enhanced with File Validation
 *
 * IMPROVEMENTS BASED ON TECHNICAL REVIEW:
 * 1. ADDED: Client-side validation for thumbnail file size (5MB limit)
 * 2. ADDED: MIME type validation for uploaded images (JPEG, PNG, GIF, WebP only)
 * 3. ADDED: User feedback for validation errors with clear error messages
 * 4. IMPROVED: Better file type restrictions in accept attribute
 * 5. ENHANCED: Updated thumbnail tips with file size and format information
 * 6. UPDATED: Course level terminology to match new naming convention
 *
 * Step 1 of the Course Creation Wizard captures essential course information:
 * - Course title (required)
 * - Course subtitle
 * - Category (required)
 * - Level (beginner, intermediate, expert)
 * - Thumbnail image with comprehensive validation
 *
 * Connected Components:
 * - CourseWizardContext.jsx - State management
 * - FormInput.jsx - Reusable form input component
 * - Card.jsx - Container component
 * - Tooltip.jsx - Help text component
 */

// fmt: off
// isort: skip_file
// Timestamp: 2025-05-30 17:44:33 - Course Basics Step (Step 1) of Course Creation Wizard

import React, { useState, useEffect, useCallback } from 'react';
import { useCourseWizard } from '../CourseWizardContext';
// Direct imports to avoid casing issues
import FormInput from '../../../components/common/FormInput';
import Card from '../../../components/common/Card';
import Tooltip from '../../../components/common/Tooltip';
import { categoryService } from '../../../services/api';
import instructorService from '../../../services/instructorService';
import { debounce } from '../../../utils/helpers';

/**
 * Step 1: Course Basics
 *
 * Captures the essential information needed to create a course:
 * - Course title (required)
 * - Course subtitle
 * - Category (required)
 * - Level (beginner, intermediate, expert)
 * - Thumbnail image with validation
 */
const CourseBasicsStep = () => {
  const { courseData, updateCourse, errors } = useCourseWizard();
  const [categories, setCategories] = useState([]);
  const [imagePreview, setImagePreview] = useState(null);
  // ADDED: State for image validation errors
  const [imageError, setImageError] = useState(null);

  // ADDED: Title validation state
  const [titleValidationState, setTitleValidationState] = useState({
    isValidating: false,
    isUnique: true,
    suggestions: [],
    showSuggestions: false,
  });
  const [debouncedTitle, setDebouncedTitle] = useState(courseData.title || '');

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await categoryService.getAllCategories();
        setCategories(data || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };

    fetchCategories();
  }, []);

  // ADDED: Debounced title validation
  const validateTitleUniqueness = useCallback(
    debounce(async title => {
      if (!title || title.trim().length < 3) {
        setTitleValidationState({
          isValidating: false,
          isUnique: true,
          suggestions: [],
          showSuggestions: false,
        });
        return;
      }

      setTitleValidationState(prev => ({ ...prev, isValidating: true }));
      try {
        const result = await instructorService.checkCourseTitle(title);
        setTitleValidationState({
          isValidating: false,
          isUnique: result.is_unique,
          suggestions: result.suggestions || [],
          showSuggestions:
            !result.is_unique &&
            Array.isArray(result.suggestions) &&
            result.suggestions.length > 0,
        });
      } catch (error) {
        console.error('Failed to validate title uniqueness:', error);
        setTitleValidationState({
          isValidating: false,
          isUnique: true,
          suggestions: [],
          showSuggestions: false,
        });
      }
    }, 600),
    []
  );

  // ADDED: Effect to validate title when it changes
  useEffect(() => {
    if (debouncedTitle && debouncedTitle.trim() !== courseData.title?.trim()) {
      validateTitleUniqueness(debouncedTitle);
    }
  }, [debouncedTitle, validateTitleUniqueness]);

  // IMPROVED: Enhanced image upload handler with comprehensive validation
  const handleImageChange = e => {
    const file = e.target.files[0];
    if (!file) return;

    // Clear previous validation errors
    setImageError(null);

    // ADDED: Client-side file size validation (5 MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setImageError('Image must be ≤ 5 MB');
      return;
    }

    // ADDED: MIME type validation for supported image formats
    const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowed.includes(file.type)) {
      setImageError('Only JPEG, PNG, GIF, WebP allowed');
      return;
    }

    // If validation passes, update course with the valid image
    updateCourse({ thumbnail: file });

    // Create image preview for user feedback
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // IMPROVED: Enhanced image removal handler that also clears validation errors
  const handleImageRemoval = () => {
    updateCourse({ thumbnail: null });
    setImagePreview(null);
    setImageError(null); // Clear any validation errors when removing image
  };
  // ADDED: Title change handler
  const handleTitleChange = e => {
    const newTitle = e.target.value;
    updateCourse({ title: newTitle });
    setDebouncedTitle(newTitle);
  };

  // ADDED: Title suggestion selection handler
  const selectSuggestion = suggestion => {
    updateCourse({ title: suggestion });
    setDebouncedTitle(suggestion);
    setTitleValidationState(prev => ({ ...prev, showSuggestions: false }));
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold">Course Basics</h2>
        <p className="text-gray-600 mt-1">
          Start with the fundamental information about your course
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main course information column */}
        <div className="md:col-span-2 space-y-4">
          {/* Course Title Input */}
          <div className="relative">
            <FormInput
              label="Course Title"
              id="course-title"
              value={courseData.title || ''}
              onChange={handleTitleChange}
              error={
                errors.title ||
                (!titleValidationState.isUnique &&
                !titleValidationState.showSuggestions
                  ? 'This course title is already taken.'
                  : null)
              }
              required
              placeholder="e.g., Complete Web Development Bootcamp"
              maxLength={100}
              helpText="Clear, specific titles perform better. (max 100 characters)"
            />

            {/* Title validation indicator */}
            {courseData.title && courseData.title.length >= 3 && (
              <div className="absolute right-3 top-9">
                {titleValidationState.isValidating ? (
                  <div className="animate-pulse h-5 w-5">
                    <svg
                      className="animate-spin h-5 w-5 text-primary-500"
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
                  </div>
                ) : titleValidationState.isUnique ? (
                  <svg
                    className="h-5 w-5 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                ) : (
                  <svg
                    className="h-5 w-5 text-yellow-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                )}
              </div>
            )}

            {/* Title suggestions */}
            {titleValidationState.showSuggestions && (
              <div className="mt-2 p-3 bg-yellow-50 border border-yellow-300 rounded-md">
                <p className="text-sm font-medium text-yellow-800 mb-2">
                  This course title is already taken. Consider one of these
                  alternatives:
                </p>
                <div className="space-y-2">
                  {titleValidationState.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => selectSuggestion(suggestion)}
                      className="block w-full text-left px-3 py-2 text-sm bg-white hover:bg-yellow-100 rounded border border-yellow-200"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Course Subtitle Input */}
          <FormInput
            label="Course Subtitle"
            id="course-subtitle"
            value={courseData.subtitle || ''}
            onChange={e => updateCourse({ subtitle: e.target.value })}
            error={errors.subtitle}
            placeholder="e.g., Learn HTML, CSS, JavaScript, React, Node.js and more!"
            maxLength={150}
            helpText="A brief, compelling description of what students will learn. (max 150 characters)"
          />

          {/* Category Selection */}
          <div className="form-group">
            <label
              htmlFor="category"
              className="block text-gray-700 font-medium mb-1"
            >
              Category <span className="text-red-500">*</span>
            </label>
            <select
              id="category"
              value={courseData.category_id || ''}
              onChange={e => updateCourse({ category_id: e.target.value })}
              className={`w-full p-3 rounded-md border ${errors.category ? 'border-red-500' : 'border-gray-300'}`}
              aria-invalid={!!errors.category}
            >
              <option value="">Select a category</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-red-500">{errors.category}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Choose the most specific category that fits your course
            </p>
          </div>

          {/* Course Level Selection */}
          <div className="form-group">
            <label
              htmlFor="level"
              className="block text-gray-700 font-medium mb-1"
            >
              Course Level
            </label>
            <select
              id="level"
              value={courseData.level || 'beginner'}
              onChange={e => updateCourse({ level: e.target.value })}
              className="w-full p-3 rounded-md border border-gray-300"
            >
              <option value="beginner">
                Beginner - No experience required
              </option>
              <option value="intermediate">
                Intermediate - Some knowledge expected
              </option>
              <option value="expert">Expert - Experienced learners</option>
              <option value="all_levels">
                All Levels - Suitable for everyone
              </option>
            </select>
            <p className="mt-1 text-sm text-gray-500">
              Setting the right level helps students find your course
            </p>
          </div>
        </div>

        {/* Thumbnail Upload Column */}
        <div className="space-y-4">
          <Card className="p-4 overflow-visible">
            <h3 className="font-medium mb-2">Course Thumbnail</h3>
            <p className="text-sm text-gray-600 mb-4">
              Upload an eye-catching image that represents your course (16:9
              ratio recommended)
            </p>

            {/* Image Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center mb-4">
              {/* Image Preview or Upload Placeholder */}
              {imagePreview || courseData.thumbnail ? (
                <div className="relative">
                  <img
                    src={
                      imagePreview ||
                      (typeof courseData.thumbnail === 'string'
                        ? courseData.thumbnail
                        : null)
                    }
                    alt="Thumbnail preview"
                    className="mx-auto max-h-40 object-contain"
                  />
                  {/* Remove Image Button */}
                  <button
                    type="button"
                    onClick={handleImageRemoval}
                    className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 transition-colors"
                    title="Remove image"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="py-8">
                  {/* Upload Icon */}
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
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  {/* IMPROVED: Updated file format text to include WebP and size limit */}
                  <p className="mt-2 text-sm text-gray-500">
                    PNG, JPG, GIF, or WebP (max 5MB)
                  </p>
                </div>
              )}

              {/* ADDED: Image validation error display */}
              {imageError && (
                <div className="mt-2 text-sm text-red-500 bg-red-50 p-2 rounded border border-red-200">
                  <div className="flex items-center">
                    {/* Error Icon */}
                    <svg
                      className="w-4 h-4 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {imageError}
                  </div>
                </div>
              )}

              {/* Hidden File Input */}
              <input
                type="file"
                id="thumbnail"
                // IMPROVED: More specific accept attribute with exact MIME types
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleImageChange}
                className="hidden"
              />

              {/* Upload Button */}
              <label
                htmlFor="thumbnail"
                className="mt-2 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
              >
                {imagePreview || courseData.thumbnail
                  ? 'Change Image'
                  : 'Upload Image'}
              </label>
            </div>

            {/* ENHANCED: Updated thumbnail tips with new validation information */}
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-blue-700 font-medium text-sm mb-1">
                Thumbnail Tips
              </h4>
              <ul className="text-xs text-blue-700 list-disc list-inside space-y-1">
                <li>Use high-quality, vibrant images</li>
                <li>Avoid too much text in the image</li>
                <li>Keep it simple and clear</li>
                <li>Recommended size: 1280×720 pixels</li>
                <li>
                  <strong>Maximum file size: 5MB</strong>
                </li>
                <li>
                  <strong>Supported formats: JPEG, PNG, GIF, WebP</strong>
                </li>
              </ul>
            </div>
          </Card>

          {/* Featured Course Checkbox */}
          <Tooltip content="Featured courses appear on the homepage and get more visibility">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is-featured"
                checked={courseData.is_featured || false}
                onChange={e => updateCourse({ is_featured: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="is-featured" className="ml-2 text-gray-700">
                Request featured placement
              </label>
            </div>
          </Tooltip>
        </div>
      </div>
    </div>
  );
};

export default CourseBasicsStep;
