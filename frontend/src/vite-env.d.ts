/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** mock (default) | http */
  readonly VITE_INFERENCE_MODE?: string;
  /** Model service base URL, e.g. http://localhost:8000 */
  readonly VITE_API_BASE_URL?: string;
  /** Per-request timeout for JSON calls, ms (default 30000). */
  readonly VITE_API_TIMEOUT_MS?: string;
  /** Mock mode: simulated server run time per job, ms (default 16000). */
  readonly VITE_MOCK_DURATION_MS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
