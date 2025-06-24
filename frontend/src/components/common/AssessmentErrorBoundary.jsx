/**
 * Specialized Error Boundary for Assessment Components
 * Provides contextual error handling for quiz, test, and assessment-related components
 */

import React from 'react';

class AssessmentErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Assessment Module Error:', error, errorInfo);
    this.setState({ errorInfo });

    // Log specific assessment errors for analytics
    if (this.props.onError) {
      this.props.onError(error, errorInfo, 'assessment');
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
        <div className="min-h-[400px] flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200">
          <div className="bg-white p-6 rounded-lg shadow-sm max-w-md w-full mx-4">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
              <svg
                className="w-6 h-6 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>

            <h3 className="text-lg font-semibold text-center mb-2 text-gray-900">
              Assessment Error
            </h3>

            <p className="text-sm text-gray-600 text-center mb-4">
              There was an issue loading the assessment content. Your progress
              has been saved.
            </p>

            {process.env.NODE_ENV === 'development' && (
              <div className="bg-gray-50 p-3 rounded mb-4 text-xs">
                <details>
                  <summary className="cursor-pointer text-gray-700 font-medium">
                    Error Details (Development)
                  </summary>
                  <pre className="mt-2 text-gray-600 whitespace-pre-wrap">
                    {this.state.error?.toString()}
                  </pre>
                  {this.state.errorInfo && (
                    <pre className="mt-2 text-gray-500 whitespace-pre-wrap text-xs">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  )}
                </details>
              </div>
            )}

            <div className="flex flex-col gap-2">
              <button
                onClick={this.resetError}
                disabled={this.state.retryCount >= 3}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {this.state.retryCount >= 3
                  ? 'Max Retries Reached'
                  : 'Try Again'}
              </button>

              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
              >
                Reload Page
              </button>

              {this.props.onNavigateBack && (
                <button
                  onClick={this.props.onNavigateBack}
                  className="w-full px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors"
                >
                  ← Return to Course
                </button>
              )}
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              If this error persists, please contact support or try refreshing
              the page.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default AssessmentErrorBoundary;
