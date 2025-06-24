/**
 * Course Cleanup Utility
 *
 * This script helps delete multiple courses at once.
 * It accesses the course API directly using the auth token.
 */
import api from '../services/api';
import instructorService from '../services/instructorService';

// Ensure we're authenticated before running this
const initialize = async () => {
  if (!api.isAuthenticated()) {
    console.log('Not authenticated. Please login first.');
    return false;
  }
  return true;
};

// Get all courses
const getAllCourses = async () => {
  try {
    const response = await instructorService.getAllCourses();
    const courses = response.results || response;
    if (!Array.isArray(courses)) {
      return Object.values(courses);
    }
    return courses;
  } catch (error) {
    console.error('Failed to fetch courses:', error);
    return [];
  }
};

// Delete a single course
const deleteCourse = async courseSlug => {
  try {
    await instructorService.deleteCourse(courseSlug);
    return true;
  } catch (error) {
    console.error(`Failed to delete course ${courseSlug}:`, error);
    return false;
  }
};

// Delete all courses
const deleteAllCourses = async () => {
  if (!(await initialize())) {
    return { success: false, message: 'Authentication required' };
  }

  const courses = await getAllCourses();
  console.log(`Found ${courses.length} courses to delete.`);

  const results = {
    total: courses.length,
    deleted: 0,
    failed: 0,
    failedCourses: [],
  };

  for (let i = 0; i < courses.length; i++) {
    const course = courses[i];
    const courseIdentifier = course.slug || course.id;
    console.log(
      `Deleting course ${i + 1}/${courses.length}: ${course.title} (${courseIdentifier})`
    );

    const success = await deleteCourse(courseIdentifier);
    if (success) {
      results.deleted++;
    } else {
      results.failed++;
      results.failedCourses.push({
        id: course.id,
        slug: course.slug,
        title: course.title,
      });
    }

    // Add a small delay to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return {
    success: true,
    results,
  };
};

// Delete courses in batches
const deleteCoursesBatch = async (batchSize = 50) => {
  if (!(await initialize())) {
    return { success: false, message: 'Authentication required' };
  }

  const courses = await getAllCourses();
  console.log(
    `Found ${courses.length} courses. Will delete in batches of ${batchSize}.`
  );

  const results = {
    total: courses.length,
    deleted: 0,
    failed: 0,
    failedCourses: [],
  };

  for (let i = 0; i < courses.length; i += batchSize) {
    const batch = courses.slice(i, i + batchSize);
    console.log(
      `Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(courses.length / batchSize)}`
    );

    for (const course of batch) {
      const courseIdentifier = course.slug || course.id;
      console.log(`Deleting course: ${course.title} (${courseIdentifier})`);

      const success = await deleteCourse(courseIdentifier);
      if (success) {
        results.deleted++;
      } else {
        results.failed++;
        results.failedCourses.push({
          id: course.id,
          slug: course.slug,
          title: course.title,
        });
      }
    }

    console.log(
      `Completed batch ${Math.floor(i / batchSize) + 1}. Deleted ${results.deleted}/${courses.length} courses so far.`
    );

    // Add a delay between batches to avoid overwhelming the server
    if (i + batchSize < courses.length) {
      console.log('Pausing before next batch...');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  return {
    success: true,
    results,
  };
};

// Export functions to be used in browser console or imported elsewhere
window.cleanupCourses = {
  deleteAll: deleteAllCourses,
  deleteBatch: deleteCoursesBatch,
  getAllCourses,
};

export { deleteAllCourses, deleteCoursesBatch, getAllCourses };
