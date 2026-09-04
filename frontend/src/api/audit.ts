import { request } from './client';
import { AuditEntry } from './types';

export async function getAuditTrail(limit: number = 50, offset: number = 0): Promise<AuditEntry[]> {
  return await request<AuditEntry[]>(`/audit?limit=${limit}&offset=${offset}`);
}
