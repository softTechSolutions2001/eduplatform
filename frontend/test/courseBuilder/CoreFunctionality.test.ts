// Simple integration test for Course Builder functionality
// This test validates the core functionality without complex dependencies

import { describe, it, expect } from 'vitest';

// Import our core modules to test their structure
import { courseBuilderSchema } from '../../src/courseBuilder/store/schema';
import { convertToCamelCase, convertToSnakeCase } from '../../src/courseBuilder/utils/caseConvert';
import { useCourseStore } from '../../src/courseBuilder/store/courseSlice';

describe('Course Builder Core Functionality', () => {
  it('should have valid schema definitions', () => {
    expect(courseBuilderSchema.Course).toBeDefined();
    expect(courseBuilderSchema.Module).toBeDefined();
    expect(courseBuilderSchema.Lesson).toBeDefined();
    expect(courseBuilderSchema.Resource).toBeDefined();
  });

  it('should convert case correctly', () => {
    const snakeCase = { user_name: 'test', created_at: '2025-01-01' };
    const camelCase = convertToCamelCase(snakeCase);
    expect(camelCase).toEqual({ userName: 'test', createdAt: '2025-01-01' });

    const backToSnake = convertToSnakeCase(camelCase);
    expect(backToSnake).toEqual(snakeCase);
  });

  it('should initialize store with default state', () => {
    const store = useCourseStore.getState();
    expect(store.course).toBeNull();
    expect(store.isDirty).toBe(false);
    expect(store.lastSaved).toBeNull();
  });

  it('should update course in store', () => {
    const testCourse = {
      id: 1,
      title: 'Test Course',
      description: 'Test Description',
      slug: 'test-course',
      modules: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    useCourseStore.getState().setCourse(testCourse);
    const updatedStore = useCourseStore.getState();
    expect(updatedStore.course).toEqual(testCourse);
    expect(updatedStore.isDirty).toBe(true);
  });
});

describe('Course Builder Module Management', () => {
  it('should add modules to course', () => {
    const initialCourse = {
      id: 1,
      title: 'Test Course',
      description: 'Test Description',
      slug: 'test-course',
      modules: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    useCourseStore.getState().setCourse(initialCourse);
    useCourseStore.getState().addModule('New Module', 'Module Description');
    
    const updatedStore = useCourseStore.getState();
    expect(updatedStore.course?.modules).toHaveLength(1);
    expect(updatedStore.course?.modules[0].title).toBe('New Module');
    expect(updatedStore.course?.modules[0].description).toBe('Module Description');
  });

  it('should update module titles', () => {
    const moduleId = useCourseStore.getState().course?.modules[0]?.id;
    if (moduleId) {
      useCourseStore.getState().updateModule(moduleId, { title: 'Updated Module' });
      const updatedStore = useCourseStore.getState();
      expect(updatedStore.course?.modules[0].title).toBe('Updated Module');
    }
  });
});
