import React from 'react';
import PropTypes from 'prop-types';

export const Badge = ({
  children,
  variant = 'primary',
  size = 'medium',
  className = '',
  ...props
}) => {
  // Base badge classes
  const baseClasses =
    'inline-flex items-center justify-center rounded-full font-medium';

  // Size classes
  const sizeClasses = {
    small: 'text-xs px-2 py-0.5',
    medium: 'text-sm px-3 py-1',
    large: 'text-base px-4 py-1.5',
  };

  // Variant classes
  const variantClasses = {
    primary: 'bg-primary-50 text-primary-600',
    secondary: 'bg-secondary-50 text-secondary-600',
    tertiary: 'bg-tertiary-50 text-tertiary-600',
    success: 'bg-green-50 text-green-600',
    warning: 'bg-yellow-50 text-yellow-600',
    danger: 'bg-red-50 text-red-600',
    info: 'bg-blue-50 text-blue-600',
    gray: 'bg-gray-100 text-gray-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    white: 'bg-white/20 text-white',
  };

  return (
    <span
      className={`
        ${baseClasses}
        ${sizeClasses[size] || sizeClasses.medium}
        ${variantClasses[variant] || variantClasses.primary}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
};

Badge.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf([
    'primary',
    'secondary',
    'tertiary',
    'success',
    'warning',
    'danger',
    'info',
    'gray',
    'purple',
    'orange',
    'white',
  ]),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string,
};

export default Badge;
