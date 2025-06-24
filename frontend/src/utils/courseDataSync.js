/**
 * File: frontend/src/utils/courseDataSync.js
 * Version: 1.0.0
 * Date: 2025-01-01
 * Author: GitHub Copilot
 *
 * Course Data Synchronization Utilities
 *
 * This module provides unified data synchronization utilities to ensure consistency
 * between different course creation modes:
 * - CourseWizard (React Context + Reducer)
 * - EditCoursePage (Traditional form-based editor)
 * - CourseBuilder (TypeScript + Zustand store)
 *
 * Key Features:
 * 1. Unified access level terminology (guest/registered/premium)
 * 2. Data transformation between different data structures
 * 3. State synchronization utilities
 * 4. Validation helpers
 * 5. Mode switching capabilities
 *
 * Access Level Mapping:
 * - guest: Unregistered users (preview content)
 * - registered: Logged-in users (basic content)
 * - premium: Paid subscribers (full content)
 */

// =============================================================================
// CONSTANTS AND CONFIGURATION
// =============================================================================

export const ACCESS_LEVELS = {
  GUEST: 'guest',
  REGISTERED: 'registered',
  PREMIUM: 'premium',
};

export const ACCESS_LEVEL_LABELS = {
  [ACCESS_LEVELS.GUEST]: 'Guest - Preview for Unregistered Users',
  [ACCESS_LEVELS.REGISTERED]: 'Registered - Logged In Users',
  [ACCESS_LEVELS.PREMIUM]: 'Premium - Paid Subscribers Only',
};

export const ACCESS_LEVEL_PRIORITIES = {
  [ACCESS_LEVELS.GUEST]: 1,
  [ACCESS_LEVELS.REGISTERED]: 2,
  [ACCESS_LEVELS.PREMIUM]: 3,
};

export const DIFFICULTY_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  ALL_LEVELS: 'all_levels',
};

export const LESSON_TYPES = {
  VIDEO: 'video',
  READING: 'reading',
  INTERACTIVE: 'interactive',
  QUIZ: 'quiz',
  LAB: 'lab',
};

export const EDITOR_MODES = {
  WIZARD: 'wizard',
  TRADITIONAL: 'traditional',
  BUILDER: 'builder',
};

// =============================================================================
// DATA TRANSFORMATION UTILITIES
// =============================================================================

/**
 * Normalize course data to unified format
 * @param {Object} courseData - Course data from any mode
 * @param {string} sourceMode - Source mode ('wizard', 'traditional', 'builder')
 * @returns {Object} Normalized course data
 */
export function normalizeCourseData(courseData, sourceMode = 'wizard') {
  if (!courseData) return null;

  const normalized = {
    id: courseData.id || null,
    slug: courseData.slug || null,
    title: courseData.title || '',
    subtitle: courseData.subtitle || '',
    description: courseData.description || '',
    category_id: courseData.category_id || courseData.categoryId || null,
    level: normalizeDifficultyLevel(courseData.level),
    price: normalizePrice(courseData.price),
    discount_price: normalizePrice(courseData.discount_price),
    thumbnail: normalizeThumbnail(courseData.thumbnail),
    is_featured: Boolean(courseData.is_featured),
    is_published: Boolean(courseData.is_published),
    has_certificate: Boolean(courseData.has_certificate),
    duration_minutes: courseData.duration_minutes || 0,
    duration_display: courseData.duration_display || '',
    requirements: normalizeArray(courseData.requirements),
    skills: normalizeArray(courseData.skills),
    modules: normalizeModules(courseData.modules || [], sourceMode),
    // Metadata
    created_at: courseData.created_at || courseData.createdAt,
    updated_at: courseData.updated_at || courseData.updatedAt,
    // Mode-specific tracking
    _sourceMode: sourceMode,
    _lastSyncAt: new Date().toISOString(),
  };

  return normalized;
}

/**
 * Transform course data for specific target mode
 * @param {Object} courseData - Normalized course data
 * @param {string} targetMode - Target mode ('wizard', 'traditional', 'builder')
 * @returns {Object} Mode-specific course data
 */
