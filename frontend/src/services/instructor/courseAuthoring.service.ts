/**
 * File: src/services/instructor/courseAuthoring.service.ts
 * Version: 1.2.0
 * Date: 2025-06-25 09:31:31
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 09:31:31 UTC
 *
 * Instructor Course Authoring Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific course CRUD operations
 *
 * Enhanced version incorporating improvements from v1.1.0:
 * - Better draft course handling in determineUrl and getCourse
 * - Improved parameter handling in getAllCourses
 * - Enhanced content-type headers for file uploads
 * - Better headers handling in checkCourseTitle and publishCourse
 * - More robust error handling and logging
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
import {
    buildFormData,
    handleError,
    hasFileUploads,
    invalidateCache,
    isSlug,
    log,
    logError,
    prepareCoursePayload,
    sanitizeCourseData,
    validateFile
} from './helpers';

// Helper function to determine URL from identifier (slug or ID)
// Enhanced: Forward includeDrafts parameter to getAllCourses for better draft handling
const determineUrl = async (identifier: string | number, options = {}) => {
    // Check if the identifier is a slug - with updated logic that considers numeric strings carefully
    if (isSlug(String(identifier))) {
        return `/instructor/courses/${identifier}/`;
    } else {
        // Pull includeDrafts from options if present and ensure draft courses are included
        const getAllCoursesOptions = {
            enableCache: true,
            ...options,
            // Make sure we include draft courses in the lookup
            params: {
                ...(options?.params || {}),
                include_drafts: true,
                include_all: true,
            }
        };

        const courses = await getAllCourses(getAllCoursesOptions);

        const coursesList = courses.results || courses;
        const course = Array.isArray(coursesList)
            ? coursesList.find(c => c.id?.toString() === identifier?.toString())
            : Object.values(coursesList).find(c => c.id?.toString() === identifier?.toString());

        if (course?.slug) {
            return `/instructor/courses/${course.slug}/`;
        } else {
            throw new Error(`Course with ID ${identifier} not found`);
        }
    }
};

export const getAllCourses = async (options = {}) => {
    try {
        log('[API] Fetching instructor courses...');

        // Enhanced: Extract params from options or use defaults for better flexibility
        const params = options?.params || { include_drafts: true, include_all: true };

        const response = await handleRequest(
            async (requestOptions) => {
                return await apiClient.get('/instructor/courses/', {
                    params,
                    ...requestOptions
                });
            },
            'Failed to fetch courses',
            {
                url: '/instructor/courses/',
                enableCache: true,
                ...options
            }
        );

        log('[API] Courses data:', response);

        return response.results || response;
    } catch (error) {
        logError('[API] Error fetching courses:', error);
        throw handleError(error);
    }
};

export const getCourse = async (identifier: string | number, options = {}) => {
    if (isSlug(String(identifier))) {
        return getCourseBySlug(String(identifier), options);
    }

    try {
        // Enhanced: Ensure draft courses are included in the lookup
        const getAllCoursesOptions = {
            enableCache: true,
            ...options,
            params: {
                ...(options?.params || {}),
                include_drafts: true,
                include_all: true,
            }
        };

        const courses = await getAllCourses(getAllCoursesOptions);

        const coursesList = courses.results || courses;

        if (!coursesList || typeof coursesList !== 'object') {
            throw new Error(`Invalid courses data received for ID ${identifier}`);
        }

        const course = Array.isArray(coursesList)
            ? coursesList.find(c => c.id?.toString() === identifier?.toString())
            : Object.values(coursesList).find(c => c.id?.toString() === identifier?.toString());

        if (course?.slug) {
            return getCourseBySlug(course.slug, options);
        } else {
            throw new Error(`Course with ID ${identifier} not found`);
        }
    } catch (error) {
        if (error.name === 'AbortError') throw error;
        logError(`Failed to fetch course using ID mapping: ${error.message}`);
        throw handleError(error);
    }
};

export const getCourseBySlug = async (slug: string, options = {}) => {
    if (!isSlug(slug)) {
        throw new Error(`Invalid slug format: ${slug}`);
    }

    log(`Instructor service: Getting course with slug: ${slug}`);

    try {
        const courseData = await handleRequest(
            async requestOptions => {
                log(`Making instructor API request to: /instructor/courses/${slug}/`);
                return await apiClient.get(`/instructor/courses/${slug}/`, requestOptions);
            },
            `Failed to fetch course by slug: ${slug}`,
            {
                url: `/instructor/courses/${slug}/`,
                ...options,
            }
        );

        return courseData;
    } catch (error) {
        if (error.name === 'AbortError') throw error;
        logError(`Error fetching from instructor endpoint: ${error.message}`);

        try {
            log('Falling back to regular course endpoint');
            const fallbackController = new AbortController();
            const fallbackOptions = {
                ...options,
                abortController: fallbackController,
            };

            const fallbackData = await handleRequest(
                async requestOptions =>
                    await apiClient.get(`/courses/${slug}/`, requestOptions),
                `Failed to fetch course by slug (fallback): ${slug}`,
                {
                    url: `/courses/${slug}/`,
                    skipAuthCheck: true,
                    ...fallbackOptions,
                }
            );

            return fallbackData;
        } catch (fallbackError) {
            if (fallbackError.name === 'AbortError') throw fallbackError;
            logError(`Fallback course endpoint also failed: ${fallbackError.message}`);
            throw handleError(error);
        }
    }
};

export const createCourse = async (courseData: any, options = {}) => {
    try {
        const processedData = prepareCoursePayload(courseData);
        const hasFilesUpload = hasFileUploads(processedData);

        let requestData;
        let headers = {};

        if (hasFilesUpload) {
            if (processedData.thumbnail && processedData.thumbnail instanceof File) {
                const validation = validateFile(processedData.thumbnail, 'image');
                if (!validation.isValid) {
                    throw new Error(`Thumbnail validation failed: ${validation.error}`);
                }
            }
            requestData = buildFormData(processedData);
            // Enhanced: Explicit content-type header for file uploads
            headers['Content-Type'] = 'multipart/form-data';
        } else {
            requestData = sanitizeCourseData(processedData);
            headers['Content-Type'] = 'application/json';
        }

        const response = await handleRequest(
            async requestOptions => {
                try {
                    return await apiClient.post('/instructor/courses/', requestData, {
                        headers,
                        ...requestOptions,
                    });
                } catch (error) {
                    if (error.response?.status === 400 && error.response?.data) {
                        logError('Course creation validation errors:', {
                            status: error.response.status,
                            data: error.response.data,
                            serializedData: hasFilesUpload ? 'FormData (cannot be inspected)' : JSON.stringify(requestData),
                            headers,
                        });
                    }
                    logError('API request failed:', error);
                    throw error;
                }
            },
            'Failed to create course',
            {
                url: '/instructor/courses/',
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError('Error creating course:', error);
        throw handleError(error);
    }
};

export const updateCourse = async (identifier: string | number, courseData: any, partial = true, options = {}) => {
    if (!identifier) {
        throw new Error('Course ID or slug is required for update');
    }

    if (!isSlug(String(identifier)) && !Number.isInteger(Number(identifier))) {
        throw new Error('Invalid course identifier provided');
    }

    try {
        const processedData = prepareCoursePayload(courseData);
        const hasFilesUpload = hasFileUploads(processedData);

        let requestData;
        let headers = {};

        if (hasFilesUpload) {
            if (processedData.thumbnail && processedData.thumbnail instanceof File) {
                const validation = validateFile(processedData.thumbnail, 'image');
                if (!validation.isValid) {
                    throw new Error(`Thumbnail validation failed: ${validation.error}`);
                }
            }
            requestData = buildFormData(processedData);
            // Enhanced: Explicit content-type header for file uploads
            headers['Content-Type'] = 'multipart/form-data';
        } else {
            requestData = sanitizeCourseData(processedData, partial);
            headers['Content-Type'] = 'application/json';
        }

        const url = await determineUrl(identifier, options);
        const method = partial ? 'patch' : 'put';

        log(`Making ${method.toUpperCase()} request to ${url}`);

        const response = await handleRequest(
            async requestOptions =>
                await apiClient[method](url, requestData, {
                    headers,
                    ...requestOptions,
                }),
            `Failed to update course ${identifier}`,
            {
                url,
                ...options,
            }
        );

        invalidateCache(url);
        invalidateCache('/instructor/courses/');

        return response;
    } catch (error) {
        if (error.name === 'AbortError') throw error;

        logError(`Failed to update course:`, error);
        if (error.response?.status === 400) {
            logError('Validation error details:', {
                data: error.response.data,
                thumbnail_type: courseData.thumbnail ? typeof courseData.thumbnail : 'undefined',
                thumbnail_is_array: courseData.thumbnail ? Array.isArray(courseData.thumbnail) : false,
                requirements_type: courseData.requirements ? typeof courseData.requirements : 'undefined',
                skills_type: courseData.skills ? typeof courseData.skills : 'undefined',
            });
        }

        throw handleError(error);
    }
};

export const checkCourseTitle = async (title: string) => {
    try {
        const response = await apiClient.post('/instructor/courses/check_title/', { title }, {
            // Enhanced: Explicit headers for consistency
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    } catch (error) {
        logError('Error checking course title:', error);
        return { is_unique: true };
    }
};

export const deleteCourse = async (identifier: string | number, options = {}) => {
    if (!identifier) {
        throw new Error('Course ID or slug is required for deletion');
    }

    if (!isSlug(String(identifier)) && !Number.isInteger(Number(identifier))) {
        throw new Error('Invalid course identifier provided for deletion');
    }

    try {
        log(`Attempting to delete course: ${identifier}`);
        const url = await determineUrl(identifier, options);

        const response = await handleRequest(
            async requestOptions => await apiClient.delete(url, requestOptions),
            `Failed to delete course ${identifier}`,
            {
                url,
                ...options,
            }
        );

        invalidateCache('/instructor/courses/');
        return response;
    } catch (error) {
        if (error.name === 'AbortError') throw error;
        logError(`Course deletion failed: ${error.message}`);
        throw handleError(error);
    }
};

export const publishCourse = async (identifier: string | number, publishStatus = true, options = {}) => {
    let courseId = identifier;

    if (!isSlug(String(identifier)) && isNaN(Number(identifier))) {
        log(`Non-standard identifier format: ${identifier}. Attempting to sanitize.`);
        courseId = String(identifier).replace(/[^a-zA-Z0-9_\-.]/g, '');
        log(`Sanitized identifier: ${courseId}`);
    }

    try {
        log(`Attempting to ${publishStatus ? 'publish' : 'unpublish'} course: ${courseId}`);

        const response = await handleRequest(
            async requestOptions =>
                await apiClient.put(
                    `/instructor/courses/${identifier}/publish/`,
                    { is_published: publishStatus },
                    {
                        // Enhanced: Explicit headers for consistency
                        headers: { 'Content-Type': 'application/json' },
                        ...requestOptions
                    }
                ),
            `Failed to ${publishStatus ? 'publish' : 'unpublish'} course`,
            {
                url: `/instructor/courses/${identifier}/publish/`,
                returnRawResponse: true,
                ...options,
            }
        );

        invalidateCache(`/instructor/courses/${identifier}/`);
        invalidateCache('/instructor/courses/');

        log(`Successfully ${publishStatus ? 'published' : 'unpublished'} course: ${identifier}`);

        return {
            ...response,
            id: response?.id || identifier,
            slug: response?.slug || identifier,
            identifier: identifier,
        };
    } catch (error) {
        logError(`Course ${publishStatus ? 'publish' : 'unpublish'} failed:`, error);

        let errorMessage = `Failed to ${publishStatus ? 'publish' : 'unpublish'} course`;

        if (error.status === 403) {
            errorMessage = `You don't have permission to ${publishStatus ? 'publish' : 'unpublish'} this course`;
        } else if (error.status === 400) {
            errorMessage = `Course cannot be ${publishStatus ? 'published' : 'unpublished'} due to missing requirements`;

            if (error.details && typeof error.details === 'object') {
                if (error.details.content_required) {
                    errorMessage = 'Course needs at least one module with content before publishing';
                } else if (error.details.missing_fields) {
                    errorMessage = `Required fields missing: ${error.details.missing_fields.join(', ')}`;
                } else if (error.details.missing_certificate && publishStatus) {
                    errorMessage = 'Certificate settings required for premium course publishing';
                }
            }
        }

        throw {
            ...error,
            message: errorMessage,
        };
    }
};

export const getCourseAnalytics = async (identifier: string | number, options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get(`/instructor/courses/${identifier}/analytics/`, requestOptions),
            `Failed to fetch course analytics for ${identifier}`,
            {
                url: `/instructor/courses/${identifier}/analytics/`,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error fetching course analytics for ${identifier}:`, error);
        throw handleError(error);
    }
};

export const duplicateCourse = async (identifier: string | number, options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post(`/instructor/courses/${identifier}/duplicate/`, {}, {
                    // Enhanced: Explicit headers for consistency
                    headers: { 'Content-Type': 'application/json' },
                    ...requestOptions
                }),
            `Failed to duplicate course ${identifier}`,
            {
                url: `/instructor/courses/${identifier}/duplicate/`,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error duplicating course ${identifier}:`, error);
        throw handleError(error);
    }
};
