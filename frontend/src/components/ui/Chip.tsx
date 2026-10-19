import type { HTMLAttributes } from 'react';
import { cx } from '../../lib/cx';
import styles from './Chip.module.css';

export type ChipTone = 'warning' | 'accent' | 'dark' | 'neutral' | 'glass' | 'soft';

interface ChipProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: ChipTone;
  /** md = 28px status chip (12px Medium), sm = 22px tag (11px Medium),
   *  xs = 26px quiet pill (12px Regular, e.g. "Pathologist", "Hide ›") */
  size?: 'md' | 'sm' | 'xs';
  /** 7×7 square status marker before the label (filled, or outlined on dark). */
  dot?: boolean;
}

export function Chip({ tone = 'neutral', size = 'md', dot, className, children, ...rest }: ChipProps) {
  return (
    <span className={cx(styles.chip, styles[tone], styles[size], className)} {...rest}>
      {dot && <span className={styles.dot} aria-hidden="true" />}
      {children}
    </span>
  );
}
