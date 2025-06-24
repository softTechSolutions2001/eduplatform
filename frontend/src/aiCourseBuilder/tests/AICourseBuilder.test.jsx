// Test script for AI Course Builder flow with mock responses
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useAIBuilderStore } from '../store/aiBuilderStore';
import AICourseBuilder from '../components/AICourseBuilder';
import mockResponses from '../api/mockResponses';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => vi.fn(),
}));

// Mock auth context
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    currentUser: { id: 'test-user', role: 'instructor' },
    isInstructor: () => true,
  }),
}));

// Mock API service
vi.mock('../api/aiCourseBuilderAPI', () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      initialize: vi
        .fn()
        .mockResolvedValue({ success: true, data: mockResponses.initialize }),
      generateCourseOutline: vi.fn().mockImplementation(basicInfo => {
        return Promise.resolve({
          success: true,
          data: mockResponses.courseOutline(basicInfo).data,
        });
      }),
      generateModuleContent: vi.fn().mockImplementation(module => {
        return Promise.resolve({
          success: true,
          data: mockResponses.moduleContent(module).data,
        });
      }),
      generateAssessment: vi.fn().mockImplementation(() => {
        return Promise.resolve({
          success: true,
          data: mockResponses.assessment().data,
        });
      }),
    })),
  };
});

describe('AI Course Builder Integration Test', () => {
  // Reset store before each test
  beforeEach(() => {
    // Clear all mocks
    vi.clearAllMocks();

    // Reset store to initial state
    const { resetBuilder } = useAIBuilderStore.getState();
    resetBuilder();
  });

  it('Complete AI Course Builder flow with mock data', async () => {
    // Render the component
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    // Wait for initialization
    await waitFor(() => {
      expect(screen.queryByText(/initializing/i)).not.toBeInTheDocument();
    });

    // Basic Info Phase
    expect(screen.getByText(/Course Information/i)).toBeInTheDocument();

    // Fill in basic course info
    fireEvent.change(screen.getByLabelText(/Course Title/i), {
      target: { value: 'JavaScript Fundamentals' },
    });

    fireEvent.change(screen.getByLabelText(/Course Description/i), {
      target: { value: 'Learn the basics of modern JavaScript programming' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    // Learning Objectives Phase
    await waitFor(() => {
      expect(screen.getByText(/Learning Objectives/i)).toBeInTheDocument();
    });

    // Add learning objectives
    fireEvent.click(screen.getByRole('button', { name: /Add Objective/i }));
    fireEvent.change(screen.getByTestId('objective-input-0'), {
      target: { value: 'Master JavaScript syntax and data structures' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    // Course Outline Generation Phase
    await waitFor(() => {
      expect(
        screen.getByText(/Course Outline Generation/i)
      ).toBeInTheDocument();
    });

    // Wait for outline generation to complete
    await waitFor(() => {
      expect(
        screen.getByText(/Introduction to JavaScript Fundamentals/i)
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    // Module Content Development Phase
    await waitFor(() => {
      expect(
        screen.getByText(/Module Content Development/i)
      ).toBeInTheDocument();
    });

    // Wait for module content generation to complete
    await waitFor(() => {
      expect(
        screen.getByText(/Variables, Data Types, and Operators/i)
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Next/i }));

    // Review and Finalization Phase
    await waitFor(() => {
      expect(screen.getByText(/Course Finalization/i)).toBeInTheDocument();
    });

    // Complete course creation
    fireEvent.click(screen.getByRole('button', { name: /Complete Course/i }));

    // Verify completion
    await waitFor(() => {
      // Expects redirect to course page, which in the test would mean
      // the navigate function was called
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.stringContaining('/instructor/courses/')
      );
    });
  });
  it('Handles API errors gracefully', async () => {
    // Mock API failure
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock the API module
    const mockInitialize = vi.fn().mockRejectedValue(new Error('API Error'));
    vi.mocked(
      vi.importMock('../api/aiCourseBuilderAPI').default
    ).mockImplementation(() => ({
      initialize: mockInitialize,
      generateCourseOutline: vi.fn(),
    }));

    // Render the component
    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    // Should show error state
    await waitFor(() => {
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
    });

    // Reset console.error mock
    console.error.mockRestore();
  });

  it('initializes with mock responses when mock mode is enabled', async () => {
    // Save original env
    const originalEnv = import.meta.env;

    // Mock the env
    vi.stubGlobal('import.meta', {
      env: {
        ...originalEnv,
        VITE_MOCK_AI: 'true',
        VITE_AI_MOCK_RESPONSES: 'true',
      },
    });

    render(
      <MemoryRouter>
        <AICourseBuilder />
      </MemoryRouter>
    );

    // Wait for initialization
    await waitFor(() => {
      expect(screen.queryByText(/Initializing/i)).not.toBeInTheDocument();
    });

    // Restore env
    vi.stubGlobal('import.meta', {
      env: originalEnv,
    });
  });
});
