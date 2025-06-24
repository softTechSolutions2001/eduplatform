import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/solid';
import React from 'react';
import { Button } from '../../../components/common';

const NotificationSystem = ({
  notifications = [],
  onDismiss,
  onAction,
  position = 'top-right',
  maxNotifications = 5,
}) => {
  const [visibleNotifications, setVisibleNotifications] = React.useState([]);

  React.useEffect(() => {
    setVisibleNotifications(notifications.slice(0, maxNotifications));
  }, [notifications, maxNotifications]);
  const getNotificationIcon = type => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-amber-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'info':
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getNotificationClasses = type => {
    const baseClasses = 'border-l-4 shadow-lg';
    switch (type) {
      case 'success':
        return `${baseClasses} bg-green-50 border-green-500`;
      case 'warning':
        return `${baseClasses} bg-yellow-50 border-yellow-500`;
      case 'error':
        return `${baseClasses} bg-red-50 border-red-500`;
      case 'info':
      default:
        return `${baseClasses} bg-blue-50 border-blue-500`;
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'top-right':
        return 'top-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2';
      case 'bottom-center':
        return 'bottom-4 left-1/2 transform -translate-x-1/2';
      default:
        return 'top-4 right-4';
    }
  };

  const handleDismiss = notification => {
    setVisibleNotifications(prev => prev.filter(n => n.id !== notification.id));
    onDismiss?.(notification);
  };

  const handleAction = (notification, action) => {
    onAction?.(notification, action);
    if (action.dismissAfterAction) {
      handleDismiss(notification);
    }
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div className={`fixed z-50 w-96 space-y-3 ${getPositionClasses()}`}>
      {visibleNotifications.map(notification => (
        <div
          key={notification.id}
          className={`
            rounded-lg p-4 transition-all duration-300 transform
            ${getNotificationClasses(notification.type)}
            animate-in slide-in-from-right-full
          `}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getNotificationIcon(notification.type)}
            </div>

            <div className="ml-3 flex-1">
              {/* Title */}
              {notification.title && (
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  {notification.title}
                </h4>
              )}

              {/* Message */}
              <p className="text-sm text-gray-700">{notification.message}</p>

              {/* Timestamp */}
              {notification.timestamp && (
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(notification.timestamp).toLocaleTimeString()}
                </p>
              )}

              {/* Actions */}
              {notification.actions && notification.actions.length > 0 && (
                <div className="mt-3 flex space-x-2">
                  {notification.actions.map((action, index) => (
                    <Button
                      key={index}
                      variant={action.variant || 'outline'}
                      size="sm"
                      onClick={() => handleAction(notification, action)}
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}

              {/* Progress Bar (for progress notifications) */}
              {notification.progress !== undefined && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>{notification.progressLabel || 'Progress'}</span>
                    <span>{Math.round(notification.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.min(notification.progress, 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* Dismiss Button */}
            {notification.dismissible !== false && (
              <div className="ml-4 flex-shrink-0">
                {' '}
                <button
                  className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none"
                  onClick={() => handleDismiss(notification)}
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Show more indicator */}
      {notifications.length > maxNotifications && (
        <div className="text-center">
          <button className="text-xs text-gray-500 hover:text-gray-700">
            +{notifications.length - maxNotifications} more notifications
          </button>
        </div>
      )}
    </div>
  );
};

// Notification Hook for easy usage
export const useNotifications = () => {
  const [notifications, setNotifications] = React.useState([]);

  const addNotification = React.useCallback(notification => {
    const id = Date.now().toString();
    const newNotification = {
      id,
      timestamp: new Date(),
      dismissible: true,
      ...notification,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-dismiss after timeout
    if (notification.timeout !== false) {
      const timeout = notification.timeout || 5000;
      setTimeout(() => {
        removeNotification(id);
      }, timeout);
    }

    return id;
  }, []);

  const removeNotification = React.useCallback(id => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const clearAll = React.useCallback(() => {
    setNotifications([]);
  }, []);

  const updateNotification = React.useCallback((id, updates) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, ...updates } : n))
    );
  }, []);

  // Convenience methods
  const success = React.useCallback(
    (message, options = {}) => {
      return addNotification({ ...options, type: 'success', message });
    },
    [addNotification]
  );

  const error = React.useCallback(
    (message, options = {}) => {
      return addNotification({
        ...options,
        type: 'error',
        message,
        timeout: false,
      });
    },
    [addNotification]
  );

  const warning = React.useCallback(
    (message, options = {}) => {
      return addNotification({ ...options, type: 'warning', message });
    },
    [addNotification]
  );

  const info = React.useCallback(
    (message, options = {}) => {
      return addNotification({ ...options, type: 'info', message });
    },
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    removeNotification,
    updateNotification,
    clearAll,
    success,
    error,
    warning,
    info,
  };
};

export default NotificationSystem;
