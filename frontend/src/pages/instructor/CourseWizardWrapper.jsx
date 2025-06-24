/**
 * File: frontend/src/pages/instructor/CourseWizardWrapper.jsx
 * Version: 1.0.0
 * Date: 2025-06-01 14:10:00
 * Author: mohithasanthanam
 * Last Modified: 2025-06-01 14:10:00 UTC
 *
 * CourseWizard wrapper component that properly organizes context providers
 *
 * This component serves as a wrapper for the CourseWizard to ensure
 * that the CourseWizardContent is always rendered inside the provider,
 * fixing context-related errors during hot module reloads.
 *
 * The wrapper ensures proper component mounting/unmounting during
 * hot module reloading, preventing the React context error:
 * "useCourseWizard must be used within a CourseWizardProvider"
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MainLayout from '../../components/layouts/MainLayout';
import { CourseWizardProvider, useCourseWizard } from './CourseWizardContext';
import { LoadingScreen, Alert, StepIndicator } from '../../components/common';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import instructorService from '../../services/instructorService';
import authPersist from '../../utils/authPersist';
import SwitchEditorBanner from './components/SwitchEditorBanner';

// Import wizard step components to make them available for the inner content
import {
  CourseBasicsStep,
  CourseDetailsStep,
  ModuleStructureStep,
  ContentCreationStep,
  ReviewPublishStep,
} from './wizardSteps';

/**
 * CourseWizardWrapper Component
 *
 * This component handles course loading similar to the CourseWizard component,
 * but ensures the context is properly set up before rendering the content.
 */
const CourseWizardWrapper = () => {
  const { courseSlug } = useParams();
  const navigate = useNavigate();

  // State management for course loading
  const [course, setCourse] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // ENHANCED: Fetch existing course data if editing with AbortController and stale recovery
  useEffect(() => {
    const controller = new AbortController();

    const fetchCourse = async () => {
      if (courseSlug) {
        try {
          setIsLoading(true);

          // Refresh auth token to prevent session expiration during editing
          if (
            authPersist &&
            typeof authPersist.isTokenValid === 'function' &&
            typeof authPersist.refreshTokenExpiry === 'function'
          ) {
            if (authPersist.isTokenValid()) {
              authPersist.refreshTokenExpiry();
            }
          }

          // Clear cache before fetching to ensure fresh data
          instructorService.clearCache();

          // FIXED: Simplified call - getCourseBySlug now returns course data directly
          const courseData = await instructorService.getCourseBySlug(
            courseSlug,
            {
              signal: controller.signal,
            }
          );

          if (!courseData) {
            throw new Error(`Course with slug "${courseSlug}" not found`);
          }

          setCourse(courseData);
          setIsLoading(false);
        } catch (error) {
          // Don't process if aborted
          if (error.name === 'AbortError') {
            console.log('Course fetch aborted');
            return;
          }

          console.error('Error fetching course:', error);

          // IMPROVED: Clean error handling
          const status = error.status;
          let errorMessage = 'Failed to fetch course. Please try again.';

          if (status === 404) {
            errorMessage = `Course "${courseSlug}" not found.`;
            // Clean up localStorage for invalid course slugs
            localStorage.removeItem('lastEditedCourseId');
            localStorage.removeItem('lastEditedCourseSlug');
          } else if (status === 403) {
            errorMessage = "You don't have permission to edit this course.";
          } else if (error.message) {
            errorMessage = error.message;
          }

          setError(errorMessage);
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    fetchCourse();

    // ADDED: Cleanup function to abort fetch if component unmounts
    return () => controller.abort();
  }, [courseSlug]);

  if (isLoading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading course data..." />
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <Alert type="error">{error}</Alert>
          <div className="mt-4">
            <Button onClick={() => window.history.back()}>Go Back</Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Render the CourseWizardContext provider directly and import the
  // CourseWizardContent component to ensure the context is available
  return (
    <MainLayout>
      <CourseWizardProvider existingCourse={course}>
        <CourseWizardContent />
      </CourseWizardProvider>
    </MainLayout>
  );
};

// Inner content component that uses the CourseWizardContext
// This is directly defined here rather than imported from CourseWizard.jsx
// to prevent the context usage outside of its provider
const CourseWizardContent = () => {
  const navigate = useNavigate();
  // Now safely use the hook within the provider
  const {
    courseData,
    currentStep,
    totalSteps,
    setStep,
    nextStep,
    prevStep,
    validateCurrentStep,
  } = useCourseWizard();

  // Handle course publication
  const handlePublishCourse = async () => {
    try {
      // Navigate to the course detail page
      if (courseData.slug) {
        navigate(`/instructor/courses/${courseData.slug}`);
      } else {
        navigate('/instructor/courses');
      }
    } catch (error) {
      console.error('Error publishing course:', error);
    }
  };

  // Navigate to previous step
  const handlePrevStep = () => {
    prevStep();
  };
  // Navigate to next step after validation
  const handleNextStep = () => {
    const isValid = validateCurrentStep();

    if (isValid) {
      nextStep();
    }
  };

  // Render step content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <CourseBasicsStep />;
      case 2:
        return <CourseDetailsStep />;
      case 3:
        return <ModuleStructureStep />;
      case 4:
        return <ContentCreationStep />;
      case 5:
        return <ReviewPublishStep />;
      default:
        return <div>Unknown step</div>;
    }
  }; // Now rendering a simplified version to get past the context error
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Add switch editor banner if we have a course slug */}
      {courseData && courseData.slug && (
        <SwitchEditorBanner
          courseSlug={courseData.slug}
          currentEditor="wizard"
        />
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          {courseData.title || 'New Course'}
        </h1>
        <p className="text-gray-600">
          Complete all steps to create your course
        </p>
      </div>

      {/* Step indicator */}
      <div className="mb-6">
        <StepIndicator
          steps={[
            { label: 'Basics' },
            { label: 'Details' },
            { label: 'Modules' },
            { label: 'Content' },
            { label: 'Review' },
          ]}
          currentStep={currentStep}
          onChange={setStep}
        />
      </div>

      {/* Main content */}
      <Card className="mb-6">{renderStepContent()}</Card>

      {/* Navigation buttons */}
      <div className="flex justify-between mt-6">
        <Button
          color="secondary"
          variant="outlined"
          onClick={handlePrevStep}
          disabled={currentStep === 1}
        >
          Previous
        </Button>
        <div className="flex space-x-2">
          {currentStep < totalSteps ? (
            <Button color="primary" onClick={handleNextStep}>
              Next
            </Button>
          ) : (
            <Button color="success" onClick={handlePublishCourse}>
              Publish Course
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseWizardWrapper;
