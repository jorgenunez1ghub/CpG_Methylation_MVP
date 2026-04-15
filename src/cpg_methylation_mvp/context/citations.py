from __future__ import annotations

from .types import Chunk, Citation


def format_citations(chunks: list[Chunk]) -> list[Citation]:
    # Keep all citations, but de-duplicate exact (source, chunk_id)
    seen = set()
    out: list[Citation] = []
    for c in chunks:
        key = (c.source, c.id)
        if key in seen:
            continue
        seen.add(key)
        out.append(Citation(source=c.source, chunk_id=c.id, section=c.section, score=c.score))
    return out
