/**
 * File: frontend/src/courseBuilder/components/ModuleCard.tsx
 * Version: 2.2.0
 * Date Created: 2025-06-14 15:30:35
 * Date Revised: 2025-06-25 10:15:00
 * Author: sujibeautysalon
 * Last Modified By: sujibeautysalon
 * Last Modified: 2025-06-25 10:15:00 UTC
 *
 * Enhanced ModuleCard Component with Memory Leak Fixes and Performance Optimizations
 *
 * This component represents a single course module in the builder with enhanced
 * error handling, accessibility features, and performance optimizations.
 *
 * Key Features:
 * - Memory leak prevention with proper cleanup mechanisms
 * - Controlled input components eliminating React warnings
 * - Enhanced accessibility with proper ARIA attributes
 * - Performance optimizations with React.memo and useCallback
 * - Comprehensive error handling with user feedback
 * - Keyboard navigation support for all interactions
 * - Proper drag-and-drop integration with accessibility
 *
 * Version 2.2.0 Changes:
 * - ADDED: Auto-save functionality with the useAutoSave hook
 * - ADDED: React Icons for better accessibility and styling
 * - IMPROVED: Cleaner action dispatching pattern
 * - IMPROVED: More efficient state updates
 * - IMPROVED: Better drag and drop integration
 * - MAINTAINED: All existing functionality with enhanced performance
 *
 * Connected Files:
 * - frontend/src/courseBuilder/dnd/Sortable.tsx - Drag-and-drop functionality
 * - frontend/src/courseBuilder/components/LessonCard.tsx - Child lesson components
 * - frontend/src/courseBuilder/store/courseSlice.ts - State management
 * - frontend/src/courseBuilder/api/courseBuilderAPI.ts - API operations
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { FaChevronDown, FaChevronUp, FaEdit, FaGripVertical, FaPlus, FaTrash } from 'react-icons/fa';
import { toast } from 'react-toastify';
import api from '../api/courseBuilderAPI';
import Sortable from '../dnd/Sortable';
import useDragTypes from '../dnd/useDragTypes';
import { useAutoSave } from '../hooks/useAutoSave';
import { useCourseStore } from '../store/courseSlice';
import { Module } from '../store/schema';
import { debounce } from '../utils/debounce';
import LessonCard from './LessonCard';

// Enhanced interface with better typing
interface ModuleCardProps {
  module: Module;
  index: number;
  onMove: (dragIndex: number, hoverIndex: number) => void;
  readOnly?: boolean;
  onError?: (error: Error) => void;
  className?: string;
  'data-testid'?: string;
}

/**
 * Enhanced ModuleCard component with memory leak fixes and performance optimizations
 * Represents a single course module in the builder with comprehensive error handling
 */
