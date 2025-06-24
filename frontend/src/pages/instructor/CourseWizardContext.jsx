/**
 * File: frontend/src/pages/instructor/CourseWizardContext.jsx
 * Version: 2.3.1
 * Date: 2025-05-28 17:25:05
 * Author: mohithasanthanam, sujibeautysalon
 * Last Modified: 2025-05-28 17:25:05 UTC
 *
 * Enhanced Course Wizard Context with HMR-safe ID Generation and Performance Improvements
 *
 * IMPROVEMENTS BASED ON TECHNICAL REVIEW:
 * 1. FIXED: Changed ID counter from global variable to useRef for Hot Module Replacement safety
 * 2. ADDED: Memoized heavy selectors (isStepCompleted) with useMemo for better performance
 * 3. IMPROVED: Added explicit imports for useRef and useMemo hooks
 * 4. ENHANCED: Better performance with dependency array optimization
 * 5. ADDED: Enhanced thumbnail handling in updateCourse to prevent array wrapping issues
 * 6. ADDED: Double-safety thumbnail handling in reducer for array unwrapping
 * 7. ADDED: Empty requirements/skills string handling to prevent validation errors
 * 8. FIXED: Added access_level fallback for new lessons
 * 9. ADDED: Cache clearing after wizard reset
 *
 * Previous improvements:
 * 1. Added support for both slug and ID-based operations
 * 2. Enhanced error handling with detailed feedback
 * 3. Improved save state management with status tracking
 * 4. Fixed mutation issues with module and lesson arrays
 * 5. Enhanced ID generation to avoid collisions
 * 6. Improved validation for all wizard steps
 * 7. CRITICAL FIX: Changed access_level default from 'all' to 'registered'
 *
 * This context manages state for the course wizard across steps:
 * - Course metadata (title, description, etc.)
 * - Module and lesson structure
 * - Current step tracking
 * - Validation state
 * - Auto-save functionality
 *
 * Variables to modify:
 * - initialState: Default starting state for new courses
 * - ACTIONS: Reducer action types for state modifications
 *
 * Connected files that need to be consistent:
 * - frontend/src/pages/instructor/CourseWizard.jsx - Main wizard component
 * - frontend/src/services/instructorService.js - API calls
 * - backend/instructor_portal/views.py - API endpoints
 * - backend/instructor_portal/serializers.py - Data validation
 */

import React, {
  createContext,
  useContext,
  useState,
  useReducer,
  useRef,
  useMemo,
} from 'react';
import authPersist from '../../utils/authPersist';
import instructorService from '../../services/instructorService';
import {
  ACCESS_LEVELS,
  EDITOR_MODES,
  normalizeCourseData,
  normalizeAccessLevel,
  createModeSwitcher,
  generateTempId as syncGenerateTempId,
} from '../../utils/courseDataSync';

// Initial state for the course wizard
const initialState = {
  // Course details
  courseData: {
    title: '',
    subtitle: '',
    description: '',
    category_id: '',
    level: 'beginner',
    price: 0,
    thumbnail: null,
    is_featured: false,
    requirements: [],
    skills: [],
    has_certificate: false,
    duration: '',
    slug: null, // Added to track course slug
    id: null, // Added to track course ID
  },

  // Modules array
  modules: [],

  // Current editing state
  currentStep: 1,
  totalSteps: 5,
  isCompleted: false,

  // Save status
  isSaving: false,
  lastSavedAt: null,

  // Validation and errors
  errors: {},
  isDirty: false,
};

// Actions for the reducer
const ACTIONS = {
  UPDATE_COURSE: 'UPDATE_COURSE',
  ADD_MODULE: 'ADD_MODULE',
  UPDATE_MODULE: 'UPDATE_MODULE',
  REMOVE_MODULE: 'REMOVE_MODULE',
  ADD_LESSON: 'ADD_LESSON',
  UPDATE_LESSON: 'UPDATE_LESSON',
  REMOVE_LESSON: 'REMOVE_LESSON',
  SET_STEP: 'SET_STEP',
  SAVE_STARTED: 'SAVE_STARTED',
  SAVE_COMPLETED: 'SAVE_COMPLETED',
  SAVE_FAILED: 'SAVE_FAILED',
  PUBLISH_COURSE: 'PUBLISH_COURSE',
  RESET_WIZARD: 'RESET_WIZARD',
  SET_ERRORS: 'SET_ERRORS',
  CLEAR_ERRORS: 'CLEAR_ERRORS',
  MARK_DIRTY: 'MARK_DIRTY',
  MARK_CLEAN: 'MARK_CLEAN',
};

