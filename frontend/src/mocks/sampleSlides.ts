/**
 * The three TCGA slides in frontend/sample-slides/, converted to DZI by tools/convert-slides.
 * `sampleType` is the TCGA barcode's sample code (01A = primary tumour, 11A = solid
 * tissue normal) — real slide metadata, deliberately not the model's answer.
 */
export interface SampleSlide {
  id: string;
  /** Original .svs filename, used to recognise an uploaded copy of a sample. */
  sourceFile: string;
  project: 'TCGA-LUAD' | 'TCGA-LUSC';
  sampleType: 'Primary tumour' | 'Solid tissue normal';
  sizeBytes: number;
}

export const SAMPLE_SLIDES: SampleSlide[] = [
  {
    id: 'TCGA-91-8496',
    sourceFile: 'TCGA-91-8496-01A-01-TS1.a92cfb28-63e4-4853-bc2c-4d614dfebdbf.svs',
    project: 'TCGA-LUAD',
    sampleType: 'Primary tumour',
    sizeBytes: 15_654_923,
  },
  {
    id: 'TCGA-52-7810',
    sourceFile: 'TCGA-52-7810-01A-01-TS1.42a4fb5e-ca1f-4441-bea7-65bfd2eb2f19.svs',
    project: 'TCGA-LUSC',
    sampleType: 'Primary tumour',
    sizeBytes: 9_988_399,
  },
  {
    id: 'TCGA-38-7271',
    sourceFile: 'TCGA-38-7271-11A-01-TS1.0125556f-24d6-4976-94fa-f092ebaa418a.svs',
    project: 'TCGA-LUAD',
    sampleType: 'Solid tissue normal',
    sizeBytes: 16_741_215,
  },
];

export const SAMPLE_ATTRIBUTION = 'The Cancer Genome Atlas (NCI GDC)';

/** Match an uploaded file to a sample by its TCGA patient barcode. */
export function sampleForFilename(name: string): SampleSlide | undefined {
  const barcode = name.match(/TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}/i)?.[0].toUpperCase();
  return barcode ? SAMPLE_SLIDES.find((s) => s.id === barcode) : undefined;
}
