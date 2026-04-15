# Current Task Spec

## Goal
Close the two remaining repo-operating risks from the prior pass: add lint/typecheck gates to verification, and resolve the ambiguous experimental `src/context/` package boundary.

## Context
The repo now has `make verify`, `program.md`, a current-task spec, a context pack, and a decision log. The remaining risks were:
- `make verify` did not yet run lint or type checks,
- experimental context helpers lived in top-level `src/context/`, outside the installed package, and imported a missing prompt module.

## Constraints
- Preserve existing app behavior and public core API.
- Add only dev-time lint/typecheck dependencies.
- Do not add biomedical, ML, RAG runtime, embedding, vector database, or OpenAI dependencies in this pass.
- Keep Streamlit-specific logic out of core modules.
- Keep context helpers out of `cpg_methylation_mvp.core` and out of the current Streamlit workflow.

## Done When
- `make verify` runs doctor, lint, typecheck, and tests.
- Ruff and mypy config lives in `pyproject.toml`.
- Context helpers live under `src/cpg_methylation_mvp/context/`.
- Tests cover context helper import/build behavior and package-boundary placement.
- Docs record the decision and remaining experimental status.
- `make verify` passes locally.

## Next Spec Update
Replace this file at the start of the next implementation session with the next small task from `NEXT_STEPS.md`.
