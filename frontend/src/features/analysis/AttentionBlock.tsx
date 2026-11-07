import type { AttentionResult } from '../../api/contracts/inference';
import { Toggle } from '../../components/ui';
import { classLabel } from './labels';
import styles from './AnalysisPanel.module.css';

interface AttentionBlockProps {
  attention: AttentionResult;
  showHeatmap: boolean;
  onToggleHeatmap: (show: boolean) => void;
}

/** Experimental second opinion from the gated-attention model, with the heatmap switch. */
export function AttentionBlock({ attention, showHeatmap, onToggleHeatmap }: AttentionBlockProps) {
  const f1 = attention.validation_macro_f1;
  return (
    <section className={styles.block}>
      <p className={styles.eyebrow}>Attention model · experimental</p>
      <p className={styles.secondary} data-class={attention.predicted_class}>
        {classLabel(attention.predicted_class)}
      </p>
      <p className={styles.meta}>
        {attention.agrees_with_default_model
          ? 'Agrees with the predicted class above.'
          : 'Differs from the predicted class above; the prediction above is unchanged.'}
      </p>
      <div className={styles.toggleRow}>
        <Toggle label="Attention heatmap" checked={showHeatmap} onChange={onToggleHeatmap} />
      </div>
      <p className={styles.meta}>
        Shows which analysed tiles the model weighted most, ranked within this slide. Not a tumor outline.
        {f1 !== null && ` Validation macro-F1 ${f1.toFixed(2)} on 6 slides.`}
      </p>
    </section>
  );
}
