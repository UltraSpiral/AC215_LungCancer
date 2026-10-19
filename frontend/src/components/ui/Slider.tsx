import type { CSSProperties } from 'react';
import styles from './Slider.module.css';

interface SliderProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  onChange: (value: number) => void;
  format?: (value: number) => string;
}

/** Labelled 120px range input with a mono readout (Figma "Opacity" control). */
export function Slider({ label, value, min = 0, max = 100, onChange, format = (v) => `${v}%` }: SliderProps) {
  const fill = ((value - min) / (max - min)) * 100;
  return (
    <label className={styles.root}>
      <span className={styles.label}>{label}</span>
      <input
        className={styles.input}
        type="range"
        min={min}
        max={max}
        value={value}
        style={{ '--fill': `${fill}%` } as CSSProperties}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <span className={styles.value}>{format(value)}</span>
    </label>
  );
}
