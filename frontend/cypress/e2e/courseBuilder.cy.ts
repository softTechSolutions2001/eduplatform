// cypress/e2e/courseBuilder.cy.ts
describe('Course Builder', () => {
  beforeEach(() => {
    // Mock authentication
    cy.window().then((win) => {
      win.localStorage.setItem('authToken', 'mock-token');
    });

    // Visit the course builder page
    cy.visit('/instructor/courses/builder');
  });

  it('should display the course builder interface', () => {
    cy.get('[data-testid="course-builder"]').should('exist');
    cy.contains('New Module').should('exist');
  });

  it('allows adding a new module', () => {
    cy.get('[data-testid="add-module-btn"]').click();
    cy.get('[data-testid="module-card"]').should('have.length.at.least', 1);
  });

  it('allows editing a module title', () => {
    cy.get('[data-testid="add-module-btn"]').click();
    cy.get('[data-testid="module-title-input"]').first().clear().type('Updated Module Title');
    cy.get('[data-testid="module-title-input"]').first().should('have.value', 'Updated Module Title');
  });

  it('preserves state after page refresh during outline generation', () => {
    // Initialize the builder and enter basic info
    cy.get('[data-testid="course-title-input"]').type('Test Course');
    cy.get('[data-testid="course-description-input"]').type('Course description for testing');
    cy.get('[data-testid="next-button"]').click();

    // Add learning objectives
    cy.get('[data-testid="add-objective-btn"]').click();
    cy.get('[data-testid="objective-input"]').last().type('Learn about state persistence');
    cy.get('[data-testid="next-button"]').click();

    // Start outline generation - mock the AI service response
    cy.intercept('POST', '**/api/instructor/ai-course-builder/*/outline/', {
      statusCode: 202,
      body: {
        status: 'pending',
        taskId: 'mock-task-123',
        message: 'Course outline generation started',
        pollUrl: '/api/instructor/ai-course-builder/1/task-status/mock-task-123/'
      }
    }).as('startOutlineGeneration');

    cy.get('[data-testid="generate-outline-btn"]').click();
    cy.wait('@startOutlineGeneration');

    // Simulate outline generation in progress
    cy.intercept('GET', '**/api/instructor/ai-course-builder/*/task-status/*', {
      statusCode: 200,
      body: {
        status: 'pending',
        state: 'PENDING',
        progress: {
          percent: 50,
          message: 'Generating outline...'
        }
      }
    }).as('taskStatus');

    // Verify progress is shown
    cy.get('[data-testid="progress-indicator"]').should('exist');

    // Refresh the page
    cy.reload();

    // Verify that after reload the state is resumed - still in outline generation phase
    cy.get('[data-testid="progress-indicator"]').should('exist');
    cy.get('[data-testid="current-phase"]').should('contain', 'Outline');

    // Now simulate outline completion
    cy.intercept('GET', '**/api/instructor/ai-course-builder/*/task-status/*', {
      statusCode: 200,
      body: {
        status: 'success',
        state: 'COMPLETED',
        result: {
          outline: {
            modules: [
              {
                title: 'Test Module',
                description: 'Test module description',
                lessons: [
                  {
                    title: 'Test Lesson',
                    type: 'video'
                  }
                ]
              }
            ]
          }
        }
      }
    }).as('completedTask');

    // Verify the outline renders after completion
    cy.get('[data-testid="outline-preview"]').should('exist');
    cy.contains('Test Module').should('exist');
  });
});
