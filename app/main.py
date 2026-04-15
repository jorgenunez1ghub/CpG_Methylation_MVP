"""Streamlit entrypoint for CpG methylation MVP."""

from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from app.ui_config import APP_CAPTION, APP_DESCRIPTION, APP_LAYOUT, APP_TITLE, PAGE_TITLE

from cpg_methylation_mvp.context import (
    ContextPackage,
    EvidenceContractError,
    build_default_workflow_context,
)
from cpg_methylation_mvp.core import (
    DEFAULT_DUPLICATE_POLICY,
    DEFAULT_MAX_UPLOAD_BYTES,
    DuplicatePolicy,
    IngestError,
    ProcessedUpload,
    ProcessingReport,
    analyze_methylation,
    duplicate_review_table,
    load_panel,
    process_methylation_upload,
    structured_interpretation,
)

_DUPLICATE_POLICY_LABELS: dict[str, DuplicatePolicy] = {
    "Preserve rows and warn": "preserve_rows_and_warn",
    "Reject duplicates": "reject_duplicates",
    "Aggregate duplicates (mean beta, matching metadata only)": "aggregate_mean_when_metadata_match",
}
_DUPLICATE_POLICY_HELP = {
    "preserve_rows_and_warn": "Keeps all rows for QC review and flags duplicates explicitly.",
    "reject_duplicates": "Stops ingestion when any cpg_id appears more than once.",
    "aggregate_mean_when_metadata_match": (
        "Collapses duplicate cpg_id rows by mean beta only when optional metadata values do not conflict."
    ),
}
_WORKFLOW_PANEL_PATH = Path("data/panels/core_demo_panel.csv")
_WORKFLOW_EVIDENCE_PATH = Path("data/evidence/workflow_01_context_chunks.json")
_LOGGER = logging.getLogger(__name__)


def process_methylation_upload_cached(
    raw_bytes: bytes,
    filename: str,
    duplicate_policy: DuplicatePolicy,
) -> ProcessedUpload:
    """Cache ingestion by upload bytes + filename to avoid rerun work."""
    return process_methylation_upload(
        uploaded_file=BytesIO(raw_bytes),
        source_name=filename,
        duplicate_policy=duplicate_policy,
    )


def _dataframe_signature(df: pd.DataFrame) -> str:
    """Create a stable lightweight signature for cached dataframe-level QC."""
    row_count = len(df)
    if row_count == 0:
        return "rows:0|checksum:0"

    cols = [col for col in ("cpg_id", "beta") if col in df.columns]
    hashed = pd.util.hash_pandas_object(df[cols], index=False)
    checksum = int(hashed.sum())
    return f"rows:{row_count}|checksum:{checksum}"


def analyze_methylation_cached(_normalized_df: pd.DataFrame, signature: str) -> dict[str, float]:
    """Cache QC summary by lightweight dataframe signature."""
    _ = signature
    return analyze_methylation(_normalized_df)


def _streamlit_cached_functions():
    """Bind Streamlit cache decorators only while the app is running."""
    return (
        st.cache_data(show_spinner=False)(process_methylation_upload_cached),
        st.cache_data(show_spinner=False)(analyze_methylation_cached),
    )


def _beta_histogram(beta_series: pd.Series, bins: int = 50) -> pd.DataFrame:
    """Return histogram data as a compact dataframe for charting."""
    beta_clean = beta_series.dropna()
    if beta_clean.empty:
        return pd.DataFrame({"count": []})

    bucketed = pd.cut(beta_clean, bins=bins, include_lowest=True)
    counts = bucketed.value_counts(sort=False)
    labels = [f"{interval.left:.2f}–{interval.right:.2f}" for interval in counts.index]

    return pd.DataFrame({"beta_bin": labels, "count": counts.values}).set_index("beta_bin")


def _drop_reason_table(report: ProcessedUpload) -> pd.DataFrame:
    """Return a compact dropped-row summary table for the UI."""
    drop_reason_df = pd.DataFrame(
        [
            {"reason": reason, "count": count}
            for reason, count in report.report.dropped_rows_by_reason.items()
            if count > 0
        ]
    )
    if drop_reason_df.empty:
        return pd.DataFrame({"reason": ["none"], "count": [0]})
    return drop_reason_df


