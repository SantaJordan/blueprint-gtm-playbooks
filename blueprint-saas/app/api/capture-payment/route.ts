import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getJobById, updateJob } from '@/lib/supabase';

export async function POST(request: NextRequest) {
  // Verify this request is from Modal worker
  const authHeader = request.headers.get('authorization');
  const expectedSecret = `Bearer ${process.env.MODAL_WEBHOOK_SECRET}`;

  if (authHeader !== expectedSecret) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { job_id, playbook_url } = body;

    if (!job_id) {
      return NextResponse.json(
        { error: 'job_id is required' },
        { status: 400 }
      );
    }

    // Get job details
    const job = await getJobById(job_id);

    if (!job) {
      return NextResponse.json(
        { error: 'Job not found' },
        { status: 404 }
      );
    }

    if (!job.stripe_payment_intent_id) {
      // Job was created without Stripe payment (legacy or test)
      console.log(`Job ${job_id} has no payment intent, skipping capture`);
      return NextResponse.json({ success: true, skipped: true });
    }

    if (job.payment_status === 'captured') {
      console.log(`Payment for job ${job_id} already captured`);
      return NextResponse.json({ success: true, already_captured: true });
    }

    // Capture the payment
    // Note: receipt_email was set during checkout session creation,
    // Stripe will automatically send the receipt when captured
    const paymentIntent = await stripe.paymentIntents.capture(
      job.stripe_payment_intent_id
    );

    // Update job with payment captured
    await updateJob(job_id, {
      payment_status: 'captured',
      payment_captured_at: new Date().toISOString(),
      playbook_url: playbook_url || job.playbook_url,
    });

    console.log(`Payment captured for job ${job_id}: ${paymentIntent.status}`);

    return NextResponse.json({
      success: true,
      payment_status: paymentIntent.status,
    });
  } catch (error) {
    console.error('Failed to capture payment:', error);

    // If capture fails, log but don't fail the job
    // The playbook was still generated, we just couldn't charge
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Payment capture failed' },
      { status: 500 }
    );
  }
}
