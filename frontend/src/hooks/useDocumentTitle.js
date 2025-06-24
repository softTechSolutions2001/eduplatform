/**
 * File: src/hooks/useDocumentTitle.js
 * Version: 1.0.0
 * Date: 2025-05-13 18:04:20
 * Author: cadsanthanam
 *
 * Hook for managing document title
 */

import { useEffect } from 'react';

/**
 * Custom hook to update document title with proper cleanup
 *
 * @param {string} title - The title to set for the document
 * @param {string} [suffix] - Optional suffix to append after title
 */
export const useDocumentTitle = (title, suffix = '') => {
  useEffect(() => {
    // Store the original title to restore on unmount
    const originalTitle = document.title;

    // Set the new title
    document.title = suffix ? `${title} ${suffix}` : title;

    // Restore original title on component unmount
    return () => {
      document.title = originalTitle;
    };
  }, [title, suffix]);
};

export default useDocumentTitle;
