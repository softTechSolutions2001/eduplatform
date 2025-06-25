/**
 * File: src/services/domains/statistics.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Statistics service for platform metrics and analytics
 */

import { logWarning } from '../../utils/logger';
import { apiClient } from '../http/apiClient';
import { ALLOW_MOCK_FALLBACK } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const statisticsService = {
    getPlatformStats: async () => {
        try {
            return await handleRequest(
                async () => await apiClient.get(API_ENDPOINTS.STATISTICS.PLATFORM),
                'Failed to fetch platform statistics'
            );
        } catch (error) {
            if (
                !ALLOW_MOCK_FALLBACK ||
                !(error.response && error.response.status === 404)
            ) {
                throw error;
            }

            logWarning('Statistics endpoint not available, using mock data', {
                error,
            });
            return {
                totalCourses: 150,
                totalStudents: 12500,
                totalInstructors: 48,
            };
        }
    },

    getUserLearningStats: async () => {
        try {
            return await handleRequest(
                async () => await apiClient.get(API_ENDPOINTS.STATISTICS.USER),
                'Failed to fetch user learning statistics'
            );
        } catch (error) {
            if (
                !ALLOW_MOCK_FALLBACK ||
                !(error.response && error.response.status === 404)
            ) {
                throw error;
            }

            logWarning('User statistics endpoint not available, using mock data', {
                error,
            });
            return {
                coursesCompleted: 0,
                hoursSpent: 0,
                averageScore: 0,
            };
        }
    },

    getInstructorTeachingStats: async () => {
        try {
            return await handleRequest(
                async () => await apiClient.get(API_ENDPOINTS.STATISTICS.INSTRUCTOR),
                'Failed to fetch instructor teaching statistics'
            );
        } catch (error) {
            if (
                !ALLOW_MOCK_FALLBACK ||
                !(error.response && error.response.status === 404)
            ) {
                throw error;
            }

            logWarning(
                'Instructor statistics endpoint not available, using mock data',
                { error }
            );
            return {
                totalStudents: 0,
                coursesCreated: 0,
                averageRating: 0,
            };
        }
    },
};
