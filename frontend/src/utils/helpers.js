/**
 * File: frontend/src/utils/helpers.js
 * Version: 1.0.0
 * Date: 2025-06-01 13:00:00
 * Author: mohithasanthanam
 * Last Modified: 2025-06-01 13:00:00 UTC
 *
 * Utility helper functions for the frontend application
 */

/**
 * Creates a debounced function that delays invoking func until after wait milliseconds
 * have elapsed since the last time the debounced function was invoked.
 *
 * @param {Function} func - The function to debounce
 * @param {number} wait - The number of milliseconds to delay
 * @returns {Function} - The debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Formats a date string or timestamp to a human-readable format
 *
 * @param {string|number|Date} date - The date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} - The formatted date string
 */
export const formatDate = (date, options = {}) => {
  if (!date) return '';

  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };

  const dateTimeOptions = { ...defaultOptions, ...options };

  return new Intl.DateTimeFormat('en-US', dateTimeOptions).format(
    new Date(date)
  );
};

/**
 * Truncates a string to a specified length and adds an ellipsis if truncated
 *
 * @param {string} str - The string to truncate
 * @param {number} maxLength - The maximum length
 * @returns {string} - The truncated string
 */
export const truncateString = (str, maxLength = 100) => {
  if (!str || str.length <= maxLength) return str;
  return `${str.substring(0, maxLength)}...`;
};

/**
 * Generates a random string of specified length
 *
 * @param {number} length - The length of the string to generate
 * @returns {string} - The random string
 */
export const generateRandomString = (length = 8) => {
  const chars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
};
