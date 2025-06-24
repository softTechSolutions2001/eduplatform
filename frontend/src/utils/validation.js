/**
 * Unified validation utilities for EduPlatform
 * Version: 2.1.0
 * Last Modified: 2025-05-30 16:53:23
 * Modified by: sujibeautysalon
 * Purpose: Ensures consistency between frontend and backend validation logic
 */

// Access level constants
export const ACCESS_LEVELS = {
  GUEST: 'guest',
  REGISTERED: 'registered',
  PREMIUM: 'premium',
};

// Subscription tier to access level mapping
export const SUBSCRIPTION_ACCESS_MAPPING = {
  guest: ACCESS_LEVELS.GUEST,
  registered: ACCESS_LEVELS.REGISTERED,
  premium: ACCESS_LEVELS.PREMIUM,
};

// User role constants
export const USER_ROLES = {
  STUDENT: 'student',
  INSTRUCTOR: 'instructor',
  ADMIN: 'admin',
};

/**
 * Normalize user role to ensure consistency
 * @param {string} role - Raw role string
 * @returns {string} - Normalized role
 */
export const normalizeUserRole = role => {
  if (!role) return null;
  return role.toLowerCase().trim();
};

/**
 * Get user access level based on authentication status and subscription
 * @param {Object} user - User object with subscription info
 * @param {boolean} isAuthenticated - Authentication status
 * @returns {string} - Access level
 */
export const getUserAccessLevel = (user, isAuthenticated = false) => {
  // Unauthenticated users get guest access (preview only)
  if (!isAuthenticated || !user) {
    return ACCESS_LEVELS.GUEST;
  }
  // Get subscription tier and map to access level
  const subscriptionTier =
    user.subscription_tier || user.subscriptionTier || 'registered';
  const accessLevel =
    SUBSCRIPTION_ACCESS_MAPPING[subscriptionTier.toLowerCase()];

  // Default to registered for authenticated users with unknown subscription
  return accessLevel || ACCESS_LEVELS.REGISTERED;
};

/**
 * Validate lesson data with unified business rules
 * @param {Object} lessonData - Lesson data to validate
 * @returns {Object} - Validation result with isValid and errors
 */
export const validateLessonData = lessonData => {
  const errors = {};
  let isValid = true;

  // Required fields validation
  if (!lessonData.title || lessonData.title.trim().length === 0) {
    errors.title = 'Lesson title is required';
    isValid = false;
  } else if (lessonData.title.length > 200) {
    errors.title = 'Lesson title must be less than 200 characters';
    isValid = false;
  }

  if (!lessonData.description || lessonData.description.trim().length === 0) {
    errors.description = 'Lesson description is required';
    isValid = false;
  } else if (lessonData.description.length > 1000) {
    errors.description = 'Lesson description must be less than 1000 characters';
    isValid = false;
  }

  // Access level validation
  const accessLevel = lessonData.access_level || lessonData.accessLevel;
  if (!accessLevel || !Object.values(ACCESS_LEVELS).includes(accessLevel)) {
    errors.access_level = 'Valid access level is required';
    isValid = false;
  }
  // Guest content validation - critical business rule
  if (accessLevel === ACCESS_LEVELS.GUEST) {
    const guestContent = lessonData.guest_content || lessonData.guestContent;
    if (!guestContent || guestContent.trim().length === 0) {
      errors.guest_content =
        'Guest content is required for guest access level lessons';
      isValid = false;
    } else if (guestContent.length > 500) {
      errors.guest_content = 'Guest content must be less than 500 characters';
      isValid = false;
    }
  }

  // Premium content validation
  if (accessLevel === ACCESS_LEVELS.PREMIUM) {
    const premiumContent =
      lessonData.premium_content || lessonData.premiumContent;
    if (premiumContent && premiumContent.length > 2000) {
      errors.premium_content =
        'Premium content must be less than 2000 characters';
      isValid = false;
    }
  }

  // Video URL validation
  if (lessonData.video_url) {
    const urlPattern =
      /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    if (!urlPattern.test(lessonData.video_url)) {
      errors.video_url = 'Please enter a valid video URL';
      isValid = false;
    }
  }

  // Order validation
  if (lessonData.order !== undefined && lessonData.order !== null) {
    if (lessonData.order < 0) {
      errors.order = 'Lesson order must be non-negative';
      isValid = false;
    }
  }

  return { isValid, errors };
};

