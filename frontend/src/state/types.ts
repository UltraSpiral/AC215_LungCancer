import type { PredictionSuccess } from '../api/contracts/inference';
import type { SampleSlide } from '../mocks/sampleSlides';

/** The slide the pathologist has picked. */
export type SlideSelection =
  | { kind: 'sample'; sample: SampleSlide; receivedAt: number }
  /** A local .svs. `sample` is set when its filename matches a sample, which gives us a DZI preview. */
  | { kind: 'file'; file: File; sample?: SampleSlide; receivedAt: number };

/**
 * Analysis lifecycle. `analysing` is a server-side job that can run for
 * minutes; it is polled, not awaited as one request.
 */
export type AnalysisState =
  | { phase: 'idle' }
  | { phase: 'uploading'; progress: number | null; bytesTotal: number | null }
  | {
      phase: 'analysing';
      jobId: string;
      status: 'queued' | 'running';
      progress: number | null;
      stage: string | null;
      startedAt: number;
    }
  | { phase: 'result'; jobId: string; prediction: PredictionSuccess; startedAt: number; finishedAt: number }
  | { phase: 'error'; reason: string; during: 'upload' | 'analysis'; jobId?: string };

export type AnalysisPhase = AnalysisState['phase'];
