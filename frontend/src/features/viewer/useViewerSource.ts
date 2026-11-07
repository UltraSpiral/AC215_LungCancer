import { SAMPLE_ATTRIBUTION } from '../../mocks/sampleSlides';
import { inferenceMode } from '../../api';
import type { AnalysisState, SlideSelection } from '../../state/types';
import type { ViewerSource } from './SlideViewer';
import { useSlideMetadata } from './slideMetadata';

/**
 * Decide what the viewer pane shows for the selected slide. Only sample slides
 * have Deep Zoom tiles; an uploaded .svs is never decoded in the browser.
 */
export function useViewerSource(
  slide: SlideSelection | null,
  analysis: AnalysisState,
  showHeatmap = false,
): ViewerSource {
  const sampleId = inferenceMode === 'http' ? null : slide?.sample?.id ?? null;
  const meta = useSlideMetadata(sampleId);

  if (!slide) return { kind: 'empty' };

  if (inferenceMode === 'http') {
    const attention = analysis.phase === 'result' ? analysis.prediction.attention : undefined;
    if (attention && showHeatmap) {
      return { kind: 'image', url: attention.heatmap, legend: true,
        alt: 'Supplied slide with analysed tiles coloured by attention rank',
        detail: `Attention model: ${attention.tiles_analyzed} analysed tiles coloured by rank within this slide; white outline = top ${attention.top_tiles_outlined}. ${attention.disclaimer}` };
    }
    if (analysis.phase === 'result' && analysis.prediction.analyzed_tiles_overlay) {
      return { kind: 'image', url: analysis.prediction.analyzed_tiles_overlay,
        detail: `${analysis.prediction.tiles_analyzed} previously analyzed tile locations. These marks show sampling locations, not a tumor heatmap.` };
    }
    return { kind: 'message', title: 'Preview follows a supported result',
      detail: 'The supplied slide is matched by its file contents. Analyzed locations appear after classification; other slides return no prediction.' };
  }

  if (!sampleId) {
    return {
      kind: 'message',
      title: 'Preview not available for uploaded slides',
      detail: `${slide.kind === 'file' ? slide.file.name : 'This slide'} is analysed on the model server. Browsers can't display .svs files, so only the bundled sample slides have a Deep Zoom preview.`,
    };
  }
  if (!meta || meta.status === 'loading') return { kind: 'loading' };
  if (meta.status === 'missing') {
    return {
      kind: 'message',
      title: 'Slide tiles not generated',
      detail: `No Deep Zoom tiles for ${sampleId}. Run (from frontend/): uv run tools/convert-slides/convert.py`,
    };
  }
  return { kind: 'dzi', meta: meta.meta, attribution: SAMPLE_ATTRIBUTION };
}
