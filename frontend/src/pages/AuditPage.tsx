import React, { useEffect, useState } from 'react';
import { getAuditTrail } from '../api/audit';
import { AuditEntry } from '../api/types';
import { ConfidenceBadge } from '../components/Common/ConfidenceBadge';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';

export const AuditPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const fetchAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAuditTrail(50);
      setEntries(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: -0.3 }}>
            Immutable Compliance Audit Trail
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
            Append-only JSONL log with automated secret scrubbing. Every AI reasoning step is verifiable.
          </p>
        </div>
        <button
          onClick={fetchAudit}
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
          <RefreshCw size={13} /> Refresh Log
        </button>
      </div>

      {loading ? (
        <div className="card-section">
          <SkeletonLoader lines={6} />
        </div>
      ) : error ? (
        <div className="card-section" style={{ color: '#DC2626', textAlign: 'center', padding: 24 }}>
          {error}
        </div>
      ) : entries.length === 0 ? (
        <div className="card-section" style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
          No audit entries recorded yet. Ask questions in the AI Workspace to generate verifiable audit logs.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {entries.map((entry) => {
            const isExpanded = expandedIds.has(entry.request_id);
            const dateStr = new Date(entry.timestamp).toLocaleString('en-IN', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            });

            return (
              <div
                key={entry.request_id}
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-card)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '16px 20px',
                  boxShadow: 'var(--shadow-subtle)',
                }}
              >
                {/* Entry Header */}
                <div
                  onClick={() => toggleExpand(entry.request_id)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }} className="font-mono">
                      {dateStr}
                    </span>
                    <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                      {entry.question}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <ConfidenceBadge confidence={entry.confidence} />
                    {isExpanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-subtle)', fontSize: 13 }}>
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                        Executive Answer
                      </div>
                      <div style={{ color: 'var(--text-primary)', lineHeight: 1.5 }}>
                        {entry.answer}
                      </div>
                    </div>

                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                        Deterministic Tools Executed ({entry.tools?.length || 0})
                      </div>
                      {entry.tools?.map((t, i) => (
                        <div key={i} style={{
                          backgroundColor: 'var(--bg-card-subtle)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-md)',
                          padding: 12,
                          marginBottom: 8,
                          fontSize: 12,
                        }}>
                          <div style={{ fontWeight: 600, color: 'var(--accent-primary)', marginBottom: 4 }} className="font-mono">
                            {t.name}
                          </div>
                          <div style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>
                            Arguments: <code>{JSON.stringify(t.arguments)}</code>
                          </div>
                          <pre style={{
                            backgroundColor: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            padding: 8,
                            borderRadius: 'var(--radius-sm)',
                            overflowX: 'auto',
                            maxHeight: 180,
                            fontSize: 11,
                          }}>
                            {JSON.stringify(t.result, null, 2)}
                          </pre>
                        </div>
                      ))}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', paddingTop: 8 }}>
                      <span>Request ID: <code className="font-mono">{entry.request_id}</code></span>
                      <span>Scrubbed & Signed</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
