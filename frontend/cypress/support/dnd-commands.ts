// dnd-commands.ts - Specialized commands for testing drag and drop functionality

/**
 * REACT-DND SPECIFIC COMMANDS
 * For use with courseBuilder implementation using react-dnd (HTML5Backend)
 */

/**
 * Simulates drag and drop for react-dnd components in the Course Builder
 * @param sourceSelector - The CSS selector for the source element to drag
 * @param targetSelector - The CSS selector for the target element to drop onto
 * @param options - Optional configuration for the drag and drop operation
 */
Cypress.Commands.add('reactDndDrag', (sourceSelector, targetSelector, options = {}) => {
    const { position = 'center', force = true } = options;

    // Get the source and target elements
    cy.get(sourceSelector).should('exist').as('source');
    cy.get(targetSelector).should('exist').as('target');

    // Perform the drag and drop
    cy.get('@source')
        .trigger('mousedown', { button: 0, force })
        .then(($source) => {
            const sourceRect = $source[0].getBoundingClientRect();
            cy.get('@target').then(($target) => {
                const targetRect = $target[0].getBoundingClientRect();

                // Calculate position based on option
                let offsetX, offsetY;
                switch (position) {
                    case 'top':
                        offsetX = targetRect.width / 2;
                        offsetY = 5;
                        break;
                    case 'bottom':
                        offsetX = targetRect.width / 2;
                        offsetY = targetRect.height - 5;
                        break;
                    case 'left':
                        offsetX = 5;
                        offsetY = targetRect.height / 2;
                        break;
                    case 'right':
                        offsetX = targetRect.width - 5;
                        offsetY = targetRect.height / 2;
                        break;
                    default: // center
                        offsetX = targetRect.width / 2;
                        offsetY = targetRect.height / 2;
                }

                cy.document().trigger('mousemove', {
                    clientX: targetRect.left + offsetX,
                    clientY: targetRect.top + offsetY,
                    force
                });
            });
        })
        .trigger('mouseup', { force })
        .wait(500); // Wait for any animations or state updates to complete
});

/**
 * Command to reorder modules in CourseBuilder (using react-dnd)
 * @param sourceIndex - The index of the module to drag
 * @param targetIndex - The target destination index
 */
Cypress.Commands.add('reorderBuilderModules', (sourceIndex, targetIndex) => {
    cy.intercept('POST', '**/modules/reorder/').as('reorderModules');

    // Get all module cards
    cy.get('[data-testid="module-card"]').then($modules => {
        if (sourceIndex >= $modules.length || targetIndex >= $modules.length) {
            throw new Error(`Invalid module indices: ${sourceIndex}, ${targetIndex}. Total modules: ${$modules.length}`);
        }

        cy.reactDndDrag(
            `[data-testid="module-card"]:nth-child(${sourceIndex + 1}) [data-testid="module-drag-handle"]`,
            `[data-testid="module-card"]:nth-child(${targetIndex + 1})`
        );

        cy.waitForApi('@reorderModules');
    });
});

/**
 * Command to reorder lessons within a module in CourseBuilder (using react-dnd)
 * @param moduleIndex - The index of the module containing the lessons
 * @param sourceIndex - The index of the lesson to drag
 * @param targetIndex - The target destination index
 */
Cypress.Commands.add('reorderBuilderLessons', (moduleIndex, sourceIndex, targetIndex) => {
    cy.intercept('POST', '**/lessons/reorder/').as('reorderLessons');

    // Ensure the module is expanded
    cy.get(`[data-testid="module-card"]:nth-child(${moduleIndex + 1}) [data-testid="module-expand-toggle"]`)
        .then($toggle => {
            if (!$toggle.hasClass('expanded')) {
                cy.wrap($toggle).click();
            }
        });

    // Wait for lessons to be visible
    cy.get(`[data-testid="module-card"]:nth-child(${moduleIndex + 1}) [data-testid="lesson-card"]`)
        .should('be.visible')
        .then($lessons => {
            if (sourceIndex >= $lessons.length || targetIndex >= $lessons.length) {
                throw new Error(`Invalid lesson indices: ${sourceIndex}, ${targetIndex}. Total lessons: ${$lessons.length}`);
            }

            cy.reactDndDrag(
                `[data-testid="module-card"]:nth-child(${moduleIndex + 1}) [data-testid="lesson-card"]:nth-child(${sourceIndex + 1}) [data-testid="lesson-drag-handle"]`,
                `[data-testid="module-card"]:nth-child(${moduleIndex + 1}) [data-testid="lesson-card"]:nth-child(${targetIndex + 1})`
            );

            cy.waitForApi('@reorderLessons');
        });
});