export function transformForMode(courseData, targetMode) {
  if (!courseData) return null;

  const base = { ...courseData };

  switch (targetMode) {
    case EDITOR_MODES.WIZARD:
      return transformForWizard(base);

    case EDITOR_MODES.TRADITIONAL:
      return transformForTraditional(base);

    case EDITOR_MODES.BUILDER:
      return transformForBuilder(base);

    default:
      console.warn(`Unknown target mode: ${targetMode}`);
      return base;
  }
}

/**
 * Transform for CourseWizard mode (React Context)
 */
function transformForWizard(data) {
  return {
    ...data,
    // Ensure wizard-specific structure
    modules:
      data.modules?.map(module => ({
        ...module,
        lessons: module.lessons?.map(lesson => ({
          ...lesson,
          access_level: normalizeAccessLevel(
            lesson.access_level || lesson.accessLevel
          ),
          // Ensure tiered content fields exist
          content: lesson.content || lesson.premium_content || '',
          guest_content: lesson.guest_content || '',
          registered_content: lesson.registered_content || lesson.content || '',
          premium_content: lesson.premium_content || lesson.content || '',
          is_free_preview: Boolean(lesson.is_free_preview),
        })),
      })) || [],
  };
}

/**
 * Transform for Traditional Editor mode
 */
function transformForTraditional(data) {
  return {
    ...data,
    // Convert arrays to strings for form compatibility
    requirements: Array.isArray(data.requirements)
      ? data.requirements.join(', ')
      : data.requirements || '',
    skills: Array.isArray(data.skills)
      ? data.skills.join(', ')
      : data.skills || '',
    // Ensure price is numeric for forms
    price: parseFloat(data.price) || 0,
    discount_price: parseFloat(data.discount_price) || 0,
  };
}

/**
 * Transform for CourseBuilder mode (TypeScript/Zustand)
 */
function transformForBuilder(data) {
  return {
    ...data,
    // Use TypeScript-friendly naming
    categoryId: data.category_id,
    modules:
      data.modules?.map(module => ({
        ...module,
        lessons: module.lessons?.map(lesson => ({
          ...lesson,
          accessLevel: normalizeAccessLevel(
            lesson.access_level || lesson.accessLevel
          ),
          // Simplify content structure for builder
          content: lesson.content || lesson.premium_content || '',
        })),
      })) || [],
  };
}

// =============================================================================
// NORMALIZATION HELPERS
// =============================================================================

/**
 * Normalize access level terminology
 * Maps old terminology to new unified standard
 */
export function normalizeAccessLevel(level) {
  if (!level) return ACCESS_LEVELS.REGISTERED;

  const normalizedLevel = level.toLowerCase();

  // Map old terminology to new
  const mapping = {
    basic: ACCESS_LEVELS.GUEST,
    intermediate: ACCESS_LEVELS.REGISTERED,
    advanced: ACCESS_LEVELS.PREMIUM,
    all: ACCESS_LEVELS.GUEST,
    // Keep existing correct values
    guest: ACCESS_LEVELS.GUEST,
    registered: ACCESS_LEVELS.REGISTERED,
    premium: ACCESS_LEVELS.PREMIUM,
  };

  return mapping[normalizedLevel] || ACCESS_LEVELS.REGISTERED;
}

/**
 * Normalize difficulty level
 */
function normalizeDifficultyLevel(level) {
  if (!level) return DIFFICULTY_LEVELS.BEGINNER;

  const validLevels = Object.values(DIFFICULTY_LEVELS);
  return validLevels.includes(level) ? level : DIFFICULTY_LEVELS.BEGINNER;
}

/**
 * Normalize price values
 */
function normalizePrice(price) {
  if (price === null || price === undefined || price === '') return 0;
  const numPrice = parseFloat(price);
  return isNaN(numPrice) ? 0 : Math.max(0, numPrice);
}

/**
 * Normalize thumbnail handling
 */
function normalizeThumbnail(thumbnail) {
  if (!thumbnail) return null;

  // Handle array-wrapped thumbnails
  if (Array.isArray(thumbnail)) {
    return thumbnail.length > 0 ? thumbnail[0] : null;
  }

  return thumbnail;
}

