/**
 * Specialized Error Boundary for Instructor Dashboard Components
 * Provides contextual error handling for course creation, management, and instructor tools
 */

import React from 'react';

class InstructorErrorBoundary extends React.Component {
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
    console.error('Instructor Dashboard Error:', error, errorInfo);
    this.setState({ errorInfo });

    // Log specific instructor workflow errors
    if (this.props.onError) {
      this.props.onError(error, errorInfo, 'instructor');
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
        <div className="min-h-[500px] flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-lg shadow-md max-w-lg w-full mx-4">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-orange-100 rounded-full mb-6">
              <svg
                className="w-8 h-8 text-orange-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>

            <h2 className="text-xl font-bold text-center mb-4 text-gray-900">
              Instructor Dashboard Error
            </h2>

            <p className="text-gray-600 text-center mb-6">
              There was an issue with the instructor tools. Your work has been
              automatically saved.
            </p>

            {process.env.NODE_ENV === 'development' && (
              <div className="bg-gray-50 p-4 rounded mb-6 max-h-40 overflow-auto">
                <details>
                  <summary className="cursor-pointer text-gray-700 font-medium text-sm">
                    Error Details (Development)
                  </summary>
                  <pre className="mt-2 text-gray-600 whitespace-pre-wrap text-xs">
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

            <div className="flex flex-col gap-3">
              <button
                onClick={this.resetError}
                disabled={this.state.retryCount >= 3}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {this.state.retryCount >= 3
                  ? 'Max Retries Reached'
                  : 'Try Again'}
              </button>

              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors font-medium"
              >
                Reload Dashboard
              </button>

              {this.props.onNavigateHome && (
                <button
                  onClick={this.props.onNavigateHome}
                  className="w-full px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors font-medium"
                >
                  ← Return to Home
                </button>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Need help? Contact our{' '}
                <a
                  href="/support"
                  className="text-blue-600 hover:text-blue-800"
                  onClick={e => {
                    e.preventDefault();
                    if (this.props.onContactSupport) {
                      this.props.onContactSupport();
                    }
                  }}
                >
                  support team
                </a>
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default InstructorErrorBoundary;
