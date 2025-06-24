import React from 'react';
import PropTypes from 'prop-types';

const Avatar = ({
  name,
  src,
  bgColor,
  size = 'medium',
  hasBorder = false,
  borderColor = 'white',
  className = '',
  ...props
}) => {
  // Get initials from name
  const getInitials = name => {
    if (!name) return '';
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase();
  };

  // Size classes
  const sizeClasses = {
    xs: 'h-6 w-6 text-xs',
    small: 'h-8 w-8 text-xs',
    medium: 'h-10 w-10 text-sm',
    large: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg',
    '2xl': 'h-20 w-20 text-xl',
  };

  // Border classes
  const borderClasses = hasBorder ? `border-2 border-${borderColor}` : '';

  return (
    <div
      className={`
        ${sizeClasses[size] || sizeClasses.medium}
        rounded-full flex items-center justify-center text-white shadow-sm overflow-hidden
        ${borderClasses}
        ${className}
      `}
      style={{ backgroundColor: src ? 'transparent' : bgColor || '#3d74f4' }}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={name || 'avatar'}
          className="h-full w-full object-cover"
        />
      ) : (
        <div className="h-full w-full flex items-center justify-center">
          {getInitials(name)}
        </div>
      )}
    </div>
  );
};

Avatar.propTypes = {
  name: PropTypes.string,
  src: PropTypes.string,
  bgColor: PropTypes.string,
  size: PropTypes.oneOf(['xs', 'small', 'medium', 'large', 'xl', '2xl']),
  hasBorder: PropTypes.bool,
  borderColor: PropTypes.string,
  className: PropTypes.string,
};

export default Avatar;
