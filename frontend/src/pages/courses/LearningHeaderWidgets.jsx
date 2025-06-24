/**
 * File: LearningHeaderWidgets.jsx
 * Version: 3.2.0
 * Date: 2025-05-18
 * Author: cadsanthanam
 *
 * Learning header widgets for SoftTech Solutions LMS platform
 *
 * This component provides motivational quotes and other learning enhancement widgets
 * that display between the main navigation and course content.
 *
 * Fixed version that resolves reference errors and positioning issues
 */

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// ============== INDIVIDUAL WIDGETS ==============

/**
 * Learning Insights Bar - Shows goals and learning streak
 */
function LearningInsightsBar({ currentUser, courseProgress }) {
  // In a real app, these would come from props or an API call
  const streak = currentUser?.learningStreak || 5;
  const completedLessons = courseProgress?.completed || 3;
  const totalLessons = courseProgress?.total || 5;
  const moduleNumber = courseProgress?.currentModule || 2;

  return (
    <div className="bg-gradient-to-r from-primary-900 to-primary-700 text-white py-3">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex flex-col mr-8">
              <span className="text-xs text-primary-200">TODAY'S GOAL</span>
              <span className="font-medium">
                Complete Module {moduleNumber} ({completedLessons}/
                {totalLessons} lessons)
              </span>
            </div>
            <div className="hidden md:block h-10 border-l border-primary-600 mx-4"></div>
            <div className="hidden md:flex flex-col">
              <span className="text-xs text-primary-200">LEARNING STREAK</span>
              <span className="font-medium">{streak} days 🔥</span>
            </div>
          </div>
          <div className="flex items-center">
            <button className="bg-primary-800 hover:bg-primary-900 py-1 px-3 rounded-md text-sm">
              Set Daily Target
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Smart Study Assistant - Shows related concepts
 */
function SmartStudyAssistant({ lesson }) {
  // In a real app, these would come from props or context
  const relatedConcept = lesson?.relatedConcepts?.[0] || 'JavaScript Promises';
  const preparesFor = lesson?.preparesFor || 'Async/Await';

  return (
    <div className="bg-gray-50 border-b border-gray-200 py-3">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="bg-blue-100 p-2 rounded-full">
              <svg
                className="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                Concept Connection
              </p>
              <p className="text-xs text-gray-600">
                This lesson builds on "{relatedConcept}" and prepares you for "
                {preparesFor}"
              </p>
            </div>
          </div>
          <div className="hidden md:flex space-x-4">
            <button className="text-sm text-primary-600 hover:text-primary-800">
              Previous Concepts
            </button>
            <button className="text-sm text-primary-600 hover:text-primary-800">
              Review Materials
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Motivational Quote Component
 */
function MotivationalQuote() {
  // Array of motivational quotes
  const quotes = [
    {
      text: 'The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice.',
      author: 'Brian Herbert',
    },
    {
      text: 'Live as if you were to die tomorrow. Learn as if you were to live forever.',
      author: 'Mahatma Gandhi',
    },
    {
      text: 'Anyone who stops learning is old, whether at twenty or eighty.',
      author: 'Henry Ford',
    },
    {
      text: 'The beautiful thing about learning is that nobody can take it away from you.',
      author: 'B.B. King',
    },
    {
      text: 'Education is not the filling of a pot but the lighting of a fire.',
      author: 'W.B. Yeats',
    },
    {
      text: "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
      author: 'Dr. Seuss',
    },
    {
      text: 'Learning is not attained by chance, it must be sought for with ardor and attended to with diligence.',
      author: 'Abigail Adams',
    },
    {
      text: 'Tell me and I forget. Teach me and I remember. Involve me and I learn.',
      author: 'Benjamin Franklin',
    },
  ];

  // Get a quote based on the day of the month so it changes daily but is consistent throughout the day
  const dayOfMonth = new Date().getDate();
  const quoteIndex = dayOfMonth % quotes.length;
  const quote = quotes[quoteIndex];

  return (
    <div className="bg-gradient-to-r from-indigo-700 to-purple-600 text-white py-3">
      <div className="container mx-auto px-4 text-center">
        <blockquote className="text-sm md:text-base italic">
          "{quote.text}"
        </blockquote>
        <p className="text-xs mt-1 text-indigo-200">— {quote.author}</p>
      </div>
    </div>
  );
}

/**
 * Time-Based Learning Assistant - Study timer and focus session tracker
 */
function TimedLearningAssistant() {
  const [timer, setTimer] = useState({ elapsed: 0, isRunning: true });
  const breakInterval = 25 * 60; // 25 minutes in seconds for a Pomodoro-style break

  useEffect(() => {
    let interval;
    if (timer.isRunning) {
      interval = setInterval(() => {
        setTimer(prev => ({ ...prev, elapsed: prev.elapsed + 1 }));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timer.isRunning]);

  // Format time as MM:SS
  const formatTime = seconds => {
    const mins = Math.floor(seconds / 60)
      .toString()
      .padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  // Calculate time until break
  const timeUntilBreak = breakInterval - (timer.elapsed % breakInterval);

  return (
    <div className="bg-white border-b border-gray-200 py-3">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-full mr-3">
              <svg
                className="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <div className="font-medium">Focused Study Session</div>
              <div className="text-xs text-gray-500">
                {formatTime(timer.elapsed)} elapsed • Take a break in{' '}
                {formatTime(timeUntilBreak)}
              </div>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-md text-sm"
              onClick={() =>
                setTimer(prev => ({ ...prev, isRunning: !prev.isRunning }))
              }
            >
              {timer.isRunning ? 'Pause' : 'Resume'}
            </button>
            <button className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-800 rounded-md text-sm">
              Take Note
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Community Progress Insights - Shows how many other learners are active
 */
function CommunityProgress({ course }) {
  // Mock data - in a real app this would come from props or API
  const activeUsers = 11;
  const courseCompletionPercentage = course?.completionPercentage || 32;

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 py-3">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex -space-x-2 mr-3">
              {/* User avatars - would be dynamic in a real app */}
              <div className="w-6 h-6 rounded-full bg-blue-400 border-2 border-white"></div>
              <div className="w-6 h-6 rounded-full bg-green-400 border-2 border-white"></div>
              <div className="w-6 h-6 rounded-full bg-yellow-400 border-2 border-white"></div>
              <div className="w-6 h-6 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center text-xs">
                +8
              </div>
            </div>
            <p className="text-sm text-gray-600">
              {activeUsers} people are learning this lesson right now
            </p>
          </div>
          <div className="hidden md:flex items-center text-sm">
            <span className="text-gray-500 mr-2">
              Course completion: {courseCompletionPercentage}%
            </span>
            <div className="w-32 h-2 bg-gray-200 rounded-full">
              <div
                className="h-2 bg-primary-500 rounded-full"
                style={{ width: `${courseCompletionPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Career Connect Panel - Shows job market relevance of current lesson
 */
function CareerConnectPanel({ lesson }) {
  const navigate = useNavigate();
  const jobRelevancePercentage = lesson?.jobRelevancePercentage || 76;

  return (
    <div className="bg-gray-50 border-b border-gray-200 py-3">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <div className="bg-blue-600 text-white p-2 rounded-lg mr-3">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                  clipRule="evenodd"
                />
                <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
              </svg>
            </div>
            <div>
              <span className="text-sm font-medium">Industry Application</span>
              <p className="text-xs text-gray-600">
                This skill appears in {jobRelevancePercentage}% of Senior
                Developer job postings
              </p>
            </div>
          </div>
          <div>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
              onClick={() => navigate('/jobs')}
            >
              View Related Jobs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Resource Recommendations - Shows contextual learning resources
 */
function ResourceRecommendations({ lesson }) {
  // Mock data - in a real app these would come from props or API based on the current lesson
  const resources = [
    {
      type: 'article',
      title: 'Understanding Closures in JS',
      duration: '5 min read',
      icon: (
        <svg
          className="w-5 h-5 text-purple-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
        </svg>
      ),
      bgColor: 'bg-purple-100',
    },
    {
      type: 'video',
      title: 'Advanced Patterns Video',
      duration: '3:45',
      icon: (
        <svg
          className="w-5 h-5 text-red-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
        </svg>
      ),
      bgColor: 'bg-red-100',
    },
    {
      type: 'event',
      title: 'Office Hours',
      duration: 'Today, 4PM',
      icon: (
        <svg
          className="w-5 h-5 text-green-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
            clipRule="evenodd"
          />
        </svg>
      ),
      bgColor: 'bg-green-100',
    },
  ];

  return (
    <div className="bg-white border-b border-gray-200 py-3">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {resources.map((resource, index) => (
            <div key={index} className="col-span-1 flex items-center">
              <div className={`${resource.bgColor} p-2 rounded mr-3`}>
                {resource.icon}
              </div>
              <span className="text-sm">
                {resource.title}{' '}
                <span className="text-xs text-gray-500">
                  ({resource.duration_display || resource.duration})
                </span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Daily Microlearning Card - Shows a tip or insight that changes daily
 */
function DailyMicrolearningCard() {
  // Array of tips that rotate daily
  const tips = [
    {
      title: 'Debugging Tip',
      content:
        'When debugging asynchronous code, adding console.log() statements with distinct labels helps track the execution flow. Try using emoji prefixes for easy visual scanning.',
      icon: (
        <svg
          className="w-6 h-6 text-primary-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
            clipRule="evenodd"
          />
        </svg>
      ),
    },
    {
      title: 'Memory Retention Technique',
      content:
        "Apply the 'Feynman Technique': Try to explain what you've learned in simple terms as if teaching someone else. This helps identify gaps in your understanding.",
      icon: (
        <svg
          className="w-6 h-6 text-primary-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
        </svg>
      ),
    },
    {
      title: 'Study Hack',
      content:
        "The 'Pomodoro Technique' involves focused 25-minute work sessions followed by 5-minute breaks. After four cycles, take a longer 15-30 minute break to maintain productivity.",
      icon: (
        <svg
          className="w-6 h-6 text-primary-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
            clipRule="evenodd"
          />
        </svg>
      ),
    },
  ];

  // Select tip based on day of month
  const dayOfMonth = new Date().getDate();
  const tipIndex = dayOfMonth % tips.length;
  const tip = tips[tipIndex];

  return (
    <div className="bg-white border-b border-gray-200 py-4">
      <div className="container mx-auto px-4">
        <div className="flex items-start">
          <div className="flex-shrink-0 p-1 bg-gray-100 rounded-lg mr-4">
            <div className="w-12 h-12 flex items-center justify-center bg-primary-100 rounded-lg">
              {tip.icon}
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-bold mb-1">{tip.title}</h3>
            <p className="text-sm text-gray-600 mb-2">{tip.content}</p>
            <div className="text-xs text-gray-500">
              Tip refreshes daily •{' '}
              <button className="text-primary-600 hover:underline">
                Save for later
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * AI Learning Companion - Offers AI assistance for the current lesson
 */
function AILearningCompanion() {
  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white py-3">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center mr-3">
              <svg
                className="w-5 h-5 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Learning Assistant</p>
              <p className="text-xs text-gray-400">
                Ask me about: key concepts, practical applications, or common
                mistakes
              </p>
            </div>
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 py-1 px-3 rounded text-sm">
            Ask Question
          </button>
        </div>
      </div>
    </div>
  );
}

// ============== MAIN COMPONENT ==============

/**
 * Main component that combines selected widgets
 * Uses a simplified approach that works reliably in most layouts
 */
export default function LearningHeaderArea({
  currentUser = {},
  lesson = {},
  course = {},
  display = {
    insights: false,
    quote: true, // Default to showing the quote widget
    smartStudy: false,
    timer: false,
    community: false,
    career: false,
    resources: false,
    microlearning: false,
    aiCompanion: false,
  },
}) {
  const headerRef = useRef(null);

  // Choose a simple approach that's more likely to work across different layouts
  // Instead of complex dynamic positioning which might be causing errors
  useEffect(() => {
    // Simple function to apply a reasonable negative margin
    const applyMargin = () => {
      if (!headerRef.current) return;

      // Apply a moderate negative margin that works in most cases
      // This value can be adjusted based on testing
      headerRef.current.style.marginTop = '-80px';
    };

    // Apply immediately and after a short delay to ensure it works
    applyMargin();
    const timer = setTimeout(applyMargin, 200);

    return () => clearTimeout(timer);
  }, []);

  // Add CSS for consistency across page loads
  useEffect(() => {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
      /* Ensure learning header connects properly to content */
      .learning-header-area {
        margin-bottom: 0;
      }

      /* Remove any conflicting margins from nearby elements */
      .breadcrumbs-container,
      .course-content-container,
      .content-wrapper {
        margin-top: 0 !important;
      }
    `;

    document.head.appendChild(styleElement);

    return () => {
      document.head.removeChild(styleElement);
    };
  }, []);

  return (
    <div className="learning-header-area w-full" ref={headerRef}>
      {display.quote && <MotivationalQuote />}
      {display.insights && (
        <LearningInsightsBar
          currentUser={currentUser}
          courseProgress={course.progress}
        />
      )}
      {display.smartStudy && <SmartStudyAssistant lesson={lesson} />}
      {display.timer && <TimedLearningAssistant />}
      {display.community && <CommunityProgress course={course} />}
      {display.career && <CareerConnectPanel lesson={lesson} />}
      {display.resources && <ResourceRecommendations lesson={lesson} />}
      {display.microlearning && <DailyMicrolearningCard />}
      {display.aiCompanion && <AILearningCompanion />}
    </div>
  );
}

// Export individual widgets if you want to use them separately
export {
  AILearningCompanion,
  CareerConnectPanel,
  CommunityProgress,
  DailyMicrolearningCard,
  LearningInsightsBar,
  MotivationalQuote,
  ResourceRecommendations,
  SmartStudyAssistant,
  TimedLearningAssistant,
};
