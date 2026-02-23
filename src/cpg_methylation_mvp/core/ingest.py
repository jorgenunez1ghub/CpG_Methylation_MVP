"""Ingestion pipeline for methylation upload files."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import BinaryIO

import pandas as pd

from .io import read_table_bytes
from .transform import normalize_upload
from .validate import (
    ValidationError,
    ensure_non_empty_dataframe,
    validate_upload,
)


class IngestError(ValidationError):
    """Raised for parsing and ingestion errors."""


def load_methylation_file(uploaded_file: BinaryIO, source_name: str | None = None) -> pd.DataFrame:
    """Load, validate, and normalize a methylation upload into canonical schema."""
    if uploaded_file is None:
        raise IngestError("No file was provided. Upload a CSV/TSV file to continue.")

    try:
        name = source_name or getattr(uploaded_file, "name", "uploaded_file")
        raw_bytes = uploaded_file.read()
        if not raw_bytes:
            raise IngestError("The uploaded file is empty. Please choose a non-empty CSV/TSV file.")

        parsed_df = read_table_bytes(raw_bytes=raw_bytes, filename=name)
        ensure_non_empty_dataframe(parsed_df)

        normalized = normalize_upload(parsed_df)
        normalized = validate_upload(normalized)
        normalized = normalized.dropna(subset=["beta", "cpg_id"])
        ensure_non_empty_dataframe(normalized)
        normalized["source_file"] = "uploaded_file"
        normalized["uploaded_at"] = datetime.now(timezone.utc).isoformat()

        return normalized.reset_index(drop=True)
    except pd.errors.EmptyDataError as exc:
        raise IngestError(
            "The uploaded file appears empty. Please upload a CSV/TSV file with header and rows."
        ) from exc
    except ValidationError as exc:
        if isinstance(exc, IngestError):
            raise
        raise IngestError(str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise IngestError(
            "Could not parse the uploaded file. Please upload a valid CSV/TSV with a header row."
        ) from exc
