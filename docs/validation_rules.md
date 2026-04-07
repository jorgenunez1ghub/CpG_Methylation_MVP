# Validation Rules (MVP)

Validation behavior applies after column canonicalization and canonical column selection.

## Hard-fail checks

1. **File must exist and be non-empty**
   - Empty upload bytes fail ingestion.
   - Parsed dataframes with zero rows fail validation.

2. **Required canonical columns must be present**
   - Required: `cpg_id`, `beta`.
   - If either is missing, ingestion fails with a clear error message.

3. **`beta` must be numeric**
   - Non-numeric values (excluding blanks that become missing) fail validation.

4. **At least one valid (`cpg_id`, `beta`) row must remain**
   - Rows with missing `cpg_id` or missing `beta` can be dropped, but the upload fails if all rows become invalid.

5. **`beta` must be in `[0, 1]`**
   - Any value `< 0` or `> 1` fails validation.

## Parsing behavior
- Delimiter selection:
  - `.csv` → comma
  - `.tsv` → tab
  - other extensions (for example `.txt`) → pandas sniffing (`sep=None`, `engine="python"`)

## Alias normalization
Before validation, known source aliases are mapped to canonical names (see `docs/SCHEMA.md`).

## Warning vs hard failure
- Current MVP behavior uses hard failures for required-column issues, invalid numeric format, and out-of-range beta values.
- Duplicate `cpg_id` values are currently allowed (not yet treated as warning/failure).

## Error messaging intent
Error strings are designed to be:
- specific about what failed,
- actionable for re-upload,
- conservative (no speculative data repair).