// Helper function to process thumbnail
function processThumbnail(thumbnail) {
  if (Array.isArray(thumbnail)) {
    console.warn('Found array-wrapped thumbnail, unwrapping');
    return thumbnail.length > 0 ? thumbnail[0] : null;
  }
  return thumbnail;
}

// Helper function to process requirements/skills
function processArrayFields(data) {
  const processed = { ...data };

  if (processed.requirements === '') {
    console.log('Converting empty requirements string to empty array');
    processed.requirements = [];
  }

  if (processed.skills === '') {
    console.log('Converting empty skills string to empty array');
    processed.skills = [];
  }

  return processed;
}

// Reducer function
function courseWizardReducer(state, action) {
  switch (action.type) {
    case ACTIONS.UPDATE_COURSE: {
      // Handle both thumbnail arrays and empty requirements/skills in the reducer
      const payload = { ...action.payload };

      // Process thumbnail if present
      if ('thumbnail' in payload) {
        payload.thumbnail = processThumbnail(payload.thumbnail);
      }

      // Process requirements/skills if present
      if ('requirements' in payload && payload.requirements === '') {
        payload.requirements = [];
      }

      if ('skills' in payload && payload.skills === '') {
        payload.skills = [];
      }

      return {
        ...state,
        courseData: {
          ...state.courseData,
          ...payload,
        },
        isDirty: true,
      };
    }

    case ACTIONS.ADD_MODULE:
      return {
        ...state,
        modules: [...state.modules, action.payload],
        isDirty: true,
      };

    case ACTIONS.UPDATE_MODULE:
      return {
        ...state,
        modules: state.modules.map(module =>
          module.id === action.payload.id
            ? { ...module, ...action.payload }
            : module
        ),
        isDirty: true,
      };

    case ACTIONS.REMOVE_MODULE:
      return {
        ...state,
        modules: state.modules.filter(module => module.id !== action.payload),
        isDirty: true,
      };

    case ACTIONS.ADD_LESSON:
      return {
        ...state,
        modules: state.modules.map(module =>
          module.id === action.payload.moduleId
            ? {
                ...module,
                lessons: Array.isArray(module.lessons)
                  ? [...module.lessons, action.payload.lesson]
                  : [action.payload.lesson],
              }
            : module
        ),
        isDirty: true,
      };

    case ACTIONS.UPDATE_LESSON:
      return {
        ...state,
        modules: state.modules.map(module =>
          module.id === action.payload.moduleId
            ? {
                ...module,
                lessons: Array.isArray(module.lessons)
                  ? module.lessons.map(lesson =>
                      lesson.id === action.payload.lesson.id
                        ? { ...lesson, ...action.payload.lesson }
                        : lesson
                    )
                  : [action.payload.lesson], // If module has no lessons array, create one with this lesson
              }
            : module
        ),
        isDirty: true,
      };

    case ACTIONS.REMOVE_LESSON:
      return {
        ...state,
        modules: state.modules.map(module =>
          module.id === action.payload.moduleId
            ? {
                ...module,
                lessons: Array.isArray(module.lessons)
                  ? module.lessons.filter(
                      lesson => lesson.id !== action.payload.lessonId
                    )
                  : [],
              }
            : module
        ),
        isDirty: true,
      };

    case ACTIONS.SET_STEP:
      return {
        ...state,
        currentStep: action.payload,
      };

    case ACTIONS.SAVE_STARTED:
      return {
        ...state,
        isSaving: true,
      };

    case ACTIONS.SAVE_COMPLETED: {
      // Process saved course data if provided
      let savedCourseData = action.payload ? { ...action.payload } : null;

      // Handle thumbnail if present in saved data
      if (savedCourseData && 'thumbnail' in savedCourseData) {
        savedCourseData.thumbnail = processThumbnail(savedCourseData.thumbnail);
      }

      return {
        ...state,
        isSaving: false,
        lastSavedAt: new Date(),
        isDirty: false,
        courseData: savedCourseData
          ? {
              ...state.courseData,
              ...savedCourseData,
              // Ensure we keep track of ID and slug
              id: savedCourseData.id || state.courseData.id,
              slug: savedCourseData.slug || state.courseData.slug,
            }
          : state.courseData,
      };
    }

    case ACTIONS.SAVE_FAILED:
      return {
        ...state,
        isSaving: false,
        errors: { ...state.errors, save: action.payload },
      };

    case ACTIONS.PUBLISH_COURSE:
      return {
        ...state,
        courseData: {
          ...state.courseData,
          is_published: action.payload,
        },
        isDirty: true,
      };

    case ACTIONS.RESET_WIZARD:
      // Clear cache on reset
      if (
        instructorService &&
        typeof instructorService.clearCache === 'function'
      ) {
        instructorService.clearCache();
      }

      return {
        ...initialState,
        currentStep: 1,
      };

    case ACTIONS.SET_ERRORS:
      return {
        ...state,
        errors: { ...state.errors, ...action.payload },
      };

    case ACTIONS.CLEAR_ERRORS:
      return {
        ...state,
        errors: {},
      };

    case ACTIONS.MARK_DIRTY:
      return {
        ...state,
        isDirty: true,
      };

    case ACTIONS.MARK_CLEAN:
      return {
        ...state,
        isDirty: false,
      };

    default:
      return state;
  }
}