/**
 * Normalize array fields (requirements, skills)
 */
function normalizeArray(field) {
  if (!field) return [];

  if (Array.isArray(field)) {
    return field.filter(item => item && item.trim());
  }

  if (typeof field === 'string') {
    return field
      .split(',')
      .map(item => item.trim())
      .filter(Boolean);
  }

  return [];
}

/**
 * Normalize modules array
 */
function normalizeModules(modules, sourceMode) {
  if (!Array.isArray(modules)) return [];

  return modules.map(module => ({
    id: module.id,
    title: module.title || '',
    description: module.description || '',
    duration_minutes: module.duration_minutes || 0,
    duration_display: module.duration_display || '',
    order: module.order || 1,
    lessons: normalizeLessons(module.lessons || [], sourceMode),
  }));
}

/**
 * Normalize lessons array
 */
function normalizeLessons(lessons, sourceMode) {
  if (!Array.isArray(lessons)) return [];

  return lessons.map(lesson => ({
    id: lesson.id,
    title: lesson.title || '',
    content: lesson.content || '',
    duration_minutes: lesson.duration_minutes || 0,
    duration_display: lesson.duration_display || '',
    type: lesson.type || LESSON_TYPES.VIDEO,
    order: lesson.order || 1,
    access_level: normalizeAccessLevel(
      lesson.access_level || lesson.accessLevel
    ),
    is_free_preview: Boolean(lesson.is_free_preview),
    // Preserve tiered content
    guest_content: lesson.guest_content || '',
    registered_content: lesson.registered_content || lesson.content || '',
    premium_content: lesson.premium_content || lesson.content || '',
  }));
}

// =============================================================================
// VALIDATION UTILITIES
// =============================================================================

/**
 * Validate course data for specific mode
 * @param {Object} courseData - Course data to validate
 * @param {string} mode - Target mode
 * @returns {Object} Validation result { isValid, errors }
 */
export function validateCourseData(courseData, mode = 'wizard') {
  const errors = {};
  let isValid = true;

  // Common validations
  if (!courseData.title || courseData.title.trim().length < 3) {
    errors.title = 'Course title must be at least 3 characters long';
    isValid = false;
  }

  if (!courseData.category_id && !courseData.categoryId) {
    errors.category = 'Category is required';
    isValid = false;
  }

  if (!courseData.description || courseData.description.trim().length < 20) {
    errors.description =
      'Course description must be at least 20 characters long';
    isValid = false;
  }

  // Price validation
  const price = parseFloat(courseData.price);
  if (isNaN(price) || price < 0) {
    errors.price = 'Price must be a valid number greater than or equal to 0';
    isValid = false;
  }

  // Mode-specific validations
  switch (mode) {
    case EDITOR_MODES.WIZARD:
      return validateWizardData(courseData, errors, isValid);

    case EDITOR_MODES.TRADITIONAL:
      return validateTraditionalData(courseData, errors, isValid);

    case EDITOR_MODES.BUILDER:
      return validateBuilderData(courseData, errors, isValid);

    default:
      return { isValid, errors };
  }
}

/**
 * Validate wizard-specific requirements
 */
function validateWizardData(courseData, errors, isValid) {
  if (!courseData.modules || courseData.modules.length === 0) {
    errors.modules = 'At least one module is required';
    isValid = false;
  } else {
    // Validate modules
    courseData.modules.forEach((module, index) => {
      if (!module.title || module.title.trim() === '') {
        errors[`module_${index}_title`] =
          `Module ${index + 1} must have a title`;
        isValid = false;
      }

      // Validate lessons
      if (!module.lessons || module.lessons.length === 0) {
        errors[`module_${index}_lessons`] =
          `Module ${index + 1} must have at least one lesson`;
        isValid = false;
      } else {
        module.lessons.forEach((lesson, lessonIndex) => {
          if (!lesson.title || lesson.title.trim() === '') {
            errors[`lesson_${index}_${lessonIndex}_title`] =
              `Lesson ${lessonIndex + 1} in module ${index + 1} must have a title`;
            isValid = false;
          }

          // Validate access levels
          if (!Object.values(ACCESS_LEVELS).includes(lesson.access_level)) {
            errors[`lesson_${index}_${lessonIndex}_access`] =
              `Invalid access level for lesson ${lessonIndex + 1} in module ${index + 1}`;
            isValid = false;
          }
        });
      }
    });
  }

  return { isValid, errors };
}

