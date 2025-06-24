/**
 * File: frontend/src/pages/instructor/wizardSteps/CourseDetailsStep.jsx
 * Version: 2.2.0
 * Date: 2025-05-27 14:44:49
 * Author: mohithasanthanam
 * Last Modified: 2025-05-27 14:44:49 UTC
 *
 * Course Details Step Component - Enhanced with Proper Price Handling
 *
 * IMPROVEMENTS BASED ON TECHNICAL REVIEW:
 * 1. FIXED: Price field data type handling for FormData compatibility
 * 2. ADDED: Convert price values to strings before updating to prevent empty string conversion to 0
 * 3. IMPROVED: Enhanced validation for discount price (ensuring it's less than regular price)
 * 4. ADDED: Price error state management for better user feedback
 * 5. ENHANCED: Better handling of empty price values
 *
 * Step 2 of the Course Creation Wizard captures detailed course information:
 * - Comprehensive description (plain text)
 * - Skills students will learn (tags)
 * - Requirements/prerequisites (tags)
 * - Pricing information (with proper string conversion for FormData)
 * - Duration and certificate options
 *
 * Connected Components:
 * - CourseWizardContext.jsx - State management
 * - FormInput.jsx - Reusable form input component
 * - Card.jsx - Container component
 * - Button.jsx - Interactive button component
 * - TagInput.jsx - Tag management component
 * - Alert.jsx - Error display component
 */

// fmt: off
// isort: skip_file
// Timestamp: 2025-05-27 14:44:49 - Course Details Step (Step 2) of Course Creation Wizard

import { useState } from 'react';
import { formatDuration } from '../../../utils/formatDuration';
import { useCourseWizard } from '../CourseWizardContext';
// Direct imports to avoid casing issues
import Alert from '../../../components/common/Alert';
import Button from '../../../components/common/Button';
import Card from '../../../components/common/Card';
import DurationInput from '../../../components/common/DurationInput';
import FormInput from '../../../components/common/FormInput';

/**
 * Step 2: Course Details
 *
 * Captures the detailed information about the course:
 * - Comprehensive description (plain text instead of rich text)
 * - Skills students will learn (tags)
 * - Requirements/prerequisites (tags)
 * - Pricing information with proper FormData compatibility
 * - Duration and certificate options
 */
