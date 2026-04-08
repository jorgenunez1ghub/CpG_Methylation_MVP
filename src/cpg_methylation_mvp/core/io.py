"""I/O helpers for methylation upload files."""

from __future__ import annotations

import csv
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
    parse_warnings: tuple[str, ...]


def detect_delimiter(filename: str) -> str | None:
    """Infer delimiter from filename extension when available."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    return None


def _strip_utf8_bom(raw_bytes: bytes) -> tuple[bytes, tuple[str, ...]]:
    """Strip a UTF-8 BOM when present and return related parse warnings."""
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        return raw_bytes[3:], ("removed_utf8_bom",)
    return raw_bytes, ()


def _sample_non_empty_lines(raw_bytes: bytes, max_lines: int = 5) -> list[str]:
    """Return the first non-empty decoded lines for delimiter diagnostics."""
    sample_text = raw_bytes.decode("utf-8", errors="replace")
    return [line for line in sample_text.splitlines()[:max_lines] if line.strip()]


def _detect_mixed_delimiters(sample_lines: list[str]) -> tuple[str, ...]:
    """Return warnings for suspicious mixed-delimiter content."""
    if not sample_lines:
        return ()

    contains_comma = any("," in line for line in sample_lines)
    contains_tab = any("\t" in line for line in sample_lines)
    if contains_comma and contains_tab:
        return ("mixed_delimiters_detected",)
    return ()


def _header_delimiter(sample_lines: list[str]) -> str | None:
    """Infer the delimiter used by the header row when unambiguous."""
    if not sample_lines:
        return None

    header_line = sample_lines[0]
    contains_comma = "," in header_line
    contains_tab = "\t" in header_line
    if contains_comma and not contains_tab:
        return ","
    if contains_tab and not contains_comma:
        return "\t"
    return None


def _csv_field_count(line: str, delimiter: str) -> int | None:
    """Return parsed field count for a single line, respecting CSV quoting."""
    try:
        return len(next(csv.reader([line], delimiter=delimiter)))
    except (StopIteration, csv.Error):
        return None


def _mixed_delimiter_structure_warnings(sample_lines: list[str]) -> tuple[str, ...]:
    """Return a warning when mixed delimiters break header-aligned row widths."""
    if "mixed_delimiters_detected" not in _detect_mixed_delimiters(sample_lines):
        return ()

    header_delimiter = _header_delimiter(sample_lines)
    if header_delimiter is None:
        return ()

    expected_field_count = _csv_field_count(sample_lines[0], delimiter=header_delimiter)
    if expected_field_count is None or expected_field_count <= 1:
        return ()

    for line in sample_lines[1:]:
        field_count = _csv_field_count(line, delimiter=header_delimiter)
        if field_count is None or field_count != expected_field_count:
            return ("mixed_delimiters_inconsistent_structure",)
    return ()


def _prepare_raw_bytes(raw_bytes: bytes) -> tuple[bytes, tuple[str, ...]]:
    """Normalize raw bytes before parsing and collect parse warnings."""
    cleaned_bytes, bom_warnings = _strip_utf8_bom(raw_bytes)
    sample_lines = _sample_non_empty_lines(cleaned_bytes)
    mixed_delimiter_warnings = _detect_mixed_delimiters(sample_lines)
    structural_warnings = _mixed_delimiter_structure_warnings(sample_lines)
    return cleaned_bytes, bom_warnings + mixed_delimiter_warnings + structural_warnings


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
    prepared_bytes, parse_warnings = _prepare_raw_bytes(raw_bytes)
    preferred_delimiter = detect_delimiter(filename)

    if preferred_delimiter is None:
        sniffed_df = _parse_table(raw_bytes=prepared_bytes, delimiter=None)
        return TableReadResult(
            dataframe=sniffed_df,
            delimiter_used=None,
            parse_strategy="sniffed_from_content",
            recovered_from_extension_mismatch=False,
            parse_warnings=parse_warnings + ("sniffed_delimiter_for_unknown_extension",),
        )

    primary_df = _parse_table(raw_bytes=prepared_bytes, delimiter=preferred_delimiter)
    fallback_df = _parse_table(raw_bytes=prepared_bytes, delimiter=None)

    if _should_try_fallback(primary_df=primary_df, fallback_df=fallback_df):
        return TableReadResult(
            dataframe=fallback_df,
            delimiter_used=None,
            parse_strategy="recovered_from_mislabeled_extension",
            recovered_from_extension_mismatch=True,
            parse_warnings=parse_warnings + ("recovered_from_mislabeled_extension",),
        )

    return TableReadResult(
        dataframe=primary_df,
        delimiter_used=preferred_delimiter,
        parse_strategy="extension_delimiter",
        recovered_from_extension_mismatch=False,
        parse_warnings=parse_warnings,
    )
