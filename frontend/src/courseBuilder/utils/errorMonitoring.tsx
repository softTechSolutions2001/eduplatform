// frontend/src/courseBuilder/utils/errorMonitoring.ts
import React, { useEffect } from 'react';

type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

interface ErrorMetadata {
    component?: string;
    action?: string;
    userId?: string | number;
    sessionId?: string;
    timestamp?: string;
    buildVersion?: string;
    featureFlags?: Record<string, boolean>;
    [key: string]: any;
}

interface ErrorOptions {
    severity?: ErrorSeverity;
    metadata?: ErrorMetadata;
    isFatal?: boolean;
    skipConsoleLog?: boolean;
}

interface ErrorReportingService {
    captureException(error: Error, options: {
        level: string;
        extra: ErrorMetadata;
        fatal: boolean;
    }): void;
}

// Extend Window interface for TypeScript
declare global {
    interface Window {
        errorReportingService?: ErrorReportingService;
        __BUILD_VERSION__?: string;
        __FEATURE_FLAGS__?: Record<string, boolean>;
    }
}

// Configuration
const CONFIG = {
    ENABLE_ERROR_TRACKING: process.env.NODE_ENV === 'production',
    ENABLE_CONSOLE_LOGGING: process.env.NODE_ENV !== 'production',
    MAX_METADATA_SIZE: 1024 * 10, // 10KB limit for metadata
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
} as const;

/**
 * Safely serializes data for error reporting
 * @param data Data to serialize
 * @param maxSize Maximum size in bytes
 * @returns Serialized string or truncated version
 */
const safeSerialize = (data: any, maxSize: number = CONFIG.MAX_METADATA_SIZE): string => {
    try {
        const serialized = JSON.stringify(data, (key, value) => {
            // Handle circular references and functions
            if (typeof value === 'function') return '[Function]';
            if (typeof value === 'object' && value !== null) {
                if (value.constructor && value.constructor.name !== 'Object') {
                    return `[${value.constructor.name}]`;
                }
            }
            return value;
        });

        if (serialized.length > maxSize) {
            return serialized.substring(0, maxSize) + '...[truncated]';
        }

        return serialized;
    } catch (error) {
        return '[Serialization Error]';
    }
};

/**
 * Gets current user context for error reporting
 * @returns User context metadata
 */
const getUserContext = (): Partial<ErrorMetadata> => {
    try {
        return {
            userAgent: navigator.userAgent,
            url: window.location.href,
            buildVersion: window.__BUILD_VERSION__ || 'unknown',
            featureFlags: window.__FEATURE_FLAGS__ || {},
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            timestamp: new Date().toISOString(),
        };
    } catch (error) {
        return { timestamp: new Date().toISOString() };
    }
};

/**
 * Reports error to external service with retry logic
 * @param error Error to report
 * @param metadata Error metadata
 * @param severity Error severity
 * @param isFatal Whether error is fatal
 */
const reportToService = async (
    error: Error,
    metadata: ErrorMetadata,
    severity: ErrorSeverity,
    isFatal: boolean
): Promise<void> => {
    if (!window.errorReportingService) {
        return;
    }

    let attempt = 0;
    const maxAttempts = CONFIG.RETRY_ATTEMPTS;

    while (attempt < maxAttempts) {
        try {
            await window.errorReportingService.captureException(error, {
                level: severity,
                extra: metadata,
                fatal: isFatal,
            });
            return; // Success, exit retry loop
        } catch (reportingError) {
            attempt++;
            if (attempt >= maxAttempts) {
                console.error('Failed to report error after', maxAttempts, 'attempts:', reportingError);
                return;
            }

            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * attempt));
        }
    }
};

/**
 * Track and report errors with comprehensive metadata
 * @param error Error object or message
 * @param options Error tracking options
 */
export const trackError = async (
    error: Error | string,
    options: ErrorOptions = {}
): Promise<void> => {
    const {
        severity = 'medium',
        metadata = {},
        isFatal = false,
        skipConsoleLog = false,
    } = options;

    try {
        const errorObject = typeof error === 'string' ? new Error(error) : error;

        // Build comprehensive metadata
        const enhancedMetadata: ErrorMetadata = {
            component: 'CourseBuilder',
            ...getUserContext(),
            ...metadata,
            errorName: errorObject.name,
            errorMessage: errorObject.message,
            stackTrace: errorObject.stack,
        };

        // Console logging (development and optionally production)
        if (CONFIG.ENABLE_CONSOLE_LOGGING || !skipConsoleLog) {
            const logMethod = severity === 'critical' ? console.error : console.warn;
            logMethod(
                `[${severity.toUpperCase()}] CourseBuilder Error:`,
                errorObject.message,
                {
                    error: errorObject,
                    metadata: enhancedMetadata,
                }
            );
        }

        // Production error reporting
        if (CONFIG.ENABLE_ERROR_TRACKING) {
            await reportToService(errorObject, enhancedMetadata, severity, isFatal);
        }

        // Critical errors should also be reported to console in production
        if (severity === 'critical' && CONFIG.ENABLE_ERROR_TRACKING) {
            console.error('Critical error in CourseBuilder:', errorObject.message);
        }
    } catch (trackingError) {
        // Fail silently but log to console to avoid error loops
        console.error('Error tracking failed:', trackingError);
    }
};

