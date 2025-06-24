/**
 * Utility functions for formatting duration values between minutes and display formats
 */

/**
 * Format duration in minutes to human-readable format
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration string
 */
export function formatDuration(minutes) {
  if (!minutes || minutes === 0) {
    return 'N/A';
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  const parts = [];

  if (hours > 0) {
    parts.push(`${hours} hour${hours > 1 ? 's' : ''}`);
  }

  if (remainingMinutes > 0) {
    parts.push(`${remainingMinutes} minute${remainingMinutes > 1 ? 's' : ''}`);
  }

  return parts.join(' ');
}

/**
 * Parse duration string to minutes
 * @param {string} durationStr - Duration string (e.g., "2 hours 30 minutes")
 * @returns {number} Duration in minutes
 */
export function parseDurationToMinutes(durationStr) {
  if (!durationStr || typeof durationStr !== 'string') {
    return 0;
  }

  let totalMinutes = 0;

  // Extract hours
  const hoursMatch = durationStr.match(/(\d+)\s*hour/i);
  if (hoursMatch) {
    totalMinutes += parseInt(hoursMatch[1]) * 60;
  }

  // Extract minutes
  const minutesMatch = durationStr.match(/(\d+)\s*minute/i);
  if (minutesMatch) {
    totalMinutes += parseInt(minutesMatch[1]);
  }

  return totalMinutes;
}

/**
 * Convert seconds to minutes (for legacy compatibility)
 * @param {number} seconds - Duration in seconds
 * @returns {number} Duration in minutes
 */
export function secondsToMinutes(seconds) {
  if (!seconds || seconds === 0) {
    return 0;
  }
  return Math.round(seconds / 60);
}

/**
 * Convert minutes to seconds (for legacy compatibility)
 * @param {number} minutes - Duration in minutes
 * @returns {number} Duration in seconds
 */
export function minutesToSeconds(minutes) {
  if (!minutes || minutes === 0) {
    return 0;
  }
  return minutes * 60;
}

/**
 * Format duration for course display with hours and minutes
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration for display
 */
export function formatCourseDuration(minutes) {
  if (!minutes || minutes === 0) {
    return 'TBD';
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (hours === 0) {
    return `${remainingMinutes} min`;
  }

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Validate duration input (should be positive and reasonable)
 * @param {number} minutes - Duration in minutes
 * @returns {boolean} Whether the duration is valid
 */
export function isValidDuration(minutes) {
  return typeof minutes === 'number' && minutes >= 0 && minutes <= 10080; // Max 7 days
}

export default {
  formatDuration,
  parseDurationToMinutes,
  secondsToMinutes,
  minutesToSeconds,
  formatCourseDuration,
  isValidDuration,
};
