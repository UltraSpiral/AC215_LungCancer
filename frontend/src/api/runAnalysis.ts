import { InferenceError, type InferenceAdapter, type SlideInput } from './adapters/InferenceAdapter';
import { parsePrediction, type Job, type Prediction } from './contracts/inference';

export interface AnalysisCallbacks {
  onUploadProgress: (loaded: number, total: number | null) => void;
  /** Fired once the job exists, then after every poll. */
  onJob: (job: Job) => void;
}

/** Give up polling after this long; a stuck job must not spin forever. */
const MAX_JOB_MS = 30 * 60_000;
/** Consecutive failed polls tolerated (network blips) before reporting an error. */
const MAX_POLL_FAILURES = 5;

const wait = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = window.setTimeout(resolve, ms);
    signal.addEventListener(
      'abort',
      () => {
        window.clearTimeout(t);
        reject(signal.reason);
      },
      { once: true },
    );
  });

/**
 * Submit a slide and poll its job to completion. Always resolves to a
 * `Prediction` — infrastructure failures become `{ status: 'error' }` — and
 * rejects only when `signal` is aborted.
 */
export async function runAnalysis(
  adapter: InferenceAdapter,
  input: SlideInput,
  signal: AbortSignal,
  callbacks: AnalysisCallbacks,
): Promise<{ jobId: string | null; prediction: Prediction }> {
  let jobId: string | null = null;
  try {
    const created = await adapter.submitJob(input, { signal, onUploadProgress: callbacks.onUploadProgress });
    jobId = created.job_id;
    callbacks.onJob({ job_id: created.job_id, status: created.status, progress: null, stage: null });

    const deadline = Date.now() + MAX_JOB_MS;
    let interval = adapter.pollIntervalMs;
    let failures = 0;

    for (;;) {
      await wait(interval, signal);
      let job: Job;
      try {
        job = await adapter.getJob(jobId, { signal });
        failures = 0;
      } catch (err) {
        if (signal.aborted) throw err;
        const retryable = !(err instanceof InferenceError) || err.retryable;
        if (!retryable || ++failures >= MAX_POLL_FAILURES) throw err;
        continue;
      }
      callbacks.onJob(job);

      if (job.status === 'done') return { jobId, prediction: parsePrediction(job.result) };
      if (job.status === 'failed') {
        return {
          jobId,
          prediction: { status: 'error', reason: job.error || 'The analysis job failed on the server.' },
        };
      }
      if (Date.now() > deadline) {
        return {
          jobId,
          prediction: {
            status: 'error',
            reason: `No result after ${MAX_JOB_MS / 60_000} minutes; job ${jobId} may be stuck.`,
          },
        };
      }
      interval = Math.min(adapter.maxPollIntervalMs, Math.round(interval * 1.5));
    }
  } catch (err) {
    if (signal.aborted) {
      if (jobId) void adapter.cancelJob?.(jobId);
      throw err;
    }
    const reason = err instanceof Error ? err.message : 'Unexpected error while analysing the slide.';
    console.error('analysis failed', err);
    return { jobId, prediction: { status: 'error', reason } };
  }
}
