/**
 * File: src/services/domains/system.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * System service for platform status monitoring
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const systemService = {
    checkApiStatus: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.SYSTEM.STATUS),
            'API status check failed'
        );
    },

    checkDbStatus: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.SYSTEM.DB_STATUS),
            'Database status check failed'
        );
    },
};
