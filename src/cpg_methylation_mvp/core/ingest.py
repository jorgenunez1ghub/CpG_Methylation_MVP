"""Ingestion pipeline for methylation upload files."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from typing import BinaryIO, Literal
from uuid import uuid4

import pandas as pd

from .io import read_table_bytes
from .transform import normalize_upload
from .validate import (
    ValidationError,
    ensure_non_empty_dataframe,
    required_value_masks,
    validate_upload,
)

DuplicatePolicy = Literal["preserve_rows_and_warn", "reject_duplicates"]
DEFAULT_DUPLICATE_POLICY: DuplicatePolicy = "preserve_rows_and_warn"
DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024
PROCESSING_REPORT_VERSION = "1.0"


class IngestError(ValidationError):
    """Raised for parsing and ingestion errors."""


@dataclass(frozen=True)
class ProcessingReport:
    """Structured processing report for upload transparency."""

    report_version: str
    run_id: str
    source_file: str
    uploaded_at: str
    input_sha256: str
    parse_strategy: str
    delimiter_used: str | None
    recovered_from_extension_mismatch: bool
    parse_warnings: tuple[str, ...]
    input_row_count: int
    retained_row_count: int
    dropped_row_count: int
    dropped_rows_by_reason: dict[str, int]
    duplicate_cpg_id_groups: int
    duplicate_cpg_id_extra_rows: int
    duplicate_metadata_conflict_groups: int
    duplicate_policy: DuplicatePolicy = DEFAULT_DUPLICATE_POLICY

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation of the report."""
        return asdict(self)

    def to_flat_dict(self) -> dict[str, object]:
        """Return a flat dictionary that is easy to write as one CSV row."""
        flattened = self.to_dict()
        dropped_rows_by_reason = flattened.pop("dropped_rows_by_reason")
        for reason, count in dropped_rows_by_reason.items():
            flattened[f"dropped_rows_{reason}"] = count
        flattened["parse_warnings"] = " | ".join(self.parse_warnings)
        return flattened


@dataclass(frozen=True)
class ProcessedUpload:
    """Normalized upload dataframe plus its structured processing report."""

    normalized_df: pd.DataFrame
    report: ProcessingReport


def _input_sha256(raw_bytes: bytes) -> str:
    """Return a stable checksum of the uploaded file bytes."""
    return hashlib.sha256(raw_bytes).hexdigest()


def _missing_row_counts(validated_df: pd.DataFrame) -> tuple[dict[str, int], pd.Series]:
    """Return exclusive dropped-row counts and the retained-row mask."""
    missing_cpg_id, missing_beta, valid_rows = required_value_masks(validated_df)
    dropped_rows_by_reason = {
        "missing_cpg_id": int((missing_cpg_id & ~missing_beta).sum()),
        "missing_beta": int((missing_beta & ~missing_cpg_id).sum()),
        "missing_cpg_id_and_beta": int((missing_cpg_id & missing_beta).sum()),
    }
    return dropped_rows_by_reason, valid_rows


def _duplicate_counts(df: pd.DataFrame) -> tuple[int, int]:
    """Return duplicate cpg_id group count and extra duplicate row count."""
    duplicate_mask = df["cpg_id"].duplicated(keep=False)
    duplicate_groups = int(df.loc[duplicate_mask, "cpg_id"].nunique())
    duplicate_extra_rows = int(df["cpg_id"].duplicated(keep="first").sum())
    return duplicate_groups, duplicate_extra_rows


def _duplicate_metadata_conflict_groups(df: pd.DataFrame) -> int:
    """Return the number of duplicate cpg_id groups with conflicting metadata."""
    duplicate_mask = df["cpg_id"].duplicated(keep=False)
    if not bool(duplicate_mask.any()):
        return 0

    metadata_columns = [column for column in df.columns if column not in {"cpg_id", "beta"}]
    if not metadata_columns:
        return 0

    conflict_groups = 0
    duplicate_groups = df.loc[duplicate_mask].groupby("cpg_id", dropna=False)
    for _, group in duplicate_groups:
        has_conflict = False
        for column in metadata_columns:
            non_null_values = group[column].dropna().astype(str).str.strip()
            distinct_values = {value for value in non_null_values if value != ""}
            if len(distinct_values) > 1:
                has_conflict = True
                break
        if has_conflict:
            conflict_groups += 1

    return conflict_groups


