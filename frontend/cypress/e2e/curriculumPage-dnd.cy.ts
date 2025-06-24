// cypress/e2e/curriculumPage-dnd.cy.ts
/**
 * Test file for CurriculumPage drag-and-drop functionality
 * This focuses on the react-beautiful-dnd implementation in the CurriculumPage
 */

describe('CurriculumPage Drag and Drop Tests', () => {
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
        cy.intercept('GET', '**/instructor/modules/*', { fixture: 'modules.json' }).as('getModules');
        cy.intercept('GET', '**/instructor/modules/*/lessons/', { fixture: 'lessons.json' }).as('getLessons');
        cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, { fixture: 'reorder-response.json' }).as('reorderModules');
        cy.intercept('POST', '**/instructor/modules/*/lessons/reorder/', { fixture: 'reorder-response.json' }).as('reorderLessons');

        // Visit the curriculum page
        cy.visitCourseCurriculum(courseSlug);
        cy.wait('@getInstructorCourse');
    });

    describe('Module Reordering', () => {
        it('should allow reordering modules via drag and drop', () => {
            // Verify initial module order
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Python Data Types');

            // Perform drag and drop
            cy.reorderRbdModules(0, 1);

            // Verify the new order after drag and drop
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');

            // Verify API was called with correct parameters
            cy.get('@reorderModules.all').should('have.length.at.least', 1);
        });

        it('should show loading state during module reordering', () => {
            // Intercept but delay the reorder API call
            cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, (req) => {
                req.reply((res) => {
                    // Delay the response by 1 second
                    setTimeout(() => {
                        res.send({ fixture: 'reorder-response.json' });
                    }, 1000);
                });
            }).as('delayedReorderModules');

            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1);

            // Check loading indicator is shown during API call
            cy.get('[data-testid="loading-indicator"]').should('be.visible');

            // Wait for the API call to complete
            cy.wait('@delayedReorderModules');

            // Check loading indicator is hidden after API call
            cy.get('[data-testid="loading-indicator"]').should('not.exist');
        });

        it('should display success message after successful reordering', () => {
            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1);

            // Wait for the API call to complete
            cy.wait('@reorderModules');

            // Check success message appears
            cy.get('[data-testid="success-message"]').should('be.visible');
            cy.get('[data-testid="success-message"]').should('contain', 'Module order updated successfully');

            // Check message disappears after a timeout
            cy.get('[data-testid="success-message"]').should('not.exist', { timeout: 5000 });
        });
    });

    describe('Lesson Reordering', () => {
        beforeEach(() => {
            // Expand the first module to access lessons
            cy.get('[aria-expanded="false"]').first().click();
            cy.wait('@getLessons');
        });

        it('should allow reordering lessons within a module', () => {
            // Get module ID from first module
            cy.get('[data-rbd-draggable-id]').first().invoke('attr', 'data-rbd-draggable-id').then(moduleId => {
                // Verify initial lesson order
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Installing Python');
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Python IDLE');

                // Perform drag and drop
                cy.reorderRbdLessons(moduleId, 0, 1);

                // Verify the new order after drag and drop
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Python IDLE');
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Installing Python');

                // Verify API was called with correct parameters
                cy.get('@reorderLessons.all').should('have.length.at.least', 1);
            });
        });

        it('should handle lesson reordering in different modules independently', () => {
            // Expand all modules
            cy.get('[aria-expanded="false"]').click({ multiple: true });
            cy.wait('@getLessons');

            // Get module IDs
            cy.get('[data-rbd-draggable-id]').then($modules => {
                const moduleId1 = $modules.eq(0).attr('data-rbd-draggable-id');
                const moduleId2 = $modules.eq(1).attr('data-rbd-draggable-id');

                // Reorder lessons in first module
                cy.reorderRbdLessons(moduleId1, 0, 1);
                cy.wait('@reorderLessons');

                // Verify first module's lessons are reordered
                cy.get(`[data-rbd-droppable-id="${moduleId1}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Python IDLE');
                cy.get(`[data-rbd-droppable-id="${moduleId1}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Installing Python');

                // Verify second module's lessons are unchanged
                cy.get(`[data-rbd-droppable-id="${moduleId2}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Numbers and Strings');
                cy.get(`[data-rbd-droppable-id="${moduleId2}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Lists and Tuples');
            });
        });
    });

    describe('Error Handling', () => {
        it('should handle API errors during module reordering', () => {
            // Intercept and mock a failed API response
            cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, {
                statusCode: 500,
                body: { error: 'Server error during reordering' }
            }).as('failedReorderModules');

            // Try to reorder modules
            cy.reorderRbdModules(0, 1);

            // Check for error message display
            cy.get('[data-testid="error-message"]').should('be.visible');
            cy.get('[data-testid="error-message"]').should('contain', 'Failed to update module order');

            // Verify modules revert to original order (could check by comparing DOM)
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Python Data Types');
        });

        it('should handle API errors during lesson reordering', () => {
            // Expand the first module
            cy.get('[aria-expanded="false"]').first().click();

            // Get module ID from first module
            cy.get('[data-rbd-draggable-id]').first().invoke('attr', 'data-rbd-draggable-id').then(moduleId => {
                // Intercept and mock a failed API response
                cy.intercept('POST', '**/instructor/modules/*/lessons/reorder/', {
                    statusCode: 500,
                    body: { error: 'Server error during reordering' }
                }).as('failedReorderLessons');

                // Try to reorder lessons
                cy.reorderRbdLessons(moduleId, 0, 1);

                // Check for error message display
                cy.get('[data-testid="error-message"]').should('be.visible');
                cy.get('[data-testid="error-message"]').should('contain', 'Failed to update lesson order');

                // Verify lessons revert to original order
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Installing Python');
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Python IDLE');
            });
        });
    });

    describe('UI Interaction Tests', () => {
        it('should maintain DnD functionality after page resize', () => {
            // Change viewport size to mobile
            cy.viewport('iphone-x');

            // Verify modules are still draggable
            cy.reorderRbdModules(0, 1);

            // Check reordering worked
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');

            // Change back to desktop size
            cy.viewport(1280, 720);

            // Verify DnD still works
            cy.reorderRbdModules(0, 1);

            // Check reordering worked again
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Python Data Types');
        });

        it('should maintain correct state after page refresh', () => {
            // Reorder modules
            cy.reorderRbdModules(0, 1);
            cy.wait('@reorderModules');

            // Refresh the page
            cy.reload();
            cy.wait('@getInstructorCourse');

            // Verify the order is maintained after refresh
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });
    });
});
