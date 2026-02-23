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
    if df.empty:
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
    numeric_beta = pd.to_numeric(df[beta_column], errors="coerce")
    invalid_mask = numeric_beta.isna() & df[beta_column].notna()
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



def validate_upload(
    df: pd.DataFrame,
    config: ValidationConfig | None = None,
) -> pd.DataFrame:
    """Validate normalized upload dataframe and return validated copy."""
    cfg = config or ValidationConfig()
    ensure_non_empty_dataframe(df)
    ensure_required_columns(df, cfg.required_columns)

    validated = df.copy()
    validated["cpg_id"] = validated["cpg_id"].astype(str).str.strip()

    ensure_beta_numeric(validated, beta_column="beta")
    validated["beta"] = pd.to_numeric(validated["beta"], errors="coerce")
    ensure_non_empty_dataframe(validated.dropna(subset=["cpg_id", "beta"]))
    ensure_beta_in_range(validated, beta_column="beta")
    return validated
