/**
 * File: src/components/common/Spinner.jsx
 * Version: 1.0.1
 * Date: 2025-08-12 15:48:30
 * Author: cadsanthanam
 *
 * Spinner component for loading indicators
 * A reusable spinner component that can be used to indicate loading states
 * with customizable size and color options.
 */

import React from 'react';
import PropTypes from 'prop-types';

const Spinner = ({
  size = 'medium',
  color = 'primary',
  className = '',
  ...props
}) => {
  // Size classes
  const sizeMap = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  // Color classes
  const colorMap = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    white: 'text-white',
    gray: 'text-gray-600',
    black: 'text-gray-900',
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
  };

  const sizeClass = sizeMap[size] || sizeMap.medium;
  const colorClass = colorMap[color] || colorMap.primary;

  return (
    <div
      className={`${sizeClass} ${colorClass} ${className}`}
      aria-label="Loading"
      role="status"
      {...props}
    >
      <svg
        className="animate-spin w-full h-full"
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
      <span className="sr-only">Loading...</span>
    </div>
  );
};

Spinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large', 'xl']),
  color: PropTypes.oneOf([
    'primary',
    'secondary',
    'white',
    'gray',
    'black',
    'success',
    'error',
    'warning',
  ]),
  className: PropTypes.string,
};

export default Spinner;
