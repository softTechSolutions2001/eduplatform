// File Path: src/courseBuilder/api/dndSession.ts
// Date Created: 2025-06-24 08:50:00
// Current Date and Time (UTC): 2025-06-25 04:25:11
// Author: saiacupunctureFolllow
// Version: 1.3.0
// Last Modified: 2025-06-25 04:25:11 UTC

// ✅ CORRECT - imports the actual Axios instance
import { apiClient } from "@/services/api";
import { API_ENDPOINTS } from "@/services/http/endpoints";
import { CourseData } from "../store/schema";

interface SessionResponse {
    session_id: string;
}

interface PublishResponse {
    course_id: number;
    slug: string;
}

interface ReorderRequest {
    items: { id: number; order: number }[];
}

interface ApiError {
    message: string;
    code?: string;
    details?: Record<string, any>;
}

// Enhanced API service with retry and error handling
export class BuilderApiService {
    private maxRetries = 3;

    /**
     * Create a new drag-and-drop course builder session
     * @returns Session ID string
     */
    async createSession(): Promise<string> {
        try {
            const { data } = await this.executeWithRetry<SessionResponse>(
                () => apiClient.post(API_ENDPOINTS.INSTRUCTOR.DND.SESSION_START)
            );
            return data.session_id;
        } catch (error) {
            this.handleApiError(error, "Failed to create session");
            throw error;
        }
    }

    /**
     * Update the order of multiple content blocks in one operation
     * @param items Array of blocks with their new order values
     */
    async reorderBlocks(items: { id: number; order: number }[]): Promise<void> {
        try {
            await this.executeWithRetry<void>(
                () => apiClient.patch(API_ENDPOINTS.INSTRUCTOR.DND.REORDER_BLOCKS, { items })
            );
        } catch (error) {
            this.handleApiError(error, "Failed to reorder content blocks");
            throw error;
        }
    }

    /**
     * Publish a course from a drag-and-drop session
     * @param sessionId The session identifier
     * @param payload Optional publish settings
     * @returns The new course ID and slug
     */
    async publishSession(
        sessionId: string,
        payload = {}
    ): Promise<PublishResponse> {
        try {
            const { data } = await this.executeWithRetry<PublishResponse>(
                () => apiClient.post(API_ENDPOINTS.INSTRUCTOR.DND.SESSION_PUBLISH(sessionId), payload)
            );
            return data;
        } catch (error) {
            this.handleApiError(error, "Failed to publish session");
            throw error;
        }
    }

    /**
     * Get an existing drag-and-drop session by ID
     * @param sessionId The session identifier
     * @returns The session data
     */
    async getSession(sessionId: string): Promise<CourseData> {
        try {
            const { data } = await this.executeWithRetry<CourseData>(
                () => apiClient.get(API_ENDPOINTS.INSTRUCTOR.DND.SESSION_GET(sessionId))
            );
            return data;
        } catch (error) {
            this.handleApiError(error, "Failed to fetch session");
            throw error;
        }
    }

    /**
     * Execute an API call with automatic retry logic
     * @param apiCall Function that returns a Promise for the API call
     * @returns Promise resolving to the API response
     */
    private async executeWithRetry<T>(
        apiCall: () => Promise<{ data: T }>,
        retries = 0
    ): Promise<{ data: T }> {
        try {
            return await apiCall();
        } catch (error: any) {
            // Don't retry on 4xx client errors (except 429)
            if (error.response && error.response.status >= 400 &&
                error.response.status < 500 &&
                error.response.status !== 429) {
                throw error;
            }

            if (retries < this.maxRetries) {
                // Exponential backoff with jitter to prevent thundering herd
                const baseDelay = Math.pow(2, retries) * 1000;
                const jitter = Math.random() * 1000;
                const delay = baseDelay + jitter;
                await new Promise((resolve) => setTimeout(resolve, delay));
                return this.executeWithRetry(apiCall, retries + 1);
            }
            throw error;
        }
    }

    /**
     * Standardized error handling for API errors
     * @param error The caught error
     * @param defaultMessage Default message to use
     */
    private handleApiError(error: any, defaultMessage: string): void {
        const apiError: ApiError = {
            message: defaultMessage,
            details: {},
        };

        if (error.response) {
            apiError.code = `HTTP_${error.response.status}`;
            apiError.message = error.response.data?.detail ||
                error.response.data?.message ||
                defaultMessage;
            apiError.details = error.response.data || {};
        } else if (error.request) {
            // Network error
            apiError.code = 'NETWORK_ERROR';
            apiError.message = 'Network request failed';
        } else {
            // Other errors
            apiError.code = 'UNKNOWN_ERROR';
            apiError.message = error.message || defaultMessage;
        }

        // Log to monitoring service in production
        console.error("API Error:", apiError);
    }
}

// Create and export singleton instance
export const builderApiService = new BuilderApiService();

// Legacy export functions for backward compatibility
export async function createSession(): Promise<string> {
    return builderApiService.createSession();
}

export async function reorderBlocks(items: { id: number; order: number }[]): Promise<void> {
    return builderApiService.reorderBlocks(items);
}

export async function publishSession(sessionId: string, payload = {}): Promise<number> {
    const response = await builderApiService.publishSession(sessionId, payload);
    return response.course_id;
}

export async function getSession(sessionId: string): Promise<CourseData> {
    return builderApiService.getSession(sessionId);
}
