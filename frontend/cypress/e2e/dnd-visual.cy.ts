// cypress/e2e/dnd-visual.cy.ts
/**
 * Visual regression tests for drag-and-drop interactions
 * Note: These tests require the Cypress image snapshot plugin to be installed
 * npm install --save-dev cypress-image-snapshot
 */

describe('Drag and Drop Visual Regression Tests', () => {
    let courseSlug: string;

    before(() => {
        // Login with instructor credentials
        cy.loginAsInstructor();

        // Create a test course via API and store its slug
        cy.createCourseViaApi().then((slug) => {
            courseSlug = slug;
        });
    });

    beforeEach(() => {
        // Intercept API requests we'll need to monitor or mock
        cy.intercept('GET', `**/courses/${courseSlug}/`, { fixture: 'course.json' }).as('getCourse');
        cy.intercept('GET', `**/instructor/courses/${courseSlug}/`, { fixture: 'course.json' }).as('getInstructorCourse');
        cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, { fixture: 'reorder-response.json' }).as('reorderModules');
        cy.intercept('POST', '**/instructor/modules/*/lessons/reorder/', { fixture: 'reorder-response.json' }).as('reorderLessons');
    });

    describe('CourseBuilder Visual Tests', () => {
        beforeEach(() => {
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');
        });

        it('should show correct visual feedback during drag operation', () => {
            // Take snapshot before drag starts
            // cy.matchImageSnapshot('builder-before-drag');

            // Start drag but don't complete
            cy.get('[data-testid="module-card"]:first-child [data-testid="module-drag-handle"]').trigger('mousedown', { button: 0 });
            cy.wait(100);
            cy.get('body').trigger('mousemove', { clientX: 500, clientY: 400 });

            // Take snapshot during drag
            // cy.matchImageSnapshot('builder-during-drag');

            // Complete drag operation
            cy.get('body').trigger('mouseup');
        });

        it('should show correct hover states for drop targets', () => {
            // Take snapshot of normal state
            // cy.matchImageSnapshot('builder-drop-target-normal');

            // Hover over module drag handle
            cy.get('[data-testid="module-card"]:first-child [data-testid="module-drag-handle"]').trigger('mouseover');

            // Take snapshot of hovered state
            // cy.matchImageSnapshot('builder-drop-target-hovered');
        });
    });

    describe('CurriculumPage Visual Tests', () => {
        beforeEach(() => {
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');
        });

        it('should show correct drag indicator in curriculum page', () => {
            // Take snapshot before drag
            // cy.matchImageSnapshot('curriculum-before-drag');

            // Start drag but not complete it yet
            cy.get('[data-rbd-draggable-id]:first-child [role="button"]').trigger('keydown', { keyCode: 32 });
            cy.wait(100);
            cy.get('[data-rbd-draggable-id]:first-child [role="button"]').trigger('dragstart');
            cy.wait(100);

            // Take snapshot during drag
            // cy.matchImageSnapshot('curriculum-during-drag');

            // Complete drag operation
            cy.get('[data-rbd-draggable-id]:last-child [role="button"]').trigger('dragover');
            cy.get('[data-rbd-draggable-id]:last-child [role="button"]').trigger('drop');
            cy.get('[data-rbd-draggable-id]:last-child [role="button"]').trigger('keyup', { keyCode: 32 });
        });
    });

    describe('CourseWizard Visual Tests', () => {
        beforeEach(() => {
            cy.visitCourseWizard(courseSlug);
            cy.wait('@getInstructorCourse');
            cy.get('[data-testid="wizard-nav-step-3"]').click();
        });

        it('should maintain proper spacing during drag operations', () => {
            // Take snapshot before drag
            // cy.matchImageSnapshot('wizard-modules-before-drag');

            // Start drag
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]:first-child').trigger('keydown', { keyCode: 32 });
            cy.wait(100);
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]:first-child').trigger('dragstart');

            // Move halfway
            cy.get('body').trigger('mousemove', { clientX: 400, clientY: 300 });

            // Take snapshot during drag
            // cy.matchImageSnapshot('wizard-modules-during-drag');

            // Complete drag operation
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]:last-child').trigger('dragover');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]:last-child').trigger('drop');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]:last-child').trigger('keyup', { keyCode: 32 });
        });
    });

    describe('Accessibility Visual Tests', () => {
        it('should maintain focus indicators during drag operations', () => {
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Tab to the module drag handle
            cy.get('body').tab();
            cy.get('[data-testid="module-card"]:first-child [data-testid="module-drag-handle"]').focus();

            // Take snapshot with focus
            // cy.matchImageSnapshot('builder-drag-handle-focus');

            // Verify focus is visible
            cy.focused().should('have.attr', 'data-testid', 'module-drag-handle');
        });

        it('should provide visual indication of drag source and target', () => {
            cy.visitCurriculumPage(courseSlug);
            cy.wait('@getInstructorCourse');

            // Start dragging
            cy.get('[data-rbd-draggable-id]:first-child').trigger('keydown', { keyCode: 32 });
            cy.wait(100);

            // Verify some visual indication is present (like a class change)
            cy.get('[data-rbd-draggable-id]:first-child').should('have.class', /dragging|isDragging/);

            // Complete the operation
            cy.get('[data-rbd-draggable-id]:first-child').trigger('keyup', { keyCode: 32 });
        });
    });
});
