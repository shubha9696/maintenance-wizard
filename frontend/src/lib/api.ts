export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Global client-side memory cache for GET requests
const clientCache: Record<string, { data: any; timestamp: number }> = {};

export function getCachedData(key: string): any | null {
  if (typeof window === 'undefined') return null;
  const cached = clientCache[key];
  if (!cached) return null;
  
  // Invalidate cache if older than 5 minutes (300,000 ms)
  if (Date.now() - cached.timestamp > 300000) {
    delete clientCache[key];
    return null;
  }
  
  return cached.data;
}

export function setCachedData(key: string, data: any): void {
  if (typeof window === 'undefined') return;
  clientCache[key] = {
    data,
    timestamp: Date.now()
  };
}

export async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function apiPost(path: string, body: unknown) {
  return apiFetch(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
