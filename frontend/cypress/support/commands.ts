// commands.ts - Common Cypress commands for EduPlatform testing

/**
 * Custom command to login as an instructor
 * Uses environment variables for credentials or falls back to defaults
 */
Cypress.Commands.add('loginAsInstructor', (email = Cypress.env('INSTRUCTOR_EMAIL') || 'mohithasanthanam@gmail.com', password = Cypress.env('INSTRUCTOR_PASSWORD') || 'Vajjiram@79') => {
    cy.session([email, password], () => {
        cy.visit('/login');
        cy.get('[data-testid="email-input"]').type(email);
        cy.get('[data-testid="password-input"]').type(password);
        cy.get('[data-testid="login-button"]').click();
        cy.url().should('include', '/instructor/dashboard');
    });
});

/**
 * Custom command to create a new course via API
 * Returns the course slug for further operations
 */
Cypress.Commands.add('createCourseViaApi', (courseData = {}) => {
    const defaultCourseData = {
        title: `Cypress Test Course ${Date.now()}`,
        description: 'Test course created by Cypress',
        category_id: 1,
        difficulty_level: 'beginner',
        is_published: false
    };

    const mergedData = { ...defaultCourseData, ...courseData };

    return cy.request({
        method: 'POST',
        url: '/api/instructor/courses/',
        body: mergedData,
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
    }).then((response) => {
        expect(response.status).to.eq(201);
        return response.body.slug;
    });
});

/**
 * Visit the course builder for a specific course
 */
Cypress.Commands.add('visitCourseBuilder', (courseSlug) => {
    cy.visit(`/instructor/courses/${courseSlug}/builder`);
    cy.get('[data-testid="course-builder"]', { timeout: 10000 }).should('exist');
});

/**
 * Visit the course wizard for a specific course
 */
Cypress.Commands.add('visitCourseWizard', (courseSlug) => {
    cy.visit(`/instructor/courses/${courseSlug}/wizard`);
    cy.get('[data-testid="course-wizard"]', { timeout: 10000 }).should('exist');
});

/**
 * Visit the course curriculum page for a specific course
 */
Cypress.Commands.add('visitCourseCurriculum', (courseSlug) => {
    cy.visit(`/instructor/courses/${courseSlug}/curriculum`);
    cy.contains('Course Curriculum', { timeout: 10000 }).should('exist');
});

/**
 * Wait for API call to complete
 */
Cypress.Commands.add('waitForApi', (alias, timeout = 10000) => {
    cy.wait(alias, { timeout }).its('response.statusCode').should('be.oneOf', [200, 201, 204]);
});

/**
 * Extract a component for easier selector reference
 */
Cypress.Commands.add('getComponent', (dataTestId, options = {}) => {
    return cy.get(`[data-testid="${dataTestId}"]`, options);
});

/**
 * Select option from dropdown by text
 */
Cypress.Commands.add('selectByText', (selector, text) => {
    cy.get(selector).select(text);
});

// Add more common commands as needed

export { };

// Augment the Cypress namespace to include custom commands
declare global {
    namespace Cypress {
        interface Chainable<Subject = any> {
            loginAsInstructor(email?: string, password?: string): void;
            createCourseViaApi(courseData?: object): Chainable<string>;
            visitCourseBuilder(courseSlug: string): void;
            visitCourseWizard(courseSlug: string): void;
            visitCourseCurriculum(courseSlug: string): void;
            waitForApi(alias: string, timeout?: number): Chainable<any>;
            getComponent(dataTestId: string, options?: any): Chainable<any>;
            selectByText(selector: string, text: string): void;
        }
    }
}
