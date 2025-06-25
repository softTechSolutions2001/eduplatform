/**
 * File: src/services/http/endpoints.ts
 * Version: 2.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * API endpoint definitions for the EduPlatform frontend
 * Enhanced with role-based routing and utility functions
 */

import { API_BASE_URL } from './constants';

// Base paths for role-based routing
const BASE_PATHS = {
    INSTRUCTOR: '/instructor',
    STUDENT: '/student',
    AUTH: '/auth',
    SYSTEM: '/system',
} as const;

/**
 * Helper function to get full API URL (including base URL)
 * Useful for external calls or when working with tools like axios-mock-adapter
 */
export function getFullApiUrl(path: string): string {
    const baseUrl = import.meta.env?.VITE_API_BASE_URL || API_BASE_URL || '/api';
    return `${baseUrl}${path}`;
}

/**
 * Helper function to validate endpoint URLs at runtime
 */
export function validateEndpoint(url: string): boolean {
    try {
        new URL(url, 'http://localhost');
        return true;
    } catch {
        return false;
    }
}

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: `${API_BASE_URL}/user/login/`,
        LOGOUT: `${API_BASE_URL}/user/logout/`,
        REFRESH: `${API_BASE_URL}/token/refresh/`,
        REGISTER: `${API_BASE_URL}/user/register/`,
        CURRENT_USER: `${API_BASE_URL}/user/me/`,
        VERIFY_EMAIL: `${API_BASE_URL}/user/email/verify/`,
        RESET_PASSWORD: `${API_BASE_URL}/user/password/reset/`,
        RESET_PASSWORD_REQUEST: `${API_BASE_URL}/user/reset-password-request/`,
        CONFIRM_RESET: `${API_BASE_URL}/user/password/reset/confirm/`,
        CHANGE_PASSWORD: `${API_BASE_URL}/user/password/change/`,
        // Enhanced social auth endpoints
        SOCIAL_AUTH: (provider: string) => `${API_BASE_URL}/user/social/${provider}/`,
        SOCIAL_AUTH_COMPLETE: () => `${API_BASE_URL}/user/social/complete/`,
    },
    COURSE: {
        BASE: `${API_BASE_URL}/courses/`,
        FEATURED: `${API_BASE_URL}/courses/featured/`,
        POPULAR: `${API_BASE_URL}/courses/popular/`,
        LATEST: `${API_BASE_URL}/courses/latest/`,
        SEARCH: `${API_BASE_URL}/courses/search/`,
        COURSE_BY_SLUG: (slug: string) => `${API_BASE_URL}/courses/${slug}/`,
        ENROLL: (slug: string) => `${API_BASE_URL}/courses/${slug}/enroll/`,
        MODULES: (slug: string) => `${API_BASE_URL}/courses/${slug}/modules/`,
        REVIEWS: (slug: string) => `${API_BASE_URL}/courses/${slug}/reviews/`,
        REVIEW: (slug: string) => `${API_BASE_URL}/courses/${slug}/review/`,
        UPDATE_REVIEW: (slug: string, reviewId: string | number) =>
            `${API_BASE_URL}/courses/${slug}/review/${reviewId}/`,
        CERTIFICATE: (slug: string) => `${API_BASE_URL}/courses/${slug}/certificate/`,
        DISCUSSIONS: (slug: string) => `${API_BASE_URL}/courses/${slug}/discussions/`,
        DISCUSSION: (slug: string, discussionId: string | number) =>
            `${API_BASE_URL}/courses/${slug}/discussions/${discussionId}/`,
        DISCUSSION_REPLIES: (slug: string, discussionId: string | number) =>
            `${API_BASE_URL}/courses/${slug}/discussions/${discussionId}/replies/`,
    },
    MODULE: {
        DETAILS: (moduleId: string | number) => `${API_BASE_URL}/modules/${moduleId}/`,
        LESSONS: (moduleId: string | number) => `${API_BASE_URL}/modules/${moduleId}/lessons/`,
    },
    LESSON: {
        DETAILS: (lessonId: string | number) => `${API_BASE_URL}/lessons/${lessonId}/`,
        COMPLETE: (lessonId: string | number) => `${API_BASE_URL}/lessons/${lessonId}/complete/`,
    },
    USER: {
        ME: `${API_BASE_URL}/user/me/`,
        UPDATE_PROFILE: `${API_BASE_URL}/user/profile/`,
        SUBSCRIPTION: {
            CURRENT: `${API_BASE_URL}/user/subscription/current/`,
            UPGRADE: `${API_BASE_URL}/user/subscription/upgrade/`,
            CANCEL: `${API_BASE_URL}/user/subscription/cancel/`,
        },
        PROGRESS: {
            BASE: `${API_BASE_URL}/user/progress/`,
            COURSE: (courseId: string | number) => `${API_BASE_URL}/user/progress/${courseId}/`,
            STATS: `${API_BASE_URL}/user/progress/stats/`,
        },
        ASSESSMENT_ATTEMPTS: `${API_BASE_URL}/user/assessment-attempts/`,
        ENROLLMENTS: `${API_BASE_URL}/enrollments/`,
    },
    ASSESSMENT: {
        BASE: `${API_BASE_URL}/assessments/`,
        DETAILS: (assessmentId: string | number) => `${API_BASE_URL}/assessments/${assessmentId}/`,
        START: (assessmentId: string | number) => `${API_BASE_URL}/assessments/${assessmentId}/start/`,
        ATTEMPTS: `${API_BASE_URL}/assessment-attempts/`,
        SUBMIT: (attemptId: string | number) =>
            `${API_BASE_URL}/assessment-attempts/${attemptId}/submit/`,
    },
    NOTE: {
        BASE: `${API_BASE_URL}/notes/`,
        DETAIL: (noteId: string | number) => `${API_BASE_URL}/notes/${noteId}/`,
    },
    LAB: {
        BASE: `${API_BASE_URL}/labs/`,
        DETAILS: (labId: string | number) => `${API_BASE_URL}/labs/${labId}/`,
        START: (labId: string | number) => `${API_BASE_URL}/labs/${labId}/start/`,
        SUBMIT: (labId: string | number) => `${API_BASE_URL}/labs/${labId}/submit/`,
    },
    CATEGORY: {
        BASE: `${API_BASE_URL}/categories/`,
        COURSES: (categorySlug: string) =>
            `${API_BASE_URL}/categories/${categorySlug}/courses/`,
    },
    CERTIFICATE: {
        BASE: `${API_BASE_URL}/certificates/`,
        VERIFY: (code: string) => `${API_BASE_URL}/certificates/verify/${code}/`,
    },
    BLOG: {
        POSTS: `${API_BASE_URL}/blog/posts/`,
        POST_BY_SLUG: (slug: string) => `${API_BASE_URL}/blog/posts/${slug}/`,
    },
    SYSTEM: {
        STATUS: `${API_BASE_URL}/system/status/`,
        DB_STATUS: `${API_BASE_URL}/system/db-status/`,
        HEALTH: `${API_BASE_URL}${BASE_PATHS.SYSTEM}/health/`,
        VERSION: `${API_BASE_URL}${BASE_PATHS.SYSTEM}/version/`,
    },
    STATISTICS: {
        PLATFORM: `${API_BASE_URL}/statistics/platform/`,
        USER: `${API_BASE_URL}/statistics/user/`,
        INSTRUCTOR: `${API_BASE_URL}/statistics/instructor/`,
    },
    TESTIMONIAL: {
        BASE: `${API_BASE_URL}/testimonials/`,
        FEATURED: `${API_BASE_URL}/testimonials/featured/`,
    },
    INSTRUCTOR: {
        COURSES: `${API_BASE_URL}/instructor/courses/`,
        MODULES: `${API_BASE_URL}/instructor/modules/`,
        LESSONS: `${API_BASE_URL}/instructor/lessons/`,
        RESOURCES: `${API_BASE_URL}/instructor/resources/`,
        ASSESSMENTS: `${API_BASE_URL}/instructor/assessments/`,
        STATISTICS: `${API_BASE_URL}/instructor/statistics/`,

        // DND session endpoints
        DND: {
            SESSION_START: `${API_BASE_URL}/instructor/dnd/sessions/start/`,
            SESSION_GET: (sessionId: string | number) => `${API_BASE_URL}/instructor/dnd/sessions/${sessionId}/`,
            SESSION_PUBLISH: (sessionId: string | number) => `${API_BASE_URL}/instructor/dnd/sessions/${sessionId}/publish/`,
            REORDER_BLOCKS: `${API_BASE_URL}/instructor/draft_course_content/reorder/`,
        },
    },
};

