import React from 'react';
import PropTypes from 'prop-types';

export const Card = ({
  children,
  variant = 'default',
  className = '',
  onClick,
  hover = true,
  ...props
}) => {
  // Base card classes
  const baseClasses = 'rounded-lg overflow-hidden';

  // Variant classes
  const variantClasses = {
    default: 'bg-white shadow-sm border border-gray-100',
    premium: 'card-premium',
    glass: 'glass-effect backdrop-blur-md bg-white/10',
    outline: 'bg-white border border-gray-200',
    flat: 'bg-white',
    testimonial: 'bg-gray-50 shadow-testimonial',
  };

  // Hover classes
  const hoverClasses = hover ? 'hover:shadow-md transition-all' : '';

  // Interactive classes
  const interactiveClasses = onClick ? 'cursor-pointer' : '';

  return (
    <div
      className={`
        ${baseClasses}
        ${variantClasses[variant] || variantClasses.default}
        ${hoverClasses}
        ${interactiveClasses}
        ${className}
      `}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf([
    'default',
    'premium',
    'glass',
    'outline',
    'flat',
    'testimonial',
  ]),
  className: PropTypes.string,
  onClick: PropTypes.func,
  hover: PropTypes.bool,
};

export default Card;
