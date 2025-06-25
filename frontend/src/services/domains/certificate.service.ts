/**
 * File: src/services/domains/certificate.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Certificate service for course completion certificates
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const certificateService = {
    getUserCertificates: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.CERTIFICATE.BASE),
            'Failed to fetch certificates'
        );
    },

    generateCertificate: async courseSlug => {
        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.COURSE.CERTIFICATE(courseSlug)),
            `Failed to generate certificate for course ${courseSlug}`
        );
    },

    verifyCertificate: async verificationCode => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.CERTIFICATE.VERIFY(verificationCode)),
            'Certificate verification failed'
        );
    },
};
