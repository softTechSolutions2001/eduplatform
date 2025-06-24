# Drag-and-Drop Course Creation Testing Suite

This directory contains comprehensive testing for the Drag-and-Drop course creation workflow in EduPlatform. The tests cover all aspects of drag-and-drop functionality across multiple interfaces including CourseBuilder, CourseWizard, and CurriculumPage.

## Test Coverage

The test suite includes:

1. **CourseBuilder Tests** (`courseBuilder-dnd.cy.ts`)
   - Module reordering using react-dnd
   - Lesson reordering within modules
   - Error handling and edge cases

2. **CurriculumPage Tests** (`curriculumPage-dnd.cy.ts`)
   - Module reordering using react-beautiful-dnd
   - Lesson reordering within expanded modules
   - UI interaction and error handling

3. **CourseWizard Tests** (`courseWizard-dnd.cy.ts`)
   - Module reordering in the Module Structure step
   - Testing context synchronization
   - Error handling and recovery

4. **Cross-Mode Compatibility** (`dnd-cross-mode.cy.ts`)
   - Data synchronization between different interfaces
   - Round-trip testing across all three interfaces
   - Data integrity validation

5. **Visual Regression Tests** (`dnd-visual.cy.ts`)
   - Visual feedback during drag operations
   - Proper hover states and spacing
   - Accessibility indicators

## Running the Tests

### Prerequisites

1. Make sure you have Node.js installed (v14+ recommended)
2. Install dependencies: `npm install`
3. Ensure the backend API server is running or properly mocked
4. Configure authentication credentials (see "Authentication Setup" below)

### Authentication Setup

Create a `cypress.env.json` file in the `frontend` directory with your instructor credentials:

```json
{
  "INSTRUCTOR_EMAIL": "your-instructor-email@example.com",
  "INSTRUCTOR_PASSWORD": "your-instructor-password"
}
```

For development/testing, you can use the following credentials (already set up):
- Email: mohithasanthanam@gmail.com
- Password: Vajjiram@79

**Important**: Never commit the `cypress.env.json` file to version control to protect credentials!

### Starting Required Services

