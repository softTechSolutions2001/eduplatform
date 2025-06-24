import React from 'react';
import PropTypes from 'prop-types';

const Rating = ({
  value = 0,
  total = 5,
  showValue = false,
  size = 'medium',
  className = '',
  count = null,
  ...props
}) => {
  // Size classes
  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
  };

  return (
    <div className={`flex items-center ${className}`} {...props}>
      <div className="text-yellow-400 flex">
        {[...Array(total)].map((_, i) => (
          <i
            key={i}
            className={`
              ${sizeClasses[size] || sizeClasses.medium}
              ${
                i < Math.floor(value)
                  ? 'fas fa-star'
                  : i < value
                    ? 'fas fa-star-half-alt'
                    : 'far fa-star'
              }
            `}
          ></i>
        ))}
      </div>
      {showValue && (
        <span
          className={`ml-1.5 font-medium text-gray-700 ${sizeClasses[size] || sizeClasses.medium}`}
        >
          {value.toFixed(1)}
        </span>
      )}
      {count !== null && (
        <span
          className={`ml-1 text-gray-500 ${sizeClasses[size] || sizeClasses.medium}`}
        >
          ({count})
        </span>
      )}
    </div>
  );
};

Rating.propTypes = {
  value: PropTypes.number,
  total: PropTypes.number,
  showValue: PropTypes.bool,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  className: PropTypes.string,
  count: PropTypes.number,
};

export default Rating;
