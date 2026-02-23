"""Public core API for app orchestration."""

from __future__ import annotations

import pandas as pd

from core.analyze import analyze_methylation, qc_summary
from core.config import AppConfig, get_app_config
from core.ingest import IngestError, load_methylation_file
from core.transform import canonicalize_columns, normalize_upload, select_canonical_columns
from core.validate import ValidationError, ValidationConfig, validate_upload


def run_pipeline(df: pd.DataFrame) -> dict[str, float]:
    """Run canonicalization, validation, and analysis over an in-memory dataframe."""
    normalized = normalize_upload(df)
    validated = validate_upload(normalized)
    return analyze_methylation(validated)

__all__ = [
    "AppConfig",
    "IngestError",
    "ValidationConfig",
    "ValidationError",
    "analyze_methylation",
    "canonicalize_columns",
    "get_app_config",
    "load_methylation_file",
    "normalize_upload",
    "qc_summary",
    "run_pipeline",
    "select_canonical_columns",
    "validate_upload",
]
