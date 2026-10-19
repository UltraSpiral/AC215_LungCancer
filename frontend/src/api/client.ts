import { InferenceError } from './adapters/InferenceAdapter';

const DEFAULT_TIMEOUT_MS = 30_000;

export const apiConfig = {
  baseUrl: (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, ''),
  /** Per-request timeout for JSON calls (not the upload, which can take much longer). */
  timeoutMs: Number(import.meta.env.VITE_API_TIMEOUT_MS) || DEFAULT_TIMEOUT_MS,
};

export function apiUrl(path: string): string {
  return `${apiConfig.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
}

/** Pull a human-readable message out of an error body (FastAPI `detail`, or `error`/`reason`). */
export function errorMessageFrom(body: unknown, fallback: string): string {
  if (typeof body === 'object' && body !== null) {
    const b = body as Record<string, unknown>;
    for (const key of ['detail', 'error', 'reason', 'message']) {
      if (typeof b[key] === 'string' && b[key]) return b[key] as string;
    }
  }
  return fallback;
}

/** fetch + JSON with a timeout, combined with the caller's abort signal. */
export async function requestJson<T = unknown>(
  path: string,
  init: RequestInit & { signal?: AbortSignal } = {},
): Promise<T> {
  const timeout = AbortSignal.timeout(apiConfig.timeoutMs);
  const signal = init.signal ? AbortSignal.any([init.signal, timeout]) : timeout;

  let res: Response;
  try {
    res = await fetch(apiUrl(path), { ...init, signal, headers: { Accept: 'application/json', ...init.headers } });
  } catch (err) {
    if (init.signal?.aborted) throw err;
    if (timeout.aborted) {
      throw new InferenceError(`The model server did not respond within ${apiConfig.timeoutMs / 1000} s.`, {
        retryable: true,
        cause: err,
      });
    }
    throw new InferenceError(`Can't reach the model server at ${apiConfig.baseUrl}.`, { retryable: true, cause: err });
  }

  const body: unknown = await res.json().catch(() => null);
  if (!res.ok) {
    throw new InferenceError(errorMessageFrom(body, `The model server returned HTTP ${res.status}.`), {
      retryable: res.status >= 500 || res.status === 429,
    });
  }
  return body as T;
}
