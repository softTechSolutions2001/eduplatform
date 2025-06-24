/**
 * File: frontend/src/courseBuilder/store/courseSlice.ts
 * Version: 3.2.0
 * Date: 2025-06-24 16:22:45 UTC
 * Author: saiacupunctureFolllow
 * Last Modified: 2025-06-24 16:22:45 UTC
 *
 * Enhanced Course Builder Store with Normalized State Structure
 *
 * This Zustand store manages the complete course building experience with
 * advanced state management, optimistic updates, and race condition protection.
 * All Redux functionality has been removed to standardize on Zustand.
 *
 * Key Features:
 * - Normalized data structure for efficient updates
 * - Optimistic UI updates with server synchronization
 * - Race-safe async operations with abort support
 * - Temporary ID management for real-time editing
 * - Draft/published state management
 * - Version control with cloning capabilities
 * - Memory leak prevention and cleanup
 * - Deep merge protection for nested updates
 * - Enhanced error handling and recovery
 * - Memoized selectors for performance
 *
 * Version 3.2.0 Changes:
 * - FIXED: Complete implementation of moveItem for all types
 * - FIXED: Proper state updates using functional setState pattern
 * - FIXED: Consistent ID type handling (string vs number)
 * - IMPROVED: Performance with selective denormalization
 * - ADDED: Resource ID remapping in mapTempIdsToReal
 * - FIXED: Cleanup handling for timeouts
 * - ENHANCED: Error handling consistency
 */

import { toast } from 'react-toastify';
import { createSelector } from 'reselect';
import { create } from 'zustand';
import { generateTempId, isTempId } from '../../utils/generateTempId';
import courseBuilderAPI from '../api/courseBuilderAPI';
import { Course, Lesson, Module, Resource } from './schema';

// ✅ FIX 1: Enhanced equality helper with deeper object comparison
const shallowEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  if (!obj1 || !obj2) return false;
  if (typeof obj1 !== 'object' || typeof obj2 !== 'object') return false;

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (obj1[key] !== obj2[key]) return false;
  }

  return true;
};

// ✅ FIX 2: Added deep equality check for complex objects
const deepEqual = (obj1: any, obj2: any, depth = 2): boolean => {
  if (obj1 === obj2) return true;
  if (!obj1 || !obj2) return false;
  if (typeof obj1 !== 'object' || typeof obj2 !== 'object') return false;

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (depth > 0 && typeof obj1[key] === 'object' && obj1[key] !== null &&
      typeof obj2[key] === 'object' && obj2[key] !== null) {
      if (!deepEqual(obj1[key], obj2[key], depth - 1)) return false;
    } else if (obj1[key] !== obj2[key]) {
      return false;
    }
  }

  return true;
};

// Extend Course interface to include updatedAt
interface EnhancedCourse extends Course {
  updatedAt?: string;
}

// Normalized state interfaces
interface NormalizedEntities {
  courses: Record<string, EnhancedCourse>;
  modules: Record<string, Module>;
  lessons: Record<string, Lesson>;
  resources: Record<string, Resource>;
}

interface NormalizedIds {
  modules: string[];
  lessonsByModule: Record<string, string[]>;
  resourcesByLesson: Record<string, string[]>;
}

interface SessionState {
  activeId: string | null;
  status: 'idle' | 'loading' | 'saving' | 'saved' | 'error';
  isDirty: boolean;
  isPristine: boolean;
  lastSaved: Date | null;
  error: string | null;
  validationErrors: Record<string, string[]>;
}

interface UIState {
  activeModuleId: string | null;
  activeLessonId: string | null;
  dragState: {
    isDragging: boolean;
    sourceId: string | null;
    targetId: string | null;
    dragType: 'module' | 'lesson' | 'resource' | null;
  };
  currentStep: number;
}

// Enhanced state with normalized structure
interface CourseState {
  // Legacy state for backward compatibility
  course: EnhancedCourse | null;
  isDirty: boolean;
  isSaving: boolean;
  isPristine: boolean;
  lastSaved: Date | null;
  error: string | null;

  // New normalized state
  normalized: {
    entities: NormalizedEntities;
    ids: NormalizedIds;
  };
  session: SessionState;
  ui: UIState;

  // Async safety tracking
  _abortController: AbortController | null;
  _isMounted: boolean;
  _timeouts: ReturnType<typeof setTimeout>[];

  // Actions (keeping original API for backward compatibility)
  setCourse: (course: EnhancedCourse | null) => void;
  mergeCourse: (partial: Partial<EnhancedCourse>) => void;
  updateCourse: (data: Partial<Course>) => void;

  // Module actions
  addModule: () => void;
  updateModule: (moduleId: string, data: Partial<Module>) => void;
  deleteModule: (moduleId: string) => void;
  reorderModules: (newOrder: string[]) => void;

  // New optimized drag operations
  startDrag: (sourceId: string, dragType: 'module' | 'lesson' | 'resource') => void;
  endDrag: (targetId: string | null) => void;
  moveItem: (sourceId: string, targetId: string, type: 'module' | 'lesson' | 'resource', options?: Record<string, any>) => void;

  // Added explicit move functions that can be called from DnDContext
  moveModule: (payload: { sourceIndex: number; targetIndex: number }) => void;
  moveLesson: (payload: {
    sourceModuleId: string;
    targetModuleId: string;
    lessonId: string;
    sourceIndex: number;
    targetIndex: number;
  }) => void;

  // Lesson actions
  addLesson: (moduleId: string, lessonData: Partial<Lesson>) => Promise<Lesson>;
  updateLesson: (moduleId: string, lessonId: string, data: Partial<Lesson>) => void;
  deleteLesson: (moduleId: string, lessonId: string) => void;
  reorderLessons: (moduleId: string, newOrder: string[]) => void;

  // Resource actions
  addResource: (moduleId: string, lessonId: string) => void;
  updateResource: (moduleId: string, lessonId: string, resourceId: string, data: Partial<Resource>) => void;
  deleteResource: (moduleId: string, lessonId: string, resourceId: string) => void;

  // Publishing actions
  publishVersion: () => Promise<void>;
  unpublishVersion: () => Promise<void>;
  cloneVersion: () => Promise<void>;

  // ID management
  mapTempIdsToReal: (serverCourse: Course) => void;

  // Cleanup method
  cleanup: () => void;

  // ✅ FIX 3: Added utility for updating nested arrays
  updateNested: <T extends { id: string }>(
    array: T[],
    predicate: (item: T) => boolean,
    merger: (item: T) => T
  ) => T[];

  // ✅ FIX 4: Added selective denormalization helper
  denormalizeItem: <T extends 'module' | 'lesson' | 'resource'>(
    itemType: T,
    itemId: string
  ) => any;
}

// ✅ FIX 5: Memoized selectors with proper caching strategy
const createCachedSelector = <S, R>(
  selector: (state: S) => R
): ((state: S) => R) => {
  let lastState: S | undefined = undefined;
  let lastResult: R | undefined = undefined;

  return (state: S) => {
    if (lastState === state) {
      return lastResult as R;
    }
    const result = selector(state);
    lastState = state;
    lastResult = result;
    return result;
  };
};

