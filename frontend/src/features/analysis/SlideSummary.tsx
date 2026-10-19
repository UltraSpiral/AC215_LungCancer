import { formatBytes } from '../../lib/formatters';
import type { SlideSelection } from '../../state/types';
import styles from './AnalysisPanel.module.css';

function describe(slide: SlideSelection): { name: string; detail: string } {
  if (slide.kind === 'file') {
    return { name: slide.file.name, detail: `Uploaded file · ${formatBytes(slide.file.size)}` };
  }
  const s = slide.sample;
  return { name: s.id, detail: `${s.project} · ${s.sampleType} · ${formatBytes(s.sizeBytes)}` };
}

/** One-row summary of the selected slide (Figma "Top regions" row style). */
export function SlideSummary({ slide }: { slide: SlideSelection }) {
  const { name, detail } = describe(slide);
  return (
    <section className={styles.slideSection} aria-label="Selected slide">
      <div className={styles.slideRow}>
        {slide.sample ? (
          <img className={styles.slideThumb} src={`/slides/${slide.sample.id}/thumbnail.jpg`} alt="" />
        ) : (
          <span className={styles.slideThumb} aria-hidden="true" />
        )}
        <div className={styles.slideText}>
          <p className={styles.slideName} title={name}>
            {name}
          </p>
          <p className={styles.slideDetail}>{detail}</p>
        </div>
      </div>
    </section>
  );
}
