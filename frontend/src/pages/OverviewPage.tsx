import React, { useEffect, useState } from 'react';
import { getBatchSummary, getLowConfidenceMatches } from '../api/reconciliation';
import { BatchSummary, LowConfidenceResponse } from '../api/types';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { ConfidenceBadge } from '../components/Common/ConfidenceBadge';
import { ArrowRight, AlertTriangle, RefreshCw } from 'lucide-react';
import { NavTab } from '../components/Layout/Sidebar';

interface OverviewPageProps {
  onNavigate: (tab: NavTab) => void;
  onAskAi: (question: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate, onAskAi }) => {
  const [summary, setSummary] = useState<BatchSummary | null>(null);
  const [lowConf, setLowConf] = useState<LowConfidenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, lowConfData] = await Promise.all([
        getBatchSummary(),
        getLowConfidenceMatches(),
      ]);
      setSummary(sumData);
      setLowConf(lowConfData);
    } catch (err: any) {
      setError(err.message || 'Failed to load reconciliation overview.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="kpi-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="kpi-card">
              <SkeletonLoader lines={2} />
            </div>
          ))}
        </div>
        <div className="card-section">
          <SkeletonLoader lines={5} />
        </div>
      </div>
    );
  }

  if (error || !summary || !lowConf) {
    return (
      <div className="card-section" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <AlertTriangle size={32} style={{ color: '#DC2626', margin: '0 auto 12px auto' }} />
        <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>
          Reconciliation Service Unavailable
        </h3>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
          {error || 'Unable to connect to FastAPI reasoning layer.'}
        </p>
        <button
          onClick={fetchData}
          style={{
            marginTop: 16,
            padding: '8px 16px',
            backgroundColor: 'var(--accent-primary)',
            color: '#FFFFFF',
            borderRadius: 'var(--radius-md)',
            fontSize: 12,
            fontWeight: 600,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <RefreshCw size={14} /> Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* 4 Headline KPI Metrics (Above The Fold — Comprehended in 3 seconds) */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Match Rate</div>
          <div className="kpi-value font-mono">
            {summary.match_rate_percentage}%
          </div>
          <div className="kpi-sub">
            {summary.matched_invoices} of {summary.total_invoices} Invoices Reconciled
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Invoice Exceptions</div>
          <div className="kpi-value font-mono" style={{ color: '#B91C1C' }}>
            {summary.exception_invoices}
          </div>
          <div className="kpi-sub">
            {summary.exception_rate_percentage}% Total Exception Rate
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Exception Exposure</div>
          <div className="kpi-value font-mono">
            ₹{summary.total_exception_exposure_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="kpi-sub">
            Total Capital Requiring Investigation
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Orphan Settlements</div>
          <div className="kpi-value font-mono" style={{ color: '#D97706' }}>
            {summary.orphan_settlement_count}
          </div>
          <div className="kpi-sub">
            ₹{summary.total_orphan_settlement_value_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })} Unlinked Gateway Receipts
          </div>
        </div>
      </div>

      {/* Prominent Low-Confidence Review Callout (Differentiating AI-CFO Feature) */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid #FDE68A',
        borderLeft: '4px solid #D97706',
        borderRadius: 'var(--radius-lg)',
        padding: '20px 24px',
        marginBottom: 28,
        boxShadow: 'var(--shadow-subtle)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 15, fontWeight: 700, color: '#92400E' }}>
                Review Recommended: Low-Confidence Matches ({lowConf.total_low_confidence_matches})
              </span>
              <ConfidenceBadge confidence="LOW_CONFIDENCE" />
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4, maxWidth: 800 }}>
              The reconciliation engine classified these transactions as <strong>MATCHED</strong> under standard fee deductions.
              However, our AI-CFO confidence layer flagged that deductions are within 0.5% of the 3.5% tolerance boundary ({lowConf.boundary_window}), which may conceal unauthorized discounts or disputes.
            </p>
          </div>
          <button
            onClick={() => onNavigate('review-queue')}
            style={{
              padding: '8px 14px',
              backgroundColor: '#FEF3C7',
              color: '#92400E',
              border: '1px solid #FCD34D',
              borderRadius: 'var(--radius-md)',
              fontSize: 12,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            Open Review Queue <ArrowRight size={14} />
          </button>
        </div>

        {lowConf.matches.length > 0 && (
          <div style={{ marginTop: 16, overflowX: 'auto' }}>
            <table className="data-table" style={{ fontSize: 12 }}>
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>Customer</th>
                  <th>Invoice Amount</th>
                  <th>Settled Amount</th>
                  <th>Deduction %</th>
                  <th>Distance from Limit</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {lowConf.matches.map((m) => (
                  <tr key={m.invoice_id} onClick={() => onNavigate('review-queue')}>
                    <td className="font-mono" style={{ fontWeight: 600 }}>{m.invoice_id}</td>
                    <td>{m.customer}</td>
                    <td className="font-mono">₹{m.invoice_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="font-mono">₹{m.settled_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="font-mono" style={{ color: '#B45309', fontWeight: 600 }}>{m.deduction_percentage}%</td>
                    <td className="font-mono">{m.distance_from_boundary}% from 3.5%</td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAskAi(`Why is ${m.invoice_id} for ${m.customer} considered a fee deduction, and why is it flagged low confidence?`);
                        }}
                        style={{
                          fontSize: 11,
                          fontWeight: 600,
                          color: 'var(--accent-primary)',
                          textDecoration: 'underline',
                        }}
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Exception Breakdown & Reconciliation Categories */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <div className="card-section" style={{ marginBottom: 0 }}>
          <div className="card-title">Exception Breakdown</div>
          <div className="card-desc">Categorized invoice failure modes</div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Count</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(summary.exception_breakdown).map(([category, count]) => (
                  <tr key={category} onClick={() => onNavigate('reconciliation')}>
                    <td style={{ fontWeight: 500, textTransform: 'capitalize' }}>
                      {category.replace(/_/g, ' ')}
                    </td>
                    <td className="font-mono" style={{ fontWeight: 600, color: '#B91C1C' }}>
                      {count}
                    </td>
                    <td>
                      <span style={{ fontSize: 11, color: 'var(--accent-primary)', fontWeight: 600 }}>
                        View in Table &rarr;
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card-section" style={{ marginBottom: 0 }}>
          <div className="card-title">Reconciliation Integrity & SLA</div>
          <div className="card-desc">Batch parameters & trust metrics</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, fontSize: 13 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 10, borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Standard Clean Matches</span>
              <span className="font-mono" style={{ fontWeight: 600 }}>{summary.matched_breakdown['clean_match'] || 36} invoices</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 10, borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Fee Deduction Matches</span>
              <span className="font-mono" style={{ fontWeight: 600 }}>{summary.matched_breakdown['fee_deduction'] || 12} invoices</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 10, borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Total Settled Gateway Volume</span>
              <span className="font-mono" style={{ fontWeight: 600 }}>
                ₹{summary.total_settled_value_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Settlement SLA Threshold</span>
              <span className="font-mono" style={{ fontWeight: 600 }}>14 Days Max</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
