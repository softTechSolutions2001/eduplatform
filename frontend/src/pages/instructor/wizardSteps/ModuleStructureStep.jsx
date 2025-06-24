/**
 * File: frontend/src/pages/instructor/wizardSteps/ModuleStructureStep.jsx
 * Version: 2.3.1 (Export Fix)
 * Date: 2025-06-20 15:59:12
 * Author: mohithasanthanam
 * Last Modified: 2025-06-20 15:59:12 UTC
 * Fixed By: sujibeautysalon
 *
 * CRITICAL FIX: Added missing React import and corrected export syntax
 */

import { DragDropContext, Draggable, Droppable } from '@hello-pangea/dnd';
import { useState } from 'react';
import Alert from '../../../components/common/Alert';
import Button from '../../../components/common/Button';
import Card from '../../../components/common/Card';
import DurationInput from '../../../components/common/DurationInput';
import FormInput from '../../../components/common/FormInput';
import Tooltip from '../../../components/common/Tooltip';
import {
  createDragDropHandler,
  syncDragDropOrder,
} from '../../../utils/courseDataSync';
import { formatDuration } from '../../../utils/formatDuration';
import { useCourseWizard } from '../CourseWizardContext';

/**
 * Step 3: Module Structure
 */
const ModuleStructureStep = () => {
  const {
    modules,
    addModule,
    updateModule,
    removeModule,
    errors,
    dispatch,
    ACTIONS,
  } = useCourseWizard();

  const [isEditing, setIsEditing] = useState(null);
  const [editData, setEditData] = useState({
    title: '',
    description: '',
    duration_minutes: 0,
  });

  const handleDragEnd = createDragDropHandler({
    items: modules,
    onReorder: reorderedItems => {
      const orderUpdates = syncDragDropOrder(reorderedItems, 'modules');

      orderUpdates.forEach(({ id, order }) => {
        updateModule(id, { order });
      });

      if (dispatch && ACTIONS) {
        dispatch({
          type: ACTIONS.REORDER_MODULES,
          payload: { modules: reorderedItems },
        });
      }
    },
  });

  const handleEditModule = module => {
    setIsEditing(module.id);
    setEditData({
      title: module.title || '',
      description: module.description || '',
      duration_minutes: module.duration_minutes || 0,
    });
  };

  const handleSaveModule = () => {
    if (!editData.title.trim()) {
      return;
    }

    updateModule(isEditing, {
      ...editData,
      title: editData.title.trim(),
      description: editData.description.trim(),
    });

    setIsEditing(null);
    setEditData({ title: '', description: '', duration_minutes: 0 });
  };

  const handleCancelEdit = () => {
    setIsEditing(null);
    setEditData({ title: '', description: '', duration_minutes: 0 });
  };

  const handleCreateModule = () => {
    const newModuleId = addModule({
      title: 'New Module',
      description: '',
      duration_minutes: 0,
      order: modules.length + 1,
    });

    handleEditModule({
      id: newModuleId,
      title: 'New Module',
      description: '',
      duration_minutes: 0,
    });
  };

  const handleRemoveModule = (moduleId) => {
    if (window.confirm('Are you sure you want to remove this module? This action cannot be undone.')) {
      removeModule(moduleId);
    }
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Course Structure</h2>
        <p className="text-gray-600 mt-1">
          Organize your course by creating modules to group related content
        </p>
      </div>

      {errors.modules && <Alert type="error">{errors.modules}</Alert>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {modules.length > 0 ? (
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="modules">
                {(provided, snapshot) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className={`space-y-4 ${snapshot.isDraggingOver ? 'bg-blue-50 rounded-lg p-2' : ''}`}
                  >
                    {modules
                      .sort((a, b) => a.order - b.order)
                      .map((module, index) => (
                        <Draggable
                          key={module.id}
                          draggableId={String(module.id)}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              className={`border rounded-lg overflow-hidden bg-white shadow-sm transition-all duration-200 ${snapshot.isDragging
                                ? 'shadow-lg scale-102 rotate-1 z-50'
                                : 'hover:shadow-md'
                                }`}
                            >
                              {isEditing === module.id ? (
                                <div className="p-4 bg-blue-50">
                                  <h4 className="font-medium text-blue-900 mb-3">
                                    Edit Module {index + 1}
                                  </h4>

                                  <FormInput
                                    label="Module Title"
                                    value={editData.title}
                                    onChange={e =>
                                      setEditData({
                                        ...editData,
                                        title: e.target.value,
                                      })
                                    }
                                    placeholder="Enter module title"
                                    required
                                    className="mb-3"
                                  />

                                  <div className="form-group mb-3">
                                    <label className="block text-gray-700 font-medium mb-1">
                                      Description
                                    </label>
                                    <textarea
                                      rows={3}
                                      className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                                      value={editData.description}
                                      onChange={e =>
                                        setEditData({
                                          ...editData,
                                          description: e.target.value,
                                        })
                                      }
                                      placeholder="Enter module description (optional)"
                                    />
                                  </div>

                                  <DurationInput
                                    label="Estimated Duration"
                                    value={editData.duration_minutes || 0}
                                    onChange={minutes =>
                                      setEditData({
                                        ...editData,
                                        duration_minutes: minutes,
                                      })
                                    }
                                    placeholder="Select module duration"
                                    className="mb-3"
                                  />

                                  {editData.duration_minutes > 0 && (
                                    <p className="mb-3 text-sm text-gray-600">
                                      Duration: {formatDuration(editData.duration_minutes)}
                                    </p>
                                  )}

                                  <div className="flex justify-end space-x-2">
                                    <Button
                                      variant="outline"
                                      onClick={handleCancelEdit}
                                    >
                                      Cancel
                                    </Button>
                                    <Button
                                      variant="primary"
                                      onClick={handleSaveModule}
                                      disabled={!editData.title.trim()}
                                    >
                                      Save Module
                                    </Button>
                                  </div>
                                </div>
                              ) : (
                                <div>
                                  <div
                                    {...provided.dragHandleProps}
                                    className="bg-gray-50 p-4 flex items-center justify-between cursor-move hover:bg-gray-100 transition-colors"
                                  >
                                    <div className="flex items-center">
                                      <div className="flex-shrink-0 mr-3 text-gray-400">
                                        <svg
                                          className="h-5 w-5"
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
                                      <h3 className="font-medium text-gray-900">
                                        {index + 1}. {module.title || 'Untitled Module'}
                                      </h3>
                                    </div>

                                    <div className="flex space-x-1">
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleEditModule(module);
                                        }}
                                        className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-100 rounded transition-colors"
                                        aria-label="Edit module"
                                        title="Edit module"
                                      >
                                        <svg
                                          className="h-4 w-4"
                                          fill="none"
                                          viewBox="0 0 24 24"
                                          stroke="currentColor"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                          />
                                        </svg>
                                      </button>
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleRemoveModule(module.id);
                                        }}
                                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-100 rounded transition-colors"
                                        aria-label="Remove module"
                                        title="Remove module"
                                      >
                                        <svg
                                          className="h-4 w-4"
                                          fill="none"
                                          viewBox="0 0 24 24"
                                          stroke="currentColor"
                                        >
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                          />
                                        </svg>
                                      </button>
                                    </div>
                                  </div>

                                  <div className="p-4">
                                    {module.description ? (
                                      <p className="text-gray-600 text-sm mb-3">
                                        {module.description}
                                      </p>
                                    ) : (
                                      <p className="text-gray-400 text-sm italic mb-3">
                                        No description provided
                                      </p>
                                    )}

                                    <div className="flex items-center justify-between text-sm text-gray-500">
                                      <div className="flex items-center">
                                        {(module.duration_minutes > 0 || module.duration) && (
                                          <>
                                            <svg
                                              className="h-4 w-4 mr-1"
                                              fill="none"
                                              viewBox="0 0 24 24"
                                              stroke="currentColor"
                                            >
                                              <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                              />
                                            </svg>
                                            <span>
                                              {module.duration_minutes > 0
                                                ? formatDuration(module.duration_minutes)
                                                : module.duration}
                                            </span>
                                          </>
                                        )}
                                      </div>

                                      {module.lessons && module.lessons.length > 0 && (
                                        <div className="flex items-center">
                                          <svg
                                            className="h-4 w-4 mr-1"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                                            />
                                          </svg>
                                          <span>
                                            {module.lessons.length} lesson{module.lessons.length !== 1 ? 's' : ''}
                                          </span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </Draggable>
                      ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No modules yet
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first module.
              </p>
              <div className="mt-6">
                <Button variant="primary" onClick={handleCreateModule}>
                  <svg
                    className="h-5 w-5 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                  Create Your First Module
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="font-medium mb-3 text-gray-900">Module Structure Tips</h3>
            <ul className="space-y-3 text-sm text-gray-600">
              <li className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Group related content into modules (chapters)</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Aim for 3-7 modules in a typical course</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Use clear, descriptive module titles</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Arrange modules in a logical sequence</span>
              </li>
              <li className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Drag and drop to reorder modules</span>
              </li>
            </ul>
          </Card>

          <div className="sticky top-4">
            <Button
              variant="primary"
              className="w-full mb-3"
              onClick={handleCreateModule}
            >
              <svg
                className="h-5 w-5 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Add New Module
            </Button>

            {modules.length > 0 && (
              <div className="text-center">
                <Tooltip content="You'll add lessons to your modules in the next step">
                  <div className="inline-block">
                    <p className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                      {modules.length} module{modules.length !== 1 ? 's' : ''} created
                    </p>
                  </div>
                </Tooltip>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// CRITICAL: Ensure proper default export
export default ModuleStructureStep;
