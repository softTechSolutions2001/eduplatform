/**
 * File: src/services/instructor/resource.service.ts
 * Version: 1.1.0
 * Date: 2025-06-25 09:31:31
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 09:31:31 UTC
 *
 * Instructor Resource Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific resource operations
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
// A-1 fix: Import from transformData directly instead of re-exporting through helpers
import { camelToSnake, mapKeys, objectToSnakeFormData } from '../../utils/transformData';
import {
    handleError,
    invalidateCache,
    logError,
    validateFile
} from './helpers';

export interface UploadProgressEvent {
    loaded: number;
    total: number;
    percentCompleted: number;
    timestamp: number;
}

export type ProgressCallback = (progress: UploadProgressEvent) => void;

// B-6 fix: Use handleRequest for uploadResource to ensure consistent error handling
export const uploadResource = async (
    { file, title, ...meta }: { file: File; title: string;[key: string]: any },
    progressCallback?: ProgressCallback,
    options = {}
) => {
    try {
        const fd = objectToSnakeFormData({ file, title, ...meta });

        if (file && file instanceof File) {
            const validation = validateFile(file, 'resource');
            if (!validation.isValid) {
                throw new Error(`File validation failed: ${validation.error}`);
            }
        }

        return await handleRequest(
            async (requestOptions) => {
                return await apiClient.post('/instructor/resources/', fd, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: progressCallback
                        ? progressEvent => {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            );
                            progressCallback({
                                ...progressEvent,
                                percentCompleted,
                                loaded: progressEvent.loaded,
                                total: progressEvent.total,
                                timestamp: Date.now(),
                            });
                        }
                        : undefined,
                    ...requestOptions
                });
            },
            'Failed to upload resource',
            {
                url: '/instructor/resources/',
                returnRawResponse: true,
                ...options,
            }
        );
    } catch (error) {
        logError('Error uploading resource:', error);
        throw handleError(error);
    }
};

export const getPresignedUrl = async (
    { fileName, contentType }: { fileName: string; contentType: string },
    options = {}
) => {
    if (!fileName || !contentType) {
        throw new Error('File name and content type are required for presigned URL');
    }

    const payload = mapKeys({ fileName, contentType }, camelToSnake);

    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post('/instructor/resources/presigned-url/', payload, {
                    headers: { 'Content-Type': 'application/json' },
                    ...requestOptions
                }),
            'Failed to get presigned URL for file upload',
            {
                url: '/instructor/resources/presigned-url/',
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError('Error getting presigned URL:', error);
        throw handleError(error);
    }
};

export const confirmResourceUpload = async (
    { resourceId, storageKey, filesize, mimeType, premium = false }: {
        resourceId: string | number;
        storageKey: string;
        filesize: number;
        mimeType: string;
        premium?: boolean;
    },
    options = {}
) => {
    try {
        const payload = mapKeys(
            { resourceId, storageKey, filesize, mimeType, premium },
            camelToSnake
        );

        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post('/instructor/resources/confirm-upload/', payload, {
                    headers: { 'Content-Type': 'application/json' },
                    ...requestOptions
                }),
            'Failed to confirm resource upload',
            {
                url: '/instructor/resources/confirm-upload/',
                ...options,
            }
        );

        if (resourceId) {
            invalidateCache(`/instructor/resources/?lesson=${resourceId}`);
        }

        return response;
    } catch (error) {
        logError('Error confirming resource upload:', error);
        throw handleError(error);
    }
};

export const getResources = async (lessonId: string | number, options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get('/instructor/resources/', {
                    params: { lesson: lessonId },
                    ...requestOptions,
                }),
            `Failed to fetch resources for lesson ${lessonId}`,
            {
                url: `/instructor/resources/?lesson=${lessonId}`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error fetching resources for lesson ${lessonId}:`, error);
        throw handleError(error);
    }
};

export const deleteResource = async (resourceId: string | number, options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.delete(`/instructor/resources/${resourceId}/`, requestOptions),
            `Failed to delete resource ${resourceId}`,
            {
                url: `/instructor/resources/${resourceId}/`,
                ...options,
            }
        );

        invalidateCache('/instructor/resources/');
        return response;
    } catch (error) {
        logError(`Error deleting resource ${resourceId}:`, error);
        throw handleError(error);
    }
};

export const purgeResource = async (resourceId: string | number, options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.delete(`/instructor/resources/${resourceId}/purge/`, requestOptions),
            `Failed to purge resource ${resourceId}`,
            {
                url: `/instructor/resources/${resourceId}/purge/`,
                ...options,
            }
        );

        invalidateCache('/instructor/resources/');
        return response;
    } catch (error) {
        logError(`Error purging resource ${resourceId}:`, error);
        throw handleError(error);
    }
};
