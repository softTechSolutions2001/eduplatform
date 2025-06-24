import React from 'react';
import PropTypes from 'prop-types';

const Skeleton = ({
  variant = 'rectangle',
  width,
  height,
  className = '',
  animated = true,
  ...props
}) => {
  // Base classes
  const baseClasses = 'bg-gray-200 rounded';

  // Animation classes
  const animationClasses = animated ? 'animate-pulse' : '';

  // Variant-specific classes
  const variantClasses = {
    rectangle: '',
    text: 'h-4',
    circle: 'rounded-full',
    avatar: 'rounded-full',
  };

  // Style object for custom width and height
  const style = {
    ...(width ? { width } : {}),
    ...(height ? { height } : {}),
    ...props.style,
  };

  // Special handling for common skeleton patterns
  if (variant === 'avatar') {
    return (
      <div
        className={`
          ${baseClasses} ${animationClasses} ${variantClasses.avatar}
          ${className} ${width ? '' : 'w-10'} ${height ? '' : 'h-10'}
        `}
        style={style}
        {...props}
      />
    );
  }

  return (
    <div
      className={`
        ${baseClasses} ${animationClasses} ${variantClasses[variant] || variantClasses.rectangle}
        ${className}
      `}
      style={style}
      {...props}
    />
  );
};

// Component for creating text skeletons with multiple lines
export const TextSkeleton = ({
  lines = 3,
  className = '',
  lastLineWidth = '75%',
  spacing = 'mb-2',
}) => {
  return (
    <div className={className}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          className={index < lines - 1 ? spacing : ''}
          width={index === lines - 1 && lastLineWidth ? lastLineWidth : '100%'}
        />
      ))}
    </div>
  );
};

// Component for creating card skeletons
export const CardSkeleton = ({
  className = '',
  imageHeight = '200px',
  lines = 3,
}) => {
  return (
    <div
      className={`border border-gray-200 rounded-lg overflow-hidden ${className}`}
    >
      <Skeleton height={imageHeight} />
      <div className="p-4">
        <TextSkeleton lines={lines} />
      </div>
    </div>
  );
};

Skeleton.propTypes = {
  variant: PropTypes.oneOf(['rectangle', 'text', 'circle', 'avatar']),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  className: PropTypes.string,
  animated: PropTypes.bool,
  style: PropTypes.object,
};

TextSkeleton.propTypes = {
  lines: PropTypes.number,
  className: PropTypes.string,
  lastLineWidth: PropTypes.string,
  spacing: PropTypes.string,
};

CardSkeleton.propTypes = {
  className: PropTypes.string,
  imageHeight: PropTypes.string,
  lines: PropTypes.number,
};

export default Skeleton;
