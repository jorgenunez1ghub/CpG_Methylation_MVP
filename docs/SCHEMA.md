# Canonical Schema v1

This document defines the canonical normalized schema used by the CpG methylation MVP core pipeline.

## Scope
- Applies to normalized outputs returned by `normalize_upload` and ingestion outputs returned by `load_methylation_file`.
- Matches the public core API behavior in `cpg_methylation_mvp.core`.

## Canonical columns

| Column | Required | Type | Constraints | Notes |
|---|---|---|---|---|
| `cpg_id` | Yes | string | non-empty after trim | CpG/probe identifier (for example, `cg000001`). |
| `beta` | Yes | float | numeric and in `[0, 1]` | Methylation beta value. |
| `chrom` | No | string | none | Chromosome label if present (`chr1`, `chrX`, etc.). |
| `pos` | No | numeric/string | none | Genomic position from source file. |
| `gene` | No | string | none | Gene symbol/annotation if present. |
| `pval` | No | numeric/string | none | P-value or source significance field if provided. |

## Alias mapping accepted at ingest
The normalizer maps known aliases to canonical names before validation.

- `cpg_id`: `cpg_id`, `cpg`, `probe`, `probe_id`, `CpG`, `cgid`
- `beta`: `beta`, `beta_value`, `methylation_level`, `methylation`, `Beta`
- `chrom`: `chrom`, `chr`, `chromosome`
- `pos`: `pos`, `position`, `bp`, `start`
- `gene`: `gene`, `symbol`, `gene_symbol`
- `pval`: `pval`, `p_value`, `p.value`

## Ingestion-added metadata columns
The ingestion pipeline currently appends the following metadata columns:

- `source_file`: original upload filename provided to ingestion
- `uploaded_at`: UTC ISO-8601 timestamp

These columns are for traceability in app workflows and are not part of the minimal canonical analytical pair (`cpg_id`, `beta`).

## Processing report fields
Successful ingestion also returns a structured processing report for app/API workflows.

Key report fields include:
- `parse_strategy`: whether parsing followed the extension delimiter, content sniffing, or recovered from a mislabeled extension
- `recovered_from_extension_mismatch`: whether content parsing overrode the file extension
- `input_row_count`, `retained_row_count`, `dropped_row_count`
- `dropped_rows_by_reason`
- `duplicate_cpg_id_groups`, `duplicate_cpg_id_extra_rows`
- `duplicate_policy`
