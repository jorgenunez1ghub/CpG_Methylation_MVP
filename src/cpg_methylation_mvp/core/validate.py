"""Validation helpers for methylation upload inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


class ValidationError(ValueError):
    """Raised when upload data cannot be validated."""


@dataclass(frozen=True)
class ValidationConfig:
    """Configuration for required canonical columns."""

    required_columns: tuple[str, ...] = ("cpg_id", "beta")


def ensure_non_empty_dataframe(df: pd.DataFrame) -> None:
    """Raise when the dataframe has no rows."""
    if len(df.index) == 0:
        raise ValidationError(
            "The uploaded file is empty. Please provide a CSV/TSV with at least one data row."
        )


def ensure_required_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    """Raise when required columns are missing."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValidationError(
            "Missing required column(s): "
            f"{missing_text}. Include these columns (or known aliases) and upload again."
        )


def ensure_beta_numeric(df: pd.DataFrame, beta_column: str = "beta") -> None:
    """Raise when beta values cannot be parsed as numeric values."""
    cleaned_beta = df[beta_column]
    if pd.api.types.is_object_dtype(cleaned_beta) or pd.api.types.is_string_dtype(cleaned_beta):
        cleaned_beta = cleaned_beta.astype("string").str.strip().replace("", pd.NA)

    numeric_beta = pd.to_numeric(cleaned_beta, errors="coerce")
    invalid_mask = numeric_beta.isna() & cleaned_beta.notna()
    invalid_count = int(invalid_mask.sum())

    if invalid_count > 0:
        raise ValidationError(
            f"Found {invalid_count} non-numeric beta value(s). "
            "Beta values must be numeric between 0 and 1."
        )


def ensure_beta_in_range(df: pd.DataFrame, beta_column: str = "beta") -> None:
    """Raise when beta values are outside [0, 1]."""
    out_of_range_mask = (df[beta_column] < 0) | (df[beta_column] > 1)
    out_of_range_count = int(out_of_range_mask.sum())

    if out_of_range_count > 0:
        raise ValidationError(
            f"Found {out_of_range_count} beta value(s) outside [0, 1]. "
            "Fix out-of-range values and re-upload."
        )


def required_value_masks(
    df: pd.DataFrame,
    cpg_id_column: str = "cpg_id",
    beta_column: str = "beta",
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return masks for missing required fields and valid analytical rows."""
    missing_cpg_id = df[cpg_id_column].isna() | df[cpg_id_column].eq("")
    missing_beta = df[beta_column].isna()
    valid_rows = ~(missing_cpg_id | missing_beta)
    return missing_cpg_id, missing_beta, valid_rows


def ensure_at_least_one_valid_required_row(df: pd.DataFrame) -> None:
    """Raise when no rows remain after excluding missing required values."""
    _, _, valid_rows = required_value_masks(df)
    if not bool(valid_rows.any()):
        raise ValidationError(
            "No valid rows remain after excluding rows missing required cpg_id/beta values."
        )



def validate_upload(
    df: pd.DataFrame,
    config: ValidationConfig | None = None,
) -> pd.DataFrame:
    """Validate normalized upload dataframe and return validated copy."""
    cfg = config or ValidationConfig()
    ensure_non_empty_dataframe(df)
    ensure_required_columns(df, cfg.required_columns)

    validated = df.copy()
    validated["cpg_id"] = validated["cpg_id"].astype("string").str.strip()

    ensure_beta_numeric(validated, beta_column="beta")
    beta_series = validated["beta"]
    if pd.api.types.is_object_dtype(beta_series) or pd.api.types.is_string_dtype(beta_series):
        beta_series = beta_series.astype("string").str.strip().replace("", pd.NA)
    validated["beta"] = pd.to_numeric(beta_series, errors="coerce")
    ensure_at_least_one_valid_required_row(validated)
    ensure_beta_in_range(validated, beta_column="beta")
    return validated
