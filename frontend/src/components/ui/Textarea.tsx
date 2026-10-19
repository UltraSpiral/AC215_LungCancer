import type { TextareaHTMLAttributes } from 'react';
import { cx } from '../../lib/cx';
import styles from './Textarea.module.css';

/** Report / modal field: white @70%, ink @10% stroke, radius 12; focus = blue stroke. */
export function Textarea({ className, ...rest }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cx(styles.field, className)} {...rest} />;
}
