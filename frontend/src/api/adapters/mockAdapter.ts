import { ERROR_FIXTURE, LOW_TISSUE_FIXTURE, PREDICTION_FIXTURES } from '../../mocks/predictions';
import { sampleForFilename } from '../../mocks/sampleSlides';
import type { Job, Prediction } from '../contracts/inference';
import { InferenceError, type InferenceAdapter, type SlideInput } from './InferenceAdapter';

/**
 * In-browser stand-in for the model service. Jobs follow a time-based script
 * (queued → pipeline stages → done) so the UI exercises the same submit/poll
 * path as the HTTP adapter. Sample slides map to their fixtures; any other
 * upload resolves to the error fixture (or the low-tissue fixture if its name contains "low-tissue").
 */

/** Total "server" time per job; override with VITE_MOCK_DURATION_MS (e.g. 180000 for realism). */
const RUN_MS = Number(import.meta.env.VITE_MOCK_DURATION_MS) || 16_000;
const QUEUE_MS = Math.min(3_000, RUN_MS * 0.15);
const UPLOAD_BYTES_PER_SEC = 12 * 1024 * 1024;

/** Pipeline stages of the real classifier, with the fraction of run time at which each starts. */
const STAGES: Array<[number, string]> = [
  [0, 'Opening slide'],
  [0.06, 'Detecting tissue'],
  [0.16, 'Tiling tissue at 20×'],
  [0.3, 'Analysing tissue regions'],
  [0.86, 'Aggregating tile embeddings'],
  [0.94, 'Classifying slide'],
];
/** The error fixture fails during tissue detection, as a real "too little tissue" error would. */
const ERROR_AT = 0.14;

interface MockJob {
  submittedAt: number;
  prediction: Prediction;
  cancelled: boolean;
}

const jobs = new Map<string, MockJob>();

function fixtureFor(input: SlideInput): Prediction {
  const id = input.kind === 'sample' ? input.sampleId : sampleForFilename(input.file.name)?.id;
  if (id && PREDICTION_FIXTURES[id]) return PREDICTION_FIXTURES[id];
  if (input.kind === 'file' && /low-tissue/i.test(input.file.name)) return LOW_TISSUE_FIXTURE;
  return ERROR_FIXTURE;
}

const sleep = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    if (signal.aborted) return reject(signal.reason);
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

/** A bit of network jitter so polling behaves like the real thing. */
const latency = () => 80 + Math.random() * 160;

function stageAt(fraction: number): string {
  let stage = STAGES[0][1];
  for (const [start, name] of STAGES) if (fraction >= start) stage = name;
  return stage;
}

export const mockAdapter: InferenceAdapter = {
  mode: 'mock',
  pollIntervalMs: 1_000,
  maxPollIntervalMs: 2_000,

  async submitJob(input, { signal, onUploadProgress }) {
    const total = input.kind === 'file' ? input.file.size : input.sizeBytes;
    const uploadMs = Math.min(4_000, Math.max(1_200, (total / UPLOAD_BYTES_PER_SEC) * 1000));
    const started = performance.now();
    onUploadProgress(0, total);
    for (;;) {
      await sleep(100, signal);
      const f = Math.min(1, (performance.now() - started) / uploadMs);
      onUploadProgress(Math.round(f * total), total);
      if (f >= 1) break;
    }
    await sleep(latency(), signal);

    const jobId = `job_${crypto.randomUUID().replace(/-/g, '').slice(0, 12)}`;
    jobs.set(jobId, { submittedAt: Date.now(), prediction: fixtureFor(input), cancelled: false });
    return { job_id: jobId, status: 'queued' };
  },

  async getJob(jobId, { signal }) {
    await sleep(latency(), signal);
    const job = jobs.get(jobId);
    if (!job) throw new InferenceError(`Unknown job ${jobId}.`);
    if (job.cancelled) return { job_id: jobId, status: 'failed', error: 'Job was cancelled.' };

    const elapsed = Date.now() - job.submittedAt;
    if (elapsed < QUEUE_MS) return { job_id: jobId, status: 'queued', progress: null, stage: null };

    const fraction = (elapsed - QUEUE_MS) / RUN_MS;
    const failsEarly = job.prediction.status === 'error';
    if (fraction >= (failsEarly ? ERROR_AT : 1)) {
      return { job_id: jobId, status: 'done', progress: 1, stage: null, result: job.prediction } satisfies Job;
    }
    return { job_id: jobId, status: 'running', progress: fraction, stage: stageAt(fraction) };
  },

  async cancelJob(jobId) {
    const job = jobs.get(jobId);
    if (job) job.cancelled = true;
  },
};
