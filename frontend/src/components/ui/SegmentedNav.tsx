import { cx } from '../../lib/cx';
import styles from './SegmentedNav.module.css';

export interface SegmentedNavItem {
  id: string;
  label: string;
  disabled?: boolean;
}

interface SegmentedNavProps {
  items: SegmentedNavItem[];
  activeId: string;
  onSelect?: (id: string) => void;
  'aria-label': string;
}

/** Header tab group: glass pill track with a dark pill on the active tab. */
export function SegmentedNav({ items, activeId, onSelect, ...rest }: SegmentedNavProps) {
  return (
    <nav className={styles.track} aria-label={rest['aria-label']}>
      {items.map((item) => {
        const active = item.id === activeId;
        return (
          <button
            key={item.id}
            type="button"
            className={cx(styles.tab, active && styles.active)}
            aria-current={active ? 'page' : undefined}
            disabled={item.disabled}
            onClick={() => onSelect?.(item.id)}
          >
            {item.label}
          </button>
        );
      })}
    </nav>
  );
}