/**
 * Validate traditional editor requirements
 */
function validateTraditionalData(courseData, errors, isValid) {
  // Traditional editor focuses on basic course info
  return { isValid, errors };
}

/**
 * Validate builder requirements
 */
function validateBuilderData(courseData, errors, isValid) {
  // Builder has TypeScript validation through Zod schemas
  return { isValid, errors };
}

// =============================================================================
// STATE SYNCHRONIZATION UTILITIES
// =============================================================================

/**
 * Synchronize data between different editor modes
 * @param {Object} sourceData - Data from source mode
 * @param {string} sourceMode - Source mode identifier
 * @param {string} targetMode - Target mode identifier
 * @returns {Object} Synchronized data for target mode
 */
export function syncBetweenModes(sourceData, sourceMode, targetMode) {
  if (sourceMode === targetMode) {
    return sourceData;
  }

  console.log(`Syncing course data: ${sourceMode} → ${targetMode}`);

  // Step 1: Normalize source data
  const normalized = normalizeCourseData(sourceData, sourceMode);

  // Step 2: Transform for target mode
  const transformed = transformForMode(normalized, targetMode);

  // Step 3: Validate transformed data
  const validation = validateCourseData(transformed, targetMode);

  if (!validation.isValid) {
    console.warn('Data sync validation errors:', validation.errors);
  }

  return {
    data: transformed,
    validation,
    syncMetadata: {
      sourceMode,
      targetMode,
      syncedAt: new Date().toISOString(),
      hasValidationErrors: !validation.isValid,
    },
  };
}

/**
 * Create mode-switching handler
 * @param {Object} options - Configuration options
 * @returns {Function} Mode switching function
 */
export function createModeSwitcher(options = {}) {
  const {
    onBeforeSwitch = () => {},
    onAfterSwitch = () => {},
    autoSave = true,
    showConfirmation = true,
  } = options;

  return async (currentData, currentMode, targetMode, navigate) => {
    try {
      // Pre-switch callback
      await onBeforeSwitch(currentData, currentMode, targetMode);

      // Show confirmation if enabled
      if (showConfirmation) {
        const confirmed = window.confirm(
          `Switch to ${targetMode} mode? Your progress will be saved.`
        );

        if (!confirmed) {
          return false;
        }
      }

      // Auto-save current data if enabled
      if (autoSave && currentData) {
        await saveCurrentData(currentData, currentMode);
      }

      // Store editor mode preference
      localStorage.setItem('editorMode', targetMode);

      // Sync data for target mode
      const syncResult = syncBetweenModes(currentData, currentMode, targetMode);

      // Navigate to target mode
      const targetUrl = getTargetModeUrl(targetMode, currentData);
      navigate(targetUrl);

      // Post-switch callback
      await onAfterSwitch(syncResult.data, currentMode, targetMode);

      return true;
    } catch (error) {
      console.error('Mode switch failed:', error);
      throw error;
    }
  };
}

/**
 * Get URL for target mode
 */
function getTargetModeUrl(targetMode, courseData) {
  const baseUrl = '/instructor/courses';
  const identifier = courseData?.slug || courseData?.id;

  switch (targetMode) {
    case EDITOR_MODES.WIZARD:
      return identifier ? `${baseUrl}/wizard/${identifier}` : `${baseUrl}/new`;

    case EDITOR_MODES.TRADITIONAL:
      return identifier
        ? `${baseUrl}/${identifier}/edit`
        : `${baseUrl}/traditional/new`;

    case EDITOR_MODES.BUILDER:
      return identifier
        ? `${baseUrl}/builder/${identifier}`
        : `${baseUrl}/builder`;

    default:
      return baseUrl;
  }
}

/**
 * Save current data before mode switch
 */
