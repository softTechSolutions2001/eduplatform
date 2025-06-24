/**
 * File: frontend/src/pages/subscription/PricingPage.jsx
 * Purpose: Display subscription plans and allow users to upgrade
 *
 * This component:
 * 1. Shows available subscription tiers (free, basic, premium)
 * 2. Highlights the user's current plan
 * 3. Allows users to upgrade or downgrade their subscription
 * 4. Provides clear information about features in each tier
 *
 * Variables to modify:
 * - SUBSCRIPTION_PLANS: Update plan details, features and prices
 * - PLAN_COLORS: Change the color scheme for different plans
 *
 * Backend Connection Points:
 * - GET /users/subscription/current/ - Get current subscription
 * - POST /users/subscription/upgrade/ - Upgrade subscription
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MainLayout } from '../../components/layouts';
import { Button, Card, Alert, Badge } from '../../components/common';
import { useAuth } from '../../contexts/AuthContext';
import { subscriptionService } from '../../services/api';

// Plan color schemes - can be customized
const PLAN_COLORS = {
  free: {
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    button: 'secondary',
    badge: 'gray',
  },
  basic: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    button: 'primary',
    badge: 'blue',
  },
  premium: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    button: 'purple',
    badge: 'purple',
  },
};

// Define subscription plans - customize as needed
const SUBSCRIPTION_PLANS = [
  {
    id: 'free',
    name: 'Free Account',
    price: 0,
    period: '',
    description: 'Basic access to course content',
    features: [
      'Access to basic course previews',
      'Browse all available courses',
      'Read public forum discussions',
      'Create and manage a learning profile',
      'Limited access to resources',
    ],
    buttonText: 'Current Plan',
    recommended: false,
  },
  {
    id: 'basic',
    name: 'Basic',
    price: 9.99,
    period: 'monthly',
    description: 'Full access to registered user content',
    features: [
      'Everything in Free, plus:',
      'Complete access to all regular courses',
      'Take course assessments',
      'Participate in forum discussions',
      'Track your learning progress',
      'Save course notes',
      'Download basic resources',
    ],
    buttonText: 'Subscribe',
    recommended: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 19.99,
    period: 'monthly',
    description: 'Complete access with certificates',
    features: [
      'Everything in Basic, plus:',
      'Course completion certificates',
      'Advanced course materials',
      'Premium downloadable resources',
      'Priority support',
      'Ad-free experience',
      'Early access to new courses',
    ],
    buttonText: 'Subscribe',
    recommended: false,
  },
];

const PricingPage = () => {
  const { currentUser, isAuthenticated, subscription, upgradeSubscription } =
    useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Get redirect path if user came from a premium content page
  const from = location.state?.from || '/dashboard';

  // Handle subscription changes
  const handleSubscribe = async planId => {
    // If not logged in, redirect to login first
    if (!isAuthenticated()) {
      navigate('/login', { state: { from: '/pricing', plan: planId } });
      return;
    }

    // If selecting current plan, do nothing
    if (subscription?.tier === planId) {
      return;
    }

    // For free tier, downgrade immediately
    if (planId === 'free') {
      try {
        setLoading(true);
        await subscriptionService.downgradeSubscription('free');
        setSuccess('Your subscription has been updated to the free plan.');
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } catch (err) {
        setError('Failed to update subscription. Please try again.');
        console.error('Subscription error:', err);
      } finally {
        setLoading(false);
      }
      return;
    }

    // For paid plans, navigate to checkout
    navigate(`/checkout/${planId}`, { state: { from } });
  };

  return (
    <MainLayout>
      <div className="bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl lg:text-5xl">
              Choose Your Learning Plan
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              Select the plan that best fits your educational needs
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div className="max-w-md mx-auto mt-6 bg-red-50 p-4 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Success message */}
          {success && (
            <div className="max-w-md mx-auto mt-6 bg-green-50 p-4 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-green-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    Success
                  </h3>
                  <div className="mt-2 text-sm text-green-700">
                    <p>{success}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Subscription plans */}
          <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-3">
            {SUBSCRIPTION_PLANS.map(plan => {
              const isCurrentPlan = subscription?.tier === plan.id;
              const colors = PLAN_COLORS[plan.id];

              return (
                <Card
                  key={plan.id}
                  className={`p-6 flex flex-col ${
                    plan.recommended
                      ? 'border-2 border-primary-500 shadow-xl'
                      : `border ${colors.border} shadow-sm`
                  } ${colors.bg}`}
                >
                  {/* Recommended badge */}
                  {plan.recommended && (
                    <div className="absolute top-0 right-0 px-3 py-1 bg-primary-500 text-white text-sm font-semibold rounded-bl">
                      Recommended
                    </div>
                  )}

                  {/* Current plan badge */}
                  {isCurrentPlan && (
                    <Badge variant={colors.badge} className="self-start mb-2">
                      Current Plan
                    </Badge>
                  )}

                  {/* Plan name */}
                  <h2 className="text-2xl font-semibold text-gray-900">
                    {plan.name}
                  </h2>

                  {/* Plan price */}
                  <div className="mt-4 flex items-baseline text-gray-900">
                    <span className="text-4xl font-extrabold tracking-tight">
                      {plan.price === 0 ? 'Free' : `$${plan.price}`}
                    </span>
                    {plan.period && (
                      <span className="ml-1 text-xl font-semibold">
                        /{plan.period}
                      </span>
                    )}
                  </div>

                  {/* Plan description */}
                  <p className="mt-5 text-lg text-gray-500">
                    {plan.description}
                  </p>

                  {/* Plan features */}
                  <ul className="mt-6 space-y-4 flex-1">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg
                            className="h-6 w-6 text-green-500"
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
                        <p className="ml-3 text-base text-gray-700">
                          {feature}
                        </p>
                      </li>
                    ))}
                  </ul>

                  {/* Action button */}
                  <Button
                    color={
                      isCurrentPlan
                        ? 'secondary'
                        : plan.recommended
                          ? 'primary'
                          : colors.button
                    }
                    fullWidth
                    className="mt-8"
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={loading || isCurrentPlan}
                  >
                    {loading
                      ? 'Processing...'
                      : isCurrentPlan
                        ? 'Current Plan'
                        : plan.buttonText}
                  </Button>
                </Card>
              );
            })}
          </div>

          {/* Additional information */}
          <div className="mt-10 text-center">
            <p className="text-base text-gray-600">
              All plans include access to our community forum and basic
              resources.
              <br />
              Need help choosing?{' '}
              <a href="/contact" className="text-primary-600 hover:underline">
                Contact us
              </a>{' '}
              for guidance.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default PricingPage;
