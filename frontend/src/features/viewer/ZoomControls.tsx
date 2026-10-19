import { Button } from '../../components/ui';
import styles from './ZoomControls.module.css';

interface ZoomControlsProps {
  magnification: string;
  onZoomOut: () => void;
  onZoomIn: () => void;
  onFit: () => void;
  disabled?: boolean;
}

/** Figma: glass pill "− 10× +" (136×38) followed by a "Fit" pill. */
export function ZoomControls({ magnification, onZoomOut, onZoomIn, onFit, disabled }: ZoomControlsProps) {
  return (
    <div className={styles.root}>
      <div className={styles.pill} role="group" aria-label="Zoom">
        <button type="button" className={styles.step} onClick={onZoomOut} disabled={disabled} aria-label="Zoom out">
          −
        </button>
        <output className={styles.readout} aria-live="polite" aria-label="Magnification">
          {magnification}
        </output>
        <button type="button" className={styles.step} onClick={onZoomIn} disabled={disabled} aria-label="Zoom in">
          +
        </button>
      </div>
      <Button variant="glass" size="sm" onClick={onFit} disabled={disabled}>
        Fit
      </Button>
    </div>
  );
}
