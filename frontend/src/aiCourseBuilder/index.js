/**
 * AI-Assisted Course Builder Module - Main Entry Point
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * This module provides comprehensive AI-powered course creation capabilities
 * integrated seamlessly with the existing EduPlatform infrastructure.
 *
 * Features:
 * - AI-driven course content generation (5-phase workflow)
 * - Advanced instructor experience with real-time AI assistance
 * - Complete compatibility with existing database schemas
 * - Modular architecture for easy maintenance and extension
 */

// Main component exports
export { default as AICourseBuilder } from './components/AICourseBuilder';
export { default as CourseGenerationWizard } from './components/CourseGenerationWizard';

// Input Components
export { default as BasicInfoForm } from './components/input/BasicInfoForm';
export { default as ObjectivesInput } from './components/input/ObjectivesInput';

// Generation Components
export { default as ContentPreview } from './components/generation/ContentPreview';
export { default as PhaseProgress } from './components/generation/PhaseProgress';

// Preview Components
export { default as CourseOutlinePreview } from './components/preview/CourseOutlinePreview';
export { default as ModulePreview } from './components/preview/ModulePreview';

// Content Components
export { default as ContentEditor } from './components/content/ContentEditor';
export { default as EnhancementSuggestions } from './components/content/EnhancementSuggestions';

// UI Components
export {
  default as NotificationSystem,
  useNotifications,
} from './components/ui/NotificationSystem';
export { default as PhaseIndicator } from './components/ui/PhaseIndicator';
export { default as ProgressBar } from './components/ui/ProgressBar';

// Hook exports
export { useAIGeneration } from './hooks/useAIGeneration';
export { useAIBuilderStore } from './store/aiBuilderStore';

// API exports
export { default as aiCourseBuilderAPI } from './api/aiCourseBuilderAPI';
export { promptTemplates } from './api/promptTemplates';

// Utility exports
export * from './utils/aiWorkflowUtils';
export * from './utils/contentTemplates';
export * from './utils/validationHelpers';

// Configuration
export { default as aiBuilderConfig } from './config/aiBuilderConfig';

// Module configuration for lazy loading
export const moduleConfig = {
  name: 'ai-course-builder',
  version: '1.0.0',
  description: 'AI-Assisted Course Builder for EduPlatform',
  main: 'AICourseBuilder',
  dependencies: ['react', 'zustand', 'immer', '@heroicons/react'],
  routes: [
    {
      path: '/instructor/ai-course-builder',
      component: 'AICourseBuilder',
      exact: true,
      title: 'AI Course Builder',
    },
    {
      path: '/instructor/ai-course-builder/:draftId',
      component: 'AICourseBuilder',
      exact: true,
      title: 'AI Course Builder - Edit Draft',
    },
  ],
};
