# AI Course Builder Troubleshooting Guide

## Common Errors and Solutions

### 1. API Connection Errors

#### Symptoms

- HTTP 404 errors in the console
- "Failed to initialize AI service" messages
- Duplicate `/api` in URLs (`/api/api/instructor/...`)

#### Solutions

- **Double `/api` prefix**: Fixed in `aiCourseBuilderAPI.js` by normalizing URLs correctly
- **Backend not running**: Use mock mode with `VITE_MOCK_AI=true`
- **Wrong API URL**: Check `VITE_API_BASE_URL` in `.env`

#### How to Verify

Check browser console for:

```
GET http://localhost:8000/api/instructor/ai-builder/initialize
```

Instead of:

```
GET http://localhost:8000/api/api/instructor/ai-builder/initialize
```

### 2. React Rendering Errors

#### Symptoms

- Error: "Objects are not valid as a React child (found: object with keys {id, name, description, estimatedTime, icon})"
- UI fails to render, showing error boundary

#### Solutions

- **Phase object rendering**: Fixed in `PhaseIndicator.jsx` by properly handling the `currentPhase` property
- **Direct object rendering**: Ensure all components render primitive values, not objects

#### How to Verify

- The PhaseIndicator component should correctly show the current phase based on ID or index
- No React errors in the console about invalid children

### 3. Mock API Issues

#### Symptoms

- Mock mode not working despite environment variables
- "Cannot read property of undefined" when accessing mock data

#### Solutions

- **Mock flag not detected**: Use `VITE_MOCK_AI=true` (not `false`, `0`, or empty string)
- **Mock data structure mismatch**: Update mock response objects in `mockResponses.js`
- **Mock mode not enabled**: Restart the development server after changing environment variables

#### How to Verify

Check for:

```
AI Course Builder is using mock responses for development
Using mock initialize response
```

in the console log.

### 4. Builder Initialization Failure

#### Symptoms

- "initializeBuilder is not a function" error
- Blank screen after loading
- Error boundary showing initialization failure

#### Solutions

- **Missing function**: Ensure `initializeBuilder` is exported in `aiBuilderStore.js`
- **Store import issue**: Check import statements in components using the function
- **Store not initialized**: Force mock mode to bypass initialization issues

#### How to Verify

```javascript
// Should be defined in aiBuilderStore.js
initializeBuilder: async () => {
  // Implementation...
}

// Should be exported in useAIBuilderActions
export const useAIBuilderActions = () => {
  // ...
  initializeBuilder: store.initializeBuilder,
  // ...
};
```

### 5. Phase Navigation Issues

#### Symptoms

- Unable to proceed to the next phase
- "Cannot read properties of undefined" errors
- Validation errors preventing progression

#### Solutions

- **Missing phase data**: Check phase data structure in the store
- **Validation errors**: Log and identify which validation is failing
- **Navigation logic**: Check `handleNext` and `handlePrevious` functions

#### How to Verify

Add console logs in the navigation functions:

```javascript
console.log("Current phase:", currentPhase);
console.log("Phase data:", phaseData);
console.log("Validation errors:", validationErrors);
```

## Quick Recovery Steps

If you encounter persistent issues with the AI Course Builder:

1. **Force mock mode**:

   ```
   VITE_MOCK_AI=true
   VITE_AI_MOCK_RESPONSES=true
   VITE_AI_DEBUG_MODE=true
   ```

2. **Clear browser cache and storage**:

   - Open DevTools > Application > Storage
   - Clear site data and localStorage

3. **Use the error boundary recovery**:

   - When the error boundary shows, click "Try Again"
   - This will reset the component state without a full page reload

4. **Run the provided batch script**:

   ```
   start-mock-ai.bat
   ```

5. **Check browser console for specific errors**:
   - Network tab for API issues
   - Console tab for JavaScript errors
   - React DevTools for component state issues

## Advanced Debugging

### Checking Component Rendering

Add these debug logs to identify rendering issues:

```jsx
console.log("PhaseIndicator props:", {
  phases,
  currentPhase: currentPhase,
  currentPhaseIndex:
    typeof currentPhase === "string"
      ? phases.findIndex((p) => p.id === currentPhase)
      : currentPhase,
});
```

### Tracking Store State Changes

Use the Zustand middleware to log state changes:

```javascript
import { devtools } from "zustand/middleware";

export const useAIBuilderStore = create(
  devtools(
    subscribeWithSelector(
      immer((set, get) => ({
        // Store implementation
      }))
    )
  )
);
```

### Monitoring API Requests

Add an interceptor to log all API requests:

```javascript
const originalFetch = window.fetch;
window.fetch = function (url, options) {
  if (url.includes("/api/")) {
    console.log("API Request:", url, options);
  }
  return originalFetch.apply(this, arguments);
};
```
