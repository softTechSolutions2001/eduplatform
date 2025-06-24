/**
 * File: frontend/src/courseBuilder/store/schema.ts
 * Version: 2.2.0
 * Date: 2025-06-14 14:59:37
 * Author: sujibeautysalon
 * Last Modified: 2025-06-14 14:59:37 UTC
 *
 * Course Builder Schema Definitions with Enhanced Validation
 *
 * This module defines Zod validation schemas for the course builder application,
 * ensuring type safety and data consistency across the frontend and backend.
 *
 * Key Features:
 * - Comprehensive validation for all course-related entities
 * - Type inference for TypeScript integration
 * - Field naming alignment with backend API expectations
 * - Proper default values matching store expectations
 * - Enhanced validation constraints for data integrity
 * - Support for both temporary and permanent IDs
 *
 * Version 2.2.0 Changes (Surgical Fixes from Code Review):
 * - FIXED: Changed categoryId to category for API alignment
 * - FIXED: Changed LessonSchema.accessLevel default from 'guest' to 'registered'
 * - FIXED: Added missing fields (slug, isDraft, isPublished, etc.) to CourseSchema
 * - FIXED: Enhanced validation constraints with proper min/max values
 * - FIXED: Added type field to LessonSchema for lesson type validation
 * - FIXED: Improved ResourceSchema with better file handling
 * - FIXED: Added comprehensive optional fields for API compatibility
 * - FIXED: Standardized naming conventions throughout schema
 *
 * Connected Files:
 * - frontend/src/courseBuilder/store/courseSlice.ts - Uses these types
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - API payload validation
 * - frontend/src/utils/buildCourseFormData.ts - FormData serialization
 * - backend/instructor_portal/serializers.py - Backend validation alignment
 */

import { z } from 'zod';

// ✅ FIX 1: Enhanced ResourceSchema with proper field validation
export const ResourceSchema = z.object({
  id: z.union([z.string(), z.number()]).optional(),
  title: z.string().min(1, 'Resource title is required').max(255, 'Resource title too long'),
  type: z.enum(['document', 'video', 'code', 'link', 'pdf', 'image']),
  url: z.string().url('Invalid URL format').optional(),
  file: z.instanceof(File).optional(),
  premium: z.boolean().default(false),
  order: z.number().nonnegative().default(0),
  description: z.string().optional(),
  size: z.number().optional(), // File size in bytes
  mimeType: z.string().optional(),
});

