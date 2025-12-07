import { createClient, SupabaseClient } from '@supabase/supabase-js';

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
  // Normalize the domain for matching
  const normalizedDomain = domain.replace(/-/g, '.');
  const companyUrl = `https://${normalizedDomain}`;
  const companyUrlWww = `https://www.${normalizedDomain}`;

  const { data: jobs, error } = await getSupabase()
    .from('blueprint_jobs')
    .select('*')
    .or(`company_url.eq.${companyUrl},company_url.eq.${companyUrlWww}`)
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
