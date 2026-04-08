"""Smoke tests for clean core imports."""

from __future__ import annotations

from typing import get_args


def test_core_module_imports() -> None:
    import cpg_methylation_mvp.core.analyze  # noqa: F401
    import cpg_methylation_mvp.core.ingest  # noqa: F401
    import cpg_methylation_mvp.core.io  # noqa: F401
    import cpg_methylation_mvp.core.transform  # noqa: F401
    import cpg_methylation_mvp.core.validate  # noqa: F401


def test_public_core_api_imports() -> None:
    from cpg_methylation_mvp.core import (
        DEFAULT_DUPLICATE_POLICY,
        DEFAULT_MAX_UPLOAD_BYTES,
        DuplicatePolicy,
        PROCESSING_REPORT_VERSION,
        ProcessedUpload,
        ProcessingReport,
        analyze_methylation,
        duplicate_review_table,
        load_methylation_file,
        normalize_upload,
        process_methylation_upload,
        validate_upload,
    )

    assert callable(load_methylation_file)
    assert callable(normalize_upload)
    assert callable(process_methylation_upload)
    assert callable(validate_upload)
    assert callable(analyze_methylation)
    assert callable(duplicate_review_table)
    assert DEFAULT_DUPLICATE_POLICY == "preserve_rows_and_warn"
    assert DEFAULT_MAX_UPLOAD_BYTES == 25 * 1024 * 1024
    assert PROCESSING_REPORT_VERSION == "2.0"
    assert ProcessedUpload.__name__ == "ProcessedUpload"
    assert ProcessingReport.__name__ == "ProcessingReport"
    assert "aggregate_mean_when_metadata_match" in get_args(DuplicatePolicy)
    assert "reject_duplicates" in get_args(DuplicatePolicy)


def test_streamlit_entrypoint_import_is_safe() -> None:
    import app.main

    assert callable(app.main.main)
