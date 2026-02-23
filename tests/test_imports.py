"""Smoke tests for clean core imports."""

from __future__ import annotations


def test_core_module_imports() -> None:
    import core.analyze  # noqa: F401
    import core.ingest  # noqa: F401
    import core.io  # noqa: F401
    import core.transform  # noqa: F401
    import core.validate  # noqa: F401


def test_public_core_api_imports() -> None:
    from core import analyze_methylation, load_methylation_file, normalize_upload, validate_upload

    assert callable(load_methylation_file)
    assert callable(normalize_upload)
    assert callable(validate_upload)
    assert callable(analyze_methylation)
