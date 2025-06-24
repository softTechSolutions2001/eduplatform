import React from 'react';
import PropTypes from 'prop-types';

const ProgressBar = ({
  value = 0,
  max = 100,
  showValue = false,
  size = 'medium',
  variant = 'primary',
  className = '',
  ...props
}) => {
  // Calculate percentage
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  // Size classes
  const sizeClasses = {
    small: 'h-1',
    medium: 'h-2',
    large: 'h-3',
    xl: 'h-4',
  };

  // Variant classes
  const variantClasses = {
    primary: 'bg-primary-500',
    secondary: 'bg-secondary-500',
    tertiary: 'bg-tertiary-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
    gray: 'bg-gray-500',
    gradient: 'bg-gradient-to-r from-primary-500 to-secondary-500',
  };

  return (
    <div className={`w-full ${className}`} {...props}>
      <div className="flex justify-between items-center mb-1">
        {props.label && (
          <div className="text-sm text-gray-700">{props.label}</div>
        )}
        {showValue && (
          <div className="text-sm text-gray-500">{Math.round(percentage)}%</div>
        )}
      </div>
      <div
        className={`w-full bg-gray-200 rounded-full ${sizeClasses[size] || sizeClasses.medium}`}
      >
        <div
          className={`${variantClasses[variant] || variantClasses.primary} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

ProgressBar.propTypes = {
  value: PropTypes.number,
  max: PropTypes.number,
  showValue: PropTypes.bool,
  size: PropTypes.oneOf(['small', 'medium', 'large', 'xl']),
  variant: PropTypes.oneOf([
    'primary',
    'secondary',
    'tertiary',
    'success',
    'warning',
    'danger',
    'info',
    'gray',
    'gradient',
  ]),
  className: PropTypes.string,
  label: PropTypes.string,
};

export default ProgressBar;
