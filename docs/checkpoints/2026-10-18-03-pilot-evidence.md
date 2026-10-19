# Checkpoint 03 — specimen, preparation, and visual evidence review

Verified at 2026-10-18T23:52:27.517809+00:00.

The saved notebook helper displays three class panels covering all nine slides.
The helper was validated to emit three embedded JPEG outputs. Its execution in
the user's open notebook uses the single cell recorded in [COMMANDS.md](../COMMANDS.md).

Factual correction: eight preservation_method values are Unknown and one is OCT
(TCGA-98-A538). None explicitly says Frozen; all nine remain inferred. This
corrects the earlier statement that all nine values were Unknown.

The archive identifier in the evidence below was current at this checkpoint's
timestamp. See [LATEST_BACKUP.md](../LATEST_BACKUP.md) for the latest overall archive.

---

# Detailed pilot evidence

Read-only verification of the existing nine-slide pilot. No downloads, extraction, or training were run.

## Counts and downloaded bytes

| Class | Slides | Independent patients |
|---|---:|---:|
| non_tumor | 3 | 3 |
| adenocarcinoma | 3 | 3 |
| squamous | 3 | 3 |

Actual raw transfer: **1,020,202,701 bytes**. UNI2 checkpoint transfer is separate from raw-slide bytes.

## Specimen linkage and labels

For each file, its associated slide UUID was matched to exactly one slide under exactly one portion/sample/case in the saved raw GDC response. Labels use the linked sample type and project, with primary-diagnosis and barcode consistency checks. Barcode names alone do not assign labels.

**TCGA-33-4547: non_tumor, TCGA-LUSC**
- File `ee261db5-3576-4c52-90b4-4c8e16f7937e` (`TCGA-33-4547-11A-01-TS1.c695e9cf-f318-48b3-a44b-bce6c3a55ae1.svs`).
- Associated slide `c695e9cf-f318-48b3-a44b-bce6c3a55ae1` (`TCGA-33-4547-11A-01-TS1`) → portion `e0caf5e6-a408-4f28-9416-b841e7606c54` (`TCGA-33-4547-11A-01`).
- Linked sample `731fc35e-1d92-4c6a-b698-1375bd15a26c` (`TCGA-33-4547-11A`, **Solid Tissue Normal**) → case `44b1d457-3a50-404e-b54c-ca619262bc2f`.

**TCGA-05-4403: adenocarcinoma, TCGA-LUAD**
- File `f6c36a27-f310-4c96-b5bf-1b6adc5f86f9` (`TCGA-05-4403-01A-01-TS1.4ea11b71-999c-4073-ab56-c6da0eb310f8.svs`).
- Associated slide `4ea11b71-999c-4073-ab56-c6da0eb310f8` (`TCGA-05-4403-01A-01-TS1`) → portion `0b554d07-ce50-40ec-80e5-dfe982ba2e6a` (`TCGA-05-4403-01A-01`).
- Linked sample `44b1d21c-0794-428c-ba01-82812d74da2f` (`TCGA-05-4403-01A`, **Primary Tumor**) → case `ce15f31f-2bad-4485-96fa-495bfa262e66`.

**TCGA-66-2794: squamous, TCGA-LUSC**
- File `bc589465-32ab-406a-94b1-ed48f412f2d9` (`TCGA-66-2794-01A-01-TS1.017a3383-b912-4701-9f9c-dbed66d18deb.svs`).
- Associated slide `017a3383-b912-4701-9f9c-dbed66d18deb` (`TCGA-66-2794-01A-01-TS1`) → portion `e10d4061-6d3f-410d-b98b-66b04d02248a` (`TCGA-66-2794-01A-01`).
- Linked sample `69ef0674-f493-4dfe-84ea-61f28d11ba69` (`TCGA-66-2794-01A`, **Primary Tumor**) → case `8d20352a-6180-40d0-adc0-c87fef854dfa`.

