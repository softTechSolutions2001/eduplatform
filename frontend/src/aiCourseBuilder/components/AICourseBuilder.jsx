/**
 * AI-Assisted Course Builder - Main Component
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * Main entry point for the AI Course Builder module. Provides a comprehensive
 * interface for instructors to create exceptional educational content using
 * state-of-the-art AI assistance.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import LoadingScreen from '../../components/common/LoadingScreen';
import { useAuth } from '../../contexts/AuthContext';
import DirectionProvider from '../../contexts/DirectionContext.jsx';
import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';
import { useAIBuilderStore } from '../store/aiBuilderStore';
import CourseGenerationWizard from './CourseGenerationWizard';
import AIBuilderErrorBoundary from './ui/AIBuilderErrorBoundary';
import NotificationSystem from './ui/NotificationSystem';

const AICourseBuilderContent = () => {
  const navigate = useNavigate();
  const { currentUser, isInstructor } = useAuth();
  const {
    currentPhase,
    isGenerating,
    error,
    courseData,
    resetBuilder,
    initializeBuilder,
  } = useAIBuilderStore();

  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize the AI Course Builder
  useEffect(() => {
    const initBuilder = async () => {
      try {
        // Check user permissions
        if (!currentUser || !isInstructor()) {
          navigate('/instructor/dashboard');
          return;
        }

        // Initialize the builder store
        await initializeBuilder();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize AI Course Builder:', error);
      }
    };

    initBuilder();
  }, [currentUser, isInstructor, navigate, initializeBuilder]);

  // Handle builder reset
  const handleReset = () => {
    resetBuilder();
    setIsInitialized(true);
  };

  // Handle navigation back to dashboard
  const handleBackToDashboard = () => {
    navigate('/instructor/dashboard');
  };

  // Loading state
  if (!isInitialized) {
    return <LoadingScreen message="Initializing AI Course Builder..." />;
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <div className="mb-4">
            <svg
              className="w-12 h-12 text-red-500 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.882 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            AI Course Builder Error
          </h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex space-x-3 justify-center">
            <Button variant="outline" onClick={handleBackToDashboard}>
              Back to Dashboard
            </Button>
            <Button variant="primary" onClick={handleReset}>
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                AI-Assisted Course Builder
              </h1>
              <p className="text-gray-600 mt-1">
                Create exceptional educational content with AI assistance
              </p>
            </div>
            <div className="flex space-x-3">
              <Button variant="outline" onClick={handleBackToDashboard}>
                Back to Dashboard
              </Button>
              {courseData && (
                <Button variant="outline" onClick={handleReset}>
                  Start New Course
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Screen or Wizard */}
        {currentPhase === 'inactive' ? (
          <WelcomeScreen onStart={() => initializeBuilder()} />
        ) : (
          <CourseGenerationWizard />
        )}
      </div>

      {/* Notification System */}
      <NotificationSystem />
    </div>
  );
};

// Welcome Screen Component
const WelcomeScreen = ({ onStart }) => {
  return (
    <div className="max-w-4xl mx-auto">
      <Card className="p-8">
        <div className="text-center">
          {/* AI Icon */}
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary-100 mb-6">
            <svg
              className="h-8 w-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>

          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to AI-Assisted Course Creation
          </h2>

          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform your expertise into engaging educational content with our
            advanced AI assistant. Experience a streamlined 5-phase workflow
            that guides you from concept to completion.
          </p>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <FeatureCard
              icon="🎯"
              title="Smart Course Outline"
              description="AI generates comprehensive course structures based on your learning objectives"
            />
            <FeatureCard
              icon="📚"
              title="Intelligent Content"
              description="Automatically create modules and lessons with rich, educational content"
            />
            <FeatureCard
              icon="⚡"
              title="Instant Enhancement"
              description="Real-time suggestions to improve engagement and learning outcomes"
            />
          </div>

          {/* Workflow Preview */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              5-Phase Creation Workflow
            </h3>{' '}
            <div className="flex justify-between items-center">
              {AI_BUILDER_CONFIG.workflow.phases.map((phase, index) => (
                <div key={phase.id} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>
                    <span className="text-sm text-gray-600 mt-2 text-center max-w-20">
                      {/* Use 'name' property instead of 'title' */}
                      {phase.name}
                    </span>
                  </div>
                  {index < AI_BUILDER_CONFIG.workflow.phases.length - 1 && (
                    <div className="flex-1 h-px bg-gray-300 mx-2" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Start Button */}
          <Button
            variant="primary"
            size="large"
            onClick={onStart}
            className="px-8 py-3"
          >
            Start Creating with AI
          </Button>
        </div>
      </Card>
    </div>
  );
};

// Feature Card Component
const FeatureCard = ({ icon, title, description }) => (
  <div className="text-center">
    <div className="text-3xl mb-3">{icon}</div>
    <h4 className="text-lg font-semibold text-gray-900 mb-2">{title}</h4>
    <p className="text-gray-600 text-sm">{description}</p>
  </div>
);

// Wrap the component with the error boundary and direction provider
const AICourseBuilder = () => (
  <DirectionProvider>
    <AIBuilderErrorBoundary>
      <AICourseBuilderContent />
    </AIBuilderErrorBoundary>
  </DirectionProvider>
);

export default AICourseBuilder;
