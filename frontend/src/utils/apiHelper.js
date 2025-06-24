// fmt: off
// isort: skip_file
// Timestamp: 2024-07-07 - API Helper for unified endpoint handling

/**
 * API Helper utilities for handling different endpoint patterns and conversions
 *
 * The backend may have different endpoint patterns for the same resource:
 * - /api/courses/:id/ - Regular endpoint with ID lookup
 * - /api/courses/:slug/ - Regular endpoint with slug lookup
 * - /api/instructor/courses/:id/ - Instructor-specific endpoint with ID lookup
 * - /api/instructor/courses/:slug/ - Instructor-specific endpoint with slug lookup
 *
 * This helper ensures consistent handling of these patterns.
 */

/**
 * Determines if a string is likely a slug vs an ID
 * @param {string} identifier - The identifier to check
 * @returns {boolean} - True if this looks like a slug, false if it's likely an ID
 */
export const isSlug = identifier => {
  if (!identifier) return false;

  // Convert to string in case it's a number
  const str = String(identifier);

  // If it's a number-only string, it's probably an ID
  if (/^\d+$/.test(str)) {
    return false;
  }

  // If it contains hyphens, letters, etc. it's probably a slug
  return true;
};

/**
 * Constructs a proper course endpoint URL based on the identifier type and context
 * @param {string|number} identifier - Course ID or slug
 * @param {boolean} isInstructorContext - Whether to use instructor-specific endpoints
 * @returns {string} - Properly formatted endpoint URL
 */
export const buildCourseEndpoint = (
  identifier,
  isInstructorContext = false
) => {
  const baseUrl = isInstructorContext ? '/instructor/courses' : '/courses';

  // Make sure identifier exists
  if (!identifier) {
    throw new Error('Course identifier is required');
  }

  return `${baseUrl}/${identifier}/`;
};

/**
 * Safely extracts an ID from a course object, with fallbacks
 * @param {Object} course - Course object
 * @returns {number|null} - Course ID or null if not found
 */
export const extractCourseId = course => {
  if (!course) return null;

  // Try common ID field names
  return course.id || course.course_id || course.courseId || null;
};

/**
 * Safely extracts a slug from a course object, with fallbacks
 * @param {Object} course - Course object
 * @returns {string|null} - Course slug or null if not found
 */
export const extractCourseSlug = course => {
  if (!course) return null;

  // Try common slug field names
  return course.slug || course.course_slug || course.courseSlug || null;
};

/**
 * Generates a courseParam object with both ID and slug for flexible API calls
 * @param {Object} course - Course object
 * @returns {Object} - Object with id and slug properties
 */
export const courseParams = course => {
  return {
    id: extractCourseId(course),
    slug: extractCourseSlug(course),
  };
};

/**
 * Tries multiple API endpoints based on available identifiers
 * @param {Function} apiCall - Function that makes the API call
 * @param {Object} identifiers - Object with possible identifiers (id, slug)
 * @returns {Promise} - Result of the first successful API call
 */
export const tryMultipleEndpoints = async (apiCall, identifiers) => {
  const errors = [];

  // Try ID-based endpoint if ID exists
  if (identifiers.id) {
    try {
      return await apiCall(identifiers.id, false); // not instructor endpoint
    } catch (error) {
      errors.push({ type: 'id', error });

      // Try instructor ID-based endpoint
      try {
        return await apiCall(identifiers.id, true); // instructor endpoint
      } catch (instructorError) {
        errors.push({ type: 'instructor_id', error: instructorError });
      }
    }
  }

  // Try slug-based endpoint if slug exists
  if (identifiers.slug) {
    try {
      return await apiCall(identifiers.slug, false); // not instructor endpoint
    } catch (error) {
      errors.push({ type: 'slug', error });

      // Try instructor slug-based endpoint
      try {
        return await apiCall(identifiers.slug, true); // instructor endpoint
      } catch (instructorError) {
        errors.push({ type: 'instructor_slug', error: instructorError });
      }
    }
  }

  // If all attempts fail, throw a comprehensive error
  throw {
    message: 'All API endpoint attempts failed',
    errors,
  };
};

export default {
  isSlug,
  buildCourseEndpoint,
  extractCourseId,
  extractCourseSlug,
  courseParams,
  tryMultipleEndpoints,
};