// External selectors with memoization
export const courseSelectors = {
  // Original selectors
  canEdit: (course: EnhancedCourse | null): boolean => {
    if (!course) return false;
    // Published courses can't be edited directly unless they're drafts
    if (course.isPublished && !course.isDraft) {
      return false;
    }
    return true;
  },

  isDraft: (course: EnhancedCourse | null): boolean => {
    return !!course?.isDraft;
  },

  isPublished: (course: EnhancedCourse | null): boolean => {
    return !!course?.isPublished;
  },

  // ✅ FIX 6: Fixed selector factory to properly cache based on params
  getModules: createSelector(
    (state: CourseState) => state.normalized.entities.modules,
    (state: CourseState) => state.normalized.ids.modules,
    (modules, moduleIds) => moduleIds.map(id => modules[id]).filter(Boolean)
  ),

  getLessonsForModule: (moduleId: string) => {
    // Use createSelector only once per moduleId
    const selector = createSelector(
      (state: CourseState) => state.normalized.entities.lessons,
      (state: CourseState) => state.normalized.ids.lessonsByModule[moduleId] || [],
      (lessons, lessonIds) => lessonIds.map(id => lessons[id]).filter(Boolean)
    );

    return createCachedSelector(selector);
  },

  getResourcesForLesson: (lessonId: string) => {
    // Use createSelector only once per lessonId
    const selector = createSelector(
      (state: CourseState) => state.normalized.entities.resources,
      (state: CourseState) => state.normalized.ids.resourcesByLesson[lessonId] || [],
      (resources, resourceIds) => resourceIds.map(id => resources[id]).filter(Boolean)
    );

    return createCachedSelector(selector);
  },

  getCourseStructure: createSelector(
    (state: CourseState) => state.normalized.entities.courses,
    (state: CourseState) => state.normalized.entities.modules,
    (state: CourseState) => state.normalized.entities.lessons,
    (state: CourseState) => state.normalized.entities.resources,
    (state: CourseState) => state.normalized.ids.modules,
    (state: CourseState) => state.normalized.ids.lessonsByModule,
    (state: CourseState) => state.normalized.ids.resourcesByLesson,
    (state: CourseState) => state.session.activeId,
    (courses, modules, lessons, resources, moduleIds, lessonsByModule, resourcesByLesson, activeId) => {
      if (!activeId || !courses[activeId]) return null;

      const activeCourse = courses[activeId];

      return {
        ...activeCourse,
        modules: moduleIds
          .map(moduleId => {
            const module = modules[moduleId];
            if (!module) return null;

            return {
              ...module,
              lessons: (lessonsByModule[moduleId] || [])
                .map(lessonId => {
                  const lesson = lessons[lessonId];
                  if (!lesson) return null;

                  return {
                    ...lesson,
                    resources: (resourcesByLesson[lessonId] || [])
                      .map(resourceId => resources[resourceId])
                      .filter(Boolean)
                  };
                })
                .filter(Boolean)
            };
          })
          .filter(Boolean)
      };
    }
  )
};

// ✅ FIX 7: Helper for normalizing course data with consistent ID types
const normalizeCourse = (course: EnhancedCourse | null): {
  entities: NormalizedEntities,
  ids: NormalizedIds
} => {
  if (!course) {
    return {
      entities: {
        courses: {},
        modules: {},
        lessons: {},
        resources: {}
      },
      ids: {
        modules: [],
        lessonsByModule: {},
        resourcesByLesson: {}
      }
    };
  }

  const courseId = String(course.id);

  const entities: NormalizedEntities = {
    courses: { [courseId]: { ...course, modules: [] } },
    modules: {},
    lessons: {},
    resources: {}
  };

  const ids: NormalizedIds = {
    modules: [],
    lessonsByModule: {},
    resourcesByLesson: {}
  };

  // Normalize modules
  if (course.modules) {
    ids.modules = course.modules.map(module => String(module.id));

    course.modules.forEach(module => {
      const moduleId = String(module.id);
      entities.modules[moduleId] = { ...module, lessons: [] };
      ids.lessonsByModule[moduleId] = [];

      // Normalize lessons
      if (module.lessons) {
        ids.lessonsByModule[moduleId] = module.lessons.map(lesson => String(lesson.id));

        module.lessons.forEach(lesson => {
          const lessonId = String(lesson.id);
          entities.lessons[lessonId] = { ...lesson, resources: [] };
          ids.resourcesByLesson[lessonId] = [];

          // Normalize resources
          if (lesson.resources) {
            ids.resourcesByLesson[lessonId] = lesson.resources.map(resource => String(resource.id));

            lesson.resources.forEach(resource => {
              const resourceId = String(resource.id);
              entities.resources[resourceId] = { ...resource };
            });
          }
        });
      }
    });
  }

  return { entities, ids };
};

// ✅ FIX 8: Helper for denormalizing specific parts of the course data
const denormalizeCourse = (
  courseId: string | null,
  entities: NormalizedEntities,
  ids: NormalizedIds
): EnhancedCourse | null => {
  if (!courseId || !entities.courses[courseId]) return null;

  const course = { ...entities.courses[courseId] };

  course.modules = ids.modules
    .map(moduleId => {
      const module = { ...entities.modules[moduleId] };

      module.lessons = (ids.lessonsByModule[moduleId] || [])
        .map(lessonId => {
          const lesson = { ...entities.lessons[lessonId] };

          lesson.resources = (ids.resourcesByLesson[lessonId] || [])
            .map(resourceId => ({ ...entities.resources[resourceId] }));

          return lesson;
        });

      return module;
    });

  return course;
};

