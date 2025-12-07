import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ domain: string }> }
) {
  const { domain } = await params;

  if (!domain) {
    return new NextResponse('Domain is required', { status: 400 });
  }

  // Construct the GitHub Pages URL
  const githubPagesUrl = `https://santajordan.github.io/blueprint-gtm-playbooks/blueprint-gtm-playbook-${domain}.html`;

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
