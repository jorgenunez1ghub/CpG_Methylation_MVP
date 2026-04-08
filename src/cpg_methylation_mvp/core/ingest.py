"""Ingestion pipeline for methylation upload files."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import BinaryIO

import pandas as pd

from .io import read_table_bytes
from .transform import normalize_upload
from .validate import (
    ValidationError,
    ensure_non_empty_dataframe,
    required_value_masks,
    validate_upload,
)


class IngestError(ValidationError):
    """Raised for parsing and ingestion errors."""


@dataclass(frozen=True)
class ProcessingReport:
    """Structured processing report for upload transparency."""

    source_file: str
    uploaded_at: str
    input_row_count: int
    retained_row_count: int
    dropped_row_count: int
    dropped_rows_by_reason: dict[str, int]
    duplicate_cpg_id_groups: int
    duplicate_cpg_id_extra_rows: int
    duplicate_policy: str = "preserve_rows_and_warn"

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation of the report."""
        return asdict(self)


@dataclass(frozen=True)
class ProcessedUpload:
    """Normalized upload dataframe plus its structured processing report."""

    normalized_df: pd.DataFrame
    report: ProcessingReport


def _missing_row_counts(validated_df: pd.DataFrame) -> tuple[dict[str, int], pd.Series]:
    """Return exclusive dropped-row counts and the retained-row mask."""
    missing_cpg_id, missing_beta, valid_rows = required_value_masks(validated_df)
    dropped_rows_by_reason = {
        "missing_cpg_id": int((missing_cpg_id & ~missing_beta).sum()),
        "missing_beta": int((missing_beta & ~missing_cpg_id).sum()),
        "missing_cpg_id_and_beta": int((missing_cpg_id & missing_beta).sum()),
    }
    return dropped_rows_by_reason, valid_rows


def _build_processing_report(
    validated_df: pd.DataFrame,
    source_file: str,
    uploaded_at: str,
) -> tuple[pd.DataFrame, ProcessingReport]:
    """Drop incomplete analytical rows and build a structured report."""
    dropped_rows_by_reason, valid_rows = _missing_row_counts(validated_df)
    retained_df = validated_df.loc[valid_rows].copy()
    ensure_non_empty_dataframe(retained_df)

    duplicate_mask = retained_df["cpg_id"].duplicated(keep=False)
    duplicate_groups = int(retained_df.loc[duplicate_mask, "cpg_id"].nunique())
    duplicate_extra_rows = int(retained_df["cpg_id"].duplicated(keep="first").sum())

    report = ProcessingReport(
        source_file=source_file,
        uploaded_at=uploaded_at,
        input_row_count=int(len(validated_df)),
        retained_row_count=int(len(retained_df)),
        dropped_row_count=int((~valid_rows).sum()),
        dropped_rows_by_reason=dropped_rows_by_reason,
        duplicate_cpg_id_groups=duplicate_groups,
        duplicate_cpg_id_extra_rows=duplicate_extra_rows,
    )

    retained_df["source_file"] = source_file
    retained_df["uploaded_at"] = uploaded_at
    return retained_df.reset_index(drop=True), report


def process_methylation_upload(
    uploaded_file: BinaryIO,
    source_name: str | None = None,
) -> ProcessedUpload:
    """Load, validate, normalize, and report on a methylation upload."""
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
        validated = validate_upload(normalized)
        uploaded_at = datetime.now(timezone.utc).isoformat()
        retained_df, report = _build_processing_report(
            validated_df=validated,
            source_file=name,
            uploaded_at=uploaded_at,
        )
        return ProcessedUpload(normalized_df=retained_df, report=report)
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


def load_methylation_file(uploaded_file: BinaryIO, source_name: str | None = None) -> pd.DataFrame:
    """Load a methylation upload and return the retained normalized dataframe."""
    return process_methylation_upload(uploaded_file=uploaded_file, source_name=source_name).normalized_df
