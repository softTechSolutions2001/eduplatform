// fmt: off
// isort: skip_file
// Timestamp: 2024-06-15 - Tag Input component for managing keyword tags

import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * TagInput Component
 *
 * A flexible component for managing tags/keywords with:
 * - Add tags by typing and pressing Enter
 * - Remove tags by clicking X
 * - Custom styling options
 * - Validation support
 * - Accessible design
 */
const TagInput = ({
  value = [],
  onChange,
  placeholder = 'Add a tag...',
  label,
  error,
  helpText,
  maxTags = null,
  className = '',
  tagClassName = '',
  disabled = false,
  required = false,
}) => {
  const [inputValue, setInputValue] = useState('');

  // Handle input change
  const handleInputChange = e => {
    setInputValue(e.target.value);
  };

  // Handle keydown for adding tags
  const handleKeyDown = e => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault(); // Prevent form submission

      // Don't add if we've reached the max number of tags
      if (maxTags !== null && value.length >= maxTags) {
        return;
      }

      // Don't add duplicates
      if (!value.includes(inputValue.trim())) {
        onChange([...value, inputValue.trim()]);
      }

      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      // Remove last tag when backspace is pressed on empty input
      onChange(value.slice(0, -1));
    }
  };

  // Remove a tag
  const removeTag = index => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className={`${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div
        className={`flex flex-wrap gap-2 p-2 border rounded-md bg-white
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${disabled ? 'bg-gray-100 opacity-70' : ''}
        `}
      >
        {/* Display existing tags */}
        {value.map((tag, index) => (
          <div
            key={index}
            className={`flex items-center bg-primary-100 text-primary-800 rounded-full px-3 py-1 text-sm
              ${tagClassName}
            `}
          >
            <span>{tag}</span>
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(index)}
                className="ml-1.5 text-primary-500 hover:text-primary-700 focus:outline-none"
                aria-label={`Remove tag ${tag}`}
              >
                <svg
                  className="h-3.5 w-3.5"
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
            )}
          </div>
        ))}

        {/* Input for new tags */}
        {(!maxTags || value.length < maxTags) && !disabled && (
          <input
            type="text"
            className="flex-grow border-0 p-0.5 focus:ring-0 focus:outline-none text-sm"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={value.length === 0 ? placeholder : ''}
            disabled={disabled}
          />
        )}
      </div>

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}

      {helpText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helpText}</p>
      )}

      {maxTags !== null && (
        <p className="mt-1 text-xs text-gray-500">
          {value.length} of {maxTags} tags used
        </p>
      )}
    </div>
  );
};

TagInput.propTypes = {
  /** Array of current tags */
  value: PropTypes.arrayOf(PropTypes.string),
  /** Callback fired when tags change */
  onChange: PropTypes.func.isRequired,
  /** Placeholder text for input */
  placeholder: PropTypes.string,
  /** Label for the input */
  label: PropTypes.string,
  /** Error message */
  error: PropTypes.string,
  /** Help text displayed below the input */
  helpText: PropTypes.string,
  /** Maximum number of tags allowed (null for unlimited) */
  maxTags: PropTypes.number,
  /** Additional className for the container */
  className: PropTypes.string,
  /** Additional className for each tag */
  tagClassName: PropTypes.string,
  /** Whether the input is disabled */
  disabled: PropTypes.bool,
  /** Whether the input is required */
  required: PropTypes.bool,
};

export default TagInput;
