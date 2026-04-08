# Duplicate CpG Policy Decision

## Status
Accepted for the current production-hardening phase.

## Decision
The app supports two explicit duplicate `cpg_id` policies:

1. `preserve_rows_and_warn`
   - keep all duplicate rows in the retained dataframe
   - surface duplicate counts in the processing report
   - surface metadata-conflict counts when duplicate groups disagree on optional columns

2. `reject_duplicates`
   - fail ingestion if any duplicate `cpg_id` is present

## Why this decision
- Preserving rows is the safest default for QC review because it avoids silent data loss.
- Rejecting duplicates is appropriate for downstream workflows that require one row per `cpg_id`.
- Aggregation is intentionally deferred because it would introduce a scientific policy that is not yet encoded or validated in the repo.

## Aggregation is out of scope for now
If aggregation is introduced later, it must define:
- how `beta` values are combined,
- how conflicting metadata (`chrom`, `pos`, `gene`, `pval`) are reconciled,
- whether provenance stays row-level or group-level,
- how aggregation is disclosed in the processing report and downloadable artifacts.

## Current implementation implications
- Duplicate counts are tracked in the processing report.
- Duplicate metadata conflicts are tracked separately to show when aggregation would be unsafe.
- UI copy must continue to describe duplicate handling as a user-selected policy, not an inferred scientific truth.
