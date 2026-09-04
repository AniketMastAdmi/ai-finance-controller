import React, { useState } from 'react';
import { askQuestion } from '../api/agent';
import { AskResponse } from '../api/types';
import { ConfidenceBadge } from '../components/Common/ConfidenceBadge';
import { Store, ShieldCheck, Sparkles } from 'lucide-react';

export const PartnerPortalPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'checkout' | 'reconciliation'>('reconciliation');
  const [selectedInvoice, setSelectedInvoice] = useState('INV1060');
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AskResponse | null>(null);

  const samplePartnerOrders = [
    { orderId: 'ORD-9821', invoiceId: 'INV1060', customer: 'Atlas Mobility', amount: '₹145,000.00', status: 'Flagged (Discrepancy)' },
    { orderId: 'ORD-9822', invoiceId: 'INV1001', customer: 'Apex Retail', amount: '₹15,000.00', status: 'Settled (Matched)' },
    { orderId: 'ORD-9823', invoiceId: 'INV1046', customer: 'Vortex Global', amount: '₹88,000.00', status: 'Settled (Borderline Fee)' },
    { orderId: 'ORD-9824', invoiceId: 'INV1056', customer: 'Zenith Retail', amount: '₹62,000.00', status: 'Pending Settlement' },
  ];

  const handleEmbedReconcile = async (invId: string) => {
    setSelectedInvoice(invId);
    setLoading(true);
    setAiResult(null);
    try {
      const res = await askQuestion(`Why didn't ${invId} match? Provide full financial breakdown.`);
      setAiResult(res);
    } catch (e: any) {
      alert(e.message || 'Error executing embedded reconciliation query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Partner Banner demonstrating API Embeddability */}
      <div
        style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: 8,
          padding: '16px 20px',
          marginBottom: 24,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 8,
              backgroundColor: '#EEF2FF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#3B82F6',
            }}
          >
            <Store size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontWeight: 700, fontSize: 16, color: '#0F172A' }}>Acme Cloud Solutions</span>
              <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', backgroundColor: '#F1F5F9', color: '#475569', borderRadius: 12 }}>
                Partner Merchant ID: MID-884920
              </span>
            </div>
            <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
              Demonstrating <strong>Razorpay AI-CFO Reasoning Layer</strong> embedded directly into third-party SMB SaaS & ERP platforms.
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#16A34A', fontWeight: 600 }}>
          <ShieldCheck size={16} /> Embedded AI-CFO API Connected
        </div>
      </div>

      {/* Simulated Merchant Portal Controls */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, borderBottom: '1px solid #E2E8F0', paddingBottom: 10 }}>
        <button
          onClick={() => setActiveTab('reconciliation')}
          style={{
            padding: '6px 14px',
            fontSize: 13,
            fontWeight: 600,
            borderRadius: 6,
            border: 'none',
            backgroundColor: activeTab === 'reconciliation' ? '#0F172A' : 'transparent',
            color: activeTab === 'reconciliation' ? '#FFFFFF' : '#64748B',
            cursor: 'pointer',
          }}
        >
          Merchant Payouts & Reconciliation
        </button>
        <button
          onClick={() => setActiveTab('checkout')}
          style={{
            padding: '6px 14px',
            fontSize: 13,
            fontWeight: 600,
            borderRadius: 6,
            border: 'none',
            backgroundColor: activeTab === 'checkout' ? '#0F172A' : 'transparent',
            color: activeTab === 'checkout' ? '#FFFFFF' : '#64748B',
            cursor: 'pointer',
          }}
        >
          Raw Settlement Adapter Spec
        </button>
      </div>

      {activeTab === 'reconciliation' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 20 }}>
          {/* Merchant Orders Table */}
          <div className="card-section" style={{ margin: 0 }}>
            <div className="card-title">Recent Invoices & Orders</div>
            <div className="card-desc">Click 'Reconcile via AI-CFO' to trigger embedded reasoning</div>

            <div className="table-wrapper" style={{ marginTop: 14 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Order & Invoice</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {samplePartnerOrders.map((ord) => (
                    <tr
                      key={ord.orderId}
                      style={{
                        backgroundColor: selectedInvoice === ord.invoiceId ? 'rgba(30, 58, 138, 0.04)' : undefined,
                      }}
                    >
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{ord.orderId}</div>
                        <div className="font-mono" style={{ fontSize: 11, color: '#64748B' }}>{ord.invoiceId}</div>
                      </td>
                      <td>
                        <div style={{ fontSize: 13 }}>{ord.customer}</div>
                        <div style={{ fontSize: 11, color: ord.status.includes('Flagged') ? '#DC2626' : '#64748B' }}>
                          {ord.status}
                        </div>
                      </td>
                      <td className="font-mono" style={{ fontWeight: 600, fontSize: 13 }}>{ord.amount}</td>
                      <td>
                        <button
                          onClick={() => handleEmbedReconcile(ord.invoiceId)}
                          disabled={loading}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            fontSize: 11,
                            fontWeight: 600,
                            padding: '6px 10px',
                            backgroundColor: selectedInvoice === ord.invoiceId ? 'var(--accent-primary)' : '#FFFFFF',
                            color: selectedInvoice === ord.invoiceId ? '#FFFFFF' : 'var(--accent-primary)',
                            border: '1px solid var(--accent-primary)',
                            borderRadius: 4,
                            cursor: 'pointer',
                          }}
                        >
                          <Sparkles size={12} /> Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Embedded AI-CFO Reasoning Widget */}
          <div className="card-section" style={{ margin: 0, backgroundColor: '#FAF9F5', border: '1px solid #E8E5DC' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, color: 'var(--accent-primary)' }}>
                  Embedded AI-CFO Reasoning Layer
                </span>
              </div>
              {aiResult && <ConfidenceBadge confidence={aiResult.confidence} />}
            </div>

            {loading ? (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: '#64748B' }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>Executing AI-CFO reconciliation analysis...</div>
                <div style={{ fontSize: 12, marginTop: 4 }}>Calling deterministic tools and Gemini reasoning loop</div>
              </div>
            ) : aiResult ? (
              <div>
                <div style={{ fontSize: 12, color: '#64748B', marginBottom: 8 }}>
                  Investigation on <strong>{selectedInvoice}</strong>:
                </div>

                <div
                  style={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E8E5DC',
                    borderRadius: 6,
                    padding: 16,
                    fontSize: 13,
                    lineHeight: 1.6,
                    color: '#1E2022',
                  }}
                >
                  {aiResult.answer}
                </div>

                {aiResult.evidence && aiResult.evidence.length > 0 && (
                  <div style={{ marginTop: 14 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: '#64748B', marginBottom: 6 }}>
                      Verified Evidence Passed to Partner
                    </div>
                    <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: 6, padding: 10, fontSize: 12 }}>
                      {aiResult.evidence.map((ev, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: i < aiResult.evidence.length - 1 ? '1px solid #F1F5F9' : 'none' }}>
                          <span style={{ color: '#64748B' }}>Invoice / Settled:</span>
                          <span className="font-mono" style={{ fontWeight: 600 }}>
                            {ev.invoice_id} • ₹{(ev.invoice_amount || 0).toLocaleString()} vs ₹{(ev.settlement_amount || 0).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{ marginTop: 14, fontSize: 11, color: '#64748B', display: 'flex', justifyContent: 'space-between' }}>
                  <span>API Latency: ~120ms</span>
                  <span>Billed Units: 1 Investigation ($0.10)</span>
                </div>
              </div>
            ) : (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: '#64748B' }}>
                <div style={{ fontSize: 13 }}>Select an invoice on the left to trigger the embedded AI-CFO reasoning widget.</div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Settlement Adapter Integration Demo */
        <div className="card-section">
          <div className="card-title">Razorpay External Settlement Normalizer (adapter.py)</div>
          <div className="card-desc">
            Standardizes disparate gateway payloads (Razorpay, Stripe, Cashfree) into canonical schema for the reconciliation engine.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>Incoming Raw Razorpay Payload:</div>
              <pre style={{ backgroundColor: '#0F172A', color: '#E2E8F0', padding: 12, borderRadius: 6, fontSize: 11, overflowX: 'auto' }}>
{`{
  "id": "setl_1060_live",
  "entity": "settlement",
  "amount": 29000000,
  "currency": "INR",
  "status": "processed",
  "fees": 580000,
  "tax": 104400,
  "utr": "UTR_RAZORPAY_884920",
  "notes": {
    "invoice_id": "INV1060",
    "customer": "Atlas Mobility"
  }
}`}
              </pre>
            </div>

            <div>
              <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>Canonical Engine Representation:</div>
              <pre style={{ backgroundColor: '#0F172A', color: '#38BDF8', padding: 12, borderRadius: 6, fontSize: 11, overflowX: 'auto' }}>
{`{
  "settlement_id": "setl_1060_live",
  "invoice_id": "INV1060",
  "customer": "Atlas Mobility",
  "settled_amount": 290000.0,
  "fee_deducted": 6844.0,
  "gateway_utr": "UTR_RAZORPAY_884920",
  "status": "NORMALIZED_FOR_RECONCILIATION"
}`}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
