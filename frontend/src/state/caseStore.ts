import { create } from 'zustand';
import { inference, inferenceMode, runAnalysis, type SlideInput } from '../api';
import type { CaseInfo } from '../components/layout/CaseStrip';
import { DEFAULT_CASE, SAMPLE_CASES, UPLOAD_CASE } from '../mocks/cases';
import { SAMPLE_SLIDES, sampleForFilename } from '../mocks/sampleSlides';
import type { AnalysisState, SlideSelection } from './types';

interface CaseStore {
  slide: SlideSelection | null;
  analysis: AnalysisState;

  selectSample: (sampleId: string) => void;
  selectFile: (file: File) => void;
  clearSlide: () => void;
  /** Upload the selected slide and poll its job until a result or error. */
  startAnalysis: () => void;
  cancelAnalysis: () => void;
}

/** `?sample=TCGA-…` preselects a sample slide (handy for demos and screenshots). */
function initialSlide(): SlideSelection | null {
  if (inferenceMode === 'http') return null;
  const id = new URLSearchParams(window.location.search).get('sample');
  const sample = SAMPLE_SLIDES.find((s) => s.id === id);
  return sample ? { kind: 'sample', sample, receivedAt: Date.now() } : null;
}

function inputFor(slide: SlideSelection): SlideInput {
  const caseId = caseInfoFor(slide).caseId;
  if (slide.kind === 'file') return { kind: 'file', file: slide.file, caseId };
  const { id, sourceFile, sizeBytes } = slide.sample;
  return { kind: 'sample', sampleId: id, sourceFile, sizeBytes, caseId };
}

/** The in-flight run; aborting it stops polling and cancels the job. */
let current: AbortController | null = null;

function abortCurrent() {
  current?.abort(new DOMException('Analysis cancelled', 'AbortError'));
  current = null;
}

export const useCaseStore = create<CaseStore>()((set, get) => ({
  slide: initialSlide(),
  analysis: { phase: 'idle' },

  selectSample: (sampleId) => {
    if (inferenceMode === 'http') return;
    const sample = SAMPLE_SLIDES.find((s) => s.id === sampleId);
    if (!sample) return;
    abortCurrent();
    set({ slide: { kind: 'sample', sample, receivedAt: Date.now() }, analysis: { phase: 'idle' } });
  },

  selectFile: (file) => {
    abortCurrent();
    set({
      slide: { kind: 'file', file, sample: inferenceMode === 'http' ? undefined : sampleForFilename(file.name), receivedAt: Date.now() },
      analysis: { phase: 'idle' },
    });
  },

  clearSlide: () => {
    abortCurrent();
    set({ slide: null, analysis: { phase: 'idle' } });
  },

  cancelAnalysis: () => {
    abortCurrent();
    set({ analysis: { phase: 'idle' } });
  },

  startAnalysis: () => {
    const { slide } = get();
    if (!slide) return;
    abortCurrent();
    const controller = new AbortController();
    current = controller;
    // Ignore callbacks from a run that has since been cancelled or replaced.
    const live = () => current === controller;

    const total = slide.kind === 'file' ? slide.file.size : slide.sample.sizeBytes;
    set({ analysis: { phase: 'uploading', progress: 0, bytesTotal: total } });
    let startedAt = Date.now();

    runAnalysis(inference, inputFor(slide), controller.signal, {
      onUploadProgress: (loaded, size) => {
        if (!live()) return;
        set({
          analysis: { phase: 'uploading', progress: size ? loaded / size : null, bytesTotal: size ?? total },
        });
      },
      onJob: (job) => {
        if (!live() || (job.status !== 'queued' && job.status !== 'running')) return;
        const prev = get().analysis;
        if (prev.phase !== 'analysing') startedAt = Date.now();
        set({
          analysis: {
            phase: 'analysing',
            jobId: job.job_id,
            status: job.status,
            progress: job.progress ?? null,
            stage: job.stage ?? null,
            startedAt,
          },
        });
      },
    })
      .then(({ jobId, prediction }) => {
        if (!live()) return;
        current = null;
        const wasUploading = get().analysis.phase === 'uploading';
        set({
          analysis:
            prediction.status === 'success' && jobId
              ? { phase: 'result', jobId, prediction, startedAt, finishedAt: Date.now() }
              : {
                  phase: 'error',
                  reason: prediction.status === 'error' ? prediction.reason : 'No job id was returned.',
                  during: wasUploading ? 'upload' : 'analysis',
                  jobId: jobId ?? undefined,
                },
        });
      })
      .catch(() => {
        // Only reached on abort; cancelAnalysis/select* already reset the state.
      });
  },
}));

/** Case-strip details for the current slide. */
export function caseInfoFor(slide: SlideSelection | null): CaseInfo {
  if (inferenceMode === 'http') {
    return { caseId: 'Preprocessed-slide demo', specimen: 'Whole-slide image', clinic: 'Local research demo' };
  }
  if (!slide) return DEFAULT_CASE;
  if (slide.sample) return SAMPLE_CASES[slide.sample.id] ?? DEFAULT_CASE;
  return UPLOAD_CASE;
}
