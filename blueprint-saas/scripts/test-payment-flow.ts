/**
 * End-to-End Payment Flow Test Script
 *
 * Tests the complete payment and workflow triggering pipeline:
 * 1. Creates a Stripe checkout session (test mode)
 * 2. Simulates the webhook payload
 * 3. Verifies job creation in Supabase
 * 4. Polls status endpoint until complete or timeout
 *
 * Usage:
 *   npx tsx scripts/test-payment-flow.ts [options]
 *
 * Options:
 *   --domain <domain>     Domain to test (default: test-example.com)
 *   --live                Use live API endpoint instead of localhost
 *   --skip-checkout       Skip checkout creation, just test webhook
 *   --skip-webhook        Skip webhook simulation, just test status
 *
 * Environment variables required:
 *   STRIPE_SECRET_KEY     Stripe secret key (sk_test_* for test mode)
 *   STRIPE_WEBHOOK_SECRET Webhook signing secret
 *   SUPABASE_URL          Supabase project URL
 *   SUPABASE_SERVICE_KEY  Supabase service key
 */

import Stripe from 'stripe';
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

// Configuration
const CONFIG = {
  baseUrl: process.argv.includes('--live')
    ? 'https://playbooks.blueprintgtm.com'
    : 'http://localhost:3000',
  testDomain: getArg('--domain') || `test-${Date.now()}.com`,
  skipCheckout: process.argv.includes('--skip-checkout'),
  skipWebhook: process.argv.includes('--skip-webhook'),
};

function getArg(name: string): string | undefined {
  const index = process.argv.indexOf(name);
  return index !== -1 ? process.argv[index + 1] : undefined;
}

// Initialize clients
function getStripe(): Stripe {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    throw new Error('STRIPE_SECRET_KEY environment variable is required');
  }
  if (!key.startsWith('sk_test_') && !key.startsWith('sk_live_')) {
    throw new Error('Invalid STRIPE_SECRET_KEY format');
  }
  if (key.startsWith('sk_live_')) {
    console.warn('\n  WARNING: Using LIVE Stripe key - real charges will occur!\n');
  }
  return new Stripe(key, { apiVersion: '2025-11-17.clover' });
}

function getSupabase() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) {
    throw new Error('SUPABASE_URL and SUPABASE_SERVICE_KEY are required');
  }
  return createClient(url, key);
}

// Utility functions
function domainToSlug(domain: string): string {
  return domain.replace(/\./g, '-');
}

function log(step: string, message: string, data?: object) {
  const timestamp = new Date().toISOString().split('T')[1].slice(0, 8);
  console.log(`[${timestamp}] [${step}] ${message}`);
  if (data) {
    console.log('  ', JSON.stringify(data, null, 2).replace(/\n/g, '\n  '));
  }
}

function success(message: string) {
  console.log(`\n  ✅ ${message}\n`);
}

function fail(message: string) {
  console.error(`\n  ❌ ${message}\n`);
}

// Test steps
async function testCheckoutCreation(stripe: Stripe, domain: string) {
  log('CHECKOUT', `Creating checkout session for ${domain}...`);

  const slug = domainToSlug(domain);
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    payment_intent_data: {
      capture_method: 'manual',
      metadata: {
        domain: slug,
        company_url: `https://${domain}`,
      },
    },
    line_items: [
      {
        price_data: {
          currency: 'usd',
          product_data: {
            name: 'Blueprint GTM Playbook (TEST)',
            description: `Test playbook for ${domain}`,
          },
          unit_amount: 50, // $0.50 for testing
        },
        quantity: 1,
      },
    ],
    success_url: `${CONFIG.baseUrl}/status/${slug}?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${CONFIG.baseUrl}/?canceled=true`,
    metadata: {
      domain: slug,
      company_url: `https://${domain}`,
    },
  });

  log('CHECKOUT', 'Session created:', {
    id: session.id,
    url: session.url,
    paymentIntent: session.payment_intent,
  });

  return session;
}

async function simulateWebhook(session: Stripe.Checkout.Session) {
  log('WEBHOOK', 'Simulating checkout.session.completed webhook...');

  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!webhookSecret) {
    throw new Error('STRIPE_WEBHOOK_SECRET is required for webhook simulation');
  }

  // Construct webhook payload
  const payload = JSON.stringify({
    id: `evt_test_${Date.now()}`,
    type: 'checkout.session.completed',
    data: {
      object: session,
    },
  });

  // Generate signature
  const timestamp = Math.floor(Date.now() / 1000);
  const signedPayload = `${timestamp}.${payload}`;
  const signature = crypto
    .createHmac('sha256', webhookSecret)
    .update(signedPayload)
    .digest('hex');
  const stripeSignature = `t=${timestamp},v1=${signature}`;

  // Send webhook request
  const response = await fetch(`${CONFIG.baseUrl}/api/stripe-webhook`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'stripe-signature': stripeSignature,
    },
    body: payload,
  });

  const result = await response.json();

  log('WEBHOOK', `Response: ${response.status}`, result);

  if (!response.ok) {
    throw new Error(`Webhook failed: ${response.status} ${JSON.stringify(result)}`);
  }

  return result;
}

