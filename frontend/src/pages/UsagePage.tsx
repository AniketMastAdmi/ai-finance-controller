import React, { useEffect, useState } from 'react';
import { getUsageStats, updatePricingTier } from '../api/usage';
import { UsageStats } from '../api/types';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { RefreshCw } from 'lucide-react';

export const UsagePage: React.FC = () => {
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getUsageStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load usage metering stats.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
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
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="card-section" style={{ textAlign: 'center', padding: 32, color: '#DC2626' }}>
        {error}
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: -0.3 }}>
            API Usage Metering & Operations
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
            Real-time telemetry supporting the pay-per-investigation pricing architecture.
          </p>
        </div>
        <button
          onClick={fetchStats}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12,
            fontWeight: 600,
            padding: '7px 12px',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-card)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
          }}
        >
          <RefreshCw size={13} /> Refresh Metrics
        </button>
      </div>

      {/* Metering KPIs */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Reasoning Questions</div>
          <div className="kpi-value font-mono">
            {stats.calls_this_session}
          </div>
          <div className="kpi-sub">Total Investigations Handled</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Tool Calls</div>
          <div className="kpi-value font-mono">
            {stats.total_tool_calls}
          </div>
          <div className="kpi-sub">Deterministic Tools Invoked</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Avg Tools / Question</div>
          <div className="kpi-value font-mono">
            {stats.average_tools_per_question}
          </div>
          <div className="kpi-sub">Tool Execution Density</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Compute Units</div>
          <div className="kpi-value font-mono" style={{ color: 'var(--accent-primary)' }}>
            {stats.estimated_compute_units}
          </div>
          <div className="kpi-sub">PoC Billing Consumption</div>
        </div>
      </div>

      {/* Commercial Pricing Tier & Cost Simulator */}
      <div className="card-section" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div className="card-title">Commercial Pricing Tier & Cost Simulator</div>
            <div className="card-desc">
              Pay-per-investigation pricing model (configurable at $0.05, $0.10, or $0.15 per reasoning cycle).
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Pricing Tier:</span>
            {[0.05, 0.10, 0.15].map((tier) => {
              const active = (stats.pricing_tier_usd ?? 0.10) === tier;
              return (
                <button
                  key={tier}
                  onClick={async () => {
                    try {
                      const updated = await updatePricingTier(tier);
                      setStats(updated);
                    } catch (e: any) {
                      alert(e.message || 'Failed to update pricing tier');
                    }
                  }}
                  style={{
                    padding: '6px 14px',
                    fontSize: 12,
                    fontWeight: 600,
                    borderRadius: 'var(--radius-sm)',
                    border: active ? '1px solid var(--accent-primary)' : '1px solid var(--border-card)',
                    backgroundColor: active ? 'var(--accent-primary)' : 'var(--bg-card)',
                    color: active ? '#FFFFFF' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  ${tier.toFixed(2)} / query
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginTop: 16 }}>
          <div style={{ padding: '14px 18px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-card)' }}>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Estimated Cost (USD)</div>
            <div className="font-mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>
              ${(stats.estimated_usage_cost_usd ?? (stats.calls_this_session * (stats.pricing_tier_usd ?? 0.10))).toFixed(2)}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
              {stats.calls_this_session} queries × ${(stats.pricing_tier_usd ?? 0.10).toFixed(2)}
            </div>
          </div>

          <div style={{ padding: '14px 18px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-card)' }}>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Estimated Cost (INR)</div>
            <div className="font-mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent-primary)', marginTop: 4 }}>
              ₹{(stats.estimated_usage_cost_inr ?? ((stats.calls_this_session * (stats.pricing_tier_usd ?? 0.10)) * (stats.usd_to_inr_rate ?? 85.0))).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
              Converted at 1 USD = ₹{(stats.usd_to_inr_rate ?? 85.0).toFixed(1)} INR
            </div>
          </div>
        </div>
      </div>

      {/* Tool Call Breakdown Table */}
      <div className="card-section">
        <div className="card-title">Deterministic Tool Invocations</div>
        <div className="card-desc">Call frequency across finance tool library</div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Deterministic Tool</th>
                <th>Invocations</th>
                <th>Role in Reasoning Pipeline</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats.calls_by_tool).map(([toolName, count]) => {
                const descriptions: Record<string, string> = {
                  get_transaction: 'Single invoice/settlement lifecycle retrieval & confidence check',
                  list_exceptions: 'Exception categorization, filtering, and orphan funds detection',
                  get_batch_summary: 'Deterministic arithmetic calculation for headline reconciliation KPIs',
                  get_low_confidence_matches: 'Tolerance boundary threshold evaluation (3.0% - 4.0% fee deduction)',
                };
                return (
                  <tr key={toolName}>
                    <td className="font-mono" style={{ fontWeight: 600 }}>{toolName}</td>
                    <td className="font-mono" style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{count}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{descriptions[toolName] || 'Deterministic tool'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
