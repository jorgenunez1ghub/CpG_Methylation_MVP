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

DuplicatePolicy = Literal[
    "preserve_rows_and_warn",
    "reject_duplicates",
    "aggregate_mean_when_metadata_match",
]
DEFAULT_DUPLICATE_POLICY: DuplicatePolicy = "preserve_rows_and_warn"
DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024
PROCESSING_REPORT_VERSION = "2.0"
_DUPLICATE_REVIEW_EXCLUDED_COLUMNS = {"cpg_id", "beta", "source_file", "uploaded_at"}
_AGGREGATION_DUPLICATE_POLICY: DuplicatePolicy = "aggregate_mean_when_metadata_match"
_AGGREGATION_METADATA_COLUMNS = ("chrom", "pos", "gene", "pval")


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
    aggregation_applied: bool = False
    pre_duplicate_policy_row_count: int = 0
    aggregated_duplicate_cpg_id_groups: int = 0
    aggregated_duplicate_input_rows: int = 0
    aggregation_output_row_count: int = 0
    aggregation_blocked_conflict_groups: int = 0

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
    """Normalized upload dataframe plus structured report and optional aggregation audit."""

    normalized_df: pd.DataFrame
    report: ProcessingReport
    aggregation_audit_df: pd.DataFrame | None = None


@dataclass(frozen=True)
class _DuplicatePolicyResult:
    """Private result object for duplicate-policy application."""

    output_df: pd.DataFrame
    duplicate_groups: int
    duplicate_extra_rows: int
    duplicate_metadata_conflict_groups: int
    aggregation_applied: bool = False
    aggregated_duplicate_cpg_id_groups: int = 0
    aggregated_duplicate_input_rows: int = 0
    aggregation_output_row_count: int = 0
    aggregation_blocked_conflict_groups: int = 0
    aggregation_audit_df: pd.DataFrame | None = None


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

    conflict_groups = 0
    duplicate_groups = df.loc[duplicate_mask].groupby("cpg_id", dropna=False)
    for _, group in duplicate_groups:
        if _duplicate_metadata_conflict_columns(group):
            conflict_groups += 1

    return conflict_groups


def _duplicate_metadata_columns(df: pd.DataFrame) -> list[str]:
    """Return metadata columns relevant for duplicate-group conflict review."""
    return [column for column in _AGGREGATION_METADATA_COLUMNS if column in df.columns]


def _duplicate_metadata_conflict_columns(group: pd.DataFrame) -> list[str]:
    """Return metadata columns whose non-empty values disagree within a duplicate group."""
    conflict_columns: list[str] = []
    for column in _duplicate_metadata_columns(group):
        non_null_values = group.loc[_non_empty_value_mask(group[column]), column].astype(str).str.strip()
        distinct_values = {value for value in non_null_values if value != ""}
        if len(distinct_values) > 1:
            conflict_columns.append(column)
    return conflict_columns


def _non_empty_value_mask(series: pd.Series) -> pd.Series:
    """Return a mask for values that are not null/blank after string trim."""
    return series.notna() & series.astype(str).str.strip().ne("")


def _carried_metadata_value(group: pd.DataFrame, column: str) -> object:
    """Return the single carried metadata value for a duplicate group, if any."""
    if column not in group.columns:
        return pd.NA

    mask = _non_empty_value_mask(group[column])
    if not bool(mask.any()):
        return pd.NA
    return group.loc[mask, column].iloc[0]


def _empty_aggregation_audit_df() -> pd.DataFrame:
    """Return an empty aggregation audit dataframe with stable columns."""
    return pd.DataFrame(
        columns=[
            "cpg_id",
            "source_row_count",
            "beta_min",
            "beta_max",
            "beta_mean",
            *_AGGREGATION_METADATA_COLUMNS,
            "source_file",
            "uploaded_at",
            "aggregation_rule",
        ]
    )


