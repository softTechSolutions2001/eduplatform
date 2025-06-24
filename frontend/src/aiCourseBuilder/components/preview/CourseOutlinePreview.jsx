import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import React from 'react';
import { Button, Card } from '../../../components/common';
import { formatDuration } from '../../../utils/formatDuration';
import { useAIBuilderStore } from '../../store/aiBuilderStore';

const CourseOutlinePreview = ({ outline, onEdit, isEditable = true }) => {
  const { updateCourseData } = useAIBuilderStore();
  const [expandedModules, setExpandedModules] = React.useState(new Set());

  const toggleModule = moduleId => {
    setExpandedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  const calculateTotalDuration = module => {
    if (!module.lessons) return 0;
    return module.lessons.reduce(
      (total, lesson) =>
        total + (lesson.duration_minutes || lesson.estimatedDuration || 0),
      0
    );
  };

  const handleModuleEdit = (moduleIndex, field, value) => {
    if (!isEditable) return;

    const updatedOutline = { ...outline };
    updatedOutline.modules[moduleIndex][field] = value;
    updateCourseData({ outline: updatedOutline });
  };

  const handleLessonEdit = (moduleIndex, lessonIndex, field, value) => {
    if (!isEditable) return;

    const updatedOutline = { ...outline };
    updatedOutline.modules[moduleIndex].lessons[lessonIndex][field] = value;
    updateCourseData({ outline: updatedOutline });
  };

  if (!outline || !outline.modules) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          <MenuBookIcon
            style={{
              fontSize: '3rem',
              color: '#D1D5DB',
              marginBottom: '0.75rem',
            }}
            className="mx-auto"
          />
          <p>No course outline available yet.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Course Outline</h3>
        {isEditable && onEdit && (
          <Button variant="outline" size="sm" onClick={onEdit}>
            Edit Outline
          </Button>
        )}
      </div>

      {/* Course Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-blue-600">
              {outline.modules?.length || 0}
            </div>
            <div className="text-gray-600">Modules</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-green-600">
              {outline.modules?.reduce(
                (total, module) => total + (module.lessons?.length || 0),
                0
              ) || 0}
            </div>
            <div className="text-gray-600">Lessons</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-purple-600">
              {formatDuration(
                outline.modules?.reduce(
                  (total, module) => total + calculateTotalDuration(module),
                  0
                ) || 0
              )}
            </div>
            <div className="text-gray-600">Duration</div>
          </div>
        </div>
      </div>

      {/* Modules List */}
      <div className="space-y-4">
        {outline.modules.map((module, moduleIndex) => (
          <div
            key={module.id || moduleIndex}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            {/* Module Header */}
            <div className="bg-gray-50 p-4">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => toggleModule(moduleIndex)}
                  className="flex items-center space-x-3 text-left flex-1"
                >
                  {' '}
                  {expandedModules.has(moduleIndex) ? (
                    <ExpandMoreIcon
                      style={{ fontSize: '1.25rem', color: '#9CA3AF' }}
                    />
                  ) : (
                    <ChevronRightIcon
                      style={{ fontSize: '1.25rem', color: '#9CA3AF' }}
                    />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-blue-600">
                        Module {moduleIndex + 1}
                      </span>
                      <span className="text-xs text-gray-500">•</span>{' '}
                      <div className="flex items-center text-xs text-gray-500">
                        <AccessTimeIcon
                          style={{
                            width: '0.75rem',
                            height: '0.75rem',
                            marginRight: '0.25rem',
                          }}
                        />
                        {formatDuration(calculateTotalDuration(module))}
                      </div>
                    </div>
                    {isEditable ? (
                      <input
                        type="text"
                        value={module.title || ''}
                        onChange={e =>
                          handleModuleEdit(moduleIndex, 'title', e.target.value)
                        }
                        className="mt-1 block w-full text-sm font-medium text-gray-900 bg-transparent border-none p-0 focus:ring-0"
                        placeholder="Module title..."
                      />
                    ) : (
                      <h4 className="mt-1 text-sm font-medium text-gray-900">
                        {module.title}
                      </h4>
                    )}
                  </div>
                </button>
              </div>

              {isEditable ? (
                <textarea
                  value={module.description || ''}
                  onChange={e =>
                    handleModuleEdit(moduleIndex, 'description', e.target.value)
                  }
                  className="mt-2 w-full text-sm text-gray-600 bg-transparent border-none p-0 resize-none focus:ring-0"
                  placeholder="Module description..."
                  rows={2}
                />
              ) : (
                <p className="mt-2 text-sm text-gray-600">
                  {module.description}
                </p>
              )}
            </div>

            {/* Module Content */}
            {expandedModules.has(moduleIndex) && module.lessons && (
              <div className="p-4 space-y-3">
                {module.lessons.map((lesson, lessonIndex) => (
                  <div
                    key={lesson.id || lessonIndex}
                    className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-blue-600">
                        {lessonIndex + 1}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      {isEditable ? (
                        <input
                          type="text"
                          value={lesson.title || ''}
                          onChange={e =>
                            handleLessonEdit(
                              moduleIndex,
                              lessonIndex,
                              'title',
                              e.target.value
                            )
                          }
                          className="block w-full text-sm font-medium text-gray-900 bg-transparent border-none p-0 focus:ring-0"
                          placeholder="Lesson title..."
                        />
                      ) : (
                        <h5 className="text-sm font-medium text-gray-900">
                          {lesson.title}
                        </h5>
                      )}

                      {isEditable ? (
                        <textarea
                          value={lesson.description || ''}
                          onChange={e =>
                            handleLessonEdit(
                              moduleIndex,
                              lessonIndex,
                              'description',
                              e.target.value
                            )
                          }
                          className="mt-1 w-full text-sm text-gray-500 bg-transparent border-none p-0 resize-none focus:ring-0"
                          placeholder="Lesson description..."
                          rows={1}
                        />
                      ) : (
                        <p className="mt-1 text-sm text-gray-500">
                          {lesson.description}
                        </p>
                      )}

                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-400">
                        <div className="flex items-center">
                          <AccessTimeIcon
                            style={{
                              width: '0.75rem',
                              height: '0.75rem',
                              marginRight: '0.25rem',
                            }}
                          />
                          {isEditable ? (
                            <input
                              type="number"
                              value={
                                lesson.duration_minutes ||
                                lesson.estimatedDuration ||
                                ''
                              }
                              onChange={e =>
                                handleLessonEdit(
                                  moduleIndex,
                                  lessonIndex,
                                  'duration_minutes',
                                  parseInt(e.target.value) || 0
                                )
                              }
                              className="w-12 bg-transparent border-none p-0 focus:ring-0"
                              placeholder="30"
                              min="0"
                            />
                          ) : (
                            formatDuration(
                              lesson.duration_minutes ||
                                lesson.estimatedDuration ||
                                0
                            )
                          )}
                          {isEditable && <span className="ml-1">min</span>}
                        </div>
                        {lesson.type && (
                          <div className="flex items-center">
                            <span className="capitalize">{lesson.type}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      {isEditable && (
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => window.print()}>
            Export Outline
          </Button>
          <Button variant="primary">Generate Content</Button>
        </div>
      )}
    </Card>
  );
};

export default CourseOutlinePreview;
