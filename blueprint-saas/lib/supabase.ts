import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Pure slug helper duplicated here to keep edge routes free of Stripe SDK.
function slugToDomainCandidates(slug: string): string[] {
  const candidates = new Set<string>();
  candidates.add(slug.replace(/-/g, '.'));
  const parts = slug.split('-').filter(Boolean);
  if (parts.length >= 2) {
    candidates.add(`${parts.slice(0, -1).join('-')}.${parts[parts.length - 1]}`);
  }
  if (parts.length >= 3) {
    candidates.add(`${parts.slice(0, -2).join('-')}.${parts.slice(-2).join('.')}`);
  }
  return Array.from(candidates);
}

// Lazy initialization to avoid errors during build
let _supabase: SupabaseClient | null = null;

function getSupabaseClient(): SupabaseClient {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseServiceKey) {
    throw new Error('Supabase environment variables are not set');
  }

  return createClient(supabaseUrl, supabaseServiceKey);
}

export function getSupabase(): SupabaseClient {
  if (!_supabase) {
    _supabase = getSupabaseClient();
  }
  return _supabase;
}

export interface BlueprintJob {
  id: string;
  company_url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  playbook_url?: string;
  error_message?: string;
  stripe_checkout_session_id?: string;
  stripe_payment_intent_id?: string;
  customer_email?: string;
  payment_status: 'pending' | 'authorized' | 'captured' | 'failed' | 'refunded';
  payment_captured_at?: string;
  amount_cents: number;
  created_at: string;
  updated_at?: string;
}

export async function createJob(data: Partial<BlueprintJob>): Promise<BlueprintJob> {
  const { data: job, error } = await getSupabase()
    .from('blueprint_jobs')
    .insert([data])
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to create job: ${error.message}`);
  }

  return job;
}

export async function getJobByDomain(domain: string): Promise<BlueprintJob | null> {
  // Normalize the domain slug into likely host candidates.
  const domainCandidates = slugToDomainCandidates(domain);

  // Build ilike patterns to tolerate legacy/raw stored URLs with http/paths.
  const patterns: string[] = [];
  for (const cand of domainCandidates) {
    patterns.push(`company_url.ilike.https://${cand}%`);
    patterns.push(`company_url.ilike.http://${cand}%`);
    patterns.push(`company_url.ilike.https://www.${cand}%`);
    patterns.push(`company_url.ilike.http://www.${cand}%`);
  }

  const { data: jobs, error } = await getSupabase()
    .from('blueprint_jobs')
    .select('*')
    .or(patterns.join(','))
    .order('created_at', { ascending: false })
    .limit(1);

  if (error) {
    throw new Error(`Failed to get job: ${error.message}`);
  }

  return jobs?.[0] || null;
}

export async function getJobById(id: string): Promise<BlueprintJob | null> {
  const { data: job, error } = await getSupabase()
    .from('blueprint_jobs')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    return null;
  }

  return job;
}

export async function updateJob(id: string, data: Partial<BlueprintJob>): Promise<BlueprintJob> {
  const { data: job, error } = await getSupabase()
    .from('blueprint_jobs')
    .update(data)
    .eq('id', id)
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to update job: ${error.message}`);
  }

  return job;
}

export async function getJobByPaymentIntent(paymentIntentId: string): Promise<BlueprintJob | null> {
  const { data: job, error } = await getSupabase()
    .from('blueprint_jobs')
    .select('*')
    .eq('stripe_payment_intent_id', paymentIntentId)
    .single();

  if (error) {
    return null;
  }

  return job;
}
