/**
 * File: src/components/common/ResumeButton.jsx
 * Version: 1.0.0
 * Date: 2025-05-14 16:34:40
 * Author: cadsanthanam
 *
 * Resume button component for quickly returning to the last lesson
 * Production-ready with error handling and fallbacks
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './index';

// Check localStorage availability
const isLocalStorageAvailable =
  typeof window !== 'undefined' &&
  window.localStorage &&
  (() => {
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      return true;
    } catch (e) {
      return false;
    }
  })();

// Safe localStorage operations
const safeGetLocalStorage = (key, defaultValue = null) => {
  if (!isLocalStorageAvailable) return defaultValue;
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : defaultValue;
  } catch (e) {
    console.error(`Error reading ${key} from localStorage:`, e);
    return defaultValue;
  }
};

const ResumeButton = ({
  courseSlug,
  className = '',
  size = 'medium',
  variant = 'primary',
  buttonText = 'Resume Learning',
  showIcon = true,
  onClick = null,
}) => {
  const [resumeData, setResumeData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Component mounted ref for cleanup
  const isMountedRef = React.useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!courseSlug) return;

    try {
      // Get resume data from localStorage
      const progressKey = `course_progress_${courseSlug}`;
      const existingProgress = safeGetLocalStorage(progressKey, {});

      // Validate data before using it
      if (
        existingProgress.last_viewed_lesson &&
        existingProgress.last_viewed_module &&
        !isNaN(existingProgress.last_viewed_lesson) &&
        !isNaN(existingProgress.last_viewed_module)
      ) {
        if (isMountedRef.current) {
          setResumeData({
            lessonId: existingProgress.last_viewed_lesson,
            moduleId: existingProgress.last_viewed_module,
            title: existingProgress.last_viewed_title || 'Last lesson',
          });
        }
      }
    } catch (error) {
      console.error('Error loading resume data:', error);
      if (isMountedRef.current) {
        setError(error);
      }
    }
  }, [courseSlug]);

  // Handler for navigation
  const handleClick = () => {
    if (!resumeData) return;

    if (onClick) {
      // Call custom click handler if provided
      onClick(resumeData);
    } else {
      // Default navigation behavior
      navigate(
        `/courses/${courseSlug}/content/${resumeData.moduleId}/${resumeData.lessonId}`
      );
    }
  };

  if (error || !resumeData) return null;

  return (
    <Button
      variant={variant}
      size={size}
      className={`flex items-center ${className}`}
      onClick={handleClick}
      title={`Resume: ${resumeData.title}`}
    >
      {showIcon && (
        <svg className="w-4 h-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
            clipRule="evenodd"
          />
        </svg>
      )}
      {buttonText}
    </Button>
  );
};

export default ResumeButton;
