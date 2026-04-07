# PR #12 Salvage Matrix (April 7, 2026)

## Decision summary
**Operational recommendation:** supersede PR #12 with one small follow-up patch, then close PR #12.

## Matrix

| PR #12 intent area | Evidence in current repo | Status | Action |
|---|---|---|---|
| Typed context models | `src/context/types.py` dataclasses exist for summary/chunks/citations/context package. | Present | Keep as canonical typed surface. |
| Citation formatting and deduplication | `src/context/citations.py` exists and deduplicates `(source, chunk_id)` pairs. | Present | Keep and test indirectly through builder flow. |
| Retriever abstraction and baseline implementations | `src/context/retriever.py` has `Retriever` protocol, `MockRetriever`, and `KeywordRetriever`. | Present | Keep; align later with production retrieval plan. |
| Central context builder entrypoint | `src/context/builder.py` exists with `build_context(...)` and input guardrails. | Present but incomplete dependency | Supersede with missing dependency fix. |
| Prompt construction module backing builder | `src/context/builder.py` imports `src.context.prompts`, but `src/context/prompts.py` is absent. | Missing | Add in superseding patch. |
| Regression checks for context builder importability | No context-specific tests currently enforce builder import or assembly behavior. | Missing | Add focused tests in superseding patch. |

## Closure gate
Close PR #12 only after all rows are either **Present** or intentionally dropped with documented rationale.
