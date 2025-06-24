/**
 * Styles Configuration
 *
 * This file contains global styling utilities and CSS variables for the application.
 * It provides a central location for managing reusable styles, animations,
 * and design system values that can be imported and used across components.
 *
 * Benefits:
 * 1. Consistency: Ensures visual consistency throughout the application
 * 2. Maintainability: Makes style updates easier by centralizing common values
 * 3. Reusability: Allows reuse of complex animations and styling logic
 */

// Animation keyframes for various effects
export const keyframes = {
  fadeInUp: `
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `,

  slideDown: `
      @keyframes slideDown {
        from {
          transform: translateY(-10px);
          opacity: 0;
        }
        to {
          transform: translateY(0);
          opacity: 1;
        }
      }
    `,

  pulse: `
      @keyframes pulse {
        0% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.05);
        }
        100% {
          transform: scale(1);
        }
      }
    `,
};

// CSS class for premium button styling
export const premiumButtonStyles = `
    .btn-premium {
      @apply px-6 py-3 rounded-lg font-medium transition-all duration-300;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }
    
    .btn-premium:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
    }
    
    .btn-premium:active {
      transform: translateY(0);
    }
  `;

// CSS class for premium card styling
export const premiumCardStyles = `
    .card-premium {
      @apply bg-white rounded-xl overflow-hidden transition-all duration-300;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .card-premium:hover {
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
      transform: translateY(-5px);
    }
  `;

// CSS class for glass effect
export const glassEffectStyles = `
    .glass-effect {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .glass-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
  `;

// CSS class for hero gradients
export const gradientStyles = `
    .hero-gradient {
      background: linear-gradient(135deg, #3d74f4 0%, #9867f0 100%);
    }
    
    .secondary-gradient {
      background: linear-gradient(135deg, #19b29a 0%, #3d74f4 100%);
    }
    
    .tertiary-gradient {
      background: linear-gradient(135deg, #ff7425 0%, #f5317f 100%);
    }
  `;

// CSS class for reveal animations
export const revealAnimationStyles = `
    .reveal {
      position: relative;
      opacity: 0;
      transition: all 0.8s ease;
      transform: translateY(30px);
    }
    
    .reveal.active {
      opacity: 1;
      transform: translateY(0);
    }
  `;

// CSS utility for hiding scrollbars
export const hideScrollbarStyles = `
    .hide-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
    
    .hide-scrollbar::-webkit-scrollbar {
      display: none;
    }
  `;

// Shadow styles
export const shadowStyles = `
    .shadow-testimonial {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    }
  `;

// Combine all styles for import into global CSS
export const allStyles = `
    ${keyframes.fadeInUp}
    ${keyframes.slideDown}
    ${keyframes.pulse}
    ${premiumButtonStyles}
    ${premiumCardStyles}
    ${glassEffectStyles}
    ${gradientStyles}
    ${revealAnimationStyles}
    ${hideScrollbarStyles}
    ${shadowStyles}
  `;

/**
 * Usage:
 *
 * 1. For global CSS:
 *    Import and add to your global CSS file:
 *    import { allStyles } from '../styles/styles';
 *
 * 2. For component-specific animations:
 *    import { keyframes } from '../styles/styles';
 *    const animationStyle = { animation: `${keyframes.fadeInUp} 0.5s ease forwards` };
 */
