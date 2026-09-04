import { request } from './client';
import { AskResponse } from './types';

export async function askQuestion(question: string): Promise<AskResponse> {
  return await request<AskResponse>('/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}