const CourseDetailsStep = () => {
  const { courseData, updateCourse, errors } = useCourseWizard();
  const [newSkill, setNewSkill] = useState('');
  const [newRequirement, setNewRequirement] = useState('');
  const [description, setDescription] = useState(courseData.description || '');
  // ADDED: State for price validation errors
  const [priceError, setPriceError] = useState('');

  // Handle description change (plain text)
  const handleDescriptionChange = e => {
    const value = e.target.value;
    setDescription(value);
    updateCourse({ description: value });
  };

  // IMPROVED: Enhanced price change handler with string conversion for FormData compatibility
  const handlePriceChange = e => {
    // Clear any previous price validation errors
    setPriceError('');
    const inputValue = e.target.value;

    // FIXED: Store empty values as empty string rather than converting to 0
    // This prevents the issue where empty strings become 0 in FormData
    if (inputValue === '') {
      updateCourse({ price: '' });
      return;
    }

    // FIXED: Convert to string representation of float for FormData compatibility
    // This ensures that when FormData.append() is called, we're passing a string
    const numericValue = parseFloat(inputValue);
    if (!isNaN(numericValue)) {
      // Store as string to maintain FormData compatibility
      updateCourse({ price: String(numericValue) });
    }
  };

  // ADDED: Enhanced discount price handler with validation
  const handleDiscountPriceChange = e => {
    // Clear any previous price validation errors
    setPriceError('');
    const inputValue = e.target.value;

    // FIXED: Store empty values as empty string
    if (inputValue === '') {
      updateCourse({ discount_price: '' });
      return;
    }

    // Convert to numeric for comparison, but store as string for FormData compatibility
    const numericValue = parseFloat(inputValue);
    const regularPrice = parseFloat(courseData.price || 0);

    if (!isNaN(numericValue)) {
      // ADDED: Validate that discount price is less than regular price
      if (numericValue >= regularPrice && regularPrice > 0) {
        setPriceError('Discount price must be less than regular price');
      }
      // Store as string for FormData compatibility
      updateCourse({ discount_price: String(numericValue) });
    }
  };

  // Handle skill tag additions and removals
  const addSkill = () => {
    if (!newSkill.trim()) return;

    const updatedSkills = [...(courseData.skills || []), newSkill.trim()];
    updateCourse({ skills: updatedSkills });
    setNewSkill('');
  };

  const removeSkill = index => {
    const updatedSkills = [...(courseData.skills || [])];
    updatedSkills.splice(index, 1);
    updateCourse({ skills: updatedSkills });
  };

  // Handle requirement tag additions and removals
  const addRequirement = () => {
    if (!newRequirement.trim()) return;

    const updatedRequirements = [
      ...(courseData.requirements || []),
      newRequirement.trim(),
    ];
    updateCourse({ requirements: updatedRequirements });
    setNewRequirement('');
  };

  const removeRequirement = index => {
    const updatedRequirements = [...(courseData.requirements || [])];
    updatedRequirements.splice(index, 1);
    updateCourse({ requirements: updatedRequirements });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold">Course Details</h2>
        <p className="text-gray-600 mt-1">
          Provide comprehensive information to showcase your course
        </p>
      </div>

      {/* Description Error Alert */}
      {errors.description && <Alert type="error">{errors.description}</Alert>}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main details column (2/3 width) */}
        <div className="md:col-span-2 space-y-4">
          {/* Course Description Section */}
          <Card className="overflow-visible">
            <h3 className="font-medium mb-3">Course Description</h3>
            <div className="mb-4">
              <textarea
                value={description}
                onChange={handleDescriptionChange}
                placeholder="Enter course description"
                rows={10}
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-500"
              />
              <p className="mt-2 text-sm text-gray-500">
                Provide a detailed description of your course. Include what
                students will learn, your teaching approach, and why they should
                take your course.
              </p>
            </div>
          </Card>

          {/* Skills/Learning Outcomes Section */}
          <Card className="overflow-visible">
            <h3 className="font-medium mb-3">What Students Will Learn</h3>
            <div className="space-y-3">
              <div className="flex space-x-2">
                <FormInput
                  id="new-skill"
                  placeholder="Add a learning outcome..."
                  value={newSkill}
                  onChange={e => setNewSkill(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && addSkill()}
                />
                <Button onClick={addSkill} variant="outlined" color="secondary">
                  Add
                </Button>
              </div>

              <div className="mt-3">
                {courseData.skills && courseData.skills.length > 0 ? (
                  <ul className="space-y-2">
                    {courseData.skills.map((skill, index) => (
                      <li
                        key={index}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
                      >
                        <span>{skill}</span>
                        <button
                          type="button"
                          onClick={() => removeSkill(index)}
                          className="text-red-500 hover:text-red-700 transition-colors"
                          title="Remove skill"
                        >
                          <svg
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm italic">
                    No learning outcomes added yet. Add at least 4-6 specific
                    outcomes.
                  </p>
                )}
              </div>
            </div>
          </Card>

          {/* Prerequisites/Requirements Section */}
          <Card className="overflow-visible">
            <h3 className="font-medium mb-3">Prerequisites & Requirements</h3>
            <div className="space-y-3">
              <div className="flex space-x-2">
                <FormInput
                  id="new-requirement"
                  placeholder="Add a course requirement..."
                  value={newRequirement}
                  onChange={e => setNewRequirement(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && addRequirement()}
                />
                <Button
                  onClick={addRequirement}
                  variant="outlined"
                  color="secondary"
                >
                  Add
                </Button>
              </div>

              <div className="mt-3">
                {courseData.requirements &&
                courseData.requirements.length > 0 ? (
                  <ul className="space-y-2">
                    {courseData.requirements.map((requirement, index) => (
                      <li
                        key={index}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
                      >
                        <span>{requirement}</span>
                        <button
                          type="button"
                          onClick={() => removeRequirement(index)}
                          className="text-red-500 hover:text-red-700 transition-colors"
                          title="Remove requirement"
                        >
                          <svg
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm italic">
                    No requirements added yet. Specify what students need to
                    know before starting.
                  </p>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar column (1/3 width) */}
        <div className="space-y-4">
          {/* Pricing & Certificates Section */}
          <Card className="overflow-visible">
            <h3 className="font-medium mb-3">Pricing & Certificates</h3>

            {/* Regular Price Input */}
            <div className="mb-4">
              <FormInput
                label="Price (USD)"
                id="price"
                type="number"
                min="0"
                step="0.01"
                // FIXED: Proper value handling to prevent undefined issues
                value={courseData.price !== undefined ? courseData.price : ''}
                onChange={handlePriceChange}
                placeholder="e.g., 49.99"
                error={errors.price}
              />
              <p className="mt-1 text-xs text-gray-500">
                Set your course's base price. You can add discounts later.
              </p>
            </div>

            {/* Discount Price Input */}
            <div className="mb-4">
              <FormInput
                label="Discount Price (Optional)"
                id="discount-price"
                type="number"
                min="0"
                step="0.01"
                // FIXED: Proper value handling to prevent undefined issues
                value={
                  courseData.discount_price !== undefined
                    ? courseData.discount_price
                    : ''
                }
                onChange={handleDiscountPriceChange}
                placeholder="e.g., 39.99"
                // ADDED: Display price validation error
                error={priceError}
              />
              <p className="mt-1 text-xs text-gray-500">
                If you want to offer a discount, set the promotional price here.
              </p>
            </div>

            {/* Certificate Checkbox */}
            <div className="flex items-center mt-4">
              <input
                type="checkbox"
                id="has-certificate"
                checked={courseData.has_certificate || false}
                onChange={e =>
                  updateCourse({ has_certificate: e.target.checked })
                }
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="has-certificate" className="ml-2 text-gray-700">
                Offer completion certificate
              </label>
            </div>
          </Card>

          {/* Course Timeline Section */}
          <Card className="overflow-visible">
            <h3 className="font-medium mb-3">Course Timeline</h3>
            {/* Duration Input */}
            <div className="mb-4">
              <DurationInput
                label="Estimated Duration"
                value={courseData.duration_minutes || 0}
                onChange={minutes =>
                  updateCourse({ duration_minutes: minutes })
                }
                placeholder="Select course duration"
              />
              {courseData.duration_minutes > 0 && (
                <p className="mt-1 text-sm text-gray-500">
                  Duration: {formatDuration(courseData.duration_minutes)}
                </p>
              )}
            </div>

            {/* Difficulty Level Selection */}
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-1">
                Difficulty Level
              </label>
              <div className="flex flex-wrap gap-2">
                {['beginner', 'intermediate', 'advanced', 'all_levels'].map(
                  level => (
                    <button
                      key={level}
                      type="button"
                      className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                        courseData.level === level
                          ? 'bg-primary-100 text-primary-800 border border-primary-300'
                          : 'bg-gray-100 text-gray-800 border border-gray-300 hover:bg-gray-200'
                      }`}
                      onClick={() => updateCourse({ level })}
                    >
                      {level.charAt(0).toUpperCase() +
                        level.slice(1).replace(/-/g, ' ')}
                    </button>
                  )
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CourseDetailsStep;
