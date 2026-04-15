# Context Pack

## Purpose
This is the compact handoff context for future agent-assisted work on CpG_Methylation_MVP. Use it to avoid dumping the full repo into a prompt while keeping the important boundaries visible.

## Product Frame
- Lightweight Streamlit MVP for CpG methylation upload, validation, normalization, panel coverage, QC, cautious structured interpretation, and local cited context.
- Educational demo only; not medical advice.
- Current supported workflow is Workflow 01: one delimited methylation upload through canonical validation/QC and structured interpretation output.

## Architecture Boundaries
- `app/`: Streamlit UI orchestration, caching wrappers, display logic.
- `app/ui_config.py`: UI text/config values.
- `src/cpg_methylation_mvp/core/`: framework-agnostic ingestion, validation, normalization, panel, and analysis logic.
- `tests/`: import, parsing, normalization, panel, workflow, smoke, and architecture checks.
- `docs/`: assumptions, data contracts, release plans, decision notes, and workflow docs.

## High-Value Files To Read First
- `program.md`
- `PROJECT_STATE.md`
- `NEXT_STEPS.md`
- `specs/current-task.md`
- `README.md`
- `docs/workflows/mvp_workflow_01.md`
- `docs/SCHEMA.md`
- `docs/validation_rules.md`
- `docs/context/evidence_contract.md`
- `tests/test_architecture_rules.py`

## Current Verification Gate
Run:

```bash
make verify
```

The gate currently checks Python/import readiness, Ruff linting, mypy type checking, and `pytest -q`. It intentionally does not include eval targets or hosted smoke checks until those workflows are explicitly added to the repo.

## Operating Assumptions
- Sample data is safe to keep in the repo; raw/private uploads are not.
- Interpretation language must remain non-diagnostic and uncertainty-aware.
- Public core API changes require matching test and doc updates.
- GitHub `main` should stay demoable.

## Known Follow-On Candidates
- Add hosted smoke automation.
- Design mixed-delimiter quarantine recovery.
- Strengthen deterministic QC explanation copy.
- Decide whether the local evidence index should later expand to external scientific sources.

## Open Risk Notes
- `cpg_methylation_mvp.context` is wired to local repo evidence only; it is not a scientific literature retrieval system.
- `docs/DEV_DAY_START.md` previously referenced Make targets before they existed; `Makefile` now supplies the core verification path.
