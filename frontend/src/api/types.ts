/**
 * TypeScript API interfaces for AI-CFO Reasoning Layer.
 */

export interface BatchSummary {
  total_invoices: number;
  total_settlements: number;
  matched_invoices: number;
  exception_invoices: number;
  match_rate_percentage: number;
  exception_rate_percentage: number;
  matched_breakdown: Record<string, number>;
  exception_breakdown: Record<string, number>;
  total_invoice_value_inr: number;
  total_settled_value_inr: number;
  total_exception_exposure_inr: number;
  orphan_settlement_count: number;
  total_orphan_settlement_value_inr: number;
  low_confidence_match_count: number;
}

export interface ReconciliationRecord {
  invoice_id: string;
  transaction_id: string;
  customer: string;
  invoice_amount: number;
  settlement_amount: number;
  status: 'MATCHED' | 'EXCEPTION';
  reason: string;
  deduction_percentage: number;
  days_to_settle: number;
  details: string;
  confidence?: 'HIGH_CONFIDENCE' | 'LOW_CONFIDENCE' | 'UNRESOLVED';
  review_recommendation?: string;
}

export interface LowConfidenceMatch {
  invoice_id: string;
  transaction_id: string;
  customer: string;
  invoice_amount: number;
  settled_amount: number;
  deduction_percentage: number;
  tolerance_boundary: number;
  distance_from_boundary: number;
  confidence_level: 'LOW_CONFIDENCE';
  review_recommendation: string;
  reasoning: string;
}

export interface LowConfidenceResponse {
  total_low_confidence_matches: number;
  tolerance_boundary: number;
  boundary_window: string;
  matches: LowConfidenceMatch[];
}

export interface ToolCallTrace {
  name: string;
  arguments: Record<string, any>;
  result: any;
  latency_ms?: number;
}

export interface EvidenceItem {
  invoice_id?: string;
  transaction_id?: string;
  customer?: string;
  invoice_amount?: number;
  settlement_amount?: number;
  amount?: number;
  status?: string;
  reason?: string;
  deduction_percentage?: number;
  distance_from_boundary?: number;
  source?: string;
  [key: string]: any;
}

export interface AskResponse {
  answer: string;
  confidence: 'HIGH_CONFIDENCE' | 'LOW_CONFIDENCE' | 'UNRESOLVED';
  evidence: EvidenceItem[];
  tools_called: ToolCallTrace[];
  usage: UsageStats;
  error: { type: string; message: string } | null;
}

export interface AuditEntry {
  timestamp: string;
  request_id: string;
  question: string;
  tools: ToolCallTrace[];
  answer: string;
  confidence: string;
  evidence: EvidenceItem[];
  error?: { type: string; message: string } | null;
  usage?: Record<string, any>;
}

export interface UsageStats {
  session_start_time?: string;
  calls_this_session: number;
  total_tool_calls: number;
  calls_by_tool: Record<string, number>;
  failed_calls: number;
  average_tools_per_question: number;
  estimated_compute_units: number;
  pricing_tier_usd?: number;
  usd_to_inr_rate?: number;
  estimated_usage_cost_usd?: number;
  estimated_usage_cost_inr?: number;
}
