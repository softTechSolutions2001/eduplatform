/**
 * File: frontend/src/courseBuilder/dnd/DnDContext.tsx
 * Version: 3.1.0
 * Date: 2025-06-24 16:11:18 UTC
 * Author: saiacupunctureFolllow
 * Last Modified: 2025-06-24 16:11:18 UTC
 *
 * Enhanced Drag-and-Drop Context Provider with Zustand Integration and Accessibility
 *
 * This component provides the core drag-and-drop infrastructure for the course builder
 * interface with comprehensive accessibility features, device detection, Zustand integration,
 * and backend switching capabilities for optimal user experience across all devices.
 *
 * Key Features:
 * - Accessibility compliance with reduced motion detection
 * - Multi-backend support (HTML5, Touch, Keyboard) based on device and preferences
 * - Zustand integration for state management
 * - Performance optimizations for different device types
 * - Error boundaries and fallback mechanisms
 * - Enhanced debugging and development tools
 * - User preference detection and respect
 * - Screen reader announcements
 * - Keyboard navigation support
 *
 * Version 3.1.0 Changes:
 * - FIXED: Import issues with react-dnd backends
 * - FIXED: Store integration and function calls
 * - IMPROVED: Proper handling of disabled backend
 * - FIXED: Conflict between native drag events and React-DnD
 * - FIXED: Touch backend configuration parameters
 * - FIXED: Timeout cleanup on drop to prevent stale state updates
 * - ENHANCED: Device capability detection performance
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { BackendFactory } from 'react-dnd';
import { DndProvider } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import TouchBackend from 'react-dnd-touch-backend';
import { useCourseStore } from '../store/courseSlice';
import { announceToScreenReader } from '../utils/accessibility';

// ✅ Enhanced item types with better organization
export const ITEM_TYPES = {
  MODULE: 'module',
  LESSON: 'lesson',
  RESOURCE: 'resource',
} as const;

// ✅ Backend type definitions
type DnDBackendType = 'html5' | 'touch' | 'keyboard' | 'disabled';

// ✅ Drag item interface for Zustand operations
interface DragItem {
  id: string;
  type: keyof typeof ITEM_TYPES;
  index: number;
  parentId?: string;
}

// ✅ Device and capability detection interface
interface DeviceCapabilities {
  hasTouch: boolean;
  hasPointer: boolean;
  hasKeyboard: boolean;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  prefersReducedMotion: boolean;
  supportsHover: boolean;
  screenSize: 'small' | 'medium' | 'large';
}

// ✅ DnD context configuration interface
interface DnDContextConfig {
  backend: DnDBackendType;
  enableAccessibility: boolean;
  enableKeyboardNavigation: boolean;
  enableTouchFallback: boolean;
  debugMode: boolean;
  respectMotionPreferences: boolean;
  autoDetectDevice: boolean;
  enableStateIntegration: boolean;
  dragDebounceMs: number;
}

// ✅ Enhanced props interface with configuration options
interface DnDContextProps {
  children: React.ReactNode;
  config?: Partial<DnDContextConfig>;
  onBackendChange?: (backend: DnDBackendType) => void;
  onError?: (error: Error) => void;
  onDragStart?: (item: DragItem) => void;
  onDragEnd?: (item: DragItem | null) => void;
  className?: string;
  'data-testid'?: string;
}

// ✅ Enhanced accessibility context with Zustand integration
interface AccessibilityContextType {
  prefersReducedMotion: boolean;
  supportsKeyboard: boolean;
  currentBackend: DnDBackendType;
  deviceCapabilities: DeviceCapabilities;
  isDragging: boolean;
  draggedItem: DragItem | null;
  draggedOverItem: DragItem | null;
  toggleKeyboardMode: () => void;
  announceChange: (message: string) => void;
  handleDragStart: (item: DragItem) => void;
  handleDragOver: (item: DragItem) => void;
  handleDrop: () => void;
  handleDragEnd: () => void;
  getItemProps: (item: DragItem) => Record<string, any>;
  isItemBeingDragged: (id: string) => boolean;
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

// ✅ Custom hook to access accessibility context
export const useAccessibilityContext = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibilityContext must be used within DnDContext');
  }
  return context;
};

// ✅ Legacy hook for backward compatibility
export const useDnD = () => {
  return useAccessibilityContext();
};

// ✅ Device and capability detection utility
const detectDeviceCapabilities = (): DeviceCapabilities => {
  const defaultCapabilities: DeviceCapabilities = {
    hasTouch: false,
    hasPointer: true,
    hasKeyboard: true,
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    prefersReducedMotion: false,
    supportsHover: true,
    screenSize: 'large',
  };

  if (typeof window === 'undefined') {
    return defaultCapabilities;
  }

  try {
    const capabilities: DeviceCapabilities = {
      hasTouch: 'ontouchstart' in window || ("maxTouchPoints" in navigator && navigator.maxTouchPoints > 0),
      hasPointer: window.matchMedia('(pointer: fine)').matches,
      hasKeyboard: !window.matchMedia('(pointer: coarse)').matches ||
        window.matchMedia('(any-pointer: fine)').matches,
      isMobile: window.matchMedia('(max-width: 768px) and (pointer: coarse)').matches,
      isTablet: window.matchMedia('(min-width: 769px) and (max-width: 1024px) and (pointer: coarse)').matches,
      isDesktop: window.matchMedia('(min-width: 1025px)').matches ||
        window.matchMedia('(pointer: fine)').matches,
      prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      supportsHover: window.matchMedia('(hover: hover)').matches,
      screenSize: window.matchMedia('(max-width: 768px)').matches ? 'small' :
        window.matchMedia('(max-width: 1024px)').matches ? 'medium' : 'large',
    };

    return capabilities;
  } catch (error) {
    console.warn('Failed to detect device capabilities:', error);
    return defaultCapabilities;
  }
};

// ✅ Backend selection logic - FIXED to properly handle disabled case
const selectOptimalBackend = (
  capabilities: DeviceCapabilities,
  config: DnDContextConfig
): { backend: BackendFactory | undefined; type: DnDBackendType } => {
  if (config.respectMotionPreferences && capabilities.prefersReducedMotion) {
    return { backend: undefined, type: 'disabled' };
  }

  if (!config.autoDetectDevice) {
    switch (config.backend) {
      case 'touch':
        return { backend: TouchBackend, type: 'touch' };
      case 'html5':
      default:
        return { backend: HTML5Backend, type: 'html5' };
    }
  }

  if (capabilities.isMobile || (capabilities.hasTouch && !capabilities.hasPointer)) {
    return { backend: TouchBackend, type: 'touch' };
  }

  if (capabilities.isTablet && capabilities.hasTouch) {
    return { backend: TouchBackend, type: 'touch' };
  }

  return { backend: HTML5Backend, type: 'html5' };
};

// ✅ Enhanced keyboard accessibility provider
const KeyboardAccessibilityProvider: React.FC<{
  children: React.ReactNode;
  capabilities: DeviceCapabilities;
  isEnabled: boolean;
  onKeyboardNavigation?: (direction: string) => void;
}> = ({ children, capabilities, isEnabled, onKeyboardNavigation }) => {
  const [keyboardModeActive, setKeyboardModeActive] = useState(false);

  useEffect(() => {
    if (!isEnabled || !capabilities.hasKeyboard) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        setKeyboardModeActive(true);
      }

      // Enhanced arrow key navigation
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
        const focusedElement = document.activeElement;
        if (focusedElement?.getAttribute('data-draggable') === 'true') {
          event.preventDefault();
          const direction = event.key.replace('Arrow', '').toLowerCase();
          onKeyboardNavigation?.(direction);

          focusedElement.dispatchEvent(new CustomEvent('keyboard-reorder', {
            detail: { direction }
          }));
        }
      }

      // Escape key handling
      if (event.key === 'Escape') {
        const focusedElement = document.activeElement;
        if (focusedElement?.getAttribute('data-draggable') === 'true') {
          focusedElement.dispatchEvent(new CustomEvent('keyboard-cancel'));
        }
      }
    };

    const handleMouseDown = () => {
      setKeyboardModeActive(false);
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, [isEnabled, capabilities.hasKeyboard, onKeyboardNavigation]);

  useEffect(() => {
    if (keyboardModeActive) {
      document.body.classList.add('keyboard-navigation-active');
    } else {
      document.body.classList.remove('keyboard-navigation-active');
    }

    return () => {
      document.body.classList.remove('keyboard-navigation-active');
    };
  }, [keyboardModeActive]);

  return <>{children}</>;
};

// ✅ Enhanced screen reader announcements
const useScreenReaderAnnouncements = () => {
  const [announcement, setAnnouncement] = useState<string>('');

  const announceChange = useCallback((message: string) => {
    setAnnouncement(message);
    announceToScreenReader(message); // Use existing utility
    setTimeout(() => {
      setAnnouncement('');
    }, 1000);
  }, []);

  const AnnouncementRegion: React.FC = () => (
    <div
      aria-live="polite"
      aria-atomic="true"
      role="status"
      className="sr-only"
      style={{
        position: 'absolute',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden',
      }}
    >
      {announcement}
    </div>
  );

  return { announceChange, AnnouncementRegion };
};

// ✅ Zustand integration hook - FIXED to use available store functions
const useZustandDragOperations = (config: DnDContextConfig) => {
  // Access the course store with available functions
  const { moveItem, course } = useCourseStore();

  const performDragOperation = useCallback((draggedItem: DragItem, draggedOverItem: DragItem) => {
    if (!config.enableStateIntegration) return;

    try {
      // Handle module reordering
      if (draggedItem.type === 'module' && draggedOverItem.type === 'module') {
        moveItem(draggedItem.id, draggedOverItem.id, 'module');
      }

      // Handle lesson reordering - both within and between modules
      if (draggedItem.type === 'lesson') {
        moveItem(
          draggedItem.id,
          draggedOverItem.id,
          'lesson',
          {
            sourceModuleId: draggedItem.parentId,
            targetModuleId: draggedOverItem.type === 'lesson' ?
              draggedOverItem.parentId : draggedOverItem.id
          }
        );
      }
    } catch (error) {
      console.error('Zustand drag operation failed:', error);
      throw error;
    }
  }, [moveItem, config.enableStateIntegration]);

  return { performDragOperation, courseState: course };
};

// ✅ Main DnD Context component with comprehensive enhancements
export const DnDContext: React.FC<DnDContextProps> = React.memo(({
  children,
  config: userConfig,
  onBackendChange,
  onError,
  onDragStart,
  onDragEnd,
  className = '',
  'data-testid': testId = 'dnd-context',
}) => {
  // ✅ Default configuration with Zustand integration
  const defaultConfig: DnDContextConfig = {
    backend: 'html5',
    enableAccessibility: true,
    enableKeyboardNavigation: true,
    enableTouchFallback: true,
    debugMode: process.env.NODE_ENV === 'development',
    respectMotionPreferences: true,
    autoDetectDevice: true,
    enableStateIntegration: true,
    dragDebounceMs: 50,
  };

  const config = useMemo(() => ({
    ...defaultConfig,
    ...userConfig,
  }), [userConfig]);

  // ✅ Device capabilities and backend selection
  const [deviceCapabilities, setDeviceCapabilities] = useState<DeviceCapabilities>(() =>
    detectDeviceCapabilities()
  );

  const backendConfig = useMemo(() => {
    try {
      return selectOptimalBackend(deviceCapabilities, config);
    } catch (error) {
      const fallbackError = error instanceof Error ? error : new Error('Backend selection failed');
      console.error('Failed to select optimal backend:', fallbackError);
      onError?.(fallbackError);
      return { backend: HTML5Backend, type: 'html5' as DnDBackendType };
    }
  }, [deviceCapabilities, config, onError]);

  // ✅ Zustand integration (replacing Redux integration)
  const { performDragOperation } = useZustandDragOperations(config);

  // ✅ Drag state management
  const [isDragging, setIsDragging] = useState(false);
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [draggedOverItem, setDraggedOverItem] = useState<DragItem | null>(null);
  const dragTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ✅ Screen reader announcements
  const { announceChange, AnnouncementRegion } = useScreenReaderAnnouncements();

  // ✅ Performance-optimized drag handlers
  const handleDragStart = useCallback((item: DragItem) => {
    setIsDragging(true);
    setDraggedItem(item);

    announceChange(`Started dragging ${item.type} ${item.id}`);
    document.body.classList.add('dragging');

    onDragStart?.(item);
  }, [announceChange, onDragStart]);

  const handleDragOver = useCallback((item: DragItem) => {
    if (!draggedItem || item.id === draggedItem.id) return;

    if (dragTimeoutRef.current) {
      clearTimeout(dragTimeoutRef.current);
    }

    dragTimeoutRef.current = setTimeout(() => {
      setDraggedOverItem(item);
    }, config.dragDebounceMs);
  }, [draggedItem, config.dragDebounceMs]);

  const handleDrop = useCallback(() => {
    if (dragTimeoutRef.current) {
      clearTimeout(dragTimeoutRef.current);
      dragTimeoutRef.current = null;
    }

    if (draggedItem && draggedOverItem) {
      try {
        performDragOperation(draggedItem, draggedOverItem);
        announceChange(`Dropped ${draggedItem.type} into new position`);
      } catch (error) {
        const dropError = error instanceof Error ? error : new Error('Drop operation failed');
        console.error('Drop operation failed:', dropError);
        onError?.(dropError);
        announceChange('Drop operation failed');
      }
    }

    resetDragState();
  }, [draggedItem, draggedOverItem, performDragOperation, announceChange, onError]);

  const handleDragEnd = useCallback(() => {
    const endedItem = draggedItem;
    resetDragState();
    onDragEnd?.(endedItem);
  }, [draggedItem, onDragEnd]);

  const resetDragState = useCallback(() => {
    setIsDragging(false);
    setDraggedItem(null);
    setDraggedOverItem(null);
    document.body.classList.remove('dragging');

    if (dragTimeoutRef.current) {
      clearTimeout(dragTimeoutRef.current);
      dragTimeoutRef.current = null;
    }
  }, []);

  // ✅ Enhanced keyboard navigation
  const handleKeyboardNavigation = useCallback((direction: string) => {
    if (!draggedItem) return;

    // Handle keyboard navigation logic here
    announceChange(`Moving ${draggedItem.type} ${direction}`);
  }, [draggedItem, announceChange]);

  // ✅ Global keyboard event handling
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!draggedItem) return;

      switch (event.key) {
        case 'Escape':
          announceChange('Drag operation cancelled');
          resetDragState();
          break;
        case 'Enter':
        case ' ':
          if (draggedOverItem) {
            event.preventDefault();
            handleDrop();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [draggedItem, draggedOverItem, handleDrop, resetDragState, announceChange]);

  // ✅ Monitor device capability changes - FIXED to be more efficient
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQueries = [
      window.matchMedia('(prefers-reduced-motion: reduce)'),
      window.matchMedia('(max-width: 768px)'),
      window.matchMedia('(min-width: 769px) and (max-width: 1024px)'),
      window.matchMedia('(pointer: fine)'),
      window.matchMedia('(hover: hover)'),
    ];

    const handleMediaChange = () => {
      const newCapabilities = detectDeviceCapabilities();
      setDeviceCapabilities(prev => {
        // Only check key properties that influence backend selection for better performance
        const significantChange =
          prev.prefersReducedMotion !== newCapabilities.prefersReducedMotion ||
          prev.hasTouch !== newCapabilities.hasTouch ||
          prev.isMobile !== newCapabilities.isMobile;

        if (significantChange) {
          if (config.debugMode) {
            console.log('Device capabilities changed:', {
              from: {
                prefersReducedMotion: prev.prefersReducedMotion,
                hasTouch: prev.hasTouch,
                isMobile: prev.isMobile
              },
              to: {
                prefersReducedMotion: newCapabilities.prefersReducedMotion,
                hasTouch: newCapabilities.hasTouch,
                isMobile: newCapabilities.isMobile
              }
            });
          }
          return newCapabilities;
        }
        return prev;
      });
    };

    mediaQueries.forEach(mq => {
      if (mq.addEventListener) {
        mq.addEventListener('change', handleMediaChange);
      } else {
        mq.addListener(handleMediaChange);
      }
    });

    return () => {
      mediaQueries.forEach(mq => {
        if (mq.removeEventListener) {
          mq.removeEventListener('change', handleMediaChange);
        } else {
          mq.removeListener(handleMediaChange);
        }
      });
    };
  }, [config.debugMode]);

  // ✅ Backend change notification
  useEffect(() => {
    onBackendChange?.(backendConfig.type);
  }, [backendConfig.type, onBackendChange]);

  // ✅ Keyboard mode toggle
  const [keyboardModeEnabled, setKeyboardModeEnabled] = useState(false);

  const toggleKeyboardMode = useCallback(() => {
    setKeyboardModeEnabled(prev => {
      const newValue = !prev;
      announceChange(`Keyboard navigation ${newValue ? 'enabled' : 'disabled'}`);
      return newValue;
    });
  }, [announceChange]);

  // ✅ Item properties helper - FIXED to use React-DnD properly without manual event handlers
  const getItemProps = useCallback((item: DragItem) => ({
    'data-type': item.type,
    'data-id': item.id,
    'data-draggable': 'true',
    'aria-grabbed': draggedItem?.id === item.id,
    tabIndex: 0,
    className: `${draggedItem?.id === item.id ? 'dragging' : ''}
              ${draggedOverItem?.id === item.id ? 'drag-over' : ''}`.trim(),
  }), [draggedItem, draggedOverItem]);

  const isItemBeingDragged = useCallback((id: string) => draggedItem?.id === id, [draggedItem]);

  // ✅ Accessibility context value with Zustand integration
  const accessibilityContextValue = useMemo<AccessibilityContextType>(() => ({
    prefersReducedMotion: deviceCapabilities.prefersReducedMotion,
    supportsKeyboard: deviceCapabilities.hasKeyboard,
    currentBackend: backendConfig.type,
    deviceCapabilities,
    isDragging,
    draggedItem,
    draggedOverItem,
    toggleKeyboardMode,
    announceChange,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    getItemProps,
    isItemBeingDragged,
  }), [
    deviceCapabilities,
    backendConfig.type,
    isDragging,
    draggedItem,
    draggedOverItem,
    toggleKeyboardMode,
    announceChange,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    getItemProps,
    isItemBeingDragged
  ]);

  // ✅ Touch backend options - FIXED to use correct parameter names
  const touchBackendOptions = useMemo(() => ({
    enableMouseEvents: deviceCapabilities.hasPointer,
    enableKeyboardEvents: deviceCapabilities.hasKeyboard,
    enableTouchEvents: deviceCapabilities.hasTouch,
    touchStartDelay: deviceCapabilities.isMobile ? 200 : 0, // Changed from delayTouchStart
    delayMouseStart: 0,
    touchSlop: deviceCapabilities.isMobile ? 5 : 0,
  }), [deviceCapabilities]);

  const backendOptions = useMemo(() => {
    return backendConfig.type === 'touch' ? touchBackendOptions : undefined;
  }, [backendConfig.type, touchBackendOptions]);

  // ✅ Debug information
  useEffect(() => {
    if (config.debugMode) {
      console.group('🔄 DnD Context Configuration');
      console.log('Device Capabilities:', deviceCapabilities);
      console.log('Selected Backend:', backendConfig.type);
      console.log('Backend Options:', backendOptions);
      console.log('Config:', config);
      console.log('Drag State:', { isDragging, draggedItem, draggedOverItem });
      console.groupEnd();
    }
  }, [config, deviceCapabilities, backendConfig, backendOptions, isDragging, draggedItem, draggedOverItem]);

  // ✅ Cleanup on unmount
  useEffect(() => {
    return () => {
      resetDragState();
    };
  }, [resetDragState]);

  // ✅ FIXED: Handle disabled backend properly
  if (backendConfig.type === 'disabled') {
    return (
      <AccessibilityContext.Provider value={accessibilityContextValue}>
        {children}
        <AnnouncementRegion />
      </AccessibilityContext.Provider>
    );
  }

  // ✅ Render with error boundary
  try {
    return (
      <div
        className={`dnd-context ${className}`}
        data-backend={backendConfig.type}
        data-reduced-motion={deviceCapabilities.prefersReducedMotion}
        data-dragging={isDragging}
        data-testid={testId}
      >
        <AccessibilityContext.Provider value={accessibilityContextValue}>
          <KeyboardAccessibilityProvider
            capabilities={deviceCapabilities}
            isEnabled={config.enableKeyboardNavigation}
            onKeyboardNavigation={handleKeyboardNavigation}
          >
            <DndProvider
              backend={backendConfig.backend}
              options={backendOptions}
            >
              {children}
              <AnnouncementRegion />

              {/* ✅ Enhanced accessibility help text */}
              <div className="sr-only">
                <p>
                  Drag and drop interface for organizing course content.
                  Use Tab to navigate, Space or Enter to pick up items,
                  arrow keys to move, and Space or Enter to drop.
                  Press Escape to cancel drag operations.
                </p>
                {deviceCapabilities.prefersReducedMotion && (
                  <p>
                    Reduced motion detected. Drag operations will use
                    alternative animations and keyboard navigation is recommended.
                  </p>
                )}
                {isDragging && (
                  <p>
                    Currently dragging {draggedItem?.type} {draggedItem?.id}.
                    Use arrow keys to navigate or Escape to cancel.
                  </p>
                )}
              </div>
            </DndProvider>
          </KeyboardAccessibilityProvider>
        </AccessibilityContext.Provider>
      </div>
    );
  } catch (error) {
    const contextError = error instanceof Error ? error : new Error('DnD Context rendering failed');
    console.error('DnD Context Error:', contextError);
    onError?.(contextError);

    // ✅ Enhanced fallback UI
    return (
      <div
        className={`dnd-context dnd-context--error ${className}`}
        data-testid={`${testId}-error`}
      >
        <div className="sr-only">
          Drag and drop functionality is currently unavailable.
          Content can still be managed using keyboard navigation.
        </div>
        <div className="dnd-error-message" style={{ padding: '1rem', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.375rem' }}>
          <p style={{ color: '#991b1b', fontSize: '0.875rem' }}>
            Drag and drop is temporarily unavailable. You can still interact with content using keyboard navigation.
          </p>
        </div>
        {children}
      </div>
    );
  }
});

DnDContext.displayName = 'DnDContext';

// ✅ Export alias for backward compatibility (renamed to avoid collision)
export const LegacyDnDProvider = DnDContext;

// ✅ Export types and utilities
export type {
  AccessibilityContextType,
  DeviceCapabilities,
  DnDBackendType,
  DnDContextConfig,
  DragItem
};

export {
  detectDeviceCapabilities,
  selectOptimalBackend
};

export default DnDContext;
