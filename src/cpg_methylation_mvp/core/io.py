"""I/O helpers for methylation upload files."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


def detect_delimiter(filename: str) -> str | None:
    """Infer delimiter from filename extension when available."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    return None


def read_table_bytes(raw_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read CSV/TSV bytes into a dataframe with light delimiter sniffing."""
    buffer = BytesIO(raw_bytes)
    delimiter = detect_delimiter(filename)

    if delimiter:
        return pd.read_csv(buffer, sep=delimiter)

    return pd.read_csv(buffer, sep=None, engine="python")
