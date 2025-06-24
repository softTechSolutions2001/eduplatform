/**
 * API Utilities for AI Course Builder
 */

import AI_BUILDER_CONFIG from '../config/aiBuilderConfig';

/**
 * Retry function for API calls
 * Retries the function up to the configured number of times
 * @param {Function} fn - Function to retry
 * @returns {Promise} - Result of the function
 */
export const retry = async fn => {
  for (let i = 0; i < AI_BUILDER_CONFIG.ai.retries.maxAttempts; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === AI_BUILDER_CONFIG.ai.retries.maxAttempts - 1) throw e;
      // Wait with exponential backoff before retrying
      await new Promise(resolve =>
        setTimeout(
          resolve,
          AI_BUILDER_CONFIG.ai.retries.backoffMs *
            Math.pow(AI_BUILDER_CONFIG.ai.retries.backoffMultiplier, i)
        )
      );
    }
  }
};

export default {
  retry,
};
