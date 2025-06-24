/**
 * Specialized Error Boundary for Course Creation and Content Management
 * Provides contextual error handling for lesson creation, module management, and content workflows
 */

import React from 'react';

class ContentCreationErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      lastSaveTime: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Content Creation Error:', error, errorInfo);
    this.setState({
      errorInfo,
      lastSaveTime: localStorage.getItem('lastAutoSave') || null,
    });

    // Log specific content creation errors
    if (this.props.onError) {
      this.props.onError(error, errorInfo, 'content-creation');
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

  handleSaveAndRetry = () => {
    // Trigger any unsaved content save if callback provided
    if (this.props.onSaveContent) {
      this.props.onSaveContent();
    }
    this.resetError();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[600px] flex items-center justify-center bg-gray-50 p-4">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <div className="flex items-center justify-center w-14 h-14 mx-auto bg-yellow-100 rounded-full mb-4">
              <svg
                className="w-7 h-7 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </div>

            <h3 className="text-lg font-semibold text-center mb-3 text-gray-900">
              Content Creation Error
            </h3>

            <p className="text-sm text-gray-600 text-center mb-4">
              There was an issue with the content editor. Don't worry - your
              work is being saved automatically.
            </p>

            {this.state.lastSaveTime && (
              <div className="bg-green-50 border border-green-200 rounded p-3 mb-4">
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 text-green-600 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm text-green-800">
                    Last saved:{' '}
                    {new Date(this.state.lastSaveTime).toLocaleTimeString()}
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
              {this.props.onSaveContent && (
                <button
                  onClick={this.handleSaveAndRetry}
                  disabled={this.state.retryCount >= 3}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  Save & Try Again
                </button>
              )}

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
                Reload Editor
              </button>

              {this.props.onNavigateBack && (
                <button
                  onClick={this.props.onNavigateBack}
                  className="w-full px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors font-medium"
                >
                  ← Back to Course List
                </button>
              )}
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              Your content is automatically saved every few minutes to prevent
              data loss.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ContentCreationErrorBoundary;
