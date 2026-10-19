import OpenSeadragon from 'openseadragon';
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { formatInt, formatMagnification } from '../../lib/formatters';
import { Minimap, type ViewRect } from './Minimap';
import type { SlideMetadata } from './slideMetadata';
import styles from './SlideViewer.module.css';
import { ZoomControls } from './ZoomControls';

/** What the pane should show. Only `dzi` renders tiles; the rest are messages. */
export type ViewerSource =
  | { kind: 'empty' }
  | { kind: 'loading' }
  | { kind: 'dzi'; meta: SlideMetadata; attribution?: string }
  | { kind: 'message'; title: string; detail: ReactNode };

interface SlideViewerProps {
  source: ViewerSource;
  /** Rendered in the pane when no slide is selected (e.g. the drop zone). */
  emptyContent?: ReactNode;
}

/** −/+ step between standard objective magnifications. */
const MAGNIFICATION_STOPS = [1.25, 2.5, 5, 10, 20, 40, 80];

function nextStop(current: number, direction: 1 | -1): number {
  const stops = direction > 0 ? MAGNIFICATION_STOPS : [...MAGNIFICATION_STOPS].reverse();
  const tolerance = 1.05;
  const stop = stops.find((m) => (direction > 0 ? m > current * tolerance : m < current / tolerance));
  return stop ?? current * (direction > 0 ? 2 : 0.5);
}

export function SlideViewer({ source, emptyContent }: SlideViewerProps) {
  const meta = source.kind === 'dzi' ? source.meta : null;
  const { viewerRef, containerRef, magnification, view, failed } = useOpenSeadragon(meta);

  const step = useCallback(
    (direction: 1 | -1) => {
      const viewport = viewerRef.current?.viewport;
      if (!viewport) return;
      if (meta?.objectivePower && magnification) {
        const target = nextStop(magnification, direction) / meta.objectivePower; // image zoom
        viewport.zoomTo(viewport.imageToViewportZoom(target));
      } else {
        viewport.zoomBy(direction > 0 ? 2 : 0.5); // no scan magnification: plain doubling
      }
      viewport.applyConstraints();
    },
    [viewerRef, meta, magnification],
  );

  const fit = useCallback(() => viewerRef.current?.viewport.goHome(), [viewerRef]);

  const navigate = useCallback(
    (fx: number, fy: number) => {
      const viewport = viewerRef.current?.viewport;
      if (!viewport || !meta) return;
      viewport.panTo(new OpenSeadragon.Point(fx, (fy * meta.height) / meta.width));
    },
    [viewerRef, meta],
  );

  const ready = !!meta && !failed;

  return (
    <div className={styles.root}>
      <div className={styles.toolbar}>
        <ZoomControls
          magnification={ready && magnification ? formatMagnification(magnification) : '—'}
          onZoomOut={() => step(-1)}
          onZoomIn={() => step(1)}
          onFit={fit}
          disabled={!ready}
        />
      </div>

      <div className={styles.pane}>
        {/* OSD owns this element's children; React never renders into it. */}
        <div ref={containerRef} className={styles.osd} hidden={!meta} aria-label="Slide image" />
        {ready && (
          <>
            <div className={styles.label}>
              <span>Original</span>
              <span className={styles.labelMag}>{magnification ? formatMagnification(magnification) : '—'}</span>
            </div>
            <Minimap src={meta.thumbnail} aspect={meta.width / meta.height} view={view} onNavigate={navigate} />
          </>
        )}
        {source.kind === 'empty' && emptyContent
          ? emptyContent
          : source.kind !== 'dzi' && <PaneMessage source={source} />}
        {meta && failed && (
          <PaneMessage
            source={{
              kind: 'message',
              title: 'Slide tiles could not be loaded',
              detail: (
                <>
                  Expected Deep Zoom tiles at <code>{meta.dzi}</code>.
                </>
              ),
            }}
          />
        )}
      </div>

      <div className={styles.caption}>
        {meta ? (
          <>
            <p>
              {[
                meta.objectivePower && `${meta.objectivePower}× objective`,
                meta.mppX && `${meta.mppX} µm/px`,
                `${formatInt(meta.width)} × ${formatInt(meta.height)} px`,
              ]
                .filter(Boolean)
                .join(' · ')}
            </p>
            <p>
              Slide <span className="numeric">{meta.id}</span>
              {source.kind === 'dzi' && source.attribution && ` · ${source.attribution}`}
            </p>
          </>
        ) : (
          <p>&nbsp;</p>
        )}
      </div>
    </div>
  );
}

function PaneMessage({ source }: { source: Exclude<ViewerSource, { kind: 'dzi' }> }) {
  if (source.kind === 'loading') {
    return <div className={styles.message} aria-busy="true" />;
  }
  const title = source.kind === 'empty' ? 'Drag and drop a slide' : source.title;
  const detail = source.kind === 'empty' ? null : source.detail;
  return (
    <div className={styles.message}>
      <p className={styles.messageTitle}>{title}</p>
      {detail && <p className={styles.messageDetail}>{detail}</p>}
    </div>
  );
}

/** Creates one OpenSeadragon viewer per slide and mirrors its zoom/bounds into React state. */
function useOpenSeadragon(meta: SlideMetadata | null) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<OpenSeadragon.Viewer | null>(null);
  const [magnification, setMagnification] = useState<number | null>(null);
  const [view, setView] = useState<ViewRect | null>(null);
  const [failedFor, setFailedFor] = useState<string | null>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element || !meta) return;

    const viewer = OpenSeadragon({
      element,
      tileSources: meta.dzi,
      showNavigationControl: false,
      showNavigator: false,
      animationTime: 0.35,
      blendTime: 0.1,
      springStiffness: 9,
      visibilityRatio: 0.4,
      minZoomImageRatio: 0.6,
      maxZoomPixelRatio: 2,
      constrainDuringPan: true,
      gestureSettingsMouse: { clickToZoom: false, dblClickToZoom: true, scrollToZoom: true },
      gestureSettingsTouch: { pinchToZoom: true, flickEnabled: true },
      preserveImageSizeOnResize: false,
    });
    viewerRef.current = viewer;
    // OSD's canvas is focusable and handles arrow keys / + / −; give it a name.
    viewer.canvas.setAttribute('aria-label', `Slide ${meta.id}. Arrow keys pan, plus and minus zoom.`);

    const sync = () => {
      const viewport = viewer.viewport;
      if (!viewer.world.getItemCount()) return;
      const imageZoom = viewport.viewportToImageZoom(viewport.getZoom(true));
      setMagnification(meta.objectivePower ? meta.objectivePower * imageZoom : null);
      const b = viewport.getBounds(true);
      const aspect = meta.height / meta.width; // viewport units: x ∈ [0,1], y ∈ [0, h/w]
      setView({ x: b.x, y: b.y / aspect, w: b.width, h: b.height / aspect });
    };

    viewer.addHandler('open', sync);
    viewer.addHandler('animation', sync);
    viewer.addHandler('animation-finish', sync);
    viewer.addHandler('resize', sync);
    viewer.addHandler('open-failed', () => setFailedFor(meta.id));

    return () => {
      viewer.destroy();
      viewerRef.current = null;
      setMagnification(null);
      setView(null);
    };
  }, [meta]);

  return { containerRef, viewerRef, magnification, view, failed: !!meta && failedFor === meta.id };
}