1. **Start the Database:**
   - Using VS Code tasks: Run the "Start Database" task
   - Or manually using PostgreSQL (ensure credentials match the application's configuration)

2. **Start the Backend Server:**
   - Using VS Code tasks: Run the "Start Backend" task
   - Or manually:
     ```bash
     cd backend
     venv\scripts\activate
     python manage.py runserver
     ```

3. **Start the Frontend Server:**
   - Using VS Code tasks: Run the "Start Frontend" task
   - Or manually:
     ```bash
     cd frontend
     npm run dev
     ```

### Running Individual Test Suites

```bash
# Run CourseBuilder DnD tests
npx cypress run --spec "cypress/e2e/courseBuilder-dnd.cy.ts"

# Run CurriculumPage DnD tests
npx cypress run --spec "cypress/e2e/curriculumPage-dnd.cy.ts"

# Run CourseWizard DnD tests
npx cypress run --spec "cypress/e2e/courseWizard-dnd.cy.ts"

# Run cross-mode compatibility tests
npx cypress run --spec "cypress/e2e/dnd-cross-mode.cy.ts"

# Run visual regression tests
npx cypress run --spec "cypress/e2e/dnd-visual.cy.ts"

### Running All DnD Tests

To run all drag-and-drop tests at once:

```bash
# Run all DnD tests in headless mode
npm run test:e2e:dnd

# Run all DnD tests in interactive mode (Cypress UI)
npm run test:e2e:dnd:open
```

## Troubleshooting Common Issues

### Authentication Problems

- Ensure `cypress.env.json` exists with correct credentials
- Check that the login API endpoint hasn't changed
- Verify the instructor account has appropriate permissions

### Test Failures

1. **Selectors Not Found**
   - UI elements may have been renamed or restructured
   - Update selectors in the test files and the DnD command files

2. **API Intercepts Failing**
   - API endpoints or response formats may have changed
   - Update the fixtures in `cypress/fixtures/` to match current API responses

3. **DnD Simulations Not Working**
   - Library versions may have changed (react-dnd or react-beautiful-dnd)
   - Check browser console for errors during test execution
   - Update the simulation logic in `dnd-commands.ts` as needed

4. **Visual Regression Failures**
   - UI styling or layout changes may affect visual tests
   - Update baseline screenshots if design changes are intentional

### Debugging Tips

- Use `cy.pause()` in test code to pause execution at specific points
- Add `cy.debug()` to inspect the current state of the application
- Use `.debug()` after a command to log detailed information about elements
- Run tests in interactive mode (`npm run test:e2e:dnd:open`) for better debugging
npx cypress run --spec "cypress/e2e/courseWizard-dnd.cy.ts"

# Run cross-mode compatibility tests
npx cypress run --spec "cypress/e2e/dnd-cross-mode.cy.ts"

# Run visual regression tests (requires cypress-image-snapshot)
npx cypress run --spec "cypress/e2e/dnd-visual.cy.ts"
```

### Running All DnD Tests

```bash
npx cypress run --spec "cypress/e2e/*dnd*.cy.ts"
```

### Opening Cypress Test Runner

```bash
npx cypress open
```

## Test Architecture

### Custom Commands

The test suite uses custom commands to abstract common operations:

1. **Drag & Drop Commands**
   - `reactDndDrag`: For react-dnd components in CourseBuilder
   - `reorderBuilderModules`: Module reordering in CourseBuilder
   - `reorderBuilderLessons`: Lesson reordering in CourseBuilder
   - `rbdDragAndDrop`: For react-beautiful-dnd components
   - `reorderRbdModules`: Module reordering in CurriculumPage/CourseWizard
   - `reorderRbdLessons`: Lesson reordering in CurriculumPage

2. **Common Commands**
   - `loginAsInstructor`: Authentication helper
   - `createCourseViaApi`: Test course setup
   - `visitCourseBuilder`, `visitCourseCurriculum`, `visitCourseWizard`: Navigation

### Fixtures

Test data is provided through fixtures:

- `course.json`: Complete course structure with modules and lessons
- `modules.json`: Sample modules for API mocking
- `lessons.json`: Sample lessons for API mocking
- `reorder-response.json`: API response for reorder operations

## Maintaining the Tests

### When Adding New Features

1. If adding new DnD functionality:
   - Add test cases to the relevant test file
   - Update custom commands if needed
   - Update fixtures to include new data structures

2. If modifying existing DnD implementations:
   - Verify all existing tests pass
   - Update selectors in tests if HTML structure changes
   - Check cross-mode compatibility tests

### Common Issues and Solutions

1. **Tests fail with "Element not found" errors**
   - Check if data-testid attributes have changed
   - Verify the DOM structure matches test expectations
   - Ensure API mocks return expected data

2. **Drag and drop operations don't work**
   - Check if the DnD library implementation changed
   - Verify the drag events are being dispatched correctly
   - Adjust the simulation in dnd-commands.ts

3. **Cross-mode tests fail**
   - Check the courseDataSync.js implementation for compatibility
   - Verify API endpoints for reordering are consistent
   - Ensure state management is properly synchronized

## Visual Testing Setup

For visual regression testing:

1. Install the required plugin: `npm install --save-dev cypress-image-snapshot`
2. Configure the plugin in `cypress/plugins/index.js`
3. Uncomment the `matchImageSnapshot` lines in the visual tests

## Continuous Integration

These tests are designed to run in CI environments. For best results:

- Use a consistent viewport size for visual tests
- Set proper timeouts for API operations
- Mock external services for consistent results

## Contributing

When adding or modifying tests:

1. Follow the existing patterns for consistency
2. Document any assumptions or special requirements
3. Ensure tests are robust against minor UI changes
4. Test on multiple resolutions if design is responsive
