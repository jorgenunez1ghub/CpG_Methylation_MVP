"""Public core API for app orchestration."""

from .analyze import analyze_methylation, qc_summary
from .ingest import (
    DEFAULT_DUPLICATE_POLICY,
    DEFAULT_MAX_UPLOAD_BYTES,
    DuplicatePolicy,
    IngestError,
    PROCESSING_REPORT_VERSION,
    ProcessedUpload,
    ProcessingReport,
    duplicate_review_table,
    load_methylation_file,
    process_methylation_upload,
)
from .panels import evaluate_panel, load_panel, panel_report_table
from .transform import canonicalize_columns, normalize_upload, select_canonical_columns
from .validate import ValidationError, ValidationConfig, validate_upload

__all__ = [
    "DEFAULT_DUPLICATE_POLICY",
    "DEFAULT_MAX_UPLOAD_BYTES",
    "DuplicatePolicy",
    "IngestError",
    "PROCESSING_REPORT_VERSION",
    "ProcessedUpload",
    "ProcessingReport",
    "ValidationConfig",
    "ValidationError",
    "analyze_methylation",
    "evaluate_panel",
    "canonicalize_columns",
    "duplicate_review_table",
    "load_methylation_file",
    "load_panel",
    "normalize_upload",
    "panel_report_table",
    "process_methylation_upload",
    "qc_summary",
    "select_canonical_columns",
    "validate_upload",
]
