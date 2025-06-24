// cypress/e2e/courseBuilder-dnd.cy.ts
/**
 * Test file for CourseBuilder drag-and-drop functionality
 * This focuses on the react-dnd implementation in the CourseBuilder
 */

describe('CourseBuilder Drag and Drop Tests', () => {
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
        cy.intercept('POST', `**/courses/${courseSlug}/modules/reorder/`, { fixture: 'reorder-response.json' }).as('reorderModules');
        cy.intercept('POST', '**/modules/*/lessons/reorder/', { fixture: 'reorder-response.json' }).as('reorderLessons');

        // Visit the course builder for our test course
        cy.visitCourseBuilder(courseSlug);
        cy.wait('@getCourse');
    });

    describe('Module Drag and Drop', () => {
        it('should allow reordering modules via drag and drop', () => {
            // Verify initial order
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Python Data Types');

            // Perform drag and drop operation
            cy.reorderBuilderModules(0, 1);

            // Verify the new order after drag and drop
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');

            // Verify API was called with correct parameters
            cy.get('@reorderModules.all').should('have.length.at.least', 1);
        });

        it('should update the UI optimistically before API response', () => {
            // Intercept but delay the reorder API call
            cy.intercept('POST', `**/courses/${courseSlug}/modules/reorder/`, (req) => {
                req.reply((res) => {
                    // Delay the response by 1 second
                    setTimeout(() => {
                        res.send({ fixture: 'reorder-response.json' });
                    }, 1000);
                });
            }).as('delayedReorderModules');

            // Get initial order of modules for reference
            cy.getModuleOrder().then(initialOrder => {
                // Perform drag and drop operation
                cy.reorderBuilderModules(0, 1);

                // Immediately after the drag, the UI should already be updated
                cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
                cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');

                // Ensure API was called but still waiting
                cy.get('@delayedReorderModules.all').should('have.length', 1);
            });
        });

        it('should handle multiple reordering operations', () => {
            // First reorder operation
            cy.reorderBuilderModules(0, 1);

            // Wait for the first operation to complete
            cy.wait('@reorderModules');

            // Second reorder operation - move the module back
            cy.reorderBuilderModules(1, 0);

            // Verify both API calls happened
            cy.get('@reorderModules.all').should('have.length', 2);

            // Verify the final order
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Python Data Types');
        });
    });

    describe('Lesson Drag and Drop', () => {
        beforeEach(() => {
            // Expand the first module to access lessons
            cy.get('[data-testid="module-expand-toggle"]').first().click();
        });

        it('should allow reordering lessons within a module', () => {
            // Verify initial order of lessons
            cy.get('[data-testid="lesson-card"]').eq(0).should('contain', 'Installing Python');
            cy.get('[data-testid="lesson-card"]').eq(1).should('contain', 'Python IDLE');

            // Perform drag and drop operation on lessons
            cy.reorderBuilderLessons(0, 0, 1);

            // Verify the new order after drag and drop
            cy.get('[data-testid="lesson-card"]').eq(0).should('contain', 'Python IDLE');
            cy.get('[data-testid="lesson-card"]').eq(1).should('contain', 'Installing Python');

            // Verify API was called with correct parameters
            cy.get('@reorderLessons.all').should('have.length.at.least', 1);
        });

        it('should update the lesson order property after dragging', () => {
            // Get the lessons in the first module
            cy.getLessonOrder('[data-testid="module-card"]:nth-child(1)', '[data-testid="lesson-card"]')
                .then(initialLessonOrder => {
                    // Perform drag and drop operation
                    cy.reorderBuilderLessons(0, 0, 1);

                    // Verify API was called with updated order (check request payload)
                    cy.wait('@reorderLessons').then(interception => {
                        expect(interception.request.body.lessons).to.be.an('array');
                        expect(interception.request.body.lessons[0].order).to.equal(1);
                        expect(interception.request.body.lessons[1].order).to.equal(2);
                    });
                });
        });

        it('should maintain correct state after module collapse and expand', () => {
            // Reorder the lessons
            cy.reorderBuilderLessons(0, 0, 1);
            cy.wait('@reorderLessons');

            // Collapse the module
            cy.get('[data-testid="module-expand-toggle"]').first().click();

            // Then expand it again
            cy.get('[data-testid="module-expand-toggle"]').first().click();

            // Check that the order is maintained
            cy.get('[data-testid="lesson-card"]').eq(0).should('contain', 'Python IDLE');
            cy.get('[data-testid="lesson-card"]').eq(1).should('contain', 'Installing Python');
        });
    });

    describe('Error Handling and Edge Cases', () => {
        it('should handle API errors during module reordering', () => {
            // Intercept and mock a failed API response
            cy.intercept('POST', `**/courses/${courseSlug}/modules/reorder/`, {
                statusCode: 500,
                body: { error: 'Server error during reordering' }
            }).as('failedReorderModules');

            // Try to reorder modules
            cy.reorderBuilderModules(0, 1);

            // Check for error message display
            cy.get('[data-testid="error-message"]').should('be.visible');
            cy.get('[data-testid="error-message"]').should('contain', 'error');
        });

        it('should handle API errors during lesson reordering', () => {
            // Expand the first module
            cy.get('[data-testid="module-expand-toggle"]').first().click();

            // Intercept and mock a failed API response for lesson reordering
            cy.intercept('POST', '**/modules/*/lessons/reorder/', {
                statusCode: 500,
                body: { error: 'Server error during lesson reordering' }
            }).as('failedReorderLessons');

            // Try to reorder lessons
            cy.reorderBuilderLessons(0, 0, 1);

            // Check for error message display
            cy.get('[data-testid="error-message"]').should('be.visible');
            cy.get('[data-testid="error-message"]').should('contain', 'error');
        });

        it('should preserve drag state during auto-save', () => {
            // Intercept auto-save API call
            cy.intercept('PUT', `**/courses/${courseSlug}/`, {
                statusCode: 200,
                body: { success: true }
            }).as('autoSave');

            // Reorder modules
            cy.reorderBuilderModules(0, 1);
            cy.wait('@reorderModules');

            // Trigger auto-save (could be by modifying some field)
            cy.get('[data-testid="course-title-input"]').clear().type('Updated Course Title');

            // Wait for auto-save to complete
            cy.wait('@autoSave');

            // Verify modules remained in the reordered state
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');
        });
    });
});
