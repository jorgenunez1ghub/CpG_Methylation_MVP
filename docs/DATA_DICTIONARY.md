# Data Dictionary (MVP)

This dictionary explains each canonical column used in normalized CpG methylation outputs.

| Column | Meaning | Example | Expected use |
|---|---|---|---|
| `cpg_id` | CpG/probe identifier for a methylation measurement. | `cg00000108` | Join key and unique-count QC metric. |
| `beta` | Methylation beta value for the CpG site. | `0.73` | Core metric for range checks and summary stats. |
| `chrom` | Chromosome annotation from input, when provided. | `chr7` | Optional context for downstream grouping/filtering. |
| `pos` | Genomic position/base-pair coordinate from input, when provided. | `27123456` | Optional positional context. |
| `gene` | Gene symbol/annotation from input, when provided. | `TP53` | Optional interpretation context only. |
| `pval` | Source p-value/significance field, when provided. | `0.0042` | Optional signal-strength context from source data. |
| `source_file` | Original upload filename captured by the ingestion pipeline. | `sample_upload.csv` | Basic provenance in app session output and exports. |
| `uploaded_at` | UTC ingestion timestamp in ISO format. | `2026-04-07T10:30:12.100000+00:00` | Provenance and reproducibility context. |

## Notes
- The MVP requires `cpg_id` and `beta` after normalization.
- Optional columns are retained only if present in the upload.
- Under the approved aggregation policy, duplicate `cpg_id` rows may be collapsed into one normalized row when optional metadata values do not conflict.
- When aggregation is applied, a separate aggregation-audit artifact records `source_row_count`, `beta_min`, `beta_max`, `beta_mean`, carried metadata values, and `aggregation_rule`.
- This is an educational analysis workflow and not clinical interpretation guidance.
