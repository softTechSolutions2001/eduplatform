/**
 * File: frontend/src/components/common/Button.jsx
 * Version: 2.1.1
 * Date: 2025-05-24 16:51:32
 * Author: mohithasanthanam
 * Last Modified: 2025-05-24 16:51:32 UTC
 *
 * Reusable Button Component with Loading State Support
 *
 * This component is a versatile button with various style variants, sizes,
 * and support for loading states. It includes a spinner animation when loading.
 *
 * Connected files that need to be consistent:
 * - frontend/src/pages/instructor/EditCoursePage.jsx (uses Button component)
 * - frontend/src/pages/instructor/CourseWizard.jsx (uses Button component)
 * - Other UI components that use the Button component
 */

import React from 'react';
import PropTypes from 'prop-types';

export const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  icon = null,
  iconPosition = 'right',
  isLoading = false,
  loading, // Added alias support for backward compatibility
  ...props
}) => {
  // Base button classes
  const baseClasses =
    'rounded-lg font-medium transition-all duration-200 inline-flex items-center justify-center';

  // Size classes
  const sizeClasses = {
    small: 'text-sm px-3 py-1.5',
    medium: 'px-4 py-2',
    large: 'text-lg px-6 py-3',
  };

  // Variant classes
  const variantClasses = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white shadow-sm',
    secondary: 'bg-secondary-500 hover:bg-secondary-600 text-white shadow-sm',
    tertiary: 'bg-tertiary-500 hover:bg-tertiary-600 text-white shadow-sm',
    outline:
      'bg-white border-2 border-primary-500 text-primary-600 hover:bg-primary-50',
    'outline-secondary':
      'bg-white border-2 border-secondary-500 text-secondary-600 hover:bg-secondary-50',
    'outline-tertiary':
      'bg-white border-2 border-tertiary-500 text-tertiary-600 hover:bg-tertiary-50',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-700',
    'ghost-white':
      'bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white border border-white/20',
    link: 'bg-transparent text-primary-600 hover:text-primary-700 underline hover:no-underline p-0',
    danger: 'bg-red-500 hover:bg-red-600 text-white shadow-sm',
    success: 'bg-green-500 hover:bg-green-600 text-white shadow-sm',
    premium: 'btn-premium',
  };

  // Width classes
  const widthClasses = fullWidth ? 'w-full' : '';

  // Disabled classes
  const disabledClasses = disabled ? 'opacity-60 cursor-not-allowed' : '';

  // Support both isLoading and loading props for backward compatibility
  const isLoadingState = isLoading || loading;

  // Loading state
  const loadingClassses = isLoadingState ? 'relative !text-transparent' : '';

  // Filter out loading prop before passing to DOM
  const buttonProps = { ...props };
  delete buttonProps.loading;

  return (
    <button
      type={type}
      className={`
        ${baseClasses}
        ${sizeClasses[size] || sizeClasses.medium}
        ${variantClasses[variant] || variantClasses.primary}
        ${widthClasses}
        ${disabledClasses}
        ${loadingClassses}
        ${className}
      `}
      disabled={disabled || isLoadingState}
      onClick={onClick}
      {...buttonProps}
    >
      {/* Loading spinner */}
      {isLoadingState && (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg
            className="animate-spin h-5 w-5 text-white"
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
      )}

      {/* Button content with icon */}
      {iconPosition === 'left' && icon && <span className="mr-2">{icon}</span>}
      {children}
      {iconPosition === 'right' && icon && <span className="ml-2">{icon}</span>}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf([
    'primary',
    'secondary',
    'tertiary',
    'outline',
    'outline-secondary',
    'outline-tertiary',
    'ghost',
    'ghost-white',
    'link',
    'danger',
    'success',
    'premium',
  ]),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  fullWidth: PropTypes.bool,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  icon: PropTypes.node,
  iconPosition: PropTypes.oneOf(['left', 'right']),
  isLoading: PropTypes.bool,
  loading: PropTypes.bool, // Added for backward compatibility
};

export default Button;
