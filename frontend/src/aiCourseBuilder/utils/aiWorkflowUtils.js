// AI Workflow Utilities for Course Builder
// Re-exporting from consolidated workflowValidation.js file

import {
  PHASES,
  PHASE_CONFIG,
  validateBasicInfo,
  validateCourseBasicInfo,
  validateCourseData,
  validateCourseOutline,
  validateCourseWithWorkflow,
} from './workflowValidation';

export {
  PHASES,
  PHASE_CONFIG,
  validateBasicInfo,
  validateCourseBasicInfo,
  validateCourseData,
  validateCourseOutline,
  validateCourseWithWorkflow,
};

// Legacy PHASE_CONFIG definition kept for backward compatibility
export const PHASE_CONFIG_LEGACY = {
  [PHASES.BASIC_INFO]: {
    title: 'Basic Information',
    description: 'Define course fundamentals and target audience',
    estimatedTime: '5-10 minutes',
    requiredFields: ['title', 'description', 'category', 'level', 'duration'],
    validations: {
      title: { minLength: 5, maxLength: 100 },
      description: { minLength: 50, maxLength: 500 },
      duration: { min: 1, max: 200 },
    },
  },
  [PHASES.LEARNING_OBJECTIVES]: {
    title: 'Learning Objectives',
    description: 'Set clear, measurable learning outcomes',
    estimatedTime: '10-15 minutes',
    requiredFields: ['objectives'],
    validations: {
      objectives: { minCount: 3, maxCount: 8 },
    },
  },
  [PHASES.OUTLINE_GENERATION]: {
    title: 'Course Outline',
    description: 'AI-generated course structure and modules',
    estimatedTime: '2-5 minutes',
    requiredFields: ['outline'],
    validations: {
      modules: { minCount: 2, maxCount: 12 },
      lessonsPerModule: { min: 2, max: 10 },
    },
  },
  [PHASES.CONTENT_CREATION]: {
    title: 'Content Creation',
    description: 'Generate detailed lesson content',
    estimatedTime: '15-30 minutes',
    requiredFields: ['content'],
    validations: {},
  },
  [PHASES.REVIEW_FINALIZE]: {
    title: 'Review & Finalize',
    description: 'Final review and course publication',
    estimatedTime: '10-15 minutes',
    requiredFields: [],
    validations: {},
  },
};

/**
 * Workflow state management
 */
export class WorkflowManager {
  constructor(initialPhase = PHASES.BASIC_INFO) {
    this.currentPhase = initialPhase;
    this.completedPhases = new Set();
    this.phaseData = {};
    this.validationErrors = {};
  }

  getCurrentPhase() {
    return this.currentPhase;
  }

  getPhaseOrder() {
    return Object.keys(PHASES).map(key => PHASES[key]);
  }

  getCurrentPhaseIndex() {
    return this.getPhaseOrder().indexOf(this.currentPhase);
  }

  canProceedToPhase(phase) {
    const currentIndex = this.getCurrentPhaseIndex();
    const targetIndex = this.getPhaseOrder().indexOf(phase);

    // Can go to current phase or next phase
    if (targetIndex <= currentIndex + 1) return true;

    // Can go to any completed phase
    return this.completedPhases.has(phase);
  }

  validatePhaseData(phase, data) {
    const config = PHASE_CONFIG[phase];
    const errors = {};

    // Check required fields
    config.requiredFields.forEach(field => {
      if (
        !data[field] ||
        (Array.isArray(data[field]) && data[field].length === 0)
      ) {
        errors[field] = `${field} is required`;
      }
    });

    // Apply specific validations
    Object.entries(config.validations).forEach(([field, rules]) => {
      const value = data[field];

      if (value !== undefined && value !== null) {
        if (rules.minLength && value.length < rules.minLength) {
          errors[field] =
            `${field} must be at least ${rules.minLength} characters`;
        }
        if (rules.maxLength && value.length > rules.maxLength) {
          errors[field] =
            `${field} must not exceed ${rules.maxLength} characters`;
        }
        if (rules.min && value < rules.min) {
          errors[field] = `${field} must be at least ${rules.min}`;
        }
        if (rules.max && value > rules.max) {
          errors[field] = `${field} must not exceed ${rules.max}`;
        }
        if (
          rules.minCount &&
          Array.isArray(value) &&
          value.length < rules.minCount
        ) {
          errors[field] = `${field} must have at least ${rules.minCount} items`;
        }
        if (
          rules.maxCount &&
          Array.isArray(value) &&
          value.length > rules.maxCount
        ) {
          errors[field] = `${field} must not exceed ${rules.maxCount} items`;
        }
      }
    });

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }

  completePhase(phase, data) {
    const validation = this.validatePhaseData(phase, data);

    if (!validation.isValid) {
      this.validationErrors[phase] = validation.errors;
      return { success: false, errors: validation.errors };
    }

    this.phaseData[phase] = data;
    this.completedPhases.add(phase);
    delete this.validationErrors[phase];

    return { success: true };
  }

  moveToPhase(phase) {
    if (!this.canProceedToPhase(phase)) {
      throw new Error(`Cannot proceed to phase ${phase}`);
    }

    this.currentPhase = phase;
    return true;
  }

  nextPhase() {
    const currentIndex = this.getCurrentPhaseIndex();
    const phases = this.getPhaseOrder();

    if (currentIndex < phases.length - 1) {
      return this.moveToPhase(phases[currentIndex + 1]);
    }

    return false;
  }

  previousPhase() {
    const currentIndex = this.getCurrentPhaseIndex();
    const phases = this.getPhaseOrder();

    if (currentIndex > 0) {
      return this.moveToPhase(phases[currentIndex - 1]);
    }

    return false;
  }

