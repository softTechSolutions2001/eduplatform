/**
 * Central Type Definitions Export
 * Provides a single point of import for all TypeScript interfaces
 */

// AI Builder types
export * from './aiBuilder';

// Batch Operations types
export * from './batchOperations';

// Payment and Webhook types
export * from './payments';

// Re-export course builder types for consistency
export type {
  Course,
  Lesson,
  Module,
  Resource,
} from '../courseBuilder/store/schema';

// Common API response patterns
export interface BaseApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  count: number;
  next: string | null;
  previous: string | null;
  page_size: number;
  current_page: number;
  total_pages: number;
}

// Common error types
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: Record<string, any>;
}

// User and access level types (standardized)
export type AccessLevel = 'guest' | 'basic' | 'premium' | 'enterprise';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  access_level: AccessLevel;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

// Course access and enrollment types
export interface CourseEnrollment {
  id: number;
  user: number;
  course: number;
  enrolled_at: string;
  progress: number;
  completed: boolean;
  access_level: AccessLevel;
}
