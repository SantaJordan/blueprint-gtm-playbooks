import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { domain } = req.query;

  if (!domain) {
    return res.status(400).json({ error: 'domain parameter required' });
  }

  try {
    // Convert domain slug back to likely domain candidates.
    const parts = String(domain).split('-').filter(Boolean);
    const candidates = new Set();
    candidates.add(parts.join('.')); // naive
    if (parts.length >= 2) {
      candidates.add(`${parts.slice(0, -1).join('-')}.${parts[parts.length - 1]}`);
    }
    if (parts.length >= 3) {
      candidates.add(`${parts.slice(0, -2).join('-')}.${parts.slice(-2).join('.')}`);
    }

    const candidateList = Array.from(candidates);

    // Look for the most recent job matching this domain
    const patterns = [];
    for (const cand of candidateList) {
      patterns.push(`company_url.ilike.https://${cand}%`);
      patterns.push(`company_url.ilike.http://${cand}%`);
      patterns.push(`company_url.ilike.https://www.${cand}%`);
      patterns.push(`company_url.ilike.http://www.${cand}%`);
    }

    const { data: jobs, error } = await supabase
      .from('blueprint_jobs')
      .select('id, status, playbook_url, error, company_url, company_name, created_at')
      .or(patterns.join(','))
      .order('created_at', { ascending: false })
      .limit(1);

    if (error) {
      console.error('Supabase error:', error);
      return res.status(500).json({ error: 'Database error', details: error.message });
    }

    if (!jobs || jobs.length === 0) {
      return res.json({
        status: 'not_found',
        domain: candidateList[0]
      });
    }

    const job = jobs[0];

    return res.json({
      id: job.id,
      status: job.status,
      playbook_url: job.playbook_url,
      error: job.error,
      company_name: job.company_name,
      company_url: job.company_url,
      created_at: job.created_at
    });

  } catch (error) {
    console.error('Unexpected error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
