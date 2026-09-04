import { request } from './client';
import { UsageStats } from './types';

export async function getUsageStats(): Promise<UsageStats> {
  return await request<UsageStats>('/usage');
}
