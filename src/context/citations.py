from __future__ import annotations

from typing import List

from src.context.types import Citation, Chunk


def format_citations(chunks: List[Chunk]) -> List[Citation]:
    # Keep all citations, but de-duplicate exact (source, chunk_id)
    seen = set()
    out: List[Citation] = []
    for c in chunks:
        key = (c.source, c.id)
        if key in seen:
            continue
        seen.add(key)
        out.append(Citation(source=c.source, chunk_id=c.id, section=c.section, score=c.score))
    return out
