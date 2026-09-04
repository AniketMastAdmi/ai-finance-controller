import React, { useEffect, useState } from 'react';
import { getUsageStats } from '../api/usage';
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
