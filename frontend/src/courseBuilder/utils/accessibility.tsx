// frontend/src/courseBuilder/utils/accessibility.tsx
import React, { useRef, useEffect } from 'react';

// Screen reader announcements
let announcementElement: HTMLElement | null = null;

/**
 * Announce a message to screen readers
 * @param message Message to be announced
 * @param priority Announcement priority (polite or assertive)
 */
export const announceToScreenReader = (
    message: string,
    priority: 'polite' | 'assertive' = 'polite'
): void => {
    if (!announcementElement) {
        announcementElement = document.createElement('div');
        announcementElement.setAttribute('aria-live', priority);
        announcementElement.setAttribute('aria-atomic', 'true');
        announcementElement.className = 'sr-only';
        // Add position and visibility styles for screen reader only content
        announcementElement.style.position = 'absolute';
        announcementElement.style.left = '-10000px';
        announcementElement.style.width = '1px';
        announcementElement.style.height = '1px';
        announcementElement.style.overflow = 'hidden';
        document.body.appendChild(announcementElement);
    }

    // Set priority as needed
    announcementElement.setAttribute('aria-live', priority);

    // Clear and set content for announcement
    announcementElement.textContent = '';

    // Use setTimeout to ensure announcement is made
    setTimeout(() => {
        if (announcementElement) {
            announcementElement.textContent = message;
        }
    }, 50);
};

/**
 * Hook for managing focus trapping within a container
 * @param active Whether focus trap is active
 * @param containerRef Ref to container element
 */
export const useFocusTrap = (
    active: boolean,
    containerRef: React.RefObject<HTMLElement>
): void => {
    const previousFocus = useRef<HTMLElement | null>(null);

    useEffect(() => {
        if (!active || !containerRef.current) return;

        // Store currently focused element
        previousFocus.current = document.activeElement as HTMLElement;

        // Get all focusable elements in container (improved selector)
        const focusableElements = containerRef.current.querySelectorAll(
            'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]):not([disabled]), [contenteditable="true"]'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        // Set initial focus
        if (firstElement) {
            firstElement.focus();
        }

        // Handle tab key navigation
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key !== 'Tab') return;

            // Check if we're still within the container
            if (!containerRef.current?.contains(document.activeElement as Node)) {
                event.preventDefault();
                firstElement.focus();
                return;
            }

            if (event.shiftKey) {
                // Shift + Tab: go to previous element
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab: go to next element
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement.focus();
                }
            }
        };

        // Add event listener
        document.addEventListener('keydown', handleKeyDown);

        // Cleanup
        return () => {
            document.removeEventListener('keydown', handleKeyDown);

            // Restore focus when trap is deactivated
            if (previousFocus.current && document.body.contains(previousFocus.current)) {
                previousFocus.current.focus();
            }
        };
    }, [active, containerRef]);
};

/**
 * Create properly labeled drag and drop elements
 * @param type Type of draggable element
 * @param index Position index
 * @param totalItems Total number of items in the list (optional)
 * @returns ARIA attributes for drag elements
 */
export const getDragAttributes = (
    type: string,
    index: number,
    totalItems?: number
): Record<string, string | number | boolean> => {
    return {
        role: 'listitem',
        'aria-roledescription': `draggable ${type}`,
        'aria-describedby': 'drag-instructions',
        'aria-setsize': totalItems ?? -1,
        'aria-posinset': index + 1,
        draggable: true,
        tabIndex: 0, // Make draggable items focusable
    };
};

/**
 * Create drag instruction element for screen readers
 * @returns React element with instructions
 */
export const DragInstructions = (): JSX.Element => (
    <div id= "drag-instructions" className = "sr-only" >
        Press space bar or enter to start dragging.
    Use arrow keys to navigate.
    Press space bar or enter again to drop.
    Press escape to cancel drag operation.
</div>
);

/**
 * Cleanup function to remove announcement element (useful for testing or cleanup)
 */
export const cleanupAnnouncements = (): void => {
    if (announcementElement && document.body.contains(announcementElement)) {
        document.body.removeChild(announcementElement);
        announcementElement = null;
    }
};
