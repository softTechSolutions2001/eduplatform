/**
 * File: frontend/src/courseBuilder/dnd/useDragTypes.ts
 * Version: 2.1.0
 * Date Created: 2025-06-14 16:11:05
 * Date Revised: 2025-06-14 16:11:05 UTC
 * Current User: sujibeautysalon
 * Last Modified By: sujibeautysalon
 *
 * Enhanced Drag Types Management Utility with Type Safety and Validation
 *
 * This module provides centralized management of drag-and-drop types across
 * the course builder interface. It eliminates magic strings, provides type safety,
 * and includes validation utilities for drag operations.
 *
 * Key Features:
 * - Centralized drag type constants with consistent naming
 * - Type safety with proper TypeScript definitions
 * - Validation utilities for drag operations
 * - Debugging helpers for troubleshooting drag issues
 * - Extensible architecture for future drag types
 * - Error handling with descriptive messages
 *
 * Version 2.1.0 Changes (Surgical Fixes from Code Review):
 * - FIXED: Centralized drag types with consistent naming conventions
 * - FIXED: Added comprehensive type safety with TypeScript definitions
 * - FIXED: Eliminated magic strings with exported constants
 * - FIXED: Enhanced validation utilities for drag operations
 * - FIXED: Added debugging support with type checking helpers
 * - FIXED: Improved maintainability with centralized configuration
 * - FIXED: Added error handling for invalid drag types
 * - FIXED: Extended API for future drag type requirements
 *
 * Connected Files:
 * - frontend/src/courseBuilder/dnd/DnDContext.tsx - Provides base item types
 * - frontend/src/courseBuilder/dnd/Sortable.tsx - Uses drag types for operations
 * - frontend/src/courseBuilder/components/ModuleCard.tsx - Module drag operations
 * - frontend/src/courseBuilder/components/LessonCard.tsx - Lesson drag operations
 * - frontend/src/courseBuilder/components/ResourceChip.tsx - Resource drag operations
 */

import { ITEM_TYPES } from './DnDContext';

// ✅ FIX 1: Enhanced type definitions for drag operations
export type DragType = keyof typeof ITEM_TYPES;
export type DragTypeValue = typeof ITEM_TYPES[DragType];

// ✅ FIX 2: Extended drag item interface with metadata
export interface DragItem {
  id: string | number;
  index: number;
  type: DragTypeValue;
  data?: Record<string, any>;
  metadata?: {
    parentId?: string | number;
    originalIndex?: number;
    timestamp?: number;
    source?: string;
  };
}

// ✅ FIX 3: Drag operation result interface
export interface DragResult {
  success: boolean;
  dragType: DragTypeValue;
  sourceIndex: number;
  targetIndex: number;
  item: DragItem;
  error?: string;
}

// ✅ FIX 4: Validation configuration
interface DragTypeConfig {
  [key: string]: {
    name: string;
    allowedParents?: string[];
    allowedChildren?: string[];
    maxDepth?: number;
    validationRules?: Array<(item: DragItem) => boolean>;
    errorMessages?: Record<string, string>;
  };
}

// ✅ FIX 5: Comprehensive drag type configuration
const DRAG_TYPE_CONFIG: DragTypeConfig = {
  [ITEM_TYPES.MODULE]: {
    name: 'Module',
    allowedChildren: [ITEM_TYPES.LESSON],
    maxDepth: 1,
    validationRules: [
      (item) => typeof item.id !== 'undefined',
      (item) => typeof item.index === 'number',
    ],
    errorMessages: {
      invalidId: 'Module must have a valid ID',
      invalidIndex: 'Module must have a valid index',
      invalidParent: 'Modules cannot be nested inside other items',
    },
  },
  [ITEM_TYPES.LESSON]: {
    name: 'Lesson',
    allowedParents: [ITEM_TYPES.MODULE],
    allowedChildren: [ITEM_TYPES.RESOURCE],
    maxDepth: 2,
    validationRules: [
      (item) => typeof item.id !== 'undefined',
      (item) => typeof item.index === 'number',
      (item) => item.metadata?.parentId !== undefined,
    ],
    errorMessages: {
      invalidId: 'Lesson must have a valid ID',
      invalidIndex: 'Lesson must have a valid index',
      invalidParent: 'Lessons must belong to a module',
      noParentId: 'Lesson must have a parent module ID',
    },
  },
  [ITEM_TYPES.RESOURCE]: {
    name: 'Resource',
    allowedParents: [ITEM_TYPES.LESSON],
    maxDepth: 3,
    validationRules: [
      (item) => typeof item.id !== 'undefined',
      (item) => typeof item.index === 'number',
      (item) => item.metadata?.parentId !== undefined,
    ],
    errorMessages: {
      invalidId: 'Resource must have a valid ID',
      invalidIndex: 'Resource must have a valid index',
      invalidParent: 'Resources must belong to a lesson',
      noParentId: 'Resource must have a parent lesson ID',
    },
  },
};

