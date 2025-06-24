/**
 * AI Course Builder Store - Zustand + Immer
 *
 * Centralized state management for the AI Course Builder module
 * Uses Zustand for simplicity and Immer for immutable updates
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';

const initialState = {
  // Current workflow state
  currentPhase: null,
  phaseProgress: {},
  phaseData: {},
  totalProgress: 0,
  isGenerating: false,
  draftId: null,

  // Course data being built
  courseData: {
    basicInfo: {
      title: '',
      description: '',
      category: '',
      level: 'intermediate',
      targetAudience: '',
      estimatedDuration: '', // Legacy field for backward compatibility
      duration_minutes: 0, // New standardized field
      learningObjectives: [],
    },
    outline: {
      modules: [],
      assessmentStrategy: '',
      prerequisites: [],
      courseStructure: null,
    },
    modules: [],
    generatedContent: {},
    enhancements: {},
    finalizedContent: {},
  },

  // AI generation state
  aiState: {
    provider: AI_BUILDER_CONFIG.ai.defaultProvider,
    isConnected: false,
    lastError: null,
    generationHistory: [],
    currentRequest: null,
  },

  // UI state
  ui: {
    activeStep: 1,
    showPreview: false,
    sidebarOpen: true,
    previewMode: 'outline',
    notifications: [],
    isFullscreen: false,
  },

  // Settings and preferences
  settings: {
    autoSave: true,
    realTimePreview: true,
    showAdvancedOptions: false,
    preferredContentTypes: ['video', 'text', 'interactive'],
    language: 'en',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  },

  // Error handling
  errors: [],
  warnings: [],

  // Performance tracking
  performance: {
    startTime: null,
    phaseTimings: {},
    totalGenerationTime: 0,
  },
};

export const useAIBuilderStore = create(
  subscribeWithSelector(
    immer((set, get) => ({
      ...initialState,

      // Phase Management Actions
      setCurrentPhase: phase =>
        set(state => {
          // Store only the phase id (string) so selector comparisons are cheap
          state.currentPhase = typeof phase === 'object' ? phase.id : phase;
          if (!state.performance.startTime) {
            state.performance.startTime = Date.now();
          }
          if (
            phase &&
            !state.performance.phaseTimings[
              typeof phase === 'object' ? phase.id : phase
            ]
          ) {
            state.performance.phaseTimings[
              typeof phase === 'object' ? phase.id : phase
            ] = { start: Date.now() };
          }
        }),

      updatePhaseProgress: (phaseId, progress) =>
        set(state => {
          state.phaseProgress[phaseId] = progress;

          // Calculate total progress - properly account for total possible progress
          const totalPhases = AI_BUILDER_CONFIG.workflow.phases.length;
          const completedProgress = Object.values(state.phaseProgress).reduce(
            (sum, p) => sum + p,
            0
          );
          state.totalProgress = Math.round(completedProgress / phases.length);
        }),

      updatePhaseData: (phase, data) =>
        set(state => {
          state.phaseData[phase] = {
            ...(state.phaseData[phase] || {}),
            ...data,
          };
        }),

      completePhase: phaseId =>
        set(state => {
          state.phaseProgress[phaseId] = 100;
          if (state.performance.phaseTimings[phaseId]) {
            state.performance.phaseTimings[phaseId].end = Date.now();
            state.performance.phaseTimings[phaseId].duration =
              state.performance.phaseTimings[phaseId].end -
              state.performance.phaseTimings[phaseId].start;
          }

          // Move to next phase if available
          const currentIndex = AI_BUILDER_CONFIG.workflow.phases.findIndex(
            p => p.id === phaseId
          );
          const nextPhase = AI_BUILDER_CONFIG.workflow.phases[currentIndex + 1];
          if (nextPhase) {
            state.currentPhase = nextPhase;
            state.performance.phaseTimings[nextPhase.id] = {
              start: Date.now(),
            };
          }
        }),

      // Course Data Actions
      updateBasicInfo: info =>
        set(state => {
          state.courseData.basicInfo = {
            ...state.courseData.basicInfo,
            ...info,
          };
        }),

      updateCourseOutline: outline =>
        set(state => {
          state.courseData.outline = outline;
        }),

      addModule: module =>
        set(state => {
          state.courseData.modules.push({
            id: Date.now().toString(),
            order: state.courseData.modules.length + 1,
            createdAt: new Date().toISOString(),
            ...module,
          });
        }),

      updateModule: (moduleId, updates) =>
        set(state => {
          const moduleIndex = state.courseData.modules.findIndex(
            m => m.id === moduleId
          );
          if (moduleIndex !== -1) {
            state.courseData.modules[moduleIndex] = {
              ...state.courseData.modules[moduleIndex],
              ...updates,
              updatedAt: new Date().toISOString(),
            };
          }
        }),

      removeModule: moduleId =>
        set(state => {
          state.courseData.modules = state.courseData.modules.filter(
            m => m.id !== moduleId
          );
          // Reorder remaining modules
          state.courseData.modules.forEach((module, index) => {
            module.order = index + 1;
          });
        }),

      // AI Generation Actions
      setGenerating: isGenerating =>
        set(state => {
          state.isGenerating = isGenerating;
        }),

      setAIProvider: provider =>
        set(state => {
          state.aiState.provider = provider;
        }),

      setAIConnected: isConnected =>
        set(state => {
          state.aiState.isConnected = isConnected;
        }),

      addGenerationToHistory: generation =>
        set(state => {
          state.aiState.generationHistory.unshift({
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            ...generation,
          });

          // Keep only last 50 generations
          if (state.aiState.generationHistory.length > 50) {
            state.aiState.generationHistory =
              state.aiState.generationHistory.slice(0, 50);
          }
        }),

      setCurrentRequest: request =>
        set(state => {
          state.aiState.currentRequest = request;
        }),

      // Content Management Actions
      setGeneratedContent: (phaseId, content) =>
        set(state => {
          state.courseData.generatedContent[phaseId] = {
            ...content,
            generatedAt: new Date().toISOString(),
            phaseId,
          };
        }),

      updateGeneratedContent: (phaseId, updates) =>
        set(state => {
          if (state.courseData.generatedContent[phaseId]) {
            state.courseData.generatedContent[phaseId] = {
              ...state.courseData.generatedContent[phaseId],
              ...updates,
              updatedAt: new Date().toISOString(),
            };
          }
        }),

      // UI Actions
      setActiveStep: step =>
        set(state => {
          state.ui.activeStep = step;
        }),

      togglePreview: () =>
        set(state => {
          state.ui.showPreview = !state.ui.showPreview;
        }),

      setPreviewMode: mode =>
        set(state => {
          state.ui.previewMode = mode;
        }),

      toggleSidebar: () =>
        set(state => {
          state.ui.sidebarOpen = !state.ui.sidebarOpen;
        }),

      addNotification: notification =>
        set(state => {
          state.ui.notifications.unshift({
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            ...notification,
          });
        }),

      removeNotification: id =>
        set(state => {
          state.ui.notifications = state.ui.notifications.filter(
            n => n.id !== id
          );
        }),

      clearNotifications: () =>
        set(state => {
          state.ui.notifications = [];
        }),

      toggleFullscreen: () =>
        set(state => {
          state.ui.isFullscreen = !state.ui.isFullscreen;
        }),

      // Settings Actions
      updateSettings: settings =>
        set(state => {
          state.settings = { ...state.settings, ...settings };
        }),

      // Error Handling Actions
      addError: error =>
        set(state => {
          state.errors.unshift({
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            message: error.message || error,
            type: error.type || 'error',
            phase: state.currentPhase?.id,
            ...error,
          });
          state.aiState.lastError = error;
        }),

      removeError: id =>
        set(state => {
          state.errors = state.errors.filter(e => e.id !== id);
        }),

      clearErrors: () =>
        set(state => {
          state.errors = [];
          state.aiState.lastError = null;
        }),

      addWarning: warning =>
        set(state => {
          state.warnings.unshift({
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            message: warning.message || warning,
            phase: state.currentPhase?.id,
            ...warning,
          });
        }),

      clearWarnings: () =>
        set(state => {
          state.warnings = [];
        }),
      // Utility Actions
      resetBuilder: () =>
        set(state => {
          // Reset to initial state but preserve settings
          const currentSettings = state.settings;
          Object.assign(state, initialState);
          state.settings = currentSettings;
        }),

      initializeBuilder: async () => {
        const state = get();
        try {
          // Clear any existing autosave timer first to prevent duplicates
          if (window.aiBuilderAutoSaveTimeout) {
            clearTimeout(window.aiBuilderAutoSaveTimeout);
            window.aiBuilderAutoSaveTimeout = null;
          }

          // Set the first phase as current
          const firstPhase = AI_BUILDER_CONFIG.workflow.phases[0];
          set(state => {
            state.currentPhase = firstPhase;
            state.performance.startTime = Date.now();
            state.performance.phaseTimings[firstPhase.id] = {
              start: Date.now(),
            };
          });

          // Check AI connectivity
          try {
            // Import and initialize the API
            const { default: api } = await import('../api/aiCourseBuilderAPI');
            const result = await api.initialize();
            if (result.success) {
              set(state => {
                state.aiState.isConnected = true;
              });
            } else {
              throw new Error(
                result.error || 'Failed to connect to AI service'
              );
            }
          } catch (error) {
            console.warn('AI service connection warning:', error);
            // Still proceed, but mark as not connected
            set(state => {
              state.aiState.isConnected = false;
            });
          }

          // Attempt to load saved progress
          get().loadProgress();

          return true;
        } catch (error) {
          set(state => {
            state.errors.push({
              id: Date.now().toString(),
              timestamp: new Date().toISOString(),
              message:
                error.message || 'Failed to initialize AI Course Builder',
              type: 'initialization_error',
            });
          });
          console.error('Failed to initialize AI Course Builder:', error);
          return false;
        }
      },

      loadFromExisting: courseData =>
        set(state => {
          state.courseData = {
            ...initialState.courseData,
            ...courseData,
          };
        }),

      // Persistence Actions
      saveProgress: async () => {
        const state = get();
        try {
          const progressData = {
            currentPhase: state.currentPhase,
            phaseProgress: state.phaseProgress,
            courseData: state.courseData,
            timestamp: new Date().toISOString(),
          };

          // Save to localStorage for quick recovery
          localStorage.setItem(
            'aiCourseBuilder_progress',
            JSON.stringify(progressData)
          );

          // Save to server if a draftId exists
          if (state.draftId) {
            const { default: api } = await import('../api/aiCourseBuilderAPI');
            await api.saveProgress(state.draftId, state.courseData);
          }

          return true;
        } catch (error) {
          get().addError({
            message: 'Failed to save progress',
            type: 'save_error',
            error,
          });
          return false;
        }
      },

      loadProgress: () => {
        try {
          const savedProgress = localStorage.getItem(
            'aiCourseBuilder_progress'
          );
          if (savedProgress) {
            const progressData = JSON.parse(savedProgress);
            set(state => {
              state.currentPhase = progressData.currentPhase;
              state.phaseProgress = progressData.phaseProgress || {};
              state.courseData = {
                ...state.courseData,
                ...progressData.courseData,
              };
            });
            return true;
          }
        } catch (error) {
          console.error('Failed to load progress:', error);
        }
        return false;
      },

      // Course finalization
      finalizeCourse: async () => {
        const state = get();
        try {
          // Ensure we have a draft ID
          if (!state.draftId) {
            throw new Error('Cannot finalize a course without a draft ID');
          }

          // Clear any autosave timer
          if (window.aiBuilderAutoSaveTimeout) {
            clearTimeout(window.aiBuilderAutoSaveTimeout);
            window.aiBuilderAutoSaveTimeout = null;
          }

          // Do a final save of all content
          await get().saveProgress();

          // Import the API and finalize the course
          const { default: api } = await import('../api/aiCourseBuilderAPI');
          const result = await api.finalizeCourse(state.draftId);

          // Clear local storage progress data
          localStorage.removeItem('aiCourseBuilder_progress');

          return result;
        } catch (error) {
          get().addError({
            message: 'Failed to finalize course',
            type: 'finalize_error',
            error,
          });
          return { success: false, error: error.message };
        }
      },

      // Computed getters
      getPhaseProgress: phaseId => {
        return get().phaseProgress[phaseId] || 0;
      },

      getCurrentPhaseData: () => {
        const state = get();
        return state.currentPhase;
      },

      getCourseDataForExport: () => {
        const state = get();
        return {
          basicInfo: state.courseData.basicInfo,
          outline: state.courseData.outline,
          modules: state.courseData.modules,
          finalizedContent: state.courseData.finalizedContent,
          metadata: {
            createdAt: state.performance.startTime,
            totalGenerationTime: state.performance.totalGenerationTime,
            aiProvider: state.aiState.provider,
            version: '1.0.0',
          },
        };
      },

      getPerformanceMetrics: () => {
        const state = get();
        const totalTime = state.performance.startTime
          ? Date.now() - state.performance.startTime
          : 0;

        return {
          totalTime,
          phaseTimings: state.performance.phaseTimings,
          averagePhaseTime: Object.values(state.performance.phaseTimings)
            .filter(timing => timing.duration)
            .reduce(
              (sum, timing, _, arr) => sum + timing.duration / arr.length,
              0
            ),
          completedPhases: Object.keys(state.phaseProgress).filter(
            phaseId => state.phaseProgress[phaseId] === 100
          ).length,
        };
      },
    }))
  )
);

// Persistence middleware - auto-save on important changes
useAIBuilderStore.subscribe(
  state => state.courseData,
  () => {
    const state = useAIBuilderStore.getState();
    if (state.settings.autoSave) {
      // Debounce auto-save
      clearTimeout(window.aiBuilderAutoSaveTimeout);
      window.aiBuilderAutoSaveTimeout = setTimeout(() => {
        state.saveProgress();
      }, 2000);
    }
  },
  { fireImmediately: false }
);

// Export hooks for component usage
export const useAIBuilderActions = () => {
  const store = useAIBuilderStore();
  return {
    // Phase actions
    setCurrentPhase: store.setCurrentPhase,
    updatePhaseProgress: store.updatePhaseProgress,
    completePhase: store.completePhase,

    // Course data actions
    updateBasicInfo: store.updateBasicInfo,
    updateCourseOutline: store.updateCourseOutline,
    addModule: store.addModule,
    updateModule: store.updateModule,
    removeModule: store.removeModule,

    // AI actions
    setGenerating: store.setGenerating,
    setAIProvider: store.setAIProvider,
    addGenerationToHistory: store.addGenerationToHistory,

    // UI actions
    setActiveStep: store.setActiveStep,
    togglePreview: store.togglePreview,
    toggleSidebar: store.toggleSidebar,
    addNotification: store.addNotification,
    removeNotification: store.removeNotification,

    // Error handling
    addError: store.addError,
    clearErrors: store.clearErrors,

    // Utility actions
    resetBuilder: store.resetBuilder,
    initializeBuilder: store.initializeBuilder,
    saveProgress: store.saveProgress,
    loadProgress: store.loadProgress,
    finalizeCourse: store.finalizeCourse,
  };
};

export const useAIBuilderSelector = selector => useAIBuilderStore(selector);

export default useAIBuilderStore;
