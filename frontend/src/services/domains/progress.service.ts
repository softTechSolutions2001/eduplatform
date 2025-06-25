/**
 * File: src/services/domains/progress.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Progress service for tracking user progress in courses
 */

import { logWarning } from '../../utils/logger';
import { apiClient } from '../http/apiClient';
import { ALLOW_MOCK_FALLBACK } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const progressService = {
    getUserEnrollments: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.USER.ENROLLMENTS),
            'Failed to fetch enrollments'
        );
    },

    getUserProgress: async courseId => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.USER.PROGRESS.COURSE(courseId)),
            `Failed to fetch progress for course ${courseId}`
        );
    },

    getUserProgressStats: async () => {
        try {
            return await handleRequest(
                async () => await apiClient.get(API_ENDPOINTS.USER.PROGRESS.STATS),
                'Failed to fetch progress statistics'
            );
        } catch (error) {
            if (!ALLOW_MOCK_FALLBACK) {
                throw error;
            }

            logWarning('Falling back to mock progress statistics data', { error });
            return {
                totalCourses: 0,
                coursesInProgress: 0,
                coursesCompleted: 0,
                totalLessons: 0,
                completedLessons: 0,
                completionPercentage: 0,
                hoursSpent: 0,
                assessmentsCompleted: 0,
                completedAssessments: 0,
                recentActivity: [],
            };
        }
    },
};
