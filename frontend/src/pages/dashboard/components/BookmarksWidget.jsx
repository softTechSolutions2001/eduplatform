/**
 * File: src/pages/dashboard/components/BookmarksWidget.jsx
 * Version: 1.0.0
 * Date: 2025-05-14 16:34:40
 * Author: cadsanthanam
 *
 * Dashboard widget for displaying bookmarked lessons
 * Simple component to show on the student dashboard
 */

import React, { useState, useEffect } from 'react';
import { BookmarksList } from '../../../components/common';
import { useNavigate } from 'react-router-dom';

const BookmarksWidget = ({ courseSlug, className = '' }) => {
  const [showAll, setShowAll] = useState(false);
  const navigate = useNavigate();

  if (!courseSlug) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow overflow-hidden ${className}`}>
      <div className="border-b border-gray-200 px-4 py-4 sm:px-6">
        <h3 className="text-lg font-medium text-gray-900">
          Bookmarked Lessons
        </h3>
      </div>
      <div className="px-4 py-2 sm:p-6">
        <BookmarksList
          courseSlug={courseSlug}
          onNavigate={() => {}}
          emptyMessage="No bookmarks for this course"
        />

        {!showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="mt-4 text-sm text-primary-600 hover:text-primary-800 font-medium"
          >
            View all bookmarks
          </button>
        )}
      </div>
    </div>
  );
};

export default BookmarksWidget;