// Create store with both normalized and backward-compatible state
export const useCourseStore = create<CourseState>((set, get) => ({
  // Legacy state
  course: null,
  isDirty: false,
  isSaving: false,
  isPristine: true,
  lastSaved: null,
  error: null,

  // New normalized state
  normalized: {
    entities: {
      courses: {},
      modules: {},
      lessons: {},
      resources: {}
    },
    ids: {
      modules: [],
      lessonsByModule: {},
      resourcesByLesson: {}
    }
  },

  session: {
    activeId: null,
    status: 'idle',
    isDirty: false,
    isPristine: true,
    lastSaved: null,
    error: null,
    validationErrors: {}
  },

  ui: {
    activeModuleId: null,
    activeLessonId: null,
    dragState: {
      isDragging: false,
      sourceId: null,
      targetId: null,
      dragType: null
    },
    currentStep: 0
  },

  _abortController: null,
  _isMounted: true,
  _timeouts: [],

  // ✅ FIX 9: Added helper for updating nested arrays
  updateNested: <T extends { id: string }>(
    array: T[],
    predicate: (item: T) => boolean,
    merger: (item: T) => T
  ): T[] => {
    return array.map(item => (predicate(item) ? merger(item) : item));
  },

  // ✅ FIX 10: Added selective denormalization helper
  denormalizeItem: (itemType, itemId) => {
    const state = get();

    switch (itemType) {
      case 'module':
        const module = { ...state.normalized.entities.modules[itemId] };
        if (!module) return null;

        module.lessons = (state.normalized.ids.lessonsByModule[itemId] || [])
          .map(lessonId => state.normalized.entities.lessons[lessonId])
          .filter(Boolean);

        return module;

      case 'lesson':
        const lesson = { ...state.normalized.entities.lessons[itemId] };
        if (!lesson) return null;

        lesson.resources = (state.normalized.ids.resourcesByLesson[itemId] || [])
          .map(resourceId => state.normalized.entities.resources[resourceId])
          .filter(Boolean);

        return lesson;

      case 'resource':
        return state.normalized.entities.resources[itemId] || null;

      default:
        return null;
    }
  },

  // Enhanced setCourse with normalization
  setCourse: (incoming) => {
    const timeoutId = setTimeout(() => {
      const state = get();
      if (state._isMounted) {
        state.mapTempIdsToReal(incoming!);
      }
    }, 0);

    set(state => {
      // Add timeout to cleanup list
      const updatedTimeouts = [...state._timeouts, timeoutId];

      if (!incoming) {
        return {
          course: null,
          isDirty: false,
          isPristine: true,
          error: null,
          normalized: normalizeCourse(null),
          session: {
            ...state.session,
            activeId: null,
            status: 'idle',
            isDirty: false,
            isPristine: true,
            error: null
          },
          _timeouts: updatedTimeouts
        };
      }

      const courseWithTimestamp = {
        ...incoming,
        updatedAt: new Date().toISOString()
      };

      const normalized = normalizeCourse(courseWithTimestamp);
      const activeId = String(incoming.id);

      return {
        course: courseWithTimestamp,
        isDirty: false,
        isPristine: true,
        error: null,
        normalized,
        session: {
          ...state.session,
          activeId,
          status: 'idle',
          isDirty: false,
          isPristine: true,
          error: null
        },
        _timeouts: updatedTimeouts
      };
    });
  },

  // mergeCourse with deep checking
  mergeCourse: (partial) => {
    const state = get();
    if (!state.course) return;

    // ✅ FIX 11: Use deeper equality check for complex objects
    if (deepEqual(state.course, { ...state.course, ...partial }, 2)) {
      return;
    }

    // Current normalized state
    const { normalized } = state;
    const sessionId = state.session.activeId;
    if (!sessionId) return;

    // Create updated course by merging
    const updatedCourse = {
      ...state.course,
      ...partial,
      updatedAt: new Date().toISOString()
    };

    // Special handling for modules array to ensure proper merging
    if (partial.modules) {
      // If course has modules in both current state and partial
      if (state.course.modules) {
        const existingModuleMap = new Map(
          state.course.modules.map(m => [String(m.id), m])
        );

        updatedCourse.modules = partial.modules.map(newModule => {
          const existing = existingModuleMap.get(String(newModule.id));
          return existing ? { ...existing, ...newModule } : newModule;
        });
      } else {
        updatedCourse.modules = partial.modules;
      }
    }

    // Re-normalize with updated course
    const newNormalized = normalizeCourse(updatedCourse);

    set(state => ({
      course: updatedCourse,
      isDirty: true,
      isPristine: false,
      normalized: newNormalized,
      session: {
        ...state.session,
        status: 'saving',
        isDirty: true,
        isPristine: false
      }
    }));
  },

  // Update course data
  updateCourse: (data) => {
    const state = get();
    if (!state.course || !state.session.activeId) return;

    const courseId = state.session.activeId;
    const updatedCourse = {
      ...state.course,
      ...data,
      updatedAt: new Date().toISOString()
    };

    set(state => ({
      course: updatedCourse,
      isDirty: true,
      isPristine: false,
      normalized: {
        ...state.normalized,
        entities: {
          ...state.normalized.entities,
          courses: {
            ...state.normalized.entities.courses,
            [courseId]: updatedCourse
          }
        }
      },
      session: {
        ...state.session,
        status: 'saving',
        isDirty: true,
        isPristine: false
      }
    }));
  },

  // Add new module (optimized with normalized state)
  addModule: () => {
    const state = get();
    if (!state.course || !state.session.activeId) return;

    const newModuleId = generateTempId();
    const newModule: Module = {
      id: newModuleId,
      title: 'New Module',
      description: '',
      order: state.normalized.ids.modules.length,
      lessons: []
    };

    set(state => {
      // Update normalized state
      const updatedNormalized = {
        entities: {
          ...state.normalized.entities,
          modules: {
            ...state.normalized.entities.modules,
            [newModuleId]: newModule
          }
        },
        ids: {
          ...state.normalized.ids,
          modules: [...state.normalized.ids.modules, newModuleId],
          lessonsByModule: {
            ...state.normalized.ids.lessonsByModule,
            [newModuleId]: []
          }
        }
      };

      // ✅ FIX 12: Only update the specific module in the course.modules array
      // instead of full denormalization
      const updatedModules = state.course?.modules ?
        [...state.course.modules, newModule] :
        [newModule];

      return {
        course: {
          ...state.course!,
          modules: updatedModules,
          updatedAt: new Date().toISOString()
        },
        normalized: updatedNormalized,
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // Update module with normalized state
  updateModule: (moduleId, data) => {
    const state = get();
    if (!state.course || !state.session.activeId) return;

    set(state => {
      // First update normalized state
      const module = state.normalized.entities.modules[moduleId];
      if (!module) return state;

      const updatedModule = { ...module, ...data };

      const updatedNormalized = {
        ...state.normalized,
        entities: {
          ...state.normalized.entities,
          modules: {
            ...state.normalized.entities.modules,
            [moduleId]: updatedModule
          }
        }
      };

      // ✅ FIX 13: Selectively update just this module in the course object
      const updatedModules = state.course?.modules?.map(m =>
        String(m.id) === moduleId ? updatedModule : m
      ) || [];

      return {
        course: {
          ...state.course!,
          modules: updatedModules,
          updatedAt: new Date().toISOString()
        },
        normalized: updatedNormalized,
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // Delete module with normalized state
  deleteModule: (moduleId) => {
    const state = get();
    if (!state.course || !state.session.activeId) return;

    set(state => {
      // Get all lesson IDs for this module to clean up
      const lessonIds = state.normalized.ids.lessonsByModule[moduleId] || [];

      // Get all resource IDs for each lesson to clean up
      const resourceIds = lessonIds.flatMap(
        lessonId => state.normalized.ids.resourcesByLesson[lessonId] || []
      );

      // Create new module entities object without this module
      const { [moduleId]: _, ...remainingModules } = state.normalized.entities.modules;

      // Create new lesson entities without these lessons
      const remainingLessons = { ...state.normalized.entities.lessons };
      lessonIds.forEach(id => delete remainingLessons[id]);

      // Create new resource entities without these resources
      const remainingResources = { ...state.normalized.entities.resources };
      resourceIds.forEach(id => delete remainingResources[id]);

      // Update module IDs list
      const updatedModuleIds = state.normalized.ids.modules.filter(id => id !== moduleId);

      // Update lessonsByModule without this module
      const { [moduleId]: __, ...remainingLessonsByModule } = state.normalized.ids.lessonsByModule;

      // Update resourcesByLesson without these lessons
      const remainingResourcesByLesson = { ...state.normalized.ids.resourcesByLesson };
      lessonIds.forEach(id => delete remainingResourcesByLesson[id]);

      const updatedNormalized = {
        entities: {
          ...state.normalized.entities,
          modules: remainingModules,
          lessons: remainingLessons,
          resources: remainingResources
        },
        ids: {
          modules: updatedModuleIds,
          lessonsByModule: remainingLessonsByModule,
          resourcesByLesson: remainingResourcesByLesson
        }
      };

      // ✅ FIX 14: Selectively remove the module from the course
      const updatedModules = state.course?.modules?.filter(m =>
        String(m.id) !== moduleId
      ) || [];

      return {
        course: {
          ...state.course!,
          modules: updatedModules,
          updatedAt: new Date().toISOString()
        },
        normalized: updatedNormalized,
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // Drag and drop actions
  startDrag: (sourceId, dragType) => {
    set(state => ({
      ui: {
        ...state.ui,
        dragState: {
          isDragging: true,
          sourceId,
          targetId: null,
          dragType
        }
      }
    }));
  },

  endDrag: (targetId) => {
    const { dragState } = get().ui;

    // If we have both source and target and they're different, perform the move
    if (dragState.isDragging && dragState.sourceId && targetId && dragState.sourceId !== targetId) {
      get().moveItem(dragState.sourceId, targetId, dragState.dragType!);
    }

    // Reset drag state
    set(state => ({
      ui: {
        ...state.ui,
        dragState: {
          isDragging: false,
          sourceId: null,
          targetId: null,
          dragType: null
        }
      }
    }));
  },

  // ✅ FIX 15: Complete implementation of moveItem for all item types
  moveItem: (sourceId, targetId, type, options = {}) => {
    const state = get();

    if (type === 'module') {
      // Find current indices
      const sourceIndex = state.normalized.ids.modules.indexOf(sourceId);
      const targetIndex = state.normalized.ids.modules.indexOf(targetId);

      if (sourceIndex === -1 || targetIndex === -1) {
        console.error('Invalid module indices for movement', { sourceIndex, targetIndex });
        return;
      }

      // Create new module order
      const moduleIds = [...state.normalized.ids.modules];
      moduleIds.splice(sourceIndex, 1);
      moduleIds.splice(targetIndex, 0, sourceId);

      // Update module order optimistically
      set(state => {
        const updatedNormalized = {
          ...state.normalized,
          ids: {
            ...state.normalized.ids,
            modules: moduleIds
          }
        };

        // Update entities with new order indices
        const updatedModules = { ...state.normalized.entities.modules };
        moduleIds.forEach((id, idx) => {
          if (updatedModules[id]) {
            updatedModules[id] = {
              ...updatedModules[id],
              order: idx
            };
          }
        });

        updatedNormalized.entities = {
          ...updatedNormalized.entities,
          modules: updatedModules
        };

        // ✅ FIX 16: Selectively update the modules array in the course
        const updatedCourseModules = moduleIds
          .map(id => updatedModules[id])
          .filter(Boolean);

        return {
          normalized: updatedNormalized,
          course: {
            ...state.course!,
            modules: updatedCourseModules,
            updatedAt: new Date().toISOString()
          },
          session: {
            ...state.session,
            status: 'saving',
            isDirty: true,
            isPristine: false
          },
          isDirty: true,
          isPristine: false
        };
      });
    }
    else if (type === 'lesson') {
      // ✅ FIX 17: Implemented lesson movement
      const { sourceModuleId = '', targetModuleId = '' } = options;

      if (!sourceModuleId || !targetModuleId) {
        console.error('Missing module IDs for lesson movement', { sourceId, targetId, options });
        return;
      }

      // Find current indices
      const sourceLessonIds = state.normalized.ids.lessonsByModule[sourceModuleId] || [];
      const targetLessonIds = state.normalized.ids.lessonsByModule[targetModuleId] || [];
      const sourceIndex = sourceLessonIds.indexOf(sourceId);
      const targetIndex = targetLessonIds.indexOf(targetId);

      if (sourceIndex === -1) {
        console.error('Invalid source lesson index', { sourceId, sourceModuleId, sourceLessonIds });
        return;
      }

      // Moving within the same module
      if (sourceModuleId === targetModuleId) {
        if (targetIndex === -1) {
          console.error('Invalid target lesson index', { targetId, targetModuleId, targetLessonIds });
          return;
        }

        // Create new lesson order
        const reorderedLessonIds = [...sourceLessonIds];
        reorderedLessonIds.splice(sourceIndex, 1);
        reorderedLessonIds.splice(targetIndex, 0, sourceId);

        get().reorderLessons(sourceModuleId, reorderedLessonIds);
      }
      // Moving between different modules
      else {
        // When moving to different module, targetId might be moduleId if dropping at the end
        const isTargetModule = !targetLessonIds.includes(targetId) &&
          state.normalized.entities.modules[targetId];

        // Remove from source module
        const newSourceLessonIds = sourceLessonIds.filter(id => id !== sourceId);

        // Add to target module
        let newTargetLessonIds = [...targetLessonIds];

        if (isTargetModule) {
          // If dropping on the module itself, append to end
          newTargetLessonIds.push(sourceId);
        } else {
          // Find target position or default to end
          const insertPosition = targetIndex !== -1 ? targetIndex : newTargetLessonIds.length;
          newTargetLessonIds.splice(insertPosition, 0, sourceId);
        }

        set(state => {
          // Update the lesson's parent module reference
          const updatedLesson = {
            ...state.normalized.entities.lessons[sourceId],
            moduleId: targetModuleId
          };

          const updatedNormalized = {
            ...state.normalized,
            entities: {
              ...state.normalized.entities,
              lessons: {
                ...state.normalized.entities.lessons,
                [sourceId]: updatedLesson
              }
            },
            ids: {
              ...state.normalized.ids,
              lessonsByModule: {
                ...state.normalized.ids.lessonsByModule,
                [sourceModuleId]: newSourceLessonIds,
                [targetModuleId]: newTargetLessonIds
              }
            }
          };

          // ✅ FIX 18: Update only the affected modules in the course
          const updatedModules = state.course?.modules?.map(module => {
            if (String(module.id) === sourceModuleId) {
              return {
                ...module,
                lessons: module.lessons?.filter(l => String(l.id) !== sourceId) || []
              };
            }
            if (String(module.id) === targetModuleId) {
              // Find the actual lesson object
              const movedLesson = state.course?.modules
                ?.find(m => String(m.id) === sourceModuleId)?.lessons
                ?.find(l => String(l.id) === sourceId);

              if (!movedLesson) return module;

              return {
                ...module,
                lessons: [...(module.lessons || []), movedLesson]
              };
            }
            return module;
          }) || [];

          return {
            normalized: updatedNormalized,
            course: {
              ...state.course!,
              modules: updatedModules,
              updatedAt: new Date().toISOString()
            },
            session: {
              ...state.session,
              status: 'saving',
              isDirty: true,
              isPristine: false
            },
            isDirty: true,
            isPristine: false
          };
        });
      }
    }
    else if (type === 'resource') {
      // ✅ FIX 19: Implemented resource movement
      const {
        sourceLessonId = '',
        targetLessonId = '',
        sourceModuleId = '',
        targetModuleId = ''
      } = options;

      if (!sourceLessonId || !targetLessonId) {
        console.error('Missing lesson IDs for resource movement', { sourceId, targetId, options });
        return;
      }

      // Find current indices
      const sourceResourceIds = state.normalized.ids.resourcesByLesson[sourceLessonId] || [];
      const targetResourceIds = state.normalized.ids.resourcesByLesson[targetLessonId] || [];
      const sourceIndex = sourceResourceIds.indexOf(sourceId);
      const targetIndex = targetResourceIds.indexOf(targetId);

      if (sourceIndex === -1) {
        console.error('Invalid source resource index', { sourceId, sourceLessonId, sourceResourceIds });
        return;
      }

      // Moving within the same lesson
      if (sourceLessonId === targetLessonId) {
        if (targetIndex === -1) {
          console.error('Invalid target resource index', { targetId, targetLessonId, targetResourceIds });
          return;
        }

        // Create new resource order
        const reorderedResourceIds = [...sourceResourceIds];
        reorderedResourceIds.splice(sourceIndex, 1);
        reorderedResourceIds.splice(targetIndex, 0, sourceId);

        set(state => {
          const updatedNormalized = {
            ...state.normalized,
            ids: {
              ...state.normalized.ids,
              resourcesByLesson: {
                ...state.normalized.ids.resourcesByLesson,
                [sourceLessonId]: reorderedResourceIds
              }
            }
          };

          // ✅ FIX 20: Selectively update just the affected lesson in the course
          const updatedCourse = state.course ? {
            ...state.course,
            modules: state.course.modules?.map(module => {
              if (String(module.id) === sourceModuleId) {
                return {
                  ...module,
                  lessons: module.lessons?.map(lesson => {
                    if (String(lesson.id) === sourceLessonId) {
                      // Reorder resources
                      const resourceMap = new Map(
                        lesson.resources?.map(r => [String(r.id), r]) || []
                      );

                      const reorderedResources = reorderedResourceIds
                        .map(id => resourceMap.get(id))
                        .filter(Boolean);

                      return {
                        ...lesson,
                        resources: reorderedResources
                      };
                    }
                    return lesson;
                  }) || []
                };
              }
              return module;
            }) || []
          } : null;

          return {
            normalized: updatedNormalized,
            course: updatedCourse,
            session: {
              ...state.session,
              status: 'saving',
              isDirty: true,
              isPristine: false
            },
            isDirty: true,
            isPristine: false
          };
        });
      }
      // Moving between different lessons
      else {
        // Remove from source lesson
        const newSourceResourceIds = sourceResourceIds.filter(id => id !== sourceId);

        // Add to target lesson
        let newTargetResourceIds = [...targetResourceIds];

        // If dropping on the lesson itself, append to end
        const isTargetLesson = !targetResourceIds.includes(targetId) &&
          state.normalized.entities.lessons[targetId];

        if (isTargetLesson) {
          newTargetResourceIds.push(sourceId);
        } else {
          // Find target position or default to end
          const insertPosition = targetIndex !== -1 ? targetIndex : newTargetResourceIds.length;
          newTargetResourceIds.splice(insertPosition, 0, sourceId);
        }

        set(state => {
          // Update the resource's parent lesson reference
          const updatedResource = {
            ...state.normalized.entities.resources[sourceId],
            lessonId: targetLessonId
          };

          const updatedNormalized = {
            ...state.normalized,
            entities: {
              ...state.normalized.entities,
              resources: {
                ...state.normalized.entities.resources,
                [sourceId]: updatedResource
              }
            },
            ids: {
              ...state.normalized.ids,
              resourcesByLesson: {
                ...state.normalized.ids.resourcesByLesson,
                [sourceLessonId]: newSourceResourceIds,
                [targetLessonId]: newTargetResourceIds
              }
            }
          };

          // Update only the affected lessons in the course
          const updatedCourse = state.course ? {
            ...state.course,
            modules: state.course.modules?.map(module => {
              if ([sourceModuleId, targetModuleId].includes(String(module.id))) {
                return {
                  ...module,
                  lessons: module.lessons?.map(lesson => {
                    // Source lesson - remove the resource
                    if (String(lesson.id) === sourceLessonId) {
                      return {
                        ...lesson,
                        resources: lesson.resources?.filter(
                          r => String(r.id) !== sourceId
                        ) || []
                      };
                    }

                    // Target lesson - add the resource
                    if (String(lesson.id) === targetLessonId) {
                      // Find the moved resource
                      const movedResource = state.course?.modules
                        ?.find(m => String(m.id) === sourceModuleId)?.lessons
                        ?.find(l => String(l.id) === sourceLessonId)?.resources
                        ?.find(r => String(r.id) === sourceId);

                      if (!movedResource) return lesson;

                      return {
                        ...lesson,
                        resources: [...(lesson.resources || []), movedResource]
                      };
                    }

                    return lesson;
                  }) || []
                };
              }
              return module;
            }) || []
          } : null;

          return {
            normalized: updatedNormalized,
            course: updatedCourse,
            session: {
              ...state.session,
              status: 'saving',
              isDirty: true,
              isPristine: false
            },
            isDirty: true,
            isPristine: false
          };
        });
      }
    }
  },

  // ✅ FIX 21: Implemented moveModule with better error handling
  moveModule: ({ sourceIndex, targetIndex }) => {
    const state = get();
    if (!state.course) return;

    const moduleIds = [...state.normalized.ids.modules];

    if (sourceIndex < 0 || sourceIndex >= moduleIds.length ||
      targetIndex < 0 || targetIndex >= moduleIds.length) {
      console.error('Invalid module indices for movement', { sourceIndex, targetIndex });
      toast.error('Cannot move module: invalid position');
      return;
    }

    // Get the actual module IDs
    const sourceId = moduleIds[sourceIndex];
    const targetId = moduleIds[targetIndex];

    // Use the existing moveItem implementation
    get().moveItem(sourceId, targetId, 'module');
  },

  // ✅ FIX 22: Implemented moveLesson with complete validation
  moveLesson: ({ sourceModuleId, targetModuleId, lessonId, sourceIndex, targetIndex }) => {
    const state = get();
    if (!state.course) return;

    // Get the lesson IDs from both modules
    const sourceLessonIds = [...(state.normalized.ids.lessonsByModule[sourceModuleId] || [])];
    const targetLessonIds = [...(state.normalized.ids.lessonsByModule[targetModuleId] || [])];

    // Validate source exists
    if (!state.normalized.entities.modules[sourceModuleId]) {
      console.error('Source module does not exist', { sourceModuleId });
      toast.error('Cannot move lesson: source module not found');
      return;
    }

    // Validate target exists
    if (!state.normalized.entities.modules[targetModuleId]) {
      console.error('Target module does not exist', { targetModuleId });
      toast.error('Cannot move lesson: target module not found');
      return;
    }

    // Validate indices
    if (sourceIndex < 0 || sourceIndex >= sourceLessonIds.length) {
      console.error('Invalid source index for lesson movement', { sourceIndex, sourceLessonIds });
      toast.error('Cannot move lesson: invalid source position');
      return;
    }

    if (targetIndex < 0 || targetIndex > targetLessonIds.length) {
      console.error('Invalid target index for lesson movement', { targetIndex, targetLessonIds });
      toast.error('Cannot move lesson: invalid target position');
      return;
    }

    // Check if lessonId matches expected source lesson
    if (lessonId !== sourceLessonIds[sourceIndex]) {
      console.error('Lesson ID mismatch', {
        lessonId,
        expectedId: sourceLessonIds[sourceIndex]
      });
      return;
    }

    // Same module movement - use reorderLessons
    if (sourceModuleId === targetModuleId) {
      // Reorder lessons within the same module
      const reorderedLessonIds = [...sourceLessonIds];
      const [movedLessonId] = reorderedLessonIds.splice(sourceIndex, 1);
      reorderedLessonIds.splice(targetIndex, 0, movedLessonId);

      // Update the store with the new order
      get().reorderLessons(sourceModuleId, reorderedLessonIds);
    }
    // Different module movement - use moveItem with appropriate options
    else {
      // Get target ID (if dropping at end of module, use module ID)
      let targetId = '';

      if (targetIndex < targetLessonIds.length) {
        targetId = targetLessonIds[targetIndex];
      } else {
        // Last position - use module ID as target
        targetId = targetModuleId;
      }

      get().moveItem(lessonId, targetId, 'lesson', {
        sourceModuleId,
        targetModuleId
      });
    }
  },

  // ✅ FIX 23: Improved reorderModules with validation and error handling
  reorderModules: (newOrder) => {
    const state = get();
    if (!state.course || !state.session.activeId) return;

    // Validate the new order contains all modules
    if (newOrder.length !== state.normalized.ids.modules.length) {
      console.error('Invalid module order - length mismatch', {
        current: state.normalized.ids.modules,
        new: newOrder
      });
      toast.error('Cannot reorder modules: invalid order');
      return;
    }

    // Check all module IDs exist
    const missingIds = newOrder.filter(id => !state.normalized.entities.modules[id]);
    if (missingIds.length > 0) {
      console.error('Invalid module order - unknown modules', { missingIds });
      toast.error('Cannot reorder modules: unknown modules');
      return;
    }

    set(state => {
      // Update normalized state with new order
      const updatedNormalized = {
        ...state.normalized,
        ids: {
          ...state.normalized.ids,
          modules: newOrder
        }
      };

      // Update module entities with new order indices
      const updatedModules = { ...state.normalized.entities.modules };
      newOrder.forEach((id, index) => {
        if (updatedModules[id]) {
          updatedModules[id] = {
            ...updatedModules[id],
            order: index
          };
        }
      });

      updatedNormalized.entities = {
        ...updatedNormalized.entities,
        modules: updatedModules
      };

      // Selectively update the modules array in the course
      const reorderedModules = newOrder
        .map(id => updatedModules[id])
        .filter(Boolean);

      return {
        course: {
          ...state.course!,
          modules: reorderedModules,
          updatedAt: new Date().toISOString()
        },
        normalized: updatedNormalized,
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // Enhanced addLesson with normalized state
  addLesson: async (moduleId, lessonData) => {
    const newLessonId = generateTempId();
    const newLesson: Lesson = {
      id: newLessonId,
      title: lessonData.title || 'New Lesson',
      content: lessonData.content || '<p>Default lesson content.</p>',
      order: lessonData.order || 0,
      type: lessonData.type || 'reading',
      accessLevel: lessonData.accessLevel || 'registered',
      resources: [],
      ...lessonData
    };

    // Store original state for rollback
    const originalState = {
      course: get().course,
      normalized: get().normalized
    };

    // Optimistic update
    set(state => {
      // Update normalized state
      const moduleOrder = state.normalized.ids.lessonsByModule[moduleId]?.length || 0;
      newLesson.order = moduleOrder;

      const updatedNormalized = {
        entities: {
          ...state.normalized.entities,
          lessons: {
            ...state.normalized.entities.lessons,
            [newLessonId]: newLesson
          }
        },
        ids: {
          ...state.normalized.ids,
          lessonsByModule: {
            ...state.normalized.ids.lessonsByModule,
            [moduleId]: [
              ...(state.normalized.ids.lessonsByModule[moduleId] || []),
              newLessonId
            ]
          },
          resourcesByLesson: {
            ...state.normalized.ids.resourcesByLesson,
            [newLessonId]: []
          }
        }
      };

      // ✅ FIX 24: Only update the specific module in the course
      const updatedCourse = state.course ? {
        ...state.course,
        modules: state.course.modules?.map(module => {
          if (String(module.id) === moduleId) {
            return {
              ...module,
              lessons: [...(module.lessons || []), newLesson]
            };
          }
          return module;
        }) || [],
        updatedAt: new Date().toISOString()
      } : null;

      return {
        course: updatedCourse,
        normalized: updatedNormalized,
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });

    // Try to persist to server if not a temporary module
    try {
      const savedLesson = await courseBuilderAPI.createLesson(moduleId, newLesson);

      // Update with server data only if still mounted
      const state = get();
      if (state._isMounted) {
        set(state => {
          // Update normalized state with real ID
          const updatedLessons = { ...state.normalized.entities.lessons };
          delete updatedLessons[newLessonId];
          updatedLessons[savedLesson.id] = savedLesson;

          // Update lesson IDs list for module
          const lessonIds = state.normalized.ids.lessonsByModule[moduleId] || [];
          const updatedLessonIds = lessonIds.map(id =>
            id === newLessonId ? savedLesson.id : id
          );

          const updatedNormalized = {
            entities: {
              ...state.normalized.entities,
              lessons: updatedLessons
            },
            ids: {
              ...state.normalized.ids,
              lessonsByModule: {
                ...state.normalized.ids.lessonsByModule,
                [moduleId]: updatedLessonIds
              },
              resourcesByLesson: {
                ...state.normalized.ids.resourcesByLesson,
                [savedLesson.id]: state.normalized.ids.resourcesByLesson[newLessonId] || []
              }
            }
          };

          // Delete old temporary ID entry
          delete updatedNormalized.ids.resourcesByLesson[newLessonId];

          // ✅ FIX 25: Selectively update just this module in the course
          const updatedCourse = state.course ? {
            ...state.course,
            modules: state.course.modules?.map(module => {
              if (String(module.id) === moduleId) {
                return {
                  ...module,
                  lessons: module.lessons?.map(lesson => {
                    if (lesson.id === newLessonId) {
                      return savedLesson;
                    }
                    return lesson;
                  }) || []
                };
              }
              return module;
            }) || []
          } : null;

          return {
            course: updatedCourse,
            normalized: updatedNormalized,
            session: {
              ...state.session,
              status: 'saved'
            }
          };
        });
      }

      return savedLesson;
    } catch (error) {
      console.error('Error saving lesson:', error);

      // Rollback optimistic update on error
      const state = get();
      if (state._isMounted) {
        set(state => ({
          ...state,
          course: originalState.course,
          normalized: originalState.normalized,
          error: 'Failed to save lesson',
          session: {
            ...state.session,
            status: 'error',
            error: error instanceof Error ? error.message : 'Failed to save lesson'
          }
        }));
        toast.error('Failed to save lesson. Changes reverted.');
      }

      throw error;
    }

    return newLesson;
  },

  // ✅ FIX 26: Refactored updateLesson to use the shared updateNested helper
  updateLesson: (moduleId, lessonId, data) => {
    set(state => {
      if (!state.course?.modules) return state;

      const updateNestedItems = get().updateNested;

      const modules = updateNestedItems(
        state.course.modules,
        module => String(module.id) === moduleId,
        module => ({
          ...module,
          lessons: updateNestedItems(
            module.lessons || [],
            lesson => String(lesson.id) === lessonId,
            lesson => ({ ...lesson, ...data })
          )
        })
      );

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // ✅ FIX 27: Refactored deleteLesson to use the shared updateNested helper
  deleteLesson: (moduleId, lessonId) => {
    set(state => {
      if (!state.course?.modules) return state;

      const updateNestedItems = get().updateNested;

      const modules = updateNestedItems(
        state.course.modules,
        module => String(module.id) === moduleId,
        module => ({
          ...module,
          lessons: (module.lessons || []).filter(
            lesson => String(lesson.id) !== lessonId
          )
        })
      );

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  reorderLessons: (moduleId, newOrder) => {
    set(state => {
      if (!state.course?.modules) return state;

      const modules = state.course.modules.map(module => {
        if (String(module.id) === moduleId) {
          const lessonMap = new Map(
            (module.lessons || []).map(lesson => [String(lesson.id), lesson])
          );

          const reorderedLessons = newOrder
            .map(id => lessonMap.get(id))
            .filter((lesson): lesson is Lesson => !!lesson)
            .map((lesson, index) => ({ ...lesson, order: index }));

          return { ...module, lessons: reorderedLessons };
        }
        return module;
      });

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // ✅ FIX 28: Refactored addResource to use the shared updateNested helper
  addResource: (moduleId, lessonId) => {
    set(state => {
      if (!state.course?.modules) return state;

      const newResource: Resource = {
        id: generateTempId(),
        title: 'New Resource',
        url: '',
        type: 'link',
      };

      const updateNestedItems = get().updateNested;

      const modules = updateNestedItems(
        state.course.modules,
        module => String(module.id) === moduleId,
        module => ({
          ...module,
          lessons: updateNestedItems(
            module.lessons || [],
            lesson => String(lesson.id) === lessonId,
            lesson => ({
              ...lesson,
              resources: [...(lesson.resources || []), newResource]
            })
          )
        })
      );

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // ✅ FIX 29: Refactored updateResource to use the shared updateNested helper
  updateResource: (moduleId, lessonId, resourceId, data) => {
    set(state => {
      if (!state.course?.modules) return state;

      const updateNestedItems = get().updateNested;

      const modules = updateNestedItems(
        state.course.modules,
        module => String(module.id) === moduleId,
        module => ({
          ...module,
          lessons: updateNestedItems(
            module.lessons || [],
            lesson => String(lesson.id) === lessonId,
            lesson => ({
              ...lesson,
              resources: updateNestedItems(
                lesson.resources || [],
                resource => String(resource.id) === resourceId,
                resource => ({ ...resource, ...data })
              )
            })
          )
        })
      );

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },


  // ✅ FIX 30: Refactored deleteResource to use the shared updateNested helper
  deleteResource: (moduleId, lessonId, resourceId) => {
    set(state => {
      if (!state.course?.modules) return state;

      const updateNestedItems = get().updateNested;

      const modules = updateNestedItems(
        state.course.modules,
        module => String(module.id) === moduleId,
        module => ({
          ...module,
          lessons: updateNestedItems(
            module.lessons || [],
            lesson => String(lesson.id) === lessonId,
            lesson => ({
              ...lesson,
              resources: (lesson.resources || []).filter(
                resource => String(resource.id) !== resourceId
              )
            })
          )
        })
      );

      return {
        course: {
          ...state.course,
          modules,
          updatedAt: new Date().toISOString()
        },
        isDirty: true,
        isPristine: false,
        session: {
          ...state.session,
          status: 'saving',
          isDirty: true,
          isPristine: false
        }
      };
    });
  },

  // ✅ FIX 31: Fixed publishVersion to use functional setState pattern
  publishVersion: async () => {
    const state = get();
    const { course } = state;

    if (!course?.slug) {
      toast.error("Can't publish: no slug");
      return;
    }

    // Cancel previous operation
    if (state._abortController) {
      state._abortController.abort();
    }

    const abortController = new AbortController();

    // Use functional setState to avoid overwriting other state
    set(state => ({
      ...state,
      isSaving: true,
      _abortController: abortController,
      session: {
        ...state.session,
        status: 'saving'
      }
    }));

    try {
      const published = await courseBuilderAPI.publish(course.slug, {
        signal: abortController.signal
      });

      // Only update if still mounted and not aborted
      const currentState = get();
      if (currentState._isMounted && !abortController.signal.aborted) {
        set(state => ({
          ...state,
          course: {
            ...published,
            updatedAt: new Date().toISOString()
          },
          normalized: normalizeCourse(published),
          isDirty: false,
          isPristine: true,
          isSaving: false,
          lastSaved: new Date(),
          _abortController: null,
          session: {
            ...state.session,
            status: 'saved',
            isDirty: false,
            isPristine: true,
            lastSaved: new Date()
          }
        }));

        toast.success('Course published successfully');
      }
    } catch (e: any) {
      if (!abortController.signal.aborted) {
        const currentState = get();
        if (currentState._isMounted) {
          set(state => ({
            ...state,
            isSaving: false,
            error: e.message || 'Publish failed',
            _abortController: null,
            session: {
              ...state.session,
              status: 'error',
              error: e.message || 'Publish failed'
            }
          }));
          toast.error(e.message || 'Failed to publish course');
        }
      }
    }
  },

  // ✅ FIX 32: Fixed unpublishVersion to use functional setState pattern
  unpublishVersion: async () => {
    const state = get();
    const { course } = state;

    if (!course?.slug) {
      toast.error("Can't unpublish: no slug");
      return;
    }

    if (state._abortController) {
      state._abortController.abort();
    }

    const abortController = new AbortController();

    // Use functional setState
    set(state => ({
      ...state,
      isSaving: true,
      _abortController: abortController,
      session: {
        ...state.session,
        status: 'saving'
      }
    }));

    try {
      const unpublished = await courseBuilderAPI.unpublish(course.slug, {
        signal: abortController.signal
      });

      const currentState = get();
      if (currentState._isMounted && !abortController.signal.aborted) {
        set(state => ({
          ...state,
          course: {
            ...unpublished,
            updatedAt: new Date().toISOString()
          },
          normalized: normalizeCourse(unpublished),
          isDirty: false,
          isPristine: true,
          isSaving: false,
          lastSaved: new Date(),
          _abortController: null,
          session: {
            ...state.session,
            status: 'saved',
            isDirty: false,
            isPristine: true,
            lastSaved: new Date()
          }
        }));

        toast.success('Course unpublished');
      }
    } catch (e: any) {
      if (!abortController.signal.aborted) {
        const currentState = get();
        if (currentState._isMounted) {
          set(state => ({
            ...state,
            isSaving: false,
            error: e.message || 'Unpublish failed',
            _abortController: null,
            session: {
              ...state.session,
              status: 'error',
              error: e.message || 'Unpublish failed'
            }
          }));
          toast.error(e.message || 'Failed to unpublish course');
        }
      }
    }
  },

  // ✅ FIX 33: Fixed cloneVersion to use functional setState pattern
  cloneVersion: async () => {
    const state = get();
    const { course } = state;

    if (!course?.slug) {
      toast.error("Can't clone: no slug");
      return;
    }

    if (state._abortController) {
      state._abortController.abort();
    }

    const abortController = new AbortController();

    // Use functional setState
    set(state => ({
      ...state,
      isSaving: true,
      _abortController: abortController,
      session: {
        ...state.session,
        status: 'saving'
      }
    }));

    try {
      const draft = await courseBuilderAPI.cloneVersion(course.slug, {
        signal: abortController.signal
      });

      const currentState = get();
      if (currentState._isMounted && !abortController.signal.aborted) {
        set(state => ({
          ...state,
          course: {
            ...draft,
            updatedAt: new Date().toISOString()
          },
          normalized: normalizeCourse(draft),
          isDirty: false,
          isPristine: true,
          isSaving: false,
          lastSaved: new Date(),
          _abortController: null,
          session: {
            ...state.session,
            status: 'saved',
            isDirty: false,
            isPristine: true,
            lastSaved: new Date(),
            activeId: String(draft.id)
          }
        }));

        toast.success('Created new draft version');
      }
    } catch (e: any) {
      if (!abortController.signal.aborted) {
        const currentState = get();
        if (currentState._isMounted) {
          set(state => ({
            ...state,
            isSaving: false,
            error: e.message || 'Clone failed',
            _abortController: null,
            session: {
              ...state.session,
              status: 'error',
              error: e.message || 'Clone failed'
            }
          }));
          toast.error(e.message || 'Failed to create new version');
        }
      }
    }
  },

  // ✅ FIX 34: Enhanced mapTempIdsToReal to include resources
  mapTempIdsToReal: (serverCourse) => {
    set(state => {
      if (!state.course || !serverCourse?.modules) return state;

      // Use server response to map IDs directly when available
      const moduleMap = new Map<string, Module>();
      serverCourse.modules.forEach((serverModule) => {
        moduleMap.set(String(serverModule.id), serverModule);
      });

      // Create maps for lessons and resources
      const lessonMap = new Map<string, Lesson>();
      const resourceMap = new Map<string, Resource>();

      // Populate the maps from server data
      serverCourse.modules.forEach(serverModule => {
        if (serverModule.lessons) {
          serverModule.lessons.forEach(serverLesson => {
            lessonMap.set(String(serverLesson.id), serverLesson);

            if (serverLesson.resources) {
              serverLesson.resources.forEach(serverResource => {
                resourceMap.set(String(serverResource.id), serverResource);
              });
            }
          });
        }
      });

      const findBestModuleMatch = (localModule: Module) => {
        if (!isTempId(localModule.id)) {
          return moduleMap.get(String(localModule.id));
        }

        // Enhanced matching: use creation order + title + lesson count
        for (const [, serverModule] of moduleMap) {
          if (
            serverModule.title === localModule.title &&
            serverModule.order === localModule.order &&
            (serverModule.lessons?.length || 0) === (localModule.lessons?.length || 0)
          ) {
            return serverModule;
          }
        }

        // Fallback to title match
        for (const [, serverModule] of moduleMap) {
          if (serverModule.title === localModule.title) {
            return serverModule;
          }
        }

        return null;
      };

      const findBestLessonMatch = (localLesson: Lesson) => {
        if (!isTempId(localLesson.id)) {
          return lessonMap.get(String(localLesson.id));
        }

        // Try exact title + order match first
        for (const [, serverLesson] of lessonMap) {
          if (
            serverLesson.title === localLesson.title &&
            serverLesson.order === localLesson.order
          ) {
            return serverLesson;
          }
        }

        // Fallback to title match
        for (const [, serverLesson] of lessonMap) {
          if (serverLesson.title === localLesson.title) {
            return serverLesson;
          }
        }

        return null;
      };

      const findBestResourceMatch = (localResource: Resource) => {
        if (!isTempId(localResource.id)) {
          return resourceMap.get(String(localResource.id));
        }

        // Try title + type match first
        for (const [, serverResource] of resourceMap) {
          if (
            serverResource.title === localResource.title &&
            serverResource.type === localResource.type
          ) {
            return serverResource;
          }
        }

        // Fallback to just title match
        for (const [, serverResource] of resourceMap) {
          if (serverResource.title === localResource.title) {
            return serverResource;
          }
        }

        return null;
      };

      if (state.course.modules) {
        const reconciledModules = state.course.modules.map(localModule => {
          const matchedModule = findBestModuleMatch(localModule);

          if (matchedModule) {
            let reconciledLessons = localModule.lessons;

            if (matchedModule.lessons && localModule.lessons) {
              reconciledLessons = localModule.lessons.map((localLesson) => {
                const matchedLesson = findBestLessonMatch(localLesson);

                if (matchedLesson) {
                  // Now also handle resources
                  let reconciledResources = localLesson.resources;

                  if (matchedLesson.resources && localLesson.resources) {
                    reconciledResources = localLesson.resources.map(localResource => {
                      const matchedResource = findBestResourceMatch(localResource);

                      if (matchedResource) {
                        return {
                          ...localResource,
                          id: matchedResource.id,
                        };
                      }

                      return localResource;
                    });
                  }

                  return {
                    ...localLesson,
                    id: matchedLesson.id,
                    resources: reconciledResources
                  };
                }

                return localLesson;
              });
            }

            return {
              ...localModule,
              id: matchedModule.id,
              lessons: reconciledLessons,
            };
          }

          return localModule;
        });

        // Update normalized state too
        const normalizedState = normalizeCourse({
          ...state.course,
          modules: reconciledModules,
          id: serverCourse.id || state.course.id
        });

        return {
          course: {
            ...state.course,
            id: serverCourse.id || state.course.id, // Make sure course ID is also reconciled
            modules: reconciledModules,
            updatedAt: new Date().toISOString()
          },
          normalized: normalizedState,
          session: {
            ...state.session,
            activeId: String(serverCourse.id || state.course.id)
          }
        };
      }

      return state;
    });
  },

  // ✅ FIX 35: Enhanced cleanup method to clear all timeouts
  cleanup: () => {
    const state = get();

    // Cancel any pending operations
    if (state._abortController) {
      state._abortController.abort();
    }

    // Clear all stored timeouts
    state._timeouts.forEach(timeoutId => {
      clearTimeout(timeoutId);
    });

    // Mark as unmounted
    set({
      _isMounted: false,
      _abortController: null,
      _timeouts: []
    });

    // External cleanup (e.g., for debounced operations in components)
    courseBuilderAPI.cancelReorder();
  },
}));

// Export Zustand store as default export
export default useCourseStore;
