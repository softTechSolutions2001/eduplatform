/**
 * File: src/services/domains/note.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Note service for managing user notes during learning
 */

import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const noteService = {
    getUserNotes: async () => {
        return handleRequest(
            async () => await apiClient.get(API_ENDPOINTS.NOTE.BASE),
            'Failed to fetch notes'
        );
    },

    getNotesForLesson: async lessonId => {
        return handleRequest(
            async () =>
                await apiClient.get(API_ENDPOINTS.NOTE.BASE, {
                    params: { lesson: lessonId },
                }),
            `Failed to fetch notes for lesson ${lessonId}`
        );
    },

    createNote: async noteData => {
        return handleRequest(
            async () => await apiClient.post(API_ENDPOINTS.NOTE.BASE, noteData),
            'Failed to create note'
        );
    },

    updateNote: async (noteId, noteData) => {
        return handleRequest(
            async () =>
                await apiClient.put(API_ENDPOINTS.NOTE.DETAIL(noteId), noteData),
            `Failed to update note ${noteId}`
        );
    },

    deleteNote: async noteId => {
        return handleRequest(
            async () => await apiClient.delete(API_ENDPOINTS.NOTE.DETAIL(noteId)),
            `Failed to delete note ${noteId}`
        );
    },
};
