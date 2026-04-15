# External Scientific RAG Policy

## Purpose
Define the rules that must be satisfied before this repo adds external scientific retrieval.

This is a planning and governance contract only. The current app does not fetch external sources, use embeddings, call an LLM, or present external scientific evidence.

## Runtime Status
- External scientific RAG is disabled.
- Machine-readable policy: `data/evidence/external_source_policy.json`
- Current app evidence source remains local repo docs: `data/evidence/workflow_01_context_chunks.json`

## Allowed Source Types
Allowed external sources must fit one of these types:

| Source type | Allowed use |
|---|---|
| Peer-reviewed primary study | Background context or candidate marker discussion. |
| Systematic review or meta-analysis | Background context or evidence summary. |
| Official database or registry record | Identifier lookup or annotation context. |
| Official guidance or reference material | Terminology, methodology, or non-clinical limitation context. |

Disallowed sources include uncited blogs or marketing pages, forums or social media posts, unreviewed LLM output, patient-specific records, and paywalled sources without reviewable metadata.

## Freshness Rules
Before runtime use:
- source metadata must be re-verified within the policy window,
- content review must not be expired,
- official database/reference records require shorter review windows than static publications,
- stale sources must be excluded or re-reviewed before retrieval.

Default policy windows are encoded in `data/evidence/external_source_policy.json`.

## Review Rules
Every external source must have:
- source type,
- required metadata for that source type,
- retrieval/access date,
- reviewer identity or review role,
- review date,
- review notes,
- known limitations.

External sources may not be used at runtime until the source registry exists and review is complete.

## Citation Requirements
Any retrieved external chunk must expose:
- chunk ID,
- source type,
- source title or record ID,
- source locator such as DOI, PMID, URL, section, table, or record field,
- publication or revision date,
- retrieval date,
- review date and reviewer,
- claim scope,
- limitations.

## Claim Boundaries
Allowed:
- educational background context,
- methodology or terminology explanation,
- identifier or annotation context,
- cautious evidence summary when supported by cited sources.

Not allowed:
- diagnosis, treatment, or medical advice,
- clinical actionability claims,
- risk prediction claims,
- marker significance claims without cited support,
- unsupported biological claims.

Unsupported or weakly supported claims must be labeled `unknown`.

## Implementation Gate
Before adding external retrieval code, create:
1. an external source registry that conforms to `data/evidence/external_source_policy.json`,
2. tests proving stale or incomplete sources are rejected,
3. UI citation display for all required citation fields,
4. documentation showing how sources are reviewed and refreshed,
5. an explicit decision record approving runtime use.
