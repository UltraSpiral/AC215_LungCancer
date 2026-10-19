import { useRef, useState, type DragEvent } from 'react';
import { cx } from '../../lib/cx';
import { ACCEPTED_EXTENSIONS, isAcceptedSlide } from './accept';
import styles from './SlideDropZone.module.css';

/**
 * Fills its container (the empty slide pane): a file dropped anywhere in it is
 * accepted, and the centred card offers "browse files" as the click path.
 */
export function SlideDropZone({ onFile }: { onFile: (file: File) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [rejected, setRejected] = useState<string | null>(null);

  const accept = (file: File | undefined) => {
    if (!file) return;
    if (!isAcceptedSlide(file)) {
      setRejected(`${file.name} is not a .svs whole-slide image.`);
      return;
    }
    setRejected(null);
    onFile(file);
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    accept(e.dataTransfer.files[0]);
  };

  return (
    <div
      className={styles.area}
      onDragOver={(e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        setDragging(true);
      }}
      onDragLeave={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setDragging(false);
      }}
      onDrop={onDrop}
    >
      <div className={cx(styles.card, dragging && styles.dragging)}>
        <p className={styles.title}>Drop a whole-slide image</p>
        <p className={styles.hint}>
          or{' '}
          <button type="button" className={styles.link} onClick={() => inputRef.current?.click()}>
            browse files
          </button>
        </p>
        <p className={styles.meta}>Aperio .svs · analysed on the model server</p>
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          tabIndex={-1} // reached via "browse files"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          aria-label="Upload a .svs slide"
          onChange={(e) => {
            accept(e.target.files?.[0]);
            e.target.value = '';
          }}
        />
      </div>
      {rejected && (
        <p className={styles.rejected} role="alert">
          {rejected}
        </p>
      )}
    </div>
  );
}
