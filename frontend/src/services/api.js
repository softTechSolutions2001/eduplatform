/**
 * File: src/services/api.js
 * Version: 4.0.2
 * Last modified: 2025-06-25 05:13:56
 * Author: softTechSolutions2001
 * Modified by: softTechSolutions2001
 *
 * Core API service barrel file for EduPlatform frontend
 * Maintains backward compatibility with existing imports
 * Includes enhanced social authentication with PKCE support
 * Updated subscription tier terminology for consistency
 */

// Import apiClient for direct use and re-export
import { apiClient } from './http/apiClient';

// Import utils
import { apiUtils } from './utils/apiUtils';

// Import all service domains
import { authService } from './domains/auth.service';
import { subscriptionService } from './domains/subscription.service';
import { courseService } from './domains/course.service';
import { assessmentService } from './domains/assessment.service';
import { progressService } from './domains/progress.service';
import { noteService } from './domains/note.service';
import { forumService } from './domains/forum.service';
import { virtualLabService } from './domains/virtualLab.service';
import { categoryService } from './domains/category.service';
import { certificateService } from './domains/certificate.service';
import { blogService } from './domains/blog.service';
import { systemService } from './domains/system.service';
import { statisticsService } from './domains/statistics.service';
import { testimonialService } from './domains/testimonial.service';

// Create the legacy API facade object
const api = {
  auth: authService,
  subscription: subscriptionService,
  course: courseService,
  assessment: assessmentService,
  progress: progressService,
  note: noteService,
  forum: forumService,
  virtualLab: virtualLabService,
  category: categoryService,
  certificate: certificateService,
  blog: blogService,
  system: systemService,
  statistics: statisticsService,
  testimonial: testimonialService,

  // Convenience proxies for common auth operations (unchanged behavior)
  login: authService.login,
  register: authService.register,
  getCurrentUser: authService.getCurrentUser,
  logout: authService.logout,
  isAuthenticated: authService.isAuthenticated,

  utils: apiUtils,
};

// Named exports - maintain all existing export signatures
export {
  apiClient,
  apiUtils,
  assessmentService,
  authService,
  blogService,
  categoryService,
  certificateService,
  courseService,
  forumService,
  noteService,
  progressService,
  statisticsService,
  subscriptionService,
  systemService,
  testimonialService,
  virtualLabService,
};

// Default export - the API facade object
export default api;