/**
 * REACT-BEAUTIFUL-DND SPECIFIC COMMANDS
 * For use with CurriculumPage and CourseWizard implementations using react-beautiful-dnd
 */

/**
 * Simulates drag and drop for react-beautiful-dnd components
 * This implementation handles the specific drag and drop protocol used by react-beautiful-dnd
 */
Cypress.Commands.add('rbdDragAndDrop', (sourceSelector, targetSelector, options = {}) => {
    const { position = 'center', force = true } = options;

    // Helper function for drag simulation
    const simulateDragAndDrop = ($source, $target) => {
        // Get the center coordinates of source and target
        const sourceRect = $source[0].getBoundingClientRect();
        const targetRect = $target[0].getBoundingClientRect();

        // Calculate position based on option
        let targetX, targetY;
        switch (position) {
            case 'top':
                targetX = targetRect.left + targetRect.width / 2;
                targetY = targetRect.top + 5;
                break;
            case 'bottom':
                targetX = targetRect.left + targetRect.width / 2;
                targetY = targetRect.bottom - 5;
                break;
            case 'left':
                targetX = targetRect.left + 5;
                targetY = targetRect.top + targetRect.height / 2;
                break;
            case 'right':
                targetX = targetRect.right - 5;
                targetY = targetRect.top + targetRect.height / 2;
                break;
            default: // center
                targetX = targetRect.left + targetRect.width / 2;
                targetY = targetRect.top + targetRect.height / 2;
        }

        const sourceX = sourceRect.left + sourceRect.width / 2;
        const sourceY = sourceRect.top + sourceRect.height / 2;

        // Required sequence of events for react-beautiful-dnd:
        // 1. Start with keydown to initiate drag
        cy.wrap($source)
            .trigger('keydown', { keyCode: 32, which: 32, force }) // Space key
            .wait(100)
            .trigger('dragstart', { force })
            .wait(100);

        // 2. Multiple mousemove events for the drag operation
        cy.wrap($source)
            .trigger('mousemove', {
                clientX: sourceX,
                clientY: sourceY,
                force
            })
            .wait(100);

        // Move halfway
        cy.wrap($source)
            .trigger('mousemove', {
                clientX: (sourceX + targetX) / 2,
                clientY: (sourceY + targetY) / 2,
                force
            })
            .wait(100);

        // Move to target
        cy.wrap($target)
            .trigger('mousemove', {
                clientX: targetX,
                clientY: targetY,
                force
            })
            .wait(100);

        // 3. End drag with mouseup and keyup
        cy.wrap($target)
            .trigger('mouseup', {
                clientX: targetX,
                clientY: targetY,
                force
            })
            .wait(100)
            .trigger('keyup', { keyCode: 32, which: 32, force });
    };

    // Get source and target elements
    cy.get(sourceSelector).should('exist').then($source => {
        cy.get(targetSelector).should('exist').then($target => {
            simulateDragAndDrop($source, $target);
        });
    });

    // Allow time for the operation to complete and state to update
    cy.wait(500);
});

/**
 * Command to reorder modules in CurriculumPage or CourseWizard (using react-beautiful-dnd)
 * @param sourceIndex - The index of the module to drag
 * @param targetIndex - The target destination index
 * @param inWizard - Whether the operation is in the course wizard (defaults to false)
 */
