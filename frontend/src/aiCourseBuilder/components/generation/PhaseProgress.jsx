/**
 * Phase Progress - Real-time AI Generation Progress Component
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * Displays real-time progress for AI generation phases with detailed
 * status updates and completion indicators.
 */

import { useEffect, useState } from 'react';
import { AI_BUILDER_CONFIG } from '../../config/aiBuilderConfig';
import { useAIBuilderStore } from '../../store/aiBuilderStore';
import ProgressBar from '../ui/ProgressBar';

const PhaseProgress = ({ phase }) => {
  const { progress, generationStatus, isGenerating } = useAIBuilderStore();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);

  // Phase-specific steps
  const phaseSteps = {
    'outline-generation': [
      'Analyzing course requirements',
      'Generating course structure',
      'Creating module outlines',
      'Optimizing learning flow',
      'Finalizing course outline',
    ],
    'content-creation': [
      'Creating module content',
      'Generating lesson materials',
      'Adding interactive elements',
      'Creating assessments',
      'Enhancing content quality',
    ],
    enhancement: [
      'Analyzing content quality',
      'Generating improvements',
      'Adding engagement elements',
      'Optimizing learning outcomes',
      'Finalizing enhancements',
    ],
  };

  const steps = phaseSteps[phase] || ['Processing...'];

  // Simulate step progression
  useEffect(() => {
    if (!isGenerating) return;

    const stepDuration =
      AI_BUILDER_CONFIG.ai.generation.estimatedTime / steps.length;
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        const next = Math.min(prev + 1, steps.length - 1);
        if (next > prev) {
          setCompletedSteps(prevCompleted => [...prevCompleted, prev]);
        }
        return next;
      });
    }, stepDuration);

    return () => clearInterval(interval);
  }, [isGenerating, steps.length]);

  // Reset when generation starts
  useEffect(() => {
    if (isGenerating) {
      setCurrentStep(0);
      setCompletedSteps([]);
    }
  }, [isGenerating]);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            AI Generation Progress
          </h3>
          <p className="text-sm text-gray-600">
            {isGenerating
              ? 'Creating your course content...'
              : 'Ready to generate'}
          </p>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center space-x-2">
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
              <span className="text-sm text-primary-600">Generating</span>
            </>
          ) : progress === 100 ? (
            <>
              <div className="h-4 w-4 rounded-full bg-green-500"></div>
              <span className="text-sm text-green-600">Complete</span>
            </>
          ) : (
            <>
              <div className="h-4 w-4 rounded-full bg-gray-400"></div>
              <span className="text-sm text-gray-500">Ready</span>
            </>
          )}
        </div>
      </div>

      {/* Overall Progress */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Overall Progress
          </span>
          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
        </div>
        <ProgressBar progress={progress} className="h-2" />
      </div>

      {/* Step-by-Step Progress */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700">Generation Steps</h4>

        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(index);
          const isCurrent = currentStep === index && isGenerating;
          const isPending = index > currentStep;

          return (
            <div
              key={index}
              className={`flex items-center space-x-3 p-3 rounded-lg border ${
                isCompleted
                  ? 'border-green-200 bg-green-50'
                  : isCurrent
                    ? 'border-blue-200 bg-blue-50'
                    : 'border-gray-200 bg-gray-50'
              }`}
            >
              {/* Step Icon */}
              <div
                className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                  isCompleted
                    ? 'bg-green-500 text-white'
                    : isCurrent
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-300 text-gray-600'
                }`}
              >
                {isCompleted ? (
                  <svg
                    className="w-3 h-3"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : isCurrent ? (
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-white"></div>
                ) : (
                  <span className="text-xs font-medium">{index + 1}</span>
                )}
              </div>

              {/* Step Text */}
              <div className="flex-1">
                <p
                  className={`text-sm font-medium ${
                    isCompleted
                      ? 'text-green-800'
                      : isCurrent
                        ? 'text-blue-800'
                        : 'text-gray-600'
                  }`}
                >
                  {step}
                </p>

                {/* Step Status */}
                {isCompleted && (
                  <p className="text-xs text-green-600 mt-1">Completed</p>
                )}
                {isCurrent && (
                  <p className="text-xs text-blue-600 mt-1">In progress...</p>
                )}
              </div>

              {/* Duration Estimate */}
              <div className="text-xs text-gray-500">
                {isCompleted
                  ? '✓'
                  : isCurrent
                    ? `~${Math.ceil(AI_BUILDER_CONFIG.ai.generation.estimatedTime / steps.length / 1000)}s`
                    : '—'}
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Provider Info */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Powered by {AI_BUILDER_CONFIG.ai.providers.primary.name}</span>
          <span>{generationStatus || 'Ready'}</span>
        </div>
      </div>

      {/* Estimated Time Remaining */}
      {isGenerating && (
        <div className="mt-3 text-center">
          <p className="text-sm text-gray-600">
            Estimated time remaining:{' '}
            {Math.ceil(
              ((100 - progress) *
                AI_BUILDER_CONFIG.ai.generation.estimatedTime) /
                1000
            )}{' '}
            seconds
          </p>
        </div>
      )}
    </div>
  );
};

export default PhaseProgress;
