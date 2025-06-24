# AI Course Builder Module

## Overview

The AI Course Builder is a comprehensive, AI-powered course creation system for the EduPlatform
application. It enables instructors to create exceptional educational content efficiently using
state-of-the-art AI assistance while maintaining complete compatibility with existing database
schemas.

## Latest Updates (June 2025)

- ✅ Fixed "initializeBuilder is not a function" error
- ✅ Fixed HTTP 404 errors with API request URL normalization
- ✅ Resolved React rendering issues with object properties
- ✅ Added mock API mode for development without backend
- ✅ Added error boundaries for improved error handling
- ✅ Enhanced testing tools and documentation

## Features

### 🤖 AI-Powered Course Generation

- **5-Phase Workflow**: Structured course creation process
- **Smart Content Generation**: AI-generated course outlines, modules, and lessons
- **Learning Objectives**: Auto-categorization using Bloom's taxonomy
- **Content Enhancement**: Real-time AI suggestions for improvement

### 🎯 Instructor Experience

- **Interactive Forms**: Step-by-step course creation with validation
- **Real-time Preview**: Live preview of generated content with typewriter effects
- **Block-based Editor**: Modern content editing with drag-and-drop
- **Progress Tracking**: Visual progress indicators throughout the workflow

### 🔧 Technical Features

- **Zero Database Changes**: Uses existing EduPlatform schemas
- **Modular Architecture**: Self-contained in `src/aiCourseBuilder/`
- **State Management**: Zustand + Immer for optimal performance
- **TypeScript Ready**: Full TypeScript compatibility
- **Error Handling**: Comprehensive error boundaries and fallbacks
- **Mock API Mode**: Develop without backend dependencies
- **Integration Tests**: Vitest-based tests for components and flow
- **Debug Mode**: Enhanced logging for development troubleshooting

## Getting Started

### 1. Environment Setup

#### Regular Setup

Copy the environment template and configure your AI service:

```bash
cp frontend/.env.template frontend/.env
```

Configure your AI service in `.env`:

#### Mock API Mode (No Backend Required)

For development without a backend or API keys:

```bash
# Option 1: Use the provided script
npm run dev:mock

# Option 2: Use the test environment
cp frontend/.env.test frontend/.env
npm run dev
```

```env
# Choose your AI provider
VITE_AI_SERVICE_PROVIDER=openai

# OpenAI Configuration
VITE_OPENAI_API_KEY=your_api_key_here
VITE_OPENAI_MODEL=gpt-4

# Enable features
VITE_ENABLE_AI_COURSE_BUILDER=true
```

### 2. Access the AI Course Builder

1. Navigate to the Instructor Dashboard
2. Click on **"AI Course Builder"** button
3. Follow the 5-phase workflow:
   - **Phase 1**: Basic Course Information
   - **Phase 2**: Learning Objectives
   - **Phase 3**: Course Outline Generation
   - **Phase 4**: Content Creation
   - **Phase 5**: Review & Finalize

### 3. Development Mode

For development, enable mock responses:

```env
VITE_AI_DEBUG_MODE=true
VITE_AI_MOCK_RESPONSES=true
```

## Architecture

### Directory Structure

```
src/aiCourseBuilder/
├── index.js                     # Main module exports
├── config/
│   └── aiBuilderConfig.js      # Configuration system
├── store/
│   └── aiBuilderStore.js       # Zustand + Immer state
├── api/
│   ├── aiCourseBuilderAPI.js   # API integration
│   └── promptTemplates.js      # AI prompt templates
├── hooks/
│   └── useAIGeneration.js      # Custom React hooks
├── components/
│   ├── AICourseBuilder.jsx     # Main component
│   ├── CourseGenerationWizard.jsx
│   ├── input/                  # Input components
│   ├── generation/             # Generation components
│   ├── preview/                # Preview components
│   ├── content/                # Content editing
│   └── ui/                     # UI components
└── utils/
    ├── aiWorkflowUtils.js      # Workflow management
    ├── contentTemplates.js     # Content templates
    └── validationHelpers.js    # Validation functions
```

### State Management

The module uses Zustand with Immer for state management:

```javascript
// Access the store
import { useAIBuilderStore } from './store/aiBuilderStore';

const { currentPhase, courseData, updateCourseData } = useAIBuilderStore();
```

