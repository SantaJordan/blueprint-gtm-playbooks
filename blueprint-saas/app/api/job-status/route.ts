import { NextRequest, NextResponse } from 'next/server';
import { getJobByDomain } from '@/lib/supabase';

// Parse error message into a category for user-friendly display
function categorizeError(errorMessage?: string): string {
  if (!errorMessage) return 'unknown';

  const lower = errorMessage.toLowerCase();

  if (lower.includes('stalled') || lower.includes('reset by cleanup')) {
    return 'timeout';
  }
  if (lower.includes('timeout') || lower.includes('timed out')) {
    return 'timeout';
  }
  if (lower.includes('rate limit') || lower.includes('429')) {
    return 'rate_limit';
  }
  if (lower.includes('unreachable') || lower.includes('enotfound') || lower.includes('econnrefused')) {
    return 'unreachable';
  }
  if (lower.includes('403') || lower.includes('forbidden')) {
    return 'blocked';
  }

  return 'unknown';
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const domain = searchParams.get('domain');

  console.log('[job-status] Query for domain:', domain);

  if (!domain) {
    return NextResponse.json(
      { error: 'Domain is required' },
      { status: 400 }
    );
  }

  try {
    const job = await getJobByDomain(domain);

    if (!job) {
      console.log('[job-status] No job found for domain:', domain);
      return NextResponse.json({
        status: 'not_found',
        message: 'No playbook found for this domain',
      });
    }

    console.log('[job-status] Found job:', {
      id: job.id,
      status: job.status,
      paymentStatus: job.payment_status,
      hasPlaybookUrl: !!job.playbook_url,
    });

    return NextResponse.json({
      id: job.id,
      status: job.status,
      playbook_url: job.playbook_url,
      error: job.error_message,
      error_category: categorizeError(job.error_message),
      payment_status: job.payment_status,
      created_at: job.created_at,
      updated_at: job.updated_at,
    });
  } catch (error) {
    console.error('[job-status] Error fetching job status:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch job status' },
      { status: 500 }
    );
  }
}
