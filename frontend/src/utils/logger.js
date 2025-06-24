/**
 * File: src/utils/logger.js
 * Version: 1.0.0
 * Date: 2025-05-13 18:04:20
 * Author: cadsanthanam
 *
 * Utility for centralized error logging
 */

import * as Sentry from '@sentry/react'; // Import your preferred logging service

/**
 * Log errors with context to console in development and
 * Sentry in production
 *
 * @param {Error} error - Error object
 * @param {Object} context - Additional context information
 */
export const logError = (error, context = {}) => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[ERROR] ${error.message}`, error, context);
  }

  // In production, send to Sentry or other monitoring
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureException(error, {
      extra: context,
    });
  }
};

/**
 * Log warnings with context
 *
 * @param {string} message - Warning message
 * @param {Object} context - Additional context information
 */
export const logWarning = (message, context = {}) => {
  if (process.env.NODE_ENV === 'development') {
    console.warn(`[WARNING] ${message}`, context);
  }

  // In production, send to monitoring at a lower priority
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureMessage(message, {
      level: 'warning',
      extra: context,
    });
  }
};

export default {
  logError,
  logWarning,
};
