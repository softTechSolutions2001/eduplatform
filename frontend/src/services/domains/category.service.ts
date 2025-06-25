/**
 * File: src/services/domains/category.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Category service for course categorization
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const categoryService = {
    getAllCategories: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.CATEGORY.BASE),
            'Failed to fetch categories'
        );
    },

    getCoursesByCategory: async categorySlug => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.CATEGORY.COURSES(categorySlug)),
            `Failed to fetch courses for category ${categorySlug}`
        );
    },
};