**TCGA-58-8391: non_tumor, TCGA-LUSC**
- File `2908ac70-541d-4521-9cf5-83e1178263ea` (`TCGA-58-8391-11A-01-TS1.26566f10-f8a3-4232-ac87-9f7db7dab873.svs`).
- Associated slide `26566f10-f8a3-4232-ac87-9f7db7dab873` (`TCGA-58-8391-11A-01-TS1`) → portion `0eca9b9c-3bce-41da-81f5-b54129dfa6e0` (`TCGA-58-8391-11A-01`).
- Linked sample `d58f92f5-ace3-4002-b787-51626dcc5d7b` (`TCGA-58-8391-11A`, **Solid Tissue Normal**) → case `9ed5c6fe-24d2-4ee6-88ba-7319c9cfa05e`.

**TCGA-55-A493: adenocarcinoma, TCGA-LUAD**
- File `179c64eb-e8ae-46fa-ba37-a2180dcd4ad2` (`TCGA-55-A493-01A-01-TS1.CA814E99-8668-4FF6-B47E-FE722E30F071.svs`).
- Associated slide `ca814e99-8668-4ff6-b47e-fe722e30f071` (`TCGA-55-A493-01A-01-TS1`) → portion `8fe5e135-9b0b-42c6-8dc0-e92e9f15ba98` (`TCGA-55-A493-01A-11`).
- Linked sample `a08a22c9-5b3a-4748-89af-0fae50522f1b` (`TCGA-55-A493-01A`, **Primary Tumor**) → case `e43a2b72-35c6-4466-9007-ce96caf77ea8`.

**TCGA-98-A538: squamous, TCGA-LUSC**
- File `660c880b-d78b-4b8b-aceb-5dc7c8e4a3f1` (`TCGA-98-A538-01A-01-TS1.E3054C6E-BF8E-4CBB-B66F-6FFB82D2B518.svs`).
- Associated slide `e3054c6e-bf8e-4cbb-b66f-6ffb82d2b518` (`TCGA-98-A538-01A-01-TS1`) → portion `2ee2823b-b240-4c5a-b387-548db3334ec7` (`TCGA-98-A538-01A-11`).
- Linked sample `1804b286-ccd1-42b1-bae4-feab67dbeec0` (`TCGA-98-A538-01A`, **Primary Tumor**) → case `d3e604d1-f8e3-47f7-86fb-104035590af8`.

**TCGA-55-7910: non_tumor, TCGA-LUAD**
- File `615609e8-fb52-41f7-8abe-d0e9d4d14742` (`TCGA-55-7910-11A-01-TS1.bcf0ef2a-e2ab-4451-9245-30b0207484c7.svs`).
- Associated slide `bcf0ef2a-e2ab-4451-9245-30b0207484c7` (`TCGA-55-7910-11A-01-TS1`) → portion `41dec384-4d77-441c-8142-dd34cec0a5a8` (`TCGA-55-7910-11A-01`).
- Linked sample `a4dd7043-345b-420e-8b36-1604ed86c6b6` (`TCGA-55-7910-11A`, **Solid Tissue Normal**) → case `b2bc53d6-ef78-4ae9-a6b5-1c7cad9a43eb`.

**TCGA-69-7761: adenocarcinoma, TCGA-LUAD**
- File `8cc3b5f7-1f74-4bb9-a046-9870d8cdf912` (`TCGA-69-7761-01A-01-TS1.5fbed09f-c790-4e78-a3c7-e026c878d906.svs`).
- Associated slide `5fbed09f-c790-4e78-a3c7-e026c878d906` (`TCGA-69-7761-01A-01-TS1`) → portion `42089966-a93c-4c73-98fa-0ed20b44efc8` (`TCGA-69-7761-01A-11`).
- Linked sample `c8c5aa67-c6b9-48ba-ace2-b040170d73fc` (`TCGA-69-7761-01A`, **Primary Tumor**) → case `77828a90-8e2a-4664-b674-d837e6e34fe4`.

**TCGA-60-2715: squamous, TCGA-LUSC**
- File `90c06ba4-30bf-49d5-a84b-ddc213de048d` (`TCGA-60-2715-01A-01-TS1.19cda9b1-60ee-4a23-9a47-adc769e600f5.svs`).
- Associated slide `19cda9b1-60ee-4a23-9a47-adc769e600f5` (`TCGA-60-2715-01A-01-TS1`) → portion `8b02a010-17b5-4610-a61a-0872fbdf47d8` (`TCGA-60-2715-01A-01`).
- Linked sample `5848ee1c-191f-4434-b7c6-598058aa0dd8` (`TCGA-60-2715-01A`, **Primary Tumor**) → case `f3e67161-1532-4b50-a9b5-0da80410c4d7`.

