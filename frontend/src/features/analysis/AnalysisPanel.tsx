import type { ReactNode } from 'react';
import { inferenceMode } from '../../api';
import { Button, ProgressBar, StatNumber } from '../../components/ui';
import { useNow } from '../../lib/useNow';
import { formatBytes, formatElapsed, formatInt, shortJobId } from '../../lib/formatters';
import type { AnalysisState, SlideSelection } from '../../state/types';
import styles from './AnalysisPanel.module.css';
import { PredictionBlock } from './PredictionBlock';
import { QualityWarnings } from './QualityWarnings';
import { SlideSummary } from './SlideSummary';

export interface AnalysisPanelProps {
  slide: SlideSelection | null;
  analysis: AnalysisState;
  /** Rendered in the idle state when no slide is selected (the uploader). */
  picker: ReactNode;
  onAnalyse: () => void;
  onCancel: () => void;
  onRetry: () => void;
  onChooseAnother: () => void;
}

/**
 * Right-hand "AI analysis" card (Figma Screen 2, 362px). MVP shows only the
 * predicted class, model identifier, tiles analysed and quality warnings.
 * Deferred Figma sections are typed in ./deferred.ts and not rendered.
 */
export function AnalysisPanel(props: AnalysisPanelProps) {
  const { slide, analysis } = props;
  const model = analysis.phase === 'result' ? analysis.prediction.model_identifier : null;

  return (
    <div className={styles.panel}>
      <header className={styles.header}>
        <h2 className={styles.title}>
          AI analysis{' '}
          {model && (
            <span className={styles.model} title={`Model: ${model}`}>
              {model}
            </span>
          )}
        </h2>
      </header>

      <div
        className={styles.body}
        aria-live="polite"
        aria-busy={analysis.phase === 'uploading' || analysis.phase === 'analysing'}
      >
        {inferenceMode === 'http' && (
          <section className={styles.block}>
            <p className={styles.eyebrow}>Preprocessed-slide demo</p>
            <p className={styles.meta}>Uses previously extracted features for the supplied slide. New slides cannot be processed here.</p>
          </section>
        )}
        <PanelBody {...props} />
        {slide && <SlideSummary slide={slide} />}
      </div>

      <PanelActions {...props} />
    </div>
  );
}

function PanelBody({ slide, analysis, picker }: AnalysisPanelProps) {
  switch (analysis.phase) {
    case 'idle':
      if (!slide) return <>{picker}</>;
      return (
        <section className={styles.block}>
          <p className={styles.eyebrow}>Not analysed yet</p>
          <h3 className={styles.headline}>Ready to analyse</h3>
        </section>
      );

    case 'uploading':
      return (
        <section className={styles.block}>
          <p className={styles.eyebrow}>Step 1 of 2 · Uploading</p>
          <h3 className={styles.headline}>Uploading slide</h3>
          <div className={styles.progress}>
            <ProgressBar value={analysis.progress} label="Upload progress" />
            <p className={styles.meta}>
              {analysis.progress !== null && analysis.bytesTotal
                ? `${formatBytes(analysis.progress * analysis.bytesTotal)} of ${formatBytes(analysis.bytesTotal)}`
                : 'Sending…'}
            </p>
          </div>
        </section>
      );

    case 'analysing':
      return <AnalysingBlock state={analysis} />;

    case 'result': {
      const p = analysis.prediction;
      return (
        <>
          <PredictionBlock predictedClass={p.predicted_class} />
          <section className={styles.stats}>
            <StatNumber value={formatInt(p.tiles_analyzed)} label="Tiles analysed" />
          </section>
          <QualityWarnings warnings={p.quality_warnings} />
          {/* Deferred slots (see ./deferred.ts): confidence, tumor area, subtype patterns,
              flags, top regions, heatmap overlay, Agree/Disagree review. */}
        </>
      );
    }

    case 'error':
      return (
        <section className={styles.block}>
          <p className={styles.eyebrow}>No prediction</p>
          <h3 className={styles.headline}>{analysis.during === 'upload' ? 'Upload failed' : 'Analysis failed'}</h3>
          <p className={styles.reason}>{analysis.reason}</p>
          {analysis.jobId && <p className={styles.meta}>Job {shortJobId(analysis.jobId)}</p>}
        </section>
      );
  }
}

function AnalysingBlock({ state }: { state: Extract<AnalysisState, { phase: 'analysing' }> }) {
  const now = useNow(1000);
  const queued = state.status === 'queued';
  return (
    <section className={styles.block}>
      <p className={styles.eyebrow}>Step 2 of 2 · Analysing</p>
      <h3 className={styles.headline}>Classifying tissue</h3>
      <div className={styles.progress}>
        <ProgressBar value={queued ? null : state.progress} label="Analysis progress" />
        <div className={styles.progressMeta}>
          <span>
            {state.stage ?? 'Starting'}
            {state.progress !== null && !queued && ` · ${Math.round(state.progress * 100)}%`}
          </span>
          <span className="numeric">{formatElapsed(now - state.startedAt)}</span>
        </div>
      </div>
    </section>
  );
}

function PanelActions({ slide, analysis, onAnalyse, onCancel, onRetry, onChooseAnother }: AnalysisPanelProps) {
  let actions: ReactNode = null;
  switch (analysis.phase) {
    case 'idle':
      if (slide)
        actions = (
          <>
            <Button block onClick={onAnalyse}>
              Analyse slide
            </Button>
            <Button block variant="secondary" onClick={onChooseAnother}>
              Change slide
            </Button>
          </>
        );
      break;
    case 'uploading':
    case 'analysing':
      actions = (
        <Button block variant="secondary" onClick={onCancel}>
          Cancel analysis
        </Button>
      );
      break;
    case 'result':
      actions = (
        <Button block variant="secondary" onClick={onChooseAnother}>
          Analyse another slide
        </Button>
      );
      break;
    case 'error':
      actions = (
        <>
          <Button block onClick={onRetry}>
            Try again
          </Button>
          <Button block variant="secondary" onClick={onChooseAnother}>
            Change slide
          </Button>
        </>
      );
      break;
  }
  if (!actions) return null;
  return <footer className={styles.actions}>{actions}</footer>;
}
