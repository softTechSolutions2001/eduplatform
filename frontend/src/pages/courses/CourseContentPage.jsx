/**
 * File: frontend/src/pages/courses/CourseContentPage.jsx
 * Version: 1.1.0
 * Date: 2025-05-16 18:55:23
 * Author: cadsanthanam (Updated by GitHub Copilot)
 *
 * Course Content Page component for displaying lesson content with tiered access
 *
 * This component:
 * 1. Displays lesson content according to user's access level
 * 2. Provides tabbed interface for content, resources, assessments, and notes
 * 3. Tracks user progress through the course
 * 4. Supports navigation between lessons and modules
 * 5. Implements note-taking functionality for users
 *
 * Access levels handled:
 * - basic: Unregistered users - preview content
 * - intermediate: Registered users - standard content
 * - advanced: Premium/paid users - full content with premium resources
 *
 * Changes in v1.1.0:
 * - Fixed tab switching issues with key={activeTab} on tab content parent div
 * - Added handleTabChange to normalize tab values from Tabs component
 * - Added auto-focus for notes textarea when opening Notes tab
 */

import { useEffect, useRef, useState } from 'react';
import ReactPlayer from 'react-player';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  Badge,
  Button,
  Card,
  ContentAccessController,
  LoadingScreen,
  ProgressBar,
  Spinner,
  Tabs,
} from '../../components/common';
import { CourseContentErrorBoundary } from '../../components/common/errorBoundaries';
import { MainLayout } from '../../components/layouts';
import { useAuth } from '../../contexts/AuthContext';
import { courseService } from '../../services/api';
import LearningHeaderArea from './LearningHeaderWidgets';

// Tab identifiers
export const TABS = {
  CONTENT: 'content',
  RESOURCES: 'resources',
  ASSESSMENT: 'assessment',
  NOTES: 'notes',
};

const TAB_ORDER = [TABS.CONTENT, TABS.RESOURCES, TABS.ASSESSMENT, TABS.NOTES];

// Validate lesson content and provide helpful feedback
const validateLessonContent = (lesson, isAuthenticated, userAccessLevel) => {
  if (!lesson) return { isValid: false, message: 'Lesson not found' };

  if (!lesson.content && !lesson.guest_content && !lesson.registered_content) {
    return {
      isValid: false,
      message:
        'This lesson does not have any content available. Please contact the instructor.',
    };
  }

  if (lesson.is_restricted && !isAuthenticated) {
    return {
      isValid: false,
      message: 'Please sign in to access this lesson content.',
    };
  }

  if (lesson.access_level === 'premium' && userAccessLevel !== 'premium') {
    return {
      isValid: false,
      message:
        'This is premium content. Please upgrade your subscription to access it.',
    };
  }

  return { isValid: true, message: '' };
};

