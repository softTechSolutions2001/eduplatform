/**
 * File: frontend/src/pages/instructor/CourseCreationOptions.jsx
 * Version: 1.0.0
 * Date: 2025-06-01
 * Author: mohithasanthanam
 * Last Modified: 2025-06-01
 *
 * Course Creation Options Component
 *
 * This component provides a selection interface for instructors to choose between
 * different course creation approaches:
 * - Step-by-step Wizard (guided approach for beginners)
 * - Drag-and-Drop Builder (visual approach for experienced users)
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/layouts/MainLayout';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

const CourseCreationOptions = () => {
  const navigate = useNavigate();

  const handleSelectWizard = () => {
    navigate('/instructor/courses/wizard');
  };
  const handleSelectBuilder = () => {
    navigate('/instructor/courses/builder');
  };

  const handleSelectAIBuilder = () => {
    navigate('/instructor/courses/ai-builder');
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create New Course</h1>
          <p className="text-gray-600">
            Choose your preferred method for creating a new course
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Wizard Option */}
          <Card className="hover:shadow-lg transition-shadow duration-300 border-2 border-transparent hover:border-primary-200">
            <div className="p-6" data-testid="wizard-option">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-4 mx-auto">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-8 w-8 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>

              <h2 className="text-xl font-semibold text-center mb-2">
                Step-by-Step Wizard
              </h2>

              <p className="mb-4 text-gray-600 text-center">
                A guided approach with clear steps to create your course
              </p>

              <ul className="list-disc text-sm text-gray-700 pl-5 mb-6 space-y-1">
                <li>Structured, step-by-step process</li>
                <li>Clear guidance at each stage</li>
                <li>Simplified content organization</li>
                <li>Recommended for beginners</li>
                <li>5 simple steps to complete course</li>
              </ul>

              <div className="text-center">
                <Button
                  variant="primary"
                  onClick={handleSelectWizard}
                  className="w-full"
                  data-testid="select-wizard-btn"
                >
                  Create with Wizard
                </Button>
              </div>
            </div>
          </Card>

          {/* Builder Option */}
          <Card className="hover:shadow-lg transition-shadow duration-300 border-2 border-transparent hover:border-secondary-200">
            <div className="p-6" data-testid="builder-option">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-secondary-100 mb-4 mx-auto">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-8 w-8 text-secondary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-center mb-2">
                Drag-and-Drop Builder
              </h2>
              <p className="mb-4 text-gray-600 text-center">
                A visual approach for creating and organizing course content
              </p>
              <ul className="list-disc text-sm text-gray-700 pl-5 mb-6 space-y-1">
                <li>Visual drag-and-drop interface</li>
                <li>Flexible content arrangement</li>
                <li>Real-time preview capabilities</li>
                <li>Great for visual learners</li>
                <li>Auto-save functionality</li>
              </ul>
              <div className="text-center">
                <Button
                  variant="secondary"
                  onClick={handleSelectBuilder}
                  className="w-full"
                  data-testid="select-builder-btn"
                >
                  Create with Builder
                </Button>
              </div>{' '}
            </div>
          </Card>

          {/* AI Builder Option */}
          <Card className="hover:shadow-lg transition-shadow duration-300 border-2 border-transparent hover:border-indigo-200">
            <div className="p-6" data-testid="ai-builder-option">
              <div className="flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4 mx-auto">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-8 w-8 text-indigo-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>

              <h2 className="text-xl font-semibold text-center mb-2">
                AI Course Builder
              </h2>

              <p className="mb-4 text-gray-600 text-center">
                Create courses powered by AI to accelerate your content creation
              </p>

              <ul className="list-disc text-sm text-gray-700 pl-5 mb-6 space-y-1">
                <li>AI-powered content generation</li>
                <li>Automatic course structure</li>
                <li>Smart content enhancement</li>
                <li>Time-saving automation</li>
                <li>Intelligent learning objectives</li>
              </ul>

              <div className="text-center">
                <Button
                  variant="primary"
                  onClick={handleSelectAIBuilder}
                  className="w-full bg-indigo-600 hover:bg-indigo-700"
                  data-testid="select-ai-builder-btn"
                >
                  Create with AI
                </Button>
              </div>
            </div>
          </Card>
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>
            All approaches create compatible courses and you can switch between
            them at any time.
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default CourseCreationOptions;
