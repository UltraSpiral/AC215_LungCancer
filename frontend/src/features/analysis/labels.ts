import type { PredictedClass, QualityWarning, QualityWarningCode } from '../../api/contracts/inference';

/**
 * The only place model classes are turned into words. Change copy here.
 */
export const CLASS_LABELS: Record<PredictedClass, string> = {
  non_tumor: 'Non-cancerous tissue',
  adenocarcinoma: 'Cancerous · Adenocarcinoma (LUAD)',
  squamous: 'Cancerous · Squamous cell carcinoma (LUSC)',
};

export function classLabel(c: PredictedClass): string {
  return CLASS_LABELS[c];
}

/** Plain-English wording for the preprocessing QC codes (lungcancer/preprocess.py). */
export const QUALITY_WARNING_LABELS: Record<QualityWarningCode, string> = {
  fewer_than_32_tiles: 'Fewer than 32 tissue tiles were analysed, so the prediction rests on very little tissue.',
  low_fraction_of_grid_passes_tissue_threshold: 'Only a small part of the slide passed the tissue filter.',
  thumbnail_mask_has_fewer_than_4_pixels_across_tile:
    'The tissue mask was too coarse to place tiles precisely; some tissue may have been missed or included in error.',
  native_resolution_coarser_than_requested_output:
    'The slide was scanned at a lower resolution than the model expects; tiles were upsampled.',
  anisotropic_native_resolution_resampled_per_axis:
    'The scan has non-square pixels; tiles were resampled separately on each axis.',
  embedded_icc_profile_present_not_applied:
    'The slide has an embedded colour profile that was not applied; colours may differ slightly from what the model was trained on.',
};

export function qualityWarningLabel(code: QualityWarning): string {
  return (
    (QUALITY_WARNING_LABELS as Record<string, string | undefined>)[code] ?? `Unrecognised quality check (${code}).`
  );
}
