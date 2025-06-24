// Import cypress commands
import './commands.ts';
import './dnd-commands.ts';

// Configure global behavior
Cypress.on('uncaught:exception', (err) => {
    // Returning false prevents Cypress from failing the test when an uncaught exception occurs
    // This is useful when testing drag and drop which can trigger exceptions in the browser
    // that don't affect the actual test functionality

    // Ignore ResizeObserver errors as they're related to UI and don't affect functionality
    if (err.message.includes('ResizeObserver') ||
        err.message.includes('draggable')) {
        return false;
    }

    // For other errors, let Cypress fail the test
    return true;
});

// Add other global configuration as needed