def duplicate_review_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return duplicate-row details for manual review without aggregating values."""
    duplicate_mask = df["cpg_id"].duplicated(keep=False)
    review_columns = list(df.columns) + [
        "duplicate_group_row_count",
        "duplicate_group_extra_rows",
        "duplicate_group_has_metadata_conflict",
        "duplicate_group_conflict_columns",
        "duplicate_group_beta_min",
        "duplicate_group_beta_max",
    ]
    if not bool(duplicate_mask.any()):
        return pd.DataFrame(columns=review_columns)

    review_df = df.loc[duplicate_mask].copy()
    group_sizes = review_df.groupby("cpg_id", dropna=False)["cpg_id"].transform("size").astype(int)
    review_df["duplicate_group_row_count"] = group_sizes
    review_df["duplicate_group_extra_rows"] = group_sizes - 1
    review_df["duplicate_group_beta_min"] = review_df.groupby("cpg_id", dropna=False)["beta"].transform("min")
    review_df["duplicate_group_beta_max"] = review_df.groupby("cpg_id", dropna=False)["beta"].transform("max")

    conflict_columns_by_cpg = {
        cpg_id: "|".join(_duplicate_metadata_conflict_columns(group))
        for cpg_id, group in review_df.groupby("cpg_id", dropna=False)
    }
    review_df["duplicate_group_conflict_columns"] = review_df["cpg_id"].map(conflict_columns_by_cpg).fillna("")
    review_df["duplicate_group_has_metadata_conflict"] = review_df["duplicate_group_conflict_columns"] != ""

    return review_df.reset_index(drop=True)


def _aggregate_duplicate_groups(
    retained_df: pd.DataFrame,
    source_file: str,
    uploaded_at: str,
) -> tuple[pd.DataFrame, pd.DataFrame, int, int]:
    """Aggregate duplicate groups by mean beta when metadata values do not conflict."""
    working_df = retained_df.copy().reset_index(drop=True)
    duplicate_mask = working_df["cpg_id"].duplicated(keep=False)
    if not bool(duplicate_mask.any()):
        return retained_df.reset_index(drop=True), _empty_aggregation_audit_df(), 0, 0

    working_df["_aggregation_input_order"] = range(len(working_df))
    duplicate_groups = working_df.loc[duplicate_mask].groupby("cpg_id", dropna=False, sort=False)

    aggregated_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    for _, group in duplicate_groups:
        carried_metadata = {
            column: _carried_metadata_value(group, column)
            for column in _AGGREGATION_METADATA_COLUMNS
        }
        aggregated_rows.append(
            {
                "cpg_id": group["cpg_id"].iloc[0],
                "beta": float(group["beta"].mean()),
                "_aggregation_input_order": int(group["_aggregation_input_order"].min()),
                **carried_metadata,
            }
        )
        audit_rows.append(
            {
                "cpg_id": group["cpg_id"].iloc[0],
                "source_row_count": int(len(group)),
                "beta_min": float(group["beta"].min()),
                "beta_max": float(group["beta"].max()),
                "beta_mean": float(group["beta"].mean()),
                **carried_metadata,
                "source_file": source_file,
                "uploaded_at": uploaded_at,
                "aggregation_rule": _AGGREGATION_DUPLICATE_POLICY,
            }
        )

    non_duplicate_df = working_df.loc[~duplicate_mask].copy()
    aggregated_df = pd.DataFrame(aggregated_rows)
    output_df = (
        pd.concat([non_duplicate_df, aggregated_df], ignore_index=True, sort=False)
        .sort_values("_aggregation_input_order")
        .drop(columns="_aggregation_input_order")
    )
    output_columns = [column for column in retained_df.columns if column in output_df.columns]
    audit_df = pd.DataFrame(audit_rows, columns=_empty_aggregation_audit_df().columns)
    aggregated_duplicate_input_rows = int(duplicate_mask.sum())
    aggregated_duplicate_cpg_id_groups = int(len(aggregated_rows))
    return (
        output_df.loc[:, output_columns].reset_index(drop=True),
        audit_df.reset_index(drop=True),
        aggregated_duplicate_cpg_id_groups,
        aggregated_duplicate_input_rows,
    )


def _apply_duplicate_policy_with_context(
    retained_df: pd.DataFrame,
    duplicate_policy: DuplicatePolicy,
    source_file: str,
    uploaded_at: str,
) -> _DuplicatePolicyResult:
    """Apply duplicate policy with additional context needed for aggregation audits."""
    duplicate_groups, duplicate_extra_rows = _duplicate_counts(retained_df)
    duplicate_metadata_conflict_groups = _duplicate_metadata_conflict_groups(retained_df)

    if duplicate_policy == "reject_duplicates" and duplicate_groups > 0:
        raise ValidationError(
            f"Found {duplicate_groups} duplicated cpg_id value(s). "
            "Selected duplicate policy requires unique cpg_id values."
        )

    if duplicate_policy == _AGGREGATION_DUPLICATE_POLICY:
        if duplicate_metadata_conflict_groups > 0:
            raise ValidationError(
                f"Cannot aggregate {duplicate_metadata_conflict_groups} duplicated cpg_id group(s) because "
                "optional metadata values conflict. Re-run with preserve_rows_and_warn to inspect them."
            )
        aggregated_df, audit_df, aggregated_groups, aggregated_input_rows = _aggregate_duplicate_groups(
            retained_df=retained_df,
            source_file=source_file,
            uploaded_at=uploaded_at,
        )
        return _DuplicatePolicyResult(
            output_df=aggregated_df,
            duplicate_groups=duplicate_groups,
            duplicate_extra_rows=duplicate_extra_rows,
            duplicate_metadata_conflict_groups=duplicate_metadata_conflict_groups,
            aggregation_applied=aggregated_groups > 0,
            aggregated_duplicate_cpg_id_groups=aggregated_groups,
            aggregated_duplicate_input_rows=aggregated_input_rows,
            aggregation_output_row_count=int(len(aggregated_df)),
            aggregation_blocked_conflict_groups=0,
            aggregation_audit_df=None if audit_df.empty else audit_df,
        )

    return _DuplicatePolicyResult(
        output_df=retained_df.reset_index(drop=True),
        duplicate_groups=duplicate_groups,
        duplicate_extra_rows=duplicate_extra_rows,
        duplicate_metadata_conflict_groups=duplicate_metadata_conflict_groups,
        aggregation_output_row_count=int(len(retained_df)),
    )


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
) -> tuple[pd.DataFrame, ProcessingReport, pd.DataFrame | None]:
    """Drop incomplete analytical rows, apply duplicate policy, and build a report."""
    dropped_rows_by_reason, valid_rows = _missing_row_counts(validated_df)
    pre_policy_df = validated_df.loc[valid_rows].copy()
    ensure_non_empty_dataframe(pre_policy_df)

    duplicate_policy_result = _apply_duplicate_policy_with_context(
        retained_df=pre_policy_df,
        duplicate_policy=duplicate_policy,
        source_file=source_file,
        uploaded_at=uploaded_at,
    )
    output_df = duplicate_policy_result.output_df.copy()

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
        retained_row_count=int(len(output_df)),
        dropped_row_count=int((~valid_rows).sum()),
        dropped_rows_by_reason=dropped_rows_by_reason,
        duplicate_cpg_id_groups=duplicate_policy_result.duplicate_groups,
        duplicate_cpg_id_extra_rows=duplicate_policy_result.duplicate_extra_rows,
        duplicate_metadata_conflict_groups=duplicate_policy_result.duplicate_metadata_conflict_groups,
        duplicate_policy=duplicate_policy,
        aggregation_applied=duplicate_policy_result.aggregation_applied,
        pre_duplicate_policy_row_count=int(len(pre_policy_df)),
        aggregated_duplicate_cpg_id_groups=duplicate_policy_result.aggregated_duplicate_cpg_id_groups,
        aggregated_duplicate_input_rows=duplicate_policy_result.aggregated_duplicate_input_rows,
        aggregation_output_row_count=duplicate_policy_result.aggregation_output_row_count,
        aggregation_blocked_conflict_groups=duplicate_policy_result.aggregation_blocked_conflict_groups,
    )

    output_df["source_file"] = source_file
    output_df["uploaded_at"] = uploaded_at
    return output_df.reset_index(drop=True), report, duplicate_policy_result.aggregation_audit_df


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
        if "mixed_delimiters_inconsistent_structure" in parse_result.parse_warnings:
            raise IngestError(
                "Mixed delimiters produced inconsistent row structure. "
                "Normalize the file to a single delimiter before upload."
            )
        ensure_non_empty_dataframe(parse_result.dataframe)

        normalized = normalize_upload(parse_result.dataframe)
        validated = validate_upload(normalized)
        uploaded_at = datetime.now(timezone.utc).isoformat()
        retained_df, report, aggregation_audit_df = _build_processing_report(
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
        return ProcessedUpload(
            normalized_df=retained_df,
            report=report,
            aggregation_audit_df=aggregation_audit_df,
        )
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
