import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ArticleIcon from '@mui/icons-material/Article';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SchoolIcon from '@mui/icons-material/School';
import { Badge, Button, Card } from '../../../components/common';
import { formatDuration } from '../../../utils/formatDuration';
import { useAIBuilderStore } from '../../store/aiBuilderStore';

const ModulePreview = ({ module, moduleIndex, onEdit, isEditable = true }) => {
  const { updateCourseData, courseData } = useAIBuilderStore();

  const calculateTotalDuration = () => {
    if (!module.lessons) return 0;
    return module.lessons.reduce(
      (total, lesson) =>
        total + (lesson.duration_minutes || lesson.estimatedDuration || 0),
      0
    );
  };

  const getTypeIcon = type => {
    switch (type) {
      case 'video':
        return <PlayArrowIcon style={{ width: '1rem', height: '1rem' }} />;
      case 'reading':
        return <ArticleIcon style={{ width: '1rem', height: '1rem' }} />;
      case 'quiz':
        return <SchoolIcon style={{ width: '1rem', height: '1rem' }} />;
      case 'assignment':
        return <CheckCircleIcon style={{ width: '1rem', height: '1rem' }} />;
      default:
        return <MenuBookIcon style={{ width: '1rem', height: '1rem' }} />;
    }
  };

  const getTypeColor = type => {
    switch (type) {
      case 'video':
        return 'blue';
      case 'reading':
        return 'green';
      case 'quiz':
        return 'purple';
      case 'assignment':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const handleModuleUpdate = (field, value) => {
    if (!isEditable) return;

    const updatedOutline = { ...courseData.outline };
    updatedOutline.modules[moduleIndex][field] = value;
    updateCourseData({ outline: updatedOutline });
  };

  const handleLessonUpdate = (lessonIndex, field, value) => {
    if (!isEditable) return;

    const updatedOutline = { ...courseData.outline };
    updatedOutline.modules[moduleIndex].lessons[lessonIndex][field] = value;
    updateCourseData({ outline: updatedOutline });
  };

  const addNewLesson = () => {
    if (!isEditable) return;

    const newLesson = {
      title: 'New Lesson',
      description: '',
      type: 'reading',
      duration_minutes: 30,
      estimatedDuration: '30 minutes', // Legacy field for compatibility
      content: '',
      resources: [],
      assessment: null,
    };

    const updatedOutline = { ...courseData.outline };
    if (!updatedOutline.modules[moduleIndex].lessons) {
      updatedOutline.modules[moduleIndex].lessons = [];
    }
    updatedOutline.modules[moduleIndex].lessons.push(newLesson);
    updateCourseData({ outline: updatedOutline });
  };

  const removeLesson = lessonIndex => {
    if (!isEditable) return;

    const updatedOutline = { ...courseData.outline };
    updatedOutline.modules[moduleIndex].lessons.splice(lessonIndex, 1);
    updateCourseData({ outline: updatedOutline });
  };

  if (!module) {
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
          <p>No module data available.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      {/* Module Header */}
      <div className="border-b border-gray-200 pb-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <Badge variant="primary" size="sm">
                Module {moduleIndex + 1}
              </Badge>{' '}
              <div className="flex items-center text-sm text-gray-500">
                <AccessTimeIcon
                  style={{
                    width: '1rem',
                    height: '1rem',
                    marginRight: '0.25rem',
                  }}
                />
                {formatDuration(calculateTotalDuration())}
              </div>{' '}
              <div className="flex items-center text-sm text-gray-500">
                <MenuBookIcon
                  style={{
                    width: '1rem',
                    height: '1rem',
                    marginRight: '0.25rem',
                  }}
                />
                {module.lessons?.length || 0} lessons
              </div>
            </div>

            {isEditable ? (
              <input
                type="text"
                value={module.title || ''}
                onChange={e => handleModuleUpdate('title', e.target.value)}
                className="text-xl font-bold text-gray-900 bg-transparent border-none p-0 w-full focus:ring-0"
                placeholder="Module title..."
              />
            ) : (
              <h2 className="text-xl font-bold text-gray-900">
                {module.title}
              </h2>
            )}

            {isEditable ? (
              <textarea
                value={module.description || ''}
                onChange={e =>
                  handleModuleUpdate('description', e.target.value)
                }
                className="mt-2 w-full text-gray-600 bg-transparent border-none p-0 resize-none focus:ring-0"
                placeholder="Module description..."
                rows={3}
              />
            ) : (
              <p className="mt-2 text-gray-600">{module.description}</p>
            )}
          </div>

          {isEditable && onEdit && (
            <Button variant="outline" size="sm" onClick={onEdit}>
              Edit Module
            </Button>
          )}
        </div>

        {/* Learning Objectives */}
        {module.objectives && module.objectives.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Learning Objectives
            </h4>
            <ul className="space-y-1">
              {module.objectives.map((objective, index) => (
                <li
                  key={objective.id || `objective-${index}`}
                  className="flex items-start space-x-2 text-sm text-gray-600"
                >
                  <CheckCircleIcon
                    style={{
                      width: '1rem',
                      height: '1rem',
                      color: '#10B981',
                      marginTop: '0.125rem',
                    }}
                    className="flex-shrink-0"
                  />
                  <span>{objective}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Lessons */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Lessons</h3>
          {isEditable && (
            <Button variant="outline" size="sm" onClick={addNewLesson}>
              Add Lesson
            </Button>
          )}
        </div>

        {module.lessons && module.lessons.length > 0 ? (
          <div className="space-y-3">
            {module.lessons.map((lesson, lessonIndex) => (
              <Card key={lesson.id || lessonIndex} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">
                        {lessonIndex + 1}
                      </span>
                    </div>

                    <div className="flex-1 min-w-0">
                      {isEditable ? (
                        <input
                          type="text"
                          value={lesson.title || ''}
                          onChange={e =>
                            handleLessonUpdate(
                              lessonIndex,
                              'title',
                              e.target.value
                            )
                          }
                          className="block w-full text-base font-medium text-gray-900 bg-transparent border-none p-0 focus:ring-0"
                          placeholder="Lesson title..."
                        />
                      ) : (
                        <h4 className="text-base font-medium text-gray-900">
                          {lesson.title}
                        </h4>
                      )}

                      {isEditable ? (
                        <textarea
                          value={lesson.description || ''}
                          onChange={e =>
                            handleLessonUpdate(
                              lessonIndex,
                              'description',
                              e.target.value
                            )
                          }
                          className="mt-1 w-full text-sm text-gray-600 bg-transparent border-none p-0 resize-none focus:ring-0"
                          placeholder="Lesson description..."
                          rows={2}
                        />
                      ) : (
                        <p className="mt-1 text-sm text-gray-600">
                          {lesson.description}
                        </p>
                      )}

                      <div className="mt-3 flex items-center space-x-4">
                        <Badge
                          variant={getTypeColor(lesson.type)}
                          size="sm"
                          className="flex items-center space-x-1"
                        >
                          {getTypeIcon(lesson.type)}
                          <span className="capitalize">{lesson.type}</span>
                        </Badge>
                        <div className="flex items-center text-sm text-gray-500">
                          <AccessTimeIcon
                            style={{
                              width: '1rem',
                              height: '1rem',
                              marginRight: '0.25rem',
                            }}
                          />
                          {isEditable ? (
                            <div className="flex items-center">
                              <input
                                type="number"
                                value={
                                  lesson.duration_minutes ||
                                  lesson.estimatedDuration ||
                                  ''
                                }
                                onChange={e => {
                                  const minutes = parseInt(e.target.value) || 0;
                                  handleLessonUpdate(
                                    lessonIndex,
                                    'duration_minutes',
                                    minutes
                                  );
                                  // Also update legacy field for compatibility
                                  handleLessonUpdate(
                                    lessonIndex,
                                    'estimatedDuration',
                                    minutes
                                  );
                                }}
                                className="w-16 bg-transparent border-none p-0 focus:ring-0 text-sm"
                                placeholder="30"
                                min="0"
                              />
                              <span className="ml-1">min</span>
                            </div>
                          ) : (
                            formatDuration(
                              lesson.duration_minutes ||
                                lesson.estimatedDuration ||
                                0
                            )
                          )}
                        </div>
                      </div>

                      {/* Lesson Content Preview */}
                      {lesson.content && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <h5 className="text-xs font-medium text-gray-700 mb-1">
                            Content Preview
                          </h5>
                          <p className="text-sm text-gray-600 line-clamp-3">
                            {lesson.content.substring(0, 200)}
                            {lesson.content.length > 200 && '...'}
                          </p>
                        </div>
                      )}

                      {/* Resources */}
                      {lesson.resources && lesson.resources.length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-xs font-medium text-gray-700 mb-1">
                            Resources
                          </h5>
                          <div className="flex flex-wrap gap-1">
                            {lesson.resources.map((resource, resourceIndex) => (
                              <Badge
                                key={
                                  resource.id ||
                                  `resource-${moduleIndex}-${lessonIndex}-${resourceIndex}`
                                }
                                variant="gray"
                                size="xs"
                              >
                                {resource.title ||
                                  resource.name ||
                                  `Resource ${resourceIndex + 1}`}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {isEditable && (
                    <div className="flex items-center space-x-2 ml-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeLesson(lessonIndex)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Remove
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <MenuBookIcon
              style={{
                fontSize: '3rem',
                color: '#D1D5DB',
                marginBottom: '0.75rem',
              }}
              className="mx-auto"
            />
            <p>No lessons in this module yet.</p>
            {isEditable && (
              <Button
                variant="outline"
                size="sm"
                onClick={addNewLesson}
                className="mt-3"
              >
                Add First Lesson
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Module Actions */}
      {isEditable && (
        <div className="mt-6 pt-6 border-t border-gray-200 flex justify-end space-x-3">
          <Button variant="outline">Preview Module</Button>
          <Button variant="primary">Generate Content</Button>
        </div>
      )}
    </Card>
  );
};

export default ModulePreview;
