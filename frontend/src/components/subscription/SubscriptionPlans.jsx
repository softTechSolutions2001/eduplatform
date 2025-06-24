/**
 * File: frontend/src/components/subscription/SubscriptionPlans.jsx
 * Version: 2.1.0
 * Date: 2025-05-30 17:44:33
 * Author: sujibeautysalon
 * Last Modified: 2025-05-30 17:44:33 UTC
 *
 * Purpose: Display subscription plans and handle subscription purchase
 *
 * This component:
 * 1. Shows available subscription tiers (guest, registered, premium)
 * 2. Highlights features of different subscription levels
 * 3. Handles subscription purchase flow
 * 4. Shows current subscription status for logged-in users
 *
 * Usage:
 * <SubscriptionPlans
 *   currentPlan="guest"
 *   onSelectPlan={(plan) => handlePlanSelection(plan)}
 * />
 *
 * Variables to modify:
 * - SUBSCRIPTION_PLANS: Update plan details, features and pricing
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../common/Button';

// Subscription plan details - modify as needed
const SUBSCRIPTION_PLANS = [
  {
    id: 'guest',
    name: 'Guest',
    price: 0,
    billingPeriod: '',
    description: 'Basic access to course content',
    features: [
      'Access to guest course materials',
      'Community forum participation',
      'Course previews',
      'Limited assessments',
    ],
    recommended: false,
    buttonText: 'Current Plan',
    accessLevel: 'guest',
  },
  {
    id: 'registered',
    name: 'Registered',
    price: 9.99,
    billingPeriod: 'monthly',
    description: 'Full access to registered user content',
    features: [
      'All Guest features',
      'Full course access',
      'Practice exercises',
      'Assignment feedback',
      'Discussion participation',
    ],
    recommended: true,
    buttonText: 'Subscribe Now',
    accessLevel: 'registered',
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 19.99,
    billingPeriod: 'monthly',
    description: 'Complete access with certificates',
    features: [
      'All Registered features',
      'Premium course materials',
      'Course certificates',
      'Direct instructor support',
      'Downloadable resources',
      'Priority support',
    ],
    recommended: false,
    buttonText: 'Subscribe Now',
    accessLevel: 'premium',
  },
];

const SubscriptionPlans = ({
  currentPlan = 'guest',
  onSelectPlan = () => {},
}) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState(null);

  const handlePlanClick = planId => {
    // If user is not logged in, redirect to login
    if (!isAuthenticated()) {
      navigate('/login', { state: { from: '/pricing', selectedPlan: planId } });
      return;
    }

    setSelectedPlan(planId);
    onSelectPlan(planId);
  };

  return (
    <div className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Choose Your Learning Plan
          </h2>
          <p className="mt-4 text-xl text-gray-600">
            Select the plan that best fits your learning needs
          </p>
        </div>

        <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-3">
          {SUBSCRIPTION_PLANS.map(plan => {
            const isCurrentPlan = plan.id === currentPlan;

            return (
              <div
                key={plan.id}
                className={`rounded-lg shadow-lg divide-y divide-gray-200 flex flex-col ${
                  plan.recommended
                    ? 'border-2 border-primary-500 ring-2 ring-primary-500 ring-opacity-50'
                    : 'border border-gray-200'
                }`}
              >
                {plan.recommended && (
                  <div className="bg-primary-500 text-white text-center py-1 text-sm font-medium">
                    Recommended
                  </div>
                )}

                <div className="p-6">
                  <h3 className="text-2xl font-medium leading-6 text-gray-900">
                    {plan.name}
                  </h3>

                  <p className="mt-4 text-sm text-gray-500">
                    {plan.description}
                  </p>

                  <p className="mt-8">
                    <span className="text-4xl font-extrabold text-gray-900">
                      ${plan.price.toFixed(2)}
                    </span>
                    {plan.billingPeriod && (
                      <span className="text-base font-medium text-gray-500">
                        /{plan.billingPeriod}
                      </span>
                    )}
                  </p>

                  <Button
                    fullWidth
                    variant={isCurrentPlan ? 'secondary' : 'primary'}
                    className="mt-8"
                    onClick={() => handlePlanClick(plan.id)}
                    disabled={isCurrentPlan}
                  >
                    {isCurrentPlan ? 'Current Plan' : plan.buttonText}
                  </Button>
                </div>

                <div className="px-6 pt-6 pb-8">
                  <h4 className="text-sm font-medium text-gray-900 tracking-wide uppercase">
                    What's included
                  </h4>
                  <ul className="mt-6 space-y-4">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex space-x-3">
                        <svg
                          className="flex-shrink-0 h-5 w-5 text-green-500"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <span className="text-sm text-gray-500">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-10 text-center">
          <p className="text-base font-medium text-gray-500">
            Need help choosing?{' '}
            <a
              href="/contact"
              className="text-primary-600 hover:text-primary-500"
            >
              Contact us
            </a>{' '}
            for guidance.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPlans;
