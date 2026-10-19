import type { Job, JobCreated } from '../contracts/inference';

/** What gets analysed: a local .svs, or one of the bundled sample slides. */
export type SlideInput =
  | { kind: 'file'; file: File; caseId?: string }
  | { kind: 'sample'; sampleId: string; sourceFile: string; sizeBytes: number; caseId?: string };

export interface SubmitOptions {
  signal: AbortSignal;
  /** Called as the slide is uploaded. `total` is null when unknown. */
  onUploadProgress: (loaded: number, total: number | null) => void;
}

/**
 * The only way the UI talks to the model. Inference is a long-running job:
 * submit once, then poll `getJob` until it is `done` or `failed`.
 */
export interface InferenceAdapter {
  readonly mode: 'mock' | 'http';
  /** First delay between polls; the runner backs off from here up to `maxPollIntervalMs`. */
  readonly pollIntervalMs: number;
  readonly maxPollIntervalMs: number;
  submitJob(input: SlideInput, options: SubmitOptions): Promise<JobCreated>;
  getJob(jobId: string, options: { signal: AbortSignal }): Promise<Job>;
  /** Best effort; servers may not support cancellation. */
  cancelJob?(jobId: string): Promise<void>;
}

/** Thrown by adapters for failures the user should read (shown verbatim in the panel). */
export class InferenceError extends Error {
  readonly retryable: boolean;
  constructor(message: string, options: { retryable?: boolean; cause?: unknown } = {}) {
    super(message, { cause: options.cause });
    this.name = 'InferenceError';
    this.retryable = options.retryable ?? false;
  }
}
