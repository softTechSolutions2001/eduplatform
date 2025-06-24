// Created on 2025-07-25
// Basic Sidebar navigation component for the EduPlatform

import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Sidebar navigation component
 * @param {Object} props
 * @param {Array} props.items - Navigation items to display
 * @param {Boolean} props.isOpen - Whether the sidebar is open or collapsed
 * @param {Function} props.onToggle - Function to handle sidebar toggle
 * @param {String} props.className - Additional classes for styling
 */
const Sidebar = ({ items = [], isOpen = true, onToggle, className = '' }) => {
  return (
    <div
      className={`bg-white shadow-md border-r border-gray-200 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-16'
      } ${className}`}
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {isOpen && (
          <h1 className="text-xl font-semibold text-primary-700">
            EduPlatform
          </h1>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-md hover:bg-gray-100"
          aria-label="Toggle sidebar"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d={
                isOpen
                  ? 'M11 19l-7-7 7-7m8 14l-7-7 7-7'
                  : 'M4 6h16M4 12h16M4 18h16'
              }
            />
          </svg>
        </button>
      </div>

      <nav className="mt-4">
        <ul className="space-y-1">
          {items.map((item, index) => (
            <li key={index}>
              <Link
                to={item.path}
                className={`flex items-center px-4 py-2 hover:bg-gray-100 ${
                  item.active
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600'
                }`}
              >
                {item.icon && <span className="mr-3">{item.icon}</span>}
                {isOpen && <span>{item.label}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
