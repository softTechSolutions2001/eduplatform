/**
 * File: frontend/src/courseBuilder/utils/caseConvert.ts
 * Version: 2.1.0
 * Date: 2025-06-14 14:47:04 UTC
 * Author: sujibeautysalon
 * Last Modified: 2025-06-14 14:47:04 UTC
 *
 * Case Conversion Utilities with Deep Object Transformation
 *
 * This module provides utilities for converting between camelCase and snake_case
 * formats, with support for deep object transformation and FormData conversion.
 *
 * Key Features:
 * - Basic string case conversion (camelCase ↔ snake_case)
 * - Deep object key transformation with mapKeys and mapKeysDeep
 * - FormData conversion with proper key transformation
 * - File handling in object transformation
 * - Array and nested object support
 *
 * Version 2.1.0 Changes:
 * - Added mapKeysDeep function for deep nested object transformation
 * - Fixed circular import issues by using named exports only
 * - Enhanced type safety for transformation functions
 * - Added proper handling of File objects in deep transformation
 *
 * Connected Files:
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - Uses deep transformation
 * - frontend/src/utils/buildCourseFormData.ts - Uses FormData conversion
 * - frontend/src/courseBuilder/utils/object.ts - Utility integration
 */

export const camelToSnake = (s: string) =>
  s.replace(/[A-Z]/g, m => `_${m.toLowerCase()}`);

export const snakeToCamel = (s: string) =>
  s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());

export const mapKeys = <T extends any>(
  obj: T,
  fn: (k: string) => string
): any => {
  if (Array.isArray(obj)) return obj.map(i => mapKeys(i, fn));
  if (obj !== null && typeof obj === 'object' && !(obj instanceof File)) {
    return Object.fromEntries(
      Object.entries(obj).map(([k, v]) => [fn(k), mapKeys(v, fn)])
    );
  }
  return obj;
};

/**
 * Deep transformation of object keys with proper type handling
 * Enhanced version that handles nested arrays and objects more reliably
 *
 * @param obj - Object to transform (can be array, object, or primitive)
 * @param fn - Function to transform each key
 * @returns Transformed object with same structure but converted keys
 */
export const mapKeysDeep = <T = any>(obj: T, fn: (k: string) => string): T => {
  // Handle arrays - recursively transform each element
  if (Array.isArray(obj)) {
    return obj.map(item => mapKeysDeep(item, fn)) as unknown as T;
  }

  // Handle objects (but not File objects, Dates, or other special objects)
  if (obj && typeof obj === 'object' && !(obj instanceof File) && !(obj instanceof Date)) {
    return Object.fromEntries(
      Object.entries(obj).map(([key, value]) => [
        fn(key),
        mapKeysDeep(value, fn)
      ])
    ) as T;
  }

  // Return primitives, Files, Dates, and other special objects as-is
  return obj;
};

export const toFormData = (data: Record<string, any>, root = ''): FormData => {
  const fd = new FormData();
  const walk = (value: any, keyPath: string) => {
    if (value === null || value === undefined) return;
    if (value instanceof File) {
      fd.append(keyPath, value);
    } else if (Array.isArray(value)) {
      value.forEach((v, i) => walk(v, `${keyPath}[${i}]`));
    } else if (typeof value === 'object') {
      Object.entries(value).forEach(([k, v]) =>
        walk(v, `${keyPath}[${camelToSnake(k)}]`)
      );
    } else {
      fd.append(keyPath, value.toString());
    }
  };
  Object.entries(data).forEach(([k, v]) => walk(v, camelToSnake(k)));
  return fd;
};

/**
 * Converts a plain JavaScript object to FormData with snake_cased keys
 * Handles all types of values including nested objects, arrays, and Files
 */
export const objectToSnakeFormData = (obj: Record<string, any>): FormData => {
  const snakeObj = mapKeys(obj, camelToSnake);
  return toFormData(snakeObj);
};
