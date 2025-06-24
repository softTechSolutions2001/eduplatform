/**
 * File: frontend/src/scripts/dropdown.js
 * Version: 1.0.0
 * Date: 2025-06-01
 *
 * Dropdown menu JavaScript functionality
 * This script enhances the CSS-only dropdowns with JavaScript functionality
 * for better accessibility and mobile support
 */

/**
 * Initialize dropdown menus with JavaScript interactions
 */
export const initDropdowns = () => {
  const dropdowns = document.querySelectorAll('.dropdown');

  dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('button');
    const menu = dropdown.querySelector('.dropdown-menu');

    if (!button || !menu) return;

    // Toggle dropdown on button click
    button.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();

      // Close all other open dropdowns
      document.querySelectorAll('.dropdown-menu').forEach(otherMenu => {
        if (otherMenu !== menu && otherMenu.classList.contains('block')) {
          otherMenu.classList.remove('block');
          otherMenu.classList.add('hidden');
        }
      });

      // Toggle this dropdown
      menu.classList.toggle('hidden');
      menu.classList.toggle('block');

      // Update aria attributes
      const isExpanded = menu.classList.contains('block');
      button.setAttribute('aria-expanded', isExpanded);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', e => {
      if (!dropdown.contains(e.target) && menu.classList.contains('block')) {
        menu.classList.remove('block');
        menu.classList.add('hidden');
        button.setAttribute('aria-expanded', 'false');
      }
    });

    // Set initial state and accessibility attributes
    menu.classList.add('hidden');
    button.setAttribute('aria-haspopup', 'true');
    button.setAttribute('aria-expanded', 'false');
  });
};

/**
 * Clean up dropdown event listeners when needed
 */
export const cleanupDropdowns = () => {
  // Implementation depends on how event listeners were attached
  // For now, this is a placeholder for future implementation
  console.log('Dropdown event listeners cleanup would happen here');
};
