/**
 * AI Course Builder Configuration
 *
 * Central configuration for all AI-powered course building features
 */

export const AI_BUILDER_CONFIG = {
  // AI Service Configuration
  ai: {
    // Provider settings (supports multiple AI providers)
    providers: {
      openai: {
        enabled: import.meta.env.VITE_OPENAI_ENABLED === 'true',
        apiKey: import.meta.env.VITE_OPENAI_API_KEY,
        model: import.meta.env.VITE_OPENAI_MODEL || 'gpt-4-turbo',
        maxTokens: parseInt(import.meta.env.VITE_OPENAI_MAX_TOKENS) || 4000,
        temperature: parseFloat(import.meta.env.VITE_OPENAI_TEMPERATURE) || 0.7,
      },
      anthropic: {
        enabled: import.meta.env.VITE_ANTHROPIC_ENABLED === 'true',
        apiKey: import.meta.env.VITE_ANTHROPIC_API_KEY,
        model:
          import.meta.env.VITE_ANTHROPIC_MODEL || 'claude-3-sonnet-20240229',
        maxTokens: parseInt(import.meta.env.VITE_ANTHROPIC_MAX_TOKENS) || 4000,
      },
      gemini: {
        enabled: import.meta.env.VITE_GEMINI_ENABLED === 'true',
        apiKey: import.meta.env.VITE_GEMINI_API_KEY,
        model: import.meta.env.VITE_GEMINI_MODEL || 'gemini-pro',
      },
    },

    // Default provider
    defaultProvider: import.meta.env.VITE_AI_DEFAULT_PROVIDER || 'openai',

    // Generation timeouts
    timeouts: {
      courseOutline: 30000, // 30 seconds
      moduleGeneration: 45000, // 45 seconds
      contentGeneration: 60000, // 1 minute
      enhancement: 30000, // 30 seconds
      finalization: 20000, // 20 seconds
    },

    // Retry configuration
    retries: {
      maxAttempts: 3,
      backoffMs: 1000,
      backoffMultiplier: 2,
    },
  },

  // Course Generation Workflow Configuration
  workflow: {
    phases: [
      {
        id: 'outline',
        name: 'Course Outline Generation',
        description: 'AI creates comprehensive course structure',
        estimatedTime: '2-3 minutes',
        icon: 'outline',
      },
      {
        id: 'modules',
        name: 'Module Content Development',
        description: 'Detailed module content and learning objectives',
        estimatedTime: '5-8 minutes',
        icon: 'modules',
      },
      {
        id: 'lessons',
        name: 'Lesson Content Creation',
        description: 'Individual lesson content with multimedia suggestions',
        estimatedTime: '8-12 minutes',
        icon: 'lessons',
      },
      {
        id: 'enhancement',
        name: 'Content Enhancement',
        description: 'AI improves and enriches generated content',
        estimatedTime: '3-5 minutes',
        icon: 'enhancement',
      },
      {
        id: 'finalization',
        name: 'Course Finalization',
        description: 'Final review and course preparation',
        estimatedTime: '2-3 minutes',
        icon: 'finalization',
      },
    ],

    // Total estimated time range
    totalEstimatedTime: '20-31 minutes',

    // Workflow settings
    allowSkipPhases: false,
    requireUserConfirmation: true,
    saveProgressAutomatically: true,
    enableRealTimePreview: true,
  },

  // UI Configuration
  ui: {
    // Theme and styling
    theme: {
      primaryColor: '#3B82F6',
      accentColor: '#10B981',
      warningColor: '#F59E0B',
      errorColor: '#EF4444',
      backgroundColor: '#F9FAFB',
      cardBackground: '#FFFFFF',
      borderRadius: '0.5rem',
      boxShadow:
        '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    },

    // Animation settings
    animations: {
      enabled: true,
      duration: 300,
      easing: 'ease-in-out',
      phaseTransition: 500,
      contentGeneration: 800,
    },

    // Layout settings
    layout: {
      maxWidth: '1200px',
      sidebarWidth: '300px',
      headerHeight: '80px',
      footerHeight: '60px',
    },

    // Form validation
    validation: {
      courseTitle: {
        minLength: 10,
        maxLength: 100,
        required: true,
      },
      courseDescription: {
        minLength: 50,
        maxLength: 500,
        required: true,
      },
      targetAudience: {
        minLength: 20,
        maxLength: 200,
        required: true,
      },
      learningObjectives: {
        minItems: 3,
        maxItems: 10,
        itemMinLength: 20,
        itemMaxLength: 100,
      },
    },
  },

  // Content Generation Settings
  content: {
    // Default course settings
    defaults: {
      level: 'intermediate',
      duration: '6-8 weeks',
      modulesCount: 6,
      lessonsPerModule: 4,
      assessmentTypes: ['quiz', 'project', 'discussion'],
      contentTypes: ['video', 'text', 'interactive', 'downloadable'],
    },

    // Content quality settings
    quality: {
      enableGrammarCheck: true,
      enablePlagiarismCheck: false, // Would require additional service
      enableReadabilityAnalysis: true,
      targetReadabilityScore: 8, // Grade level
      enableSEOOptimization: true,
    },

    // Content enhancement features
    enhancement: {
      enableAutoSummaries: true,
      enableKeywordExtraction: true,
      enableRelatedTopics: true,
      enableQuizGeneration: true,
      enableProjectSuggestions: true,
      enableResourceRecommendations: true,
    },
  },

  // Integration Settings
  integration: {
    // Database integration
    database: {
      useExistingSchemas: true,
      preserveCompatibility: true,
      enableDataValidation: true,
    },

    // External services
    services: {
      imageGeneration: import.meta.env.VITE_IMAGE_GENERATION_ENABLED === 'true',
      videoSuggestions:
        import.meta.env.VITE_VIDEO_SUGGESTIONS_ENABLED === 'true',
      translationServices: import.meta.env.VITE_TRANSLATION_ENABLED === 'true',
      cloudStorage: import.meta.env.VITE_CLOUD_STORAGE_ENABLED === 'true',
    },

    // API endpoints
    endpoints: {
      aiGeneration: '/api/instructor/ai-course-builder',
      contentSave: '/api/instructor/courses',
      progress: '/api/instructor/ai-course-builder/draft/',
      templateLibrary: '/api/instructor/ai-builder/templates',
    },
  },

  // Performance Settings
  performance: {
    // Caching
    caching: {
      enableResponseCache: true,
      cacheTimeout: 300000, // 5 minutes
      maxCacheSize: 50, // Maximum cached responses
    },

    // Batch processing
    batchProcessing: {
      enabled: true,
      batchSize: 5,
      processingDelay: 1000, // 1 second between batches
    },

    // Resource management
    resources: {
      maxConcurrentRequests: 3,
      enableRequestQueue: true,
      prioritizeUserRequests: true,
    },
  },

  // Development and Debug Settings
  debug: {
    enabled: import.meta.env.MODE === 'development',
    logLevel: import.meta.env.VITE_LOG_LEVEL || 'info',
    enablePerformanceMetrics: true,
    enableErrorTracking: true,
    mockAIResponses: import.meta.env.VITE_MOCK_AI === 'true',
  },

  // Feature Flags
  features: {
    enableAdvancedPrompts: true,
    enableCustomTemplates: true,
    enableCollaborativeEditing: false, // Future feature
    enableVersionControl: false, // Future feature
    enableAITutor: true, // AI assistant during creation
    enableContentAnalytics: true, // Content quality analytics
    enableExportOptions: true, // Export to various formats
    enableBulkGeneration: false, // Future feature
  },
};

// Environment validation
export const validateConfig = () => {
  const errors = [];

  // Check if at least one AI provider is configured
  const enabledProviders = Object.entries(
    AI_BUILDER_CONFIG.ai.providers
  ).filter(([, config]) => config.enabled && config.apiKey);

  if (enabledProviders.length === 0) {
    errors.push('No AI providers are properly configured');
  }

  // Check if default provider is enabled
  const defaultProvider =
    AI_BUILDER_CONFIG.ai.providers[AI_BUILDER_CONFIG.ai.defaultProvider];
  if (!defaultProvider?.enabled || !defaultProvider?.apiKey) {
    errors.push(
      `Default AI provider '${AI_BUILDER_CONFIG.ai.defaultProvider}' is not properly configured`
    );
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

// Make AI_BUILDER_CONFIG the default export as well as a named export
export default AI_BUILDER_CONFIG;
