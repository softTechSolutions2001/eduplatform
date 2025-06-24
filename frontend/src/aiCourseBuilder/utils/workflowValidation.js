/**
 * Consolidated workflow validation utilities for AI Course Builder
 *
 * This file combines validation functions from:
 * - aiWorkflowUtils.js
 * - validationHelpers.js
 */

/**
 * Form validation utilities
 */
export const validateEmail = email => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUrl = url => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateRequired = (value, fieldName) => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName} is required`;
  }
  if (Array.isArray(value) && value.length === 0) {
    return `${fieldName} must have at least one item`;
  }
  return null;
};

export const validateMinLength = (value, minLength, fieldName) => {
  if (value && value.length < minLength) {
    return `${fieldName} must be at least ${minLength} characters`;
  }
  return null;
};

export const validateMaxLength = (value, maxLength, fieldName) => {
  if (value && value.length > maxLength) {
    return `${fieldName} must not exceed ${maxLength} characters`;
  }
  return null;
};

export const validateRange = (value, min, max, fieldName) => {
  if (value !== undefined && value !== null) {
    if (value < min) {
      return `${fieldName} must be at least ${min}`;
    }
    if (value > max) {
      return `${fieldName} must not exceed ${max}`;
    }
  }
  return null;
};

export const validateArrayLength = (array, min, max, fieldName) => {
  if (!array) return `${fieldName} is required`;
  if (!Array.isArray(array)) return `${fieldName} must be a list`;

  if (array.length < min) {
    return `${fieldName} must have at least ${min} items`;
  }
  if (max && array.length > max) {
    return `${fieldName} must not exceed ${max} items`;
  }
  return null;
};

/**
 * Create a field validator function
 */
export const createFieldValidator = (fieldName, rules = {}) => {
  return value => {
    if (rules.required && !value) {
      return `${fieldName} is required`;
    }
    if (rules.minLength && value && value.length < rules.minLength) {
      return `${fieldName} must be at least ${rules.minLength} characters`;
    }
    if (rules.maxLength && value && value.length > rules.maxLength) {
      return `${fieldName} must be no more than ${rules.maxLength} characters`;
    }
    if (rules.pattern && value && !rules.pattern.test(value)) {
      return rules.patternMessage || `${fieldName} format is invalid`;
    }
    return null;
  };
};

/**
 * Generic field validation
 */
export const validateField = (value, fieldName, rules = {}) => {
  const validator = createFieldValidator(fieldName, rules);
  const error = validator(value);
  return { isValid: !error, error };
};

/**
 * Generic data validation
 */
export const validateData = (data, schema) => {
  const errors = {};
  for (const [fieldName, rules] of Object.entries(schema)) {
    const value = data[fieldName];
    const result = validateField(value, fieldName, rules);
    if (!result.isValid) {
      errors[fieldName] = result.error;
    }
  }
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

/**
 * Learning objectives validation
 */
export const validateLearningObjectives = objectives => {
  if (!Array.isArray(objectives)) {
    return { isValid: false, error: 'Learning objectives must be an array' };
  }
  if (objectives.length < 3) {
    return {
      isValid: false,
      error: 'Course must have at least 3 learning objectives',
    };
  }
  if (objectives.length > 10) {
    return {
      isValid: false,
      error: 'Course cannot have more than 10 learning objectives',
    };
  }
  for (let i = 0; i < objectives.length; i++) {
    if (!objectives[i] || objectives[i].trim().length < 10) {
      return {
        isValid: false,
        error: `Objective ${i + 1} must be at least 10 characters`,
      };
    }
  }
  return { isValid: true };
};

/**
 * Content quality validation
 */
export const validateContentQuality = content => {
  if (!content || content.trim().length < 100) {
    return { isValid: false, error: 'Content must be at least 100 characters' };
  }
  return { isValid: true };
};

/**
 * Complete course validation
 */
export const validateCompleteCourse = courseData => {
  const errors = [];

  const basicInfo = validateCourseBasicInfo(courseData);
  if (!basicInfo.isValid) {
    errors.push(...Object.values(basicInfo.errors));
  }

  if (courseData.objectives) {
    const objectives = validateLearningObjectives(courseData.objectives);
    if (!objectives.isValid) {
      errors.push(objectives.error);
    }
  }

  if (courseData.outline) {
    const outline = validateCourseOutline(courseData.outline);
    if (!outline.isValid) {
      errors.push(...Object.values(outline.errors));
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Title uniqueness validation (placeholder - needs API call)
 */
export const validateTitleUniqueness = async (
  title,
  currentCourseId = null
) => {
  // This would typically make an API call to check title uniqueness
  // For now, return a simple validation
  if (!title || title.trim().length < 5) {
    return { isValid: false, error: 'Title must be at least 5 characters' };
  }
  return { isValid: true };
};

/**
 * Course title validation
 */
export const validateCourseTitle = title => {
  if (!title || title.trim() === '') {
    return {
      isValid: false,
      message: 'Course title is required',
    };
  }

  if (title.length < 5) {
    return {
      isValid: false,
      message: 'Course title must be at least 5 characters',
    };
  }

  if (title.length > 100) {
    return {
      isValid: false,
      message: 'Course title must not exceed 100 characters',
    };
  }

  return { isValid: true };
};

/**
 * Course description validation
 */
export const validateCourseDescription = description => {
  if (!description || description.trim() === '') {
    return {
      isValid: false,
      message: 'Course description is required',
    };
  }

  if (description.length < 50) {
    return {
      isValid: false,
      message: 'Course description must be at least 50 characters',
    };
  }

  if (description.length > 2000) {
    return {
      isValid: false,
      message: 'Course description must not exceed 2000 characters',
    };
  }

  return { isValid: true };
};

/**
 * Course basic info validation
 */
export const validateCourseBasicInfo = data => {
  const errors = {};

  if (!data.title) {
    errors.title = 'Title is required';
  } else if (data.title.length < 5) {
    errors.title = 'Title must be at least 5 characters';
  } else if (data.title.length > 100) {
    errors.title = 'Title must not exceed 100 characters';
  }

  if (!data.description) {
    errors.description = 'Description is required';
  } else if (data.description.length < 50) {
    errors.description = 'Description must be at least 50 characters';
  } else if (data.description.length > 2000) {
    errors.description = 'Description must not exceed 2000 characters';
  }

  if (!data.categoryId) {
    errors.categoryId = 'Category is required';
  }

  if (!data.level) {
    errors.level = 'Level is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

/**
 * Course outline validation
 */
export const validateCourseOutline = outline => {
  const errors = {};

  if (!outline.modules || !Array.isArray(outline.modules)) {
    errors.modules = 'Modules are required';
    return { isValid: false, errors };
  }

  if (outline.modules.length < 2) {
    errors.modules = 'Course must have at least 2 modules';
  }

  // No longer returning early if modules.length > 10 as this was a bug
  // Fix according to code review instruction

  outline.modules.forEach((module, index) => {
    if (!module.title) {
      errors[`module_${index}_title`] = `Module ${index + 1} must have a title`;
    }

    if (!module.lessons || !Array.isArray(module.lessons)) {
      errors[`module_${index}_lessons`] =
        `Module ${index + 1} lessons must be a list`;
      return;
    }

    if (module.lessons.length < 2) {
      errors[`module_${index}_lessons`] =
        `Module ${index + 1} must have at least 2 lessons`;
    } else if (module.lessons.length > 15) {
      errors[`module_${index}_lessons`] =
        `Module ${index + 1} should not have more than 15 lessons`;
    }

    module.lessons.forEach((lesson, lessonIndex) => {
      if (!lesson.title) {
        errors[`module_${index}_lesson_${lessonIndex}_title`] =
          `Lesson ${lessonIndex + 1} in Module ${index + 1} must have a title`;
      }
    });
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

/**
 * Course data validation - comprehensive validation for all course data
 */
export const validateCourseData = courseData => {
  const errors = {};

  // Basic info validation
  if (!courseData.title) {
    errors.title = 'Course title is required';
  } else if (courseData.title.length < 5) {
    errors.title = 'Course title must be at least 5 characters';
  } else if (courseData.title.length > 100) {
    errors.title = 'Course title must not exceed 100 characters';
  }

  if (!courseData.description) {
    errors.description = 'Course description is required';
  } else if (courseData.description.length < 50) {
    errors.description = 'Course description must be at least 50 characters';
  }

  if (!courseData.categoryId) {
    errors.categoryId = 'Course category is required';
  }

  if (!courseData.level) {
    errors.level = 'Course level is required';
  }

  // Learning objectives validation
  if (!courseData.objectives || courseData.objectives.length < 3) {
    errors.objectives = 'Course must have at least 3 learning objectives';
  }

  // Outline validation
  if (courseData.outline) {
    if (!courseData.outline.modules || courseData.outline.modules.length < 2) {
      errors.outline = 'Course must have at least 2 modules';
    }

    courseData.outline.modules?.forEach((module, index) => {
      if (!module.title) {
        errors[`module_${index}_title`] =
          `Module ${index + 1} must have a title`;
      }
      if (!module.lessons || module.lessons.length < 2) {
        errors[`module_${index}_lessons`] =
          `Module ${index + 1} must have at least 2 lessons`;
      }
    });
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    validatedAt: new Date().toISOString(),
  };
};

/**
 * Validate basic info for course creation
 */
export const validateBasicInfo = info => {
  const errors = {};

  if (!info.title) {
    errors.title = 'Title is required';
  } else if (info.title.length < 5) {
    errors.title = 'Title must be at least 5 characters';
  } else if (info.title.length > 100) {
    errors.title = 'Title must not exceed 100 characters';
  }

  if (!info.description) {
    errors.description = 'Description is required';
  } else if (info.description.length < 50) {
    errors.description = 'Description must be at least 50 characters';
  }

  if (!info.categoryId) {
    errors.categoryId = 'Category is required';
  }

  if (!info.level) {
    errors.level = 'Level is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const PHASES = {
  BASIC_INFO: 'basic-info',
  LEARNING_OBJECTIVES: 'learning-objectives',
  OUTLINE_GENERATION: 'outline-generation',
  CONTENT_CREATION: 'content-creation',
  REVIEW_FINALIZE: 'review-finalize',
};

export const VALIDATION_SCHEMAS = {
  basicInfo: {
    title: { required: true, minLength: 5, maxLength: 100 },
    description: { required: true, minLength: 20, maxLength: 1000 },
    category: { required: true },
    level: {
      required: true,
      options: ['beginner', 'intermediate', 'advanced'],
    },
    duration: { required: true, min: 30, max: 600 },
  },
  objectives: {
    objectives: { required: true, minItems: 3, maxItems: 10 },
  },
  outline: {
    modules: { required: true, minItems: 1, maxItems: 20 },
  },
};

export const PHASE_CONFIG = {
  [PHASES.BASIC_INFO]: {
    title: 'Basic Information',
    description: 'Define course fundamentals and target audience',
    estimatedTime: '5-10 minutes',
    requiredFields: ['title', 'description', 'category', 'level', 'duration'],
    validations: {
      title: { minLength: 5, maxLength: 100 },
      description: { minLength: 50, maxLength: 500 },
      duration: { min: 1, max: 200 },
    },
  },
  [PHASES.LEARNING_OBJECTIVES]: {
    title: 'Learning Objectives',
    description: 'Set clear, measurable learning outcomes',
    estimatedTime: '10-15 minutes',
    requiredFields: ['objectives'],
    validations: {
      objectives: { minCount: 3, maxCount: 8 },
    },
  },
  [PHASES.OUTLINE_GENERATION]: {
    title: 'Course Outline',
    description: 'AI-generated course structure and modules',
    estimatedTime: '2-5 minutes',
    requiredFields: ['outline'],
    validations: {
      modules: { minCount: 2, maxCount: 12 },
      lessonsPerModule: { min: 2, max: 10 },
    },
  },
  [PHASES.CONTENT_CREATION]: {
    title: 'Content Creation',
    description: 'Generate detailed lesson content',
    estimatedTime: '15-30 minutes',
    requiredFields: ['content'],
    validations: {},
  },
  [PHASES.REVIEW_FINALIZE]: {
    title: 'Review & Publish',
    description: 'Review the complete course before publishing',
    estimatedTime: '5-10 minutes',
    requiredFields: [],
    validations: {},
  },
};

/**
 * Comprehensive validation with phased workflow
 */
export const validateCourseWithWorkflow = courseData => {
  return {
    isValid: true,
    phase: {
      basicInfo: validateCourseBasicInfo(courseData),
      objectives: courseData.objectives
        ? { isValid: courseData.objectives.length >= 3 }
        : { isValid: false },
      outline: validateCourseOutline(courseData.outline || {}),
    },
    validatedAt: new Date().toISOString(),
  };
};
