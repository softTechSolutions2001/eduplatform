/**
 * File: frontend/src/utils/unsavedChangesTracker.js
 * Version: 1.0.0
 * Date: 2025-06-01
 *
 * Utility for tracking unsaved changes in course editors
 * This shared utility helps maintain consistency between
 * the wizard and builder approaches
 */

/**
 * Set the unsaved changes status in the DOM
 * @param {boolean} hasUnsavedChanges - Whether there are unsaved changes
 */
export const setUnsavedChanges = hasUnsavedChanges => {
  if (hasUnsavedChanges) {
    document.body.classList.add('has-unsaved-changes');
  } else {
    document.body.classList.remove('has-unsaved-changes');
  }
};

/**
 * Check if there are unsaved changes
 * @returns {boolean} - Whether there are unsaved changes
 */
export const hasUnsavedChanges = () => {
  return document.body.classList.contains('has-unsaved-changes');
};

/**
 * Setup beforeunload event handler for the window
 * @param {Function} checkDirty - Function that returns whether there are unsaved changes
 */
export const setupUnsavedChangesWarning = (checkDirty = hasUnsavedChanges) => {
  const handleBeforeUnload = e => {
    if (checkDirty()) {
      // Standard text (browsers will display their own message)
      const message =
        'You have unsaved changes. Are you sure you want to leave?';
      e.returnValue = message;
      return message;
    }
  };

  window.addEventListener('beforeunload', handleBeforeUnload);

  // Return cleanup function
  return () => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
  };
};
