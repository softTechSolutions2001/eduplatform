/**
 * EduPlatform Theme Configuration
 *
 * This file serves as the single source of truth for all design tokens in the application.
 * It provides consistent styling variables that can be used throughout the codebase.
 *
 * Key Features:
 * - Complete color palette with semantic naming
 * - Typography settings (fonts, sizes, weights)
 * - Layout constants (heights, widths, spacing)
 * - Shadows, transitions, z-index scales, and other design tokens
 *
 * Variables that can be modified:
 * - COLOR_PALETTE: Brand colors can be adjusted to match design requirements
 * - LAYOUT: Header heights and component dimensions can be modified
 * - FONTS: Font families can be updated based on typography needs
 *
 * Usage:
 * import { COLORS, LAYOUT, TYPOGRAPHY } from '../styles/theme';
 *
 * Created: 2025-05-03
 * Last updated: 2025-05-03 13:15:30
 * Author: nanthiniSanthanam
 */

// Color Palette - Main brand colors
export const COLORS = {
  primary: {
    50: '#eef5ff',
    100: '#d9e8ff',
    200: '#bbd5ff',
    300: '#8bbaff',
    400: '#5694ff',
    500: '#3d74f4', // Primary brand color
    600: '#2a56cf',
    700: '#2342b8', // From gradient
    800: '#22398b',
    900: '#1e3372',
    950: '#172048',
  },
  secondary: {
    50: '#fff6ed',
    100: '#ffebd4',
    200: '#ffd3a8',
    300: '#ffb36f',
    400: '#ff9141',
    500: '#ff7425', // Secondary brand color
    600: '#ed5511',
    700: '#c5400c',
    800: '#9c3410',
    900: '#7e2d12',
    950: '#441407',
  },
  tertiary: {
    50: '#ecfff7',
    100: '#d5fff0',
    200: '#aeffe0',
    300: '#72ffcb',
    400: '#30ebb0',
    500: '#19b29a', // Tertiary brand color
    600: '#0b7268', // From gradient
    700: '#0a7566',
    800: '#0d5d52',
    900: '#0f4c44',
    950: '#02251e',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#0d1117',
  },
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#0ea5e9',
  },
};

// Layout Constants - Application dimensions
export const LAYOUT = {
  // Header dimensions - Can be modified to match component implementation
  headerHeight: '80px',
  dateTimeHeight: '28px',
  totalHeaderOffset: '108px', // Combined height (headerHeight + dateTimeHeight)

  // Layout dimensions
  sidebarWidth: '240px',
  maxContentWidth: '1280px',

  // Containers
  containerPadding: {
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
  },

  // Border radius
  borderRadius: {
    sm: '0.25rem', // 4px
    md: '0.5rem', // 8px
    lg: '0.75rem', // 12px
    xl: '1rem', // 16px
    '2xl': '1.5rem', // 24px
    full: '9999px',
  },
};

// Typography - Font settings
export const TYPOGRAPHY = {
  fontFamily: {
    sans: '"Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    display:
      '"Plus Jakarta Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
  },
  fontSize: {
    xs: '0.75rem', // 12px
    sm: '0.875rem', // 14px
    base: '1rem', // 16px
    lg: '1.125rem', // 18px
    xl: '1.25rem', // 20px
    '2xl': '1.5rem', // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem', // 48px
  },
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },
};

// Shadows - Box shadow definitions
export const SHADOWS = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  card: '0 7px 15px rgba(0, 0, 0, 0.03), 0 3px 8px rgba(0, 0, 0, 0.05)',
  soft: '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01)',
  testimonial:
    '0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.01)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
  none: 'none',
};

