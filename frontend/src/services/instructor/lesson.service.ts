/**
 * File: src/services/instructor/lesson.service.ts
 * Version: 1.1.0
 * Date: 2025-06-25 10:02:06
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 10:02:06 UTC
 *
 * Instructor Lesson Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific lesson operations
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
import {
    handleError,
    invalidateCache,
    log,
    logError
} from './helpers';
import { Lesson, RequestOptions } from './types';

export const getLessons = async (moduleId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get('/instructor/lessons/', {
                    params: { module: moduleId },
                    ...requestOptions,
                }),
            `Failed to fetch lessons for module ${moduleId}`,
            {
                url: `/instructor/lessons/?module=${moduleId}`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return Array.isArray(response) ? response : response?.results || [];
    } catch (error) {
        logError(`Error fetching lessons for module ${moduleId}:`, error);
        throw handleError(error);
    }
};

export const getLesson = async (lessonId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get(`/instructor/lessons/${lessonId}/`, requestOptions),
            `Failed to fetch lesson ${lessonId}`,
            {
                url: `/instructor/lessons/${lessonId}/`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error fetching lesson ${lessonId}:`, error);
        throw handleError(error);
    }
};

// Function overload signatures for better type safety
export async function createLesson(lessonData: Lesson, options?: RequestOptions): Promise<any>;
export async function createLesson(moduleId: string | number, lessonData: Omit<Lesson, 'module'>, options?: RequestOptions): Promise<any>;

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export async function createLesson(
    moduleIdOrData: string | number | Lesson,
    lessonDataOrOptions?: Omit<Lesson, 'module'> | RequestOptions,
    optionsOrNothing?: RequestOptions
): Promise<any> {
    // Handle the case where first parameter is the lesson data object
    if (moduleIdOrData && typeof moduleIdOrData === 'object') {
        const lessonData = moduleIdOrData as Lesson;
        const options = lessonDataOrOptions as RequestOptions || {};

        if (lessonData.access_level === 'guest' && !lessonData.guest_content?.trim()) {
            throw new Error('Guest preview content is required for Guest access level');
        }

        log('Creating lesson with single object parameter');
        return handleRequest(
            async requestOptions =>
                await apiClient.post('/instructor/lessons/', lessonData, requestOptions),
            'Failed to create lesson',
            {
                url: '/instructor/lessons/',
                ...options,
            }
        );
    }
    // Handle the case where module ID is separate from lesson data
    else {
        const moduleId = moduleIdOrData;
        const lessonData = lessonDataOrOptions as Omit<Lesson, 'module'>;
        const options = optionsOrNothing || {};

        const completeData = {
            ...lessonData,
            module: moduleId,
        };

        if (completeData.access_level === 'guest' && !completeData.guest_content?.trim()) {
            throw new Error('Guest preview content is required for Guest access level');
        }

        try {
            log(`Creating lesson for module ${moduleId}`);
            const response = await handleRequest(
                async requestOptions =>
                    await apiClient.post('/instructor/lessons/', completeData, requestOptions),
                'Failed to create lesson',
                {
                    url: '/instructor/lessons/',
                    ...options,
                }
            );

            if (moduleId) {
                invalidateCache(`/instructor/lessons/?module=${moduleId}`);
            }

            return response;
        } catch (error) {
            logError('Error creating lesson:', error);
            throw handleError(error);
        }
    }
}

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const updateLesson = async (lessonId: string | number, lessonData: Partial<Lesson>, options: RequestOptions = {}) => {
    if (lessonData.access_level === 'guest' && !lessonData.guest_content?.trim()) {
        throw new Error('Guest preview content is required for Guest access level');
    }

    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.put(`/instructor/lessons/${lessonId}/`, lessonData, requestOptions),
            `Failed to update lesson ${lessonId}`,
            {
                url: `/instructor/lessons/${lessonId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/lessons/${lessonId}/`);
        if (lessonData.module) {
            invalidateCache(`/instructor/lessons/?module=${lessonData.module}`);
        }

        return response;
    } catch (error) {
        logError(`Error updating lesson ${lessonId}:`, error);
        throw handleError(error);
    }
};

export const deleteLesson = async (lessonId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.delete(`/instructor/lessons/${lessonId}/`, requestOptions),
            `Failed to delete lesson ${lessonId}`,
            {
                url: `/instructor/lessons/${lessonId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/lessons/${lessonId}/`);
        invalidateCache('/instructor/lessons/');

        return response;
    } catch (error) {
        logError(`Error deleting lesson ${lessonId}:`, error);
        throw handleError(error);
    }
};

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const updateLessonOrder = async (moduleId: string | number, lessonsOrder: Array<string | number>, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post(
                    `/instructor/modules/${moduleId}/lessons/reorder/`,
                    { lessons: lessonsOrder },
                    requestOptions
                ),
            'Failed to update lesson order',
            {
                url: `/instructor/modules/${moduleId}/lessons/reorder/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/modules/${moduleId}/`);
        invalidateCache(`/instructor/lessons/?module=${moduleId}`);

        return response;
    } catch (error) {
        logError('Error updating lesson order:', error);
        throw handleError(error);
    }
};

export const getInstructorLessons = async (options: RequestOptions = {}) => {
    return handleRequest(
        async requestOptions =>
            await apiClient.get('/instructor/lessons/', requestOptions),
        'Failed to fetch instructor lessons',
        {
            url: '/instructor/lessons/',
            enableCache: true,
            cacheTime: 30000,
            ...options,
        }
    );
};
