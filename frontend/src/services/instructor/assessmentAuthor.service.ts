/**
 * File: src/services/instructor/assessmentAuthor.service.ts
 * Version: 1.1.0
 * Date: 2025-06-25 10:02:06
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 10:02:06 UTC
 *
 * Instructor Assessment Authoring Service
 *
 * Extracted from instructorService.js v3.0.0
 * Handles instructor-specific assessment operations
 */

import { apiClient } from '../../services/api';
import { handleRequest } from '../../services/utils/handleRequest';
import {
    handleError,
    invalidateCache,
    log,
    logError
} from './helpers';
import { Assessment, RequestOptions } from './types';

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const createAssessment = async (assessmentData: Assessment, options: RequestOptions = {}) => {
    try {
        log('Creating assessment for lesson:', assessmentData.lesson);

        const response = await handleRequest(
            async requestOptions =>
                await apiClient.post('/instructor/assessments/', assessmentData, requestOptions),
            'Failed to create assessment',
            {
                url: '/instructor/assessments/',
                ...options,
            }
        );

        if (assessmentData.lesson) {
            invalidateCache(`/instructor/assessments/?lesson=${assessmentData.lesson}`);
        }

        return response;
    } catch (error) {
        logError('Error creating assessment:', error);
        throw handleError(error);
    }
};

export const getAssessments = async (lessonId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.get('/instructor/assessments/', {
                    params: { lesson: lessonId },
                    ...requestOptions,
                }),
            `Failed to fetch assessments for lesson ${lessonId}`,
            {
                url: `/instructor/assessments/?lesson=${lessonId}`,
                enableCache: true,
                cacheTime: 30000,
                ...options,
            }
        );

        return response;
    } catch (error) {
        logError(`Error fetching assessments for lesson ${lessonId}:`, error);
        throw handleError(error);
    }
};

// B-7 fix: Remove explicit Content-Type header to let Axios handle it
export const updateAssessment = async (assessmentId: string | number, assessmentData: Partial<Assessment>, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.put(`/instructor/assessments/${assessmentId}/`, assessmentData, requestOptions),
            `Failed to update assessment ${assessmentId}`,
            {
                url: `/instructor/assessments/${assessmentId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/assessments/${assessmentId}/`);
        if (assessmentData.lesson) {
            invalidateCache(`/instructor/assessments/?lesson=${assessmentData.lesson}`);
        }

        return response;
    } catch (error) {
        logError(`Error updating assessment ${assessmentId}:`, error);
        throw handleError(error);
    }
};

export const deleteAssessment = async (assessmentId: string | number, options: RequestOptions = {}) => {
    try {
        const response = await handleRequest(
            async requestOptions =>
                await apiClient.delete(`/instructor/assessments/${assessmentId}/`, requestOptions),
            `Failed to delete assessment ${assessmentId}`,
            {
                url: `/instructor/assessments/${assessmentId}/`,
                ...options,
            }
        );

        invalidateCache(`/instructor/assessments/${assessmentId}/`);
        invalidateCache('/instructor/assessments/');

        return response;
    } catch (error) {
        logError(`Error deleting assessment ${assessmentId}:`, error);
        throw handleError(error);
    }
};

/**
 * Validate assessment data against common requirements
 * Useful for client-side validation before sending to API
 *
 * @param assessmentData Assessment data to validate
 * @returns Object with validation result
 */
export const validateAssessment = (assessmentData: Partial<Assessment>): { isValid: boolean, errors: string[] } => {
    const errors: string[] = [];

    if (!assessmentData.title?.trim()) {
        errors.push('Assessment title is required');
    }

    if (!assessmentData.lesson) {
        errors.push('Associated lesson is required');
    }

    if (!assessmentData.questions || !Array.isArray(assessmentData.questions) || assessmentData.questions.length === 0) {
        errors.push('At least one question is required');
    } else {
        // Validate questions
        assessmentData.questions.forEach((question, index) => {
            if (!question.text?.trim()) {
                errors.push(`Question #${index + 1} text is required`);
            }

            if (question.question_type === 'multiple_choice') {
                if (!question.choices || !Array.isArray(question.choices) || question.choices.length < 2) {
                    errors.push(`Question #${index + 1} requires at least 2 choices`);
                }

                // Check if at least one choice is marked as correct
                const hasCorrectChoice = question.choices?.some(choice => choice.is_correct);
                if (!hasCorrectChoice) {
                    errors.push(`Question #${index + 1} requires at least one correct answer`);
                }
            } else if (question.question_type === 'true_false') {
                if (!question.correct_answer) {
                    errors.push(`Question #${index + 1} requires a correct answer (true/false)`);
                }
            }
        });
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};