// Create context
const CourseWizardContext = createContext();

// Context provider component
export function CourseWizardProvider({ children, existingCourse = null }) {
  // Initialize state with existing course data if available
  const [state, dispatch] = useReducer(
    courseWizardReducer,
    existingCourse
      ? {
          ...initialState,
          courseData: {
            ...initialState.courseData,
            ...existingCourse,
            // Ensure we capture ID and slug
            id: existingCourse.id || null,
            slug: existingCourse.slug || null,
            // Process thumbnail if present
            thumbnail: existingCourse.thumbnail
              ? processThumbnail(existingCourse.thumbnail)
              : null,
            // Ensure requirements and skills are arrays
            requirements: existingCourse.requirements || [],
            skills: existingCourse.skills || [],
          },
          modules: existingCourse.modules || [],
        }
      : initialState
  );

  // HMR-safe ID counter using useRef instead of global variable
  const idRef = useRef(1);

  // Generate a temporary ID for new modules/lessons
  const generateTempId = () => {
    // Use a combination of timestamp, random number, and counter to avoid collisions
    const ts = Date.now();
    const rand = Math.floor(Math.random() * 100000);

    // Increment the counter with each call to ensure uniqueness even for quick successive calls
    idRef.current += 1;

    return `temp_${ts}_${rand}_${idRef.current}`;
  };

  // Methods for updating state
  const updateCourse = data => {
    // Create a processed copy of the data
    const processedData = { ...data };

    // Check if thumbnail is being updated and handle potential array wrapping
    if ('thumbnail' in processedData) {
      if (Array.isArray(processedData.thumbnail)) {
        console.warn(
          'Found array-wrapped thumbnail in updateCourse, unwrapping'
        );
        if (processedData.thumbnail.length > 0) {
          processedData.thumbnail = processedData.thumbnail[0];
        } else {
          processedData.thumbnail = null;
        }
      }

      // Log the processed thumbnail for debugging
      console.log('Processed thumbnail:', {
        type: typeof processedData.thumbnail,
        isFile: processedData.thumbnail instanceof File,
        isArray: Array.isArray(processedData.thumbnail),
        value: processedData.thumbnail,
      });
    }

    // Convert empty string requirements/skills to arrays
    if (processedData.requirements === '') {
      console.log('Converting empty requirements string to array');
      processedData.requirements = [];
    }

    if (processedData.skills === '') {
      console.log('Converting empty skills string to array');
      processedData.skills = [];
    }

    // Now dispatch with the properly processed data
    dispatch({ type: ACTIONS.UPDATE_COURSE, payload: processedData });
  };

  const addModule = moduleData => {
    const newModule = {
      id: generateTempId(),
      title: '',
      description: '',
      order: state.modules.length + 1,
      lessons: [],
      ...moduleData,
    };
    dispatch({ type: ACTIONS.ADD_MODULE, payload: newModule });
    return newModule.id;
  };

  const updateModule = (moduleId, data) => {
    dispatch({
      type: ACTIONS.UPDATE_MODULE,
      payload: { id: moduleId, ...data },
    });
  };

  const removeModule = moduleId => {
    dispatch({ type: ACTIONS.REMOVE_MODULE, payload: moduleId });
  };

  const addLesson = (moduleId, lessonData) => {
    // Find the module to calculate proper lesson order
    const module = state.modules.find(m => m.id === moduleId);
    const lessonCount = module?.lessons?.length || 0;

    const newLesson = {
      id: generateTempId(),
      title: '',
      content: '',
      order: lessonCount + 1,
      // CRITICAL FIX: Changed from 'all' to 'intermediate' to match backend model choices
      access_level: 'registered',
      ...lessonData,
    };
    // Re-ensure access_level is set properly after spreading lessonData
    if (!newLesson.access_level) {
      newLesson.access_level = 'registered';
    }

    dispatch({
      type: ACTIONS.ADD_LESSON,
      payload: { moduleId, lesson: newLesson },
    });

    return newLesson.id;
  };

  const updateLesson = (moduleId, lessonId, data) => {
    // Ensure access_level is set properly if updating
    const lessonData = { id: lessonId, ...data };
    // Always set access_level if it's missing
    if (!lessonData.access_level) {
      lessonData.access_level = 'registered';
    }

    dispatch({
      type: ACTIONS.UPDATE_LESSON,
      payload: {
        moduleId,
        lesson: lessonData,
      },
    });
  };

  const removeLesson = (moduleId, lessonId) => {
    dispatch({
      type: ACTIONS.REMOVE_LESSON,
      payload: { moduleId, lessonId },
    });
  };

  const setStep = step => {
    // Refresh auth token when changing steps to prevent session timeout
    if (
      authPersist &&
      typeof authPersist.isTokenValid === 'function' &&
      typeof authPersist.refreshTokenExpiry === 'function'
    ) {
      if (authPersist.isTokenValid()) {
        authPersist.refreshTokenExpiry();
      }
    }

    dispatch({ type: ACTIONS.SET_STEP, payload: step });
  };

  const nextStep = () => {
    if (state.currentStep < state.totalSteps) {
      dispatch({ type: ACTIONS.SET_STEP, payload: state.currentStep + 1 });
    }
  };

  const prevStep = () => {
    if (state.currentStep > 1) {
      dispatch({ type: ACTIONS.SET_STEP, payload: state.currentStep - 1 });
    }
  };

  const goToStep = step => {
    if (step >= 1 && step <= state.totalSteps) {
      dispatch({ type: ACTIONS.SET_STEP, payload: step });
    }
  };

  const saveStarted = () => {
    dispatch({ type: ACTIONS.SAVE_STARTED });
  };

  const saveCompleted = (courseData = null) => {
    dispatch({
      type: ACTIONS.SAVE_COMPLETED,
      payload: courseData,
    });
  };

  const saveFailed = error => {
    dispatch({
      type: ACTIONS.SAVE_FAILED,
      payload: error,
    });
  };

  const publishCourse = (isPublished = true) => {
    dispatch({
      type: ACTIONS.PUBLISH_COURSE,
      payload: isPublished,
    });
  };

  const resetWizard = () => {
    // Clear cache when resetting the wizard
    if (
      instructorService &&
      typeof instructorService.clearCache === 'function'
    ) {
      instructorService.clearCache();
    }

    dispatch({ type: ACTIONS.RESET_WIZARD });
  };

  const setErrors = errors => {
    dispatch({
      type: ACTIONS.SET_ERRORS,
      payload: errors,
    });
  };

  const clearErrors = () => {
    dispatch({ type: ACTIONS.CLEAR_ERRORS });
  };

  // Function to prepare modules for saving by removing temporary IDs
  const prepareModulesForSaving = modulesList => {
    return modulesList.map(module => {
      // Create a new module object to avoid mutating state
      const preparedModule = { ...module };

      // Remove temporary IDs
      if (
        preparedModule.id &&
        typeof preparedModule.id === 'string' &&
        preparedModule.id.startsWith('temp_')
      ) {
        preparedModule.id = null;
      }

      // Process lessons if they exist
      if (preparedModule.lessons && Array.isArray(preparedModule.lessons)) {
        preparedModule.lessons = preparedModule.lessons.map(lesson => {
          const preparedLesson = { ...lesson };

          // Remove temporary IDs from lessons
          if (
            preparedLesson.id &&
            typeof preparedLesson.id === 'string' &&
            preparedLesson.id.startsWith('temp_')
          ) {
            preparedLesson.id = null;
          }
          // CRITICAL FIX: Ensure access_level is set to a valid value
          // Changed from 'all' to 'intermediate' to match backend model choices
          if (!preparedLesson.access_level) {
            preparedLesson.access_level = 'registered';
          }

          return preparedLesson;
        });
      }

      return preparedModule;
    });
  };

  // Function to validate the current step
  const validateCurrentStep = () => {
    let isValid = true;
    const errors = {};

    switch (state.currentStep) {
      case 1: // Course basics
        if (!state.courseData.title) {
          errors.title = 'Course title is required';
          isValid = false;
        }
        if (!state.courseData.category_id) {
          errors.category = 'Category is required';
          isValid = false;
        }
        break;

      case 2: // Course details
        if (
          !state.courseData.description ||
          state.courseData.description.trim() === ''
        ) {
          errors.description = 'Course description is required';
          isValid = false;
        }
        // Price validation - must be a number or empty string (which will be converted to 0)
        if (state.courseData.price === '' || state.courseData.price === null) {
          // Empty price is valid (will be converted to 0)
        } else if (isNaN(parseFloat(state.courseData.price))) {
          errors.price = 'Price must be a valid number';
          isValid = false;
        }
        break;

      case 3: // Modules
        if (state.modules.length === 0) {
          errors.modules = 'At least one module is required';
          isValid = false;
        } else {
          // Check if all modules have titles
          const modulesWithoutTitles = state.modules.filter(
            module => !module.title || module.title.trim() === ''
          );
          if (modulesWithoutTitles.length > 0) {
            errors.moduleTitles = 'All modules must have titles';
            isValid = false;
          }
        }
        break;

      case 4: // Content
        // Check if any modules have no lessons
        const modulesWithoutLessons = state.modules.filter(
          module => !module.lessons || module.lessons.length === 0
        );
        if (modulesWithoutLessons.length > 0) {
          errors.lessons = 'All modules must have at least one lesson';
          isValid = false;
        }

        // Check if all lessons have titles
        let hasUntitledLessons = false;
        state.modules.forEach(module => {
          if (module.lessons && Array.isArray(module.lessons)) {
            const untitledLessons = module.lessons.filter(
              lesson => !lesson.title || lesson.title.trim() === ''
            );
            if (untitledLessons.length > 0) {
              hasUntitledLessons = true;
            }
          }
        });

        if (hasUntitledLessons) {
          errors.lessonTitles = 'All lessons must have titles';
          isValid = false;
        }
        break;

      case 5: // Review
        // Final validation before publishing
        if (!state.courseData.title || state.courseData.title.trim() === '') {
          errors.title = 'Course title is required';
          isValid = false;
        }

        if (
          !state.courseData.description ||
          state.courseData.description.trim() === ''
        ) {
          errors.description = 'Course description is required';
          isValid = false;
        }

        if (!state.courseData.category_id) {
          errors.category = 'Category is required';
          isValid = false;
        }

        if (state.modules.length === 0) {
          errors.modules = 'At least one module is required';
          isValid = false;
        }

        // Check if there's at least one lesson across all modules
        let hasLessons = false;
        state.modules.forEach(module => {
          if (
            module.lessons &&
            Array.isArray(module.lessons) &&
            module.lessons.length > 0
          ) {
            hasLessons = true;
          }
        });

        if (!hasLessons) {
          errors.lessons = 'Course must have at least one lesson';
          isValid = false;
        }
        break;
    }

    if (!isValid) {
      setErrors(errors);
    } else {
      clearErrors();
    }

    return isValid;
  };

  // Memoize the isStepCompleted function for better performance
  // Check if a step is completed based on state
  const isStepCompleted = useMemo(
    () => step => {
      switch (step) {
        case 1: // Course basics
          return !!state.courseData.title && !!state.courseData.category_id;

        case 2: // Course details
          return (
            !!state.courseData.description &&
            state.courseData.description.trim() !== ''
          );

        case 3: // Modules
          return (
            state.modules.length > 0 &&
            state.modules.every(
              module => module.title && module.title.trim() !== ''
            )
          );

        case 4: // Content
          return state.modules.every(
            module =>
              Array.isArray(module.lessons) &&
              module.lessons.length > 0 &&
              module.lessons.every(
                lesson => lesson.title && lesson.title.trim() !== ''
              )
          );

        case 5: // Review
          return true; // Always considered complete

        default:
          return false;
      }
    },
    [
      // OPTIMIZED: Dependency array only includes relevant state properties to minimize re-computation
      state.courseData.title,
      state.courseData.category_id,
      state.courseData.description,
      state.modules,
    ]
  );

  // Enhanced data synchronization and mode switching utilities
  const modeSwitcher = createModeSwitcher({
    currentData: {
      courseData: state.courseData,
      modules: state.modules,
    },
    onModeSwitch: (newMode, synchronizedData) => {
      // Update course data with normalized data
      dispatch({
        type: ACTIONS.UPDATE_COURSE,
        payload: synchronizedData.courseData,
      });

      // Update modules with normalized data
      synchronizedData.modules.forEach(module => {
        dispatch({
          type: ACTIONS.UPDATE_MODULE,
          payload: module,
        });
      });
    },
  });

  // Normalize course data for consistency
  const getNormalizedCourseData = () => {
    return normalizeCourseData({
      courseData: state.courseData,
      modules: state.modules,
    });
  };

  // Switch between editor modes with data synchronization
  const switchMode = targetMode => {
    const normalizedData = getNormalizedCourseData();
    return modeSwitcher.switchMode(targetMode, normalizedData);
  };

  // Validate access levels across all content
  const validateAccessLevels = () => {
    const errors = {};

    // Validate course access level
    if (
      state.courseData.access_level &&
      !Object.values(ACCESS_LEVELS).includes(state.courseData.access_level)
    ) {
      errors.courseAccessLevel = `Invalid course access level: ${state.courseData.access_level}`;
    }

    // Validate lesson access levels
    state.modules.forEach((module, moduleIndex) => {
      if (module.lessons && Array.isArray(module.lessons)) {
        module.lessons.forEach((lesson, lessonIndex) => {
          if (
            lesson.access_level &&
            !Object.values(ACCESS_LEVELS).includes(lesson.access_level)
          ) {
            errors[`module_${moduleIndex}_lesson_${lessonIndex}_access`] =
              `Invalid lesson access level: ${lesson.access_level}`;
          }
        });
      }
    });

    return errors;
  };

  // Value object
  const value = {
    ...state,
    updateCourse,
    addModule,
    updateModule,
    removeModule,
    addLesson,
    updateLesson,
    removeLesson,
    setStep,
    nextStep,
    prevStep,
    goToStep,
    saveStarted,
    saveCompleted,
    saveFailed,
    publishCourse,
    resetWizard,
    setErrors,
    clearErrors,
    validateCurrentStep,
    isStepCompleted,
    prepareModulesForSaving,
    // Enhanced data synchronization utilities
    getNormalizedCourseData,
    switchMode,
    validateAccessLevels,
    normalizeAccessLevel,
    // Constants from data sync utilities
    ACCESS_LEVELS,
    EDITOR_MODES,
    ACTIONS,
    dispatch,
  };

  return (
    <CourseWizardContext.Provider value={value}>
      {children}
    </CourseWizardContext.Provider>
  );
}

// Custom hook to use the context
export function useCourseWizard() {
  const context = useContext(CourseWizardContext);
  if (!context) {
    throw new Error(
      'useCourseWizard must be used within a CourseWizardProvider'
    );
  }
  return context;
}

// Export the context for direct access if needed
export default CourseWizardContext;

// Export actions for unit testing
export const WizardActions = ACTIONS;
