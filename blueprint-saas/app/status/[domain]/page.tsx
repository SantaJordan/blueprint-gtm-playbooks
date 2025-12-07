'use client';

import { useState, useEffect, useCallback, use } from 'react';

interface JobStatus {
  id?: string;
  status: 'not_found' | 'pending' | 'processing' | 'completed' | 'failed';
  playbook_url?: string;
  error?: string;
  payment_status?: string;
  created_at?: string;
}

const POLL_INTERVAL = 5000; // 5 seconds

const stages = [
  { id: 'research', label: 'Research', icon: '🔍' },
  { id: 'analysis', label: 'Analysis', icon: '📊' },
  { id: 'messages', label: 'Messages', icon: '✉️' },
  { id: 'playbook', label: 'Playbook', icon: '📋' },
];

export default function StatusPage({ params }: { params: Promise<{ domain: string }> }) {
  const { domain } = use(params);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [currentStage, setCurrentStage] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  const displayDomain = domain.replace(/-/g, '.');

  // Calculate time remaining based on job creation time
  useEffect(() => {
    if (!status?.created_at || status?.status === 'completed' || status?.status === 'failed') {
      setTimeRemaining(null);
      return;
    }

    const updateTimeRemaining = () => {
      const created = new Date(status.created_at!);
      const elapsed = (Date.now() - created.getTime()) / 1000 / 60; // minutes
      const remaining = Math.max(0, 15 - elapsed);
      setTimeRemaining(Math.ceil(remaining));
    };

    updateTimeRemaining();
    const interval = setInterval(updateTimeRemaining, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [status?.created_at, status?.status]);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`/api/job-status?domain=${encodeURIComponent(domain)}`);
      const data = await response.json();
      setStatus(data);
      setLastChecked(new Date());

      // Update stage based on status
      if (data.status === 'processing') {
        // Simulate progress through stages
        setCurrentStage((prev) => (prev < 2 ? prev + 1 : prev));
      } else if (data.status === 'completed') {
        setCurrentStage(3);
      }
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  }, [domain]);

  useEffect(() => {
    fetchStatus();

    const interval = setInterval(() => {
      if (status?.status !== 'completed' && status?.status !== 'failed' && status?.status !== 'not_found') {
        fetchStatus();
      }
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchStatus, status?.status]);

  // Redirect to playbook when completed
  useEffect(() => {
    if (status?.status === 'completed' && status?.playbook_url) {
      const timer = setTimeout(() => {
        window.location.href = status.playbook_url!;
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const getStatusIcon = () => {
    switch (status?.status) {
      case 'pending':
        return { icon: '⏳', className: 'loading' };
      case 'processing':
        return { icon: '⚡', className: 'processing' };
      case 'completed':
        return { icon: '✓', className: 'completed' };
      case 'failed':
        return { icon: '✗', className: 'failed' };
      default:
        return { icon: '📋', className: 'not-found' };
    }
  };

  const getStatusText = () => {
    switch (status?.status) {
      case 'pending':
        return { title: 'Queued', subtitle: 'Waiting for worker...' };
      case 'processing':
        return { title: 'Generating...', subtitle: 'Running 5-wave analysis' };
      case 'completed':
        return { title: 'Complete!', subtitle: 'Redirecting to your playbook...' };
      case 'failed':
        return { title: 'Failed', subtitle: 'No charge - authorization released' };
      default:
        return { title: 'No Playbook Yet', subtitle: 'Start a new analysis' };
    }
  };

  const { icon, className } = getStatusIcon();
  const { title, subtitle } = getStatusText();

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="card max-w-lg w-full">
        {/* Logo */}
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold mb-2" style={{
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

        {/* Domain Name */}
        <div
          className="text-center text-2xl font-semibold mb-6"
          style={{ color: 'var(--print-blue)' }}
        >
          {displayDomain}
        </div>

        {/* Status Card */}
        <div
          className="rounded-xl p-6 mb-6"
          style={{ background: 'var(--ice)' }}
        >
          {/* Status Header */}
          <div className="flex items-center gap-4 mb-4">
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center text-2xl ${
                className === 'processing' ? 'animate-pulse-slow' : ''
              }`}
              style={{
                background: className === 'completed' ? '#d4edda' :
                  className === 'processing' ? 'var(--corn)' :
                  className === 'failed' ? '#f8d7da' :
                  'var(--light-print)',
                color: className === 'completed' ? '#155724' :
                  className === 'failed' ? '#721c24' :
                  'var(--dark-print)',
              }}
            >
              {icon}
            </div>
            <div>
              <h2 className="text-xl font-semibold" style={{ color: 'var(--dark-print)' }}>
                {title}
              </h2>
              <p className="text-sm" style={{ color: 'var(--dark-print)', opacity: 0.7 }}>
                {subtitle}
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          {(status?.status === 'pending' || status?.status === 'processing') && (
            <>
              <div
                className="h-2 rounded-full overflow-hidden mb-4"
                style={{ background: 'var(--light-print)' }}
              >
                <div className="h-full progress-shimmer" />
              </div>

              {/* Stage Indicators */}
              <div className="flex justify-between mb-4">
                {stages.map((stage, index) => (
                  <div
                    key={stage.id}
                    className={`flex flex-col items-center gap-1 ${
                      index <= currentStage ? 'opacity-100' : 'opacity-40'
                    }`}
                  >
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                      style={{
                        background: index < currentStage ? 'var(--light-print)' :
                          index === currentStage ? 'var(--corn)' : '#e5e7eb',
                        color: index <= currentStage ? 'var(--dark-print)' : '#9ca3af',
                      }}
                    >
                      {index < currentStage ? '✓' : stage.icon}
                    </div>
                    <span
                      className="text-xs font-medium"
                      style={{ color: 'var(--dark-print)' }}
                    >
                      {stage.label}
                    </span>
                  </div>
                ))}
              </div>

              <p
                className="text-center text-sm"
                style={{ color: 'var(--dark-print)', opacity: 0.7 }}
              >
                {timeRemaining !== null && timeRemaining > 0 ? (
                  <>Estimated time remaining: <strong>~{timeRemaining} minute{timeRemaining !== 1 ? 's' : ''}</strong></>
                ) : timeRemaining === 0 ? (
                  <strong>Almost done...</strong>
                ) : (
                  'Typically takes 12-15 minutes'
                )}
                {' '}• Page will auto-update.
              </p>
            </>
          )}

          {/* Completed State */}
          {status?.status === 'completed' && (
            <div
              className="p-4 rounded-lg text-center"
              style={{ background: '#d4edda', color: '#155724' }}
            >
              <strong className="block mb-2">Playbook Ready!</strong>
              Redirecting you now...
            </div>
          )}

          {/* Failed State */}
          {status?.status === 'failed' && (
            <>
              <div
                className="p-4 rounded-lg mb-4 text-sm"
                style={{
                  background: '#f8d7da',
                  color: '#721c24',
                  borderLeft: '3px solid #dc3545'
                }}
              >
                {status.error || 'An error occurred during generation'}
              </div>
              <a
                href="/"
                className="btn-primary w-full text-center block"
              >
                Try Again
              </a>
            </>
          )}

          {/* Not Found State */}
          {status?.status === 'not_found' && (
            <div className="text-center">
              <p
                className="mb-4"
                style={{ color: 'var(--dark-print)', opacity: 0.7 }}
              >
                No playbook found for this domain yet.
              </p>
              <a
                href="/"
                className="btn-primary w-full text-center block"
              >
                Generate Playbook
              </a>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          className="text-center text-sm"
          style={{ color: 'var(--dark-print)', opacity: 0.5 }}
        >
          {lastChecked && (
            <p>Last checked: {lastChecked.toLocaleTimeString()}</p>
          )}
        </div>
      </div>
    </main>
  );
}
