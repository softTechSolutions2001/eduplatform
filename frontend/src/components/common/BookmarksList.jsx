/**
 * File: src/components/common/BookmarksList.jsx
 * Version: 1.0.0
 * Date: 2025-05-14 16:34:40
 * Author: cadsanthanam
 *
 * Component to display and manage bookmarked lessons
 * Production-ready with error handling and optimizations
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, formatDistanceToNow } from 'date-fns';

// Check localStorage availability
const isLocalStorageAvailable =
  typeof window !== 'undefined' &&
  window.localStorage &&
  (() => {
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      return true;
    } catch (e) {
      return false;
    }
  })();

// Safe localStorage operations
const safeGetLocalStorage = (key, defaultValue = null) => {
  if (!isLocalStorageAvailable) return defaultValue;
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : defaultValue;
  } catch (e) {
    console.error(`Error reading ${key} from localStorage:`, e);
    return defaultValue;
  }
};

const safeSetLocalStorage = (key, value) => {
  if (!isLocalStorageAvailable) return false;
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    console.error(`Error writing to localStorage:`, e);
    return false;
  }
};

const BookmarksList = ({
  courseSlug,
  onNavigate,
  className = '',
  emptyMessage = 'No bookmarks yet',
}) => {
  const [bookmarks, setBookmarks] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const isMountedRef = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Load bookmarks from localStorage
  useEffect(() => {
    if (!courseSlug) {
      setLoading(false);
      return;
    }

    const loadBookmarks = () => {
      try {
        setLoading(true);
        const bookmarksKey = `course_bookmarks_${courseSlug}`;
        const savedBookmarks = safeGetLocalStorage(bookmarksKey, []);

        // Validate bookmarks
        const validBookmarks = Array.isArray(savedBookmarks)
          ? savedBookmarks.filter(
              bookmark =>
                bookmark &&
                bookmark.lessonId &&
                bookmark.moduleId &&
                bookmark.timestamp
            )
          : [];

        // Sort bookmarks by most recent first
        validBookmarks.sort((a, b) => {
          try {
            return (
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
            );
          } catch (e) {
            return 0; // Fallback if timestamp is invalid
          }
        });

        if (isMountedRef.current) {
          setBookmarks(validBookmarks);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error loading bookmarks:', error);
        if (isMountedRef.current) {
          setError(error);
          setBookmarks([]);
          setLoading(false);
        }
      }
    };

    loadBookmarks();

    // Add listener to update bookmarks if they change in another component
    const handleStorageChange = e => {
      if (e.key === `course_bookmarks_${courseSlug}`) {
        loadBookmarks();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [courseSlug]);

  // Handle navigation to a bookmarked lesson
  const navigateToBookmark = bookmark => {
    if (!bookmark || !bookmark.lessonId || !bookmark.moduleId) {
      console.error('Invalid bookmark data:', bookmark);
      return;
    }

    navigate(
      `/courses/${courseSlug}/content/${bookmark.moduleId}/${bookmark.lessonId}`
    );
    if (onNavigate) onNavigate(bookmark);
  };

  // Remove a bookmark
  const removeBookmark = (bookmark, e) => {
    e.stopPropagation(); // Prevent navigation
    e.preventDefault();

    if (!bookmark || !bookmark.lessonId) {
      console.error('Invalid bookmark data for removal:', bookmark);
      return;
    }

    const bookmarksKey = `course_bookmarks_${courseSlug}`;
    try {
      const savedBookmarks = safeGetLocalStorage(bookmarksKey, []);
      const updatedBookmarks = Array.isArray(savedBookmarks)
        ? savedBookmarks.filter(b => b.lessonId !== bookmark.lessonId)
        : [];

      safeSetLocalStorage(bookmarksKey, updatedBookmarks);
      setBookmarks(updatedBookmarks);

      // Notify other components
      const event = new Event('storage');
      event.key = bookmarksKey;
      window.dispatchEvent(event);
    } catch (error) {
      console.error('Error removing bookmark:', error);
    }
  };

  // Format the bookmark timestamp
  const formatTimestamp = timestamp => {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return 'unknown time';
      }
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (e) {
      console.error('Error formatting timestamp:', e);
      return 'unknown time';
    }
  };

  if (loading) {
    return (
      <div className={`py-4 ${className}`}>
        <div className="flex justify-center">
          <div className="animate-pulse space-y-2 w-full">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-center py-4 text-red-500 ${className}`}>
        <p>Error loading bookmarks</p>
      </div>
    );
  }

  if (bookmarks.length === 0) {
    return (
      <div className={`text-center py-6 text-gray-500 ${className}`}>
        <p>{emptyMessage}</p>
        <p className="text-sm mt-1">
          Bookmark lessons to quickly access them later
        </p>
      </div>
    );
  }

  return (
    <div className={`divide-y divide-gray-200 ${className}`}>
      {bookmarks.map((bookmark, index) => (
        <div
          key={`${bookmark.lessonId}_${index}`}
          onClick={() => navigateToBookmark(bookmark)}
          className="flex items-center justify-between py-3 px-2 hover:bg-gray-50 cursor-pointer"
        >
          <div className="flex-1">
            <h4 className="text-sm font-medium text-gray-900">
              {bookmark.title || `Lesson ${bookmark.lessonId}`}
            </h4>
            <p className="mt-1 text-xs text-gray-500">
              Bookmarked {formatTimestamp(bookmark.timestamp)}
            </p>
          </div>
          <button
            onClick={e => removeBookmark(bookmark, e)}
            className="ml-2 p-1 text-gray-400 hover:text-gray-600 focus:outline-none"
            title="Remove bookmark"
            aria-label="Remove bookmark"
          >
            <svg
              className="h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
};

export default BookmarksList;
