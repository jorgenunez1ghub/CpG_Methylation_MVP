# Evidence Contract

## Purpose
Define the minimum contract for local evidence used by `cpg_methylation_mvp.context`.

This layer supports deterministic, cited orientation for the current MVP. It is not a biomedical knowledge base, clinical evidence engine, vector store, or LLM response layer.

## Current Evidence Source
- `data/evidence/workflow_01_context_chunks.json`
- Source files are local repo documents such as workflow, schema, validation, and data-policy docs.
- Each chunk must cite an existing source path and section.

## Chunk Schema
Each evidence chunk is a JSON object with:

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Stable unique chunk ID. |
| `text` | Yes | Short evidence text grounded in the cited source. |
| `source` | Yes | Local repo path or URL. Local paths must exist. |
| `section` | Yes | Source section or heading. |
| `score` | No | Retrieval score added at runtime. |
| `metadata.evidence_type` | Yes | Contract category, such as `workflow_contract` or `validation_contract`. |
| `metadata.claim_scope` | Yes | Boundary for what the chunk can support. |
| `metadata.allowed_use` | Yes | Intended use in the app or future prompt context. |

## Allowed Claims
Allowed:
- describe supported app workflow,
- explain schema and validation behavior,
- explain duplicate, delimiter, and data-handling policy,
- explain that interpretation is bounded, heuristic, and non-clinical.

Not allowed:
- diagnosis, treatment, or medical advice,
- unstated biological significance,
- claims that a marker implies health status,
- claims from sources not present in the evidence index.

## Retrieval Contract
- Retrieval is deterministic keyword overlap.
- No embeddings or vector database are used.
- No LLM call is made.
- If no chunks match, the app should say that no local cited context matched.

## App Display Contract
When rendered in the app, evidence context must show:
- source,
- section,
- chunk ID,
- relevance score when available,
- evidence text.

The UI must not present retrieved chunks as clinical evidence. They are repo-local context for the MVP workflow.
