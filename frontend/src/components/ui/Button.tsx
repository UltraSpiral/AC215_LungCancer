import type { ButtonHTMLAttributes } from 'react';
import { cx } from '../../lib/cx';
import styles from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'glass';
export type ButtonSize = 'lg' | 'md' | 'sm';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  /** lg = 44px panel action, md = 38px modal action, sm = 35px viewer pill */
  size?: ButtonSize;
  block?: boolean;
}

/** Pill button. Variants map to Figma: Agree (primary), Disagree (secondary),
 *  Cancel (ghost), Fit (glass). */
export function Button({ variant = 'primary', size = 'lg', block, className, type = 'button', ...rest }: ButtonProps) {
  return (
    <button
      type={type}
      className={cx(styles.button, styles[variant], styles[size], block && styles.block, className)}
      {...rest}
    />
  );
}
