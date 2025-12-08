import { NextRequest, NextResponse } from 'next/server';
import { stripe, PRODUCT_PRICE_CENTS, normalizeCompanyDomain, domainToSlug } from '@/lib/stripe';

export async function POST(request: NextRequest) {
  // Debug: Log environment variable status
  const stripeKeySet = !!process.env.STRIPE_SECRET_KEY;
  const stripeKeyPrefix = process.env.STRIPE_SECRET_KEY?.substring(0, 10) || 'NOT_SET';
  const baseUrl = process.env.BASE_URL || 'https://playbooks.blueprintgtm.com';

  console.log('[create-checkout] Environment check:', {
    stripeKeySet,
    stripeKeyPrefix: stripeKeyPrefix + '...',
    baseUrl,
    baseUrlLength: baseUrl.length,
  });

  // Validate BASE_URL format
  if (!baseUrl.startsWith('https://')) {
    console.error('[create-checkout] Invalid BASE_URL - must start with https://');
    return NextResponse.json(
      { error: 'Server configuration error: invalid BASE_URL' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();
    const { companyUrl } = body;

    if (!companyUrl) {
      return NextResponse.json(
        { error: 'Company URL is required' },
        { status: 400 }
      );
    }

    const domain = normalizeCompanyDomain(companyUrl);
    const slug = domainToSlug(domain);
    const fullCompanyUrl = `https://${domain}`;

    console.log('[create-checkout] Processing:', { domain, slug, fullCompanyUrl });

    // Create Stripe Checkout Session with manual capture
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_intent_data: {
        capture_method: 'manual', // Authorization only - will capture on completion
        metadata: {
          domain: slug,
          company_url: fullCompanyUrl,
        },
      },
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: 'Blueprint GTM Playbook',
              description: `Intelligence playbook for ${domain}. Your playbook will be available at: https://playbooks.blueprintgtm.com/${slug}`,
            },
            unit_amount: PRODUCT_PRICE_CENTS,
          },
          quantity: 1,
        },
      ],
      success_url: `${baseUrl}/status/${slug}?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/?canceled=true`,
      metadata: {
        domain: slug,
        company_url: fullCompanyUrl,
      },
    });

    return NextResponse.json({
      sessionId: session.id,
      url: session.url,
    });
  } catch (error) {
    // Enhanced error logging for debugging
    const errorDetails = error instanceof Error ? {
      message: error.message,
      name: error.name,
      // @ts-expect-error - Stripe errors have additional properties
      type: error.type,
      // @ts-expect-error
      code: error.code,
      // @ts-expect-error
      param: error.param,
    } : error;

    console.error('[create-checkout] Error creating checkout session:', errorDetails);

    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
