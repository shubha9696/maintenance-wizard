export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Global client-side memory cache for GET requests
const clientCache: Record<string, { data: any; timestamp: number }> = {};

export function getCachedData(key: string): any | null {
  if (typeof window === 'undefined') return null;
  
  // Try memory cache first
  const cached = clientCache[key];
  if (cached) {
    // Return if fresh (within 5 minutes)
    if (Date.now() - cached.timestamp <= 300000) {
      return cached.data;
    }
  }
  
  // Fallback to localStorage for instant hydration of stale data
  try {
    const lsData = localStorage.getItem(`mw_cache_${key}`);
    if (lsData) {
      const parsed = JSON.parse(lsData);
      return parsed.data;
    }
  } catch (e) {
    console.error('Error reading cache from localStorage', e);
  }
  
  return null;
}

export function setCachedData(key: string, data: any): void {
  if (typeof window === 'undefined') return;
  
  clientCache[key] = {
    data,
    timestamp: Date.now()
  };
  
  try {
    localStorage.setItem(`mw_cache_${key}`, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  } catch (e) {
    console.error('Error writing cache to localStorage', e);
  }
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
