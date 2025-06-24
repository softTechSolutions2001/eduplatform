import React, { useCallback, useEffect, useState } from 'react';
import {
  UNSAFE_NavigationContext,
  useBeforeUnload,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { useCourseStore } from '../store/courseSlice';

interface DirtyPromptOptions {
  /** Message to show in the prompt */
  message?: string;
  /** Whether to enable the prompt */
  enabled?: boolean;
  /** Bypass conditions where true means don't show prompt */
  bypassConditions?: () => boolean;
}

/**
 * Custom blocker for React Router v6
 * This uses the unstable API but it's the recommended approach until there's an official solution
 */
const useNavigationBlocker = (shouldBlock: boolean, message: string) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { navigator } = React.useContext(UNSAFE_NavigationContext);

  useEffect(() => {
    if (!shouldBlock) return;

    // Check if navigator has a block method - if not, we can't block navigation
    if (!(navigator as any).block) {
      console.warn(
        'Navigation blocking is not supported in this browser or React Router version'
      );
      return;
    }

    // Save the current history.block function
    const unblock = (navigator as any).block((tx: any) => {
      const autoUnblockingTx = {
        ...tx,
        retry() {
          unblock();
          tx.retry();
        },
      };

      const targetPath =
        autoUnblockingTx.location.pathname + autoUnblockingTx.location.search;
      const currentPath = location.pathname + location.search;

      // Only block if we're actually changing routes
      if (targetPath !== currentPath && window.confirm(message)) {
        // User confirmed navigation - let it proceed
        unblock();
        navigate(targetPath);
      }
    });

    return () => {
      unblock();
    };
  }, [shouldBlock, message, navigate, location, navigator]);
};

/**
 * A simpler fallback implementation when navigator.block isn't available
 */
const useSimpleNavigationWarning = (shouldBlock: boolean, message: string) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Store the last pathname to detect navigation changes
  const lastPathRef = React.useRef(location.pathname);

  // Listen for route changes
  useEffect(() => {
    if (shouldBlock && location.pathname !== lastPathRef.current) {
      // We can't block navigation after it happens, but we can at least log a warning
      console.warn(
        'Navigation occurred without confirmation. Consider using a custom router to block navigation.'
      );
    }
    lastPathRef.current = location.pathname;
  }, [location, shouldBlock]);
};

/**
 * Hook that shows a prompt when navigating away with unsaved changes
 * @param options Configuration options
 * @returns Functions to interact with the prompt
 */
export const useDirtyPrompt = (options: DirtyPromptOptions = {}) => {
  const {
    message = 'You have unsaved changes. Are you sure you want to leave?',
    enabled = true,
    bypassConditions = () => false,
  } = options;

  const isDirty = useCourseStore(state => state.isDirty);
  const isSaving = useCourseStore(state => state.isSaving);
  const [isPromptActive, setIsPromptActive] = useState(false);

  // Determine if we should block navigation
  const shouldBlock = enabled && isDirty && !isSaving && !bypassConditions();

  // Set up React Router navigation blocking - with fallback
  const { navigator } = React.useContext(UNSAFE_NavigationContext);

  // Check if we can use the block method
  const canUseBlock = React.useMemo(() => {
    return typeof (navigator as any).block === 'function';
  }, [navigator]);

  // Use the appropriate hook based on browser support
  if (canUseBlock) {
    useNavigationBlocker(shouldBlock, message);
  } else {
    useSimpleNavigationWarning(shouldBlock, message);
  }

  // Show browser prompt when closing window/tab
  useBeforeUnload(
    event => {
      if (shouldBlock) {
        event.preventDefault();
        return message;
      }
      return undefined;
    },
    { capture: true }
  );

  // Set up prompt handling
  useEffect(() => {
    setIsPromptActive(shouldBlock);
  }, [shouldBlock]);

  // Provide a function to reset the dirty state and bypass the prompt
  const resetDirtyState = useCallback(() => {
    useCourseStore.getState().markClean();
  }, []);

  // Safe navigation that checks dirty state first
  const navigateSafe = useCallback(
    (to: string | number, options?: any) => {
      const navigateFunc = useNavigate();
      if (shouldBlock && !window.confirm(message)) {
        return;
      }

      if (typeof to === 'number') {
        navigateFunc(to);
      } else {
        navigateFunc(to, options);
      }
    },
    [shouldBlock, message]
  );

  return {
    isPromptActive,
    resetDirtyState,
    promptMessage: message,
    navigateSafe,
  };
};
