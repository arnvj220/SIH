/**
 * Minimal in-memory cache with TTL.
 *
 * Fetch functions check the cache first; writes explicitly bust the relevant
 * key via `invalidate(key)`.
 */
interface Entry<T> {
  value: T;
  expiresAt: number;
}

const store = new Map<string, Entry<unknown>>();

export function cached<T>(
  key: string,
  ttlMs: number,
  fetcher: () => Promise<T>
): Promise<T> {
  const hit = store.get(key) as Entry<T> | undefined;
  if (hit && hit.expiresAt > Date.now()) {
    return Promise.resolve(hit.value);
  }
  return fetcher().then((value) => {
    store.set(key, { value, expiresAt: Date.now() + ttlMs });
    return value;
  });
}

export function invalidate(key: string): void {
  store.delete(key);
}

export function invalidateAll(): void {
  store.clear();
}