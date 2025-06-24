/**
 * AI Course Builder Integration Test
 *
 * This test verifies that the AI Course Builder module is properly integrated
 * with the EduPlatform application.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AICourseBuilder } from '../src/aiCourseBuilder';

// Mock the auth context
jest.mock('../src/contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    isInstructor: true,
    user: { id: 1, name: 'Test Instructor' }
  })
}));

// Mock environment variables
global.import.meta = {
  env: {
    VITE_ENABLE_AI_COURSE_BUILDER: 'true',
    VITE_AI_MOCK_RESPONSES: 'true',
    VITE_AI_DEBUG_MODE: 'true'
  }
};

describe('AI Course Builder Integration', () => {
  beforeEach(() => {
    // Reset any mocks or state before each test
  });

  it('should render the main AI Course Builder component', () => {
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    expect(screen.getByText(/AI Course Builder/i)).toBeInTheDocument();
  });

  it('should display the welcome screen initially', () => {
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    expect(screen.getByText(/Welcome to the AI Course Builder/i)).toBeInTheDocument();
    expect(screen.getByText(/Start Creating/i)).toBeInTheDocument();
  });

  it('should navigate to basic info phase when started', async () => {
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    const startButton = screen.getByText(/Start Creating/i);
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Course Basic Information/i)).toBeInTheDocument();
    });
  });

  it('should validate required fields', async () => {
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    // Start the workflow
    const startButton = screen.getByText(/Start Creating/i);
    fireEvent.click(startButton);

    await waitFor(() => {
      const nextButton = screen.getByText(/Next/i);
      fireEvent.click(nextButton);
    });

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/Course title is required/i)).toBeInTheDocument();
    });
  });

  it('should progress through all phases', async () => {
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    // Start workflow
    fireEvent.click(screen.getByText(/Start Creating/i));

    // Fill basic info
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/Course Title/i), {
        target: { value: 'Test Course' }
      });
      fireEvent.change(screen.getByLabelText(/Description/i), {
        target: { value: 'Test Description' }
      });
    });

    // Proceed through phases
    const phases = ['basic-info', 'objectives', 'outline', 'content', 'review'];

    for (let i = 0; i < phases.length - 1; i++) {
      const nextButton = screen.getByText(/Next/i);
      fireEvent.click(nextButton);

      await waitFor(() => {
        // Verify phase progression
        expect(screen.getByTestId(`phase-${phases[i + 1]}`)).toBeInTheDocument();
      });
    }
  });
});

describe('AI Course Builder Store', () => {
  it('should initialize with default state', () => {
    const { useAIBuilderStore } = require('../src/aiCourseBuilder/store/aiBuilderStore');
    const state = useAIBuilderStore.getState();

    expect(state.currentPhase).toBe('welcome');
    expect(state.courseData).toEqual({});
    expect(state.isGenerating).toBe(false);
  });

  it('should update course data correctly', () => {
    const { useAIBuilderStore } = require('../src/aiCourseBuilder/store/aiBuilderStore');
    const { updateCourseData } = useAIBuilderStore.getState();

    updateCourseData({ title: 'Test Course' });

    const updatedState = useAIBuilderStore.getState();
    expect(updatedState.courseData.title).toBe('Test Course');
  });
});

describe('AI API Integration', () => {  it('should handle mock responses in development', async () => {
    const aiCourseBuilderAPI = require('../src/aiCourseBuilder/api/aiCourseBuilderAPI').default;

    const courseInfo = {
      title: 'Test Course',
      description: 'Test Description',
      subject: 'Technology'
    };

    const result = await aiCourseBuilderAPI.generateCourseOutline(courseInfo);

    expect(result).toBeDefined();
    expect(result.modules).toBeInstanceOf(Array);
    expect(result.modules.length).toBeGreaterThan(0);
  });
  it('should handle API errors gracefully', async () => {
    const aiCourseBuilderAPI = require('../src/aiCourseBuilder/api/aiCourseBuilderAPI').default;

    // Mock API failure
    global.fetch = jest.fn().mockRejectedValue(new Error('API Error'));

    const courseInfo = { title: 'Test Course' };

    await expect(generateCourseOutline(courseInfo)).rejects.toThrow();
  });
});

describe('Validation Helpers', () => {
  it('should validate course titles correctly', () => {
    const { validateCourseTitle } = require('../src/aiCourseBuilder/utils/validationHelpers');

    expect(validateCourseTitle('').isValid).toBe(false);
    expect(validateCourseTitle('Valid Course Title').isValid).toBe(true);
    expect(validateCourseTitle('a'.repeat(300)).isValid).toBe(false);
  });

  it('should validate learning objectives', () => {
    const { validateLearningObjectives } = require('../src/aiCourseBuilder/utils/validationHelpers');

    expect(validateLearningObjectives([]).isValid).toBe(false);
    expect(validateLearningObjectives(['Objective 1', 'Objective 2']).isValid).toBe(true);
  });
});

export default {
  name: 'AI Course Builder Integration Tests',
  description: 'Comprehensive tests for the AI Course Builder module integration'
};
