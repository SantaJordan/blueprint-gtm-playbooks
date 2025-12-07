import Stripe from 'stripe';

function getStripeClient(): Stripe {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error('STRIPE_SECRET_KEY is not set');
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: '2025-11-17.clover',
    typescript: true,
  });
}

// Lazy initialization to avoid errors during build
let _stripe: Stripe | null = null;

export function getStripe(): Stripe {
  if (!_stripe) {
    _stripe = getStripeClient();
  }
  return _stripe;
}

// For backwards compatibility (throws during build if used at module level)
export const stripe = {
  get checkout() { return getStripe().checkout; },
  get paymentIntents() { return getStripe().paymentIntents; },
  get webhooks() { return getStripe().webhooks; },
};

export const PRODUCT_PRICE_CENTS = 50; // $0.50 - TESTING MODE (Stripe minimum)

export function normalizeCompanyDomain(input: string): string {
  let url = input.trim().toLowerCase();

  // Remove protocol
  url = url.replace(/^https?:\/\//, '');

  // Remove www
  url = url.replace(/^www\./, '');

  // Remove trailing slashes and paths
  url = url.split('/')[0];

  return url;
}

export function domainToSlug(domain: string): string {
  return normalizeCompanyDomain(domain).replace(/\./g, '-');
}

export function slugToDomain(slug: string): string {
  return slug.replace(/-/g, '.');
}
