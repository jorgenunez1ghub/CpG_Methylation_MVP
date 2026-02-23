"""Public core API for app orchestration."""

from core.analyze import analyze_methylation, qc_summary
from core.config import APP_CAPTION, APP_DESCRIPTION, APP_LAYOUT, APP_TITLE, PAGE_TITLE
from core.ingest import IngestError, load_methylation_file
from core.transform import canonicalize_columns, normalize_upload, select_canonical_columns
from core.validate import ValidationError, ValidationConfig, validate_upload

__all__ = [
    "IngestError",
    "APP_CAPTION",
    "APP_DESCRIPTION",
    "APP_LAYOUT",
    "APP_TITLE",
    "PAGE_TITLE",
    "ValidationConfig",
    "ValidationError",
    "analyze_methylation",
    "canonicalize_columns",
    "load_methylation_file",
    "normalize_upload",
    "qc_summary",
    "select_canonical_columns",
    "validate_upload",
]
