import { useRef, type PointerEvent } from 'react';
import styles from './Minimap.module.css';

/** Visible region as fractions of the slide (0–1 on each axis). */
export interface ViewRect {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface MinimapProps {
  src: string;
  /** slide width / height */
  aspect: number;
  view: ViewRect | null;
  /** Pan so the given slide fraction is centred. */
  onNavigate: (fx: number, fy: number) => void;
}

const LONG_SIDE = 133; // Figma minimap: 133×100 for a landscape image
const SHORT_MAX = 100;

function boxFor(aspect: number): { width: number; height: number } {
  if (aspect >= 1) {
    const height = Math.min(SHORT_MAX, LONG_SIDE / aspect);
    return { width: height * aspect, height };
  }
  return { width: LONG_SIDE * aspect, height: LONG_SIDE };
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** Thumbnail navigator: white 2px frame, blue viewport box (Figma "b_mod20.png" minimap). */
export function Minimap({ src, aspect, view, onNavigate }: MinimapProps) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const box = boxFor(aspect);

  const navigate = (e: PointerEvent) => {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return;
    onNavigate(clamp01((e.clientX - r.left) / r.width), clamp01((e.clientY - r.top) / r.height));
  };

  // Clip the viewport box to the thumbnail so it never spills over the frame.
  const rect = view && {
    left: clamp01(view.x),
    top: clamp01(view.y),
    right: clamp01(view.x + view.w),
    bottom: clamp01(view.y + view.h),
  };

  return (
    <div className={styles.frame} style={{ width: box.width + 4, height: box.height + 4 }}>
      <div
        ref={ref}
        className={styles.map}
        role="presentation"
        onPointerDown={(e) => {
          dragging.current = true;
          e.currentTarget.setPointerCapture(e.pointerId);
          navigate(e);
        }}
        onPointerMove={(e) => dragging.current && navigate(e)}
        onPointerUp={() => (dragging.current = false)}
        onPointerCancel={() => (dragging.current = false)}
      >
        <img src={src} alt="" draggable={false} className={styles.thumb} />
        {rect && rect.right > rect.left && rect.bottom > rect.top && (
          <div
            className={styles.view}
            style={{
              left: `${rect.left * 100}%`,
              top: `${rect.top * 100}%`,
              width: `${(rect.right - rect.left) * 100}%`,
              height: `${(rect.bottom - rect.top) * 100}%`,
            }}
          />
        )}
      </div>
    </div>
  );
}
