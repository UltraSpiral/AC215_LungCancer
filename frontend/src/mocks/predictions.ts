import type { PredictionFailure, PredictionSuccess } from '../api/contracts/inference';

/**
 * prediction.json fixtures, one per sample slide plus an error. Shapes follow
 * src/api/contracts/inference.ts exactly. Values are illustrative, NOT model output:
 * tile counts are sized to each slide's tissue area at 224 px / 0.5 µm/px.
 * quality_warnings use only the real codes from lungcancer/preprocess.py.
 */
export const MOCK_MODEL_IDENTIFIER = 'uni2h-logreg-lung3-v0.1';

export const PREDICTION_FIXTURES: Record<string, PredictionSuccess> = {
  'TCGA-91-8496': {
    status: 'success',
    predicted_class: 'adenocarcinoma',
    class_probabilities: { non_tumor: 0.04, adenocarcinoma: 0.87, squamous: 0.09 },
    probabilities_calibrated: false,
    tiles_analyzed: 412,
    quality_warnings: ['embedded_icc_profile_present_not_applied'],
    model_identifier: MOCK_MODEL_IDENTIFIER,
  },
  'TCGA-52-7810': {
    status: 'success',
    predicted_class: 'squamous',
    class_probabilities: { non_tumor: 0.06, adenocarcinoma: 0.11, squamous: 0.83 },
    probabilities_calibrated: false,
    tiles_analyzed: 1862,
    quality_warnings: [],
    model_identifier: MOCK_MODEL_IDENTIFIER,
  },
  'TCGA-38-7271': {
    status: 'success',
    predicted_class: 'non_tumor',
    class_probabilities: { non_tumor: 0.91, adenocarcinoma: 0.06, squamous: 0.03 },
    probabilities_calibrated: false,
    tiles_analyzed: 738,
    quality_warnings: [],
    model_identifier: MOCK_MODEL_IDENTIFIER,
  },
};

/**
 * Borderline case next to the error path: a prediction is returned but from very
 * little tissue. Mock serves it for uploads whose filename contains "low-tissue".
 */
export const LOW_TISSUE_FIXTURE: PredictionSuccess = {
  status: 'success',
  predicted_class: 'adenocarcinoma',
  class_probabilities: { non_tumor: 0.31, adenocarcinoma: 0.52, squamous: 0.17 },
  probabilities_calibrated: false,
  tiles_analyzed: 27,
  quality_warnings: ['fewer_than_32_tiles'],
  model_identifier: MOCK_MODEL_IDENTIFIER,
};

/** Returned by the mock for any upload that is not one of the sample slides. */
export const ERROR_FIXTURE: PredictionFailure = {
  status: 'error',
  // Wording is a placeholder: the real error strings come from the model service.
  reason: 'No tissue tiles passed the tissue threshold, so the slide could not be classified.',
};
