from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Chunk:
    source: str
    id: str
    text: str
    section: Optional[str] = None
    score: Optional[float] = None


@dataclass(frozen=True)
class DatasetSummary:
    row_count: int
    missing_pct: float
    platform: Optional[str] = None
    beta_range: Optional[Tuple[float, float]] = None
    notes: Optional[str] = None