const CourseContentPage = ({ previewMode = false }) => {
  // ─── UTILITY FUNCTIONS ─────────────────────────────────────────────────────
  // NOTE: The backend LessonSerializer already handles content access control
  // and provides the appropriate content in the 'content' field based on user access level.
  // This utility function is now simplified since we can trust the backend logic.
  const getContentField = (lesson, fieldType) => {
    if (!lesson) return '';

    // Add debug logging to understand what fields are available in the lesson object
    if (process.env.NODE_ENV === 'development' && lesson) {
      console.log(`getContentField called for ${fieldType}:`, {
        lesson: lesson.title,
        hasContent: !!lesson.content,
        contentLength: lesson.content?.length || 0,
        accessLevel: lesson.access_level,
        isRestricted: lesson.is_restricted,
      });
    }

    // The backend serializer handles access control and provides appropriate content
    // in the 'content' field, so we just return that directly
    return lesson.content || '';
  };

  // ─── STATE AND HOOKS ─────────────────────────────────────────────────────
  const { courseSlug, moduleId, lessonId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, currentUser, getAccessLevel, canAccessContent } =
    useAuth();

  const userAccessLevel = getAccessLevel();

  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [course, setCourse] = useState(null);
  const [module, setModule] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [modules, setModules] = useState([]);
  const [activeTab, setActiveTab] = useState(TABS.CONTENT);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userNote, setUserNote] = useState('');
  const [savedNotes, setSavedNotes] = useState([]);
  const [noteSaving, setNoteSaving] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [markingComplete, setMarkingComplete] = useState(false);

  // Refs
  const contentRef = useRef(null);
  const noteInputRef = useRef(null);

  // Normalize tab value - handles various possible values from Tabs component

  const handleTabChange = (eventOrValue, maybeValue) => {
    let newVal =
      typeof eventOrValue === 'string'
        ? eventOrValue
        : typeof maybeValue === 'string'
          ? maybeValue
          : // ⇣ if it’s a number (the usual “index” pattern)
            typeof eventOrValue === 'number'
            ? TAB_ORDER[eventOrValue]
            : typeof maybeValue === 'number'
              ? TAB_ORDER[maybeValue]
              : eventOrValue?.target?.dataset?.tabId;

    // safety-net: unknown → stick with current tab instead of resetting
    if (!newVal || !Object.values(TABS).includes(newVal)) return;

    setActiveTab(newVal);
  };

  // Auto-focus notes textarea when opening Notes tab
  useEffect(() => {
    if (activeTab === TABS.NOTES && noteInputRef.current) {
      noteInputRef.current.focus();
    }
  }, [activeTab]);

  // Effect for fetching course data
  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        setLoading(true);

        // Fetch course details first
        const courseResponse = await courseService.getCourseBySlug(courseSlug);
        const courseData = courseResponse.data || courseResponse;

        setCourse(courseData);

        // Set modules from course data
        if (courseData.modules?.length > 0) {
          setModules(courseData.modules);
        }

        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch course details:', err);
        setError('Failed to load course information. Please try again later.');
        setLoading(false);
      }
    };

    fetchCourseDetails();
  }, [courseSlug]);

  // Effect for fetching module and lesson data
  useEffect(() => {
    const fetchModuleAndLesson = async () => {
      if (!moduleId || !lessonId) return;

      try {
        setLoading(true);

        // Fetch module details
        const moduleResponse = await courseService.getModuleDetails(moduleId);
        const moduleData = moduleResponse.data || moduleResponse;
        setModule(moduleData);

        // Find the current lesson in the module
        const currentLesson = moduleData?.lessons?.find(
          l => l.id.toString() === lessonId.toString()
        );

        if (currentLesson) {
          // Debug logging - log the lesson structure to see what fields are available
          console.log('Lesson loaded successfully:', {
            lessonTitle: currentLesson.title,
            lessonId: currentLesson.id,
            hasContent: !!currentLesson.content,
            contentLength: currentLesson.content?.length || 0,
            accessLevel: currentLesson.access_level,
            isRestricted: currentLesson.is_restricted,
            userAccessLevel: userAccessLevel,
            isAuthenticated: isAuthenticated,
            userId: currentUser?.id,
            userEmail: currentUser?.email,
          });

          setLesson(currentLesson);

          // If lesson has assessment and tab isn't already set, show assessment tab
          if (currentLesson.has_assessment && activeTab !== TABS.ASSESSMENT) {
            // Keep on content tab by default, user can click to see assessment
            setActiveTab(TABS.CONTENT);
          }

          // Fetch user notes for this lesson if authenticated
          if (isAuthenticated) {
            try {
              const notesResponse =
                await courseService.note.getNotesForLesson(lessonId);
              const notesData = notesResponse.data || notesResponse;
              if (notesData && notesData.length > 0) {
                setSavedNotes(notesData);
                // Set the most recent note as the current note
                setUserNote(notesData[0].content);
              }
            } catch (noteErr) {
              console.warn('Failed to fetch notes:', noteErr);
              // Non-critical error, don't show to user
            }
          }
        } else {
          console.error('Lesson not found in module');
          setError('Lesson not found. It may have been moved or deleted.');
        }

        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch module or lesson:', err);
        setError('Failed to load lesson content. Please try again later.');
        setLoading(false);
      }
    };

    fetchModuleAndLesson();
  }, [moduleId, lessonId, isAuthenticated]);

  // Scroll to top when lesson changes
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTo(0, 0);
    }

    // Reset video progress when lesson changes
    setVideoProgress(0);

    // Reset active tab when lesson changes (but keep on assessment if coming to a lesson with an assessment)
    if (lesson?.has_assessment) {
      setActiveTab(prevTab =>
        prevTab === TABS.ASSESSMENT ? TABS.ASSESSMENT : TABS.CONTENT
      );
    } else {
      setActiveTab(TABS.CONTENT);
    }
  }, [lessonId]);

  // Handle saving notes
  const handleSaveNote = async () => {
    if (!isAuthenticated || !userNote.trim() || !lessonId) {
      return;
    }

    try {
      setNoteSaving(true);

      // Check if we're updating an existing note or creating a new one
      if (savedNotes.length > 0) {
        await courseService.note.updateNote(savedNotes[0].id, {
          lesson: lessonId,
          content: userNote,
        });
      } else {
        await courseService.note.createNote({
          lesson: lessonId,
          content: userNote,
        });
      }

      // Refresh notes
      const notesResponse =
        await courseService.note.getNotesForLesson(lessonId);
      const notesData = notesResponse.data || notesResponse;
      setSavedNotes(notesData);

      setNoteSaving(false);
    } catch (err) {
      console.error('Failed to save note:', err);
      setNoteSaving(false);
      // Show a simple inline error
      alert('Failed to save your note. Please try again.');
    }
  };

  // Handle marking lesson as complete
  const handleMarkComplete = async () => {
    if (!isAuthenticated || !lessonId) {
      return;
    }

    try {
      setMarkingComplete(true);

      // Calculate time spent (in seconds) - simplified version
      const timeSpent = Math.floor(videoProgress) || 0;

      const response = await courseService.completeLesson(lessonId, timeSpent);

      // Update the UI to show lesson as completed
      if (response && lesson) {
        setLesson({
          ...lesson,
          is_completed: true,
        });

        // If course is available, update the progress information
        if (course) {
          setCourse({
            ...course,
            user_progress: response.progress,
          });
        }

        // Show success message
        alert('Lesson marked as complete!');
      }

      setMarkingComplete(false);
    } catch (err) {
      console.error('Failed to mark lesson as complete:', err);
      setMarkingComplete(false);
      alert('Failed to mark lesson as complete. Please try again.');
    }
  };

  // Handle navigation to another lesson
  const handleNavigateToLesson = (moduleId, lessonId) => {
    navigate(`/courses/${courseSlug}/content/${moduleId}/${lessonId}`);
  };

  // Get the next and previous lessons for navigation
  const getAdjacentLessons = () => {
    if (!modules.length || !moduleId || !lessonId) {
      return { nextLesson: null, prevLesson: null };
    }

    let currentModuleIndex = -1;
    let currentLessonIndex = -1;

    // Find current indices
    modules.forEach((mod, mIdx) => {
      if (mod.id.toString() === moduleId.toString()) {
        currentModuleIndex = mIdx;

        if (mod.lessons) {
          mod.lessons.forEach((les, lIdx) => {
            if (les.id.toString() === lessonId.toString()) {
              currentLessonIndex = lIdx;
            }
          });
        }
      }
    });

    // Calculate next lesson
    let nextLesson = null;

    if (currentModuleIndex >= 0 && currentLessonIndex >= 0) {
      const currentModule = modules[currentModuleIndex];

      // Check if there's another lesson in the same module
      if (currentLessonIndex < currentModule.lessons.length - 1) {
        nextLesson = {
          moduleId: currentModule.id,
          lessonId: currentModule.lessons[currentLessonIndex + 1].id,
        };
      }
      // Check if there's another module
      else if (currentModuleIndex < modules.length - 1) {
        const nextModule = modules[currentModuleIndex + 1];
        if (nextModule.lessons && nextModule.lessons.length > 0) {
          nextLesson = {
            moduleId: nextModule.id,
            lessonId: nextModule.lessons[0].id,
          };
        }
      }
    }

    // Calculate previous lesson
    let prevLesson = null;

    if (currentModuleIndex >= 0 && currentLessonIndex >= 0) {
      const currentModule = modules[currentModuleIndex];

      // Check if there's a previous lesson in the same module
      if (currentLessonIndex > 0) {
        prevLesson = {
          moduleId: currentModule.id,
          lessonId: currentModule.lessons[currentLessonIndex - 1].id,
        };
      }
      // Check if there's a previous module
      else if (currentModuleIndex > 0) {
        const prevModule = modules[currentModuleIndex - 1];
        if (prevModule.lessons && prevModule.lessons.length > 0) {
          prevLesson = {
            moduleId: prevModule.id,
            lessonId: prevModule.lessons[prevModule.lessons.length - 1].id,
          };
        }
      }
    }

    return { nextLesson, prevLesson };
  };

  const { nextLesson, prevLesson } = getAdjacentLessons();

  // Get access level icon - Enhanced to match CourseLandingPage implementation
  const getAccessLevelIcon = accessLevel => {
    switch (accessLevel || 'guest') {
      case 'premium':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-4 h-4 text-amber-500"
            aria-label="Premium content"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        );
      case 'registered':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-4 h-4 text-blue-500"
            aria-label="Registered users"
          >
            <path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
            <path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
          </svg>
        );
      default: // guest
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="w-4 h-4 text-green-500"
            aria-label="Free content"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  // If loading, show loading screen
  if (loading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading course content..." />
      </MainLayout>
    );
  }

  // If error, show error message
  if (error) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 px-4">
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
            <Button
              color="primary"
              onClick={() => navigate(`/courses/${courseSlug}`)}
            >
              Back to Course
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // If no lesson found, show not found message
  if (!lesson) {
    return (
      <MainLayout>
        <div className="container mx-auto py-8 px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Lesson Not Found</h1>
            <p className="mb-6 text-gray-600">
              The lesson you're looking for could not be found.
            </p>
            <Button
              color="primary"
              onClick={() => navigate(`/courses/${courseSlug}`)}
            >
              Back to Course
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <LearningHeaderArea
        currentUser={currentUser}
        lesson={lesson}
        course={course}
        display={{
          insights: false,
          quote: true,
          smartStudy: false,
          timer: false,
          community: false,
          career: false,
          resources: false,
          microlearning: false,
          aiCompanion: false,
        }}
      />
      <div className="min-h-screen bg-gray-50">
        {/* Breadcrumbs */}
        <div className="bg-white border-b border-gray-200 py-3">
          <div className="container mx-auto px-4">
            <nav className="flex items-center text-sm">
              <Link
                to="/courses"
                className="text-gray-500 hover:text-primary-600"
              >
                Courses
              </Link>
              <span className="mx-2 text-gray-500">/</span>
              <Link
                to={`/courses/${courseSlug}`}
                className="text-gray-500 hover:text-primary-600"
              >
                {course?.title || 'Course'}
              </Link>
              <span className="mx-2 text-gray-500">/</span>
              <span className="text-gray-800 font-medium truncate max-w-xs">
                {lesson.title}
              </span>
            </nav>
          </div>
        </div>

        {/* Course Progress Bar */}
        {course?.user_progress && (
          <div className="bg-white border-b border-gray-200 py-2">
            <div className="container mx-auto px-4">
              <div className="flex items-center">
                <div className="w-full mr-4">
                  <ProgressBar
                    progress={course.user_progress.percentage || 0}
                    showPercentage
                    labelPosition="right"
                    size="small"
                  />
                </div>
                <div className="whitespace-nowrap text-sm font-medium">
                  {course.user_progress.completed || 0}/
                  {course.user_progress.total || 0} lessons
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row">
            {/* Sidebar (collapsible on mobile) */}
            <div
              className={`md:w-1/4 md:block ${sidebarOpen ? 'block' : 'hidden'}`}
            >
              <div className="bg-white rounded-lg shadow-sm p-4 md:sticky md:top-4">
                {/* Sidebar Header */}
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-lg">Course Content</h3>
                  <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="md:hidden text-gray-500 hover:text-gray-700"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                {/* Module and Lesson Navigation */}
                {modules.map((mod, index) => (
                  <div key={mod.id} className="mb-3 last:mb-0">
                    <div className="font-medium text-gray-700 mb-2 flex items-center">
                      <span className="bg-gray-200 text-gray-700 rounded-full h-5 w-5 flex items-center justify-center text-xs mr-2">
                        {index + 1}
                      </span>
                      <span className="flex-1">{mod.title}</span>
                    </div>

                    <ul className="pl-7 space-y-1">
                      {mod.lessons?.map(les => {
                        const isActive = les.id.toString() === lessonId;
                        const hasCompleted = les.is_completed;

                        // Enhanced access level determination - check all possible property paths
                        const lessonAccessLevel =
                          les.accessLevel ||
                          les.access_level ||
                          (les.metadata &&
                            (les.metadata.accessLevel ||
                              les.metadata.access_level)) ||
                          'basic';

                        return (
                          <li key={les.id}>
                            <button
                              onClick={() =>
                                handleNavigateToLesson(mod.id, les.id)
                              }
                              className={`w-full text-left py-1.5 px-3 rounded flex items-center ${
                                isActive
                                  ? 'bg-primary-50 text-primary-600 font-medium'
                                  : 'text-gray-700 hover:bg-gray-100'
                              }`}
                            >
                              <div className="flex-shrink-0 w-5 h-5 mr-2">
                                {hasCompleted ? (
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-green-500"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                ) : (
                                  getAccessLevelIcon(lessonAccessLevel)
                                )}
                              </div>
                              <span className="flex-1 text-sm">
                                {les.title}
                              </span>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Mobile sidebar toggle button - shown only on mobile */}
            <button
              className="md:hidden fixed z-10 bottom-4 left-4 bg-primary-600 text-white rounded-full p-3 shadow-lg"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16m-7 6h7"
                />
              </svg>
            </button>

            {/* Main lesson content */}
            <div className="md:w-3/4 md:pl-6 mt-4 md:mt-0">
              <div
                className="bg-white rounded-lg shadow-sm p-6"
                ref={contentRef}
              >
                {/* Lesson Header */}
                <div className="mb-6">
                  <div className="flex items-center mb-1">
                    <div className="flex items-center mr-3">
                      {getAccessLevelIcon(lesson.access_level)}
                      <span className="ml-1 text-sm text-gray-500">
                        {lesson.access_level === 'premium'
                          ? 'Premium'
                          : lesson.access_level === 'registered'
                            ? 'Registered'
                            : 'Free'}
                      </span>
                    </div>
                    <Badge
                      variant={lesson.is_completed ? 'success' : 'secondary'}
                      size="small"
                    >
                      {lesson.is_completed ? 'Completed' : 'In Progress'}
                    </Badge>
                  </div>

                  <h1 className="text-2xl font-bold">{lesson.title}</h1>

                  {lesson.duration_display && (
                    <div className="flex items-center mt-2 text-sm text-gray-500">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
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
                      {lesson.duration_display}
                    </div>
                  )}
                </div>

                {/* Tab Navigation - UPDATED with handleTabChange */}
                <Tabs
                  tabs={[
                    { value: TABS.CONTENT, label: 'Content' },
                    {
                      value: TABS.RESOURCES,
                      label: 'Resources',
                      badge: lesson.resources?.length || 0,
                    },
                    {
                      value: TABS.ASSESSMENT,
                      label: 'Assessment',
                      disabled: !lesson.has_assessment,
                    },
                    {
                      value: TABS.NOTES,
                      label: 'Notes',
                      disabled: !isAuthenticated,
                    },
                  ]}
                  value={activeTab}
                  onChange={handleTabChange}
                />

                {/* Tab Content */}
                <div className="mt-6" key={activeTab}>
                  {/* Content Tab */}
                  {activeTab === TABS.CONTENT && (
                    <div className="space-y-6">
                      {/* Video content for video-type lessons */}
                      {lesson.type === 'video' && (
                        <div className="aspect-w-16 aspect-h-9 bg-black rounded-lg overflow-hidden mb-6">
                          <ContentAccessController
                            requiredLevel={lesson.access_level}
                            isLoggedIn={isAuthenticated}
                            userAccessLevel={userAccessLevel}
                            guestContent={
                              <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 text-white">
                                <div className="text-center p-6">
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-12 w-12 mx-auto mb-4"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                    />
                                  </svg>
                                  <h3 className="text-xl font-bold mb-2">
                                    Premium Content
                                  </h3>
                                  <p className="mb-4">
                                    Sign up or upgrade your subscription to
                                    access this video.
                                  </p>
                                  <Button
                                    color="primary"
                                    onClick={() => navigate('/login')}
                                  >
                                    Sign In to Access
                                  </Button>
                                </div>
                              </div>
                            }
                          >
                            <ReactPlayer
                              url="https://www.youtube.com/watch?v=ysz5S6PUM-U"
                              width="100%"
                              height="100%"
                              controls={true}
                              onProgress={progress => {
                                setVideoProgress(progress.playedSeconds);
                              }}
                              config={{
                                youtube: {
                                  playerVars: { modestbranding: 1 },
                                },
                              }}
                            />
                          </ContentAccessController>
                        </div>
                      )}

                      {/* Lesson content - HTML rendering with access control */}
                      <div className="prose prose-blue max-w-none">
                        <ContentAccessController
                          requiredLevel={lesson.access_level}
                          isLoggedIn={isAuthenticated}
                          userAccessLevel={userAccessLevel}
                          content={lesson.content}
                          guestContent={
                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                              <div className="mb-4">
                                <div className="flex items-center">
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-yellow-500 mr-2"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                  <h3 className="font-bold text-lg">
                                    Content Preview
                                  </h3>
                                </div>
                              </div>
                              <div
                                dangerouslySetInnerHTML={{
                                  __html:
                                    lesson.guest_content ||
                                    '<p>Sign in to access the full content of this lesson.</p>',
                                }}
                              />
                              <div className="mt-6 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                                <Button
                                  color="primary"
                                  onClick={() =>
                                    navigate('/login', {
                                      state: { from: window.location.pathname },
                                    })
                                  }
                                >
                                  Sign In
                                </Button>
                                <Button
                                  color="secondary"
                                  onClick={() => navigate('/register')}
                                >
                                  Register
                                </Button>
                              </div>
                            </div>
                          }
                          upgradeMessage={
                            lesson.access_level === 'premium' &&
                            userAccessLevel !== 'premium'
                              ? 'This premium content requires a subscription upgrade to access.'
                              : 'Please sign in to access this content.'
                          }
                        />
                      </div>

                      {/* Completion and navigation buttons */}
                      <div className="border-t border-gray-200 pt-6 mt-8 flex flex-col sm:flex-row sm:justify-between items-center space-y-4 sm:space-y-0">
                        <div>
                          {!lesson.is_completed && isAuthenticated && (
                            <Button
                              color="success"
                              onClick={handleMarkComplete}
                              disabled={markingComplete}
                            >
                              {markingComplete ? (
                                <>
                                  <Spinner color="white" size="small" /> Marking
                                  Complete...
                                </>
                              ) : (
                                <>Mark as Complete</>
                              )}
                            </Button>
                          )}
                        </div>

                        <div className="flex space-x-4">
                          {prevLesson && (
                            <Button
                              color="secondary"
                              onClick={() =>
                                handleNavigateToLesson(
                                  prevLesson.moduleId,
                                  prevLesson.lessonId
                                )
                              }
                            >
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 mr-1"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                                  clipRule="evenodd"
                                />
                              </svg>
                              Previous
                            </Button>
                          )}

                          {nextLesson && (
                            <Button
                              color="primary"
                              onClick={() =>
                                handleNavigateToLesson(
                                  nextLesson.moduleId,
                                  nextLesson.lessonId
                                )
                              }
                            >
                              Next
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5 ml-1"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Resources Tab */}
                  {activeTab === TABS.RESOURCES && (
                    <div>
                      <h2 className="text-xl font-bold mb-4">
                        Lesson Resources
                      </h2>

                      {/* Check if user has access to resources */}
                      <ContentAccessController
                        requiredLevel={lesson.access_level}
                        isLoggedIn={isAuthenticated}
                        userAccessLevel={userAccessLevel}
                        basicContent={
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                            <h3 className="font-bold mb-2">Access Required</h3>
                            <p className="mb-4">
                              Sign in or upgrade your subscription to access
                              resources for this lesson.
                            </p>
                            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                              <Button
                                color="primary"
                                onClick={() =>
                                  navigate('/login', {
                                    state: { from: window.location.pathname },
                                  })
                                }
                              >
                                Sign In
                              </Button>
                              <Button
                                color="secondary"
                                onClick={() => navigate('/register')}
                              >
                                Register
                              </Button>
                            </div>
                          </div>
                        }
                      >
                        {lesson.resources && lesson.resources.length > 0 ? (
                          <div className="space-y-4">
                            {lesson.resources.map(resource => (
                              <Card
                                key={resource.id}
                                className="flex items-center p-4"
                              >
                                <div className="flex-shrink-0 mr-4 bg-gray-100 w-12 h-12 rounded-lg flex items-center justify-center">
                                  {resource.type === 'document' && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-6 w-6 text-blue-500"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                                      />
                                    </svg>
                                  )}
                                  {resource.type === 'video' && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-6 w-6 text-red-500"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                                      />
                                    </svg>
                                  )}
                                  {resource.type === 'link' && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-6 w-6 text-green-500"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                                      />
                                    </svg>
                                  )}
                                  {resource.type === 'code' && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-6 w-6 text-purple-500"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                                      />
                                    </svg>
                                  )}
                                  {resource.type === 'tool' && (
                                    <svg
                                      xmlns="http://www.w3.org/2000/svg"
                                      className="h-6 w-6 text-gray-500"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                                      />
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                      />
                                    </svg>
                                  )}
                                </div>

                                <div className="flex-grow">
                                  <h3 className="font-medium">
                                    {resource.title}
                                  </h3>
                                  {resource.description && (
                                    <p className="text-sm text-gray-600">
                                      {resource.description}
                                    </p>
                                  )}
                                </div>

                                <div>
                                  {/* Resource access based on premium status */}
                                  {resource.premium &&
                                  userAccessLevel !== 'premium' ? (
                                    <div className="flex items-center text-yellow-500 bg-yellow-50 px-3 py-1 rounded">
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-4 w-4 mr-1"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                      >
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                      </svg>
                                      <span className="text-sm">Premium</span>
                                    </div>
                                  ) : (
                                    <>
                                      {resource.url && (
                                        <a
                                          href={resource.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="text-primary-600 hover:text-primary-800 bg-primary-50 hover:bg-primary-100 px-3 py-1 rounded inline-block"
                                        >
                                          Access
                                        </a>
                                      )}
                                      {resource.file && (
                                        <a
                                          href={resource.file}
                                          download
                                          className="text-primary-600 hover:text-primary-800 bg-primary-50 hover:bg-primary-100 px-3 py-1 rounded inline-block"
                                        >
                                          Download
                                        </a>
                                      )}
                                    </>
                                  )}
                                </div>
                              </Card>
                            ))}
                          </div>
                        ) : (
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                            <p className="text-gray-500">
                              No resources available for this lesson.
                            </p>
                          </div>
                        )}

                        {/* Premium resources section */}
                        {lesson.premium_resources &&
                          lesson.premium_resources.length > 0 && (
                            <div className="mt-8">
                              <h3 className="text-lg font-bold mb-4 flex items-center">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                  className="w-5 h-5 text-yellow-500 mr-2"
                                >
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                                Premium Resources
                              </h3>

                              <ContentAccessController
                                requiredLevel="advanced"
                                isLoggedIn={isAuthenticated}
                                userAccessLevel={userAccessLevel}
                                basicContent={
                                  <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border border-amber-200 rounded-lg p-6">
                                    <div className="flex items-start">
                                      <div className="flex-shrink-0 mt-0.5">
                                        <svg
                                          xmlns="http://www.w3.org/2000/svg"
                                          className="h-5 w-5 text-amber-500"
                                          viewBox="0 0 20 20"
                                          fill="currentColor"
                                        >
                                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                      </div>
                                      <div className="ml-3">
                                        <h3 className="font-medium text-amber-800">
                                          Premium Content
                                        </h3>
                                        <p className="text-amber-700 mt-1">
                                          Upgrade to access{' '}
                                          {lesson.premium_resources.length}{' '}
                                          premium resources including
                                          downloadable files, code samples, and
                                          more.
                                        </p>
                                        <div className="mt-4">
                                          <Button
                                            color="warning"
                                            onClick={() => navigate('/pricing')}
                                          >
                                            Upgrade Now
                                          </Button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                }
                              >
                                <div className="space-y-4">
                                  {lesson.premium_resources.map(resource => (
                                    <Card
                                      key={resource.id}
                                      className="flex items-center p-4 border-amber-200 bg-gradient-to-r from-yellow-50 to-amber-50"
                                    >
                                      <div className="flex-shrink-0 mr-4 bg-amber-100 w-12 h-12 rounded-lg flex items-center justify-center">
                                        {resource.type === 'document' && (
                                          <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            className="h-6 w-6 text-amber-600"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                                            />
                                          </svg>
                                        )}
                                        {resource.type === 'video' && (
                                          <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            className="h-6 w-6 text-amber-600"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                                            />
                                          </svg>
                                        )}
                                        {resource.type === 'link' && (
                                          <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            className="h-6 w-6 text-amber-600"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                                            />
                                          </svg>
                                        )}
                                        {resource.type === 'code' && (
                                          <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            className="h-6 w-6 text-amber-600"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                                            />
                                          </svg>
                                        )}
                                        {resource.type === 'tool' && (
                                          <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            className="h-6 w-6 text-amber-600"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                                            />
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                            />
                                          </svg>
                                        )}
                                      </div>

                                      <div className="flex-grow">
                                        <div className="flex items-center">
                                          <h3 className="font-medium">
                                            {resource.title}
                                          </h3>
                                          <span className="ml-2 px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-xs font-medium">
                                            Premium
                                          </span>
                                        </div>
                                        {resource.description && (
                                          <p className="text-sm text-gray-600">
                                            {resource.description}
                                          </p>
                                        )}
                                      </div>

                                      <div>
                                        {resource.url && (
                                          <a
                                            href={resource.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-amber-700 hover:text-amber-900 bg-amber-100 hover:bg-amber-200 px-3 py-1 rounded inline-block"
                                          >
                                            Access
                                          </a>
                                        )}
                                        {resource.file && (
                                          <a
                                            href={resource.file}
                                            download
                                            className="text-amber-700 hover:text-amber-900 bg-amber-100 hover:bg-amber-200 px-3 py-1 rounded inline-block"
                                          >
                                            Download
                                          </a>
                                        )}
                                      </div>
                                    </Card>
                                  ))}
                                </div>
                              </ContentAccessController>
                            </div>
                          )}
                      </ContentAccessController>
                    </div>
                  )}

                  {/* Assessment Tab */}
                  {activeTab === TABS.ASSESSMENT && (
                    <div>
                      <h2 className="text-xl font-bold mb-4">
                        Lesson Assessment
                      </h2>

                      {/* Only show assessment to authenticated users with proper access */}
                      <ContentAccessController
                        requiredLevel={lesson.access_level}
                        isLoggedIn={isAuthenticated}
                        userAccessLevel={userAccessLevel}
                        basicContent={
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                            <h3 className="font-bold mb-2">Access Required</h3>
                            <p className="mb-4">
                              Sign in or upgrade your subscription to access the
                              assessment for this lesson.
                            </p>
                            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                              <Button
                                color="primary"
                                onClick={() =>
                                  navigate('/login', {
                                    state: { from: window.location.pathname },
                                  })
                                }
                              >
                                Sign In
                              </Button>
                              <Button
                                color="secondary"
                                onClick={() => navigate('/register')}
                              >
                                Register
                              </Button>
                            </div>
                          </div>
                        }
                      >
                        {lesson.has_assessment ? (
                          <div className="space-y-6">
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                              <div className="flex items-start">
                                <div className="flex-shrink-0 mt-0.5">
                                  <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-blue-500"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                                    <path
                                      fillRule="evenodd"
                                      d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                </div>
                                <div className="ml-3">
                                  <h3 className="font-medium text-blue-800">
                                    {lesson.assessment?.title ||
                                      'Lesson Assessment'}
                                  </h3>
                                  <p className="text-blue-700 mt-1">
                                    {lesson.assessment?.description ||
                                      'Test your knowledge of the concepts covered in this lesson.'}
                                  </p>
                                  <div className="mt-4 space-y-2">
                                    {lesson.assessment?.time_limit > 0 && (
                                      <div className="flex items-center text-sm text-blue-700">
                                        <svg
                                          xmlns="http://www.w3.org/2000/svg"
                                          className="h-4 w-4 mr-1"
                                          viewBox="0 0 24 24"
                                          fill="currentColor"
                                        >
                                          <path
                                            fillRule="evenodd"
                                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                                            clipRule="evenodd"
                                          />
                                        </svg>
                                        Time Limit:{' '}
                                        {lesson.assessment.time_limit} minutes
                                      </div>
                                    )}
                                    <div className="flex items-center text-sm text-blue-700">
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-4 w-4 mr-1"
                                        viewBox="0 0 24 24"
                                        fill="currentColor"
                                      >
                                        <path
                                          fillRule="evenodd"
                                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                          clipRule="evenodd"
                                        />
                                      </svg>
                                      Passing Score:{' '}
                                      {lesson.assessment?.passing_score || 70}%
                                    </div>
                                    <div className="flex items-center text-sm text-blue-700">
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-4 w-4 mr-1"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                      >
                                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                                        <path
                                          fillRule="evenodd"
                                          d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                          clipRule="evenodd"
                                        />
                                      </svg>
                                      Questions:{' '}
                                      {lesson.assessment?.questions?.length ||
                                        0}
                                    </div>
                                  </div>
                                  <div className="mt-6">
                                    {/* For simplicity, link to the assessment page */}
                                    <Button
                                      color="primary"
                                      onClick={() =>
                                        navigate(
                                          `/courses/${courseSlug}/assessment/${lesson.assessment?.id}`
                                        )
                                      }
                                    >
                                      Start Assessment
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                            <p className="text-gray-500">
                              No assessment available for this lesson.
                            </p>
                          </div>
                        )}
                      </ContentAccessController>
                    </div>
                  )}

                  {/* Notes Tab */}
                  {activeTab === TABS.NOTES && (
                    <div>
                      <h2 className="text-xl font-bold mb-4">Your Notes</h2>

                      {/* Only show notes to authenticated users */}
                      {!isAuthenticated ? (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                          <h3 className="font-bold mb-2">
                            Sign In to Take Notes
                          </h3>
                          <p className="mb-4">
                            Notes are available for registered users. Sign in to
                            save your notes for this lesson.
                          </p>
                          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                            <Button
                              color="primary"
                              onClick={() =>
                                navigate('/login', {
                                  state: { from: window.location.pathname },
                                })
                              }
                            >
                              Sign In
                            </Button>
                            <Button
                              color="secondary"
                              onClick={() => navigate('/register')}
                            >
                              Register
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-6">
                          <div className="bg-gray-50 rounded-lg p-4">
                            <textarea
                              className="w-full h-48 p-4 border border-gray-300 rounded-lg
                                     focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                              value={userNote}
                              onChange={e => setUserNote(e.target.value)}
                              placeholder="Take notes on this lesson..."
                              ref={noteInputRef}
                            ></textarea>
                            <div className="flex justify-end mt-2">
                              <Button
                                color="primary"
                                onClick={handleSaveNote}
                                disabled={noteSaving || !userNote.trim()}
                              >
                                {noteSaving ? (
                                  <>
                                    <Spinner color="white" size="small" />{' '}
                                    Saving...
                                  </>
                                ) : (
                                  <>Save Note</>
                                )}
                              </Button>
                            </div>
                          </div>

                          {/* Previous notes */}
                          <div>
                            <h3 className="text-lg font-medium mb-3">
                              Previous Notes
                            </h3>
                            {savedNotes.length > 1 ? (
                              <div className="space-y-4">
                                {savedNotes.slice(1).map(note => (
                                  <Card key={note.id} className="p-4">
                                    <div className="flex justify-between items-start">
                                      <div className="prose prose-sm max-w-none">
                                        <p>{note.content}</p>
                                      </div>
                                      <div className="text-xs text-gray-500">
                                        {new Date(
                                          note.updated_date || note.created_date
                                        ).toLocaleDateString()}
                                      </div>
                                    </div>
                                  </Card>
                                ))}
                              </div>
                            ) : (
                              <div className="text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                                <p>No previous notes for this lesson</p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

// Replace default export with error boundary wrapper
export default function CourseContentPageWithErrorBoundary(props) {
  const { currentTime } = props;
  return (
    <CourseContentErrorBoundary currentTime={currentTime}>
      <CourseContentPage {...props} />
    </CourseContentErrorBoundary>
  );
}
