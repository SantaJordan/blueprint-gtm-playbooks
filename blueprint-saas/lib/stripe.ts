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

export const PRODUCT_PRICE_CENTS = 50; // $0.50 for testing

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

/**
 * Convert a slug like "canvas-medical-com" back into likely domain candidates.
 * Slugs are created by replacing dots with dashes, so hyphens are ambiguous.
 */
export function slugToDomainCandidates(slug: string): string[] {
  const candidates = new Set<string>();

  // Naive replacement (existing behavior)
  candidates.add(slug.replace(/-/g, '.'));

  const parts = slug.split('-').filter(Boolean);
  if (parts.length >= 2) {
    // Replace only the last dash with a dot (best for hyphenated hosts)
    candidates.add(`${parts.slice(0, -1).join('-')}.${parts[parts.length - 1]}`);
  }
  if (parts.length >= 3) {
    // Replace the last two dashes with dots (best for multi-part TLDs like co.uk)
    candidates.add(`${parts.slice(0, -2).join('-')}.${parts.slice(-2).join('.')}`);
  }

  return Array.from(candidates);
}

/**
 * Best-effort display domain from slug.
 */
export function slugToDomain(slug: string): string {
  const parts = slug.split('-').filter(Boolean);
  if (parts.length >= 3) {
    const last = parts[parts.length - 1];
    const secondLast = parts[parts.length - 2];
    if (last.length === 2 && secondLast.length <= 3) {
      return `${parts.slice(0, -2).join('-')}.${secondLast}.${last}`;
    }
  }
  if (parts.length >= 2) {
    return `${parts.slice(0, -1).join('-')}.${parts[parts.length - 1]}`;
  }
  return slug;
}
