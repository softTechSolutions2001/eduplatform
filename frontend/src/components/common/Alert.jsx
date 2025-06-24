// fmt: off
// isort: skip_file
// Timestamp: 2024-07-07 - Fixed circular reference errors in Alert component

import React from 'react';
import PropTypes from 'prop-types';

/**
 * Alert Component
 *
 * Displays informational, success, warning, or error messages to the user
 * with appropriate styling and iconography.
 *
 * @param {Object} props Component props
 * @param {string} props.type Alert type: 'info', 'success', 'warning', 'error'
 * @param {React.ReactNode} props.children Alert content
 * @param {string} props.className Additional CSS classes
 * @param {Function} props.onClose Optional close handler
 */
const Alert = ({
  type = 'info',
  children,
  className = '',
  onClose,
  dismissible = true,
}) => {
  if (!children) return null;

  // Define styles based on alert type
  const alertStyles = {
    info: 'bg-blue-50 border-blue-500 text-blue-800',
    success: 'bg-green-50 border-green-500 text-green-800',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    error: 'bg-red-50 border-red-500 text-red-800',
  };

  // Helper function to safely stringify objects without circular references
  const safeStringify = (obj, maxDepth = 3, depth = 0) => {
    if (depth > maxDepth) return '[Object]';

    try {
      if (obj === null || obj === undefined) return String(obj);
      if (typeof obj !== 'object') return String(obj);

      if (Array.isArray(obj)) {
        return obj
          .map(item => safeStringify(item, maxDepth, depth + 1))
          .join(', ');
      }

      const pairs = [];
      for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          const value = obj[key];
          pairs.push(`${key}: ${safeStringify(value, maxDepth, depth + 1)}`);
        }
      }
      return `{ ${pairs.join(', ')} }`;
    } catch (error) {
      return '[Circular or complex object]';
    }
  };

  // Helper function to format different error message types
  const renderContent = () => {
    if (typeof children === 'string') {
      // Check if the message contains newlines - if so, split and render as list
      if (children.includes('\n')) {
        const lines = children.split('\n').filter(line => line.trim() !== '');
        return (
          <ul className="list-disc list-inside">
            {lines.map((line, index) => (
              <li key={index}>{line}</li>
            ))}
          </ul>
        );
      }
      return <p>{children}</p>;
    } else if (typeof children === 'object' && children !== null) {
      if (Array.isArray(children)) {
        return (
          <ul className="list-disc list-inside">
            {children.map((item, index) => (
              <li key={index}>
                {typeof item === 'object' ? safeStringify(item) : String(item)}
              </li>
            ))}
          </ul>
        );
      }

      // Handle error objects
      if (children instanceof Error) {
        return <p>{children.message || 'An error occurred'}</p>;
      }

      // Handle special error response objects from API
      if (children.response && children.response.data) {
        const errorData = children.response.data;

        // Format error messages from various API response structures
        if (typeof errorData === 'string') {
          return <p>{errorData}</p>;
        } else if (Array.isArray(errorData)) {
          return (
            <ul className="list-disc list-inside">
              {errorData.map((msg, idx) => (
                <li key={idx}>
                  {typeof msg === 'object' ? safeStringify(msg) : String(msg)}
                </li>
              ))}
            </ul>
          );
        } else if (typeof errorData === 'object') {
          // Extract error messages from nested object
          return (
            <ul className="list-disc list-inside">
              {Object.entries(errorData).map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong>{' '}
                  {typeof value === 'object'
                    ? safeStringify(value)
                    : String(value)}
                </li>
              ))}
            </ul>
          );
        }
      }

      // For simple message objects with a single message property
      if (children.message) {
        return <p>{children.message}</p>;
      }

      // For other objects, stringify them safely
      return <p>{safeStringify(children)}</p>;
    }

    // Fallback for any other type
    return <p>{String(children)}</p>;
  };

  return (
    <div className={`border-l-4 p-4 mb-4 ${alertStyles[type]} ${className}`}>
      <div className="flex justify-between items-start">
        <div className="flex-grow">{renderContent()}</div>

        {dismissible && onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-gray-500 hover:text-gray-800 focus:outline-none"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

Alert.propTypes = {
  /** Alert type - controls color scheme */
  type: PropTypes.oneOf(['info', 'success', 'warning', 'error']),

  /** Alert content - can be text, components, or an error object */
  children: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.object,
    PropTypes.array,
  ]),

  /** Additional CSS classes */
  className: PropTypes.string,

  /** Close button handler */
  onClose: PropTypes.func,

  /** Whether the alert is dismissible */
  dismissible: PropTypes.bool,
};

export default Alert;
