/**
 * Panel sections from Figma Screen 2 that the MVP deliberately does NOT render.
 * They are typed here so the panel has named slots to grow into; nothing in the
 * MVP reads or displays them.
 *
 * - confidence   ← class_probabilities exist in the contract but are uncalibrated
 *                  (probabilities_calibrated: false), so no % is shown.
 * - heatmap      ← analyzed_tiles_overlay in the contract; viewer layer not built yet.
 * - tumorArea, regions, flags, subtypePatterns, review: not produced by the model yet.
 *   (Figma's "Subtype probabilities" are adenocarcinoma growth patterns —
 *   acinar/papillary/solid/lepidic/micropapillary — not LUAD vs LUSC.)
 */
export interface DeferredPanelSections {
  confidence?: { value: number; threshold: number };
  tumorAreaFraction?: number;
  heatmap?: { overlayUrl: string; opacity: number };
  regions?: Array<{ id: number; label: string; score: number; bbox: [number, number, number, number] }>;
  flags?: Array<{ id: string; title: string; detail: string }>;
  subtypePatterns?: Array<{ pattern: string; fraction: number }>;
  review?: { decision: 'agree' | 'disagree'; reason?: string; diagnosis?: string };
}

/** Feature switches for the slots above. All off in the MVP. */
export const DEFERRED_SECTIONS_ENABLED: Record<keyof DeferredPanelSections, false> = {
  confidence: false,
  tumorAreaFraction: false,
  heatmap: false,
  regions: false,
  flags: false,
  subtypePatterns: false,
  review: false,
};
