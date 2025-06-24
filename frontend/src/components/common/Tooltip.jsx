import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { createPortal } from 'react-dom';

const Tooltip = ({
  children,
  content,
  position = 'top',
  delay = 300,
  className = '',
  tooltipClassName = '',
  disabled = false,
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const targetRef = useRef(null);
  const tooltipRef = useRef(null);
  const timerRef = useRef(null);

  const positions = {
    top: 'translate(-50%, -100%) translateY(-8px)',
    bottom: 'translate(-50%, 0) translateY(8px)',
    left: 'translate(-100%, -50%) translateX(-8px)',
    right: 'translate(0, -50%) translateX(8px)',
  };

  const arrows = {
    top: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-t-current border-x-transparent border-b-0',
    bottom:
      'top-0 left-1/2 -translate-x-1/2 -translate-y-full border-b-current border-x-transparent border-t-0',
    left: 'right-0 top-1/2 translate-x-full -translate-y-1/2 border-l-current border-y-transparent border-r-0',
    right:
      'left-0 top-1/2 -translate-x-full -translate-y-1/2 border-r-current border-y-transparent border-l-0',
  };

  // Calculate tooltip position
  const updateTooltipPosition = () => {
    if (!targetRef.current || !tooltipRef.current) return;

    const targetRect = targetRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollY = window.scrollY || window.pageYOffset;
    const scrollX = window.scrollX || window.pageXOffset;

    let top, left;

    switch (position) {
      case 'bottom':
        top = targetRect.bottom + scrollY;
        left = targetRect.left + targetRect.width / 2 + scrollX;
        break;
      case 'left':
        top = targetRect.top + targetRect.height / 2 + scrollY;
        left = targetRect.left + scrollX;
        break;
      case 'right':
        top = targetRect.top + targetRect.height / 2 + scrollY;
        left = targetRect.right + scrollX;
        break;
      case 'top':
      default:
        top = targetRect.top + scrollY;
        left = targetRect.left + targetRect.width / 2 + scrollX;
    }

    setTooltipPosition({ top, left });
  };

  // Handle mouse events
  const handleMouseEnter = () => {
    if (disabled) return;

    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setIsVisible(true);
      requestAnimationFrame(updateTooltipPosition);
    }, delay);
  };

  const handleMouseLeave = () => {
    clearTimeout(timerRef.current);
    setIsVisible(false);
  };

  // Update position when tooltip becomes visible
  useEffect(() => {
    if (isVisible) {
      updateTooltipPosition();
      window.addEventListener('resize', updateTooltipPosition);
      window.addEventListener('scroll', updateTooltipPosition);
    }

    return () => {
      window.removeEventListener('resize', updateTooltipPosition);
      window.removeEventListener('scroll', updateTooltipPosition);
    };
  }, [isVisible]);

  // Clean up timer
  useEffect(() => {
    return () => {
      clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <>
      <div
        ref={targetRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleMouseEnter}
        onBlur={handleMouseLeave}
        className={`inline-block ${className}`}
        {...props}
      >
        {children}
      </div>

      {isVisible &&
        content &&
        createPortal(
          <div
            ref={tooltipRef}
            className={`
            fixed z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-md
            ${tooltipClassName}
          `}
            style={{
              top: `${tooltipPosition.top}px`,
              left: `${tooltipPosition.left}px`,
              transform: positions[position],
              pointerEvents: 'none',
            }}
          >
            {content}
            <div
              className={`absolute w-0 h-0 border-4 ${arrows[position]}`}
            ></div>
          </div>,
          document.body
        )}
    </>
  );
};

Tooltip.propTypes = {
  children: PropTypes.node.isRequired,
  content: PropTypes.node,
  position: PropTypes.oneOf(['top', 'right', 'bottom', 'left']),
  delay: PropTypes.number,
  className: PropTypes.string,
  tooltipClassName: PropTypes.string,
  disabled: PropTypes.bool,
};

export default Tooltip;
