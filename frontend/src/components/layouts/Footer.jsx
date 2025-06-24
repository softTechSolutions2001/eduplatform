/**
 * File: C:\Users\Santhanam\OneDrive\Personal\Full stack web development\eduplatform\frontend\src\components\layouts\Footer.jsx
 * Purpose: Footer component for the educational platform
 *
 * This component:
 * 1. Displays copyright information and company details
 * 2. Provides navigation links to important pages
 * 3. Shows social media links and contact information
 * 4. Includes newsletter subscription
 *
 * Fixed Layout Issues:
 * - Added proper width classes to ensure full-width display
 * - Adjusted container padding for consistent spacing
 * - Removed any classes that would cause width restrictions
 *
 * Variables to modify:
 * - FOOTER_LINKS: Update footer navigation links as needed
 * - SOCIAL_LINKS: Update social media links as needed
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27 11:04:16
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// Footer navigation links - customize as needed
const FOOTER_LINKS = [
  {
    title: 'Platform',
    links: [
      { name: 'Courses', path: '/courses' },
      { name: 'Pricing', path: '/pricing' },
      { name: 'Teachers', path: '/teachers' },
      { name: 'Enterprise', path: '/enterprise' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { name: 'Blog', path: '/blog' },
      { name: 'Documentation', path: '/docs' },
      { name: 'Help Center', path: '/help' },
      { name: 'Learning Paths', path: '/paths' },
    ],
  },
  {
    title: 'Company',
    links: [
      { name: 'About Us', path: '/about' },
      { name: 'Contact', path: '/contact' },
      { name: 'Careers', path: '/careers' },
      { name: 'Terms of Service', path: '/terms' },
      { name: 'Privacy Policy', path: '/privacy' },
    ],
  },
];

// Social media links - customize as needed
const SOCIAL_LINKS = [
  {
    name: 'Twitter',
    path: 'https://twitter.com/youraccount',
    icon: (
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
      </svg>
    ),
  },
  {
    name: 'GitHub',
    path: 'https://github.com/youraccount',
    icon: (
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
        <path
          fillRule="evenodd"
          d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  {
    name: 'LinkedIn',
    path: 'https://linkedin.com/in/youraccount',
    icon: (
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
      </svg>
    ),
  },
  {
    name: 'YouTube',
    path: 'https://youtube.com/youraccount',
    icon: (
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
  },
];

const Footer = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  // Handle newsletter subscription
  const handleSubscribe = e => {
    e.preventDefault();
    // Normally would send to API, for now just fake success
    if (email) {
      setSubscribed(true);
      setEmail('');

      // Reset after 3 seconds
      setTimeout(() => {
        setSubscribed(false);
      }, 3000);
    }
  };

  return (
    <footer className="bg-gray-800 text-white py-12 w-full">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Logo and Company Info */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center mb-4">
              <div className="h-10 w-10 bg-white rounded-full flex items-center justify-center text-primary-600 font-bold mr-2">
                ST
              </div>
              <div className="font-semibold text-xl text-white">
                <span>SoftTech</span>
                <span className="block -mt-1">Solutions</span>
              </div>
            </Link>
            <p className="text-gray-300 mb-4">
              Empowering learners worldwide through accessible, high-quality
              education and innovative learning experiences.
            </p>
            <div className="flex space-x-4">
              {SOCIAL_LINKS.map(social => (
                <a
                  key={social.name}
                  href={social.path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors"
                  aria-label={social.name}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Footer Links */}
          {FOOTER_LINKS.map(section => (
            <div key={section.title}>
              <h3 className="font-semibold text-lg mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map(link => (
                  <li key={link.path}>
                    <Link
                      to={link.path}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Newsletter */}
          <div>
            <h3 className="font-semibold text-lg mb-4">
              Subscribe to our Newsletter
            </h3>
            <p className="text-gray-400 mb-4">
              Get the latest updates and educational content delivered to your
              inbox.
            </p>
            <form onSubmit={handleSubscribe} className="mt-2">
              <div className="flex max-w-xs">
                <input
                  type="email"
                  placeholder="Your email address"
                  className="bg-gray-700 text-white px-4 py-2 rounded-l focus:outline-none focus:ring-2 focus:ring-primary-500 flex-grow"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
                <button
                  type="submit"
                  className="bg-primary-600 hover:bg-primary-700 px-4 py-2 rounded-r"
                >
                  Subscribe
                </button>
              </div>
              {subscribed && (
                <p className="text-green-400 text-sm mt-2">
                  Thanks for subscribing!
                </p>
              )}
            </form>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-700 mt-12 pt-6 text-center text-gray-400 text-sm">
          <p>
            © {new Date().getFullYear()} SoftTech Solutions Educational
            Platform. All rights reserved.
          </p>
          <p className="mt-1">Designed and developed by Professor Santhanam</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
