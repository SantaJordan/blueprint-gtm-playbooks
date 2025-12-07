-- Blueprint GTM SaaS - Supabase Schema Migration
-- Add payment tracking columns to blueprint_jobs table

-- Add Stripe session ID
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  stripe_checkout_session_id TEXT;

-- Add Stripe payment intent ID
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  stripe_payment_intent_id TEXT;

-- Add customer email
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  customer_email TEXT;

-- Add payment status with check constraint
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  payment_status TEXT DEFAULT 'pending';

-- Add constraint if not exists (run separately if needed)
-- ALTER TABLE blueprint_jobs ADD CONSTRAINT payment_status_check
--   CHECK (payment_status IN ('pending', 'authorized', 'captured', 'failed', 'refunded'));

-- Add payment captured timestamp
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  payment_captured_at TIMESTAMPTZ;

-- Add amount in cents
ALTER TABLE blueprint_jobs ADD COLUMN IF NOT EXISTS
  amount_cents INTEGER DEFAULT 3999;

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_jobs_checkout_session
  ON blueprint_jobs(stripe_checkout_session_id);

CREATE INDEX IF NOT EXISTS idx_jobs_payment_intent
  ON blueprint_jobs(stripe_payment_intent_id);

-- Grant permissions (adjust role as needed)
-- GRANT SELECT, INSERT, UPDATE ON blueprint_jobs TO authenticated;
-- GRANT SELECT, INSERT, UPDATE ON blueprint_jobs TO service_role;
