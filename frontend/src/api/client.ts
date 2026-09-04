/**
 * Centralized API client for AI-CFO backend communication.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorText = await res.text();
      let parsedError;
      try {
        parsedError = JSON.parse(errorText);
      } catch {
        parsedError = { message: errorText || `HTTP error ${res.status}` };
      }
      throw new Error(parsedError.detail || parsedError.message || `Request failed with status ${res.status}`);
    }
    return (await res.json()) as T;
  } catch (error: any) {
    console.error(`API request to ${url} failed:`, error);
    throw error;
  }
}
