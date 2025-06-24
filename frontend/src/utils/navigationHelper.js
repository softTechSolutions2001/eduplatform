/**
 * File: frontend/src/utils/navigationHelper.js
 * Version: 1.0.0
 * Date: 2025-06-01
 * Author: mohithasanthanam
 * Last Modified: 2025-06-01
 *
 * Navigation Helper - Utility functions to help with course navigation
 * and fix the 404 error when navigating after course publish.
 */

/**
 * Ensures a course identifier is usable for navigation
 * @param {Object} response API response containing course data
 * @param {Object} courseData Current course data from context
 * @param {string} fallbackIdentifier A fallback identifier to use if no other is available
 * @returns {string} A valid course identifier for navigation
 */
export const getValidCourseIdentifier = (
  response,
  courseData,
  fallbackIdentifier
) => {
  // First, try to get the identifier from the API response
  const responseIdentifier =
    response?.id ||
    response?.slug ||
    (response?.data && (response.data?.id || response.data?.slug));

  // If that fails, use the course data
  const dataIdentifier = courseData?.id || courseData?.slug;

  // Use the first valid identifier found, or fallback to the original
  const identifier = responseIdentifier || dataIdentifier || fallbackIdentifier;

  console.log('Navigation helper - identifier sources:', {
    responseIdentifier,
    dataIdentifier,
    fallbackIdentifier,
    finalIdentifier: identifier,
  });

  return identifier;
};

/**
 * Constructs a valid navigation URL for course detail page
 * @param {string} identifier Course identifier (slug or ID)
 * @returns {string} URL to navigate to
 */
export const getCourseDetailUrl = identifier => {
  if (!identifier) {
    console.error('No valid course identifier provided for navigation');
    return '/instructor/dashboard'; // Fallback to dashboard
  }

  // Ensure the identifier is clean for URL use
  const cleanIdentifier = String(identifier).trim();
  const navigationUrl = `/instructor/courses/${cleanIdentifier}`;

  console.log('Navigation helper - creating URL:', {
    originalIdentifier: identifier,
    cleanIdentifier,
    navigationUrl,
  });

  return navigationUrl;
};

/**
 * Safely navigate to a course detail page with validation
 * @param {Function} navigate React Router navigate function
 * @param {string} identifier Course identifier (slug or ID)
 * @param {number} delay Delay in ms before navigating
 */
export const navigateToCourseDetail = (navigate, identifier, delay = 0) => {
  const navigationUrl = getCourseDetailUrl(identifier);

  console.log(
    `Navigation helper - will navigate to ${navigationUrl} in ${delay}ms`
  );

  if (delay > 0) {
    setTimeout(() => {
      console.log(`Navigation helper - navigating to ${navigationUrl}`);
      navigate(navigationUrl);
    }, delay);
  } else {
    console.log(
      `Navigation helper - navigating to ${navigationUrl} immediately`
    );
    navigate(navigationUrl);
  }
};
