/**
 * Custom React Hooks for AI Course Builder
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import aiCourseBuilderAPI from '../api/aiCourseBuilderAPI';
import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';
import {
  useAIBuilderActions,
  useAIBuilderStore,
} from '../store/aiBuilderStore';

/**
 * Main hook for AI generation functionality
 */
export const useAIGeneration = () => {
  const { isGenerating, currentPhase, courseData, aiState, errors } =
    useAIBuilderStore();

  const {
    setGenerating,
    addGenerationToHistory,
    setGeneratedContent,
    addError,
    updatePhaseProgress,
    completePhase,
    addNotification,
  } = useAIBuilderActions();

  const abortControllerRef = useRef();

  /**
   * Generate course outline
   */
  const generateOutline = useCallback(
    async basicInfo => {
      if (isGenerating)
        return { success: false, error: 'Generation already in progress' };

      try {
        setGenerating(true);
        updatePhaseProgress('outline', 10);

        // Initialize abort controller for cancellation
        abortControllerRef.current = new AbortController();

        const result = await aiCourseBuilderAPI.generateCourseOutline(
          basicInfo,
          { signal: abortControllerRef.current.signal }
        );

        if (result.success) {
          setGeneratedContent('outline', result.data);
          addGenerationToHistory({
            type: 'outline',
            input: basicInfo,
            output: result.data,
            success: true,
          });
          updatePhaseProgress('outline', 100);
          completePhase('outline');

          addNotification({
            type: 'success',
            title: 'Course Outline Generated',
            message: 'AI has successfully created your course outline',
          });

          return result;
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        addError({
          type: 'generation_error',
          phase: 'outline',
          message: `Failed to generate course outline: ${error.message}`,
        });

        addGenerationToHistory({
          type: 'outline',
          input: basicInfo,
          success: false,
          error: error.message,
        });

        return { success: false, error: error.message };
      } finally {
        setGenerating(false);
      }
    },
    [
      isGenerating,
      setGenerating,
      updatePhaseProgress,
      completePhase,
      setGeneratedContent,
      addGenerationToHistory,
      addError,
      addNotification,
    ]
  );

  /**
   * Generate module content
   */
  const generateModuleContent = useCallback(
    async (moduleData, courseContext) => {
      if (isGenerating)
        return { success: false, error: 'Generation already in progress' };

      try {
        setGenerating(true);
        updatePhaseProgress('modules', 20);

        // Initialize abort controller for cancellation
        abortControllerRef.current = new AbortController();

        const result = await aiCourseBuilderAPI.generateModuleContent(
          moduleData,
          courseContext,
          { signal: abortControllerRef.current.signal }
        );

        if (result.success) {
          setGeneratedContent('modules', result.data);
          updatePhaseProgress('modules', 100);
          completePhase('modules');

          // Add to generation history
          addGenerationToHistory({
            type: 'modules',
            input: { moduleData, courseContext },
            output: result.data,
            timestamp: new Date().toISOString(),
          });

          addNotification({
            type: 'success',
            title: 'Module Content Generated',
            message: `Generated content for module: ${moduleData.title}`,
          });

          return result;
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        addError({
          type: 'generation_error',
          phase: 'modules',
          message: `Failed to generate module content: ${error.message}`,
        });

        return { success: false, error: error.message };
      } finally {
        setGenerating(false);
      }
    },
    [
      isGenerating,
      setGenerating,
      updatePhaseProgress,
      completePhase,
      setGeneratedContent,
      addError,
      addNotification,
    ]
  );

  /**
   * Generate lesson content
   */
  const generateLessonContent = useCallback(
    async (lessonData, moduleContext, courseContext) => {
      if (isGenerating)
        return { success: false, error: 'Generation already in progress' };

      try {
        setGenerating(true);
        updatePhaseProgress('lessons', 30);

        // Initialize abort controller for cancellation
        abortControllerRef.current = new AbortController();

        const result = await aiCourseBuilderAPI.generateLessonContent(
          lessonData,
          moduleContext,
          courseContext,
          { signal: abortControllerRef.current.signal }
        );

        if (result.success) {
          setGeneratedContent('lessons', result.data);
          updatePhaseProgress('lessons', 100);
          completePhase('lessons');

          // Add to generation history
          addGenerationToHistory({
            type: 'lessons',
            input: { lessonData, moduleContext },
            output: result.data,
            timestamp: new Date().toISOString(),
          });

          addNotification({
            type: 'success',
            title: 'Lesson Content Generated',
            message: `Generated content for lesson: ${lessonData.title}`,
          });

          return result;
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        addError({
          type: 'generation_error',
          phase: 'lessons',
          message: `Failed to generate lesson content: ${error.message}`,
        });

        return { success: false, error: error.message };
      } finally {
        setGenerating(false);
      }
    },
    [
      isGenerating,
      setGenerating,
      updatePhaseProgress,
      completePhase,
      setGeneratedContent,
      addError,
      addNotification,
    ]
  );

  /**
   * Enhance existing content
   */
  const enhanceContent = useCallback(
    async (content, enhancementType = 'general') => {
      if (isGenerating)
        return { success: false, error: 'Enhancement already in progress' };

      try {
        setGenerating(true);
        updatePhaseProgress('enhancement', 40);

        const result = await aiCourseBuilderAPI.enhanceContent(
          content,
          enhancementType
        );

        if (result.success) {
          setGeneratedContent('enhancement', result.data);
          updatePhaseProgress('enhancement', 100);
          completePhase('enhancement');

          addNotification({
            type: 'success',
            title: 'Content Enhanced',
            message: `Successfully enhanced content with ${enhancementType} improvements`,
          });

          return result;
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        addError({
          type: 'enhancement_error',
          phase: 'enhancement',
          message: `Failed to enhance content: ${error.message}`,
        });

        return { success: false, error: error.message };
      } finally {
        setGenerating(false);
      }
    },
    [
      isGenerating,
      setGenerating,
      updatePhaseProgress,
      completePhase,
      setGeneratedContent,
      addError,
      addNotification,
    ]
  );

  /**
   * Generate assessments
   */
  const generateAssessments = useCallback(
    async (lessonContent, assessmentType = 'mixed') => {
      try {
        setGenerating(true);
        updatePhaseProgress('assessments', 10);

        // Initialize abort controller for cancellation
        abortControllerRef.current = new AbortController();

        const result = await aiCourseBuilderAPI.generateAssessments(
          lessonContent,
          assessmentType,
          { signal: abortControllerRef.current.signal }
        );

        if (result.success) {
          // Store the results in the state
          setGeneratedContent('assessments', result.data);

          // Update progress to completion
          updatePhaseProgress('assessments', 100);

          // Add to generation history
          addGenerationToHistory({
            type: 'assessments',
            input: { lessonContent, assessmentType },
            output: result.data,
            timestamp: new Date().toISOString(),
          });

          addNotification({
            type: 'success',
            title: 'Assessments Generated',
            message: 'AI has created assessments for your lesson',
          });

          return result;
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        addError({
          type: 'assessment_error',
          message: `Failed to generate assessments: ${error.message}`,
        });

        return { success: false, error: error.message };
      } finally {
        setGenerating(false);
      }
    },
    [setGenerating, addError, addNotification]
  );

  /**
   * Cancel current generation
   */
  const cancelGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setGenerating(false);

      addNotification({
        type: 'info',
        title: 'Generation Cancelled',
        message: 'AI content generation has been cancelled',
      });
    }
  }, [setGenerating, addNotification]);

  /**
   * Run full course generation workflow
   */
  const runFullWorkflow = useCallback(
    async basicInfo => {
      const results = {
        outline: null,
        modules: null,
        lessons: null,
        enhancement: null,
        success: false,
      };

      try {
        // Phase 1: Generate outline
        addNotification({
          type: 'info',
          title: 'Starting Course Generation',
          message: 'Beginning AI-powered course creation workflow',
        });

        const outlineResult = await generateOutline(basicInfo);
        if (!outlineResult.success) {
          throw new Error(`Outline generation failed: ${outlineResult.error}`);
        }
        results.outline = outlineResult.data;

        // Phase 2: Generate module content
        if (results.outline?.modules) {
          const moduleResults = [];
          for (const moduleData of results.outline.modules) {
            const moduleResult = await generateModuleContent(
              moduleData,
              basicInfo
            );
            if (moduleResult.success) {
              moduleResults.push(moduleResult.data);
            }
          }
          results.modules = moduleResults;
        }

        // Phase 3: Generate lesson content (for first module as example)
        if (results.modules?.[0]?.lessons) {
          const lessonResults = [];
          for (const lessonData of results.modules[0].lessons.slice(0, 2)) {
            // Limit to first 2 lessons
            const lessonResult = await generateLessonContent(
              lessonData,
              results.modules[0],
              basicInfo
            );
            if (lessonResult.success) {
              lessonResults.push(lessonResult.data);
            }
          }
          results.lessons = lessonResults;
        }

        // Phase 4: Content enhancement
        if (results.lessons?.[0]) {
          const enhancementResult = await enhanceContent(
            results.lessons[0],
            'engagement'
          );
          if (enhancementResult.success) {
            results.enhancement = enhancementResult.data;
          }
        }

        results.success = true;

        addNotification({
          type: 'success',
          title: 'Course Generation Complete',
          message: 'AI has successfully generated your complete course!',
        });

        return results;
      } catch (error) {
        addError({
          type: 'workflow_error',
          message: `Workflow failed: ${error.message}`,
        });

        return { ...results, success: false, error: error.message };
      }
    },
    [
      generateOutline,
      generateModuleContent,
      generateLessonContent,
      enhanceContent,
      addError,
      addNotification,
    ]
  );

  return {
    // State
    isGenerating,
    currentPhase,
    aiState,
    errors,

    // Actions
    generateOutline,
    generateModuleContent,
    generateLessonContent,
    enhanceContent,
    generateAssessments,
    cancelGeneration,
    runFullWorkflow,
  };
};

/**
 * Hook for AI Builder store integration
 */
export const useAIBuilderStoreHook = () => {
  return {
    store: useAIBuilderStore(),
    actions: useAIBuilderActions(),
  };
};

/**
 * Hook for course validation and quality checks
 */
export const useCourseValidation = () => {
  const { courseData } = useAIBuilderStore();
  const { addError, addWarning } = useAIBuilderActions();

  const validateBasicInfo = useCallback(basicInfo => {
    const errors = [];
    const warnings = [];

    // Required field validation
    if (
      !basicInfo.title ||
      basicInfo.title.length <
        AI_BUILDER_CONFIG.ui.validation.courseTitle.minLength
    ) {
      errors.push(
        `Course title must be at least ${AI_BUILDER_CONFIG.ui.validation.courseTitle.minLength} characters`
      );
    }

    if (
      !basicInfo.description ||
      basicInfo.description.length <
        AI_BUILDER_CONFIG.ui.validation.courseDescription.minLength
    ) {
      errors.push(
        `Course description must be at least ${AI_BUILDER_CONFIG.ui.validation.courseDescription.minLength} characters`
      );
    }

    if (
      !basicInfo.targetAudience ||
      basicInfo.targetAudience.length <
        AI_BUILDER_CONFIG.ui.validation.targetAudience.minLength
    ) {
      errors.push(
        `Target audience must be at least ${AI_BUILDER_CONFIG.ui.validation.targetAudience.minLength} characters`
      );
    }

    // Learning objectives validation
    const objectives = basicInfo.learningObjectives || [];
    if (
      objectives.length <
      AI_BUILDER_CONFIG.ui.validation.learningObjectives.minItems
    ) {
      errors.push(
        `Please provide at least ${AI_BUILDER_CONFIG.ui.validation.learningObjectives.minItems} learning objectives`
      );
    }

    // Quality warnings
    if (
      basicInfo.title &&
      basicInfo.title.length >
        AI_BUILDER_CONFIG.ui.validation.courseTitle.maxLength
    ) {
      warnings.push('Course title might be too long for optimal display');
    }

    return { errors, warnings, isValid: errors.length === 0 };
  }, []);

  const validateCourseStructure = useCallback(courseStructure => {
    const errors = [];
    const warnings = [];

    if (!courseStructure.modules || courseStructure.modules.length === 0) {
      errors.push('Course must have at least one module');
    } else {
      // Check module structure
      courseStructure.modules.forEach((module, index) => {
        if (!module.title) {
          errors.push(`Module ${index + 1} is missing a title`);
        }

        if (!module.lessons || module.lessons.length === 0) {
          warnings.push(`Module "${module.title}" has no lessons`);
        }
      });
    }

    return { errors, warnings, isValid: errors.length === 0 };
  }, []);

  return {
    validateBasicInfo,
    validateCourseStructure,
    courseData,
  };
};

/**
 * Hook for progress tracking and analytics
 */
export const useProgressTracking = () => {
  const { performance, phaseProgress, totalProgress } = useAIBuilderStore();
  const [analytics, setAnalytics] = useState({
    timeSpent: 0,
    phasesCompleted: 0,
    efficiency: 0,
  });

  useEffect(() => {
    const updateAnalytics = () => {
      const timeSpent = performance.startTime
        ? Date.now() - performance.startTime
        : 0;
      const phasesCompleted = Object.values(phaseProgress).filter(
        progress => progress === 100
      ).length;
      const efficiency = totalProgress / Math.max(timeSpent / 1000 / 60, 1); // progress per minute

      setAnalytics({
        timeSpent,
        phasesCompleted,
        efficiency: Math.round(efficiency * 100) / 100,
      });
    };

    const interval = setInterval(updateAnalytics, 1000);
    return () => clearInterval(interval);
  }, [performance.startTime, phaseProgress, totalProgress]);

  const getTimeEstimate = useCallback(phaseId => {
    const phase = AI_BUILDER_CONFIG.workflow.phases.find(p => p.id === phaseId);
    return phase?.estimatedTime || 'Unknown';
  }, []);

  const getCompletionETA = useCallback(() => {
    const remainingPhases = AI_BUILDER_CONFIG.workflow.phases.filter(
      phase => (phaseProgress[phase.id] || 0) < 100
    );

    // Simple estimation based on average time per completed phase
    const completedPhases = Object.keys(phaseProgress).filter(
      id => phaseProgress[id] === 100
    );
    const avgTimePerPhase =
      analytics.timeSpent / Math.max(completedPhases.length, 1);
    const estimatedRemainingTime = avgTimePerPhase * remainingPhases.length;

    return {
      remainingPhases: remainingPhases.length,
      estimatedMinutes: Math.round(estimatedRemainingTime / 1000 / 60),
      estimatedTime: new Date(Date.now() + estimatedRemainingTime),
    };
  }, [phaseProgress, analytics.timeSpent]);

  return {
    analytics,
    getTimeEstimate,
    getCompletionETA,
    totalProgress,
    phaseProgress,
  };
};

/**
 * Hook for AI provider management
 */
export const useAIProvider = () => {
  const { aiState } = useAIBuilderStore();
  const { setAIProvider, setAIConnected, addError } = useAIBuilderActions();

  const checkConnection = useCallback(async () => {
    try {
      const health = await aiCourseBuilderAPI.healthCheck();
      setAIConnected(health.success);
      return health;
    } catch (error) {
      setAIConnected(false);
      addError({
        type: 'connection_error',
        message: `AI service connection failed: ${error.message}`,
      });
      return { success: false, error: error.message };
    }
  }, [setAIConnected, addError]);

  const switchProvider = useCallback(
    async provider => {
      try {
        const success = aiCourseBuilderAPI.switchProvider(provider);
        if (success) {
          setAIProvider(provider);
          await checkConnection();
          return { success: true };
        } else {
          throw new Error(`Provider ${provider} is not available`);
        }
      } catch (error) {
        addError({
          type: 'provider_error',
          message: `Failed to switch AI provider: ${error.message}`,
        });
        return { success: false, error: error.message };
      }
    },
    [setAIProvider, checkConnection, addError]
  );

  const getAvailableProviders = useCallback(() => {
    return aiCourseBuilderAPI.getAvailableProviders();
  }, []);

  return {
    currentProvider: aiState.provider,
    isConnected: aiState.isConnected,
    checkConnection,
    switchProvider,
    getAvailableProviders,
  };
};
