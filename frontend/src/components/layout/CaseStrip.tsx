import type { ReactNode } from 'react';
import { GlassCard } from '../ui';
import styles from './CaseStrip.module.css';

export interface CaseInfo {
  caseId: string;
  specimen: string;
  clinic: string;
}

interface CaseStripProps {
  info: CaseInfo;
  /** Pre-formatted received time. */
  received: string;
  /** Trailing status chip (analysis state). */
  status?: ReactNode;
}

export function CaseStrip({ info, received, status }: CaseStripProps) {
  const fields: Array<[string, string]> = [
    ['Specimen', info.specimen],
    ['Sending clinic', info.clinic],
    ['Received', received],
  ];
  return (
    <GlassCard className={styles.strip} aria-label="Case details">
      <h1 className={styles.caseId}>{info.caseId}</h1>
      <dl className={styles.fields}>
        {fields.map(([label, value]) => (
          <div key={label} className={styles.field}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      {status && <div className={styles.chips}>{status}</div>}
    </GlassCard>
  );
}
