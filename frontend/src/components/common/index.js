/**
 * File: frontend/src/components/common/index.js
 * Version: 2.1.2
 * Date: 2025-05-24 12:00:00
 * Author: mohithasanthanam
 * Last Modified: 2025-05-24 12:00:00 UTC
 *
 * Common Components Index - Central Export Hub
 *
 * This file serves as a central export point for all common/reusable components.
 * Enhanced exports for course creation workflow components with backend compatibility.
 *
 * This pattern provides several benefits:
 *
 * 1. Simplified Imports: Instead of importing each component individually from its own file,
 *    you can import multiple components from this single entry point:
 *    import { Button, Card, Badge } from '../components/common';
 *
 * 2. Better Organization: It makes the codebase more organized by providing a clear
 *    catalog of available reusable components.
 *
 * 3. Easier Maintenance: When components need to be renamed or restructured,
 *    you only need to update the exports here rather than throughout the codebase.
 *
 * 4. Discoverability: New team members can quickly see what components are available
 *    by looking at this file.
 *
 * Key Improvements:
 * 1. Added ContentAccessController for restricted content handling
 * 2. Added utility functions compatible with existing backend
 * 3. Better organization and documentation
 * 4. Case-insensitive pattern matching for content restrictions
 *
 * Connected files that import from this index:
 * - frontend/src/pages/instructor/CourseWizard.jsx - Course creation UI
 * - frontend/src/pages/instructor/wizardSteps/*.jsx - Wizard step components
 * - All other components that use common UI elements
 */

// UI Elements
import Button, { Button as ButtonComponent } from './Button';
import Card, { Card as CardComponent } from './Card';
import Badge, { Badge as BadgeComponent } from './Badge';
import Avatar from './Avatar';
import Rating from './Rating';
import Alert from './Alert';
import ProgressBar from './ProgressBar';
import Skeleton, { TextSkeleton, CardSkeleton } from './Skeleton';
import Tooltip from './Tooltip';
import AnimatedElement from './AnimatedElement';
import Certificate from './Certificate';
import Container from './Container';
import LoadingScreen from './LoadingScreen';
import ResumeButton from './ResumeButton';
import BookmarksList from './BookmarksList';
import Spinner from './Spinner';
import ErrorBoundary from './ErrorBoundary';

// Form Elements
import FormInput from './FormInput';
import TagInput from './TagInput';

// Layout Components
import Modal from './Modal';
import Tabs from './Tabs';
import Accordion from './Accordion';
import StepIndicator from './StepIndicator';
import ResourceCard from './ResourceCard';
import SearchBar from './SearchBar';
import Sidebar from './Sidebar';
import ContentAccessController from './ContentAccessController';
import Dropdown from './Dropdown';
import Pagination from './Pagination';
import ProfileBadge from './ProfileBadge';

// Export individual components (alphabetically ordered for better discoverability)
export {
  // UI Elements
  Accordion,
  Alert,
  AnimatedElement,
  Avatar,
  Badge,
  BadgeComponent,
  BookmarksList,
  Button,
  ButtonComponent,
  Card,
  CardComponent,
  CardSkeleton,
  Certificate,
  Container,
  ContentAccessController,
  Dropdown,
  ErrorBoundary,

  // Form Elements
  FormInput,

  // Layout Components
  LoadingScreen,
  Modal,
  Pagination,
  ProfileBadge,
  ProgressBar,
  Rating,
  ResourceCard,
  ResumeButton,
  SearchBar,
  Sidebar,
  Skeleton,
  Spinner,
  StepIndicator,
  Tabs,
  TagInput,
  TextSkeleton,
  Tooltip,
};

// Export utility functions compatible with existing backend
export const getInitials = name => {
  if (!name) return '';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase();
};

/**
 * Format duration string for display
 * @param {string|number} duration - Duration string (e.g., "15 minutes", "2 hours") or number (minutes)
 * @returns {string} - Formatted duration
 */
export const formatDuration = duration => {
  if (!duration) return '';

  // Handle numeric values (assume minutes)
  if (typeof duration === 'number') {
    if (duration < 60) {
      return `${duration} min`;
    } else {
      const hours = Math.floor(duration / 60);
      const minutes = duration % 60;
      return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
    }
  }

  // Handle string values
  if (typeof duration === 'string') {
    return duration
      .toLowerCase()
      .replace('minutes', 'min')
      .replace('minute', 'min')
      .replace('hours', 'h')
      .replace('hour', 'h');
  }

  return duration;
};

