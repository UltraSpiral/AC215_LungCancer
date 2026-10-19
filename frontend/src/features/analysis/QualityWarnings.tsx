import type { QualityWarning } from '../../api/contracts/inference';
import styles from './AnalysisPanel.module.css';
import { qualityWarningLabel } from './labels';

/** Preprocessing QC codes as plain-English rows, styled like the Figma "Flags" list (amber dot). */
export function QualityWarnings({ warnings }: { warnings: QualityWarning[] }) {
  return (
    <section className={styles.listSection}>
      <h4 className={styles.listTitle}>Quality warnings · {warnings.length}</h4>
      {warnings.length === 0 ? (
        <p className={styles.listEmpty}>None reported by the pipeline.</p>
      ) : (
        <ul className={styles.list}>
          {warnings.map((code) => (
            <li key={code} className={styles.warning} title={code}>
              <span className={styles.warningDot} aria-hidden="true" />
              <span>{qualityWarningLabel(code)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
