# Course Creation and Editing Integration

## Overview

This document explains the integration between two distinct course creation and editing approaches:

1. **Step-by-Step Wizard**: A guided approach with clear steps
2. **Drag-and-Drop Builder**: A visual approach with more flexibility

## Key Components

### Selection Interface

- `CourseCreationOptions.jsx`: Provides UI for instructors to choose between approaches
- Route: `/instructor/courses/new`

### Wizard Components

- `CourseWizard.jsx`: Main wizard component for course creation
- `CourseWizardContext.jsx`: State management for the wizard
- `CourseWizardWrapper.jsx`: Wrapper to handle context properly
- `SwitchEditorBanner.jsx`: Banner to switch to builder mode

### Builder Components

- `CourseBuilder.tsx`: Main builder component for drag-and-drop course creation
- `BuilderBoard.tsx`: Canvas for drag-and-drop course building
- `SwitchEditorBanner.tsx`: Banner to switch to wizard mode

### Shared Components

- `unsavedChangesTracker.js`: Utility for tracking unsaved changes

## Integration Points

### Routes

- New course: `/instructor/courses/new` → Shows selection interface
- Wizard mode: `/instructor/courses/wizard/:courseSlug?`
- Builder mode: `/instructor/courses/builder/:courseSlug?`

### Edit Flow

The InstructorDashboard provides a dropdown menu with two editing options:

- "Edit with Wizard"
- "Edit with Builder"

### Data Consistency

Both approaches use the same backend API for saving courses, modules, and lessons, ensuring data
consistency regardless of which approach is used.

## Implementation Notes

### Unsaved Changes

Both approaches track unsaved changes using a shared utility, showing warnings when switching
between editors if there are unsaved changes.

### Accessibility

The dropdown menus and editor switching components are fully accessible.

## Future Improvements

1. Implement automatic data sync between editor modes
2. Add real-time collaboration features
3. Enhance mobile support for the builder interface
