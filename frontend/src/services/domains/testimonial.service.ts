/**
 * File: src/services/domains/testimonial.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Testimonial service for user reviews and testimonials
 */

import { logWarning } from '../../utils/logger';
import { apiClient } from '../http/apiClient';
import { ALLOW_MOCK_FALLBACK } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const testimonialService = {
    getFeaturedTestimonials: async (limit = 3) => {
        try {
            return await handleRequest(
                async () =>
                    await apiClient.get(API_ENDPOINTS.TESTIMONIAL.FEATURED, {
                        params: { limit },
                    }),
                'Failed to fetch featured testimonials'
            );
        } catch (error) {
            if (
                !ALLOW_MOCK_FALLBACK ||
                !(error.response && error.response.status === 404)
            ) {
                throw error;
            }

            logWarning('Testimonials endpoint not available, using mock data', {
                error,
            });
            return [
                {
                    id: 1,
                    name: 'Jane Smith',
                    role: 'Software Engineer',
                    content:
                        'This platform helped me transition from a junior to senior developer in just 6 months.',
                    rating: 5,
                    avatar: '/images/avatars/avatar-1.jpg',
                },
                {
                    id: 2,
                    name: 'Michael Johnson',
                    role: 'Data Scientist',
                    content:
                        'The data science courses here are comprehensive and practical. I use what I learned daily.',
                    rating: 5,
                    avatar: '/images/avatars/avatar-2.jpg',
                },
                {
                    id: 3,
                    name: 'Sarah Williams',
                    role: 'UX Designer',
                    content:
                        'The design courses completely changed how I approach user experience. Highly recommended!',
                    rating: 4,
                    avatar: '/images/avatars/avatar-3.jpg',
                },
            ];
        }
    },

    getAllTestimonials: async (params = {}) => {
        try {
            return await handleRequest(
                async () =>
                    await apiClient.get(API_ENDPOINTS.TESTIMONIAL.BASE, { params }),
                'Failed to fetch testimonials'
            );
        } catch (error) {
            if (
                !ALLOW_MOCK_FALLBACK ||
                !(error.response && error.response.status === 404)
            ) {
                throw error;
            }

            logWarning('Testimonials endpoint not available, using mock data', {
                error,
            });
            return [
                {
                    id: 1,
                    name: 'Jane Smith',
                    role: 'Software Engineer',
                    content:
                        'This platform helped me transition from a junior to senior developer in just 6 months.',
                    rating: 5,
                    avatar: '/images/avatars/avatar-1.jpg',
                },
                {
                    id: 2,
                    name: 'Michael Johnson',
                    role: 'Data Scientist',
                    content:
                        'The data science courses here are comprehensive and practical. I use what I learned daily.',
                    rating: 5,
                    avatar: '/images/avatars/avatar-2.jpg',
                },
                {
                    id: 3,
                    name: 'Sarah Williams',
                    role: 'UX Designer',
                    content:
                        'The design courses completely changed how I approach user experience. Highly recommended!',
                    rating: 4,
                    avatar: '/images/avatars/avatar-3.jpg',
                },
            ];
        }
    },

    submitTestimonial: async testimonialData => {
        return handleRequest(
            async () =>
                await apiClient.post(API_ENDPOINTS.TESTIMONIAL.BASE, testimonialData),
            'Failed to submit testimonial'
        );
    },
};
