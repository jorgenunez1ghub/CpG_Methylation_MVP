# Current Task Spec

## Goal
Close the remaining context-layer risk by defining the citation/evidence contract, adding a local evidence source, and wiring deterministic cited context into the app.

## Context
The repo has `make verify`, `program.md`, a current-task spec, a context pack, a decision log, and package-scoped context helpers. The remaining risks were:
- `cpg_methylation_mvp.context` was not backed by a concrete evidence source,
- no evidence/citation contract existed for future RAG work,
- the context layer was not visible in the app.

## Constraints
- Preserve existing app behavior and public core API.
- Use only local repo evidence sources.
- Do not add biomedical, ML, RAG runtime, embedding, vector database, or OpenAI dependencies in this pass.
- Keep Streamlit-specific logic out of core modules.
- Keep context helpers out of `cpg_methylation_mvp.core`.
- Do not present local context chunks as clinical evidence.

## Done When
- `docs/context/evidence_contract.md` defines chunk, citation, retrieval, and display rules.
- `data/evidence/workflow_01_context_chunks.json` provides local repo-doc context.
- The app renders cited local context after structured interpretation.
- Tests cover evidence loading, context building, app table output, and invalid source rejection.
- `make verify` passes locally.

## Next Spec Update
Replace this file at the start of the next implementation session with the next small task from `NEXT_STEPS.md`.
