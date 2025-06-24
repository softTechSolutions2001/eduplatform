/**
 * File: frontend/src/pages/subscription/SubscriptionSuccessPage.jsx
 * Purpose: Confirmation page after successful subscription upgrade
 *
 * This component:
 * 1. Shows a success message after subscription upgrade
 * 2. Displays subscription details and next steps
 * 3. Provides links to start exploring premium content
 *
 * Variables to modify:
 * - NEXT_STEPS: Customize suggestions for users based on their subscription
 *
 * Backend Connection Points:
 * None - This is a simple confirmation page
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27
 */

import React, { useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { MainLayout } from '../../components/layouts';
import { Button } from '../../components/common';
import { useAuth } from '../../contexts/AuthContext';

// Customizable next steps for new subscribers
const NEXT_STEPS = [
  {
    title: 'Browse premium courses',
    description:
      'Explore our library of advanced courses with your new subscription.',
    icon: (
      <svg
        className="h-6 w-6 text-primary-600"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
    ),
    link: '/courses',
  },
  {
    title: 'Update your profile',
    description:
      'Complete your learning profile to get personalized recommendations.',
    icon: (
      <svg
        className="h-6 w-6 text-primary-600"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    ),
    link: '/profile',
  },
  {
    title: 'Join the community',
    description: 'Connect with other learners and instructors in our forums.',
    icon: (
      <svg
        className="h-6 w-6 text-primary-600"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
        />
      </svg>
    ),
    link: '/forum',
  },
];

const SubscriptionSuccessPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  // Get data from location state
  const { planName, planPrice, from } = location.state || {};

  // If no plan data, redirect to dashboard
  useEffect(() => {
    if (!planName) {
      navigate('/dashboard');
    }
  }, [planName, navigate]);

  return (
    <MainLayout>
      <div className="bg-gray-50 py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
              <svg
                className="h-8 w-8 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>

            <h1 className="mt-4 text-3xl font-bold text-gray-900">
              Subscription Successful!
            </h1>

            <p className="mt-2 text-lg text-gray-600">
              Thank you for subscribing to the {planName}
            </p>

            <div className="mt-6 bg-white shadow-md rounded-lg p-6 text-left">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Subscription Details
              </h2>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Plan</span>
                  <span className="font-medium">{planName}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Amount</span>
                  <span className="font-medium">${planPrice}/month</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Subscriber</span>
                  <span className="font-medium">
                    {currentUser?.first_name} {currentUser?.last_name}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Status</span>
                  <span className="font-medium text-green-600">Active</span>
                </div>
              </div>
            </div>

            {/* Next steps */}
            <div className="mt-8">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                What's Next?
              </h2>

              <div className="grid gap-6 md:grid-cols-3">
                {NEXT_STEPS.map((step, index) => (
                  <div
                    key={index}
                    className="bg-white shadow-md rounded-lg p-6 text-left"
                  >
                    <div className="mb-4">{step.icon}</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4">
                      {step.description}
                    </p>
                    <Link
                      to={step.link}
                      className="text-primary-600 hover:text-primary-800 font-medium text-sm inline-flex items-center"
                    >
                      Get started
                      <svg
                        className="ml-1 h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </Link>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <Button
                color="primary"
                onClick={() => navigate(from || '/dashboard')}
              >
                {from && !from.startsWith('/dashboard')
                  ? 'Continue Where You Left Off'
                  : 'Go to Dashboard'}
              </Button>

              <Button color="secondary" onClick={() => navigate('/courses')}>
                Browse Courses
              </Button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default SubscriptionSuccessPage;
