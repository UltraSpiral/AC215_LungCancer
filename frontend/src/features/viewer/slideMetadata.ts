import { useEffect, useState } from 'react';

/** Written by tools/convert-slides next to each slide's .dzi. */
export interface SlideMetadata {
  id: string;
  sourceFile: string;
  width: number;
  height: number;
  mppX: number | null;
  mppY: number | null;
  objectivePower: number | null;
  vendor: string | null;
  dzi: string;
  thumbnail: string;
  thumbnailWidth: number;
  thumbnailHeight: number;
  tileSize: number;
  overlap: number;
  format: string;
  levels: number;
  tiles: number;
}

export type SlideMetadataState =
  { status: 'loading' } | { status: 'ready'; meta: SlideMetadata } | { status: 'missing'; id: string };

export function metadataUrl(slideId: string): string {
  return `/slides/${encodeURIComponent(slideId)}/metadata.json`;
}

/** Loads /slides/<id>/metadata.json; `missing` if the slide was never converted. */
export function useSlideMetadata(slideId: string | null): SlideMetadataState | null {
  const [state, setState] = useState<{ id: string; value: SlideMetadataState } | null>(null);

  useEffect(() => {
    if (!slideId) return;
    const controller = new AbortController();
    fetch(metadataUrl(slideId), { signal: controller.signal })
      .then(async (res) => {
        // Vite's dev server answers unknown paths with index.html, so check the type too.
        if (!res.ok || !res.headers.get('content-type')?.includes('json')) throw new Error('missing');
        return (await res.json()) as SlideMetadata;
      })
      .then((meta) => setState({ id: slideId, value: { status: 'ready', meta } }))
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        console.warn(`slide metadata for ${slideId} unavailable`, err);
        setState({ id: slideId, value: { status: 'missing', id: slideId } });
      });
    return () => controller.abort();
  }, [slideId]);

  if (!slideId) return null;
  return state?.id === slideId ? state.value : { status: 'loading' };
}
