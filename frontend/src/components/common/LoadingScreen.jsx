/**
 * File: frontend/src/components/common/LoadingScreen.jsx
 * Purpose: Loading screen component for the educational platform
 * Created: 2025-05-02
 *
 * This component displays a loading spinner with an optional message.
 * Used throughout the application to indicate loading states.
 *
 * Usage:
 * <LoadingScreen message="Loading content..." />
 */

import React from 'react';
import PropTypes from 'prop-types';

const LoadingScreen = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white">
      <div className="w-16 h-16 mb-4">
        <svg
          className="animate-spin text-primary-600 w-full h-full"
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
      {message && <p className="text-gray-600 text-lg">{message}</p>}
    </div>
  );
};

LoadingScreen.propTypes = {
  message: PropTypes.string,
};

export default LoadingScreen;
