/**
 * Course Generation Wizard - 5-Phase AI-Powered Workflow
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * A comprehensive wizard that guides instructors through the AI-assisted
 * course creation process. Features real-time AI generation, progress tracking,
 * and seamless database integration.
 */

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';
import { useAIGeneration } from '../hooks/useAIGeneration';
import { useAIBuilderStore } from '../store/aiBuilderStore';

// Phase Components
import ContentEditor from './content/ContentEditor';
import EnhancementSuggestions from './content/EnhancementSuggestions';
import ContentPreview from './generation/ContentPreview';
import PhaseProgress from './generation/PhaseProgress';
import BasicInfoForm from './input/BasicInfoForm';
import ObjectivesInput from './input/ObjectivesInput';
import CourseOutlinePreview from './preview/CourseOutlinePreview';
import ModulePreview from './preview/ModulePreview';

// UI Components
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import AIBuilderErrorBoundary from './ui/AIBuilderErrorBoundary';
import PhaseIndicator from './ui/PhaseIndicator';
import ProgressBar from './ui/ProgressBar';

const CourseGenerationWizard = () => {
  const navigate = useNavigate();
  const { draftId } = useParams(); // Get draftId from route parameters
  const {
    currentPhase,
    phaseData,
    courseData,
    isGenerating,
    error,
    progress,
    updatePhaseData,
    setCurrentPhase,
    completeCourseCreation,
    saveProgress,
    loadDraft,
  } = useAIBuilderStore();

  const {
    generateCourseOutline,
    generateModuleContent,
    generateLessonContent,
    enhanceContent,
    generateAssessments,
    isGenerating: aiIsGenerating,
    error: aiError,
  } = useAIGeneration();

  const [validationErrors, setValidationErrors] = useState({});
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);

  // Get current phase configuration
  const currentPhaseConfig = AI_BUILDER_CONFIG.workflow.phases.find(
    phase => phase.id === currentPhase
  );

  // Load existing draft if draftId is provided
  useEffect(() => {
    if (draftId) {
      loadDraft(draftId).catch(err => {
        console.error('Error loading draft:', err);
      });
    }
  }, [draftId, loadDraft]);

  // Auto-save functionality
  useEffect(() => {
    if (autoSaveEnabled && phaseData[currentPhase]) {
      const saveTimer = setTimeout(() => {
        // Auto-save phase data
        console.log(
          'Auto-saving phase data:',
          currentPhase,
          phaseData[currentPhase]
        );
        saveProgress();
      }, AI_BUILDER_CONFIG.ui.autoSave.interval);

      return () => clearTimeout(saveTimer);
    }
  }, [phaseData, currentPhase, autoSaveEnabled, saveProgress, draftId]);

  // Handle phase navigation
  const handleNext = async () => {
    try {
      // Validate current phase
      const isValid = await validateCurrentPhase();
      if (!isValid) return;

      // Get next phase
      const currentIndex = AI_BUILDER_CONFIG.workflow.phases.findIndex(
        phase => phase.id === currentPhase
      );

      if (currentIndex < AI_BUILDER_CONFIG.workflow.phases.length - 1) {
        const nextPhase = AI_BUILDER_CONFIG.workflow.phases[currentIndex + 1];
        setCurrentPhase(nextPhase.id);

        // Trigger AI generation for appropriate phases
        await triggerAIGeneration(nextPhase.id);
      } else {
        // Complete course creation
        await handleCourseCompletion();
      }
    } catch (error) {
      console.error('Error navigating to next phase:', error);
    }
  };

  const handlePrevious = () => {
    const currentIndex = AI_BUILDER_CONFIG.workflow.phases.findIndex(
      phase => phase.id === currentPhase
    );

    if (currentIndex > 0) {
      const previousPhase = AI_BUILDER_CONFIG.workflow.phases[currentIndex - 1];
      setCurrentPhase(previousPhase.id);
    }
  };

  // Validate current phase data
  const validateCurrentPhase = async () => {
    const errors = {};
    const currentData = phaseData[currentPhase] || {};

    switch (currentPhase) {
      case 'basic-info':
        if (!currentData.title?.trim()) {
          errors.title = 'Course title is required';
        }
        if (!currentData.description?.trim()) {
          errors.description = 'Course description is required';
        }
        if (!currentData.category) {
          errors.category = 'Course category is required';
        }
        break;

      case 'learning-objectives':
        if (!currentData.objectives?.length) {
          errors.objectives = 'At least one learning objective is required';
        }
        break;

      case 'outline-generation':
        if (!courseData.outline) {
          errors.outline = 'Course outline generation is required';
        }
        break;

      case 'content-creation':
        if (!courseData.modules?.length) {
          errors.modules = 'At least one module must be created';
        }
        break;

      case 'review-finalize':
        if (!courseData.isComplete) {
          errors.completion = 'Course must be fully reviewed before completion';
        }
        break;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Trigger AI generation based on phase
  const triggerAIGeneration = async phaseId => {
    try {
      switch (phaseId) {
        case 'outline-generation':
          await generateCourseOutline({
            title: phaseData['basic-info']?.title,
            description: phaseData['basic-info']?.description,
            objectives: phaseData['learning-objectives']?.objectives,
            category: phaseData['basic-info']?.category,
            level: phaseData['basic-info']?.level,
          });
          break;

        case 'content-creation':
          if (courseData.outline) {
            await Promise.all(
              courseData.outline.modules.map(module =>
                generateModuleContent(module)
              )
            );
          }
          break;

        case 'review-finalize':
          await enhanceContent(courseData);
          break;
      }
    } catch (error) {
      console.error('Error in AI generation:', error);
    }
  };

  // Handle course completion
  const handleCourseCompletion = async () => {
    try {
      const completedCourse = await completeCourseCreation(draftId);

      // Navigate to course management
      navigate(`/instructor/courses/${completedCourse.slug}`);
    } catch (error) {
      console.error('Error completing course creation:', error);
    }
  };

  // Render phase content
  const renderPhaseContent = () => {
    const content = (() => {
      switch (currentPhase) {
        case 'basic-info':
          return (
            <BasicInfoForm
              data={phaseData['basic-info'] || {}}
              onChange={data => updatePhaseData('basic-info', data)}
              errors={validationErrors}
            />
          );

        case 'learning-objectives':
          return (
            <ObjectivesInput
              data={phaseData['learning-objectives'] || {}}
              onChange={data => updatePhaseData('learning-objectives', data)}
              errors={validationErrors}
            />
          );

        case 'outline-generation':
          return (
            <div className="space-y-6">
              <PhaseProgress phase={currentPhase} />
              {courseData.outline ? (
                <CourseOutlinePreview outline={courseData.outline} />
              ) : (
                <ContentPreview
                  title="Generating Course Outline"
                  description="AI is creating a comprehensive course structure based on your inputs..."
                />
              )}
            </div>
          );

        case 'content-creation':
          return (
            <div className="space-y-6">
              <PhaseProgress phase={currentPhase} />
              {courseData.modules?.length ? (
                <div className="space-y-4">
                  {courseData.modules.map(module => (
                    <ModulePreview
                      key={module.id || `module-${module.title}`}
                      module={module}
                    />
                  ))}
                </div>
              ) : (
                <ContentPreview
                  title="Creating Module Content"
                  description="AI is developing detailed lesson content for each module..."
                />
              )}
            </div>
          );

        case 'review-finalize':
          return (
            <div className="space-y-6">
              <ContentEditor courseData={courseData} />
              <EnhancementSuggestions courseData={courseData} />
            </div>
          );

        default:
          return <div>Unknown phase: {currentPhase}</div>;
      }
    })();

    // Wrap content with animation
    return (
      <div className="transition-all duration-300 ease-in-out animate-fade-in">
        {content}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Progress Indicator */}
      <div className="mb-8">
        <AIBuilderErrorBoundary>
          <PhaseIndicator
            phases={AI_BUILDER_CONFIG.workflow.phases}
            currentPhase={currentPhase}
          />
          <ProgressBar
            progress={progress}
            showPercentage={true}
            className="mt-4"
          />
        </AIBuilderErrorBoundary>
      </div>

      {/* Phase Content */}
      <Card className="p-8">
        {/* Phase Header */}{' '}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {currentPhaseConfig ? currentPhaseConfig.name : 'Course Generation'}
          </h2>
          <p className="text-gray-600">
            {currentPhaseConfig
              ? currentPhaseConfig.description
              : 'Creating your course...'}
          </p>
        </div>
        {/* Phase Content */}
        <div className="mb-8">{renderPhaseContent()}</div>
        {/* Navigation Controls */}
        <div className="flex justify-between items-center pt-6 border-t border-gray-200">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={
                currentPhase === 'basic-info' || isGenerating || aiIsGenerating
              }
            >
              Previous
            </Button>
          </div>

          <div className="flex items-center space-x-4">
            {/* Auto-save indicator */}
            {autoSaveEnabled && (
              <span className="text-sm text-gray-500">Auto-save enabled</span>
            )}

            {/* Error display */}
            {(error || aiError) && (
              <span className="text-sm text-red-600">{error || aiError}</span>
            )}

            {/* Next/Complete button */}
            <Button
              variant="primary"
              onClick={handleNext}
              disabled={isGenerating || aiIsGenerating}
              loading={isGenerating || aiIsGenerating}
            >
              {currentPhase === 'review-finalize' ? 'Complete Course' : 'Next'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Help Panel */}
      <Card className="mt-6 p-6 bg-blue-50">
        <h3 className="font-semibold text-blue-900 mb-2">
          💡 {currentPhaseConfig?.title} Tips
        </h3>
        <p className="text-blue-800 text-sm">
          {currentPhaseConfig?.helpText ||
            'Follow the prompts to complete this phase.'}
        </p>
      </Card>
    </div>
  );
};

export default CourseGenerationWizard;
