import React from 'react';

class AIBuilderErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can log the error to an error reporting service
    console.error('AI Course Builder Error:', error, errorInfo);
    this.setState({ errorInfo });

    // If you have an error tracking service (like Sentry), you could report the error here
    // reportErrorToService(error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
          <div className="bg-white p-8 rounded-lg shadow-md max-w-lg w-full">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-red-100 rounded-full mb-6">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                ></path>
              </svg>
            </div>

            <h2 className="text-2xl font-bold text-center mb-4">
              AI Course Builder Error
            </h2>

            <div className="bg-gray-50 p-4 rounded mb-6 overflow-auto max-h-60">
              <p className="font-mono text-sm text-red-600 whitespace-pre-wrap">
                {this.state.error && this.state.error.toString()}
              </p>
              {this.state.errorInfo && (
                <details className="mt-2">
                  <summary className="text-sm text-gray-700 cursor-pointer">
                    View Component Stack
                  </summary>
                  <p className="mt-2 font-mono text-xs text-gray-600 whitespace-pre-wrap">
                    {this.state.errorInfo.componentStack}
                  </p>
                </details>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Reload Page
              </button>
              <button
                onClick={this.resetError}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
              >
                Try Again
              </button>
            </div>

            <p className="text-sm text-gray-500 mt-6 text-center">
              If this error persists, please contact technical support.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default AIBuilderErrorBoundary;
