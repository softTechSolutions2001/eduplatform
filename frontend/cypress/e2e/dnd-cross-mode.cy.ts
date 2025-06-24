// cypress/e2e/dnd-cross-mode.cy.ts
/**
 * Cross-mode compatibility testing for the drag-and-drop functionality
 * This test suite validates that changes made in one mode (CourseBuilder, CourseWizard, CurriculumPage)
 * are correctly reflected in the other modes
 */

describe('Cross-Mode Drag and Drop Compatibility Tests', () => {
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
    });

    describe('CourseBuilder to CurriculumPage Sync', () => {
        it('should reflect module reordering from CourseBuilder in CurriculumPage', () => {
            // First visit the course builder and reorder modules
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Perform drag and drop in CourseBuilder
            cy.reorderBuilderModules(0, 1);
            cy.wait('@reorderModules');

            // Verify the reordering worked in CourseBuilder
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');

            // Now visit the curriculum page
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');

            // Verify the same order is reflected in CurriculumPage
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });

        it('should reflect lesson reordering from CourseBuilder in CurriculumPage', () => {
            // First visit the course builder and reorder lessons
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Expand the first module
            cy.get('[data-testid="module-expand-toggle"]').first().click();

            // Perform drag and drop of lessons in CourseBuilder
            cy.reorderBuilderLessons(0, 0, 1);
            cy.wait('@reorderLessons');

            // Verify the reordering worked in CourseBuilder
            cy.get('[data-testid="lesson-card"]').eq(0).should('contain', 'Python IDLE');
            cy.get('[data-testid="lesson-card"]').eq(1).should('contain', 'Installing Python');

            // Now visit the curriculum page
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');

            // Expand the first module
            cy.get('[aria-expanded="false"]').first().click();
            cy.wait('@getLessons');

            // Get module ID and verify lessons have the same order
            cy.get('[data-rbd-draggable-id]').first().invoke('attr', 'data-rbd-draggable-id').then(moduleId => {
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(0).should('contain', 'Python IDLE');
                cy.get(`[data-rbd-droppable-id="${moduleId}"] [data-rbd-draggable-id]`).eq(1).should('contain', 'Installing Python');
            });
        });
    });

    describe('CurriculumPage to CourseWizard Sync', () => {
        it('should reflect module reordering from CurriculumPage in CourseWizard', () => {
            // First visit the curriculum page and reorder modules
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');

            // Perform drag and drop in CurriculumPage
            cy.reorderRbdModules(0, 1);
            cy.wait('@reorderModules');

            // Now visit the course wizard
            cy.visitCourseWizard(courseSlug);
            cy.wait('@getInstructorCourse');

            // Navigate to the module structure step
            cy.get('[data-testid="wizard-nav-step-3"]').click();
            cy.contains('Module Structure').should('be.visible');

            // Verify the modules have the same order in CourseWizard
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(1).should('contain', 'Getting Started with Python');
        });
    });

    describe('CourseWizard to CourseBuilder Sync', () => {
        it('should reflect module reordering from CourseWizard in CourseBuilder', () => {
            // First visit the course wizard and reorder modules
            cy.visitCourseWizard(courseSlug);
            cy.wait('@getInstructorCourse');

            // Navigate to the module structure step
            cy.get('[data-testid="wizard-nav-step-3"]').click();
            cy.contains('Module Structure').should('be.visible');

            // Perform drag and drop in CourseWizard
            cy.reorderRbdModules(0, 1, true);
            cy.wait('@reorderModules');

            // Now visit the course builder
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Verify the modules have the same order in CourseBuilder
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');
        });
    });

    describe('Full Round-Trip Testing', () => {
        it('should maintain consistent module ordering across all three interfaces', () => {
            // Start with a known state in CourseBuilder
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Verify initial order
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Getting Started with Python');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Python Data Types');

            // Reorder in CourseBuilder
            cy.reorderBuilderModules(0, 1);
            cy.wait('@reorderModules');

            // Verify in CurriculumPage
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');
            cy.get('[data-rbd-draggable-id]').eq(0).should('contain', 'Python Data Types');

            // Reorder back in CurriculumPage
            cy.reorderRbdModules(0, 1);
            cy.wait('@reorderModules');

            // Verify in CourseWizard
            cy.visitCourseWizard(courseSlug);
            cy.wait('@getInstructorCourse');
            cy.get('[data-testid="wizard-nav-step-3"]').click();
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').eq(0).should('contain', 'Getting Started with Python');

            // Final reorder in CourseWizard
            cy.reorderRbdModules(0, 1, true);
            cy.wait('@reorderModules');

            // Verify back in CourseBuilder
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');
            cy.get('[data-testid="module-card"]').eq(0).should('contain', 'Python Data Types');
            cy.get('[data-testid="module-card"]').eq(1).should('contain', 'Getting Started with Python');
        });
    });

    describe('Data Integrity Tests', () => {
        it('should maintain proper course data structure when switching between modes', () => {
            // Start in CourseBuilder
            cy.visitCourseBuilder(courseSlug);
            cy.wait('@getCourse');

            // Add a new module
            cy.get('[data-testid="add-module-btn"]').click();
            cy.get('[data-testid="module-card"]').should('have.length', 3);

            // Add a lesson to the new module
            cy.get('[data-testid="module-card"]:last-child [data-testid="module-expand-toggle"]').click();
            cy.get('[data-testid="module-card"]:last-child [data-testid="add-lesson-btn"]').click();

            // Switch to CurriculumPage
            cy.visitCourseCurriculum(courseSlug);
            cy.wait('@getInstructorCourse');

            // Verify the new module and lesson appear in curriculum page
            cy.get('[data-rbd-draggable-id]').should('have.length', 3);

            // Switch to CourseWizard
            cy.visitCourseWizard(courseSlug);
            cy.wait('@getInstructorCourse');
            cy.get('[data-testid="wizard-nav-step-3"]').click();

            // Verify the data appears in the wizard
            cy.get('[data-testid="module-structure-step"] [data-rbd-draggable-id]').should('have.length', 3);
        });
    });
});
