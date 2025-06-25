/**
 * File: src/services/domains/assessment.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Assessment service for operations related to quizzes and exams
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const assessmentService = {
    getUserAssessmentAttempts: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.USER.ASSESSMENT_ATTEMPTS),
            'Failed to fetch assessment attempts'
        );
    },
};