def _enforce_duplicate_policy(
    retained_df: pd.DataFrame,
    duplicate_policy: DuplicatePolicy,
) -> tuple[int, int, int]:
    """Apply the configured duplicate policy and return duplicate diagnostics."""
    duplicate_groups, duplicate_extra_rows = _duplicate_counts(retained_df)
    duplicate_metadata_conflict_groups = _duplicate_metadata_conflict_groups(retained_df)

    if duplicate_policy == "reject_duplicates" and duplicate_groups > 0:
        raise ValidationError(
            f"Found {duplicate_groups} duplicated cpg_id value(s). "
            "Selected duplicate policy requires unique cpg_id values."
        )

    return duplicate_groups, duplicate_extra_rows, duplicate_metadata_conflict_groups


def _build_processing_report(
    validated_df: pd.DataFrame,
    source_file: str,
    uploaded_at: str,
    input_sha256: str,
    parse_strategy: str,
    delimiter_used: str | None,
    recovered_from_extension_mismatch: bool,
    parse_warnings: tuple[str, ...],
    duplicate_policy: DuplicatePolicy,
) -> tuple[pd.DataFrame, ProcessingReport]:
    """Drop incomplete analytical rows, apply duplicate policy, and build a report."""
    dropped_rows_by_reason, valid_rows = _missing_row_counts(validated_df)
    retained_df = validated_df.loc[valid_rows].copy()
    ensure_non_empty_dataframe(retained_df)

    duplicate_groups, duplicate_extra_rows, duplicate_metadata_conflict_groups = _enforce_duplicate_policy(
        retained_df=retained_df,
        duplicate_policy=duplicate_policy,
    )

    report = ProcessingReport(
        report_version=PROCESSING_REPORT_VERSION,
        run_id=str(uuid4()),
        source_file=source_file,
        uploaded_at=uploaded_at,
        input_sha256=input_sha256,
        parse_strategy=parse_strategy,
        delimiter_used=delimiter_used,
        recovered_from_extension_mismatch=recovered_from_extension_mismatch,
        parse_warnings=parse_warnings,
        input_row_count=int(len(validated_df)),
        retained_row_count=int(len(retained_df)),
        dropped_row_count=int((~valid_rows).sum()),
        dropped_rows_by_reason=dropped_rows_by_reason,
        duplicate_cpg_id_groups=duplicate_groups,
        duplicate_cpg_id_extra_rows=duplicate_extra_rows,
        duplicate_metadata_conflict_groups=duplicate_metadata_conflict_groups,
        duplicate_policy=duplicate_policy,
    )

    retained_df["source_file"] = source_file
    retained_df["uploaded_at"] = uploaded_at
    return retained_df.reset_index(drop=True), report


def process_methylation_upload(
    uploaded_file: BinaryIO,
    source_name: str | None = None,
    duplicate_policy: DuplicatePolicy = DEFAULT_DUPLICATE_POLICY,
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
) -> ProcessedUpload:
    """Load, validate, normalize, and report on a methylation upload."""
    if uploaded_file is None:
        raise IngestError("No file was provided. Upload a CSV/TSV file to continue.")

    try:
        name = source_name or getattr(uploaded_file, "name", "uploaded_file")
        raw_bytes = uploaded_file.read()
        if not raw_bytes:
            raise IngestError("The uploaded file is empty. Please choose a non-empty CSV/TSV file.")
        if len(raw_bytes) > max_upload_bytes:
            limit_mb = max_upload_bytes / (1024 * 1024)
            raise IngestError(
                f"The uploaded file exceeds the {limit_mb:.0f} MB limit. "
                "Use a smaller file or raise the deployment upload limit intentionally."
            )

        parse_result = read_table_bytes(raw_bytes=raw_bytes, filename=name)
        ensure_non_empty_dataframe(parse_result.dataframe)

        normalized = normalize_upload(parse_result.dataframe)
        validated = validate_upload(normalized)
        uploaded_at = datetime.now(timezone.utc).isoformat()
        retained_df, report = _build_processing_report(
            validated_df=validated,
            source_file=name,
            uploaded_at=uploaded_at,
            input_sha256=_input_sha256(raw_bytes),
            parse_strategy=parse_result.parse_strategy,
            delimiter_used=parse_result.delimiter_used,
            recovered_from_extension_mismatch=parse_result.recovered_from_extension_mismatch,
            parse_warnings=parse_result.parse_warnings,
            duplicate_policy=duplicate_policy,
        )
        return ProcessedUpload(normalized_df=retained_df, report=report)
    except pd.errors.EmptyDataError as exc:
        raise IngestError(
            "The uploaded file appears empty. Please upload a CSV/TSV file with header and rows."
        ) from exc
    except pd.errors.ParserError as exc:
        raise IngestError(
            "Could not parse the uploaded file. Check for malformed quotes or inconsistent delimiter structure."
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
