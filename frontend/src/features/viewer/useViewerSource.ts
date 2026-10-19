import { SAMPLE_ATTRIBUTION } from '../../mocks/sampleSlides';
import type { SlideSelection } from '../../state/types';
import type { ViewerSource } from './SlideViewer';
import { useSlideMetadata } from './slideMetadata';

/**
 * Decide what the viewer pane shows for the selected slide. Only sample slides
 * have Deep Zoom tiles; an uploaded .svs is never decoded in the browser.
 */
export function useViewerSource(slide: SlideSelection | null): ViewerSource {
  const sampleId = slide?.sample?.id ?? null;
  const meta = useSlideMetadata(sampleId);

  if (!slide) return { kind: 'empty' };

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
