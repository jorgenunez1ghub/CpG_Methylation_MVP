# PR #7 Staleness Review (April 7, 2026)

## Scope reviewed
PR #7 title: **"Refactor UI orchestration; expose core public API and add dependency guardrail tests"**.

## Current state in repository
The key intentions of PR #7 already appear in the current branch history:

- The app imports from the public core surface (`from cpg_methylation_mvp.core import ...`) rather than pulling directly from internal implementation modules.
- Core API exports are centralized in `src/cpg_methylation_mvp/core/__init__.py`.
- Architecture guardrail tests exist to prevent Streamlit leakage into core modules.
- Additional UI/core separation hardening landed in subsequent merged PRs.

## Recommendation
Treat PR #7 as **stale and superseded** unless it contains unique, unmerged changes not present in this repository.

### Practical decision rule
- **Close PR #7** if its diff is fully covered by merged work.
- **Supersede only if needed** by opening a small replacement PR for any residual, isolated hunks.

## Salvage checklist (if any residual diff remains on GitHub)
1. Cherry-pick only focused, still-missing hunks.
2. Preserve app/core separation (`app/` orchestration only, `core/` framework-agnostic).
3. Keep/expand architecture tests for import boundaries.
4. Re-run focused tests before merge.
