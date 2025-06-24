/**
 * Basic Info Form - Course Creation Input Component
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * Collects essential course information including title, description,
 * category, level, and other basic metadata for AI generation.
 */

import { useEffect, useState } from 'react';
import { Alert, Button, FormInput } from '../../../components/common';
import DurationInput from '../../../components/common/DurationInput';
import { useDebounce } from '../../../hooks/useDebounce';
import { courseService } from '../../../services/api';
import { formatDuration } from '../../../utils/formatDuration';

const BasicInfoForm = ({ data, onChange, errors }) => {
  const [localData, setLocalData] = useState({
    title: '',
    description: '',
    category: '',
    level: 'beginner',
    targetAudience: '',
    estimatedDuration: '', // Legacy field for backward compatibility
    duration_minutes: 0, // New standardized field
    language: 'en',
    price: '',
    hasCertificate: false,
    ...data,
  });

  const [categories, setCategories] = useState([]);
  const [isCheckingTitle, setIsCheckingTitle] = useState(false);
  const [titleSuggestions, setTitleSuggestions] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);

  const debouncedTitle = useDebounce(localData.title, 500);

  // Load categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoadingCategories(true);
        const response = await courseService.getCategories();
        const { results } = response;
        setCategories(results || []);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        setCategories([]);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  // Check title uniqueness and generate suggestions
  useEffect(() => {
    const checkTitle = async () => {
      if (!debouncedTitle || debouncedTitle.length < 3) {
        setTitleSuggestions([]);
        return;
      }

      try {
        setIsCheckingTitle(true);
        // Check if title exists
        const existing = await courseService.checkTitleExists(debouncedTitle);

        if (existing) {
          // Generate alternative titles
          const suggestions = generateTitleSuggestions(debouncedTitle);
          setTitleSuggestions(suggestions);
        } else {
          setTitleSuggestions([]);
        }
      } catch (error) {
        console.error('Error checking title:', error);
      } finally {
        setIsCheckingTitle(false);
      }
    };

    checkTitle();
  }, [debouncedTitle]);

  // Generate title suggestions
  const generateTitleSuggestions = originalTitle => {
    const suggestions = [
      `${originalTitle} - Complete Guide`,
      `Master ${originalTitle}`,
      `${originalTitle} Fundamentals`,
      `Advanced ${originalTitle}`,
      `${originalTitle} for Beginners`,
    ];
    return suggestions.slice(0, 3);
  };

  // Handle input changes
  const handleChange = (field, value) => {
    const updatedData = { ...localData, [field]: value };
    setLocalData(updatedData);
    onChange(updatedData);
  };

  // Handle suggestion selection
  const handleSuggestionSelect = suggestion => {
    handleChange('title', suggestion);
    setTitleSuggestions([]);
  };

  // Auto-generate description based on title
  const generateDescription = () => {
    if (!localData.title) return;

    const template = `Learn ${localData.title} with this comprehensive course designed for ${localData.level} learners. Master key concepts and practical skills through hands-on exercises and real-world examples.`;
    handleChange('description', template);
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="relative">
        <FormInput
          label="Course Title"
          type="text"
          value={localData.title}
          onChange={e => handleChange('title', e.target.value)}
          error={errors.title}
          placeholder="Enter a compelling course title"
          required
          className="pr-10"
        />

        {isCheckingTitle && (
          <div className="absolute right-3 top-9">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
          </div>
        )}

        {/* Title Suggestions */}
        {titleSuggestions.length > 0 && (
          <Alert type="warning" className="mt-2">
            <div>
              <p className="text-sm font-medium">
                Similar title found. Consider these alternatives:
              </p>
              <div className="mt-2 space-y-1">
                {titleSuggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionSelect(suggestion)}
                    className="block text-sm text-blue-600 hover:text-blue-800 underline"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </Alert>
        )}
      </div>

      {/* Description */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Course Description *
          </label>
          {localData.title && (
            <Button
              variant="text"
              size="small"
              onClick={generateDescription}
              className="text-primary-600"
            >
              Auto-generate
            </Button>
          )}
        </div>
        <textarea
          value={localData.description}
          onChange={e => handleChange('description', e.target.value)}
          placeholder="Describe what students will learn and achieve in this course"
          rows={4}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
            errors.description ? 'border-red-300' : 'border-gray-300'
          }`}
          required
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description}</p>
        )}
      </div>

      {/* Category and Level Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            value={localData.category}
            onChange={e => handleChange('category', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              errors.category ? 'border-red-300' : 'border-gray-300'
            }`}
            required
          >
            <option value="">Select a category</option>
            {loadingCategories ? (
              <option disabled>Loading categories...</option>
            ) : (
              categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))
            )}
          </select>
          {errors.category && (
            <p className="mt-1 text-sm text-red-600">{errors.category}</p>
          )}
        </div>

        {/* Level */}
        <FormInput
          label="Difficulty Level"
          type="select"
          value={localData.level}
          onChange={e => handleChange('level', e.target.value)}
          options={[
            { value: 'beginner', label: 'Beginner' },
            { value: 'intermediate', label: 'Intermediate' },
            { value: 'advanced', label: 'Advanced' },
            { value: 'expert', label: 'Expert' },
          ]}
          required
        />
      </div>

      {/* Target Audience and Duration Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormInput
          label="Target Audience"
          type="text"
          value={localData.targetAudience}
          onChange={e => handleChange('targetAudience', e.target.value)}
          placeholder="e.g., Software developers, Marketing professionals"
        />

        <DurationInput
          label="Estimated Duration"
          value={localData.duration_minutes}
          onChange={minutes => handleChange('duration_minutes', minutes)}
          placeholder="Select course duration"
        />
      </div>

      {/* Pricing and Language Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormInput
          label="Price (USD)"
          type="number"
          value={localData.price}
          onChange={e => handleChange('price', e.target.value)}
          placeholder="0 for free course"
          min="0"
          step="0.01"
        />

        <FormInput
          label="Language"
          type="select"
          value={localData.language}
          onChange={e => handleChange('language', e.target.value)}
          options={[
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish' },
            { value: 'fr', label: 'French' },
            { value: 'de', label: 'German' },
            { value: 'zh', label: 'Chinese' },
            { value: 'ja', label: 'Japanese' },
          ]}
        />
      </div>

      {/* Certificate Option */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="hasCertificate"
          checked={localData.hasCertificate}
          onChange={e => handleChange('hasCertificate', e.target.checked)}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label
          htmlFor="hasCertificate"
          className="ml-2 block text-sm text-gray-900"
        >
          Offer completion certificate
        </label>
      </div>

      {/* Course Preview */}
      {localData.title && localData.description && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Course Preview
          </h3>
          <div className="space-y-2">
            <p>
              <span className="font-medium">Title:</span> {localData.title}
            </p>
            <p>
              <span className="font-medium">Level:</span> {localData.level}
            </p>
            {localData.targetAudience && (
              <p>
                <span className="font-medium">Target Audience:</span>{' '}
                {localData.targetAudience}
              </p>
            )}
            {(localData.duration_minutes > 0 ||
              localData.estimatedDuration) && (
              <p>
                <span className="font-medium">Duration:</span>{' '}
                {localData.duration_minutes > 0
                  ? formatDuration(localData.duration_minutes)
                  : localData.estimatedDuration}
              </p>
            )}
            <p>
              <span className="font-medium">Description:</span>
            </p>
            <p className="text-gray-700">{localData.description}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BasicInfoForm;
