/**
 * File: src/components/common/ErrorBoundary.jsx
 * Version: 1.0.0
 * Date: 2025-08-12 15:22:45
 * Author: cadsanthanam
 *
 * React Error Boundary component for graceful error handling
 * Catches JavaScript errors in child component tree and displays fallback UI
 */

import React, { Component } from 'react';

class ErrorBoundary extends Component {
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
    // Log the error to an error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });

    // If an onError prop exists, call it with the error details
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      if (this.props.renderFallback) {
        return this.props.renderFallback(
          this.state.error,
          this.state.errorInfo
        );
      }

      // Default error view
      return (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 my-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Something went wrong
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
                {this.props.showStack && this.state.errorInfo && (
                  <details className="mt-2 text-xs whitespace-pre-wrap">
                    <summary>Error Details</summary>
                    {this.state.errorInfo.componentStack}
                  </details>
                )}
              </div>
              {this.props.resetErrorBoundary && (
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={this.props.resetErrorBoundary}
                    className="rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-800 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2"
                  >
                    Try again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    // If no error, render children
    return this.props.children;
  }
}

export default ErrorBoundary;
