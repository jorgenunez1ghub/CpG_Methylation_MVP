# Validation Rules (MVP)

Validation behavior applies after column canonicalization and canonical column selection.

## Hard-fail checks

1. **File must exist and be non-empty**
   - Empty upload bytes fail ingestion.
   - Parsed dataframes with zero rows fail validation.
   - Uploads larger than the configured limit fail before parsing.

2. **Required canonical columns must be present**
   - Required: `cpg_id`, `beta`.
   - If either is missing, ingestion fails with a clear error message.

3. **`beta` must be numeric**
   - Non-numeric values (excluding blanks that become missing) fail validation.

4. **At least one valid (`cpg_id`, `beta`) row must remain**
   - Rows with missing `cpg_id` or missing `beta` are excluded from the retained analytical dataframe.
   - The upload fails if all rows become invalid after that exclusion.

5. **`beta` must be in `[0, 1]`**
   - Any value `< 0` or `> 1` fails validation.

## Parsing behavior
- Delimiter selection:
  - `.csv` → comma
  - `.tsv` → tab
  - other extensions (for example `.txt`) → pandas sniffing (`sep=None`, `engine="python"`)
  - if extension-based parsing collapses to a single column but content sniffing yields a multi-column table, ingestion recovers via content parsing and records that recovery in the processing report
- UTF-8 BOM:
  - if present, it is removed before parsing and recorded as a parse warning
- Mixed delimiters:
  - mixed comma/tab content is not auto-repaired beyond the conservative fallback above
  - the processing report surfaces a parse warning so the user can inspect dropped rows
- Malformed quoting:
  - malformed quotes or broken delimiter structure raise a clear parsing error

## Alias normalization
Before validation, known source aliases are mapped to canonical names (see `docs/SCHEMA.md`).

## Warning vs hard failure
- Current behavior uses hard failures for required-column issues, invalid numeric format, out-of-range beta values, and uploads where no valid analytical rows remain.
- Duplicate `cpg_id` handling is explicit:
  - `preserve_rows_and_warn` keeps all rows, counts duplicates, and surfaces a warning
  - `reject_duplicates` fails ingestion when any duplicated `cpg_id` is present

## Error messaging intent
Error strings are designed to be:
- specific about what failed,
- actionable for re-upload,
- conservative (no speculative data repair).

## Processing report
Successful ingestion returns a retained normalized dataframe plus a structured processing report for UI/API use.

The report includes:
- report version and run ID,
- source filename,
- UTC upload timestamp,
- input SHA-256 checksum,
- parser strategy and whether delimiter recovery was needed,
- parse warnings,
- input row count,
- retained row count,
- dropped row count,
- dropped-row counts by reason,
- duplicate CpG warning counts,
- duplicate metadata conflict counts,
- applied duplicate policy.
