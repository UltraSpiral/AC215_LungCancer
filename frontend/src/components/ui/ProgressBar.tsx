import styles from './ProgressBar.module.css';

interface ProgressBarProps {
  /** 0–1, or null for an indeterminate bar. */
  value: number | null;
  label: string;
}

/** 4px bar on an ink @8% track — the Figma probability-bar style. */
export function ProgressBar({ value, label }: ProgressBarProps) {
  const pct = value === null ? undefined : Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div
      className={styles.track}
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      data-indeterminate={pct === undefined || undefined}
    >
      <div className={styles.fill} style={pct === undefined ? undefined : { width: `${pct}%` }} />
    </div>
  );
}
