/**
 * File: src/services/domains/forum.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Forum service for managing course discussions
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const forumService = {
    getCourseDiscussions: async courseSlug => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.COURSE.DISCUSSIONS(courseSlug)),
            `Failed to fetch discussions for course ${courseSlug}`
        );
    },

    getDiscussion: async (courseSlug, discussionId) => {
        return handleRequest(
            async () =>
                await apiClient.get(
                    API_ENDPOINTS.COURSE.DISCUSSION(courseSlug, discussionId)
                ),
            `Failed to fetch discussion ${discussionId}`
        );
    },

    createDiscussion: async (courseSlug, discussionData) => {
        return handleRequest(
            async () =>
                await apiClient.post(
                    API_ENDPOINTS.COURSE.DISCUSSIONS(courseSlug),
                    discussionData
                ),
            'Failed to create discussion'
        );
    },

    addDiscussionReply: async (courseSlug, discussionId, replyData) => {
        return handleRequest(
            async () =>
                await apiClient.post(
                    API_ENDPOINTS.COURSE.DISCUSSION_REPLIES(courseSlug, discussionId),
                    replyData
                ),
            `Failed to add reply to discussion ${discussionId}`
        );
    },
};
