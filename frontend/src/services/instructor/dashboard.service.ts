/**
 * File: src/services/instructor/dashboard.service.ts
 * Version: 1.0.0
 * Date: 2025-06-25 08:43:44
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 08:43:44 UTC
 *
 * Instructor Dashboard Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific dashboard and statistics operations
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
import {
    logError
} from './helpers';

export const getInstructorStatistics = async (options = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get('/statistics/instructor/', requestOptions),
            'Failed to fetch instructor statistics',
            {
                url: '/statistics/instructor/',
                enableCache: true,
                cacheTime: 60000,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError('Error fetching instructor statistics:', error);
        return {
            totalCourses: 0,
            totalStudents: 0,
            totalRevenue: 0,
            recentEnrollments: 0,
        };
    }
};

export const getPublicHealthCheck = async (options = {}) => {
    return handleRequest(
        async requestOptions =>
            await apiClient.get('/statistics/platform/', requestOptions),
        'Failed to fetch platform health check',
        {
            url: '/statistics/platform/',
            skipAuthCheck: true,
            enableCache: true,
            cacheTime: 60000,
            ...options,
        }
    );
};
