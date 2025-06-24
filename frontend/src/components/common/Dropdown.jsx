// Created on 2025-07-25
// Basic Dropdown component for the EduPlatform

import React, { useState, useRef, useEffect } from 'react';

/**
 * A reusable dropdown component
 * @param {Object} props
 * @param {React.ReactNode} props.trigger - Element that triggers the dropdown
 * @param {React.ReactNode} props.children - Dropdown content
 * @param {String} props.align - Alignment of dropdown (left, right)
 * @param {String} props.className - Additional classes for styling
 */
const Dropdown = ({ trigger, children, align = 'left', className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleOutsideClick = event => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleOutsideClick);
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, []);

  // Handle escape key press
  useEffect(() => {
    const handleEscapeKey = event => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Trigger element */}
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>

      {/* Dropdown content */}
      {isOpen && (
        <div
          className={`origin-top-${align} absolute ${align}-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none z-10 ${className}`}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="dropdown-button"
        >
          {children}
        </div>
      )}
    </div>
  );
};

/**
 * Dropdown Item component for use within Dropdown
 */
export const DropdownItem = ({ onClick, children, icon, disabled = false }) => {
  const handleClick = e => {
    if (!disabled && onClick) {
      onClick(e);
    }
  };

  return (
    <button
      className={`group flex items-center w-full px-4 py-2 text-sm ${
        disabled
          ? 'text-gray-300 cursor-not-allowed'
          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
      }`}
      onClick={handleClick}
      disabled={disabled}
      role="menuitem"
    >
      {icon && <span className="mr-3">{icon}</span>}
      {children}
    </button>
  );
};

export default Dropdown;
