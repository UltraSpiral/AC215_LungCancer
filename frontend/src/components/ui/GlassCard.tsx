import type { ElementType, HTMLAttributes } from 'react';
import { cx } from '../../lib/cx';
import styles from './GlassCard.module.css';

interface GlassCardProps extends HTMLAttributes<HTMLElement> {
  /** `card` = white @72% (default); `modal` = white @94% */
  variant?: 'card' | 'modal';
  as?: ElementType;
}

/** Frosted white surface used for every card on the Review screen. */
export function GlassCard({ variant = 'card', as: Tag = 'section', className, ...rest }: GlassCardProps) {
  return <Tag className={cx(styles.card, variant === 'modal' && styles.modal, className)} {...rest} />;
}
