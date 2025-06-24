/**
 * File: C:\Users\Santhanam\OneDrive\Personal\Full stack web development\eduplatform\frontend\src\components\layouts\Header.jsx
 * Purpose: Enhanced header component for the educational platform with sticky behavior
 *
 * This component:
 * 1. Provides navigation links to main sections of the platform
 * 2. Shows the website logo and branding
 * 3. Displays user authentication status and controls
 * 4. Includes search functionality for courses
 * 5. Features a sticky header that shrinks when scrolling
 *
 * Enhanced features:
 * - Header stays fixed at the top of the page while scrolling
 * - Header height reduces when scrolling down for a compact appearance
 * - Logo size adjusts during scrolling
 * - Smooth transitions when changing header size
 * - Full width display with proper container spacing
 *
 * Variables that can be modified:
 * - NAV_LINKS: Update navigation links as needed
 * - SCROLL_THRESHOLD: Pixel value where the header starts to shrink (default: 50)
 * - ANIMATION_DURATION: How fast the header shrinks/expands (default: 0.3s)
 * - COMPACT_HEADER_HEIGHT: Height of the header when scrolled (default: 60px)
 * - EXPANDED_HEADER_HEIGHT: Height of the header when at top (default: 80px)
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-05-22 12:15:00
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Configuration variables - modify these values to adjust header behavior
const SCROLL_THRESHOLD = 50; // How many pixels to scroll before shrinking header
const ANIMATION_DURATION = '0.3s'; // How quickly the header shrinks/expands
const COMPACT_HEADER_HEIGHT = '60px'; // Height of header when scrolled
const EXPANDED_HEADER_HEIGHT = '80px'; // Height of header when at top

// Navigation links - customize as needed
const NAV_LINKS = [
  { name: 'Home', path: '/' },
  { name: 'Explore', path: '/courses' },
  { name: 'Learn', path: '/learn' },
  { name: 'Practice', path: '/practice' },
  { name: 'Community', path: '/community' },
  { name: 'Resources', path: '/resources' },
];

const Header = () => {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  // New state for tracking scroll position
  const [scrolled, setScrolled] = useState(false);

  // Handle search submission
  const handleSearch = e => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/courses?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Effect to handle scroll events
  useEffect(() => {
    const handleScroll = () => {
      // Check if we've scrolled past the threshold
      const isScrolled = window.scrollY > SCROLL_THRESHOLD;

      // Only update state if it changed, to avoid unnecessary re-renders
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);

    // Check initial scroll position
    handleScroll();

    // Clean up event listener on component unmount
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrolled]); // Only re-run if scrolled state changes

  // Handle logout with confirmation
  const handleLogout = () => {
    if (window.confirm('Are you sure you want to sign out?')) {
      logout();
      setShowUserMenu(false);
      navigate('/');
    }
  };

  return (
    <header
      className={`bg-white shadow-md w-full fixed top-0 left-0 z-50 transition-all`}
      style={{
        height: scrolled ? COMPACT_HEADER_HEIGHT : EXPANDED_HEADER_HEIGHT,
        transitionDuration: ANIMATION_DURATION,
      }}
    >
      <div className="container mx-auto px-4 h-full">
        <div className="flex items-center justify-between h-full">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <div
              className={`bg-primary-600 rounded-full flex items-center justify-center text-white font-bold mr-2 transition-all`}
              style={{
                height: scrolled ? '36px' : '40px',
                width: scrolled ? '36px' : '40px',
                transitionDuration: ANIMATION_DURATION,
              }}
            >
              ST
            </div>
            <div
              className={`font-semibold transition-all`}
              style={{
                fontSize: scrolled ? '1rem' : '1.25rem',
                transitionDuration: ANIMATION_DURATION,
              }}
            >
              <span>SoftTech</span>
              <span className="block -mt-1">Solutions</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-6">
            {NAV_LINKS.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`text-gray-600 hover:text-primary-600 transition-all ${
                  window.location.pathname === link.path
                    ? 'text-primary-600 font-medium'
                    : ''
                }`}
                style={{
                  fontSize: scrolled ? '0.9rem' : '1rem',
                  transitionDuration: ANIMATION_DURATION,
                }}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Search and User Menu */}
          <div className="flex items-center space-x-4">
            {/* Search Box */}
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Search courses..."
                className={`bg-gray-100 rounded-full py-2 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all`}
                style={{
                  padding: scrolled
                    ? '0.5rem 1rem 0.5rem 2.5rem'
                    : '0.625rem 1rem 0.625rem 2.5rem',
                  width: scrolled ? '200px' : '256px', // Slightly smaller on scroll
                  transitionDuration: ANIMATION_DURATION,
                }}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <button
                type="submit"
                className="absolute left-3 text-gray-400"
                style={{
                  top: scrolled ? '0.5rem' : '0.625rem',
                  transitionDuration: ANIMATION_DURATION,
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </button>
            </form>

            {/* User Menu or Login/Register Links */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  className="flex items-center focus:outline-none"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  <div
                    className="bg-primary-200 rounded-full flex items-center justify-center text-primary-700 font-medium mr-2 transition-all"
                    style={{
                      height: scrolled ? '28px' : '32px',
                      width: scrolled ? '28px' : '32px',
                      transitionDuration: ANIMATION_DURATION,
                    }}
                  >
                    {currentUser?.first_name?.[0]?.toUpperCase() ||
                      currentUser?.username?.[0]?.toUpperCase() ||
                      'U'}
                  </div>
                  <span
                    className="text-gray-700 transition-all"
                    style={{
                      fontSize: scrolled ? '0.8rem' : '0.875rem',
                      transitionDuration: ANIMATION_DURATION,
                    }}
                  >
                    {currentUser?.first_name || currentUser?.username || 'User'}
                  </span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className={`h-4 w-4 ml-1 text-gray-500 transition-transform ${showUserMenu ? 'transform rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200">
                    <Link
                      to="/dashboard"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      My Profile
                    </Link>
                    <Link
                      to="/user/courses"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      My Courses
                    </Link>
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className={`text-gray-700 hover:text-primary-600 transition-all`}
                  style={{
                    fontSize: scrolled ? '0.8rem' : '0.875rem',
                    transitionDuration: ANIMATION_DURATION,
                  }}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-all"
                  style={{
                    padding: scrolled ? '0.375rem 0.875rem' : '0.5rem 1rem',
                    fontSize: scrolled ? '0.8rem' : '0.875rem',
                    transitionDuration: ANIMATION_DURATION,
                  }}
                >
                  Sign Up
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden flex items-center"
              onClick={() => setShowMobileMenu(!showMobileMenu)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {showMobileMenu && (
          <nav className="md:hidden pt-4 pb-2 border-t mt-4">
            <div className="flex flex-col space-y-3">
              {NAV_LINKS.map(link => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-gray-600 hover:text-primary-600 ${
                    window.location.pathname === link.path
                      ? 'text-primary-600 font-medium'
                      : ''
                  }`}
                  onClick={() => setShowMobileMenu(false)}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