/**
 * Check if user can access specific content based on access level
 * @param {string} userAccessLevel - User's access level
 * @param {string} contentAccessLevel - Content's required access level
 * @returns {boolean} - Whether user can access the content
 */
export const canUserAccessContent = (userAccessLevel, contentAccessLevel) => {
  const accessHierarchy = {
    [ACCESS_LEVELS.GUEST]: 1,
    [ACCESS_LEVELS.REGISTERED]: 2,
    [ACCESS_LEVELS.PREMIUM]: 3,
  };

  const userLevel = accessHierarchy[userAccessLevel] || 0;
  const contentLevel = accessHierarchy[contentAccessLevel] || 1;

  return userLevel >= contentLevel;
};

/**
 * Validate instructor data
 * @param {Object} instructorData - Instructor data to validate
 * @returns {Object} - Validation result
 */
export const validateInstructorData = instructorData => {
  const errors = {};
  let isValid = true;

  // Required fields
  if (!instructorData.bio || instructorData.bio.trim().length === 0) {
    errors.bio = 'Instructor bio is required';
    isValid = false;
  } else if (instructorData.bio.length > 1000) {
    errors.bio = 'Bio must be less than 1000 characters';
    isValid = false;
  }

  if (!instructorData.expertise || instructorData.expertise.length === 0) {
    errors.expertise = 'At least one area of expertise is required';
    isValid = false;
  }

  // Experience validation
  if (instructorData.years_of_experience !== undefined) {
    if (
      instructorData.years_of_experience < 0 ||
      instructorData.years_of_experience > 50
    ) {
      errors.years_of_experience =
        'Years of experience must be between 0 and 50';
      isValid = false;
    }
  }

  return { isValid, errors };
};

/**
 * Validate course data
 * @param {Object} courseData - Course data to validate
 * @returns {Object} - Validation result
 */
export const validateCourseData = courseData => {
  const errors = {};
  let isValid = true;

  // Required fields
  if (!courseData.title || courseData.title.trim().length === 0) {
    errors.title = 'Course title is required';
    isValid = false;
  } else if (courseData.title.length > 200) {
    errors.title = 'Course title must be less than 200 characters';
    isValid = false;
  }

  if (!courseData.description || courseData.description.trim().length === 0) {
    errors.description = 'Course description is required';
    isValid = false;
  } else if (courseData.description.length > 2000) {
    errors.description = 'Course description must be less than 2000 characters';
    isValid = false;
  }

  if (!courseData.category || courseData.category.trim().length === 0) {
    errors.category = 'Course category is required';
    isValid = false;
  }

  // Price validation
  if (courseData.price !== undefined && courseData.price !== null) {
    if (courseData.price < 0) {
      errors.price = 'Course price cannot be negative';
      isValid = false;
    }
  }

  return { isValid, errors };
};

/**
 * Validate module data for creation/editing
 * @param {Object} moduleData - Module data to validate
 * @returns {Object} - Validation errors object
 */
export const validateModule = moduleData => {
  const errors = {};

  // Title validation
  if (!moduleData.title?.trim()) {
    errors.title = 'Module title is required';
  } else if (moduleData.title.length > 200) {
    errors.title = 'Module title must be less than 200 characters';
  }

  // Description validation (optional but with length limit)
  if (moduleData.description && moduleData.description.length > 1000) {
    errors.description = 'Module description must be less than 1000 characters';
  }

  // Order validation
  if (moduleData.order !== undefined) {
    const order = parseInt(moduleData.order);
    if (isNaN(order) || order < 1) {
      errors.order = 'Module order must be a positive number';
    }
  }

  // Duration validation (optional but must be positive if provided)
  if (
    moduleData.duration_minutes !== undefined &&
    moduleData.duration_minutes !== ''
  ) {
    const duration = parseInt(moduleData.duration_minutes);
    if (isNaN(duration) || duration < 1) {
      errors.duration_minutes = 'Duration must be a positive number in minutes';
    }
  }

  // Access level validation
  if (
    moduleData.access_level &&
    !Object.values(ACCESS_LEVELS).includes(moduleData.access_level)
  ) {
    errors.access_level = 'Invalid access level selected';
  }

  return errors;
};

// Default export for convenience
export default {
  ACCESS_LEVELS,
  SUBSCRIPTION_ACCESS_MAPPING,
  USER_ROLES,
  normalizeUserRole,
  getUserAccessLevel,
  validateLessonData,
  canUserAccessContent,
  validateInstructorData,
  validateCourseData,
  validateModule,
};
