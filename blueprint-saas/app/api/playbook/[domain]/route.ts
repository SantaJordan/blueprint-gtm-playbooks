import { NextRequest, NextResponse } from 'next/server';
import { getJobByDomain } from '@/lib/supabase';

export const runtime = 'edge';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ domain: string }> }
) {
  const { domain } = await params;

  if (!domain) {
    return new NextResponse('Domain is required', { status: 400 });
  }

  // Prefer the stored playbook_url (Vercel custom domain or GitHub Pages).
  try {
    const job = await getJobByDomain(domain);
    if (job?.playbook_url && job.status === 'completed') {
      return NextResponse.redirect(job.playbook_url, 302);
    }
    if (job && job.status !== 'completed') {
      // If a job exists but isn't done, send user to status.
      return NextResponse.redirect(new URL(`/status/${domain}`, request.url));
    }
  } catch (e) {
    console.error('[playbook] Failed to resolve job by domain:', e);
  }

  // Legacy fallback: construct GitHub Pages URL using old slug (without TLD).
  const parts = domain.split('-').filter(Boolean);
  let oldSlug = domain;
  if (parts.length >= 2) {
    oldSlug = parts.slice(0, -1).join('-');
    const last = parts[parts.length - 1];
    const secondLast = parts[parts.length - 2];
    if (last.length === 2 && secondLast.length <= 3 && parts.length >= 3) {
      oldSlug = parts.slice(0, -2).join('-');
    }
  }
  const githubPagesUrl = `https://santajordan.github.io/blueprint-gtm-playbooks/blueprint-gtm-playbook-${oldSlug}.html`;

  try {
    const response = await fetch(githubPagesUrl, {
      headers: {
        'User-Agent': 'Blueprint-GTM-Proxy/1.0',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return new NextResponse('Playbook not found', { status: 404 });
      }
      return new NextResponse('Failed to fetch playbook', { status: response.status });
    }

    const html = await response.text();

    return new NextResponse(html, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    });
  } catch (error) {
    console.error('Error fetching playbook:', error);
    return new NextResponse('Failed to fetch playbook', { status: 500 });
  }
}