const ModuleCard: React.FC<ModuleCardProps> = React.memo(({
  module,
  index,
  onMove,
  readOnly = false,
  onError,
  className = '',
  'data-testid': testId = 'module-card',
}) => {
  // State management with proper typing
  const { updateModule, deleteModule, addLesson, reorderLessons } = useCourseStore();
  const [expanded, setExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [moduleTitle, setModuleTitle] = useState(module.title || '');
  const [lessonTitle, setLessonTitle] = useState('');
  const [isAddingLesson, setIsAddingLesson] = useState(false);
  const [showAddLessonForm, setShowAddLessonForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // Refs for cleanup and focus management
  const debouncedSaveOrderRef = useRef<ReturnType<typeof debounce> | null>(null);
  const lessonTitleInputRef = useRef<HTMLInputElement>(null);
  const moduleCardRef = useRef<HTMLDivElement>(null);
  const dragTypes = useDragTypes();

  // New: AutoSave integration
  const { triggerSave } = useAutoSave();

  // Sync local state with module prop changes
  useEffect(() => {
    setModuleTitle(module.title || '');
  }, [module.title]);

  // Create debounced function with proper cleanup
  useEffect(() => {
    debouncedSaveOrderRef.current = debounce(
      async (moduleId: number | string, newOrder: (string | number)[]) => {
        // Skip API call if this is a temporary module or if readOnly
        if (
          readOnly ||
          (typeof moduleId === 'string' && moduleId.startsWith('temp_'))
        ) {
          console.log('Skipping API call for temporary module or readOnly mode:', moduleId);
          return;
        }

        try {
          const updatedLessons = await api.reorderLessons(moduleId, newOrder);
          console.log('Lesson order updated on server:', updatedLessons);
        } catch (error) {
          console.error('Failed to update lesson order on server:', error);
          toast.error('Failed to save lesson order');

          // Report error to parent component
          if (onError) {
            onError(error instanceof Error ? error : new Error('Failed to update lesson order'));
          }
        }
      },
      500
    );

    // Cleanup debounced function on unmount
    return () => {
      if (debouncedSaveOrderRef.current) {
        debouncedSaveOrderRef.current.cancel();
        debouncedSaveOrderRef.current = null;
      }
    };
  }, [readOnly, onError]);

  // Enhanced error handling with user feedback
  const handleError = useCallback((error: Error, context: string) => {
    console.error(`ModuleCard error in ${context}:`, error);
    setLocalError(error.message);

    // Clear error after 5 seconds
    setTimeout(() => setLocalError(null), 5000);

    if (onError) {
      onError(error);
    }
  }, [onError]);

  // Controlled input handler with validation
  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (readOnly) return;

    const newTitle = e.target.value;
    if (newTitle.length <= 200) { // Validate max length
      setModuleTitle(newTitle);
      setLocalError(null);
    } else {
      setLocalError('Module title cannot exceed 200 characters');
    }
  }, [readOnly]);

  // Enhanced save handler with validation and auto-save integration
  const handleSaveTitle = useCallback(async () => {
    if (readOnly || !moduleTitle.trim()) {
      if (!moduleTitle.trim()) {
        setLocalError('Module title cannot be empty');
        return;
      }
      return;
    }

    setIsLoading(true);
    try {
      await updateModule(module.id, { title: moduleTitle.trim() });
      setIsEditing(false);
      setLocalError(null);
      toast.success('Module title updated successfully');
      triggerSave(); // New: Trigger auto-save
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to update module title'), 'handleSaveTitle');
    } finally {
      setIsLoading(false);
    }
  }, [readOnly, moduleTitle, updateModule, module.id, handleError, triggerSave]);

  // Enhanced delete handler with confirmation and auto-save integration
  const handleDelete = useCallback(async () => {
    if (readOnly) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete the module "${module.title}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    setIsLoading(true);
    try {
      await deleteModule(module.id);
      toast.success('Module deleted successfully');
      triggerSave(); // New: Trigger auto-save
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to delete module'), 'handleDelete');
    } finally {
      setIsLoading(false);
    }
  }, [readOnly, module.title, module.id, deleteModule, handleError, triggerSave]);

  // Enhanced lesson creation with comprehensive validation and auto-save integration
  const handleAddLesson = useCallback(async () => {
    if (!lessonTitle.trim()) {
      setLocalError('Lesson title cannot be empty');
      return;
    }

    if (lessonTitle.length > 200) {
      setLocalError('Lesson title cannot exceed 200 characters');
      return;
    }

    setIsAddingLesson(true);
    setLocalError(null);

    try {
      const newLessonData = {
        title: lessonTitle.trim(),
        type: 'reading' as const,
        order: module.lessons?.length ? module.lessons.length + 1 : 1,
        content: '<p>Default lesson content. Edit this to add your lesson material.</p>',
        guest_content: '',
        registered_content: '',
        access_level: 'registered' as const,
        duration_minutes: 15,
      };

      await addLesson(module.id, newLessonData);
      triggerSave(); // New: Trigger auto-save

      // Reset form state
      setLessonTitle('');
      setShowAddLessonForm(false);
      toast.success('Lesson created successfully!');
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to add lesson'), 'handleAddLesson');
    } finally {
      setIsAddingLesson(false);
    }
  }, [lessonTitle, module.lessons?.length, module.id, addLesson, handleError, triggerSave]);

  // Enhanced lesson form management
  const handleSimpleAddLesson = useCallback(() => {
    if (readOnly) return;
    setShowAddLessonForm(true);
    setExpanded(true);
    setLocalError(null);

    // Focus the input after state update
    setTimeout(() => {
      lessonTitleInputRef.current?.focus();
    }, 0);
  }, [readOnly]);

  const handleCancelAddLesson = useCallback(() => {
    setShowAddLessonForm(false);
    setLessonTitle('');
    setLocalError(null);
  }, []);

  // Enhanced lesson reordering with proper error handling and auto-save integration
  const handleMoveLessons = useCallback((dragIndex: number, hoverIndex: number) => {
    if (readOnly || !module.lessons) return;

    try {
      const lessonOrder = [...module.lessons];
      const draggedLesson = lessonOrder[dragIndex];

      if (!draggedLesson) {
        throw new Error('Invalid drag index');
      }

      // Remove the dragged item and insert at new position
      lessonOrder.splice(dragIndex, 1);
      lessonOrder.splice(hoverIndex, 0, draggedLesson);

      // Get the new order of ids
      const newOrder = lessonOrder.map(lesson => lesson.id);

      // Update local state via the store
      reorderLessons(module.id, newOrder);
      triggerSave(); // New: Trigger auto-save

      // Filter out temporary IDs for API call
      const realIds = newOrder.filter(
        id => !(typeof id === 'string' && id.startsWith('temp_'))
      );

      // Make API call if we have real IDs to reorder
      if (realIds.length > 0 && debouncedSaveOrderRef.current) {
        if (typeof module.id === 'number') {
          debouncedSaveOrderRef.current(module.id, realIds);
        } else if (typeof module.id === 'string' && !module.id.startsWith('temp_')) {
          const moduleNumericId = parseInt(module.id, 10);
          if (!isNaN(moduleNumericId)) {
            debouncedSaveOrderRef.current(moduleNumericId, realIds);
          }
        }
      }
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to reorder lessons'), 'handleMoveLessons');
    }
  }, [readOnly, module.lessons, module.id, reorderLessons, handleError, triggerSave]);

  // Enhanced keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (readOnly) return;

    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        setExpanded(!expanded);
        break;
      case 'Escape':
        if (isEditing) {
          setIsEditing(false);
          setModuleTitle(module.title || '');
        }
        if (showAddLessonForm) {
          handleCancelAddLesson();
        }
        break;
    }
  }, [readOnly, expanded, isEditing, showAddLessonForm, module.title, handleCancelAddLesson]);

  // Enhanced lesson title input handler
  const handleLessonTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value;
    if (newTitle.length <= 200) {
      setLessonTitle(newTitle);
      setLocalError(null);
    } else {
      setLocalError('Lesson title cannot exceed 200 characters');
    }
  }, []);

  const handleLessonTitleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'Enter':
        if (!isAddingLesson && lessonTitle.trim()) {
          handleAddLesson();
        }
        break;
      case 'Escape':
        handleCancelAddLesson();
        break;
    }
  }, [isAddingLesson, lessonTitle, handleAddLesson, handleCancelAddLesson]);

  // Memoized computed values for performance
  const containerClasses = useMemo(() => {
    const baseClasses = [
      'bg-white border border-gray-200 rounded-lg shadow-sm mb-4 transition-all duration-200',
      className,
    ];

    if (readOnly) {
      baseClasses.push('opacity-60');
    }

    if (localError) {
      baseClasses.push('border-red-300 bg-red-50');
    }

    if (isLoading) {
      baseClasses.push('opacity-75');
    }

    return baseClasses.filter(Boolean).join(' ');
  }, [className, readOnly, localError, isLoading]);

  const lessonCount = module.lessons?.length || 0;
  const moduleAriaLabel = `Module ${index + 1}: ${module.title || 'Untitled Module'}. ${lessonCount} lesson${lessonCount !== 1 ? 's' : ''}`;

  // Keyboard move handler for accessibility
  const handleKeyboardMove = useCallback((direction: 'up' | 'down', currentIndex: number) => {
    if (readOnly) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    onMove(currentIndex, newIndex);
    triggerSave(); // New: Trigger auto-save
  }, [readOnly, onMove, triggerSave]);

  return (
    <div ref={moduleCardRef} className="module-card-wrapper">
      {/* Error display */}
      {localError && (
        <div className="mb-2 p-2 bg-red-100 border border-red-300 rounded-md text-red-700 text-sm">
          <div className="flex items-center justify-between">
            <span>{localError}</span>
            <button
              onClick={() => setLocalError(null)}
              className="text-red-500 hover:text-red-700"
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <Sortable
        id={module.id}
        index={index}
        type={dragTypes.MODULE}
        onMove={readOnly ? undefined : onMove}
        onKeyboardMove={readOnly ? undefined : handleKeyboardMove}
        className={containerClasses}
        disabled={readOnly || isLoading}
        showDragHandle={!readOnly}
        ariaLabel={moduleAriaLabel}
        data-testid={testId}
      >
        <div className="p-4">
          <div className="flex items-center justify-between">
            {/* Module title section with improved drag handle using React Icons */}
            <div className="flex-1 min-w-0">
              {!readOnly && (
                <span className="inline-block mr-2 text-gray-400 cursor-move" title="Drag to reorder">
                  <FaGripVertical aria-hidden="true" />
                  <span className="sr-only">Drag handle</span>
                </span>
              )}

              {isEditing && !readOnly ? (
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    className="flex-1 border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={moduleTitle}
                    onChange={handleTitleChange}
                    onBlur={handleSaveTitle}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleSaveTitle();
                      } else if (e.key === 'Escape') {
                        setIsEditing(false);
                        setModuleTitle(module.title || '');
                      }
                    }}
                    autoFocus
                    disabled={isLoading}
                    placeholder="Enter module title..."
                    maxLength={200}
                    data-testid="module-title-input"
                    aria-label="Module title"
                  />
                  {isLoading && (
                    <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                  )}
                </div>
              ) : (
                <h3
                  className={`font-medium text-lg truncate ${!readOnly ? 'hover:text-blue-600 cursor-pointer' : 'cursor-default'}`}
                  onClick={() => !readOnly && !isLoading && setIsEditing(true)}
                  onKeyDown={handleKeyDown}
                  tabIndex={readOnly ? -1 : 0}
                  role={readOnly ? undefined : 'button'}
                  data-testid="module-title"
                  aria-expanded={expanded}
                  aria-label={`Edit module: ${module.title || 'Untitled Module'}`}
                  title={module.title || 'Untitled Module'}
                >
                  {module.title || 'Untitled Module'}
                </h3>
              )}
            </div>

            {/* Action buttons with React Icons */}
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={() => !readOnly && !isLoading && setIsEditing(true)}
                className={`p-2 text-gray-600 rounded-md transition-colors ${!readOnly ? 'hover:text-blue-600 hover:bg-gray-100' : 'cursor-not-allowed opacity-50'}`}
                aria-label="Edit module title"
                data-testid="edit-module-btn"
                disabled={readOnly || isLoading}
                title="Edit module title"
              >
                <FaEdit className="w-4 h-4" />
              </button>

              <button
                onClick={handleSimpleAddLesson}
                className={`p-2 text-gray-600 rounded-md transition-colors ${!readOnly ? 'hover:text-green-600 hover:bg-gray-100' : 'cursor-not-allowed opacity-50'}`}
                aria-label="Add lesson"
                data-testid="add-lesson-btn"
                disabled={readOnly || isLoading}
                title="Add lesson"
              >
                <FaPlus className="w-4 h-4" />
              </button>

              <button
                onClick={handleDelete}
                className={`p-2 text-gray-600 rounded-md transition-colors ${!readOnly ? 'hover:text-red-600 hover:bg-gray-100' : 'cursor-not-allowed opacity-50'}`}
                aria-label="Delete module"
                data-testid="delete-module-btn"
                disabled={readOnly || isLoading}
                title="Delete module"
              >
                <FaTrash className="w-4 h-4" />
              </button>

              <button
                onClick={() => setExpanded(!expanded)}
                className="p-2 text-gray-600 rounded-md transition-colors hover:bg-gray-100"
                aria-label={expanded ? 'Collapse module' : 'Expand module'}
                aria-expanded={expanded}
                data-testid="expand-module-btn"
                title={expanded ? 'Collapse module' : 'Expand module'}
              >
                {expanded ? (
                  <FaChevronUp className="w-4 h-4" />
                ) : (
                  <FaChevronDown className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Expanded content */}
          {expanded && (
            <div className="mt-4 pl-4 border-l-2 border-gray-200">
              {/* Add lesson form */}
              {showAddLessonForm && !readOnly && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <input
                        ref={lessonTitleInputRef}
                        type="text"
                        placeholder="Enter lesson title..."
                        value={lessonTitle}
                        onChange={handleLessonTitleChange}
                        onKeyDown={handleLessonTitleKeyDown}
                        disabled={isAddingLesson}
                        maxLength={200}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                        data-testid="lesson-title-input"
                        aria-label="Lesson title"
                      />
                      <button
                        onClick={handleAddLesson}
                        disabled={isAddingLesson || !lessonTitle.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        data-testid="add-lesson-submit-btn"
                      >
                        {isAddingLesson ? (
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            <span>Adding...</span>
                          </div>
                        ) : (
                          'Add Lesson'
                        )}
                      </button>
                      <button
                        onClick={handleCancelAddLesson}
                        disabled={isAddingLesson}
                        className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        data-testid="add-lesson-cancel-btn"
                      >
                        Cancel
                      </button>
                    </div>
                    <p className="text-sm text-gray-600">
                      Press Enter to add the lesson or Escape to cancel
                    </p>
                  </div>
                </div>
              )}

              {/* Lessons list */}
              {lessonCount > 0 ? (
                <div className="space-y-3" role="list" aria-label="Lessons">
                  {module.lessons!.map((lesson, lessonIndex) => (
                    <LessonCard
                      key={`lesson-${lesson.id}-${lessonIndex}`}
                      lesson={lesson}
                      moduleId={module.id}
                      index={lessonIndex}
                      onMove={handleMoveLessons}
                      readOnly={readOnly}
                      data-testid={`lesson-card-${lessonIndex}`}
                    />
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-gray-500">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-lg font-medium mb-2">No lessons yet</p>
                  <p className="text-sm mb-4">Get started by adding your first lesson to this module.</p>
                  {!readOnly && !showAddLessonForm && (
                    <button
                      onClick={() => setShowAddLessonForm(true)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      data-testid="add-first-lesson-btn"
                    >
                      <FaPlus className="w-4 h-4 mr-2" />
                      Add your first lesson
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Sortable>
    </div>
  );
});

ModuleCard.displayName = 'ModuleCard';

export default ModuleCard;
