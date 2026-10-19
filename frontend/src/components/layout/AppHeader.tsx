import { Chip, SegmentedNav } from '../ui';
import styles from './AppHeader.module.css';

const NAV = [
  // Queue and Report are outside the MVP; shown for orientation, not navigable.
  { id: 'queue', label: 'Queue · 11', disabled: true },
  { id: 'review', label: 'Review' },
  { id: 'report', label: 'Report', disabled: true },
];

export function AppHeader() {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <span className={styles.mark} aria-hidden="true" />
        <span className={styles.role}>Remote Pathologist</span>
      </div>

      <SegmentedNav aria-label="Sections" items={NAV} activeId="review" />

      <div className={styles.user}>
        <Chip tone="glass" size="xs">
          Pathologist
        </Chip>
        <Chip tone="glass" size="xs">
          Dr. A. Okafor
        </Chip>
      </div>
    </header>
  );
}
