/**
 * File: src/services/domains/subscription.service.ts
 * Version: 1.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * Subscription management service for user subscription operations
 */

import { logWarning } from '../../utils/logger';
import { apiClient } from '../http/apiClient';
import { ALLOW_MOCK_FALLBACK } from '../http/constants';
import { API_ENDPOINTS } from '../http/endpoints';
import { handleRequest } from '../utils/handleRequest';

export const subscriptionService = {
    getCurrentSubscription: async () => {
        try {
            return await handleRequest(
                async () =>
                    await apiClient.get(API_ENDPOINTS.USER.SUBSCRIPTION.CURRENT),
                'Failed to retrieve subscription information'
            );
        } catch (error) {
            if (
                ALLOW_MOCK_FALLBACK &&
                error.response &&
                error.response.status === 404
            ) {
                logWarning('Subscription endpoint not available, using mock data');

                return {
                    tier: 'guest',
                    status: 'active',
                    isActive: true,
                    daysRemaining: 30,
                    endDate: new Date(
                        Date.now() + 30 * 24 * 60 * 60 * 1000
                    ).toISOString(),
                };
            }

            throw error;
        }
    },

    upgradeSubscription: async subscriptionData => {
        try {
            return await handleRequest(
                async () =>
                    await apiClient.post(
                        API_ENDPOINTS.USER.SUBSCRIPTION.UPGRADE,
                        subscriptionData
                    ),
                'Failed to upgrade subscription'
            );
        } catch (error) {
            if (
                ALLOW_MOCK_FALLBACK &&
                error.response &&
                error.response.status === 404
            ) {
                logWarning(
                    'Subscription upgrade endpoint not available, using mock data'
                );

                return {
                    tier: subscriptionData.tier,
                    status: 'active',
                    isActive: true,
                    daysRemaining: 30,
                    endDate: new Date(
                        Date.now() + 30 * 24 * 60 * 60 * 1000
                    ).toISOString(),
                };
            }

            throw error;
        }
    },

    cancelSubscription: async () => {
        try {
            return await handleRequest(
                async () =>
                    await apiClient.post(API_ENDPOINTS.USER.SUBSCRIPTION.CANCEL),
                'Failed to cancel subscription'
            );
        } catch (error) {
            if (
                ALLOW_MOCK_FALLBACK &&
                error.response &&
                error.response.status === 404
            ) {
                logWarning(
                    'Subscription cancel endpoint not available, using mock data'
                );

                return {
                    tier: 'guest',
                    status: 'inactive',
                    isActive: false,
                    daysRemaining: 0,
                    endDate: new Date().toISOString(),
                };
            }

            throw error;
        }
    },
};
