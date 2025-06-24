/**
 * Batch Operations Type Definitions
 * Resolves schema mismatch for bulk operation results
 */

export interface BatchOperationError {
  item_id: string | number;
  error_code: string;
  error_message: string;
  field_errors?: Record<string, string[]>;
}

export interface BatchOperationResult {
  operation_id: string;
  total_items: number;
  successful_items: number;
  failed_items: number;
  errors?: BatchOperationError[];
  results?: Record<string, any>[];
}

export interface BatchOperationResponse {
  data: BatchOperationResult;
  success: boolean;
  message?: string;
}

// Specific batch operation types
export interface BatchCourseUpdateRequest {
  course_ids: number[];
  updates: {
    category_id?: number;
    access_level?: 'guest' | 'basic' | 'premium' | 'enterprise';
    is_published?: boolean;
    tags?: string[];
  };
}

export interface BatchUserUpdateRequest {
  user_ids: number[];
  updates: {
    access_level?: 'guest' | 'basic' | 'premium' | 'enterprise';
    is_active?: boolean;
    groups?: string[];
  };
}

export interface BatchDeleteRequest {
  item_ids: (string | number)[];
  item_type: 'course' | 'user' | 'lesson' | 'module';
  cascade?: boolean;
}

// Hook return types for React Query integration
export interface UseBatchOperationReturn {
  executeBatch: (
    request:
      | BatchCourseUpdateRequest
      | BatchUserUpdateRequest
      | BatchDeleteRequest
  ) => Promise<BatchOperationResult>;
  isLoading: boolean;
  error: string | null;
  result: BatchOperationResult | null;
}

export interface UseBatchStatusReturn {
  status: BatchOperationResult | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}
