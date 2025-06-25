/**
 * File: src/services/instructor/module.service.ts
 * Version: 1.1.0
 * Date: 2025-06-25 10:02:06
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 10:02:06 UTC
 *
 * Instructor Module Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific module operations
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
import {
    handleError,
    invalidateCache,
    isSlug,
    logError
} from './helpers';
import { Module, RequestOptions } from './types';

export const getModules = async (courseId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get('/instructor/modules/', {
                    params: { course: courseId },
                    ...requestOptions,
                }),
            `Failed to fetch modules for course ${courseId}`,
            {
                url: `/instructor/modules/?course=${courseId}`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return Array.isArray(response) ? response : response?.results || [];
    } catch (error) {
        logError(`Error fetching modules for course ${courseId}:`, error);
        throw handleError(error);
    }
};

export const getModule = async (moduleId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get(`/instructor/modules/${moduleId}/`, requestOptions),
            `Failed to fetch module ${moduleId}`,
            {
                url: `/instructor/modules/${moduleId}/`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error fetching module ${moduleId}:`, error);
        throw handleError(error);
    }
};

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const createModule = async (moduleData: Module, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post('/instructor/modules/', moduleData, requestOptions),
            'Failed to create module',
            {
                url: '/instructor/modules/',
                ...options,
            }
        );

        if (moduleData.course) {
            invalidateCache(`/instructor/modules/?course=${moduleData.course}`);
        }

        return response;
    } catch (error) {
        logError('Error creating module:', error);
        throw handleError(error);
    }
};

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const updateModule = async (moduleId: string | number, moduleData: Partial<Module>, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.put(`/instructor/modules/${moduleId}/`, moduleData, requestOptions),
            `Failed to update module ${moduleId}`,
            {
                url: `/instructor/modules/${moduleId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/modules/${moduleId}/`);
        if (moduleData.course) {
            invalidateCache(`/instructor/modules/?course=${moduleData.course}`);
        }

        return response;
    } catch (error) {
        logError(`Error updating module ${moduleId}:`, error);
        throw handleError(error);
    }
};

export const deleteModule = async (moduleId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.delete(`/instructor/modules/${moduleId}/`, requestOptions),
            `Failed to delete module ${moduleId}`,
            {
                url: `/instructor/modules/${moduleId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/modules/${moduleId}/`);
        invalidateCache('/instructor/modules/');

        return response;
    } catch (error) {
        logError(`Error deleting module ${moduleId}:`, error);
        throw handleError(error);
    }
};

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const updateModuleOrder = async (courseSlug: string, modulesOrder: Array<string | number>, options: RequestOptions = {}) => {
    try {
        if (!isSlug(courseSlug)) {
            throw new Error(`Invalid slug format for module reordering: ${courseSlug}`);
        }

        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post(
                    `/instructor/courses/${courseSlug}/modules/reorder/`,
                    { modules: modulesOrder },
                    requestOptions
                ),
            'Failed to update module order',
            {
                url: `/instructor/courses/${courseSlug}/modules/reorder/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/courses/${courseSlug}/`);
        invalidateCache('/instructor/modules/');

        return response;
    } catch (error) {
        logError('Error updating module order:', error);
        throw handleError(error);
    }
};
