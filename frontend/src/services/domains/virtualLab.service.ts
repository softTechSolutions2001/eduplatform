/**
 * File: src/services/domains/virtualLab.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Virtual Lab service for interactive learning environments
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const virtualLabService = {
    getLabDetails: async labId => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.LAB.DETAILS(labId)),
            `Failed to fetch lab ${labId}`
        );
    },

    startLabSession: async labId => {
        return handleRequest(
            async () => await apiClient.post(API_ENDPOINTS.LAB.START(labId)),
            `Failed to start lab ${labId}`
        );
    },

    submitLabSolution: async (labId, solutionData) => {
        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.LAB.SUBMIT(labId), solutionData),
            `Failed to submit solution for lab ${labId}`
        );
    },
};
