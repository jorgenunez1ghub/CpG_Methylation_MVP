"""Streamlit app entrypoint for CpG methylation ingestion MVP."""

from __future__ import annotations

from io import BytesIO

import streamlit as st

from core.ingest import IngestError, load_methylation_file, qc_summary

st.set_page_config(page_title="CpG Methylation MVP", layout="wide")
st.title("CpG Upload → Parse → Normalize")

st.caption(
    "Educational demo only. Not medical advice. "
    "No raw upload data is logged or displayed outside your session."
)

st.markdown(
    "Upload a **CSV or TSV** containing CpG methylation values. "
    "The app validates and normalizes your data into a canonical schema for downstream analysis."
)

uploaded_file = st.file_uploader(
    "Upload methylation results file",
    type=["csv", "tsv", "txt"],
    accept_multiple_files=False,
)

if uploaded_file is not None:
    try:
        normalized_df = load_methylation_file(
            uploaded_file=BytesIO(uploaded_file.getvalue()),
            source_name=uploaded_file.name,
        )
        st.session_state["normalized_df"] = normalized_df
        st.success("Upload parsed and normalized successfully.")
    except IngestError as error:
        st.session_state.pop("normalized_df", None)
        st.error(str(error))

if "normalized_df" not in st.session_state:
    st.info("Upload a CSV/TSV file to view normalized data and QC summary.")
    st.stop()

normalized_df = st.session_state["normalized_df"]
summary = qc_summary(normalized_df)

st.subheader("Normalized Data (Canonical Schema)")
st.dataframe(normalized_df.head(100), width="stretch")

st.subheader("QC Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{int(summary['row_count']):,}")
col2.metric("Unique CpGs", f"{int(summary['unique_cpg']):,}")
col3.metric("Missing beta %", f"{summary['missing_beta_pct']:.2f}%")
col4.metric("Out-of-range beta", f"{int(summary['out_of_range_beta_count'])}")

st.markdown(
    f"**Beta stats:** min={summary['beta_min']:.3f}, "
    f"median={summary['beta_median']:.3f}, max={summary['beta_max']:.3f}"
)

st.bar_chart(normalized_df["beta"], x_label="Row Index", y_label="Beta")
