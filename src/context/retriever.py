from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol

from src.context.types import Chunk


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int) -> List[Chunk]:
        ...


@dataclass
class MockRetriever:
    """Use for early wiring + tests."""

    canned: List[Chunk]

    def retrieve(self, query: str, top_k: int) -> List[Chunk]:
        return self.canned[:top_k]


@dataclass
class KeywordRetriever:
    """
    Lightweight baseline: loads a chunk index from disk and ranks by term overlap.
    Good enough until you wire embeddings.
    """

    chunk_index_path: Path

    def retrieve(self, query: str, top_k: int) -> List[Chunk]:
        data = json.loads(self.chunk_index_path.read_text(encoding="utf-8"))
        chunks: List[Chunk] = [Chunk(**item) for item in data]

        q_terms = _terms(query)
        scored: List[Chunk] = []
        for c in chunks:
            c_terms = _terms(c.text)
            overlap = len(q_terms.intersection(c_terms))
            score = float(overlap)
            if score <= 0:
                continue
            scored.append(Chunk(**{**c.__dict__, "score": score}))

        scored.sort(key=lambda x: (x.score or 0.0), reverse=True)
        return scored[:top_k]


_TERM_RE = re.compile(r"[a-z0-9]+")


def _terms(text: str) -> set[str]:
    return set(_TERM_RE.findall(text.lower()))
