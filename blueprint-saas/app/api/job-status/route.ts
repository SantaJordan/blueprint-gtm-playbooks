import { NextRequest, NextResponse } from 'next/server';
import { getJobByDomain } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const domain = searchParams.get('domain');

  if (!domain) {
    return NextResponse.json(
      { error: 'Domain is required' },
      { status: 400 }
    );
  }

  try {
    const job = await getJobByDomain(domain);

    if (!job) {
      return NextResponse.json({
        status: 'not_found',
        message: 'No playbook found for this domain',
      });
    }

    return NextResponse.json({
      id: job.id,
      status: job.status,
      playbook_url: job.playbook_url,
      error: job.error_message,
      payment_status: job.payment_status,
      created_at: job.created_at,
    });
  } catch (error) {
    console.error('Error fetching job status:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch job status' },
      { status: 500 }
    );
  }
}