// ✅ FIX 6: Enhanced drag types hook with validation utilities
export const useDragTypes = () => {
  // ✅ FIX 7: Type validation utilities
  const isValidDragType = (type: string): type is DragTypeValue => {
    return Object.values(ITEM_TYPES).includes(type as DragTypeValue);
  };

  const validateDragItem = (item: DragItem): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!item) {
      errors.push('Drag item cannot be null or undefined');
      return { isValid: false, errors };
    }

    if (!isValidDragType(item.type)) {
      errors.push(`Invalid drag type: ${item.type}`);
      return { isValid: false, errors };
    }

    const config = DRAG_TYPE_CONFIG[item.type];
    if (!config) {
      errors.push(`No configuration found for drag type: ${item.type}`);
      return { isValid: false, errors };
    }

    // Run validation rules
    if (config.validationRules) {
      for (const rule of config.validationRules) {
        try {
          if (!rule(item)) {
            errors.push(`Validation rule failed for ${config.name.toLowerCase()}`);
          }
        } catch (error) {
          errors.push(`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }
    }

    return { isValid: errors.length === 0, errors };
  };

  // ✅ FIX 8: Drag operation validation
  const canDrop = (dragItem: DragItem, targetType: DragTypeValue, targetParentType?: DragTypeValue): boolean => {
    if (!isValidDragType(dragItem.type) || !isValidDragType(targetType)) {
      return false;
    }

    const dragConfig = DRAG_TYPE_CONFIG[dragItem.type];
    const targetConfig = DRAG_TYPE_CONFIG[targetType];

    // Check if drag item can be dropped on target
    if (dragConfig.allowedParents && !dragConfig.allowedParents.includes(targetType)) {
      return false;
    }

    // Check if target can accept drag item
    if (targetConfig.allowedChildren && !targetConfig.allowedChildren.includes(dragItem.type)) {
      return false;
    }

    // Check depth restrictions
    if (targetParentType) {
      const parentConfig = DRAG_TYPE_CONFIG[targetParentType];
      if (parentConfig.maxDepth && getTypeDepth(dragItem.type) > parentConfig.maxDepth) {
        return false;
      }
    }

    return true;
  };

  // ✅ FIX 9: Type hierarchy utilities
  const getTypeDepth = (type: DragTypeValue): number => {
    const typeDepths: Record<DragTypeValue, number> = {
      [ITEM_TYPES.MODULE]: 1,
      [ITEM_TYPES.LESSON]: 2,
      [ITEM_TYPES.RESOURCE]: 3,
    };
    return typeDepths[type] || 0;
  };

  const getTypeHierarchy = (): DragTypeValue[] => {
    return [ITEM_TYPES.MODULE, ITEM_TYPES.LESSON, ITEM_TYPES.RESOURCE];
  };

  const getParentTypes = (type: DragTypeValue): DragTypeValue[] => {
    const config = DRAG_TYPE_CONFIG[type];
    return (config.allowedParents as DragTypeValue[]) || [];
  };

  const getChildTypes = (type: DragTypeValue): DragTypeValue[] => {
    const config = DRAG_TYPE_CONFIG[type];
    return (config.allowedChildren as DragTypeValue[]) || [];
  };

  // ✅ FIX 10: Debugging and logging utilities
  const logDragOperation = (operation: string, item: DragItem, target?: any): void => {
    if (process.env.NODE_ENV === 'development') {
      console.group(`🔄 Drag Operation: ${operation}`);
      console.log('Item:', item);
      if (target) console.log('Target:', target);
      console.log('Type Config:', DRAG_TYPE_CONFIG[item.type]);
      console.groupEnd();
    }
  };

  const getDragTypeInfo = (type: DragTypeValue) => {
    return DRAG_TYPE_CONFIG[type] || null;
  };

  // ✅ FIX 11: Error handling utilities
  const createDragError = (message: string, item?: DragItem, context?: string): Error => {
    const errorMessage = context ? `[${context}] ${message}` : message;
    const error = new Error(errorMessage);

    if (item && process.env.NODE_ENV === 'development') {
      console.error('Drag Error:', {
        message: errorMessage,
        item,
        type: item.type,
        config: DRAG_TYPE_CONFIG[item.type],
      });
    }

    return error;
  };

  // ✅ FIX 12: Item creation utilities
  const createDragItem = (
    id: string | number,
    index: number,
    type: DragTypeValue,
    data?: Record<string, any>,
    metadata?: DragItem['metadata']
  ): DragItem => {
    const item: DragItem = {
      id,
      index,
      type,
      data,
      metadata: {
        timestamp: Date.now(),
        source: 'useDragTypes',
        ...metadata,
      },
    };

    const validation = validateDragItem(item);
    if (!validation.isValid) {
      throw createDragError(
        `Failed to create drag item: ${validation.errors.join(', ')}`,
        item,
        'createDragItem'
      );
    }

    return item;
  };

  // ✅ FIX 13: Type conversion utilities
  const getDragTypeFromString = (typeString: string): DragTypeValue | null => {
    if (isValidDragType(typeString)) {
      return typeString;
    }

    // Try case-insensitive match
    const normalizedType = typeString.toLowerCase();
    const matchedType = Object.values(ITEM_TYPES).find(
      type => type.toLowerCase() === normalizedType
    );

    return matchedType || null;
  };

  const getAllDragTypes = (): DragTypeValue[] => {
    return Object.values(ITEM_TYPES);
  };

  // ✅ FIX 14: Performance optimization utilities
  const memoizedValidations = new Map<string, { isValid: boolean; errors: string[] }>();

  const validateDragItemCached = (item: DragItem): { isValid: boolean; errors: string[] } => {
    const cacheKey = `${item.type}_${item.id}_${item.index}_${JSON.stringify(item.metadata)}`;

    if (memoizedValidations.has(cacheKey)) {
      return memoizedValidations.get(cacheKey)!;
    }

    const result = validateDragItem(item);

    // Limit cache size to prevent memory leaks
    if (memoizedValidations.size > 1000) {
      const firstKey = memoizedValidations.keys().next().value;
      memoizedValidations.delete(firstKey);
    }

    memoizedValidations.set(cacheKey, result);
    return result;
  };

  const clearValidationCache = (): void => {
    memoizedValidations.clear();
  };

  // ✅ FIX 15: Return comprehensive API
  return {
    // Core drag types
    types: ITEM_TYPES,

    // Type information
    config: DRAG_TYPE_CONFIG,

    // Validation utilities
    isValidDragType,
    validateDragItem,
    validateDragItemCached,
    canDrop,

    // Type hierarchy
    getTypeDepth,
    getTypeHierarchy,
    getParentTypes,
    getChildTypes,

    // Item creation
    createDragItem,

    // Type conversion
    getDragTypeFromString,
    getAllDragTypes,

    // Information utilities
    getDragTypeInfo,

    // Debugging utilities
    logDragOperation,

    // Error handling
    createDragError,

    // Performance utilities
    clearValidationCache,

    // Legacy compatibility
    MODULE: ITEM_TYPES.MODULE,
    LESSON: ITEM_TYPES.LESSON,
    RESOURCE: ITEM_TYPES.RESOURCE,
  } as const;
};

// ✅ FIX 16: Export individual utilities for tree-shaking
export const dragTypes = ITEM_TYPES;
export const dragTypeConfig = DRAG_TYPE_CONFIG;

// ✅ FIX 17: Standalone validation function for external use
export const validateDragItem = (item: DragItem): { isValid: boolean; errors: string[] } => {
  return useDragTypes().validateDragItem(item);
};

// ✅ FIX 18: Standalone type checking for external use
export const isValidDragType = (type: string): type is DragTypeValue => {
  return Object.values(ITEM_TYPES).includes(type as DragTypeValue);
};

// ✅ FIX 19: Quick access constants for common operations
export const DRAG_TYPES = {
  MODULE: ITEM_TYPES.MODULE,
  LESSON: ITEM_TYPES.LESSON,
  RESOURCE: ITEM_TYPES.RESOURCE,
} as const;

// ✅ FIX 20: Type exports for external use
export type {
  DragItem,
  DragResult, DragType,
  DragTypeValue
};

// Default export for backward compatibility
export default useDragTypes;