Cypress.Commands.add('reorderRbdModules', (sourceIndex, targetIndex, inWizard = false) => {
    cy.intercept('POST', '**/modules/reorder/').as('reorderModules');

    const containerSelector = inWizard
        ? '[data-testid="module-structure-step"] [data-rbd-droppable-id="modules"]'
        : '[data-rbd-droppable-id="modules"]';

    cy.get(`${containerSelector} [data-rbd-draggable-id]`).then($modules => {
        if (sourceIndex >= $modules.length || targetIndex >= $modules.length) {
            throw new Error(`Invalid module indices: ${sourceIndex}, ${targetIndex}. Total modules: ${$modules.length}`);
        }

        cy.rbdDragAndDrop(
            `${containerSelector} [data-rbd-draggable-id]:nth-child(${sourceIndex + 1}) [role="button"]`,
            `${containerSelector} [data-rbd-draggable-id]:nth-child(${targetIndex + 1})`
        );

        cy.waitForApi('@reorderModules');
    });
});

/**
 * Command to reorder lessons within a module in CurriculumPage (using react-beautiful-dnd)
 * @param moduleId - The ID of the module containing the lessons
 * @param sourceIndex - The index of the lesson to drag
 * @param targetIndex - The target destination index
 */
Cypress.Commands.add('reorderRbdLessons', (moduleId, sourceIndex, targetIndex) => {
    cy.intercept('POST', '**/lessons/reorder/').as('reorderLessons');

    // Ensure the module is expanded
    cy.get(`[data-rbd-draggable-id="${moduleId}"] [aria-expanded]`).then($disclosure => {
        if ($disclosure.attr('aria-expanded') === 'false') {
            cy.wrap($disclosure).click();
        }
    });

    const containerSelector = `[data-rbd-droppable-id="${moduleId}"]`;

    // Wait for lessons to be visible
    cy.get(`${containerSelector} [data-rbd-draggable-id]`).should('be.visible').then($lessons => {
        if (sourceIndex >= $lessons.length || targetIndex >= $lessons.length) {
            throw new Error(`Invalid lesson indices: ${sourceIndex}, ${targetIndex}. Total lessons: ${$lessons.length}`);
        }

        cy.rbdDragAndDrop(
            `${containerSelector} [data-rbd-draggable-id]:nth-child(${sourceIndex + 1})`,
            `${containerSelector} [data-rbd-draggable-id]:nth-child(${targetIndex + 1})`
        );

        cy.waitForApi('@reorderLessons');
    });
});

// COMMON UTILITY FUNCTIONS

/**
 * Get the current modules order in the DOM
 * Returns an array of module IDs in their current visual order
 */
Cypress.Commands.add('getModuleOrder', (selector = '[data-testid="module-card"]') => {
    return cy.get(selector).then($modules => {
        const ids = [];
        $modules.each((index, el) => {
            ids.push(el.getAttribute('data-module-id'));
        });
        return ids;
    });
});

/**
 * Get the current lessons order in a module
 * Returns an array of lesson IDs in their current visual order
 */
Cypress.Commands.add('getLessonOrder', (moduleSelector, lessonSelector) => {
    return cy.get(`${moduleSelector} ${lessonSelector}`).then($lessons => {
        const ids = [];
        $lessons.each((index, el) => {
            ids.push(el.getAttribute('data-lesson-id'));
        });
        return ids;
    });
});

export { };

// Augment the Cypress namespace to include custom commands
declare global {
    namespace Cypress {
        interface Chainable<Subject = any> {
            reactDndDrag(sourceSelector: string, targetSelector: string, options?: object): void;
            reorderBuilderModules(sourceIndex: number, targetIndex: number): void;
            reorderBuilderLessons(moduleIndex: number, sourceIndex: number, targetIndex: number): void;
            rbdDragAndDrop(sourceSelector: string, targetSelector: string, options?: object): void;
            reorderRbdModules(sourceIndex: number, targetIndex: number, inWizard?: boolean): void;
            reorderRbdLessons(moduleId: string, sourceIndex: number, targetIndex: number): void;
            getModuleOrder(selector?: string): Chainable<string[]>;
            getLessonOrder(moduleSelector: string, lessonSelector: string): Chainable<string[]>;
        }
    }
}
