/**
 * Contract with the model service. Mirrors `prediction.json` written by the
 * classifier (UNI2-h tile embeddings + logistic regression, three classes).
 * Reference server implementing it: frontend/tools/stub-model-server/server.py.
 *
 * The UI must never invent a prediction: anything that does not validate as a
 * `PredictionSuccess` is shown as an error.
 */

// ── prediction.json ──────────────────────────────────────────────────────────

export const PREDICTED_CLASSES = ['non_tumor', 'adenocarcinoma', 'squamous'] as const;
export type PredictedClass = (typeof PREDICTED_CLASSES)[number];

/** Fixed QC codes emitted by lungcancer/preprocess.py. Wording for each lives in features/analysis/labels.ts. */
export const QUALITY_WARNING_CODES = [
  'fewer_than_32_tiles',
  'low_fraction_of_grid_passes_tissue_threshold',
  'thumbnail_mask_has_fewer_than_4_pixels_across_tile',
  'native_resolution_coarser_than_requested_output',
  'anisotropic_native_resolution_resampled_per_axis',
  'embedded_icc_profile_present_not_applied',
] as const;
export type QualityWarningCode = (typeof QUALITY_WARNING_CODES)[number];
/** A known code, or a code added by a newer pipeline (kept as-is, shown with a generic label). */
export type QualityWarning = QualityWarningCode | (string & {});

export interface PredictionSuccess {
  status: 'success';
  predicted_class: PredictedClass;
  /** Softmax output of the logistic regression, one entry per class. Not shown in the MVP. */
  class_probabilities: Record<PredictedClass, number>;
  /** Probabilities are raw model scores, not calibrated likelihoods. Always false for this model. */
  probabilities_calibrated: false;
  /** Number of tissue tiles embedded and aggregated for the slide-level call. */
  tiles_analyzed: number;
  /** QC codes from preprocessing (may be empty). Not free text. */
  quality_warnings: QualityWarning[];
  model_identifier: string;
  /** Optional URL/path of an image showing which tiles were analysed. Not shown in the MVP. */
  analyzed_tiles_overlay?: string;
}

export interface PredictionFailure {
  status: 'error';
  reason: string;
}

export type Prediction = PredictionSuccess | PredictionFailure;

// ── job API (POST /jobs, GET /jobs/:id) ──────────────────────────────────────

export type JobStatus = 'queued' | 'running' | 'done' | 'failed';

export interface JobCreated {
  job_id: string;
  status: JobStatus;
}

export interface Job {
  job_id: string;
  status: JobStatus;
  /** 0–1 when the server can estimate it, otherwise null/absent. */
  progress?: number | null;
  /** Short description of the current pipeline step, e.g. "Analysing tissue regions". */
  stage?: string | null;
  /** Present when status === 'done': the prediction.json contents (success or error). */
  result?: unknown;
  /** Present when status === 'failed': the job crashed before writing prediction.json. */
  error?: string | null;
}

// ── validation ───────────────────────────────────────────────────────────────

const isObject = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null;
const isFiniteNumber = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);

export function isPredictedClass(v: unknown): v is PredictedClass {
  return typeof v === 'string' && (PREDICTED_CLASSES as readonly string[]).includes(v);
}

/**
 * Validate an untrusted prediction.json payload. Returns the payload typed as
 * `Prediction`, or a `PredictionFailure` describing why it was rejected.
 */
export function parsePrediction(raw: unknown): Prediction {
  const invalid = (why: string): PredictionFailure => ({
    status: 'error',
    reason: `The model service returned an invalid prediction (${why}).`,
  });

  if (!isObject(raw)) return invalid('not a JSON object');

  if (raw.status === 'error') {
    return {
      status: 'error',
      reason: typeof raw.reason === 'string' && raw.reason.trim() ? raw.reason : 'The model reported an error.',
    };
  }
  if (raw.status !== 'success') return invalid(`unknown status ${JSON.stringify(raw.status)}`);

  if (!isPredictedClass(raw.predicted_class)) {
    return invalid(`unknown predicted_class ${JSON.stringify(raw.predicted_class)}`);
  }
  const probs = raw.class_probabilities;
  if (!isObject(probs) || !PREDICTED_CLASSES.every((c) => isFiniteNumber(probs[c]))) {
    return invalid('class_probabilities must have a number for every class');
  }
  if (raw.probabilities_calibrated !== false) return invalid('probabilities_calibrated must be false');
  if (!isFiniteNumber(raw.tiles_analyzed) || raw.tiles_analyzed < 0 || !Number.isInteger(raw.tiles_analyzed)) {
    return invalid('tiles_analyzed must be a non-negative integer');
  }
  if (!Array.isArray(raw.quality_warnings) || !raw.quality_warnings.every((w) => typeof w === 'string')) {
    return invalid('quality_warnings must be a list of code strings');
  }
  if (typeof raw.model_identifier !== 'string' || !raw.model_identifier.trim()) {
    return invalid('model_identifier is missing');
  }
  if (raw.analyzed_tiles_overlay !== undefined && typeof raw.analyzed_tiles_overlay !== 'string') {
    return invalid('analyzed_tiles_overlay must be a string');
  }

  return {
    status: 'success',
    predicted_class: raw.predicted_class,
    class_probabilities: {
      non_tumor: probs.non_tumor as number,
      adenocarcinoma: probs.adenocarcinoma as number,
      squamous: probs.squamous as number,
    },
    probabilities_calibrated: false,
    tiles_analyzed: raw.tiles_analyzed,
    quality_warnings: raw.quality_warnings as QualityWarning[],
    model_identifier: raw.model_identifier,
    ...(raw.analyzed_tiles_overlay !== undefined && { analyzed_tiles_overlay: raw.analyzed_tiles_overlay }),
  };
}

const JOB_STATUSES: readonly JobStatus[] = ['queued', 'running', 'done', 'failed'];

/** Validate an untrusted GET /jobs/:id body; throws on a malformed envelope. */
export function parseJob(raw: unknown): Job {
  if (!isObject(raw) || typeof raw.job_id !== 'string' || !JOB_STATUSES.includes(raw.status as JobStatus)) {
    throw new Error('Malformed job response from the model service.');
  }
  return {
    job_id: raw.job_id,
    status: raw.status as JobStatus,
    progress: isFiniteNumber(raw.progress) ? Math.min(1, Math.max(0, raw.progress)) : null,
    stage: typeof raw.stage === 'string' ? raw.stage : null,
    result: raw.result,
    error: typeof raw.error === 'string' ? raw.error : null,
  };
}
