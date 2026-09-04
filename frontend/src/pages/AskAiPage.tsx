import React, { useState, useEffect } from 'react';
import { askQuestion } from '../api/agent';
import { AskResponse } from '../api/types';
import { ConfidenceBadge } from '../components/Common/ConfidenceBadge';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { Sparkles, ChevronDown, ChevronUp, Terminal, AlertCircle } from 'lucide-react';

interface AskAiPageProps {
  initialQuestion?: string;
  onClearInitialQuestion?: () => void;
}

export const AskAiPage: React.FC<AskAiPageProps> = ({ 
  initialQuestion = '', 
  onClearInitialQuestion 
}) => {
  const [question, setQuestion] = useState(initialQuestion);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAuditTrace, setShowAuditTrace] = useState(false);

  const suggestedQuestions = [
    "Why didn't INV1060 match?",
    "Why is INV1046 considered a fee deduction?",
    "Which customers have the most exceptions?",
    "What's my total exception exposure in this batch?",
    "Show me all missing settlements.",
    "Why didn't INV9999 match?",
  ];

  const handleExecuteQuestion = async (qText: string) => {
    if (!qText.trim()) return;
    setQuestion(qText);
    setLoading(true);
    setError(null);
    setResponse(null);
    setShowAuditTrace(false);

    try {
      const res = await askQuestion(qText);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'AI Reasoning service was unable to complete this query.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuestion) {
      handleExecuteQuestion(initialQuestion);
      if (onClearInitialQuestion) {
        onClearInitialQuestion();
      }
    }
  }, [initialQuestion]);

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Workspace Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: -0.4 }}>
          Financial Operations Reasoning Workspace
        </h1>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
          Investigate reconciliation anomalies, check exposure, and inspect borderline matches backed by deterministic tool evidence.
        </p>
      </div>

      {/* Question Input Card */}
      <div className="card-section" style={{ padding: '20px 24px', marginBottom: 20 }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleExecuteQuestion(question);
          }}
          style={{ display: 'flex', gap: 12 }}
        >
          <input
            type="text"
            placeholder="Ask about this reconciliation batch (e.g. Why didn't INV1060 match?)..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 16px',
              fontSize: 14,
              border: '1px solid var(--border-card)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-app)',
              color: 'var(--text-primary)',
              outline: 'none',
            }}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            style={{
              backgroundColor: 'var(--accent-primary)',
              color: 'var(--text-inverse)',
              borderRadius: 'var(--radius-md)',
              padding: '0 20px',
              fontSize: 13,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              opacity: loading || !question.trim() ? 0.6 : 1,
              cursor: loading || !question.trim() ? 'not-allowed' : 'pointer',
              boxShadow: 'var(--shadow-subtle)',
            }}
          >
            <Sparkles size={16} />
            Reason with AI-CFO
          </button>
        </form>

        {/* Suggested Investigation Pills */}
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: 0.4 }}>
            Suggested Investigations
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleExecuteQuestion(q)}
                disabled={loading}
                style={{
                  backgroundColor: 'var(--bg-card-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-full)',
                  padding: '5px 12px',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-card)';
                  e.currentTarget.style.color = 'var(--accent-primary)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading Skeleton State */}
      {loading && (
        <div className="card-section" style={{ padding: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent-primary)' }}>
              Executing deterministic finance tools & synthesizing evidence...
            </span>
          </div>
          <SkeletonLoader lines={4} />
          <div style={{ height: 20 }} />
          <SkeletonLoader lines={3} />
        </div>
      )}

      {/* Error Card */}
      {error && !loading && (
        <div className="card-section" style={{
          backgroundColor: '#FEF2F2',
          borderColor: '#FECACA',
          borderLeft: '4px solid #DC2626',
          padding: 20,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <AlertCircle size={20} style={{ color: '#DC2626' }} />
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#991B1B' }}>
                Query Execution Failed
              </div>
              <div style={{ fontSize: 13, color: '#7F1D1D', marginTop: 2 }}>
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Answer & Machine-Readable Evidence Card */}
      {response && !loading && (
        <div className="card-section" style={{ padding: 28, borderLeft: '4px solid var(--accent-primary)' }}>
          {/* Header & Confidence */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.6, color: 'var(--text-muted)' }}>
              Executive Finding
            </span>
            <ConfidenceBadge confidence={response.confidence} />
          </div>

          {/* Plain Language Finding */}
          <div style={{
            fontSize: 15,
            lineHeight: 1.65,
            color: 'var(--text-primary)',
            marginBottom: 24,
            whiteSpace: 'pre-line',
          }}>
            {response.answer}
          </div>

          {/* Machine Evidence Table */}
          {response.evidence && response.evidence.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.4, marginBottom: 8 }}>
                Verifiable Financial Evidence
              </div>
              <div className="table-wrapper">
                <table className="data-table" style={{ fontSize: 12 }}>
                  <thead>
                    <tr>
                      {Object.keys(response.evidence[0]).map((k) => (
                        <th key={k}>{k.replace(/_/g, ' ')}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {response.evidence.map((item, idx) => (
                      <tr key={idx}>
                        {Object.values(item).map((val, vIdx) => (
                          <td key={vIdx} className={typeof val === 'number' ? 'font-mono' : undefined}>
                            {typeof val === 'number'
                              ? `₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                              : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Source Attribution */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 14, borderTop: '1px solid var(--border-subtle)', fontSize: 12, color: 'var(--text-muted)' }}>
            <span>Source: <code>reconciliation_report.csv</code> (Deterministic Ledger)</span>
            <span>Latency: {response.tools_called[0]?.latency_ms || 1.2}ms</span>
          </div>

          {/* Expandable Audit Trace */}
          <div style={{ marginTop: 18 }}>
            <button
              onClick={() => setShowAuditTrace(!showAuditTrace)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--accent-primary)',
              }}
            >
              <Terminal size={14} />
              {showAuditTrace ? 'Hide Audit Trace' : '▸ View Audit Trail & Tool Calls'}
              {showAuditTrace ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showAuditTrace && (
              <div style={{
                marginTop: 12,
                backgroundColor: 'var(--bg-card-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: 16,
                fontSize: 12,
                fontFamily: 'var(--font-mono)',
              }}>
                <div style={{ color: 'var(--text-secondary)', marginBottom: 8, fontWeight: 600 }}>
                  Tools Executed:
                </div>
                {response.tools_called.map((t, i) => (
                  <div key={i} style={{ marginBottom: 12 }}>
                    <div style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
                      &bull; {t.name} (args: {JSON.stringify(t.arguments)})
                    </div>
                    <pre style={{
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: 10,
                      marginTop: 4,
                      overflowX: 'auto',
                      maxHeight: 200,
                      fontSize: 11,
                    }}>
                      {JSON.stringify(t.result, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
