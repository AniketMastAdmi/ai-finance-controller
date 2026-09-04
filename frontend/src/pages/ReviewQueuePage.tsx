import React, { useEffect, useState } from 'react';
import { getLowConfidenceMatches } from '../api/reconciliation';
import { LowConfidenceMatch, LowConfidenceResponse } from '../api/types';
import { ConfidenceBadge } from '../components/Common/ConfidenceBadge';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { AlertCircle, Sparkles, RefreshCw, ArrowRight } from 'lucide-react';

interface ReviewQueuePageProps {
  onAskAi: (question: string) => void;
}

export const ReviewQueuePage: React.FC<ReviewQueuePageProps> = ({ onAskAi }) => {
  const [data, setData] = useState<LowConfidenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getLowConfidenceMatches();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load low-confidence review queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="card-section">
          <SkeletonLoader lines={6} />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card-section" style={{ textAlign: 'center', padding: 32 }}>
        <p style={{ color: '#DC2626', marginBottom: 12 }}>{error || 'Error loading review queue.'}</p>
        <button
          onClick={fetchQueue}
          style={{
            padding: '8px 16px',
            backgroundColor: 'var(--accent-primary)',
            color: '#FFFFFF',
            borderRadius: 'var(--radius-md)',
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Intro Banner */}
      <div style={{
        backgroundColor: '#FFFBEB',
        border: '1px solid #FDE68A',
        borderRadius: 'var(--radius-lg)',
        padding: '20px 24px',
        marginBottom: 28,
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
          <AlertCircle size={22} style={{ color: '#D97706', flexShrink: 0, marginTop: 2 }} />
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#92400E', letterSpacing: -0.3 }}>
              Borderline Matches Requiring Controller Review
            </h2>
            <p style={{ fontSize: 13, color: '#78350F', marginTop: 4, lineHeight: 1.5 }}>
              The reconciliation engine classifies transactions with deductions between <strong>1.0% and 3.5%</strong> as <strong>MATCHED</strong>. 
              The AI-CFO confidence layer identifies transactions within <strong>0.5%</strong> of the upper boundary (<strong>{data.boundary_window}</strong>) to prevent concealed discounts or customer short-payments from slipping through.
            </p>
          </div>
        </div>
      </div>

      {/* Queue Count */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
          {data.total_low_confidence_matches} Transactions Flagged for Review
        </div>
        <button
          onClick={fetchQueue}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            fontSize: 12,
            color: 'var(--text-secondary)',
          }}
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Items List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {data.matches.map((item: LowConfidenceMatch) => (
          <div
            key={item.invoice_id}
            className="card-section"
            style={{
              padding: 24,
              marginBottom: 0,
              borderLeft: '4px solid #D97706',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className="font-mono" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {item.invoice_id}
                  </span>
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                    • {item.customer}
                  </span>
                  <ConfidenceBadge confidence="LOW_CONFIDENCE" />
                </div>
                <div className="font-mono" style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                  Settlement ID: {item.transaction_id}
                </div>
              </div>

              <button
                onClick={() => {
                  onAskAi(`Why is ${item.invoice_id} for ${item.customer} considered a fee deduction, and why did the AI-CFO flag it as low confidence?`);
                }}
                style={{
                  backgroundColor: 'var(--accent-primary)',
                  color: 'var(--text-inverse)',
                  borderRadius: 'var(--radius-md)',
                  padding: '8px 14px',
                  fontSize: 12,
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  boxShadow: 'var(--shadow-subtle)',
                }}
              >
                <Sparkles size={14} /> Investigate with AI-CFO <ArrowRight size={13} />
              </button>
            </div>

            {/* Metrics Breakdown Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: 16,
              backgroundColor: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '14px 18px',
              marginBottom: 16,
            }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Invoice Amount</div>
                <div className="font-mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                  ₹{item.invoice_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Settled Gateway Amount</div>
                <div className="font-mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                  ₹{item.settled_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Fee Deduction %</div>
                <div className="font-mono" style={{ fontSize: 15, fontWeight: 700, color: '#B45309', marginTop: 2 }}>
                  {item.deduction_percentage}%
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Distance to 3.5% Boundary</div>
                <div className="font-mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                  {item.distance_from_boundary}%
                </div>
              </div>
            </div>

            {/* Explanatory Context */}
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong>AI Controller Assessment:</strong> {item.reasoning}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