// Spacing scale
export const SPACING = {
  px: '1px',
  0: '0px',
  0.5: '0.125rem',
  1: '0.25rem',
  1.5: '0.375rem',
  2: '0.5rem',
  2.5: '0.625rem',
  3: '0.75rem',
  3.5: '0.875rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  7: '1.75rem',
  8: '2rem',
  9: '2.25rem',
  10: '2.5rem',
  11: '2.75rem',
  12: '3rem',
  14: '3.5rem',
  16: '4rem',
  20: '5rem',
  24: '6rem',
  28: '7rem',
  32: '8rem',
  36: '9rem',
  40: '10rem',
  44: '11rem',
  48: '12rem',
  52: '13rem',
  56: '14rem',
  60: '15rem',
  64: '16rem',
  72: '18rem',
  80: '20rem',
  96: '24rem',
};

// Transition presets
export const TRANSITIONS = {
  fast: 'all 0.15s ease-in-out',
  default: 'all 0.3s ease-in-out',
  slow: 'all 0.5s ease-in-out',
  premium: 'all 0.3s ease', // For premium elements
};

// Z-index scale
export const Z_INDEX = {
  0: '0',
  10: '10',
  20: '20',
  30: '30',
  40: '40',
  50: '50',
  auto: 'auto',
  dropdown: '1000',
  sticky: '1020',
  fixed: '1030',
  modalBackdrop: '1040',
  modal: '1050',
  popover: '1060',
  tooltip: '1070',
};

// Breakpoints (matching Tailwind defaults)
export const BREAKPOINTS = {
  xs: '480px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Animation keyframes and durations
export const ANIMATIONS = {
  keyframes: {
    fadeIn: {
      '0%': { opacity: '0' },
      '100%': { opacity: '1' },
    },
    fadeInUp: {
      '0%': { opacity: '0', transform: 'translateY(20px)' },
      '100%': { opacity: '1', transform: 'translateY(0)' },
    },
    slideDown: {
      '0%': { transform: 'translateY(-20px)', opacity: '0' },
      '100%': { transform: 'translateY(0)', opacity: '1' },
    },
  },
  duration: {
    fast: '0.3s',
    default: '0.5s',
    slow: '0.8s',
  },
};

// Component styles using Tailwind classes - For consistent component styling
export const COMPONENT_STYLES = {
  // Button variants
  button: {
    primary:
      'bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-all duration-300',
    secondary:
      'bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-all duration-300',
    tertiary:
      'bg-tertiary-500 hover:bg-tertiary-600 text-white font-medium rounded-lg transition-all duration-300',
    outline:
      'border border-primary-500 text-primary-500 hover:bg-primary-50 font-medium rounded-lg transition-all duration-300',
    ghost:
      'text-primary-500 hover:bg-primary-50 font-medium rounded-lg transition-all duration-300',
    premium:
      'px-4 py-2 sm:px-6 sm:py-3 font-medium rounded-xl shadow-md transition-all duration-300 transform hover:-translate-y-0.5',
    // Button sizes
    sizes: {
      xs: 'px-2 py-1 text-xs',
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
      xl: 'px-8 py-4 text-xl',
    },
  },
  // Card variants
  card: {
    default: 'bg-white rounded-xl shadow-card overflow-hidden',
    premium:
      'bg-white rounded-xl shadow-card overflow-hidden transition-all duration-300 hover:shadow-soft hover:-translate-y-1',
    bordered: 'bg-white border border-gray-200 rounded-xl',
    glass: 'bg-white/10 backdrop-blur-md border border-white/10 rounded-xl',
  },
  // Input styles
  input: {
    default:
      'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors duration-200',
    error:
      'w-full px-4 py-2 border border-red-500 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-colors duration-200',
  },
  // Container styles
  container: {
    default: 'w-full mx-auto px-4 sm:px-6 lg:px-8',
    narrow: 'w-full mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl',
    wide: 'w-full mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl',
  },
};

// Export everything as a default object
export default {
  COLORS,
  LAYOUT,
  TYPOGRAPHY,
  SHADOWS,
  SPACING,
  TRANSITIONS,
  Z_INDEX,
  BREAKPOINTS,
  ANIMATIONS,
  COMPONENT_STYLES,
};