/**
 * Get access level display name (uses unified access levels)
 * @param {string} level - Access level ('basic', 'intermediate', 'advanced')
 * @returns {string} - Display name
 */
export const getAccessLevelDisplay = level => {
  const levels = {
    [ACCESS_LEVELS.GUEST]: 'Guest',
    [ACCESS_LEVELS.REGISTERED]: 'Registered',
    [ACCESS_LEVELS.PREMIUM]: 'Premium',
  };
  return levels[level] || level;
};

/**
 * Get access level color for UI (uses unified access levels)
 * @param {string} level - Access level
 * @returns {string} - CSS color class
 */
export const getAccessLevelColor = level => {
  const colors = {
    [ACCESS_LEVELS.GUEST]: 'text-gray-600',
    [ACCESS_LEVELS.REGISTERED]: 'text-blue-600',
    [ACCESS_LEVELS.PREMIUM]: 'text-purple-600',
  };
  return colors[level] || 'text-gray-600';
};

/**
 * Format price for display
 * @param {number|string} price - Price value
 * @param {string} currency - Currency symbol (default: ₹)
 * @returns {string} - Formatted price
 */
export const formatPrice = (price, currency = '₹') => {
  // Handle explicit zero as a valid price (₹0.00)
  if (price === 0) return `${currency}0`;

  // Handle null, undefined, empty string as "Free"
  if (price == null || price === '') return 'Free';

  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  if (isNaN(numPrice)) return 'Free';

  return `${currency}${numPrice.toLocaleString()}`;
};

// Import unified validation utilities
import {
  validateLessonData as unifiedValidateLessonData,
  ACCESS_LEVELS,
  getUserAccessLevel as unifiedGetUserAccessLevel,
  canUserAccessContent,
  normalizeUserRole,
} from '../../utils/validation';

/**
 * Validate lesson form data (uses unified validation logic)
 * @param {Object} lessonData - Lesson form data
 * @returns {Array} - Array of validation errors (for backward compatibility)
 */
export const validateLessonData = lessonData => {
  const { isValid, errors } = unifiedValidateLessonData(lessonData);

  // Convert errors object to array for backward compatibility
  const errorArray = [];
  Object.values(errors).forEach(error => {
    if (error) errorArray.push(error);
  });

  return errorArray;
};

/**
 * Check if HTML content is from restricted access (contains specific patterns)
 * This helps identify if content is a restriction message from backend utils
 * Uses case-insensitive matching for better detection
 * @param {string} content - HTML content string
 * @returns {boolean} - True if content appears to be a restriction message
 */
export const isRestrictedContent = content => {
  if (!content || typeof content !== 'string') return false;

  // Normalize content to lowercase for case-insensitive matching
  const lowerContent = content.toLowerCase();

  // Check for patterns that indicate restriction messages from backend utils
  const restrictionPatterns = [
    'premium-content-notice',
    'preview-content',
    'requires a premium subscription',
    'register for free to access',
  ];

  return restrictionPatterns.some(pattern => lowerContent.includes(pattern));
};

/**
 * Usage examples:
 *
 * 1. Import multiple components:
 *    import { Button, Card, Avatar } from '../components/common';
 *
 * 2. Import a specific component:
 *    import { Button } from '../components/common';
 *
 * 3. Import with alias:
 *    import { Button as CustomButton } from '../components/common';
 *
 * 4. Import utility functions:
 *    import { formatDuration, validateLessonData } from '../components/common';
 */

/**
 * Default export for backward compatibility
 * Includes all components and utility functions in alphabetical order
 */
export default {
  // Core components (alphabetically ordered)
  Accordion,
  Alert,
  AnimatedElement,
  Avatar,
  Badge,
  BookmarksList,
  Button,
  Card,
  CardSkeleton,
  Certificate,
  Container,
  ContentAccessController,
  Dropdown,
  ErrorBoundary,
  FormInput,
  LoadingScreen,
  Modal,
  Pagination,
  ProfileBadge,
  ProgressBar,
  Rating,
  ResourceCard,
  ResumeButton,
  SearchBar,
  Sidebar,
  Skeleton,
  Spinner,
  StepIndicator,
  Tabs,
  TagInput,
  TextSkeleton,
  Tooltip,

  // Utility functions
  formatDuration,
  formatPrice,
  getAccessLevelColor,
  getAccessLevelDisplay,
  getInitials,
  isRestrictedContent,
  validateLessonData,
};
