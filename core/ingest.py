"""Ingestion pipeline for methylation upload files."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from core.validate import (
    ValidationConfig,
    ValidationError,
    ensure_beta_in_range,
    ensure_non_empty_dataframe,
    ensure_required_columns,
)

CANONICAL_COLUMNS: tuple[str, ...] = (
    "cpg_id",
    "beta",
    "chrom",
    "pos",
    "gene",
    "pval",
)

ALIASES: dict[str, tuple[str, ...]] = {
    "cpg_id": ("cpg_id", "cpg", "probe", "probe_id", "CpG", "cgid"),
    "beta": ("beta", "beta_value", "methylation_level", "methylation", "Beta"),
    "chrom": ("chrom", "chr", "chromosome"),
    "pos": ("pos", "position", "bp", "start"),
    "gene": ("gene", "symbol", "gene_symbol"),
    "pval": ("pval", "p_value", "p.value"),
}


class IngestError(ValidationError):
    """Raised for parsing and ingestion errors."""


def _detect_delimiter(filename: str) -> str | None:
    suffix = Path(filename).suffix.lower()
    if suffix == ".tsv":
        return "\t"
    if suffix == ".csv":
        return ","
    return None


def _read_with_sniffing(raw_bytes: bytes, filename: str) -> pd.DataFrame:
    buffer = BytesIO(raw_bytes)
    delimiter = _detect_delimiter(filename)

    try:
        if delimiter:
            return pd.read_csv(buffer, sep=delimiter)

        return pd.read_csv(buffer, sep=None, engine="python")
    except pd.errors.EmptyDataError as exc:
        raise IngestError(
            "The uploaded file appears empty. Please upload a CSV/TSV file with header and rows."
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise IngestError(
            "Could not parse the uploaded file. Please upload a valid CSV/TSV with a header row."
        ) from exc


def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lowered = {column.lower().strip(): column for column in df.columns}
    rename_map: dict[str, str] = {}

    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in lowered:
                rename_map[lowered[alias_lower]] = canonical
                break

    return df.rename(columns=rename_map)


def load_methylation_file(uploaded_file: BinaryIO, source_name: str | None = None) -> pd.DataFrame:
    """Load, validate, and normalize a methylation upload into canonical schema."""
    if uploaded_file is None:
        raise IngestError("No file was provided. Upload a CSV/TSV file to continue.")

    try:
        name = source_name or getattr(uploaded_file, "name", "uploaded_file")
        raw_bytes = uploaded_file.read()
        if not raw_bytes:
            raise IngestError("The uploaded file is empty. Please choose a non-empty CSV/TSV file.")

        parsed_df = _read_with_sniffing(raw_bytes=raw_bytes, filename=name)
        ensure_non_empty_dataframe(parsed_df)

        normalized = _canonicalize_columns(parsed_df)
        ensure_required_columns(normalized, ValidationConfig().required_columns)

        normalized = normalized.copy()
        normalized["cpg_id"] = normalized["cpg_id"].astype(str).str.strip()

        raw_beta = normalized["beta"]
        numeric_beta = pd.to_numeric(raw_beta, errors="coerce")
        invalid_count = int((numeric_beta.isna() & raw_beta.notna()).sum())
        if invalid_count > 0:
            raise IngestError(
                f"Found {invalid_count} non-numeric beta value(s). "
                "Beta values must be numeric between 0 and 1."
            )

        normalized["beta"] = numeric_beta
        normalized = normalized.dropna(subset=["beta", "cpg_id"])
        ensure_non_empty_dataframe(normalized)
        ensure_beta_in_range(normalized, beta_column="beta")

        keep_columns = [column for column in CANONICAL_COLUMNS if column in normalized.columns]
        normalized = normalized[keep_columns].copy()

        normalized["source_file"] = "uploaded_file"
        normalized["uploaded_at"] = datetime.now(timezone.utc).isoformat()

        return normalized.reset_index(drop=True)
    except ValidationError as exc:
        if isinstance(exc, IngestError):
            raise
        raise IngestError(str(exc)) from exc
