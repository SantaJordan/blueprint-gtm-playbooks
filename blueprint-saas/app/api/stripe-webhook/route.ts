import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { createJob } from '@/lib/supabase';
import Stripe from 'stripe';

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('stripe-signature');

  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 400 }
    );
  }

  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session);
      break;

    case 'payment_intent.canceled':
      await handlePaymentCanceled(event.data.object as Stripe.PaymentIntent);
      break;

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  return NextResponse.json({ received: true });
}

async function handleCheckoutCompleted(session: Stripe.Checkout.Session) {
  const domain = session.metadata?.domain;
  const companyUrl = session.metadata?.company_url;
  const paymentIntentId = session.payment_intent as string;
  const customerEmail = session.customer_details?.email || undefined;

  if (!domain || !companyUrl) {
    console.error('Missing domain or company_url in session metadata');
    return;
  }

  try {
    // Create job in Supabase - this will trigger the Modal worker via Supabase webhook
    await createJob({
      company_url: companyUrl,
      status: 'pending',
      stripe_checkout_session_id: session.id,
      stripe_payment_intent_id: paymentIntentId,
      customer_email: customerEmail,
      payment_status: 'authorized',
      amount_cents: session.amount_total || 3999,
    });

    console.log(`Job created for ${domain}, payment authorized`);
  } catch (error) {
    console.error('Failed to create job:', error);
    throw error;
  }
}

async function handlePaymentCanceled(paymentIntent: Stripe.PaymentIntent) {
  // This happens when authorization expires (after 7 days)
  // The job would already be failed or completed by now
  console.log(`Payment intent ${paymentIntent.id} was canceled`);

  // We could update the job status here if needed, but typically
  // the job would have completed or failed long before 7 days
}
