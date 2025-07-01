/**
 * File: src/services/domains/course.service.ts
 * Version: 1.0.2
 * Modified: 2025-06-26
 * Author: softTechSolutions2001
 *
 * Course service for operations related to course management
 */

import { logWarning } from '../../utils/logger'; // Added missing import
import { apiClient } from '../http/apiClient';
import { ALLOW_MOCK_FALLBACK, DEBUG_MODE } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { contentCache, createFormData } from '../utils/apiUtils';
import { handlePublicRequest, handleRequest } from '../utils/handleRequest';

export const courseService = {
    getAllCourses: async (params = {}) => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.COURSE.BASE, { params }),
            'Failed to fetch courses'
        );
    },

    // Added missing method from original api.js
    getPopularCourses: async (limit = 10) => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.COURSE.POPULAR, { params: { limit } }),
            'Failed to fetch popular courses'
        );
    },

    // Added missing method from original api.js
    getLatestCourses: async (limit = 10) => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.COURSE.LATEST, { params: { limit } }),
            'Failed to fetch latest courses'
        );
    },

    getCourseBySlug: async slug => {
        console.log(`Getting course by slug: ${slug}`);

        try {
            return await handleRequest(
                async () =>
                    await apiClient.get(API_ENDPOINTS.COURSE.COURSE_BY_SLUG(slug)),
                `Failed to fetch course ${slug}`
            );
        } catch (error) {
            console.error(`Error fetching course: ${error.message}`);
            throw error;
        }
    },

    enrollInCourse: async slug => {
        return handleRequest(
            async () => await apiClient.post(API_ENDPOINTS.COURSE.ENROLL(slug)),
            `Failed to enroll in course ${slug}`
        );
    },

    createCourse: async (courseData, thumbnailFile) => {
        const formData = thumbnailFile
            ? prepareCourseFormData(courseData, thumbnailFile)
            : createFormData(courseData);

        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.COURSE.BASE, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }),
            'Failed to create course'
        );
    },

    updateCourse: async (slug, courseData, thumbnailFile) => {
        const formData = thumbnailFile
            ? prepareCourseFormData(courseData, thumbnailFile)
            : createFormData(courseData);

        return handleRequest(
            async () =>
                await apiClient.put(
                    API_ENDPOINTS.COURSE.COURSE_BY_SLUG(slug),
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                        },
                    }
                ),
            `Failed to update course ${slug}`
        );
    },

    getCourseModules: async slug => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.COURSE.MODULES(slug)),
            `Failed to fetch modules for course ${slug}`
        );
    },

    getModuleDetails: async moduleId => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.MODULE.DETAILS(moduleId)),
            `Failed to fetch module details for module ${moduleId}`
        );
    },

    getModuleLessons: async moduleId => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.MODULE.LESSONS(moduleId)),
            `Failed to fetch lessons for module ${moduleId}`
        );
    },

    getLessonDetails: async (
        lessonId,
        isPublicContent = false,
        isAuthenticated = false,
        options = {}
    ) => {
        if (typeof isPublicContent === 'object') {
            options = isPublicContent;
            isPublicContent = options.isPublicContent || false;
            isAuthenticated = options.isAuthenticated || false;
        }

        const moduleData = options.moduleData || null;
        const moduleId = options.moduleId || null;
        const signal = options.signal || null;

        console.log(
            `Getting lesson details for ${lessonId}, isPublic: ${isPublicContent}, isAuth: ${isAuthenticated}, hasSignal: ${!!signal}`
        );

        const MAX_RETRIES = 2;
        const RETRY_DELAY = 1000;
        const useLocalStorage =
            typeof window !== 'undefined' && window.localStorage;

        const startTime = performance.now();
        let source = 'api';

        let cachedContent = null;
        let fallbackContent = null;

        if (useLocalStorage) {
            try {
                const contentCacheKey = `content_cache_lesson_${lessonId}`;
                cachedContent = contentCache.get(contentCacheKey);

                if (cachedContent) {
                    fallbackContent = cachedContent;
                    source = 'cache';
                    console.log('Using cached lesson content');
                }

                if (!cachedContent && moduleId) {
                    const moduleContentKey = `content_cache_module_${moduleId}`;
                    const moduleCachedData = contentCache.get(moduleContentKey);

                    if (moduleCachedData?.lessons) {
                        const cachedLesson = moduleCachedData.lessons.find(
                            l => l.id.toString() === lessonId.toString()
                        );
                        if (cachedLesson && cachedLesson.content) {
                            console.log('Using cached lesson content from module cache');
                            cachedContent = cachedLesson;
                            fallbackContent = cachedLesson;
                            source = 'module-cache';
                        }
                    }
                }
            } catch (error) {
                console.error('Error accessing cached lesson content:', error);
            }
        }

        const fetchWithRetry = async fetchFn => {
            let lastError = null;

            for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
                try {
                    if (attempt > 0) {
                        console.log(`Retry attempt ${attempt} for lesson ${lessonId}`);
                        await new Promise(resolve =>
                            setTimeout(resolve, RETRY_DELAY * attempt)
                        );
                    }

                    return await fetchFn();
                } catch (error) {
                    lastError = error;

                    if (error.name === 'AbortError' || error.message === 'canceled') {
                        console.log(`Lesson fetch aborted for ${lessonId}`);
                        throw error;
                    }

                    console.error(
                        `Attempt ${attempt} failed for lesson ${lessonId}:`,
                        error
                    );

                    if (attempt === MAX_RETRIES) {
                        if (fallbackContent) {
                            console.warn(
                                `Using fallback content after ${MAX_RETRIES + 1} failed attempts`
                            );
                            return fallbackContent;
                        }
                        throw error;
                    }
                }
            }
        };

        try {
            if (isAuthenticated) {
                console.log('Using authenticated request for lesson content');

                const response = await fetchWithRetry(async () => {
                    const result = await handleRequest(async () => {
                        const requestOptions = {
                            headers: {
                                ...apiClient.defaults.headers,
                                'X-Force-Auth': 'true',
                            },
                        };

                        if (signal) {
                            requestOptions.signal = signal;
                        }

                        return await apiClient.get(
                            API_ENDPOINTS.LESSON.DETAILS(lessonId),
                            requestOptions
                        );
                    }, `Failed to fetch lesson details for lesson ${lessonId}`);
                    return result;
                });

                if (
                    cachedContent?.content &&
                    response.content &&
                    cachedContent.content.length > response.content.length
                ) {
                    console.log('Using cached content (longer than API response)');
                    response.content = cachedContent.content;
                    source = 'cache+api';
                } else {
                    source = 'api';
                }

                if (DEBUG_MODE) {
                    const duration = performance.now() - startTime;
                    console.log(
                        `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
                    );
                }

                if (useLocalStorage && response.content) {
                    const contentCacheKey = `content_cache_lesson_${lessonId}`;
                    contentCache.set(contentCacheKey, response);
                }

                return response;
            }

            if (isPublicContent) {
                console.log('Using public request for freely accessible content');

                const publicOptions = {};
                if (signal) {
                    publicOptions.signal = signal;
                }

                const response = await fetchWithRetry(async () => {
                    return await handlePublicRequest(
                        API_ENDPOINTS.LESSON.DETAILS(lessonId),
                        `Failed to fetch public lesson details for lesson ${lessonId}`,
                        publicOptions
                    );
                });

                if (
                    cachedContent?.content &&
                    response.content &&
                    cachedContent.content.length > response.content.length
                ) {
                    console.log('Using cached content (longer than API response)');
                    response.content = cachedContent.content;
                    source = 'cache+public';
                } else {
                    source = 'public';
                }

                if (DEBUG_MODE) {
                    const duration = performance.now() - startTime;
                    console.log(
                        `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
                    );
                }

                return response;
            }

            const defaultOptions = {};
            if (signal) {
                defaultOptions.signal = signal;
            }

            console.log('Using default API request for lesson content');

            const response = await fetchWithRetry(async () => {
                return await handleRequest(
                    async () =>
                        await apiClient.get(
                            API_ENDPOINTS.LESSON.DETAILS(lessonId),
                            defaultOptions
                        ),
                    `Failed to fetch lesson details for lesson ${lessonId}`
                );
            });

            if (DEBUG_MODE) {
                const duration = performance.now() - startTime;
                console.log(
                    `Lesson content fetch (${source}) took ${duration.toFixed(2)}ms`
                );
            }

            return response;
        } catch (error) {
            console.error(`Error fetching lesson ${lessonId}:`, error);

            if (DEBUG_MODE) {
                const duration = performance.now() - startTime;
                console.log(`Lesson content fetch FAILED (${duration.toFixed(2)}ms)`);
            }

            if (fallbackContent) {
                console.warn(`Using fallback content after API error`);
                return fallbackContent;
            }

            throw error;
        }
    },

    completeLesson: async (lessonId, timeSpent = 0) => {
        return handleRequest(
            async () =>
                await apiClient.put(API_ENDPOINTS.LESSON.COMPLETE(lessonId), {
                    timeSpent,
                }),
            `Failed to mark lesson ${lessonId} as complete`
        );
    },

    getCourseReviews: async slug => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.COURSE.REVIEWS(slug)),
            `Failed to fetch reviews for course ${slug}`
        );
    },

    addCourseReview: async (slug, reviewData) => {
        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.COURSE.REVIEW(slug), reviewData),
            `Failed to add review for course ${slug}`
        );
    },

    updateCourseReview: async (slug, reviewId, reviewData) => {
        return handleRequest(
            async () =>
                await apiClient.put(
                    API_ENDPOINTS.COURSE.UPDATE_REVIEW(slug, reviewId),
                    reviewData
                ),
            `Failed to update review ${reviewId}`
        );
    },

    deleteCourseReview: async (slug, reviewId) => {
        return handleRequest(
            async () =>
                await apiClient.delete(
                    API_ENDPOINTS.COURSE.UPDATE_REVIEW(slug, reviewId)
                ),
            `Failed to delete review ${reviewId}`
        );
    },

    // Updated to use the correct search endpoint
    searchCourses: async query => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.COURSE.SEARCH, {
                    params: { q: query },
                }),
            'Course search failed'
        );
    },

    // FIXED: Enhanced featured courses function to handle new API response structure
    getFeaturedCourses: async (limit = 3) => {
        const useLocalStorage = typeof window !== 'undefined' && window.localStorage;
        const cacheKey = `featured_courses_${limit}`;
        let cachedData = null;

        // Try to get data from cache first
        if (useLocalStorage) {
            try {
                cachedData = contentCache.get(cacheKey);
                if (cachedData && Array.isArray(cachedData) && cachedData.length > 0) {
                    if (DEBUG_MODE) console.log('Using cached featured courses data');
                    return cachedData;
                }
            } catch (error) {
                console.error('Error accessing cached featured courses:', error);
            }
        }

        try {
            // Try the new API endpoint with updated structure
            try {
                const response = await handleRequest(
                    async () =>
                        await apiClient.get(API_ENDPOINTS.COURSE.FEATURED, {
                            params: { limit },
                        }),
                    'Failed to fetch featured courses'
                );

                // Extract courses from the new nested response format
                if (response && response.courses && Array.isArray(response.courses)) {
                    if (DEBUG_MODE) console.log('Using new featured courses API structure');

                    // Cache the courses array for future use
                    if (useLocalStorage) {
                        contentCache.set(cacheKey, response.courses, 5 * 60); // Cache for 5 minutes
                    }

                    return response.courses;
                } else {
                    // Response exists but doesn't have expected structure
                    throw new Error('Invalid response structure from featured courses API');
                }
            } catch (error) {
                console.warn('New featured endpoint failed, trying legacy endpoint', error);

                // Try the legacy/old endpoint as fallback
                if (API_ENDPOINTS.COURSE.FEATURED_OLD) {
                    const legacyResponse = await handleRequest(
                        async () =>
                            await apiClient.get(API_ENDPOINTS.COURSE.FEATURED_OLD, {
                                params: { limit },
                            }),
                        'Failed to fetch featured courses (legacy endpoint)'
                    );

                    if (DEBUG_MODE) console.log('Using legacy featured courses API');

                    // Cache the legacy response for future use
                    if (useLocalStorage && legacyResponse) {
                        contentCache.set(cacheKey, legacyResponse, 5 * 60);
                    }

                    return legacyResponse;
                }

                // If we can't use legacy endpoint, re-throw the error
                throw error;
            }
        } catch (error) {
            if (!ALLOW_MOCK_FALLBACK) {
                throw error;
            }

            logWarning('Falling back to mock featured courses data', { error });

            // Return standardized mock data
            return [
                {
                    id: 1,
                    title: 'Introduction to Programming',
                    instructor: 'John Smith',
                    category: 'Computer Science',
                    rating: 4.8,
                    students: 1200,
                    image: '/images/courses/programming-intro.jpg',
                },
                {
                    id: 2,
                    title: 'Web Development Bootcamp',
                    instructor: 'Maria Johnson',
                    category: 'Web Development',
                    rating: 4.9,
                    students: 2500,
                    image: '/images/courses/web-dev.jpg',
                },
                {
                    id: 3,
                    title: 'Data Science Fundamentals',
                    instructor: 'Robert Chen',
                    category: 'Data Science',
                    rating: 4.7,
                    students: 1800,
                    image: '/images/courses/data-science.jpg',
                },
            ];
        }
    },

    getAssessmentDetails: async assessmentId => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.ASSESSMENT.DETAILS(assessmentId)),
            `Failed to fetch assessment details for assessment ${assessmentId}`
        );
    },

    startAssessment: async assessmentId => {
        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.ASSESSMENT.START(assessmentId)),
            `Failed to start assessment ${assessmentId}`
        );
    },

    submitAssessment: async (attemptId, answers) => {
        return handleRequest(
            async () =>
                await apiClient.put(
                    API_ENDPOINTS.ASSESSMENT.SUBMIT(attemptId),
                    answers
                ),
            `Failed to submit assessment attempt ${attemptId}`
        );
    },
};

// Helper function for course form data preparation
function prepareCourseFormData(courseData, thumbnailFile) {
    const formData = createFormData(courseData);
    if (thumbnailFile) {
        formData.append('thumbnail', thumbnailFile);
    }
    return formData;
}
