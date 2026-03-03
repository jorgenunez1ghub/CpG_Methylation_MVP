from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class DatasetSummary:
    """Aggregated metadata ONLY. Never include raw rows, PII, or per-sample values."""
    row_count: int
    missing_pct: float
    platform: Optional[str] = None
    beta_range: Optional[Tuple[float, float]] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class Chunk:
    """A retrieved knowledge snippet."""
    id: str
    text: str
    source: str                 # e.g., "methylation_basics.md"
    section: Optional[str] = None
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Citation:
    source: str
    chunk_id: str
    section: Optional[str] = None
    score: Optional[float] = None


@dataclass(frozen=True)
class ContextPackage:
    system_prompt: str
    user_message: str
    retrieved_chunks: List[Chunk]
    citations: List[Citation]
    token_estimate: int
