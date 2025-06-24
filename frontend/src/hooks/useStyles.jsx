/**
 * useStyles Hook
 *
 * This custom hook provides a convenient way to access all styling utilities
 * and theme variables throughout the application.
 *
 * Features:
 * - Access to theme variables (colors, spacing, typography, etc.)
 * - Component style presets from theme.js
 * - Helper functions for style manipulation
 *
 * Usage:
 * import { useStyles } from '../hooks/useStyles';
 *
 * function MyComponent() {
 *   const { colors, components, combineClasses } = useStyles();
 *   return (
 *     <button className={combineClasses(
 *       components.button.primary,
 *       components.button.sizes.md
 *     )}>
 *       Click Me
 *     </button>
 *   );
 * }
 *
 * Created: 2025-05-03
 * Last updated: 2025-05-03 13:15:30
 * Author: nanthiniSanthanam
 */

import {
  COLORS,
  LAYOUT,
  TYPOGRAPHY,
  SHADOWS,
  TRANSITIONS,
  Z_INDEX,
  COMPONENT_STYLES,
  SPACING,
  BREAKPOINTS,
  ANIMATIONS,
} from '../styles/theme';

/**
 * Custom hook for accessing styling utilities and theme variables
 * @returns {Object} An object containing theme values and helper functions
 */
export function useStyles() {
  /**
   * Combines multiple class strings, filtering out falsy values
   * @param {...string} classes - Class strings to combine
   * @returns {string} Combined class string
   */
  const combineClasses = (...classes) => {
    return classes.filter(Boolean).join(' ');
  };

  /**
   * Gets a nested value from an object using a dot-notation path
   * @param {Object} obj - The object to traverse
   * @param {string} path - Dot-notation path (e.g., 'colors.primary.500')
   * @param {*} defaultValue - Default value if path doesn't exist
   * @returns {*} Value from the object or defaultValue
   */
  const getNestedValue = (obj, path, defaultValue = undefined) => {
    const keys = path.split('.');
    return (
      keys.reduce((acc, key) => {
        return acc && acc[key] !== undefined ? acc[key] : undefined;
      }, obj) ?? defaultValue
    );
  };

  /**
   * Creates a CSS variable string from a theme value
   * @param {string} path - Path to the theme value (e.g., 'colors.primary.500')
   * @returns {string} CSS variable string
   */
  const createVar = path => {
    return `var(--${path.replace(/\./g, '-')})`;
  };

  return {
    // Theme variables
    colors: COLORS,
    layout: LAYOUT,
    typography: TYPOGRAPHY,
    shadows: SHADOWS,
    spacing: SPACING,
    transitions: TRANSITIONS,
    zIndex: Z_INDEX,
    breakpoints: BREAKPOINTS,
    animations: ANIMATIONS,

    // Component styles
    components: COMPONENT_STYLES,

    // Helper functions
    combineClasses,
    getNestedValue,
    createVar,

    // Shorthand helpers
    color: (path, defaultValue) => getNestedValue(COLORS, path, defaultValue),
    fontSize: key => TYPOGRAPHY.fontSize[key],
    shadow: key => SHADOWS[key],
    spacing: key => SPACING[key],
  };
}

export default useStyles;
