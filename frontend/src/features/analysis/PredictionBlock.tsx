import type { PredictedClass } from '../../api/contracts/inference';
import { classLabel } from './labels';
import styles from './AnalysisPanel.module.css';

/** Figma "Suggested diagnosis / Most consistent with adenocarcinoma" block. */
export function PredictionBlock({ predictedClass }: { predictedClass: PredictedClass }) {
  return (
    <section className={styles.block}>
      <p className={styles.eyebrow}>Predicted class</p>
      <h3 className={styles.headline} data-class={predictedClass}>
        {classLabel(predictedClass)}
      </h3>
    </section>
  );
}
