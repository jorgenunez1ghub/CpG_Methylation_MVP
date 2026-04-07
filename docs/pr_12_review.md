# PR #12 Review: Close vs Supersede (April 7, 2026)

## PR under review
PR #12 title shown: **"Add context prompt builder and typed models for educational methylation assistant"**.

## What is already present in `main` history
From local git history and repository state, most PR #12 intent appears already landed in subsequent commits:

- `src/context/types.py` defines typed dataclasses (`DatasetSummary`, `Chunk`, `Citation`, `ContextPackage`).
- `src/context/citations.py` centralizes citation deduplication.
- `src/context/retriever.py` includes retriever protocol plus mock/keyword implementations.
- `src/context/builder.py` provides a single `build_context(...)` entrypoint and guardrails around query/chunk handling.

## Gap that blocks “close as fully superseded”
`src/context/builder.py` imports `src.context.prompts`, but that module is missing in this repo state.

Result: direct import of the builder currently fails (`ModuleNotFoundError: No module named 'src.context.prompts'`).

## Recommendation
**Do not close PR #12 as fully superseded yet.**

Treat PR #12 as **partially superseded** and use a focused superseding PR that:

1. Adds the missing `src/context/prompts.py` module with explicit safety/citation/educational framing.
2. Adds narrow tests for `src.context.builder` import and basic context package assembly.
3. Keeps this layer isolated from `cpg_methylation_mvp.core` until integration is intentional.

After that focused patch merges, PR #12 can be safely closed as superseded.

## Fast decision rule for GitHub triage
- **Supersede (recommended now):** if PR #12 still contains unique implementation details for `prompts.py` and/or tests not present in `main`.
- **Close immediately:** only if the live PR diff has no unique hunks beyond already-merged context files.
