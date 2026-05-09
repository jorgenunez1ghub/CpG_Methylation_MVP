# Current Task Spec

## Goal
Add deterministic QC explanation layer and demo readiness docs for the Release 0.1 hosted demo slice.

## Context
The MVP already supports upload, validation, normalization, QC, panel coverage, structured interpretation, and local cited context. The next implementation slice is to improve demo trust/readability by explaining QC outputs in plain language and shipping focused demo-operation documentation.

## Constraints
- Keep scope to Workflow 01 only.
- Keep explanations deterministic, educational, and non-clinical.
- Do not add external RAG runtime, embeddings, vector DBs, or OpenAI dependencies.
- Preserve app/core separation: Streamlit stays in `app/`; reusable logic stays in `src/cpg_methylation_mvp/core/`.
- Preserve current public core API behavior used by `app/main.py`.

## Done When
- `src/cpg_methylation_mvp/core/qc_explain.py` provides deterministic QC explanation output.
- App QC section renders the explanation blocks (observed data, possible meaning, limitations, next steps).
- Focused tests cover clean/edge QC explanation behavior (missing beta, out-of-range beta, duplicates, parse warnings).
- Demo readiness docs exist under `docs/demo/` for checklist, script, and known issues.
- `NEXT_STEPS.md` top priorities align to hosted smoke checklist/automation, mixed-delimiter quarantine recovery, and release evidence packaging.
- `make verify` passes.
