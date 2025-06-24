/**
 * AI Course Builder API Layer
 *
 * Handles all API communications for AI-powered course generation
 * Integrates with existing instructor service patterns
 */

import instructorService from '../../services/instructorService';
import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';
import mockResponses from './mockResponses';
import { promptTemplates } from './promptTemplates';

class AICourseBuilderAPI {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.endpoints = AI_BUILDER_CONFIG.integration.endpoints;
    this.currentProvider = AI_BUILDER_CONFIG.ai.defaultProvider;
    this.requestQueue = [];
    this.isProcessing = false;

    // Check if we should use mock responses
    const mockEnvVariable = String(import.meta.env.VITE_MOCK_AI).toLowerCase();
    const mockConfigValue =
      AI_BUILDER_CONFIG.debug && AI_BUILDER_CONFIG.debug.mockAIResponses;

    this.useMockResponses =
      mockEnvVariable === 'true' || mockConfigValue === true;

    // Force mock mode in development if there's any issue with API
    if (import.meta.env.DEV) {
      console.log('Development mode: Mock API fallbacks enabled');
    }

    if (this.useMockResponses) {
      console.info('AI Course Builder is using mock responses for development');
    }
  }

  /**
   * Health check for AI services
   */
  async healthCheck() {
    try {
      const response = await this.makeRequest(
        '/api/instructor/ai-course-builder/health',
        {
          method: 'GET',
          timeout: 5000,
        }
      );

      return { success: true, data: response };
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        success: false,
        error: error.message,
        message: 'AI services are currently unavailable',
      };
    }
  }

  /**
   * Initialize AI service connection
   */
  async initialize() {
    try {
      // Check if mock mode is enabled via environment variables or config
      const isMockMode =
        import.meta.env.VITE_MOCK_AI === 'true' ||
        import.meta.env.VITE_ENABLE_AI_MOCK_MODE === 'true' ||
        (AI_BUILDER_CONFIG.debug && AI_BUILDER_CONFIG.debug.mockAIResponses) ||
        this.useMockResponses;

      if (isMockMode || import.meta.env.DEV) {
        console.log('🤖 AI Builder: Using mock responses for development');
        return { success: true, data: mockResponses.initialize };
      }

      // Use a standardized endpoint from config
      const endpoint = '/api/instructor/ai-course-builder/initialize';
      const response = await this.makeRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          provider: this.currentProvider,
          config: AI_BUILDER_CONFIG.ai.providers[this.currentProvider],
        }),
      });

      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to initialize AI service:', error);

      // Fallback to mock response if in development mode
      if (import.meta.env.DEV && this.useMockResponses) {
        console.log('🔄 Falling back to mock response');
        return { success: true, data: mockResponses.initialize };
      }

      return { success: false, error: error.message };
    }
  }

  /**
   * Generate course outline based on basic information
   */
  async generateCourseOutline(basicInfo) {
    const prompt = promptTemplates.courseOutline(basicInfo);

    return this.generateContent('outline', prompt, {
      maxTokens: AI_BUILDER_CONFIG.ai.providers[this.currentProvider].maxTokens,
      temperature: 0.7,
      expectedStructure: {
        modules: 'array',
        assessmentStrategy: 'string',
        prerequisites: 'array',
        estimatedDuration: 'string',
      },
    });
  }

  /**
   * Generate detailed module content
   */
  async generateModuleContent(moduleData, courseContext) {
    const prompt = promptTemplates.moduleContent(moduleData, courseContext);

    return this.generateContent('module', prompt, {
      maxTokens: AI_BUILDER_CONFIG.ai.providers[this.currentProvider].maxTokens,
      temperature: 0.8,
      expectedStructure: {
        lessons: 'array',
        objectives: 'array',
        assessments: 'array',
        resources: 'array',
      },
    });
  }

  /**
   * Generate lesson content
   */
  async generateLessonContent(lessonData, moduleContext, courseContext) {
    const prompt = promptTemplates.lessonContent(
      lessonData,
      moduleContext,
      courseContext
    );

    return this.generateContent('lesson', prompt, {
      maxTokens: AI_BUILDER_CONFIG.ai.providers[this.currentProvider].maxTokens,
      temperature: 0.8,
      expectedStructure: {
        content: 'string',
        objectives: 'array',
        activities: 'array',
        assessments: 'array',
        resources: 'array',
        estimatedDuration: 'string',
      },
    });
  }

  /**
   * Enhance existing content
   */
  async enhanceContent(content, enhancementType = 'general') {
    const prompt = promptTemplates.contentEnhancement(content, enhancementType);

    return this.generateContent('enhancement', prompt, {
      maxTokens: AI_BUILDER_CONFIG.ai.providers[this.currentProvider].maxTokens,
      temperature: 0.6,
      preserveStructure: true,
    });
  }

  /**
   * Generate assessment questions
   */
  async generateAssessments(lessonContent, assessmentType = 'mixed') {
    const prompt = promptTemplates.assessmentGeneration(
      lessonContent,
      assessmentType
    );

    return this.generateContent('assessment', prompt, {
      maxTokens: 2000,
      temperature: 0.7,
      expectedStructure: {
        questions: 'array',
        rubric: 'object',
        estimatedTime: 'string',
      },
    });
  }

  /**
   * Core content generation method
   * @private
   */
  async generateContent(type, prompt, options = {}) {
    try {
      // Check if we should return mock responses
      if (this.useMockResponses) {
        console.log(`Using mock response for: ${type}`);

        // Return specific mock for the request type
        const mockResponse = mockResponses[type] || mockResponses.generic;

        // Add artificial delay to simulate real API
        await new Promise(resolve => setTimeout(resolve, 1000));

        return {
          success: true,
          data: mockResponse,
          source: 'mock',
        };
      }

      // Prepare the generation request
      const endpoint =
        this.endpoints.generate || '/api/instructor/ai-course-builder/generate';

      const response = await this.makeRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          type,
          prompt,
          options: {
            provider: this.currentProvider,
            ...options,
          },
        }),
      });

      return { success: true, data: response.data, source: 'api' };
    } catch (error) {
      console.error(`Failed to generate ${type}:`, error);

      // Fallback to mock in development
      if (import.meta.env.DEV) {
        console.log(`Falling back to mock response for ${type}`);
        return {
          success: true,
          data: mockResponses[type] || mockResponses.generic,
          source: 'mock-fallback',
        };
      }

      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Make a standardized API request
   * @private
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${instructorService.getToken()}`,
      },
    };

    const requestOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...(options.headers || {}),
      },
    };

    try {
      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `Request failed with status ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  /**
   * Save course progress to the backend
   */
  async saveCourseProgress(progressData) {
    try {
      const response = await this.makeRequest(
        this.endpoints.progress || '/api/instructor/ai-course-builder/progress',
        {
          method: 'POST',
          body: JSON.stringify({
            ...progressData,
            timestamp: new Date().toISOString(),
          }),
        }
      );

      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Create course in the existing database schema
   */
  async createCourse(courseData) {
    try {
      // Transform AI-generated data to match existing schema
      const transformedData = this.transformToExistingSchema(courseData);

      // Use existing instructor service for course creation
      const course = await instructorService.createCourse(
        transformedData.course
      );

      // Create modules using existing service
      const modules = [];
      for (const moduleData of transformedData.modules) {
        const module = await instructorService.createModule(
          course.id,
          moduleData
        );
        modules.push(module);

        // Create lessons for each module
        for (const lessonData of moduleData.lessons || []) {
          await instructorService.createLesson(module.id, {
            ...lessonData,
            course_id: course.id,
          });
        }
      }

      return {
        success: true,
        data: {
          course,
          modules,
          message: 'Course created successfully with AI-generated content',
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Transform AI-generated content to existing database schema
   * @private
   */
  transformToExistingSchema(aiCourseData) {
    const {
      basicInfo,
      outline,
      modules: aiModules,
      finalizedContent,
    } = aiCourseData;

    // Transform course data
    const courseData = {
      title: basicInfo.title,
      description: basicInfo.description,
      category_id: basicInfo.categoryId || null,
      level: basicInfo.level || 'intermediate',
      price: basicInfo.price || 0,
      has_certificate: basicInfo.hasCertificate || false,
      is_published: false, // Start as draft
      estimated_duration: basicInfo.estimatedDuration,
      learning_objectives: outline?.objectives || [],
    };

    // Transform modules data
    const modulesData = (aiModules || []).map((aiModule, index) => ({
      title: aiModule.title,
      description: aiModule.description,
      order: index + 1,
      duration_minutes: aiModule.duration_minutes || 0,
      learning_objectives: aiModule.objectives || [],
      lessons: (aiModule.lessons || []).map((aiLesson, lessonIndex) => ({
        title: aiLesson.title,
        content: aiLesson.content,
        order: lessonIndex + 1,
        type: aiLesson.type || 'text',
        duration_minutes: aiLesson.duration_minutes || 0,
        access_level: aiLesson.accessLevel || 'registered', // guest, registered, premium
        is_preview: lessonIndex === 0, // First lesson as preview
        objectives: aiLesson.objectives || [],
        resources: (aiLesson.resources || []).map(resource => ({
          title: resource.title,
          type: resource.type || 'link',
          url: resource.url,
          description: resource.description,
        })),
      })),
    }));

    return {
      course: courseData,
      modules: modulesData,
    };
  }

  /**
   * Queue management for concurrent requests
   * @private
   */
  async addToQueue(requestId, type, prompt, options) {
    return new Promise(resolve => {
      this.requestQueue.push({
        requestId,
        type,
        prompt,
        options,
        resolve,
      });
    });
  }

  /**
   * Process the next item in the queue
   * @private
   */
  async processQueue() {
    if (this.requestQueue.length === 0 || this.isProcessing) {
      return;
    }

    const request = this.requestQueue.shift();
    try {
      const result = await this.generateContent(
        request.type,
        request.prompt,
        request.options
      );
      request.resolve(result);
    } catch (error) {
      request.resolve({
        success: false,
        error: error.message,
      });
    }
  }

  /**
   * Switch AI provider
   */
  switchProvider(provider) {
    if (AI_BUILDER_CONFIG.ai.providers[provider]?.enabled) {
      this.currentProvider = provider;
      return true;
    }
    return false;
  }

  /**
   * Get available providers
   */
  getAvailableProviders() {
    return Object.entries(AI_BUILDER_CONFIG.ai.providers)
      .filter(([, config]) => config.enabled && config.apiKey)
      .map(([name, config]) => ({
        name,
        model: config.model,
        maxTokens: config.maxTokens,
      }));
  }

  /**
   * Save progress for a draft course
   */
  async saveProgress(draftId, payload) {
    return this.makeRequest(
      `/api/instructor/ai-course-builder/draft/${draftId}/`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }
    );
  }
}

// Create singleton instance
const aiCourseBuilderAPI = new AICourseBuilderAPI();
export default aiCourseBuilderAPI;
