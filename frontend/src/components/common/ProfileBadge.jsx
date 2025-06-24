// Created on 2025-07-25
// Basic ProfileBadge component for the EduPlatform

import React from 'react';

/**
 * A badge component to display user profile information
 * @param {Object} props
 * @param {Object} props.user - User object with profile information
 * @param {String} props.size - Size of the badge (small, medium, large)
 * @param {String} props.className - Additional classes for styling
 */
const ProfileBadge = ({ user, size = 'medium', className = '' }) => {
  if (!user) return null;

  const { firstName, lastName, email, role, avatarUrl } = user;
  const initials = getInitials(firstName, lastName);

  // Determine size classes
  const sizeClasses = {
    small: 'h-8 w-8 text-xs',
    medium: 'h-10 w-10 text-sm',
    large: 'h-12 w-12 text-base',
  };

  // Determine role color
  const roleColors = {
    student: 'bg-blue-100 text-blue-800',
    instructor: 'bg-amber-100 text-amber-800',
    admin: 'bg-purple-100 text-purple-800',
    default: 'bg-gray-100 text-gray-800',
  };

  const roleColor = roleColors[role] || roleColors.default;
  const avatarSizeClass = sizeClasses[size] || sizeClasses.medium;

  return (
    <div className={`flex items-center ${className}`}>
      {/* Avatar/Initials */}
      <div className="flex-shrink-0">
        {avatarUrl ? (
          <img
            src={avatarUrl}
            alt={`${firstName} ${lastName}`}
            className={`${avatarSizeClass} rounded-full object-cover`}
          />
        ) : (
          <div
            className={`${avatarSizeClass} rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-medium`}
          >
            {initials}
          </div>
        )}
      </div>

      {/* User info */}
      <div className="ml-3">
        <div className="text-sm font-medium text-gray-900">
          {firstName} {lastName}
        </div>
        <div className="text-xs text-gray-500">{email}</div>
        {role && (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${roleColor} mt-1`}
          >
            {role.charAt(0).toUpperCase() + role.slice(1)}
          </span>
        )}
      </div>
    </div>
  );
};

/**
 * Helper function to get initials from name
 */
const getInitials = (firstName = '', lastName = '') => {
  const first = firstName.charAt(0).toUpperCase();
  const last = lastName.charAt(0).toUpperCase();

  return first + (last || '');
};

export default ProfileBadge;
