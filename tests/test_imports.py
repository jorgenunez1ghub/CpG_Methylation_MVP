"""Smoke tests for clean core imports."""

from __future__ import annotations

from typing import get_args


def test_core_module_imports() -> None:
    import cpg_methylation_mvp.core.analyze  # noqa: F401
    import cpg_methylation_mvp.core.ingest  # noqa: F401
    import cpg_methylation_mvp.core.io  # noqa: F401
    import cpg_methylation_mvp.core.panels  # noqa: F401
    import cpg_methylation_mvp.core.transform  # noqa: F401
    import cpg_methylation_mvp.core.validate  # noqa: F401


def test_public_core_api_imports() -> None:
    from cpg_methylation_mvp.core import (
        DEFAULT_DUPLICATE_POLICY,
        DEFAULT_MAX_UPLOAD_BYTES,
        PROCESSING_REPORT_VERSION,
        DuplicatePolicy,
        ProcessedUpload,
        ProcessingReport,
        analyze_methylation,
        duplicate_review_table,
        evaluate_panel,
        load_methylation_file,
        load_panel,
        normalize_upload,
        panel_report_table,
        process_methylation_upload,
        validate_upload,
    )

    assert callable(load_methylation_file)
    assert callable(normalize_upload)
    assert callable(process_methylation_upload)
    assert callable(validate_upload)
    assert callable(analyze_methylation)
    assert callable(duplicate_review_table)
    assert callable(load_panel)
    assert callable(evaluate_panel)
    assert callable(panel_report_table)
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


def test_context_helper_api_imports() -> None:
    from cpg_methylation_mvp.context import (
        DEFAULT_EVIDENCE_INDEX_PATH,
        DEFAULT_EXTERNAL_SOURCE_POLICY_PATH,
        Chunk,
        DatasetSummary,
        EvidenceContractError,
        KeywordRetriever,
        MockRetriever,
        build_context,
        build_default_workflow_context,
        format_citations,
        load_evidence_chunks,
        load_external_source_policy,
    )

    assert DEFAULT_EVIDENCE_INDEX_PATH.name == "workflow_01_context_chunks.json"
    assert DEFAULT_EXTERNAL_SOURCE_POLICY_PATH.name == "external_source_policy.json"
    assert Chunk.__name__ == "Chunk"
    assert DatasetSummary.__name__ == "DatasetSummary"
    assert EvidenceContractError.__name__ == "EvidenceContractError"
    assert callable(build_context)
    assert callable(build_default_workflow_context)
    assert callable(format_citations)
    assert callable(load_evidence_chunks)
    assert callable(load_external_source_policy)
    assert KeywordRetriever.__name__ == "KeywordRetriever"
    assert MockRetriever.__name__ == "MockRetriever"
