/**
 * File: frontend/src/pages/subscription/CheckoutPage.jsx
 * Purpose: Handle payment and checkout for subscription upgrades
 *
 * This component:
 * 1. Shows subscription details and costs
 * 2. Collects payment information
 * 3. Processes the subscription upgrade
 * 4. Redirects to success page after completion
 *
 * Variables to modify:
 * - PLAN_DETAILS: Update subscription plan names and prices
 * - PAYMENT_METHODS: Configure available payment methods
 *
 * Backend Connection Points:
 * - POST /users/subscription/upgrade/ - Upgrade subscription
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { MainLayout } from '../../components/layouts';
import { Button, Card, FormInput, Alert } from '../../components/common';
import { useAuth } from '../../contexts/AuthContext';
import { subscriptionService } from '../../services/api';

// Plan information - modify to match your subscription tiers
const PLAN_DETAILS = {
  basic: {
    name: 'Basic Plan',
    price: 9.99,
    description: 'Full access to registered user content',
    billingCycle: 'monthly',
  },
  premium: {
    name: 'Premium Plan',
    price: 19.99,
    description: 'Complete access with certificates',
    billingCycle: 'monthly',
  },
};

// Available payment methods
const PAYMENT_METHODS = [
  { id: 'credit_card', name: 'Credit or Debit Card' },
  { id: 'paypal', name: 'PayPal' },
];

const CheckoutPage = () => {
  const { planId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { upgradeSubscription } = useAuth();

  // Redirect path after successful checkout
  const from = location.state?.from || '/dashboard';

  // Form state
  const [formData, setFormData] = useState({
    cardNumber: '',
    cardExpiry: '',
    cardCvc: '',
    nameOnCard: '',
    paymentMethod: 'credit_card',
    autoRenew: true,
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Plan information
  const [planInfo, setPlanInfo] = useState(null);

  // Set plan information based on the plan ID
  useEffect(() => {
    if (!PLAN_DETAILS[planId]) {
      // Invalid plan ID, redirect to pricing page
      navigate('/pricing');
      return;
    }

    setPlanInfo(PLAN_DETAILS[planId]);
  }, [planId, navigate]);

  // Handle form input change
  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  // Handle form submission
  const handleSubmit = async e => {
    e.preventDefault();

    // Simple validation
    if (
      formData.paymentMethod === 'credit_card' &&
      (!formData.cardNumber || !formData.cardExpiry || !formData.cardCvc)
    ) {
      setError('Please fill in all required fields.');
      return;
    }

    try {
      setLoading(true);

      // In a real app, you would process payment here
      // For this demo, we'll just update the subscription

      await upgradeSubscription(planId, {
        paymentMethod: formData.paymentMethod,
        autoRenew: formData.autoRenew,
      });

      // Redirect to success page
      navigate('/subscription/success', {
        state: {
          from,
          planName: planInfo.name,
          planPrice: planInfo.price,
        },
      });
    } catch (err) {
      console.error('Checkout error:', err);
      setError('Failed to process payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!planInfo) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto mb-4"></div>
            <p className="text-primary-700 font-medium">
              Loading plan information...
            </p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="bg-gray-50 py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Complete Your Subscription
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              You're subscribing to our {planInfo.name}
            </p>
          </div>

          {error && (
            <Alert type="error" title="Checkout Error" className="mb-6">
              {error}
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Order summary */}
            <Card className="md:col-span-1 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Order Summary
              </h2>

              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">{planInfo.name}</span>
                  <span className="font-medium">
                    ${planInfo.price}/{planInfo.billingCycle}
                  </span>
                </div>

                <div className="border-t border-gray-200 pt-4 flex justify-between">
                  <span className="font-medium">Total</span>
                  <span className="font-bold">
                    ${planInfo.price}/{planInfo.billingCycle}
                  </span>
                </div>
              </div>

              <div className="mt-6 text-sm text-gray-500">
                <p>
                  You will be charged ${planInfo.price} every{' '}
                  {planInfo.billingCycle}.
                </p>
                <p className="mt-1">
                  You can cancel your subscription at any time from your account
                  settings.
                </p>
              </div>
            </Card>

            {/* Payment form */}
            <Card className="md:col-span-2 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Payment Information
              </h2>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Payment method selection */}
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-2">
                    Payment Method
                  </label>

                  <div className="space-y-2">
                    {PAYMENT_METHODS.map(method => (
                      <div key={method.id} className="flex items-center">
                        <input
                          id={`payment-${method.id}`}
                          name="paymentMethod"
                          type="radio"
                          value={method.id}
                          checked={formData.paymentMethod === method.id}
                          onChange={handleChange}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                        />
                        <label
                          htmlFor={`payment-${method.id}`}
                          className="ml-3 text-gray-700"
                        >
                          {method.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Credit card details - only show if credit card is selected */}
                {formData.paymentMethod === 'credit_card' && (
                  <div className="space-y-4">
                    <FormInput
                      label="Card Number"
                      name="cardNumber"
                      type="text"
                      placeholder="1234 5678 9012 3456"
                      value={formData.cardNumber}
                      onChange={handleChange}
                      required
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormInput
                        label="Expiry Date"
                        name="cardExpiry"
                        type="text"
                        placeholder="MM/YY"
                        value={formData.cardExpiry}
                        onChange={handleChange}
                        required
                      />

                      <FormInput
                        label="CVC"
                        name="cardCvc"
                        type="text"
                        placeholder="123"
                        value={formData.cardCvc}
                        onChange={handleChange}
                        required
                      />
                    </div>

                    <FormInput
                      label="Name on Card"
                      name="nameOnCard"
                      type="text"
                      placeholder="John Smith"
                      value={formData.nameOnCard}
                      onChange={handleChange}
                      required
                    />
                  </div>
                )}

                {/* Auto-renew option */}
                <div className="flex items-center">
                  <input
                    id="auto-renew"
                    name="autoRenew"
                    type="checkbox"
                    checked={formData.autoRenew}
                    onChange={handleChange}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="auto-renew" className="ml-2 text-gray-700">
                    Automatically renew subscription
                  </label>
                </div>

                {/* Submit button */}
                <div className="flex justify-between items-center pt-4">
                  <Button
                    type="button"
                    color="secondary"
                    onClick={() => navigate('/pricing')}
                    disabled={loading}
                  >
                    Back
                  </Button>

                  <Button type="submit" color="primary" disabled={loading}>
                    {loading
                      ? 'Processing...'
                      : `Pay $${planInfo.price} and Subscribe`}
                  </Button>
                </div>
              </form>

              <div className="mt-6 text-center text-sm text-gray-500">
                <p>
                  Your payment information is processed securely. We do not
                  store your credit card details.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default CheckoutPage;
