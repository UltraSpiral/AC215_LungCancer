import { useId } from 'react';
import styles from './Toggle.module.css';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  /** Muted trailing note, e.g. "(low confidence)". */
  note?: string;
  disabled?: boolean;
}

/** 30×16 switch with a 12px rounded-square knob (Figma layer toggles). */
export function Toggle({ checked, onChange, label, note, disabled }: ToggleProps) {
  const id = useId();
  return (
    <label className={styles.root} htmlFor={id} data-disabled={disabled || undefined}>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        className={styles.track}
        onClick={() => onChange(!checked)}
      >
        <span className={styles.knob} />
      </button>
      <span className={styles.label}>{label}</span>
      {note && <span className={styles.note}>{note}</span>}
    </label>
  );
}
