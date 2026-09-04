import React, { useEffect, useState, useMemo } from 'react';
import { getReconciliationRecords } from '../api/reconciliation';
import { ReconciliationRecord } from '../api/types';
import { StatusBadge } from '../components/Common/StatusBadge';
import { SkeletonLoader } from '../components/Common/SkeletonLoader';
import { TransactionDrawer } from '../components/Reconciliation/TransactionDrawer';
import { Search, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';

interface ReconciliationPageProps {
  onAskAi: (question: string) => void;
}

export const ReconciliationPage: React.FC<ReconciliationPageProps> = ({ onAskAi }) => {
  const [records, setRecords] = useState<ReconciliationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'MATCHED' | 'EXCEPTION'>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');

  // Selected for drawer
  const [selectedRecord, setSelectedRecord] = useState<ReconciliationRecord | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  const fetchRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getReconciliationRecords();
      setRecords(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load reconciliation records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      // Status filter
      if (statusFilter !== 'ALL' && r.status !== statusFilter) return false;

      // Category filter
      if (categoryFilter !== 'ALL' && r.reason !== categoryFilter) return false;

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchInv = r.invoice_id?.toLowerCase().includes(q);
        const matchTxn = r.transaction_id?.toLowerCase().includes(q);
        const matchCust = r.customer?.toLowerCase().includes(q);
        if (!matchInv && !matchTxn && !matchCust) return false;
      }

      return true;
    });
  }, [records, statusFilter, categoryFilter, searchQuery]);

  // Pagination calculations
  const totalPages = Math.ceil(filteredRecords.length / pageSize) || 1;
  const paginatedRecords = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRecords.slice(start, start + pageSize);
  }, [filteredRecords, currentPage]);

  const categories = useMemo(() => {
    const cats = new Set(records.map((r) => r.reason));
    return Array.from(cats);
  }, [records]);

  return (
    <div>
      {/* Controls Bar */}
      <div className="card-section" style={{ padding: '16px 20px', marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Search Input */}
          <div style={{
            position: 'relative',
            flex: '1 1 240px',
          }}>
            <Search size={15} style={{ position: 'absolute', left: 12, top: 10, color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search by invoice ID, transaction ID, customer..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                width: '100%',
                padding: '8px 12px 8px 34px',
                fontSize: 13,
                border: '1px solid var(--border-card)',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-app)',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
          </div>

          {/* Status Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as any);
                setCurrentPage(1);
              }}
              style={{
                padding: '7px 10px',
                fontSize: 12,
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-card)',
                backgroundColor: 'var(--bg-app)',
                color: 'var(--text-primary)',
              }}
            >
              <option value="ALL">All Statuses</option>
              <option value="MATCHED">Matched</option>
              <option value="EXCEPTION">Exception</option>
            </select>
          </div>

          {/* Category Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Category:</span>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                padding: '7px 10px',
                fontSize: 12,
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-card)',
                backgroundColor: 'var(--bg-app)',
                color: 'var(--text-primary)',
              }}
            >
              <option value="ALL">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Reset Filters */}
          {(searchQuery || statusFilter !== 'ALL' || categoryFilter !== 'ALL') && (
            <button
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('ALL');
                setCategoryFilter('ALL');
                setCurrentPage(1);
              }}
              style={{
                fontSize: 12,
                color: 'var(--accent-primary)',
                fontWeight: 600,
                padding: '6px 10px',
              }}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Table Section */}
      <div className="card-section" style={{ padding: 0 }}>
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            Showing <strong>{filteredRecords.length}</strong> of {records.length} transactions
          </span>
          <button
            onClick={fetchRecords}
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

        {loading ? (
          <div style={{ padding: 24 }}>
            <SkeletonLoader lines={8} />
          </div>
        ) : error ? (
          <div style={{ padding: 32, textAlign: 'center', color: '#DC2626' }}>
            {error}
          </div>
        ) : filteredRecords.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
            No reconciliation transactions matched the selected filters.
          </div>
        ) : (
          <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>Transaction ID</th>
                  <th>Customer</th>
                  <th>Invoice Amount</th>
                  <th>Settlement Amount</th>
                  <th>Variance</th>
                  <th>Status</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {paginatedRecords.map((r) => {
                  const isLowConf = r.status === 'MATCHED' && r.reason === 'fee_deduction' && r.deduction_percentage >= 3.0 && r.deduction_percentage <= 4.0;
                  return (
                    <tr
                      key={r.invoice_id}
                      onClick={() => setSelectedRecord(r)}
                      style={{ backgroundColor: isLowConf ? 'rgba(254, 243, 199, 0.25)' : undefined }}
                    >
                      <td className="font-mono" style={{ fontWeight: 600 }}>{r.invoice_id}</td>
                      <td className="font-mono" style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                        {r.transaction_id || 'NONE'}
                      </td>
                      <td style={{ fontWeight: 500 }}>{r.customer}</td>
                      <td className="font-mono">₹{r.invoice_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                      <td className="font-mono">₹{r.settlement_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                      <td className="font-mono" style={{
                        color: r.deduction_percentage > 0 ? (r.deduction_percentage > 3.5 ? '#B91C1C' : '#B45309') : 'var(--text-muted)',
                        fontWeight: r.deduction_percentage > 0 ? 600 : 400,
                      }}>
                        {r.deduction_percentage > 0 ? `${r.deduction_percentage}%` : '0%'}
                      </td>
                      <td>
                        <StatusBadge status={r.status} reason={r.reason} />
                      </td>
                      <td>
                        <span style={{ fontSize: 11, color: 'var(--accent-primary)', fontWeight: 600 }}>
                          Inspect &rarr;
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 20px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: 12,
          color: 'var(--text-secondary)',
        }}>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div style={{ display: 'flex', gap: 6 }}>
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              style={{
                padding: '5px 10px',
                border: '1px solid var(--border-card)',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-app)',
                opacity: currentPage === 1 ? 0.4 : 1,
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <ChevronLeft size={14} /> Previous
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              style={{
                padding: '5px 10px',
                border: '1px solid var(--border-card)',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-app)',
                opacity: currentPage === totalPages ? 0.4 : 1,
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Transaction Slide-Over Detail Drawer */}
      <TransactionDrawer
        transaction={selectedRecord}
        onClose={() => setSelectedRecord(null)}
        onAskAi={(q) => {
          setSelectedRecord(null);
          onAskAi(q);
        }}
      />
    </div>
  );
};
