import { AppHeader } from '../components/layout/AppHeader';
import { CaseStrip } from '../components/layout/CaseStrip';
import { PageFrame } from '../components/layout/PageFrame';
import { GlassCard } from '../components/ui';
import { AnalysisPanel } from '../features/analysis/AnalysisPanel';
import { StatusChip } from '../features/analysis/StatusChip';
import { SamplePicker } from '../features/upload/SamplePicker';
import { SlideDropZone } from '../features/upload/SlideDropZone';
import { SlideViewer } from '../features/viewer/SlideViewer';
import { useViewerSource } from '../features/viewer/useViewerSource';
import { formatEastern } from '../lib/formatters';
import { useNow } from '../lib/useNow';
import { caseInfoFor, useCaseStore } from '../state/caseStore';

/** Review screen (Figma Screen 2), MVP subset. */
export function ReviewPage() {
  const slide = useCaseStore((s) => s.slide);
  const analysis = useCaseStore((s) => s.analysis);
  const selectSample = useCaseStore((s) => s.selectSample);
  const selectFile = useCaseStore((s) => s.selectFile);
  const clearSlide = useCaseStore((s) => s.clearSlide);
  const startAnalysis = useCaseStore((s) => s.startAnalysis);
  const cancelAnalysis = useCaseStore((s) => s.cancelAnalysis);
  const source = useViewerSource(slide);
  // Before a slide arrives, show the live Eastern clock; afterwards, when it was received.
  const now = useNow(1_000);

  return (
    <PageFrame
      header={<AppHeader />}
      strip={
        <CaseStrip
          info={caseInfoFor(slide)}
          received={formatEastern(slide?.receivedAt ?? now)}
          status={<StatusChip analysis={analysis} />}
        />
      }
      viewer={
        <GlassCard>
          <SlideViewer source={source} emptyContent={<SlideDropZone onFile={selectFile} />} />
        </GlassCard>
      }
      panel={
        <GlassCard>
          <AnalysisPanel
            slide={slide}
            analysis={analysis}
            picker={<SamplePicker onSample={selectSample} />}
            onAnalyse={startAnalysis}
            onCancel={cancelAnalysis}
            onRetry={startAnalysis}
            onChooseAnother={clearSlide}
          />
        </GlassCard>
      }
    />
  );
}
