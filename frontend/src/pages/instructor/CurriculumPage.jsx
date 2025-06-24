/**
 * File: frontend/src/pages/instructor/CurriculumPage.jsx
 * Version: 1.0.0
 * Date: 2025-05-26 10:50:33
 * Author: mohithasanthanam
 * Last Modified: 2025-05-26 10:50:33 UTC
 *
 * Course Curriculum Management Page
 *
 * This component provides a comprehensive interface for managing a course's curriculum:
 * - View, add, edit, and reorder modules
 * - View, add, edit, and reorder lessons within modules
 * - Quick links to detailed editors for modules and lessons
 * - Drag-and-drop reordering of content
 *
 * Features:
 * 1. Expandable/collapsible module sections
 * 2. Drag-and-drop reordering of modules and lessons
 * 3. Inline editing for quick updates
 * 4. Detailed summary of course structure
 * 5. Direct links to dedicated editors for complex changes
 * 6. Responsive design for all device sizes
 */

import { Disclosure, Transition } from '@headlessui/react';
import {
  ChevronDownIcon,
  ChevronUpIcon,
  PencilIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/react/solid';
import { useCallback, useEffect, useState } from 'react';
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Alert from '../../components/common/Alert';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { ContentCreationErrorBoundary } from '../../components/common/errorBoundaries';
import LoadingScreen from '../../components/common/LoadingScreen';
import MainLayout from '../../components/layouts/MainLayout';
import { useAuth } from '../../contexts/AuthContext';
import instructorService from '../../services/instructorService';

const CurriculumPage = () => {
  const { courseSlug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isInstructor } = useAuth();

  const [courseData, setCourseData] = useState(null);
  const [modules, setModules] = useState([]);
  const [expandedModules, setExpandedModules] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [reorderingModules, setReorderingModules] = useState(false);
  const [reorderingLessons, setReorderingLessons] = useState(false);

  // Keep track of which module we're editing lessons for
  const [activeModuleId, setActiveModuleId] = useState(null);

  // Function to toggle module expansion
  const toggleModule = moduleId => {
    setExpandedModules(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  // Check authentication and redirect if needed
  useEffect(() => {
    if (isAuthenticated === false) {
      navigate(
        '/login?redirect=' + encodeURIComponent(window.location.pathname)
      );
    } else if (isAuthenticated === true && !isInstructor()) {
      navigate('/');
    }
  }, [isAuthenticated, isInstructor, navigate]);

  // Fetch course data and modules
  const fetchCourseData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch course data
      const course = await instructorService.getCourseBySlug(courseSlug);
      setCourseData(course);

      // Fetch modules for this course
      const modulesData = await instructorService.getModules(course.id);
      const sortedModules = Array.isArray(modulesData)
        ? [...modulesData].sort((a, b) => a.order - b.order)
        : [];

      setModules(sortedModules);

      // Initialize expanded state for modules
      const initialExpandedState = {};
      sortedModules.forEach(module => {
        initialExpandedState[module.id] = false;
      });
      setExpandedModules(initialExpandedState);

      // Fetch lessons for each module
      for (const module of sortedModules) {
        try {
          const lessonsData = await instructorService.getLessons(module.id);
          const sortedLessons = Array.isArray(lessonsData)
            ? [...lessonsData].sort((a, b) => a.order - b.order)
            : [];

          // Update the module with its lessons
          setModules(prevModules =>
            prevModules.map(m =>
              m.id === module.id ? { ...m, lessons: sortedLessons } : m
            )
          );
        } catch (lessonError) {
          console.error(
            `Error fetching lessons for module ${module.id}:`,
            lessonError
          );
        }
      }
    } catch (err) {
      console.error('Error fetching course curriculum data:', err);
      setError(
        err.message || 'Failed to load course curriculum. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  }, [courseSlug]);

  useEffect(() => {
    if (courseSlug) {
      fetchCourseData();
    }
  }, [courseSlug, fetchCourseData]);

  // Handle drag and drop reordering
  const handleDragEnd = async result => {
    // Dropped outside a droppable area
    if (!result.destination) {
      return;
    }

    const { source, destination, type } = result;

    // If dropped in the same position
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return;
    }

    // Handle module reordering
    if (type === 'module') {
      const reorderedModules = Array.from(modules);
      const [movedModule] = reorderedModules.splice(source.index, 1);
      reorderedModules.splice(destination.index, 0, movedModule);

      // Update order property for each module
      const updatedModules = reorderedModules.map((module, index) => ({
        ...module,
        order: index + 1,
      }));

      // Optimistically update UI
      setModules(updatedModules);

      try {
        setReorderingModules(true);

        // Send reordering request to backend
        await instructorService.updateModuleOrder(
          courseSlug,
          updatedModules.map(m => ({ id: m.id, order: m.order }))
        );

        setSuccessMessage('Module order updated successfully.');

        // Clear success message after a delay
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      } catch (error) {
        console.error('Error updating module order:', error);
        setError('Failed to update module order. Please try again.');

        // Revert to original order
        fetchCourseData();
      } finally {
        setReorderingModules(false);
      }
    }
    // Handle lesson reordering within a module
    else if (type === 'lesson') {
      const moduleId = source.droppableId;

      // Find the module
      const moduleIndex = modules.findIndex(m => m.id.toString() === moduleId);
      if (moduleIndex === -1) return;

      const module = modules[moduleIndex];
      const lessons = Array.from(module.lessons || []);

      // Reorder lessons
      const [movedLesson] = lessons.splice(source.index, 1);
      lessons.splice(destination.index, 0, movedLesson);

      // Update order property for each lesson
      const updatedLessons = lessons.map((lesson, index) => ({
        ...lesson,
        order: index + 1,
      }));

      // Optimistically update UI
      const updatedModules = [...modules];
      updatedModules[moduleIndex] = {
        ...module,
        lessons: updatedLessons,
      };

      setModules(updatedModules);

      try {
        setReorderingLessons(true);
        setActiveModuleId(moduleId);

        // Send reordering request to backend
        await instructorService.updateLessonOrder(
          moduleId,
          updatedLessons.map(l => ({ id: l.id, order: l.order }))
        );

        setSuccessMessage('Lesson order updated successfully.');

        // Clear success message after a delay
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      } catch (error) {
        console.error('Error updating lesson order:', error);
        setError('Failed to update lesson order. Please try again.');

        // Revert to original order
        fetchCourseData();
      } finally {
        setReorderingLessons(false);
        setActiveModuleId(null);
      }
    }
  };

  // Handle module deletion
  const handleDeleteModule = async moduleId => {
    if (
      !window.confirm(
        'Are you sure you want to delete this module? This will also delete all lessons within this module.'
      )
    ) {
      return;
    }

    try {
      await instructorService.deleteModule(moduleId);

      // Update UI
      setModules(prevModules => prevModules.filter(m => m.id !== moduleId));

      setSuccessMessage('Module deleted successfully.');

      // Clear success message after a delay
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (error) {
      console.error('Error deleting module:', error);
      setError('Failed to delete module. Please try again.');
    }
  };

  // Handle lesson deletion
  const handleDeleteLesson = async (moduleId, lessonId) => {
    if (
      !window.confirm(
        'Are you sure you want to delete this lesson? This action cannot be undone.'
      )
    ) {
      return;
    }

    try {
      await instructorService.deleteLesson(lessonId);

      // Update UI
      setModules(prevModules =>
        prevModules.map(module =>
          module.id === moduleId
            ? {
                ...module,
                lessons: module.lessons.filter(
                  lesson => lesson.id !== lessonId
                ),
              }
            : module
        )
      );

      setSuccessMessage('Lesson deleted successfully.');

      // Clear success message after a delay
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (error) {
      console.error('Error deleting lesson:', error);
      setError('Failed to delete lesson. Please try again.');
    }
  };

  // Loading state
  if (loading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading course curriculum..." />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Course Curriculum</h1>
            {courseData && (
              <p className="text-gray-600">
                {courseData.title} - {modules.length} modules,{' '}
                {modules.reduce(
                  (count, module) => count + (module.lessons?.length || 0),
                  0
                )}{' '}
                lessons
              </p>
            )}
          </div>

          <div className="flex flex-col sm:flex-row gap-2 mt-4 md:mt-0">
            <Button
              variant="primary"
              onClick={() =>
                navigate(`/instructor/courses/${courseSlug}/modules/new`)
              }
            >
              <PlusIcon className="h-5 w-5 mr-1" />
              Add Module
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate(`/instructor/courses/${courseSlug}/edit`)}
            >
              Edit Course Details
            </Button>
          </div>
        </div>

        {error && (
          <Alert type="error" className="mb-6">
            {error}
          </Alert>
        )}

        {successMessage && (
          <Alert type="success" className="mb-6">
            {successMessage}
          </Alert>
        )}

        <Card className="p-6">
          {modules.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">
                This course doesn't have any modules yet.
              </p>
              <Button
                variant="primary"
                onClick={() =>
                  navigate(`/instructor/courses/${courseSlug}/modules/new`)
                }
              >
                Add Your First Module
              </Button>
            </div>
          ) : (
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="modules" type="module">
                {provided => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className="space-y-4"
                  >
                    {modules.map((module, index) => (
                      <Draggable
                        key={module.id.toString()}
                        draggableId={module.id.toString()}
                        index={index}
                      >
                        {provided => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            className="border border-gray-200 rounded-lg overflow-hidden"
                          >
                            <Disclosure
                              defaultOpen={expandedModules[module.id]}
                            >
                              {({ open }) => (
                                <>
                                  <Disclosure.Button
                                    className="w-full bg-gray-50 p-4 flex justify-between items-center"
                                    onClick={() => toggleModule(module.id)}
                                  >
                                    <div className="flex items-center">
                                      <div
                                        {...provided.dragHandleProps}
                                        className="mr-3 p-1 cursor-move"
                                      >
                                        <svg
                                          xmlns="http://www.w3.org/2000/svg"
                                          className="h-5 w-5 text-gray-400"
                                          fill="none"
                                          viewBox="0 0 24 24"
                                          stroke="currentColor"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M4 8h16M4 16h16"
                                          />
                                        </svg>
                                      </div>
                                      <div className="text-left">
                                        <span className="text-gray-500 text-sm mr-2">
                                          Module {module.order}:
                                        </span>
                                        <span className="font-medium">
                                          {module.title}
                                        </span>
                                      </div>
                                    </div>

                                    <div className="flex items-center">
                                      <span className="text-sm text-gray-500 mr-3">
                                        {module.lessons?.length || 0} lessons
                                      </span>
                                      <Link
                                        to={`/instructor/courses/${courseSlug}/modules/${module.id}/edit`}
                                        className="p-1 text-blue-600 hover:text-blue-800 mr-1"
                                        onClick={e => e.stopPropagation()}
                                      >
                                        <PencilIcon className="h-5 w-5" />
                                      </Link>
                                      <button
                                        type="button"
                                        className="p-1 text-red-600 hover:text-red-800 mr-2"
                                        onClick={e => {
                                          e.stopPropagation();
                                          handleDeleteModule(module.id);
                                        }}
                                      >
                                        <TrashIcon className="h-5 w-5" />
                                      </button>
                                      {open ? (
                                        <ChevronUpIcon className="h-5 w-5" />
                                      ) : (
                                        <ChevronDownIcon className="h-5 w-5" />
                                      )}
                                    </div>
                                  </Disclosure.Button>

                                  <Transition
                                    show={open}
                                    enter="transition duration-100 ease-out"
                                    enterFrom="transform scale-95 opacity-0"
                                    enterTo="transform scale-100 opacity-100"
                                    leave="transition duration-75 ease-out"
                                    leaveFrom="transform scale-100 opacity-100"
                                    leaveTo="transform scale-95 opacity-0"
                                  >
                                    <Disclosure.Panel
                                      static
                                      className="p-4 bg-white"
                                    >
                                      <div className="mb-4 flex justify-between items-center">
                                        <h3 className="font-medium">Lessons</h3>
                                        <Link
                                          to={`/instructor/courses/${courseSlug}/modules/${module.id}/lessons/new`}
                                          className="text-sm text-primary-600 hover:text-primary-800 flex items-center"
                                        >
                                          <PlusIcon className="h-4 w-4 mr-1" />
                                          Add Lesson
                                        </Link>
                                      </div>

                                      {!module.lessons ||
                                      module.lessons.length === 0 ? (
                                        <p className="text-gray-500 text-sm">
                                          No lessons in this module yet.
                                        </p>
                                      ) : (
                                        <Droppable
                                          droppableId={module.id.toString()}
                                          type="lesson"
                                        >
                                          {provided => (
                                            <div
                                              {...provided.droppableProps}
                                              ref={provided.innerRef}
                                              className="space-y-2"
                                            >
                                              {module.lessons.map(
                                                (lesson, index) => (
                                                  <Draggable
                                                    key={lesson.id.toString()}
                                                    draggableId={lesson.id.toString()}
                                                    index={index}
                                                  >
                                                    {provided => (
                                                      <div
                                                        ref={provided.innerRef}
                                                        {...provided.draggableProps}
                                                        {...provided.dragHandleProps}
                                                        className="flex items-center justify-between p-3 bg-gray-50 rounded-md border border-gray-100 hover:bg-gray-100"
                                                      >
                                                        <div className="flex items-center">
                                                          <span className="text-gray-500 text-sm mr-2">
                                                            {lesson.order}.
                                                          </span>
                                                          <span>
                                                            {lesson.title}
                                                          </span>
                                                        </div>

                                                        <div className="flex items-center">
                                                          <Link
                                                            to={`/instructor/courses/${courseSlug}/modules/${module.id}/lessons/${lesson.id}/edit`}
                                                            className="p-1 text-blue-600 hover:text-blue-800 mr-1"
                                                          >
                                                            <PencilIcon className="h-4 w-4" />
                                                          </Link>
                                                          <button
                                                            type="button"
                                                            className="p-1 text-red-600 hover:text-red-800"
                                                            onClick={() =>
                                                              handleDeleteLesson(
                                                                module.id,
                                                                lesson.id
                                                              )
                                                            }
                                                          >
                                                            <TrashIcon className="h-4 w-4" />
                                                          </button>
                                                        </div>
                                                      </div>
                                                    )}
                                                  </Draggable>
                                                )
                                              )}
                                              {provided.placeholder}
                                            </div>
                                          )}
                                        </Droppable>
                                      )}
                                    </Disclosure.Panel>
                                  </Transition>
                                </>
                              )}
                            </Disclosure>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          )}
        </Card>
      </div>
    </MainLayout>
  );
};

export default function CurriculumPageWithErrorBoundary() {
  const navigate = useNavigate();
  const { courseSlug } = useParams();

  const handleNavigateBack = () => {
    navigate(`/instructor/courses/${courseSlug}`); // Go back to course detail
  };

  const handleSaveContent = () => {
    // Trigger auto-save functionality if available
    const event = new CustomEvent('triggerCurriculumAutoSave');
    window.dispatchEvent(event);
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Curriculum Management Error:', {
      error,
      errorInfo,
      context,
    });
    // Could send to error tracking service here
  };

  return (
    <ContentCreationErrorBoundary
      onNavigateBack={handleNavigateBack}
      onSaveContent={handleSaveContent}
      onError={handleError}
    >
      <CurriculumPage />
    </ContentCreationErrorBoundary>
  );
}
