import { request } from './client';
import { BatchSummary, ReconciliationRecord, LowConfidenceResponse } from './types';

export async function getBatchSummary(): Promise<BatchSummary> {
  const res = await request<{ success: boolean; data: BatchSummary; error: any }>('/summary');
  return res.data;
}

export async function getReconciliationRecords(): Promise<ReconciliationRecord[]> {
  const res = await request<{ success: boolean; data: { total_records: number; records: ReconciliationRecord[] }; error: any }>('/reconciliation');
  return res.data.records;
}

export async function getTransaction(identifier: string): Promise<ReconciliationRecord> {
  const res = await request<{ success: boolean; data: ReconciliationRecord; error: any }>(`/transactions/${encodeURIComponent(identifier)}`);
  if (!res.success || !res.data) {
    throw new Error(res.error?.message || `Transaction ${identifier} not found`);
  }
  return res.data;
}

export async function getLowConfidenceMatches(): Promise<LowConfidenceResponse> {
  const res = await request<{ success: boolean; data: LowConfidenceResponse; error: any }>('/review-queue');
  return res.data;
}

export async function getExceptions(category?: string): Promise<ReconciliationRecord[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  const res = await request<{ success: boolean; data: { total_exceptions: number; exceptions: ReconciliationRecord[] }; error: any }>(`/exceptions${query}`);
  return res.data.exceptions;
}