/**
 * Role-based API routes for new architecture
 * These endpoints follow a cleaner role-based structure
 */
export const API_ROUTES = {
    // Authentication routes (role-based structure)
    AUTH: {
        LOGIN: `${API_BASE_URL}${BASE_PATHS.AUTH}/token/`,
        REFRESH: `${API_BASE_URL}${BASE_PATHS.AUTH}/token/refresh/`,
        REGISTER: `${API_BASE_URL}${BASE_PATHS.AUTH}/register/`,
        CURRENT_USER: `${API_BASE_URL}${BASE_PATHS.AUTH}/me/`,
    },

    // Instructor routes
    INSTRUCTOR: {
        COURSES: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/courses/`,
        MODULES: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/modules/`,
        LESSONS: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/lessons/`,
        RESOURCES: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/resources/`,
        ASSESSMENTS: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/assessments/`,
        STATISTICS: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/statistics/`,

        // DND session routes
        DND: {
            SESSION_START: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/dnd/sessions/start/`,
            SESSION_GET: (sessionId: string) =>
                `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/dnd/sessions/${sessionId}/`,
            SESSION_PUBLISH: (sessionId: string) =>
                `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/dnd/sessions/${sessionId}/publish/`,
            REORDER_BLOCKS: `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}/draft_course_content/reorder/`,
        },
    },

    // Student routes
    STUDENT: {
        COURSES: `${API_BASE_URL}${BASE_PATHS.STUDENT}/courses/`,
        ENROLLMENTS: `${API_BASE_URL}${BASE_PATHS.STUDENT}/enrollments/`,
        PROGRESS: `${API_BASE_URL}${BASE_PATHS.STUDENT}/progress/`,
    },

    // System routes
    SYSTEM: {
        HEALTH: `${API_BASE_URL}${BASE_PATHS.SYSTEM}/health/`,
        VERSION: `${API_BASE_URL}${BASE_PATHS.SYSTEM}/version/`,
    },
} as const;

/**
 * Endpoint builder utilities for dynamic route construction
 */
export const EndpointBuilder = {
    /**
     * Build instructor-specific endpoint
     */
    instructor: (path: string) => `${API_BASE_URL}${BASE_PATHS.INSTRUCTOR}${path}`,

    /**
     * Build student-specific endpoint
     */
    student: (path: string) => `${API_BASE_URL}${BASE_PATHS.STUDENT}${path}`,

    /**
     * Build auth-specific endpoint
     */
    auth: (path: string) => `${API_BASE_URL}${BASE_PATHS.AUTH}${path}`,

    /**
     * Build system-specific endpoint
     */
    system: (path: string) => `${API_BASE_URL}${BASE_PATHS.SYSTEM}${path}`,
} as const;

/**
 * Type definitions for better TypeScript support
 */
export type EndpointFunction = (...args: (string | number)[]) => string;
export type EndpointValue = string | EndpointFunction;

// Export base paths for external use
export { BASE_PATHS };
