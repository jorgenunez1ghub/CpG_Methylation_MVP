# PR #7 Hunk-by-Hunk Salvage Matrix (April 7, 2026)

## Inputs available for this matrix
Because the full GitHub PR #7 unified diff is not available in this local environment, this matrix is built from:

1. PR #7 title and motivation text.
2. Local commit history around adjacent PRs (#5, #6, #9).
3. Current repository state (`app/`, `src/cpg_methylation_mvp/core/`, and `tests/`).

## Decision summary
**Operational recommendation:** close PR #7 as superseded, then open a tiny follow-up PR only if you find unique unmerged hunks in the GitHub diff.

## Salvage matrix

| Likely PR #7 hunk | Evidence in current repo | Status | Action |
|---|---|---|---|
| App uses public core API surface (not internal module imports) | `app/main.py` imports from `cpg_methylation_mvp.core`; architecture test now enforces this import style. | Present + enforced | Keep; no further merge needed. |
| Core public API is explicitly exported | `src/cpg_methylation_mvp/core/__init__.py` exports stable orchestration symbols (`IngestError`, `ValidationConfig`, `load_methylation_file`, `validate_upload`, `normalize_upload`, `analyze_methylation`, `qc_summary`). | Present | Keep; treat as authoritative orchestration surface. |
| Dependency guardrail: core modules should not depend on Streamlit | `tests/test_architecture_rules.py` checks for Streamlit imports inside core modules. | Present | Keep; continue running in CI. |
| Dependency guardrail: app should not bypass public core API | `tests/test_architecture_rules.py` now forbids direct imports from internal core implementation modules (`ingest`, `transform`, `validate`, `analyze`). | Present + tightened | Salvaged in current branch; keep. |
| UI orchestration hardening and caching flow | Existing app path includes cached wrappers and separation of orchestration/display logic from core implementation modules. | Present | Keep; no special PR #7 salvage required. |
| Documentation of app/core separation rationale | Existing docs include refactor notes and now include explicit stale/supersede guidance. | Present | Keep docs; no additional migration action required. |

## What to verify against the live PR #7 diff before closing
If you open PR #7 on GitHub, only block closure if you find a hunk that is:

- not already represented by current code,
- not covered by tests,
- and still aligned with current `src/` layout.

If such a hunk exists, cherry-pick only that hunk into a minimal replacement PR.
