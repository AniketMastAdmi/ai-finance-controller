import React from 'react';
import { ReconciliationRecord } from '../../api/types';
import { StatusBadge } from '../Common/StatusBadge';
import { ConfidenceBadge } from '../Common/ConfidenceBadge';
import { X, Sparkles, Calendar, User, FileText, ArrowRight } from 'lucide-react';

interface TransactionDrawerProps {
  transaction: ReconciliationRecord | null;
  onClose: () => void;
  onAskAi: (question: string) => void;
}

export const TransactionDrawer: React.FC<TransactionDrawerProps> = ({
  transaction,
  onClose,
  onAskAi,
}) => {
  if (!transaction) return null;

  const handleInvestigate = () => {
    const question = `Why did ${transaction.invoice_id} have status ${transaction.status} with reason ${transaction.reason}? Explain the discrepancy and financial evidence.`;
    onAskAi(question);
  };

  const isMatched = transaction.status === 'MATCHED';
  const hasDeduction = transaction.deduction_percentage > 0 && transaction.deduction_percentage < 100;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Transaction Record
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }} className="font-mono">
              {transaction.invoice_id}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{ padding: 6, color: 'var(--text-secondary)', borderRadius: 'var(--radius-sm)' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status Callout */}
        <div style={{
          backgroundColor: isMatched ? 'var(--status-matched-bg)' : 'var(--status-exception-bg)',
          border: `1px solid ${isMatched ? 'var(--status-matched-border)' : 'var(--status-exception-border)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '14px 16px',
          marginBottom: 24,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <StatusBadge status={transaction.status} reason={transaction.reason} />
            {transaction.confidence && <ConfidenceBadge confidence={transaction.confidence} />}
          </div>
          <div style={{ fontSize: 13, color: isMatched ? 'var(--status-matched-text)' : 'var(--status-exception-text)', marginTop: 8 }}>
            {transaction.details}
          </div>
        </div>

        {/* Core Financial Details */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12 }}>
            Financial Breakdown
          </div>
          
          <div style={{
            backgroundColor: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <User size={14} /> Customer
              </span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{transaction.customer}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <FileText size={14} /> Settlement ID(s)
              </span>
              <span className="font-mono" style={{ color: 'var(--text-primary)', fontSize: 12 }}>
                {transaction.transaction_id || 'NONE'}
              </span>
            </div>

            <div style={{ height: 1, backgroundColor: 'var(--border-subtle)' }} />

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Invoice Amount</span>
              <span className="font-mono" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                ₹{transaction.invoice_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Settled Amount</span>
              <span className="font-mono" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                ₹{transaction.settlement_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>

            {hasDeduction && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--text-secondary)' }}>Deduction Variance</span>
                <span className="font-mono" style={{ fontWeight: 600, color: '#B45309' }}>
                  {transaction.deduction_percentage}% (₹{(transaction.invoice_amount - transaction.settlement_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })})
                </span>
              </div>
            )}

            {transaction.days_to_settle >= 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Calendar size={14} /> Settlement Timeline
                </span>
                <span style={{ color: 'var(--text-primary)' }}>
                  {transaction.days_to_settle} day(s) {transaction.days_to_settle > 14 ? '(SLA Breached)' : '(Within SLA)'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* AI Investigation Trigger */}
        <div style={{ marginTop: 'auto', paddingTop: 20 }}>
          <button
            onClick={handleInvestigate}
            style={{
              width: '100%',
              backgroundColor: 'var(--accent-primary)',
              color: 'var(--text-inverse)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 16px',
              fontSize: 13,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              boxShadow: 'var(--shadow-subtle)',
              transition: 'background-color 0.15s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'var(--accent-primary-hover)')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'var(--accent-primary)')}
          >
            <Sparkles size={16} />
            Ask AI-CFO About This Transaction
            <ArrowRight size={15} />
          </button>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', marginTop: 8 }}>
            Grounded in deterministic tool evidence & audit trails
          </div>
        </div>
      </div>
    </div>
  );
};
