import { NextRequest, NextResponse } from 'next/server';
import { stripe, PRODUCT_PRICE_CENTS, normalizeCompanyDomain, domainToSlug } from '@/lib/stripe';

export async function POST(request: NextRequest) {
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

    const baseUrl = process.env.BASE_URL || 'https://blueprintgtm.com';

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
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
