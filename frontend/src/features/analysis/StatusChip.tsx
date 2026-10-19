import { Chip } from '../../components/ui';
import type { AnalysisState } from '../../state/types';

/** Case-strip chip in the slot Figma uses for "Confident" / "Declined to predict". */
export function StatusChip({ analysis }: { analysis: AnalysisState }) {
  switch (analysis.phase) {
    case 'idle':
      return null; // nothing to report until an upload/analysis starts
    case 'uploading':
      return (
        <Chip tone="accent" dot>
          Uploading
        </Chip>
      );
    case 'analysing':
      return (
        <Chip tone="accent" dot>
          Analysing
        </Chip>
      );
    case 'result':
      return (
        <Chip tone="accent" dot>
          AI result ready
        </Chip>
      );
    case 'error':
      return (
        <Chip tone="dark" dot>
          No prediction
        </Chip>
      );
  }
}
