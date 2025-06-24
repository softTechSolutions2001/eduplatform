/**
 * File: frontend/src/pages/instructor/components/SwitchEditorBanner.jsx
 * Version: 1.0.0
 * Date: 2025-06-01
 *
 * Banner component for wizard interface that allows users to switch
 * between the wizard and drag-and-drop builder editing modes
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

const SwitchEditorBanner = ({ courseSlug, currentEditor }) => {
  const navigate = useNavigate();

  if (!courseSlug) {
    return null; // Don't show for new courses without a slug
  }

  const handleSwitchEditor = () => {
    // Check if there are unsaved changes
    const hasUnsavedChanges = document.body.classList.contains(
      'has-unsaved-changes'
    );

    if (hasUnsavedChanges) {
      const confirmSwitch = window.confirm(
        'You have unsaved changes. Switching editors may cause you to lose these changes. Continue anyway?'
      );

      if (!confirmSwitch) {
        return;
      }
    }

    if (currentEditor === 'builder') {
      navigate(`/instructor/courses/wizard/${courseSlug}`);
    } else {
      navigate(`/instructor/courses/builder/${courseSlug}`);
    }
  };

  return (
    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-blue-700">
            You're using the{' '}
            <strong>
              {currentEditor === 'builder'
                ? 'drag-and-drop builder'
                : 'step-by-step wizard'}
            </strong>
            .
            {currentEditor === 'builder'
              ? ' Want a more guided approach?'
              : ' Want more visual flexibility?'}
          </p>
        </div>
        <button
          onClick={handleSwitchEditor}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          data-testid="switch-editor-btn"
        >
          Switch to {currentEditor === 'builder' ? 'Wizard' : 'Builder'}
        </button>
      </div>
    </div>
  );
};

export default SwitchEditorBanner;