/**
 * Creates a wrapped version of a function that reports errors
 * @param fn Function to wrap
 * @param options Error options
 * @returns Wrapped function with error reporting
 */
export function withErrorTracking<T extends (...args: any[]) => any>(
    fn: T,
    options: ErrorOptions = {}
): (...args: Parameters<T>) => ReturnType<T> {
    return (...args: Parameters<T>): ReturnType<T> => {
        try {
            const result = fn(...args);

            // Handle async functions
            if (result instanceof Promise) {
                return result.catch((error: Error) => {
                    trackError(error, {
                        ...options,
                        metadata: {
                            ...options.metadata,
                            functionName: fn.name || 'anonymous',
                            arguments: safeSerialize(args, 512), // Smaller limit for args
                            isAsync: true,
                        },
                    });
                    throw error;
                }) as ReturnType<T>;
            }

            return result;
        } catch (error) {
            trackError(error as Error, {
                ...options,
                metadata: {
                    ...options.metadata,
                    functionName: fn.name || 'anonymous',
                    arguments: safeSerialize(args, 512),
                    isAsync: false,
                },
            });
            throw error;
        }
    };
}

/**
 * Hook for tracking component errors
 * @param componentName Name of the component
 * @returns Error tracking function
 */
export const useErrorTracking = (componentName: string) => {
    return (error: Error | string, options: ErrorOptions = {}) => {
        trackError(error, {
            ...options,
            metadata: {
                component: componentName,
                ...options.metadata,
            },
        });
    };
};

/**
 * Production-ready error boundary fallback component
 */
export const BuilderErrorFallback: React.FC<{
    error: Error;
    resetErrorBoundary: () => void;
    componentName?: string;
}> = ({
    error,
    resetErrorBoundary,
    componentName = 'CourseBuilder',
}) => {
        useEffect(() => {
            trackError(error, {
                severity: 'high',
                isFatal: true,
                metadata: {
                    component: 'ErrorBoundary',
                    action: 'component-crash',
                    crashedComponent: componentName,
                },
            });
        }, [error, componentName]);

        const handleReload = () => {
            try {
                window.location.reload();
            } catch (reloadError) {
                trackError(reloadError as Error, {
                    severity: 'medium',
                    metadata: {
                        component: 'ErrorBoundary',
                        action: 'reload-failed',
                    },
                });
            }
        };

        return (
            <div
      className= "error-container"
        role = "alert"
        aria - live="assertive"
        style = {{
            padding: '2rem',
                textAlign: 'center',
                    backgroundColor: '#fef2f2',
                        border: '1px solid #fecaca',
                            borderRadius: '0.5rem',
                                margin: '1rem',
      }
    }
    >
    <div className="error-icon" style = {{ fontSize: '3rem', marginBottom: '1rem' }}>
        ⚠️
</div>

    < h2 style = {{ color: '#dc2626', marginBottom: '1rem' }}>
        Something went wrong in the { componentName }
</h2>

    < p style = {{ color: '#6b7280', marginBottom: '1.5rem' }}>
        We've been notified about this issue and are working to fix it.
            </p>

{
    process.env.NODE_ENV !== 'production' && (
        <details
          className="error-details"
    style = {{
        marginBottom: '1.5rem',
            textAlign: 'left',
                backgroundColor: '#f9fafb',
                    padding: '1rem',
                        borderRadius: '0.25rem',
                            border: '1px solid #e5e7eb',
          }
}
        >
    <summary style={ { cursor: 'pointer', fontWeight: 'bold', marginBottom: '0.5rem' } }>
        Error Details
            </summary>
            < p style = {{ fontFamily: 'monospace', marginBottom: '0.5rem' }}>
                { error.message }
                </p>
{
    error.stack && (
        <pre style={
        {
            fontSize: '0.75rem',
                overflow: 'auto',
                    backgroundColor: '#f3f4f6',
                        padding: '0.5rem',
                            borderRadius: '0.25rem',
            }
    }>
        { error.stack }
        </pre>
          )
}
</details>
      )}

<div className="error-actions" style = {{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
    <button
          onClick={ resetErrorBoundary }
className = "primary-button"
style = {{
    backgroundColor: '#3b82f6',
        color: 'white',
            border: 'none',
                padding: '0.75rem 1.5rem',
                    borderRadius: '0.375rem',
                        cursor: 'pointer',
                            fontWeight: '500',
          }}
        >
    Try Again
        </button>

        < button
onClick = { handleReload }
className = "secondary-button"
style = {{
    backgroundColor: '#6b7280',
        color: 'white',
            border: 'none',
                padding: '0.75rem 1.5rem',
                    borderRadius: '0.375rem',
                        cursor: 'pointer',
                            fontWeight: '500',
          }}
        >
    Reload Page
        </button>
        </div>
        </div>
  );
};
