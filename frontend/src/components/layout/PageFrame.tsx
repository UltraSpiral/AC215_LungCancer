import type { ReactNode } from 'react';
import styles from './PageFrame.module.css';

interface PageFrameProps {
  header: ReactNode;
  strip: ReactNode;
  viewer: ReactNode;
  panel: ReactNode;
}

/** Review screen grid: header, case strip, then viewer (fluid) + panel (362px). */
export function PageFrame({ header, strip, viewer, panel }: PageFrameProps) {
  return (
    <div className={styles.frame}>
      {header}
      <main className={styles.main}>
        {strip}
        <div className={styles.grid}>
          <div className={styles.viewer}>{viewer}</div>
          <aside className={styles.panel} aria-label="AI analysis">
            {panel}
          </aside>
        </div>
      </main>
    </div>
  );
}