// ✅ FIX 2: Enhanced LessonSchema with proper defaults and validation
export const LessonSchema = z.object({
  id: z.union([z.string(), z.number()]),
  title: z.string().min(3, 'Lesson title must be at least 3 characters').max(200, 'Lesson title too long'),
  content: z.string().min(1, 'Lesson content is required').optional(),
  guest_content: z.string().optional(), // Content visible to guests
  registered_content: z.string().optional(), // Content visible to registered users
  order: z.number().nonnegative().default(0), // Changed from positive to nonnegative
  // ✅ CRITICAL FIX: Changed default from 'guest' to 'registered' to match store expectations
  accessLevel: z.enum(['guest', 'registered', 'premium']).default('registered'),
  // ✅ FIX 3: Added type field for lesson type validation
  type: z.enum(['reading', 'video', 'quiz', 'assignment', 'discussion', 'lab']).default('reading'),
  duration_minutes: z.number().nonnegative().default(15), // Default 15 minutes
  resources: z.array(ResourceSchema).default([]),
  // Additional lesson fields for API compatibility
  has_assessment: z.boolean().default(false),
  has_lab: z.boolean().default(false),
  is_free_preview: z.boolean().default(false),
  video_url: z.string().url().optional(),
  video_duration: z.number().nonnegative().optional(),
  completed: z.boolean().default(false),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

// ✅ FIX 4: Enhanced ModuleSchema with comprehensive validation
export const ModuleSchema = z.object({
  id: z.union([z.string(), z.number()]),
  title: z.string().min(3, 'Module title must be at least 3 characters').max(200, 'Module title too long'),
  description: z.string().optional(),
  order: z.number().nonnegative().default(0), // Changed from positive to nonnegative
  duration_minutes: z.number().nonnegative().default(0),
  lessons: z.array(LessonSchema).default([]),
  // Additional module fields for API compatibility
  is_published: z.boolean().default(false),
  lesson_count: z.number().nonnegative().optional(),
  estimated_duration: z.string().optional(), // Human-readable duration
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

// ✅ FIX 5: Comprehensive CourseSchema with API alignment
export const CourseSchema = z.object({
  id: z.number().optional(),
  title: z.string().min(5, 'Course title must be at least 5 characters').max(160, 'Course title too long'), // Reduced from 120 to match API
  // ✅ CRITICAL FIX: Changed from categoryId to category for API alignment
  category: z.union([z.number(), z.string()]).optional(), // Allow both number and string for flexibility
  description: z.string().min(20, 'Course description must be at least 20 characters').max(2000, 'Course description too long'),

  // Image/thumbnail handling
  thumbnail: z.any().optional(), // Can be File, string URL, or null
  image: z.union([z.instanceof(File), z.string(), z.null()]).optional(), // Alternative field name

  modules: z.array(ModuleSchema).default([]),

  // ✅ FIX 6: Added missing course fields for complete API compatibility
  slug: z.string().optional(),
  isDraft: z.boolean().default(true),
  isPublished: z.boolean().default(false),
  is_draft: z.boolean().optional(), // Snake case version for API
  is_published: z.boolean().optional(), // Snake case version for API

  // Course metadata
  price: z.number().nonnegative().optional(),
  language: z.string().optional(),
  level: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
  tags: z.array(z.string()).default([]),

  // Course statistics
  completion_percentage: z.number().min(0).max(100).default(0),
  completedLessons: z.number().nonnegative().default(0),
  totalLessons: z.number().nonnegative().optional(),
  estimated_duration: z.string().optional(),

  // Course status and versioning
  status: z.enum(['draft', 'published', 'archived', 'pending']).default('draft'),
  version: z.number().positive().default(1),
  parent_course_id: z.number().optional(), // For versioned courses

  // Timestamps
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
  published_at: z.string().datetime().optional(),

  // Author information
  instructor: z.object({
    id: z.number(),
    username: z.string(),
    email: z.string().email().optional(),
    full_name: z.string().optional(),
  }).optional(),

  // Course settings
  allow_comments: z.boolean().default(true),
  allow_reviews: z.boolean().default(true),
  is_featured: z.boolean().default(false),
  certificate_enabled: z.boolean().default(false),

  // SEO and marketing
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  keywords: z.array(z.string()).default([]),

  // Course content tracking
  creation_method: z.enum(['manual', 'wizard', 'template', 'import']).default('manual'),
});

// ✅ FIX 7: Enhanced type exports with proper inference
export type Course = z.infer<typeof CourseSchema>;
export type Module = z.infer<typeof ModuleSchema>;
export type Lesson = z.infer<typeof LessonSchema>;
export type Resource = z.infer<typeof ResourceSchema>;

// ✅ FIX 8: Additional utility types for form handling
export type CourseFormData = Omit<Course, 'id' | 'created_at' | 'updated_at'>;
export type ModuleFormData = Omit<Module, 'id' | 'created_at' | 'updated_at'>;
export type LessonFormData = Omit<Lesson, 'id' | 'created_at' | 'updated_at'>;
export type ResourceFormData = Omit<Resource, 'id'>;

// ✅ FIX 9: Validation helper functions
export const validateCourse = (data: unknown): Course => {
  return CourseSchema.parse(data);
};

export const validateModule = (data: unknown): Module => {
  return ModuleSchema.parse(data);
};

export const validateLesson = (data: unknown): Lesson => {
  return LessonSchema.parse(data);
};

export const validateResource = (data: unknown): Resource => {
  return ResourceSchema.parse(data);
};

// ✅ FIX 10: Partial validation for form updates
export const PartialCourseSchema = CourseSchema.partial();
export const PartialModuleSchema = ModuleSchema.partial();
export const PartialLessonSchema = LessonSchema.partial();
export const PartialResourceSchema = ResourceSchema.partial();

// Additional helper types for partial updates
export type PartialCourse = z.infer<typeof PartialCourseSchema>;
export type PartialModule = z.infer<typeof PartialModuleSchema>;
export type PartialLesson = z.infer<typeof PartialLessonSchema>;
export type PartialResource = z.infer<typeof PartialResourceSchema>;

// ✅ FIX 11: Schema validation with error handling
export const safeValidateCourse = (data: unknown) => {
  const result = CourseSchema.safeParse(data);
  if (!result.success) {
    console.error('Course validation failed:', result.error.flatten());
    return null;
  }
  return result.data;
};

export const safeValidateModule = (data: unknown) => {
  const result = ModuleSchema.safeParse(data);
  if (!result.success) {
    console.error('Module validation failed:', result.error.flatten());
    return null;
  }
  return result.data;
};

export const safeValidateLesson = (data: unknown) => {
  const result = LessonSchema.safeParse(data);
  if (!result.success) {
    console.error('Lesson validation failed:', result.error.flatten());
    return null;
  }
  return result.data;
};

// Export all schemas for external validation
export const schemas = {
  CourseSchema,
  ModuleSchema,
  LessonSchema,
  ResourceSchema,
  PartialCourseSchema,
  PartialModuleSchema,
  PartialLessonSchema,
  PartialResourceSchema,
};

export default schemas;
