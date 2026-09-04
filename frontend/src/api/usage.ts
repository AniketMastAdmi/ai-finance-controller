import { request } from './client';
import { UsageStats } from './types';

export async function getUsageStats(): Promise<UsageStats> {
  return await request<UsageStats>('/usage');
}

export async function updatePricingTier(tierUsd: number): Promise<UsageStats> {
  return await request<UsageStats>('/usage/pricing', {
    method: 'POST',
    body: JSON.stringify({ tier_usd: tierUsd }),
  });
}
