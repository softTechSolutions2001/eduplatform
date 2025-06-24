# AI Course Builder Setup Guide

This guide will walk you through setting up and testing the AI Course Builder component with mock API responses.

## Setup Options

### Option 1: Quick Start (Recommended)

Run the provided batch script from the project root:

```bash
start-mock-ai.bat
```

This script automatically:

- Sets the necessary environment variables for mock mode
- Starts the frontend development server

### Option 2: Using npm Scripts

```bash
cd frontend
npm run dev:mock
```

This command uses the cross-env package to set environment variables and start the development server.

### Option 3: Manual Configuration

1. Create or modify `.env` in the frontend directory:

   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_MOCK_AI=true
   VITE_AI_MOCK_RESPONSES=true
   VITE_AI_DEBUG_MODE=true
   VITE_ENABLE_AI_COURSE_BUILDER=true
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

## Testing the AI Course Builder

1. Start the frontend using one of the methods above
2. Open your browser to `http://localhost:5173`
3. Log in with instructor credentials
4. Navigate to "Courses" → "Create Course" → "Create with AI"
5. Follow the step-by-step wizard:

   a. **Basic Information**:

   - Enter course title, description, and other details
   - Click "Next"

   b. **Learning Objectives**:

   - Add 3-5 learning objectives
   - Click "Next"

   c. **Course Outline Generation**:

   - This will display a mock outline generation process
   - Review the generated outline
   - Click "Next"

   d. **Module Content Development**:

   - Review the mock module content
   - Click "Next"

   e. **Course Finalization**:

   - Review and finalize the course
   - Click "Complete Course"

## Verification

To verify mock mode is working correctly:

1. Open the browser developer console (F12)
2. Look for these messages:

   - "AI Course Builder is using mock responses for development"
   - "Using mock initialize response"

3. Confirm there are no 404 errors in the API requests
4. Check that all phases of the wizard show realistic mock data

## Common Issues and Solutions

### Issue: "Objects are not valid as a React child"

**Solution**: This is usually caused by trying to render an object directly. We've fixed this by properly handling the `currentPhase` property in the PhaseIndicator component.

### Issue: API 404 errors

**Solution**: The URL normalization has been fixed to prevent duplicate `/api` prefixes in requests.

### Issue: Mock responses not being used

**Solution**:

- Check that `VITE_MOCK_AI=true` is set in your environment
- Verify that the browser console shows "AI Course Builder is using mock responses for development"
- Try restarting the development server

### Issue: Changes to mock responses not reflecting

**Solution**: Any changes to the mock responses in `mockResponses.js` require a server restart to take effect.

## Development Tips

1. **Customizing Mock Responses**:
   Edit `src/aiCourseBuilder/api/mockResponses.js` to modify the mock data

2. **Debug Mode**:
   With `VITE_AI_DEBUG_MODE=true`, you'll see additional console logging

3. **Error Testing**:
   To test error handling, modify the mock responses to return `success: false` with an error message
