/**
 * Error Boundary for Course Content Display
 * Provides contextual error handling for course lesson playback and content viewing
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

class CourseContentErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      lastPlaybackPosition: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Course Content Error:', error, errorInfo);
    this.setState({
      errorInfo,
      lastPlaybackPosition:
        localStorage.getItem('lastPlaybackPosition') || null,
    });

    // Log specific content errors
    if (this.props.onError) {
      this.props.onError(error, errorInfo, 'course-content');
    }
  }

  resetError = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
    }));
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[500px] flex items-center justify-center bg-gray-50 p-4">
          <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full">
            <div className="flex items-center justify-center w-14 h-14 mx-auto bg-blue-100 rounded-full mb-4">
              <svg
                className="w-7 h-7 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </div>

            <h3 className="text-lg font-semibold text-center mb-3 text-gray-900">
              Content Display Error
            </h3>

            <p className="text-sm text-gray-600 text-center mb-4">
              There was an issue loading the lesson content. We've saved your
              progress.
            </p>

            {this.state.lastPlaybackPosition && (
              <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 text-blue-600 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm text-blue-800">
                    Progress saved at{' '}
                    {new Date(
                      parseInt(this.state.lastPlaybackPosition)
                    ).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            )}

            {process.env.NODE_ENV === 'development' && (
              <div className="bg-gray-50 p-3 rounded mb-4 text-xs max-h-32 overflow-auto">
                <details>
                  <summary className="cursor-pointer text-gray-700 font-medium">
                    Error Details (Development)
                  </summary>
                  <pre className="mt-2 text-gray-600 whitespace-pre-wrap">
                    {this.state.error?.toString()}
                  </pre>
                </details>
              </div>
            )}

            <div className="space-y-2">
              <button
                onClick={this.resetError}
                disabled={this.state.retryCount >= 3}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {this.state.retryCount >= 3
                  ? 'Max Retries Reached'
                  : 'Try Again'}
              </button>

              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors font-medium"
              >
                Reload Page
              </button>

              {this.props.onNavigateToCourse && (
                <button
                  onClick={this.props.onNavigateToCourse}
                  className="w-full px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors font-medium"
                >
                  ← Back to Course Home
                </button>
              )}
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              Your progress in this course is always saved automatically.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default function CourseContentErrorBoundaryWrapper(props) {
  const navigate = useNavigate();

  const handleNavigateToCourse = () => {
    // Extract course slug from URL and navigate back to course landing page
    const pathSegments = window.location.pathname.split('/');
    const courseSlugIndex = pathSegments.indexOf('courses') + 1;

    if (courseSlugIndex > 0 && courseSlugIndex < pathSegments.length) {
      const courseSlug = pathSegments[courseSlugIndex];
      navigate(`/courses/${courseSlug}`);
    } else {
      // Fallback to courses page if can't determine specific course
      navigate('/courses');
    }
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Course Content Error:', { error, errorInfo, context });

    // Save playback position
    if (props.currentTime) {
      localStorage.setItem('lastPlaybackPosition', Date.now().toString());
      localStorage.setItem('lastContentPosition', props.currentTime.toString());
    }
  };

  return (
    <CourseContentErrorBoundary
      onNavigateToCourse={handleNavigateToCourse}
      onError={handleError}
      {...props}
    />
  );
}
