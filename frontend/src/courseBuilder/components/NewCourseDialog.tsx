import React, { useCallback, useEffect, useState } from 'react';
import courseBuilderAPI from '../api/courseBuilderAPI';
import CourseTitleInput from './CourseTitleInput';

interface NewCourseDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCourseCreated: (course: any) => void;
}

const NewCourseDialog: React.FC<NewCourseDialogProps> = ({
  isOpen,
  onClose,
  onCourseCreated,
}) => {
  const [title, setTitle] = useState('');
  const [isTitleValid, setIsTitleValid] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle ESC key press
  const handleEscKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose]
  );

  // Set up ESC key listener
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscKey);
    } else {
      document.removeEventListener('keydown', handleEscKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [isOpen, handleEscKey]);

  const handleCreateCourse = async () => {
    if (!title || !isTitleValid) return;

    try {
      setIsCreating(true);
      setError(null);

      const newCourse = await courseBuilderAPI.createDraft(title);
      onCourseCreated(newCourse);
    } catch (err: any) {
      console.error('Failed to create course:', err);
      setError(err.message || 'Failed to create course. Please try again.');

      // If the error is a title conflict, reset validity to force recheck
      if (err.message?.includes('title was just taken')) {
        setIsTitleValid(false);
      }
    } finally {
      setIsCreating(false);
    }
  };

  // Handle backdrop click - needs to stop propagation on dialog itself
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">Create a New Course</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
            aria-label="Close"
          >
            <span className="sr-only">Close</span>
            <svg
              className="h-6 w-6"
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

        <div className="mb-4">
          <p className="text-sm text-gray-500 mb-4">
            Your course needs a unique title. Please enter a title that hasn't
            been used before.
          </p>

          <CourseTitleInput
            onChange={setTitle}
            onValidityChange={setIsTitleValid}
          />
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleCreateCourse}
            disabled={!title || !isTitleValid || isCreating}
            className={`px-4 py-2 rounded-md text-sm font-medium text-white
              ${
                !title || !isTitleValid || isCreating
                  ? 'bg-blue-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
          >
            {isCreating ? (
              <div className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Creating...
              </div>
            ) : (
              'Create Course'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewCourseDialog;
