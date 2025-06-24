// fmt: off
// isort: skip_file
// Timestamp: 2024-06-15 - Step Indicator component for multi-step forms and wizards

import React from 'react';
import PropTypes from 'prop-types';

/**
 * StepIndicator Component
 *
 * A flexible component for displaying multi-step progress indicators with:
 * - Optional steps with labels
 * - Clickable steps for navigation
 * - Completion status indicators
 * - Responsive design for mobile and desktop
 */
const StepIndicator = ({
  steps,
  currentStep,
  onChange = () => {},
  className = '',
}) => {
  // Handle step click if needed
  const handleStepClick = index => {
    if (onChange) {
      onChange(index + 1); // Convert to 1-indexed for consistency
    }
  };

  return (
    <div className={`w-full ${className}`}>
      <div className="hidden sm:flex items-center">
        {steps.map((step, index) => {
          const isActive = index + 1 === currentStep;
          const isCompleted = step.completed || index + 1 < currentStep;

          return (
            <React.Fragment key={index}>
              {/* Step circle */}
              <div
                className={`relative flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors cursor-pointer
                  ${
                    isActive
                      ? 'bg-primary-100 border-primary-600 text-primary-600'
                      : isCompleted
                        ? 'bg-primary-600 border-primary-600 text-white'
                        : 'bg-white border-gray-300 text-gray-500'
                  }`}
                onClick={() => handleStepClick(index)}
              >
                {isCompleted ? (
                  <svg
                    className="w-4 h-4"
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
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>

              {/* Step label */}
              <div className="ml-2 text-sm font-medium text-gray-700">
                {step.label}
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-4 h-0.5 bg-gray-200">
                  <div
                    className="h-full bg-primary-600 transition-all"
                    style={{ width: isCompleted ? '100%' : '0%' }}
                  ></div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Mobile version */}
      <div className="sm:hidden">
        <nav className="flex justify-between items-center">
          {steps.map((step, index) => {
            const isActive = index + 1 === currentStep;
            const isCompleted = step.completed || index + 1 < currentStep;

            return (
              <button
                key={index}
                type="button"
                className={`flex flex-col items-center 
                  ${isActive ? 'text-primary-600' : isCompleted ? 'text-primary-500' : 'text-gray-500'}`}
                onClick={() => handleStepClick(index)}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs
                    ${
                      isActive
                        ? 'bg-primary-100 border border-primary-600 text-primary-600'
                        : isCompleted
                          ? 'bg-primary-600 border border-primary-600 text-white'
                          : 'bg-white border border-gray-300 text-gray-500'
                    }`}
                >
                  {isCompleted ? (
                    <svg
                      className="w-3 h-3"
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
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </div>
                <span className="text-xs mt-1 hidden md:block">
                  {step.label}
                </span>
              </button>
            );
          })}
        </nav>

        {/* Progress bar for mobile */}
        <div className="mt-2 h-1 bg-gray-200 rounded">
          <div
            className="h-full bg-primary-600 rounded transition-all"
            style={{
              width: `${((currentStep - 1) / (steps.length - 1)) * 100}%`,
            }}
          ></div>
        </div>
      </div>
    </div>
  );
};

StepIndicator.propTypes = {
  /** Array of step objects with label and completed status */
  steps: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      completed: PropTypes.bool,
    })
  ).isRequired,
  /** Current active step (1-indexed) */
  currentStep: PropTypes.number.isRequired,
  /** Optional callback for when a step is clicked */
  onChange: PropTypes.func,
  /** Additional className to apply */
  className: PropTypes.string,
};

export default StepIndicator;
