# Current Task Spec

## Goal
Close the external scientific RAG planning gap by defining allowed source types, freshness/review rules, citation requirements, and a runtime-disabled policy gate.

## Context
The repo now has local cited context backed by repo-doc evidence. The remaining gap was external scientific RAG governance: future work needed allowed source types, freshness and review rules, and required citation fields before any retrieval implementation.

## Constraints
- Preserve existing app behavior and public core API.
- Define policy only; do not enable external retrieval.
- Do not add biomedical, ML, RAG runtime, embedding, vector database, or OpenAI dependencies in this pass.
- Keep Streamlit-specific logic out of core modules.
- Keep context helpers out of `cpg_methylation_mvp.core`.
- Keep `runtime_enabled` false until a future reviewed source registry and implementation decision exist.

## Done When
- `docs/context/external_scientific_rag_policy.md` defines source, freshness, review, citation, and claim-boundary rules.
- `data/evidence/external_source_policy.json` encodes the policy.
- Context validation rejects external runtime enablement without approval.
- Tests cover policy shape and runtime-disabled enforcement.
- `make verify` passes locally.

## Next Spec Update
Replace this file at the start of the next implementation session with the next small task from `NEXT_STEPS.md`.
