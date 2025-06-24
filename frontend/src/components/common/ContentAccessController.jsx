/**
 * File: frontend/src/components/common/ContentAccessController.jsx
 * Date: 2025-05-30 16:49:05
 * Modified: Updated access level terminology for consistency
 * Purpose: Control content display based on user access level
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import DOMPurify from 'dompurify';
import { ACCESS_LEVELS, canUserAccessContent } from '../../utils/validation';

// Default message shown when content is locked
const DEFAULT_UPGRADE_MESSAGE =
  'Upgrade your account to access this premium content';

/**
 * Controls access to content based on the user's access level.
 * Handles content visibility according to subscription tier.
 *
 * NOTE: The backend serializer (LessonSerializer) already handles access control
 * and sends appropriate content in the 'content' field based on user access level.
 * This component mainly handles the UI presentation of that content.
 */
export default function ContentAccessController({
  requiredLevel = ACCESS_LEVELS.GUEST,
  isLoggedIn,
  userAccessLevel,
  guestContent,
  content,
  upgradeMessage,
  children,
}) {
  // Use auth context values or provided props
  const auth = useAuth();
  const effectiveIsLoggedIn = isLoggedIn ?? auth?.isAuthenticated ?? false;

  // CRITICAL FIX: Added special case for authenticated users - they get at least REGISTERED access
  const effectiveUserAccessLevel =
    userAccessLevel ??
    auth?.userAccessLevel ??
    (auth?.getAccessLevel?.() ||
      (effectiveIsLoggedIn ? ACCESS_LEVELS.REGISTERED : ACCESS_LEVELS.GUEST));

  // Normalize required level (default to GUEST if invalid)
  const normalizedRequiredLevel = Object.values(ACCESS_LEVELS).includes(
    requiredLevel
  )
    ? requiredLevel
    : ACCESS_LEVELS.GUEST;

  // Use unified access control logic
  const hasAccess = canUserAccessContent(
    effectiveUserAccessLevel,
    normalizedRequiredLevel
  );

  // For development debugging only
  if (process.env.NODE_ENV === 'development') {
    console.debug('ContentAccessController:', {
      requiredLevel: normalizedRequiredLevel,
      isLoggedIn: effectiveIsLoggedIn,
      userAccessLevel: effectiveUserAccessLevel,
      hasAccess,
      contentLength: content?.length || 0,
      hasGuestContent: !!guestContent,
    });
  }

  // SIMPLIFIED LOGIC: Since backend already handles access control,
  // authenticated users should always see the content directly
  if (effectiveIsLoggedIn && content) {
    return (
      children ?? (
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}
        />
      )
    );
  }

  // If user has access, show the content
  if (hasAccess) {
    return (
      children ??
      (content && (
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}
        />
      ))
    );
  }
  // User doesn't have access - show appropriate message
  if (!effectiveIsLoggedIn) {
    // Not logged in users see login prompt
    const sanitizedGuestContent =
      typeof guestContent === 'string' ? (
        <div
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(guestContent) }}
        />
      ) : (
        guestContent
      );

    return (
      sanitizedGuestContent || (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 my-4">
          <h3 className="font-semibold text-primary-800 mb-1">
            Login Required
          </h3>
          <p className="text-primary-700 mb-3">
            Please sign in to access this content.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center px-3 py-1.5 border border-primary-300 text-sm font-medium rounded-md text-primary-800 bg-primary-100 hover:bg-primary-200"
          >
            Sign In
          </Link>
        </div>
      )
    );
  } else {
    // Logged in users need upgrade
    const sanitizedGuestContent =
      typeof guestContent === 'string' ? (
        <div
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(guestContent) }}
        />
      ) : (
        guestContent
      );

    return (
      sanitizedGuestContent || (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 my-4">
          <h3 className="font-semibold text-amber-800 mb-1">Premium Content</h3>
          <p className="text-amber-700 mb-3">
            {upgradeMessage || DEFAULT_UPGRADE_MESSAGE}
          </p>
          <Link
            to="/pricing"
            className="inline-flex items-center px-3 py-1.5 border border-amber-300 text-sm font-medium rounded-md text-amber-800 bg-amber-100 hover:bg-amber-200"
          >
            Upgrade Subscription
          </Link>
        </div>
      )
    );
  }
}

ContentAccessController.propTypes = {
  requiredLevel: PropTypes.oneOf(Object.values(ACCESS_LEVELS)),
  isLoggedIn: PropTypes.bool,
  userAccessLevel: PropTypes.oneOf(Object.values(ACCESS_LEVELS)),
  guestContent: PropTypes.node,
  content: PropTypes.string,
  upgradeMessage: PropTypes.string,
  children: PropTypes.node,
};
