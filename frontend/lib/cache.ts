/**
 * Simple localStorage cache utilities for dashboard data
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const DEFAULT_STALE_MS = 30 * 1000; // 30 seconds

export function saveToCache<T>(key: string, data: T): void {
  if (typeof window === 'undefined') return;
  try {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
    };
    localStorage.setItem(`btc_cache_${key}`, JSON.stringify(entry));
  } catch {
    // localStorage may be unavailable (SSR, private browsing)
  }
}

export function loadFromCache<T>(key: string): CacheEntry<T> | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(`btc_cache_${key}`);
    if (!raw) return null;
    return JSON.parse(raw) as CacheEntry<T>;
  } catch {
    return null;
  }
}

export function isCacheStale(
  entry: CacheEntry<unknown> | null,
  staleMs: number = DEFAULT_STALE_MS
): boolean {
  if (!entry) return true;
  return Date.now() - entry.timestamp > staleMs;
}

export function formatCacheAge(entry: CacheEntry<unknown> | null): string {
  if (!entry) return 'No cache';
  const ageMs = Date.now() - entry.timestamp;
  const ageSec = Math.floor(ageMs / 1000);
  if (ageSec < 60) return `${ageSec}s ago`;
  const ageMin = Math.floor(ageSec / 60);
  return `${ageMin}m ago`;
}
