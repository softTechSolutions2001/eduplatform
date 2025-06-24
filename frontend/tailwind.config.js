/**
 * Tailwind CSS Configuration
 * 
 * This file configures Tailwind CSS with custom theme settings derived from
 * our theme.js file to ensure consistency across the application.
 * 
 * Features:
 * - Imports and uses our theme variables from styles/theme.js
 * - Configures colors, typography, spacing, etc. to match our design system
 * - Sets up container defaults and custom plugins
 * 
 * Variables that can be modified:
 * - Update the primary, secondary, tertiary colors in the theme.js file
 * - The container settings can be adjusted based on layout requirements
 * 
 * Created: 2025-05-03
 * Last updated: 2025-06-02 14:07:19
 * Author: nanthiniSanthanam
 */

const { 
  COLORS, 
  TYPOGRAPHY, 
  SHADOWS, 
  LAYOUT, 
  ANIMATIONS 
} = require('./src/styles/theme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],

  theme: {
    // Container configuration
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '4rem',
        xl: '5rem',
      },
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },
    },

    extend: {
      colors: {
        // Import color palette from theme.js
        primary: COLORS.primary,
        secondary: COLORS.secondary,
        tertiary: COLORS.tertiary,
        gray: COLORS.gray,
        // Status colors
        success: COLORS.status.success,
        warning: COLORS.status.warning,
        error: COLORS.status.error,
        info: COLORS.status.info,
      },
      
      fontFamily: {
        sans: [TYPOGRAPHY.fontFamily.sans],
        display: [TYPOGRAPHY.fontFamily.display],
        mono: [TYPOGRAPHY.fontFamily.mono],
      },
      
      fontSize: TYPOGRAPHY.fontSize,
      fontWeight: TYPOGRAPHY.fontWeight,
      lineHeight: TYPOGRAPHY.lineHeight,
      
      boxShadow: SHADOWS,
      
      borderRadius: LAYOUT.borderRadius,
      
      animation: {
        'fade-in-up': `fadeInUp ${ANIMATIONS.duration.default} ease-out forwards`,
        'fade-in': `fadeIn ${ANIMATIONS.duration.default} ease-out forwards`,
        'slide-down': `slideDown ${ANIMATIONS.duration.fast} ease-out forwards`,
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      
      keyframes: ANIMATIONS.keyframes,
    }
  },
  
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}