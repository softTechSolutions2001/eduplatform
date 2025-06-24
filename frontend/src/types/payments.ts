/**
 * Payment and Webhook Type Definitions
 * Resolves schema mismatch for webhook payload handling
 */

export type WebhookEventType =
  | 'subscription.created'
  | 'subscription.updated'
  | 'subscription.cancelled'
  | 'payment.succeeded'
  | 'payment.failed'
  | 'payment.refunded'
  | 'invoice.payment_succeeded'
  | 'invoice.payment_failed';

export interface WebhookPayload {
  webhook_id: string;
  event_type: WebhookEventType;
  payload: {
    subscription_id?: string;
    user_id: number;
    amount?: number;
    currency?: string;
    status: string;
    metadata?: Record<string, any>;
    invoice_id?: string;
    payment_intent_id?: string;
    customer_id?: string;
  };
  processed: boolean;
  created_at: string;
}

export interface WebhookResponse {
  data: WebhookPayload;
  success: boolean;
  message?: string;
}

// Subscription related types
export interface SubscriptionStatus {
  id: string;
  user_id: number;
  plan_type: 'guest' | 'basic' | 'premium' | 'enterprise';
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  current_period_start: string;
  current_period_end: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentRecord {
  id: string;
  user_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'refunded';
  payment_method: string;
  subscription_id?: string;
  created_at: string;
  updated_at: string;
}

// Processing and validation types
export interface WebhookValidationResult {
  is_valid: boolean;
  signature_verified: boolean;
  timestamp_valid: boolean;
  error_message?: string;
}

export interface WebhookProcessingResult {
  processed: boolean;
  action_taken: string;
  user_updated?: boolean;
  subscription_updated?: boolean;
  error_message?: string;
}

// Hook return types for React Query integration
export interface UseWebhookStatusReturn {
  webhooks: WebhookPayload[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export interface UsePaymentHistoryReturn {
  payments: PaymentRecord[];
  isLoading: boolean;
  error: string | null;
  hasNextPage: boolean;
  fetchNextPage: () => void;
}
