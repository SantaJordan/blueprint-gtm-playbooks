'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

function HomeContent() {
  const [companyUrl, setCompanyUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const searchParams = useSearchParams();

  const canceled = searchParams.get('canceled');

  useEffect(() => {
    if (canceled) {
      setError('Payment was canceled. You can try again when ready.');
    }
  }, [canceled]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ companyUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create checkout session');
      }

      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setIsLoading(false);
    }
  };

  const normalizeForDisplay = (url: string) => {
    return url
      .replace(/^https?:\/\//, '')
      .replace(/^www\./, '')
      .split('/')[0];
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="card max-w-lg w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2" style={{
            background: 'linear-gradient(135deg, var(--print-blue) 0%, var(--dark-print) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            borderBottom: 'none',
            paddingBottom: 0,
          }}>
            Blueprint GTM
          </h1>
          <p className="text-lg" style={{ color: 'var(--dark-print)', opacity: 0.7 }}>
            Intelligence-Driven Outreach
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="companyUrl"
              className="block text-sm font-semibold mb-2"
              style={{ color: 'var(--dark-print)' }}
            >
              Company Domain
            </label>
            <input
              type="text"
              id="companyUrl"
              value={companyUrl}
              onChange={(e) => setCompanyUrl(e.target.value)}
              placeholder="example.com"
              required
              disabled={isLoading}
              className="w-full"
            />
            {companyUrl && (
              <p className="mt-2 text-sm" style={{ color: 'var(--print-blue)' }}>
                Analyzing: {normalizeForDisplay(companyUrl)}
              </p>
            )}
          </div>

          {error && (
            <div
              className="p-4 rounded-lg text-sm"
              style={{
                background: '#fee2e2',
                color: '#991b1b',
                borderLeft: '3px solid #dc2626'
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !companyUrl.trim()}
            className="btn-primary w-full text-lg"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Creating checkout...
              </span>
            ) : (
              'Get Your Playbook — $0.50'
            )}
          </button>
        </form>

        {/* Trust Signals */}
        <div className="mt-8 space-y-3">
          <div className="flex items-center gap-3">
            <span
              className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm"
              style={{ background: 'var(--corn)', color: 'var(--dark-print)' }}
            >
              ✓
            </span>
            <span className="text-sm" style={{ color: 'var(--dark-print)', opacity: 0.8 }}>
              <strong>Pay only when complete</strong> — Authorization held until delivery
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm"
              style={{ background: 'var(--corn)', color: 'var(--dark-print)' }}
            >
              ✓
            </span>
            <span className="text-sm" style={{ color: 'var(--dark-print)', opacity: 0.8 }}>
              <strong>12-15 minute delivery</strong> — AI-powered research & generation
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm"
              style={{ background: 'var(--corn)', color: 'var(--dark-print)' }}
            >
              ✓
            </span>
            <span className="text-sm" style={{ color: 'var(--dark-print)', opacity: 0.8 }}>
              <strong>Receipt sent to your email</strong> — Via Stripe secure checkout
            </span>
          </div>
        </div>

        {/* Footer */}
        <div
          className="mt-8 pt-6 text-center text-sm"
          style={{
            borderTop: '1px solid var(--light-print)',
            color: 'var(--dark-print)',
            opacity: 0.6
          }}
        >
          <p>Powered by Claude AI • Data from 50+ public sources</p>
        </div>
      </div>
    </main>
  );
}

export default function Home() {
  return (
    <Suspense fallback={
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="card max-w-lg w-full animate-pulse">
          <div className="h-12 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </main>
    }>
      <HomeContent />
    </Suspense>
  );
}