async function checkSupabaseJob(supabase: ReturnType<typeof getSupabase>, domain: string) {
  log('SUPABASE', `Checking for job with domain ${domain}...`);

  const companyUrl = `https://${domain}`;
  const { data: jobs, error } = await supabase
    .from('blueprint_jobs')
    .select('*')
    .eq('company_url', companyUrl)
    .order('created_at', { ascending: false })
    .limit(1);

  if (error) {
    throw new Error(`Supabase query failed: ${error.message}`);
  }

  if (!jobs || jobs.length === 0) {
    log('SUPABASE', 'No job found for domain');
    return null;
  }

  const job = jobs[0];
  log('SUPABASE', 'Found job:', {
    id: job.id,
    status: job.status,
    paymentStatus: job.payment_status,
    createdAt: job.created_at,
  });

  return job;
}

async function pollJobStatus(domain: string, maxAttempts = 10) {
  log('STATUS', `Polling job status for ${domain}...`);

  const slug = domainToSlug(domain);

  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`${CONFIG.baseUrl}/api/job-status?domain=${slug}`);
    const data = await response.json();

    log('STATUS', `Attempt ${i + 1}/${maxAttempts}:`, data);

    if (data.status === 'completed') {
      success(`Job completed! Playbook URL: ${data.playbook_url}`);
      return data;
    }

    if (data.status === 'failed') {
      fail(`Job failed: ${data.error}`);
      return data;
    }

    if (data.status === 'not_found' && i === maxAttempts - 1) {
      fail('Job never appeared in database');
      return data;
    }

    // Wait 3 seconds between polls
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }

  fail('Timeout waiting for job to complete');
  return null;
}

async function cleanupTestJob(supabase: ReturnType<typeof getSupabase>, domain: string) {
  log('CLEANUP', `Removing test job for ${domain}...`);

  const companyUrl = `https://${domain}`;
  const { error } = await supabase
    .from('blueprint_jobs')
    .delete()
    .eq('company_url', companyUrl);

  if (error) {
    console.warn('  Warning: Failed to cleanup test job:', error.message);
  } else {
    log('CLEANUP', 'Test job removed');
  }
}

// Main test runner
async function main() {
  console.log('\n========================================');
  console.log('  Blueprint GTM Payment Flow Test');
  console.log('========================================\n');

  console.log('Configuration:');
  console.log(`  Base URL: ${CONFIG.baseUrl}`);
  console.log(`  Test Domain: ${CONFIG.testDomain}`);
  console.log(`  Skip Checkout: ${CONFIG.skipCheckout}`);
  console.log(`  Skip Webhook: ${CONFIG.skipWebhook}`);
  console.log('');

  try {
    const stripe = getStripe();
    const supabase = getSupabase();

    let session: Stripe.Checkout.Session | null = null;

    // Step 1: Create checkout session
    if (!CONFIG.skipCheckout) {
      console.log('\n--- Step 1: Create Checkout Session ---\n');
      session = await testCheckoutCreation(stripe, CONFIG.testDomain);
      success('Checkout session created');

      console.log('\n  To complete the checkout manually, visit:');
      console.log(`  ${session.url}\n`);
    }

    // Step 2: Simulate webhook
    if (!CONFIG.skipWebhook && session) {
      console.log('\n--- Step 2: Simulate Stripe Webhook ---\n');

      // Retrieve full session to get all fields
      const fullSession = await stripe.checkout.sessions.retrieve(session.id, {
        expand: ['payment_intent'],
      });

      await simulateWebhook(fullSession);
      success('Webhook simulation complete');
    }

    // Step 3: Check Supabase job
    console.log('\n--- Step 3: Verify Supabase Job ---\n');
    const job = await checkSupabaseJob(supabase, CONFIG.testDomain);

    if (job) {
      success('Job found in Supabase');
    } else {
      fail('Job NOT found in Supabase - webhook may have failed');
    }

    // Step 4: Poll status endpoint
    console.log('\n--- Step 4: Poll Status Endpoint ---\n');
    const finalStatus = await pollJobStatus(CONFIG.testDomain, 5);

    // Summary
    console.log('\n========================================');
    console.log('  Test Summary');
    console.log('========================================\n');

    const results = [
      { step: 'Checkout Creation', passed: !CONFIG.skipCheckout && !!session },
      { step: 'Webhook Simulation', passed: !CONFIG.skipWebhook },
      { step: 'Supabase Job', passed: !!job },
      { step: 'Status Polling', passed: finalStatus?.status !== 'not_found' },
    ];

    results.forEach(({ step, passed }) => {
      console.log(`  ${passed ? '✅' : '❌'} ${step}`);
    });

    const allPassed = results.every((r) => r.passed);
    console.log(`\n  Overall: ${allPassed ? '✅ PASSED' : '❌ FAILED'}\n`);

    // Cleanup (optional)
    // await cleanupTestJob(supabase, CONFIG.testDomain);

    process.exit(allPassed ? 0 : 1);
  } catch (error) {
    console.error('\n  Fatal error:', error);
    process.exit(1);
  }
}

main();
