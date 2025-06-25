/**
 * File: src/services/instructor/types.ts
 * Version: 1.1.0
 * Date: 2025-06-25 10:06:10
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 10:06:10 UTC
 *
 * Instructor Service Type Definitions
 *
 * Contains TypeScript interfaces for instructor-related data models
 * Updated with additional types for robust type checking
 */

// Course-related types
export interface Course {
    id?: number | string;
    title: string;
    subtitle?: string;
    description: string;
    slug?: string;
    thumbnail?: File | string | null;
    price?: number | string;
    discount_price?: number | string;
    category_id?: number | string;
    categoryId?: number | string;
    level?: 'beginner' | 'intermediate' | 'advanced' | 'all_levels' | string;
    has_certificate?: boolean;
    is_featured?: boolean;
    is_published?: boolean;
    requirements?: string[];
    skills?: string[];
    modules?: Module[];
    duration_minutes?: number;
    enrollments_count?: number;
    rating?: number;
    reviews_count?: number;
}

export interface CourseAnalytics {
    total_students: number;
    total_revenue: number;
    completion_rate: number;
    average_rating: number;
    monthly_enrollments: Record<string, number>;
    engagement_metrics?: {
        average_time_spent: number;
        completion_rate: number;
        dropout_points: Array<{
            module_id: number;
            module_title: string;
            dropout_count: number;
        }>;
    };
}

// Module-related types
export interface Module {
    id?: number | string;
    title: string;
    description?: string;
    course?: number | string;
    order?: number;
    lessons?: Lesson[];
    completion_percentage?: number;
    is_published?: boolean;
}

// Lesson-related types
export interface Lesson {
    id?: number | string;
    title: string;
    description?: string;
    module: number | string;
    order?: number;
    content?: string;
    guest_content?: string;
    access_level?: 'free' | 'premium' | 'guest';
    duration_minutes?: number;
    resources?: Resource[];
    assessments?: Assessment[];
    is_published?: boolean;
    completion_percentage?: number;
}

// Resource-related types
export interface Resource {
    id?: number | string;
    title: string;
    description?: string;
    lesson: number | string;
    file?: File;
    file_url?: string;
    file_size?: number;
    file_type?: string;
    premium?: boolean;
    storage_key?: string;
    download_count?: number;
}

export interface ResourceUploadPayload {
    file: File;
    title: string;
    description?: string;
    lesson: string | number;
    premium?: boolean;
}

export interface PresignedUrlPayload {
    fileName: string;
    contentType: string;
}

export interface ResourceConfirmPayload {
    resourceId: string | number;
    storageKey: string;
    filesize: number;
    mimeType: string;
    premium?: boolean;
}

// Assessment-related types
export interface Assessment {
    id?: number | string;
    title: string;
    description?: string;
    lesson: number | string;
    questions: AssessmentQuestion[];
    passing_score?: number;
    time_limit_minutes?: number;
    attempts_allowed?: number;
    is_published?: boolean;
}

export interface AssessmentQuestion {
    id?: number | string;
    text: string;
    order?: number;
    question_type: 'multiple_choice' | 'true_false' | 'short_answer';
    choices?: AssessmentChoice[];
    correct_answer?: string;
    points?: number;
    explanation?: string;
}

export interface AssessmentChoice {
    id?: number | string;
    text: string;
    is_correct?: boolean;
    explanation?: string;
}

export interface AssessmentResult {
    id?: number | string;
    assessment_id: number | string;
    user_id: number | string;
    score: number;
    passed: boolean;
    completed_at: string;
    time_spent_seconds: number;
    answers: Array<{
        question_id: number | string;
        selected_choice_id?: number | string;
        text_answer?: string;
        is_correct: boolean;
    }>;
}

// API-related types
export interface RequestOptions {
    enableCache?: boolean;
    cacheTime?: number;
    abortController?: AbortController;
    skipAuthCheck?: boolean;
    url?: string;
    returnRawResponse?: boolean;
    explicitUrl?: string;
    params?: Record<string, any>;
    retries?: number;
    retryDelay?: number;
}

export interface CacheEntry {
    data: any;
    timestamp: number;
    url: string;
}

export interface CacheStats {
    cacheSize: number;
    pendingRequests: number;
    cacheEntries: {
        key: string;
        timestamp: number;
        age: number;
        url: string;
    }[];
    refreshInProgress: boolean;
    circuitBreakerActive: boolean;
    oldestEntry: number | null;
    newestEntry: number | null;
}

// Statistics-related types
export interface InstructorStatistics {
    totalCourses: number;
    totalStudents: number;
    totalRevenue: number;
    recentEnrollments: number;
    courseCompletionRate?: number;
    activeCoursesCount?: number;
    averageRating?: number;
    reviewsCount?: number;
    monthlyStats?: Record<string, {
        revenue: number;
        enrollments: number;
    }>;
}

export interface PlatformHealthCheck {
    status: 'ok' | 'degraded' | 'outage';
    services: Record<string, {
        status: 'up' | 'down' | 'degraded';
        latency: number;
        message?: string;
    }>;
    uptime: number;
    version: string;
}

// Validation-related types
export interface FileValidationResult {
    isValid: boolean;
    error?: string;
}

export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}
