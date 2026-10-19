import { formatBytes } from '../../lib/formatters';
import { SAMPLE_SLIDES } from '../../mocks/sampleSlides';
import styles from './SamplePicker.module.css';

/** Idle-state panel content: the bundled sample slides. Uploads go through the viewer's drop zone. */
export function SamplePicker({ onSample }: { onSample: (sampleId: string) => void }) {
  return (
    <>
      <section className={styles.block}>
        <p className={styles.eyebrow}>No slide selected</p>
        <h3 className={styles.headline}>Choose a slide to analyse</h3>
      </section>

      <section className={styles.samples} aria-labelledby="sample-slides-title">
        <h4 id="sample-slides-title" className={styles.samplesTitle}>
          Sample slides · {SAMPLE_SLIDES.length}
        </h4>
        <ul className={styles.sampleList}>
          {SAMPLE_SLIDES.map((s) => (
            <li key={s.id}>
              <button type="button" className={styles.sample} onClick={() => onSample(s.id)}>
                <img className={styles.thumb} src={`/slides/${s.id}/thumbnail.jpg`} alt="" />
                <span className={styles.sampleText}>
                  <span className={styles.sampleId}>{s.id}</span>
                  <span className={styles.sampleDetail}>
                    {s.project} · {s.sampleType} · {formatBytes(s.sizeBytes)}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
