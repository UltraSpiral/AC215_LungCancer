import { GlassCard } from '../components/ui';
import { AnalysisPanel } from '../features/analysis/AnalysisPanel';
import { ERROR_FIXTURE, LOW_TISSUE_FIXTURE, PREDICTION_FIXTURES } from '../mocks/predictions';
import { SAMPLE_SLIDES } from '../mocks/sampleSlides';
import type { AnalysisState, SlideSelection } from '../state/types';
import styles from './KitchenSink.module.css';

const noop = () => {};
const [luad, lusc, normal] = SAMPLE_SLIDES;
const startedAt = Date.now() - 134_000;

const STATES: Array<{ name: string; slide: SlideSelection | null; analysis: AnalysisState }> = [
  { name: 'idle · no slide', slide: null, analysis: { phase: 'idle' } },
  {
    name: 'idle · slide chosen',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: { phase: 'idle' },
  },
  {
    name: 'uploading',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: { phase: 'uploading', progress: 0.42, bytesTotal: luad.sizeBytes },
  },
  {
    name: 'analysing · queued',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: { phase: 'analysing', jobId: 'job_7f3a9c21e0', status: 'queued', progress: null, stage: null, startedAt },
  },
  {
    name: 'analysing · running',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: {
      phase: 'analysing',
      jobId: 'job_7f3a9c21e0',
      status: 'running',
      progress: 0.58,
      stage: 'Analysing tissue regions',
      startedAt,
    },
  },
  ...[luad, lusc, normal].map((sample) => ({
    name: `result · ${sample.id}`,
    slide: { kind: 'sample' as const, sample, receivedAt: startedAt },
    analysis: {
      phase: 'result' as const,
      jobId: 'job_7f3a9c21e0',
      prediction: PREDICTION_FIXTURES[sample.id],
      startedAt,
      finishedAt: Date.now(),
    },
  })),
  {
    name: 'result · low tissue + unknown code',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: {
      phase: 'result',
      jobId: 'job_7f3a9c21e0',
      prediction: { ...LOW_TISSUE_FIXTURE, quality_warnings: ['fewer_than_32_tiles', 'some_future_check'] },
      startedAt,
      finishedAt: Date.now(),
    },
  },
  {
    name: 'error',
    slide: { kind: 'sample', sample: luad, receivedAt: startedAt },
    analysis: { phase: 'error', reason: ERROR_FIXTURE.reason, during: 'analysis', jobId: 'job_7f3a9c21e0' },
  },
];

/** Every AnalysisPanel state side by side, at the Figma panel size (362 wide). */
export function PanelStates() {
  return (
    <div className={styles.panelGrid}>
      {STATES.map((s) => (
        <figure key={s.name} className={styles.panelFigure}>
          <figcaption>{s.name}</figcaption>
          <GlassCard className={styles.panelCard}>
            <AnalysisPanel
              slide={s.slide}
              analysis={s.analysis}
              picker={<p style={{ padding: 20, color: 'var(--color-text-secondary)' }}>[slide picker]</p>}
              onAnalyse={noop}
              onCancel={noop}
              onRetry={noop}
              onChooseAnother={noop}
            />
          </GlassCard>
        </figure>
      ))}
    </div>
  );
}
