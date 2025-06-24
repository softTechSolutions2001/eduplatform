/**
 * AI Course Builder Type Definitions
 * Resolves schema mismatch for AI generation status tracking
 */

import { Course } from '../courseBuilder/store/schema';

export type AIGenerationStatusType =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

export interface AIGenerationStatus {
  id: string;
  user: number;
  status: AIGenerationStatusType;
  progress: number;
  message?: string;
  result_data?: Course;
  created_at: string;
  updated_at: string;
}

export interface AIGenerationStatusResponse {
  data: AIGenerationStatus;
  success: boolean;
  message?: string;
}

export interface AIGenerationRequest {
  prompt: string;
  course_level?: 'beginner' | 'intermediate' | 'advanced';
  duration_preference?: 'short' | 'medium' | 'long';
  include_assessments?: boolean;
}

export interface AIGenerationError {
  error_code: string;
  error_message: string;
  details?: Record<string, any>;
}

// Hook return types for React Query integration
export interface UseAIGenerationStatusReturn {
  status: AIGenerationStatus | null;
  isLoading: boolean;
  error: AIGenerationError | null;
  refetch: () => void;
}

export interface UseStartGenerationReturn {
  startGeneration: (
    request: AIGenerationRequest
  ) => Promise<AIGenerationStatus>;
  isLoading: boolean;
  error: AIGenerationError | null;
}
