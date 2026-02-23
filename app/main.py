"""Streamlit entrypoint for CpG methylation MVP."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_config import APP_CAPTION, APP_DESCRIPTION, APP_LAYOUT, APP_TITLE, PAGE_TITLE
from core import IngestError, analyze_methylation, load_methylation_file


@st.cache_data(show_spinner=False)
def load_methylation_file_cached(raw_bytes: bytes, filename: str) -> pd.DataFrame:
    """Cache ingestion by upload bytes + filename to avoid rerun work."""
    return load_methylation_file(uploaded_file=BytesIO(raw_bytes), source_name=filename)


def _dataframe_signature(df: pd.DataFrame) -> str:
    """Create a stable lightweight signature for cached dataframe-level QC."""
    row_count = len(df)
    if row_count == 0:
        return "rows:0|checksum:0"

    cols = [col for col in ("cpg_id", "beta") if col in df.columns]
    hashed = pd.util.hash_pandas_object(df[cols], index=False)
    checksum = int(hashed.sum())
    return f"rows:{row_count}|checksum:{checksum}"


@st.cache_data(show_spinner=False)
def analyze_methylation_cached(_normalized_df: pd.DataFrame, signature: str) -> dict[str, float]:
    """Cache QC summary by lightweight dataframe signature."""
    _ = signature
    return analyze_methylation(_normalized_df)


def _beta_histogram(beta_series: pd.Series, bins: int = 50) -> pd.DataFrame:
    """Return histogram data as a compact dataframe for charting."""
    beta_clean = beta_series.dropna()
    if beta_clean.empty:
        return pd.DataFrame({"count": []})

    bucketed = pd.cut(beta_clean, bins=bins, include_lowest=True)
    counts = bucketed.value_counts(sort=False)
    labels = [f"{interval.left:.2f}–{interval.right:.2f}" for interval in counts.index]

    return pd.DataFrame({"beta_bin": labels, "count": counts.values}).set_index("beta_bin")


st.set_page_config(page_title=PAGE_TITLE, layout=APP_LAYOUT)
st.title(APP_TITLE)
st.caption(APP_CAPTION)
st.markdown(APP_DESCRIPTION)

uploaded_file = st.file_uploader(
    "Upload methylation results file",
    type=["csv", "tsv", "txt"],
    accept_multiple_files=False,
)

if uploaded_file is not None:
    try:
        raw_bytes = uploaded_file.getvalue()
        normalized_df = load_methylation_file_cached(raw_bytes=raw_bytes, filename=uploaded_file.name)
        st.session_state["normalized_df"] = normalized_df
        st.success("Upload parsed and normalized successfully.")
    except IngestError as error:
        st.session_state.pop("normalized_df", None)
        st.error(str(error))

if "normalized_df" not in st.session_state:
    st.info("Upload a CSV/TSV file to view normalized data and QC summary.")
    st.stop()

normalized_df = st.session_state["normalized_df"]
summary = analyze_methylation_cached(normalized_df, signature=_dataframe_signature(normalized_df))

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

st.caption("Showing beta distribution as a 50-bin histogram for large-file-safe visualization.")
beta_hist_df = _beta_histogram(normalized_df["beta"], bins=50)
st.bar_chart(beta_hist_df, x_label="Beta bin", y_label="Count")
