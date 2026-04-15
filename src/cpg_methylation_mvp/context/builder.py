from __future__ import annotations

from .citations import format_citations
from .prompts import SYSTEM_PROMPT, build_user_message
from .retriever import Retriever
from .types import Chunk, ContextPackage, DatasetSummary


def build_context(
    markers: list[str],
    dataset_summary: DatasetSummary,
    retriever: Retriever,
    top_k: int = 5,
    max_chunk_chars: int = 1200,
) -> ContextPackage:
    """
    Single entrypoint: all LLM calls should go through this builder.
    - Accepts only aggregated dataset_summary (NO raw rows)
    - Retrieves top_k knowledge chunks
    - Builds system_prompt + user_message
    - Returns citations for UI
    """
    _validate_inputs(markers, dataset_summary)

    query = _build_query(markers, dataset_summary)
    chunks = retriever.retrieve(query, top_k=top_k)
    chunks = _trim_chunks(chunks, max_chunk_chars=max_chunk_chars)

    citations = format_citations(chunks)
    user_message = build_user_message(markers=markers, summary=dataset_summary, chunks=chunks)

    return ContextPackage(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        retrieved_chunks=chunks,
        citations=citations,
        token_estimate=_estimate_tokens(SYSTEM_PROMPT + "\n\n" + user_message),
    )


def _build_query(markers: list[str], summary: DatasetSummary) -> str:
    markers_part = ", ".join(markers[:25])  # avoid massive queries
    platform_part = f" platform={summary.platform}" if summary.platform else ""
    return f"DNA methylation educational interpretation markers: {markers_part}.{platform_part}"


def _trim_chunks(chunks: list[Chunk], max_chunk_chars: int) -> list[Chunk]:
    out: list[Chunk] = []
    for c in chunks:
        text = c.text.strip()
        if len(text) > max_chunk_chars:
            text = text[: max_chunk_chars - 1].rstrip() + "…"
        out.append(Chunk(**{**c.__dict__, "text": text}))
    return out


def _estimate_tokens(text: str) -> int:
    # Conservative heuristic: ~4 chars/token in English text
    return max(1, int(len(text) / 4))


def _validate_inputs(markers: list[str], summary: DatasetSummary) -> None:
    if summary.row_count < 0:
        raise ValueError("row_count must be >= 0")
    if not (0.0 <= summary.missing_pct <= 100.0):
        raise ValueError("missing_pct must be in [0, 100]")
    # Guardrail: markers should be simple strings to reduce prompt injection risk.
    for m in markers:
        if len(m) > 120:
            raise ValueError("Marker name too long.")
