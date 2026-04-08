"""Smoke tests for clean core imports."""

from __future__ import annotations


def test_core_module_imports() -> None:
    import cpg_methylation_mvp.core.analyze  # noqa: F401
    import cpg_methylation_mvp.core.ingest  # noqa: F401
    import cpg_methylation_mvp.core.io  # noqa: F401
    import cpg_methylation_mvp.core.transform  # noqa: F401
    import cpg_methylation_mvp.core.validate  # noqa: F401


def test_public_core_api_imports() -> None:
    from cpg_methylation_mvp.core import (
        ProcessedUpload,
        ProcessingReport,
        analyze_methylation,
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
    assert ProcessedUpload.__name__ == "ProcessedUpload"
    assert ProcessingReport.__name__ == "ProcessingReport"


def test_streamlit_entrypoint_import_is_safe() -> None:
    import app.main

    assert callable(app.main.main)