def _normalized_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize normalized dataframe for download."""
    return df.to_csv(index=False).encode("utf-8")


def _processing_report_json(report: ProcessingReport) -> str:
    """Serialize processing report as formatted JSON."""
    return json.dumps(report.to_dict(), indent=2)


def _processing_report_csv_bytes(report: ProcessingReport) -> bytes:
    """Serialize processing report as a single-row CSV artifact."""
    return pd.DataFrame([report.to_flat_dict()]).to_csv(index=False).encode("utf-8")


def _structured_interpretation_json_bytes(interpretation: dict[str, object]) -> bytes:
    """Serialize structured interpretation output as formatted JSON."""
    return json.dumps(interpretation, indent=2).encode("utf-8")


def _duplicate_review_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize duplicate-row review details for download."""
    return df.to_csv(index=False).encode("utf-8")


def _aggregation_audit_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize aggregation-audit details for download."""
    return df.to_csv(index=False).encode("utf-8")


def _duplicate_policy_label(policy: DuplicatePolicy) -> str:
    """Return the human-readable label for a duplicate policy value."""
    for label, value in _DUPLICATE_POLICY_LABELS.items():
        if value == policy:
            return label
    return policy


def _artifact_basename(source_file: str) -> str:
    """Return a safe artifact basename derived from the upload filename."""
    return source_file.rsplit(".", 1)[0]


def _parse_warning_messages(report: ProcessingReport) -> list[str]:
    """Return UI-facing parse warning text for the processing report."""
    warning_messages = {
        "removed_utf8_bom": "A UTF-8 BOM was removed before parsing.",
        "mixed_delimiters_detected": "The upload appears to contain mixed delimiters; inspect dropped rows carefully.",
        "sniffed_delimiter_for_unknown_extension": "Delimiter was inferred from file content because the extension was not specific.",
        "recovered_from_mislabeled_extension": "The file extension did not match the detected delimiter; parsing recovered from content.",
    }
    return [warning_messages.get(warning, warning) for warning in report.parse_warnings]


def _interpretation_marker_ids(interpretation: dict[str, object]) -> list[str]:
    """Return observed marker IDs from the structured interpretation object."""
    interpretation_block = interpretation.get("interpretation", {})
    if not isinstance(interpretation_block, dict):
        return []

    marker_rows = interpretation_block.get("marker_interpretations", [])
    if not isinstance(marker_rows, list):
        return []

    marker_ids: list[str] = []
    for marker_row in marker_rows:
        if isinstance(marker_row, dict):
            cpg_id = str(marker_row.get("cpg_id", "")).strip()
            if cpg_id:
                marker_ids.append(cpg_id)
    return marker_ids


def _context_evidence_table(context_package: ContextPackage) -> pd.DataFrame:
    """Return retrieved local evidence chunks as a citation-friendly table."""
    rows = [
        {
            "chunk_id": chunk.id,
            "source": chunk.source,
            "section": chunk.section or "",
            "relevance_score": chunk.score,
            "evidence_text": chunk.text,
        }
        for chunk in context_package.retrieved_chunks
    ]
    return pd.DataFrame(rows)


def _build_context_package(
    interpretation: dict[str, object],
    qc_metrics: dict[str, float],
) -> ContextPackage | None:
    """Build local cited context without blocking the primary app workflow."""
    observed_data = interpretation.get("observed_data", {})
    coverage_status = "unknown"
    if isinstance(observed_data, dict):
        coverage_status = str(observed_data.get("coverage_status", "unknown"))

    try:
        return build_default_workflow_context(
            markers=_interpretation_marker_ids(interpretation),
            qc_metrics=qc_metrics,
            coverage_status=coverage_status,
            evidence_index_path=_WORKFLOW_EVIDENCE_PATH,
        )
    except (EvidenceContractError, FileNotFoundError, json.JSONDecodeError) as error:
        _LOGGER.warning("workflow_step=local_context status=error detail=%s", str(error))
        return None


def main() -> None:
    """Render the Streamlit app."""
    cached_process_methylation_upload, cached_analyze_methylation = _streamlit_cached_functions()

    st.set_page_config(page_title=PAGE_TITLE, layout=APP_LAYOUT)
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
    st.markdown(APP_DESCRIPTION)

    selected_duplicate_label = st.selectbox(
        "Duplicate CpG handling",
        options=list(_DUPLICATE_POLICY_LABELS.keys()),
        index=list(_DUPLICATE_POLICY_LABELS.values()).index(DEFAULT_DUPLICATE_POLICY),
        help="Choose whether duplicated cpg_id values should be preserved for QC or rejected.",
    )
    duplicate_policy = _DUPLICATE_POLICY_LABELS[selected_duplicate_label]
    st.caption(_DUPLICATE_POLICY_HELP[duplicate_policy])
    st.caption(
        f"Upload limit: {DEFAULT_MAX_UPLOAD_BYTES // (1024 * 1024)} MB. "
        "Uploads and generated artifacts are session-scoped; no durable storage is configured."
    )

    uploaded_file = st.file_uploader(
        "Upload methylation results file",
        type=["csv", "tsv", "txt"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        try:
            raw_bytes = uploaded_file.getvalue()
            processed_upload = cached_process_methylation_upload(
                raw_bytes=raw_bytes,
                filename=uploaded_file.name,
                duplicate_policy=duplicate_policy,
            )
            st.session_state["processed_upload"] = processed_upload
            _LOGGER.info("workflow_step=ingest_parse_normalize status=success source_file=%s", uploaded_file.name)
            st.success("Upload parsed and normalized successfully.")
        except IngestError as error:
            st.session_state.pop("processed_upload", None)
            _LOGGER.warning("workflow_step=ingest_parse_normalize status=error detail=%s", str(error))
            st.error(str(error))

    processed_upload = st.session_state.get("processed_upload")
    if processed_upload is None:
        st.info("Upload a CSV/TSV file to view normalized data, processing report, QC summary, and structured interpretation.")
        return

    normalized_df = processed_upload.normalized_df
    report = processed_upload.report
    summary = cached_analyze_methylation(normalized_df, signature=_dataframe_signature(normalized_df))
    panel_df = load_panel(_WORKFLOW_PANEL_PATH)
    interpretation = structured_interpretation(normalized_df=normalized_df, panel_df=panel_df)
    observed_data = interpretation["observed_data"]
    context_package = _build_context_package(interpretation=interpretation, qc_metrics=summary)

    st.subheader("Processing Report")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Input rows", f"{report.input_row_count:,}")
    col2.metric("Retained rows", f"{report.retained_row_count:,}")
    col3.metric("Dropped rows", f"{report.dropped_row_count:,}")
    col4.metric("Extra duplicate rows", f"{report.duplicate_cpg_id_extra_rows:,}")

    st.caption(
        f"Source file: {report.source_file} | Uploaded at (UTC): {report.uploaded_at} | "
        f"Parse strategy: {report.parse_strategy} | Duplicate policy: {_duplicate_policy_label(report.duplicate_policy)} | "
        f"Run ID: {report.run_id} | Report version: {report.report_version} | "
        f"Input checksum: {report.input_sha256[:12]}..."
    )
    st.dataframe(_drop_reason_table(processed_upload), width="stretch", hide_index=True)

    for warning_message in _parse_warning_messages(report):
        st.info(warning_message)

    if report.duplicate_policy == "preserve_rows_and_warn" and report.duplicate_cpg_id_groups > 0:
        st.warning(
            f"Found {report.duplicate_cpg_id_groups} duplicated cpg_id value(s). "
            "Rows were preserved to avoid silent aggregation."
        )
    if report.duplicate_policy == "aggregate_mean_when_metadata_match":
        if report.aggregation_applied:
            st.info(
                f"Aggregated {report.aggregated_duplicate_cpg_id_groups} duplicated cpg_id group(s) from "
                f"{report.aggregated_duplicate_input_rows} retained row(s)."
            )
        else:
            st.info("Aggregation mode was selected, but no duplicate cpg_id groups required aggregation.")
    if report.duplicate_metadata_conflict_groups > 0 and not report.aggregation_applied:
        st.warning(
            f"{report.duplicate_metadata_conflict_groups} duplicate cpg_id group(s) contain conflicting metadata. "
            "Aggregation remains unsafe without a defined scientific rule."
        )

    aggregation_audit_df = processed_upload.aggregation_audit_df
    if aggregation_audit_df is not None and not aggregation_audit_df.empty:
        st.subheader("Aggregation Audit")
        st.caption(
            "This audit artifact records the duplicate groups collapsed under the explicit aggregation policy."
        )
        st.download_button(
            "Download aggregation audit CSV",
            data=_aggregation_audit_csv_bytes(aggregation_audit_df),
            file_name=f"{_artifact_basename(report.source_file)}_aggregation_audit.csv",
            mime="text/csv",
        )
        st.dataframe(aggregation_audit_df.head(100), width="stretch")

    duplicate_review_df = duplicate_review_table(normalized_df)
    if not duplicate_review_df.empty:
        st.subheader("Duplicate Review")
        st.caption(
            "Inspect repeated retained rows here before any manual deduplication or future aggregation decision."
        )
        st.download_button(
            "Download duplicate review CSV",
            data=_duplicate_review_csv_bytes(duplicate_review_df),
            file_name=f"{_artifact_basename(report.source_file)}_duplicate_review.csv",
            mime="text/csv",
        )
        st.dataframe(duplicate_review_df.head(100), width="stretch")

    download_col1, download_col2, download_col3, download_col4 = st.columns(4)
    download_col1.download_button(
        "Download normalized CSV",
        data=_normalized_csv_bytes(normalized_df),
        file_name=(
            f"{_artifact_basename(report.source_file)}_aggregated_normalized.csv"
            if report.aggregation_applied
            else f"{_artifact_basename(report.source_file)}_normalized.csv"
        ),
        mime="text/csv",
    )
    download_col2.download_button(
        "Download report JSON",
        data=_processing_report_json(report),
        file_name=f"{_artifact_basename(report.source_file)}_processing_report.json",
        mime="application/json",
    )
    download_col3.download_button(
        "Download report CSV",
        data=_processing_report_csv_bytes(report),
        file_name=f"{_artifact_basename(report.source_file)}_processing_report.csv",
        mime="text/csv",
    )
    download_col4.download_button(
        "Download interpretation JSON",
        data=_structured_interpretation_json_bytes(interpretation),
        file_name=f"{_artifact_basename(report.source_file)}_structured_interpretation.json",
        mime="application/json",
    )

    st.subheader("Normalized Data (Canonical Schema)")
    st.dataframe(normalized_df.head(100), width="stretch")

    st.subheader("QC Summary (Retained Rows)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{int(summary['row_count']):,}")
    col2.metric("Unique CpGs", f"{int(summary['unique_cpg']):,}")
    col3.metric("Missing beta %", f"{summary['missing_beta_pct']:.2f}%")
    col4.metric("Out-of-range beta", f"{int(summary['out_of_range_beta_count'])}")

    st.markdown(
        f"**Beta stats:** min={summary['beta_min']:.3f}, "
        f"median={summary['beta_median']:.3f}, max={summary['beta_max']:.3f}"
    )

    st.caption("Showing beta distribution as a 50-bin histogram for large-file-safe visualization.")
    beta_hist_df = _beta_histogram(normalized_df["beta"], bins=50)
    st.bar_chart(beta_hist_df, x_label="Beta bin", y_label="Count")

    st.subheader("Structured Interpretation (Workflow 01)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Coverage", f"{observed_data['coverage_pct']:.2f}%")
    col2.metric("Markers found", f"{observed_data['markers_found']}")
    col3.metric("Markers missing", f"{observed_data['markers_missing']}")
    st.caption(f"Status: {interpretation['status']}")
    st.markdown(f"**Interpretation summary:** {interpretation['interpretation']['summary']}")
    marker_interpretation_df = pd.DataFrame(interpretation["interpretation"]["marker_interpretations"])
    if marker_interpretation_df.empty:
        st.info("No panel markers were observed in this upload. Interpretation is limited to coverage only.")
    else:
        st.dataframe(marker_interpretation_df, width="stretch", hide_index=True)
    st.markdown("**Limitations**")
    for limitation in interpretation["limitations"]:
        st.write(f"- {limitation}")
    st.markdown("**Recommended next analytical steps**")
    for next_step in interpretation["next_steps"]:
        st.write(f"- {next_step}")

    st.subheader("Cited Context")
    st.caption("Local workflow, schema, validation, and data-policy sources. Not clinical evidence.")
    if context_package is None:
        st.info("Local cited context is unavailable for this run.")
    else:
        evidence_table = _context_evidence_table(context_package)
        if evidence_table.empty:
            st.info("No local cited context matched this upload summary.")
        else:
            st.dataframe(evidence_table, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
