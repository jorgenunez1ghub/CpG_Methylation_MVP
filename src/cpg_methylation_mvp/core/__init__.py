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
    "canonicalize_columns",
    "duplicate_review_table",
    "load_methylation_file",
    "normalize_upload",
    "process_methylation_upload",
    "qc_summary",
    "select_canonical_columns",
    "validate_upload",
]
