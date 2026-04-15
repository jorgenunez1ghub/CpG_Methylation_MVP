from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatasetSummary:
    """Aggregated metadata ONLY. Never include raw rows, PII, or per-sample values."""

    row_count: int
    missing_pct: float
    platform: str | None = None
    beta_range: tuple[float, float] | None = None
    notes: str | None = None


@dataclass(frozen=True)
class Chunk:
    """A retrieved knowledge snippet."""

    id: str
    text: str
    source: str
    section: str | None = None
    score: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class Citation:
    source: str
    chunk_id: str
    section: str | None = None
    score: float | None = None


@dataclass(frozen=True)
class ContextPackage:
    system_prompt: str
    user_message: str
    retrieved_chunks: list[Chunk]
    citations: list[Citation]
    token_estimate: int