## Preparation evidence

Explicit Frozen confirmations: **0/9**. Frozen by documented TS barcode inference: **9/9**. All nine portions report `is_ffpe=false`; this is evidence of reported non-FFPE status, not independent proof of freezing.

Preservation fields: **Unknown for eight samples; OCT for TCGA-98-A538**. OCT is supporting context and is not promoted to an explicit Frozen confirmation. The raw Unknown values remain Unknown in the evidence.

[GDC](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/) defines TS as Top Slide. [The TCGA archive methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC3822112/) describe TS/BS as frozen sections adjacent to genomics tissue.

## Encoder and finite embeddings

Encoder: `MahmoodLab/UNI2-h`; revision `d517a8dd47902dd7c308b3c36f63bce47e7b9a43`; checkpoint SHA256 `6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e`.

All nine arrays have shape **[512,1536]** with matching **[512,2]** coordinates; **4,608 embeddings, all finite**. The frozen model and official evaluation transforms were used; no synthetic features contributed to these arrays.

## Tile filtering

| Patient | Candidates | Accepted | Rejected | Embedded | Accepted, not sampled |
|---|---:|---:|---:|---:|---:|
| TCGA-33-4547 | 7625 | 2865 | 4760 | 512 | 2353 |
| TCGA-05-4403 | 4588 | 1192 | 3396 | 512 | 680 |
| TCGA-66-2794 | 8277 | 2940 | 5337 | 512 | 2428 |
| TCGA-58-8391 | 2279 | 1167 | 1112 | 512 | 655 |
| TCGA-55-A493 | 15478 | 1265 | 14213 | 512 | 753 |
| TCGA-98-A538 | 10985 | 1994 | 8991 | 512 | 1482 |
| TCGA-55-7910 | 4686 | 2486 | 2200 | 512 | 1974 |
| TCGA-69-7761 | 2385 | 1251 | 1134 | 512 | 739 |
| TCGA-60-2715 | 4712 | 1317 | 3395 | 512 | 805 |

Rejected means below the 50% tissue-coverage threshold on the complete candidate grid. The sampling cap is separate; partial edge positions are also recorded separately in the JSON.

Whole-grid pass rates include slide background and cannot measure tissue false-negative rates. The 50% threshold may favor denser normal tissue despite all three normals exceeding 512 accepted candidates. Three slides per class cannot establish absence of masking bias.

Mean complete-grid acceptance: non_tumor: 47.3%, adenocarcinoma: 28.9%, squamous: 27.2%.

All slides warn that embedded ICC profiles were not applied. Visual QC also noted pale/low-contrast tiles in TCGA-60-2715, folds, cut edges, and focus/color variation. No aggressive blur/artifact filter was added.

## Normal source projects

Normals from both projects are represented: **TCGA-LUSC 2** (TCGA-33-4547, TCGA-58-8391); **TCGA-LUAD 1** (TCGA-55-7910).

## Exact persistent locations

- root: `/content/drive/MyDrive/LungCancer_AC215`
- selection: `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_selection.json`
- raw_metadata_and_manifest: `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery`
- download_ledger: `/content/drive/MyDrive/LungCancer_AC215/artifacts/download_ledger.json`
- slide_outputs: `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides`
- review: `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review`
- detailed_summary: `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/details.json`
- source_backups: `/content/drive/MyDrive/LungCancer_AC215/code_backups`
- notebook_helper: `/content/drive/MyDrive/LungCancer_AC215/code/scripts/show_pilot.py`

Latest code backup: `/content/drive/MyDrive/LungCancer_AC215/code_backups/code-20261018T235227Z.tar.gz`; SHA256 `ebf9e812995c7108d97f61be7bfe0db7668bd83c8daf41177e5ef15992f9b0bd`.

The JSON lists all nine exact per-file output paths, all UUIDs, raw preparation fields, encoder transforms, and every code archive.

**Downloads and training remain paused.**
