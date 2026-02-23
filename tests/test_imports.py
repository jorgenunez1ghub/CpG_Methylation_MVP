"""Smoke tests for clean core imports."""

from __future__ import annotations


def test_core_module_imports() -> None:
    import cpg_methylation_mvp.core.analyze  # noqa: F401
    import cpg_methylation_mvp.core.ingest  # noqa: F401
    import cpg_methylation_mvp.core.io  # noqa: F401
    import cpg_methylation_mvp.core.transform  # noqa: F401
    import cpg_methylation_mvp.core.validate  # noqa: F401


def test_public_core_api_imports() -> None:
    from cpg_methylation_mvp.core import analyze_methylation, load_methylation_file, normalize_upload, validate_upload

    assert callable(load_methylation_file)
    assert callable(normalize_upload)
    assert callable(validate_upload)
    assert callable(analyze_methylation)
