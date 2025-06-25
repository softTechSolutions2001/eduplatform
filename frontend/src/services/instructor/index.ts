/**
 * File: src/services/instructor/index.ts
 * Version: 1.1.0
 * Date: 2025-06-25 10:06:10
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 10:06:10 UTC
 *
 * Instructor Service Index/Barrel
 *
 * Creates a backward-compatible facade for the modularized instructor services
 * Improved to handle potential missing mappings and better type safety
 */

// Import all services
import * as Assessment from './assessmentAuthor.service';
import * as CourseAuthoring from './courseAuthoring.service';
import * as Dashboard from './dashboard.service';
import * as Lesson from './lesson.service';
import * as Module from './module.service';
import * as Resource from './resource.service';

// Import helpers
import * as Helpers from './helpers';
import {
    buildFormData,
    camelToSnake,
    clearCache,
    FILE_VALIDATION,
    formatFileSize,
    getCacheStats,
    hasFileUploads,
    invalidateCache,
    isSlug,
    limitCacheSize,
    mapKeys,
    sanitizeCourseData,
    tmpId,
    validateFile
} from './helpers';

// Import types

// Export all types for direct imports
export * from './types';

// C-2 fix: Create dynamic facade to avoid missing methods
// First, collect all service exports
const allServiceExports = {
    ...CourseAuthoring,
    ...Module,
    ...Lesson,
    ...Resource,
    ...Assessment,
    ...Dashboard
};

// Legacy-compatible facade with improved type safety
class InstructorFacade {
    // Base URL
    baseURL = '/api/instructor';

    // File validation constants
    FILE_VALIDATION = FILE_VALIDATION;

    // Course methods
    getAllCourses = CourseAuthoring.getAllCourses;
    getCourse = CourseAuthoring.getCourse;
    getCourseBySlug = CourseAuthoring.getCourseBySlug;
    createCourse = CourseAuthoring.createCourse;
    updateCourse = CourseAuthoring.updateCourse;
    checkCourseTitle = CourseAuthoring.checkCourseTitle;
    deleteCourse = CourseAuthoring.deleteCourse;
    publishCourse = CourseAuthoring.publishCourse;
    getCourseAnalytics = CourseAuthoring.getCourseAnalytics;
    duplicateCourse = CourseAuthoring.duplicateCourse;

    // Module methods
    getModules = Module.getModules;
    getModule = Module.getModule;
    createModule = Module.createModule;
    updateModule = Module.updateModule;
    deleteModule = Module.deleteModule;
    updateModuleOrder = Module.updateModuleOrder;

    // Lesson methods
    getLessons = Lesson.getLessons;
    getLesson = Lesson.getLesson;
    createLesson = Lesson.createLesson;
    updateLesson = Lesson.updateLesson;
    deleteLesson = Lesson.deleteLesson;
    updateLessonOrder = Lesson.updateLessonOrder;
    getInstructorLessons = Lesson.getInstructorLessons;

    // Resource methods
    uploadResource = Resource.uploadResource;
    getPresignedUrl = Resource.getPresignedUrl;
    confirmResourceUpload = Resource.confirmResourceUpload;
    getResources = Resource.getResources;
    deleteResource = Resource.deleteResource;
    purgeResource = Resource.purgeResource;

    // Assessment methods
    createAssessment = Assessment.createAssessment;
    getAssessments = Assessment.getAssessments;
    updateAssessment = Assessment.updateAssessment;
    deleteAssessment = Assessment.deleteAssessment;
    validateAssessment = Assessment.validateAssessment;

    // Dashboard/Statistics methods
    getInstructorStatistics = Dashboard.getInstructorStatistics;
    getPublicHealthCheck = Dashboard.getPublicHealthCheck;

    // Utils
    utils = {
        isSlug,
        validateFile,
        generateTempId: () => tmpId.generateTempId(),
        formatFileSize,
        // Add additional utility methods for broader compatibility
        camelToSnake,
        mapKeys,
    };

    // Helper methods
    clearCache = clearCache;
    getCacheStats = getCacheStats;
    invalidateCache = invalidateCache;
    hasFileUploads = hasFileUploads;
    buildFormData = buildFormData;
    sanitizeCourseData = sanitizeCourseData;
    handleError = Helpers.handleError;
    generateTempId = () => tmpId.generateTempId();
    formatFileSize = formatFileSize;
    limitCacheSize = limitCacheSize; // Add the new cache limiting function

    // Dynamic method resolution to avoid silent API breaks (C-2 fix)
    constructor() {
        // Create proxy to catch potential missing methods
        return new Proxy(this, {
            get(target, prop, receiver) {
                const value = Reflect.get(target, prop, receiver);

                // If method exists on target, return it
                if (value !== undefined) {
                    return value;
                }

                // Try to find method in service exports
                if (typeof prop === 'string' && prop in allServiceExports) {
                    console.warn(`Method "${String(prop)}" accessed via facade but not explicitly mapped. Consider updating InstructorFacade class.`);
                    return allServiceExports[prop];
                }

                // Property truly doesn't exist
                console.warn(`Attempted to access undefined property "${String(prop)}" on InstructorFacade`);
                return undefined;
            }
        });
    }
}

// Create singleton instance
const instructorFacade = new InstructorFacade();
export default instructorFacade;

// Named exports
export { InstructorFacade as InstructorService };

// Re-export all service functions for direct imports
export * from './assessmentAuthor.service';
export * from './courseAuthoring.service';
export * from './dashboard.service';
export * from './lesson.service';
export * from './module.service';
export * from './resource.service';
