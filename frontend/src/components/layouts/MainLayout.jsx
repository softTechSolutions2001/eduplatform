/**
 * File: frontend/src/components/layouts/MainLayout.jsx
 * Purpose: Main layout wrapper for consistent page structure with fixed header support
 * Date: 2025-07-24 17:13:10
 *
 * This component:
 * 1. Provides a consistent layout structure for pages
 * 2. Includes the Header and Footer components
 * 3. Wraps the main content in appropriate containers
 * 4. Adds proper padding to account for fixed header
 * 5. Ensures full width display with proper spacing
 *
 * Enhanced features:
 * - Added padding-top to main content to prevent it from being hidden under fixed header
 * - Uses flex layout for proper content distribution
 * - Only includes the current date/time banner once
 * - Ensures proper spacing between all elements
 * - Displays user's local time instead of UTC
 *
 * Variables that can be modified:
 * - DATE_TIME_FORMAT: Change how date/time are displayed
 * - HEADER_HEIGHT_EXPANDED: Must match the expanded header height in Header.jsx
 * - DATE_BANNER_HEIGHT: Height of the date/time banner (default: 28px)
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27 11:45:00
 */

import React, { useState, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Configuration variables - modify as needed
const DATE_TIME_FORMAT = {
  dateStyle: 'medium',
  timeStyle: 'medium',
  hour12: true,
};

// These values should match those in Header.jsx
const HEADER_HEIGHT_EXPANDED = '80px'; // Match the EXPANDED_HEADER_HEIGHT in Header.jsx
const DATE_BANNER_HEIGHT = '28px'; // Height of the date/time banner

const MainLayout = ({ children }) => {
  const [currentDateTime, setCurrentDateTime] = useState(new Date());

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(timer);
  }, []);

  // Get formatted date and time for the banner
  const getFormattedDateTime = () => {
    try {
      return currentDateTime.toLocaleString('en-US', DATE_TIME_FORMAT);
    } catch (error) {
      // Fallback formatting if toLocaleString with options isn't supported
      return currentDateTime.toString();
    }
  };

  // Get authentication status to display correct user info
  const { isAuthenticated, currentUser } = useAuth();

  // Calculate total header height (date banner + header)
  const totalHeaderOffset = `calc(${HEADER_HEIGHT_EXPANDED} + ${DATE_BANNER_HEIGHT})`;

  return (
    <div className="flex flex-col min-h-screen w-full">
      {/* Current Date/Time Banner - Fixed at the top */}
      <div
        className="bg-gray-900 text-gray-300 text-sm py-1 px-4 w-full fixed top-0 left-0 z-50"
        style={{ height: DATE_BANNER_HEIGHT }}
      >
        <div className="container mx-auto flex justify-between">
          <span>Current Date and Time: {getFormattedDateTime()}</span>
          <span>
            {isAuthenticated ? (
              `User: ${currentUser?.first_name || currentUser?.username || 'User'}`
            ) : (
              <div>
                <Link
                  to="/login"
                  className="text-primary-300 hover:text-white mr-3"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="text-primary-300 hover:text-white"
                >
                  Register
                </Link>
              </div>
            )}
          </span>
        </div>
      </div>

      {/* Add offset for date/time banner */}
      <div style={{ height: DATE_BANNER_HEIGHT }}></div>

      {/* Header - Already fixed in its component */}
      <Header />

      {/* Main Content - Add padding top to account for fixed header */}
      <main
        className="flex-grow w-full"
        style={{ paddingTop: HEADER_HEIGHT_EXPANDED }}
      >
        {children}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default MainLayout;
