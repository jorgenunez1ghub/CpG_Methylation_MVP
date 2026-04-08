"""I/O helpers for methylation upload files."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class TableReadResult:
    """Parsed table plus delimiter-detection metadata."""

    dataframe: pd.DataFrame
    delimiter_used: str | None
    parse_strategy: str
    recovered_from_extension_mismatch: bool


def detect_delimiter(filename: str) -> str | None:
    """Infer delimiter from filename extension when available."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    return None


def _parse_table(raw_bytes: bytes, delimiter: str | None) -> pd.DataFrame:
    """Parse raw bytes with a specific delimiter or pandas sniffing."""
    buffer = BytesIO(raw_bytes)
    if delimiter is None:
        return pd.read_csv(buffer, sep=None, engine="python")
    return pd.read_csv(buffer, sep=delimiter)


def _should_try_fallback(primary_df: pd.DataFrame, fallback_df: pd.DataFrame) -> bool:
    """Return whether fallback parsing is clearly better than the primary parse."""
    return len(primary_df.columns) <= 1 and len(fallback_df.columns) > len(primary_df.columns)


def read_table_bytes(raw_bytes: bytes, filename: str) -> TableReadResult:
    """Read CSV/TSV bytes into a dataframe with conservative delimiter recovery."""
    preferred_delimiter = detect_delimiter(filename)

    if preferred_delimiter is None:
        sniffed_df = _parse_table(raw_bytes=raw_bytes, delimiter=None)
        return TableReadResult(
            dataframe=sniffed_df,
            delimiter_used=None,
            parse_strategy="sniffed_from_content",
            recovered_from_extension_mismatch=False,
        )

    primary_df = _parse_table(raw_bytes=raw_bytes, delimiter=preferred_delimiter)
    fallback_df = _parse_table(raw_bytes=raw_bytes, delimiter=None)

    if _should_try_fallback(primary_df=primary_df, fallback_df=fallback_df):
        return TableReadResult(
            dataframe=fallback_df,
            delimiter_used=None,
            parse_strategy="recovered_from_mislabeled_extension",
            recovered_from_extension_mismatch=True,
        )

    return TableReadResult(
        dataframe=primary_df,
        delimiter_used=preferred_delimiter,
        parse_strategy="extension_delimiter",
        recovered_from_extension_mismatch=False,
    )