async function saveCurrentData(courseData, currentMode) {
  try {
    // Dynamic import to avoid circular dependencies
    const { default: instructorService } = await import(
      '../services/instructorService'
    );

    if (courseData.id || courseData.slug) {
      // Update existing course
      const identifier = courseData.slug || courseData.id;
      await instructorService.updateCourse(identifier, courseData);
    } else if (courseData.title && courseData.category_id) {
      // Create new course
      await instructorService.createCourse(courseData);
    }

    console.log('Course data saved before mode switch');
  } catch (error) {
    console.error('Failed to save data before mode switch:', error);
    throw error;
  }
}

// =============================================================================
// DRAG-AND-DROP STATE MANAGEMENT
// =============================================================================

/**
 * Synchronize drag-and-drop order changes across modes
 * @param {Array} items - Reordered items
 * @param {string} itemType - Type of items ('modules', 'lessons')
 * @param {Object} context - Context information
 * @returns {Array} Updated items with correct order
 */
export function syncDragDropOrder(items, itemType, context = {}) {
  if (!Array.isArray(items)) return [];

  // Update order property based on new positions
  const updatedItems = items.map((item, index) => ({
    ...item,
    order: index + 1,
  }));

  console.log(
    `Synced ${itemType} order:`,
    updatedItems.map(item => ({
      id: item.id,
      title: item.title,
      order: item.order,
    }))
  );

  return updatedItems;
}

/**
 * Create drag-and-drop handler that syncs across modes
 */
export function createDragDropHandler(updateFunction, itemType = 'items') {
  return result => {
    if (!result.destination) return;

    const { source, destination } = result;

    if (source.index === destination.index) return;

    // This will be implemented by the calling component
    // The component should pass its current items and get back synced items
    console.log(`Drag drop ${itemType}:`, {
      source: source.index,
      destination: destination.index,
    });

    // Return a function that the component can call with its current items
    return currentItems => {
      const reorderedItems = Array.from(currentItems);
      const [removed] = reorderedItems.splice(source.index, 1);
      reorderedItems.splice(destination.index, 0, removed);

      const syncedItems = syncDragDropOrder(reorderedItems, itemType);

      // Update using the provided function
      updateFunction(syncedItems);

      return syncedItems;
    };
  };
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Check if access level is valid
 */
export function isValidAccessLevel(level) {
  return Object.values(ACCESS_LEVELS).includes(level);
}

/**
 * Get access level priority for comparison
 */
export function getAccessLevelPriority(level) {
  return ACCESS_LEVEL_PRIORITIES[level] || 0;
}

/**
 * Compare access levels
 */
export function compareAccessLevels(level1, level2) {
  return getAccessLevelPriority(level1) - getAccessLevelPriority(level2);
}

/**
 * Get current editor mode from URL or localStorage
 */
export function getCurrentEditorMode() {
  const path = window.location.pathname;

  if (path.includes('/wizard')) {
    return EDITOR_MODES.WIZARD;
  } else if (path.includes('/builder')) {
    return EDITOR_MODES.BUILDER;
  } else if (path.includes('/edit')) {
    return EDITOR_MODES.TRADITIONAL;
  }

  return localStorage.getItem('editorMode') || EDITOR_MODES.WIZARD;
}

/**
 * Deep clone object to avoid mutation
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof File) return obj; // Don't clone File objects
  if (Array.isArray(obj)) return obj.map(item => deepClone(item));

  const cloned = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
}

/**
 * Generate temporary ID for new items
 */
export function generateTempId() {
  return `temp_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
}

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  // Constants
  ACCESS_LEVELS,
  ACCESS_LEVEL_LABELS,
  ACCESS_LEVEL_PRIORITIES,
  DIFFICULTY_LEVELS,
  LESSON_TYPES,
  EDITOR_MODES,

  // Core functions
  normalizeCourseData,
  transformForMode,
  validateCourseData,
  syncBetweenModes,
  createModeSwitcher,

  // Drag and drop
  syncDragDropOrder,
  createDragDropHandler,

  // Utilities
  normalizeAccessLevel,
  isValidAccessLevel,
  getAccessLevelPriority,
  compareAccessLevels,
  getCurrentEditorMode,
  deepClone,
  generateTempId,
};
