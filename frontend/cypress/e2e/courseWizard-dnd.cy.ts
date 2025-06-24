// cypress/e2e/courseWizard-dnd.cy.ts
/**
 * Test file for CourseWizard drag-and-drop functionality
 * This focuses on the react-beautiful-dnd implementation in the ModuleStructureStep of the CourseWizard
 */

describe('CourseWizard Drag and Drop Tests', () => {
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
        cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, { fixture: 'reorder-response.json' }).as('reorderModules');

        // Visit the course wizard
        cy.visitCourseWizard(courseSlug);
        cy.wait('@getInstructorCourse');

        // Navigate to the module structure step (step 3)
        cy.get('[data-testid="wizard-nav-step-3"]').click();
        cy.contains('Module Structure').should('be.visible');
    });

    describe('Module Structure Step DnD Tests', () => {
        it('should allow reordering modules via drag and drop', () => {
            // Verify initial module order
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Python Data Types');

            // Perform drag and drop
            cy.reorderRbdModules(0, 1, true);

            // Verify the new order after drag and drop
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');

            // Verify API was called with correct parameters
            cy.get('@reorderModules.all').should('have.length.at.least', 1);
        });

        it('should allow creating a new module and then reordering it', () => {
            // Intercept module creation API
            cy.intercept('POST', '**/instructor/modules/', {
                statusCode: 201,
                body: {
                    id: 99,
                    title: 'New Test Module',
                    description: 'Created during testing',
                    order: 3,
                    lessons: []
                }
            }).as('createModule');

            // Click add module button
            cy.get('[data-testid="create-module-btn"]').click();

            // Fill in module details
            cy.get('[data-testid="module-title-input"]').type('New Test Module');
            cy.get('[data-testid="module-description-input"]').type('Created during testing');
            cy.get('[data-testid="save-module-btn"]').click();

            // Wait for module creation to complete
            cy.wait('@createModule');

            // Verify new module appears at the end
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(2).should('contain', 'New Test Module');

            // Reorder the new module to the top
            cy.reorderRbdModules(2, 0, true);

            // Verify the new order after drag and drop
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'New Test Module');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(2).should('contain', 'Python Data Types');
        });

        it('should update module order values after dragging', () => {
            // Capture the initial order values
            cy.window().then(win => {
                // Store a reference to the wizard context in window
                cy.spy(win.console, 'log').as('consoleLog');
            });

            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1, true);
            cy.wait('@reorderModules');

            // Check that the console logged the reordering with updated order values
            cy.get('@consoleLog').should('be.calledWithMatch', /Synced modules order/);

            // Check API payload sent during reorder
            cy.get('@reorderModules.all').then(interceptions => {
                const latestInterception = interceptions[interceptions.length - 1];
                expect(latestInterception.request.body.modules).to.be.an('array');
                expect(latestInterception.request.body.modules[0].order).to.equal(1);
                expect(latestInterception.request.body.modules[1].order).to.equal(2);
            });
        });
    });

    describe('Context Synchronization', () => {
        it('should update the wizard context state after reordering', () => {
            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1, true);
            cy.wait('@reorderModules');

            // Verify state change by checking a UI element that depends on the context
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');

            // Go to another step and come back to verify state persistence
            cy.get('[data-testid="wizard-nav-step-2"]').click();
            cy.contains('Learning Objectives').should('be.visible');

            cy.get('[data-testid="wizard-nav-step-3"]').click();
            cy.contains('Module Structure').should('be.visible');

            // Verify the module order persisted
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });

        it('should preserve module order when switching between wizard and builder', () => {
            // First reorder modules in the wizard
            cy.reorderRbdModules(0, 1, true);
            cy.wait('@reorderModules');

            // Click switch to builder button
            cy.get('[data-testid="switch-to-builder-btn"]').click();

            // Intercept course builder page load
            cy.intercept('GET', `**/courses/${courseSlug}/builder`, { fixture: 'course.json' }).as('getBuilderCourse');
            cy.wait('@getBuilderCourse');

            // Verify the order is maintained in the builder
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');

            // Go back to wizard
            cy.get('[data-testid="switch-to-wizard-btn"]').click();
            cy.wait('@getInstructorCourse');

            // Navigate to module structure step again
            cy.get('[data-testid="wizard-nav-step-3"]').click();

            // Verify the order is still maintained
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });
    });

    describe('Error Handling', () => {
        it('should display an error message when module reordering fails', () => {
            // Intercept and mock a failed API response
            cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, {
                statusCode: 500,
                body: { error: 'Server error during reordering' }
            }).as('failedReorderModules');

            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1, true);

            // Check for error message
            cy.get('[data-testid="error-message"]').should('be.visible');
            cy.get('[data-testid="error-message"]').should('contain', 'Failed to update module order');

            // Verify UI reverts to original order
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Python Data Types');
        });

        it('should handle and recover from network issues during reordering', () => {
            // First simulate network failure
            cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, {
                forceNetworkError: true
            }).as('networkErrorReorderModules');

            // Perform drag and drop operation
            cy.reorderRbdModules(0, 1, true);

            // Check for error message
            cy.get('[data-testid="error-message"]').should('be.visible');

            // Now allow successful reorder
            cy.intercept('POST', `**/instructor/courses/${courseSlug}/modules/reorder/`, {
                statusCode: 200,
                body: { success: true }
            }).as('successReorderModules');

            // Try reordering again
            cy.reorderRbdModules(0, 1, true);

            // Verify the reordering was successful
            cy.get('[data-testid="success-message"]').should('be.visible');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });
    });
});