  getPhaseProgress() {
    const totalPhases = this.getPhaseOrder().length;
    const completed = this.completedPhases.size;
    return (completed / totalPhases) * 100;
  }

  getAllData() {
    return this.phaseData;
  }

  reset() {
    this.currentPhase = PHASES.BASIC_INFO;
    this.completedPhases.clear();
    this.phaseData = {};
    this.validationErrors = {};
  }
}

/**
 * AI Generation utilities
 */
export const AI_GENERATION_TYPES = {
  COURSE_OUTLINE: 'course-outline',
  LEARNING_OBJECTIVES: 'learning-objectives',
  LESSON_CONTENT: 'lesson-content',
  ASSESSMENT: 'assessment',
  ENHANCEMENT_SUGGESTIONS: 'enhancement-suggestions',
};

export class AIGenerationManager {
  constructor() {
    this.generationHistory = [];
    this.activeGenerations = new Map();
  }

  async generateContent(type, context, options = {}) {
    const generationId = this.createGenerationId();

    const generation = {
      id: generationId,
      type,
      context,
      options,
      status: 'pending',
      startTime: new Date(),
      progress: 0,
    };

    this.activeGenerations.set(generationId, generation);

    try {
      // Simulate AI generation with progress updates
      const result = await this.simulateAIGeneration(
        generation,
        options.onProgress
      );

      generation.status = 'completed';
      generation.endTime = new Date();
      generation.result = result;
      generation.progress = 100;

      this.generationHistory.push(generation);
      this.activeGenerations.delete(generationId);

      return result;
    } catch (error) {
      generation.status = 'failed';
      generation.error = error.message;
      generation.endTime = new Date();

      this.generationHistory.push(generation);
      this.activeGenerations.delete(generationId);

      throw error;
    }
  }

  async simulateAIGeneration(generation, onProgress) {
    const { type, context } = generation;

    // Simulate progress updates
    const progressSteps = [20, 40, 60, 80, 100];
    for (const progress of progressSteps) {
      await new Promise(resolve =>
        setTimeout(resolve, 500 + Math.random() * 1000)
      );
      generation.progress = progress;
      onProgress?.(progress);
    }

    // Return mock results based on type
    switch (type) {
      case AI_GENERATION_TYPES.COURSE_OUTLINE:
        return this.generateMockOutline(context);
      case AI_GENERATION_TYPES.LEARNING_OBJECTIVES:
        return this.generateMockObjectives(context);
      case AI_GENERATION_TYPES.LESSON_CONTENT:
        return this.generateMockContent(context);
      case AI_GENERATION_TYPES.ASSESSMENT:
        return this.generateMockAssessment(context);
      default:
        return { generated: true, content: 'Generated content' };
    }
  }

  generateMockOutline(context) {
    const { title, level, duration } = context;
    const moduleCount = Math.ceil(duration / 20); // Rough estimate

    return {
      modules: Array.from({ length: moduleCount }, (_, i) => ({
        title: `Module ${i + 1}: Core Concepts`,
        description: `Essential concepts and practical applications for ${title}`,
        estimatedDuration: Math.floor(duration / moduleCount),
        lessons: Array.from(
          { length: 3 + Math.floor(Math.random() * 3) },
          (_, j) => ({
            title: `Lesson ${j + 1}: Understanding Key Principles`,
            description: 'Detailed exploration of fundamental concepts',
            type: ['video', 'reading', 'quiz'][Math.floor(Math.random() * 3)],
            estimatedDuration: 15 + Math.floor(Math.random() * 30),
          })
        ),
      })),
    };
  }

  generateMockObjectives(context) {
    return {
      objectives: [
        'Understand fundamental concepts and principles',
        'Apply knowledge to real-world scenarios',
        'Analyze complex problems and propose solutions',
        'Evaluate different approaches and methodologies',
        'Create original content and implementations',
      ],
    };
  }

  generateMockContent(context) {
    return `# ${context.title || 'Lesson Content'}

## Introduction
This lesson covers essential concepts that will help you understand the core principles of the subject matter.

## Key Concepts
- **Concept 1**: Fundamental principle that forms the foundation
- **Concept 2**: Advanced application of the fundamental principle
- **Concept 3**: Practical implementation strategies

## Detailed Explanation
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Practice Exercise
Try implementing the concepts you've learned:
1. Step one instructions
2. Step two instructions
3. Step three instructions

## Summary
In this lesson, you learned about the key concepts and their applications.`;
  }

  generateMockAssessment(context) {
    return {
      questions: [
        {
          type: 'multiple-choice',
          question: 'What is the primary concept discussed in this lesson?',
          options: ['Option A', 'Option B', 'Option C', 'Option D'],
          correct: 0,
        },
        {
          type: 'true-false',
          question: 'The fundamental principle applies to all scenarios.',
          correct: true,
        },
        {
          type: 'short-answer',
          question:
            'Explain how you would apply this concept in a real-world scenario.',
        },
      ],
    };
  }

  createGenerationId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  getActiveGenerations() {
    return Array.from(this.activeGenerations.values());
  }

  getGenerationHistory() {
    return this.generationHistory;
  }

  cancelGeneration(id) {
    if (this.activeGenerations.has(id)) {
      const generation = this.activeGenerations.get(id);
      generation.status = 'cancelled';
      generation.endTime = new Date();

      this.generationHistory.push(generation);
      this.activeGenerations.delete(id);

      return true;
    }
    return false;
  }
}

/**
 * Content formatting utilities
 */
export const formatDuration = minutes => {
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
};

export const formatProgress = (progress, total) => {
  return Math.round((progress / total) * 100);
};

export const generateUniqueId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};
