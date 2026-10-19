import { cx } from '../../lib/cx';
import styles from './StatNumber.module.css';

interface StatNumberProps {
  /** Value (pre-formatted if a string), or null to render the "—" placeholder. */
  value: number | string | null;
  /** Light 24px unit after the numeral, e.g. "%". */
  suffix?: string;
  label: string;
  /** Greys the numeral (Figma: declined-case confidence). */
  muted?: boolean;
}

/** Light 52px numeral with a Light 24px suffix and a 12px caption. */
export function StatNumber({ value, suffix, label, muted }: StatNumberProps) {
  return (
    <div className={styles.root}>
      <p className={cx(styles.number, muted && styles.muted, value === null && styles.empty)}>
        {value === null ? (
          '—'
        ) : (
          <>
            {value}
            {suffix && <span className={styles.suffix}>{suffix}</span>}
          </>
        )}
      </p>
      <p className={styles.label}>{label}</p>
    </div>
  );
}
