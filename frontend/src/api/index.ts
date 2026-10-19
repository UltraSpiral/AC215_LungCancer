import type { InferenceAdapter } from './adapters/InferenceAdapter';
import { httpAdapter } from './adapters/httpAdapter';
import { mockAdapter } from './adapters/mockAdapter';

export type InferenceMode = 'mock' | 'http';

function resolveMode(): InferenceMode {
  const raw = import.meta.env.VITE_INFERENCE_MODE ?? 'mock';
  if (raw === 'mock' || raw === 'http') return raw;
  console.warn(`VITE_INFERENCE_MODE="${raw}" is not mock|http; using mock.`);
  return 'mock';
}

export const inferenceMode: InferenceMode = resolveMode();

/** The adapter the whole UI uses. Switch with VITE_INFERENCE_MODE=mock|http. */
export const inference: InferenceAdapter = inferenceMode === 'http' ? httpAdapter : mockAdapter;

export { runAnalysis } from './runAnalysis';
export type { AnalysisCallbacks } from './runAnalysis';
export type { InferenceAdapter, SlideInput } from './adapters/InferenceAdapter';
