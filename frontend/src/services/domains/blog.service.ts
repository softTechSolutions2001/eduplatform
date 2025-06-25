/**
 * File: src/services/domains/blog.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Blog service for platform blog functionality
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const blogService = {
    getLatestPosts: async (limit = 3) => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.BLOG.POSTS, { params: { limit } }),
            'Failed to fetch latest blog posts'
        );
    },

    getPostBySlug: async slug => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.BLOG.POST_BY_SLUG(slug)),
            `Failed to fetch blog post ${slug}`
        );
    },
};
