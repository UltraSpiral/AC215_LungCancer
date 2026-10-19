import type { CaseInfo } from '../components/layout/CaseStrip';

/**
 * Case-strip fixtures. Field layout and copy style follow Figma Screen 2
 * (LH-2026-0417, Ridgeway Rural Clinic…); specimen reflects what the TCGA
 * "TS1" slides actually are (frozen sections of a lung resection).
 */
export const DEFAULT_CASE: CaseInfo = {
  caseId: 'LH-2026-0417',
  specimen: 'Lung biopsy',
  clinic: 'Ridgeway Rural Clinic',
};

export const SAMPLE_CASES: Record<string, CaseInfo> = {
  'TCGA-91-8496': {
    caseId: 'LH-2026-0417',
    specimen: 'Lung resection (frozen)',
    clinic: 'Ridgeway Rural Clinic',
  },
  'TCGA-52-7810': {
    caseId: 'LH-2026-0421',
    specimen: 'Lung resection (frozen)',
    clinic: 'Kerio Valley Health Post',
  },
  'TCGA-38-7271': {
    caseId: 'LH-2026-0422',
    specimen: 'Lung resection (frozen)',
    clinic: 'Ridgeway Rural Clinic',
  },
};

/** Case shown for a slide uploaded from disk (no fixture to match). */
export const UPLOAD_CASE: CaseInfo = {
  caseId: 'LH-2026-0430',
  specimen: 'Lung specimen',
  clinic: 'Uploaded from this device',
};