### AI Integration

Multiple AI providers are supported:

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude models
- **Google**: Gemini Pro
- **Local**: Ollama/local models

## API Integration

### Existing EduPlatform Services

The module integrates with existing services:

```javascript
import courseService from '../services/courseService';
import instructorService from '../services/instructorService';
```

### AI API Calls

AI generation is handled through the API layer:

```javascript
import { generateCourseOutline, enhanceContent } from './api/aiCourseBuilderAPI';
```

## Components

### Main Components

1. **AICourseBuilder**: Main wrapper component
2. **CourseGenerationWizard**: 5-phase workflow manager
3. **BasicInfoForm**: Course information input
4. **ObjectivesInput**: Learning objectives management
5. **ContentEditor**: Block-based content editing

### UI Components

- **ProgressBar**: Reusable progress indicator
- **PhaseIndicator**: Workflow phase display
- **NotificationSystem**: Toast notifications

## Customization

### AI Prompts

Customize AI prompts in `api/promptTemplates.js`:

```javascript
export const courseOutlinePrompt = courseInfo => `
  Create a course outline for: ${courseInfo.title}
  // ... custom prompt logic
`;
```

### Content Templates

Add new templates in `utils/contentTemplates.js`:

```javascript
export const customTemplate = {
  id: 'custom',
  name: 'Custom Template',
  structure: {
    // template definition
  },
};
```

### Validation Rules

Customize validation in `utils/validationHelpers.js`:

```javascript
export const validateCourseTitle = title => {
  // custom validation logic
  return { isValid: true, message: '' };
};
```

## Testing

### Unit Tests

Run component tests:

```bash
cd frontend
npm test
```

### Integration Tests

Test the full workflow:

```bash
npm run test:integration
```

### E2E Tests

Test user interactions:

```bash
npm run test:e2e
```

## Configuration

### AI Builder Config

Configure the module in `config/aiBuilderConfig.js`:

```javascript
export const aiBuilderConfig = {
  phases: ['basic-info', 'objectives', 'outline', 'content', 'review'],
  aiService: {
    provider: process.env.VITE_AI_SERVICE_PROVIDER,
    timeout: parseInt(process.env.VITE_AI_GENERATION_TIMEOUT),
    retryAttempts: parseInt(process.env.VITE_AI_RETRY_ATTEMPTS),
  },
};
```

### Environment Variables

| Variable                        | Description          | Default  |
| ------------------------------- | -------------------- | -------- |
| `VITE_AI_SERVICE_PROVIDER`      | AI service provider  | `openai` |
| `VITE_OPENAI_API_KEY`           | OpenAI API key       | -        |
| `VITE_AI_GENERATION_TIMEOUT`    | Request timeout (ms) | `30000`  |
| `VITE_ENABLE_AI_COURSE_BUILDER` | Enable the module    | `true`   |
| `VITE_AI_DEBUG_MODE`            | Debug mode           | `false`  |
| `VITE_AI_MOCK_RESPONSES`        | Use mock responses   | `false`  |

## Troubleshooting

### Common Issues

1. **Module not loading**: Check that the route is properly configured in `App.jsx`
2. **AI generation failing**: Verify API keys and network connectivity
3. **State not persisting**: Check Zustand store configuration
4. **Styling issues**: Ensure Tailwind CSS is properly configured

### Debug Mode

Enable debug mode for detailed logging:

```env
VITE_AI_DEBUG_MODE=true
```

### Mock Responses

For development without AI API calls:

```env
VITE_AI_MOCK_RESPONSES=true
```

## Performance

### Optimization Features

- **Lazy Loading**: Components are loaded on-demand
- **Code Splitting**: Separate bundles for optimal loading
- **State Batching**: Efficient state updates with Immer
- **Memoization**: React.memo and useMemo for performance

### Bundle Analysis

Analyze the bundle size:

```bash
npm run build:analyze
```

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/ai-builder-enhancement`
2. Make changes in `src/aiCourseBuilder/`
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

### Code Standards

- Follow existing EduPlatform conventions
- Use TypeScript types where applicable
- Add comprehensive error handling
- Include JSDoc comments for functions

## License

This module is part of the EduPlatform application and follows the same licensing terms.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed description
4. Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: June 2, 2025  
**Author**: EduPlatform Development Team
