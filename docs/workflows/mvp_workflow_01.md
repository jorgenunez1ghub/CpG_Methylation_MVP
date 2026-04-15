# MVP Workflow 01: Single-file CpG panel coverage + cautious interpretation

## Scope statement
This repository currently supports **one defensible end-to-end workflow**:

1. Upload one delimited methylation file (`.csv`, `.tsv`, or `.txt`) containing at minimum `cpg_id` and `beta`.
2. Parse, normalize, and validate the file into the canonical schema.
3. Evaluate only against the curated panel in `data/panels/core_demo_panel.csv`.
4. Produce a structured interpretation object with explicit limitations and next analytical steps.
5. Retrieve deterministic cited context from local repo evidence chunks.
6. Render the report in the Streamlit app and allow JSON export.

Out-of-scope behavior is intentionally rejected with clear ingestion errors.

## Input contract

### Supported file class
- Delimited text file with a header row.
- Required analytical columns (or aliases resolvable by normalization):
  - `cpg_id`
  - `beta` (numeric within `[0,1]` before retained-row analysis)

### Optional metadata columns
- `chrom`, `pos`, `gene`, `pval`

### Not supported
- JSON payloads.
- Files without required CpG/beta fields.
- Mixed-delimiter content that yields inconsistent row widths.

## Failure behavior
- **Parse failures** return `IngestError` with human-readable remediation guidance.
- **Validation failures** return explicit schema/value errors (for example, missing required columns).
- **Unsupported content** fails closed rather than guessing coercions.

## Output contract

### Structured interpretation schema
The workflow emits a JSON-friendly object with fixed top-level sections:
- `workflow_id`
- `panel_id`
- `status`
- `observed_data`
- `interpretation`
- `limitations`
- `next_steps`

### Interpretation constraints
- Marker-level direction is heuristic only.
- `beta` states are bounded to:
  - `lower` for `<= 0.30`
  - `intermediate` for `(0.30, 0.70)`
  - `higher` for `>= 0.70`
- Clinical claims are out of scope.

### Local cited context
- Source index: `data/evidence/workflow_01_context_chunks.json`
- Contract: `docs/context/evidence_contract.md`
- Retrieval is deterministic keyword overlap.
- Retrieved chunks are repo-local workflow/schema/validation/data-policy context, not clinical evidence.
- No LLM call, embedding model, or vector database is used in Workflow 01.

## Operational checks
- Parse/normalize step outcome is logged in app runtime logs.
- Errors are surfaced to user with step-aware messaging.
- Interpretation is generated only after successful ingestion.

## Rollback / fallback
If interpretation behavior regresses, fallback path is:
1. keep ingestion/QC/report artifacts enabled,
2. disable interpretation section in UI,
3. continue exposing normalized data + processing report while investigation proceeds.
