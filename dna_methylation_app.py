import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="DNA Methylation Interpreter (MVP)", layout="wide")
st.title("DNA Methylation Interpreter (MVP)")

st.caption(
    "Educational demo only. Not medical advice. "
    "Do not use this tool to diagnose or treat conditions. "
    "Consult a qualified clinician for interpretation."
)

# --- Sidebar: instructions & controls ---
st.sidebar.header("How to use")
st.sidebar.write(
    "1) Upload a CSV\n"
    "2) Map your columns (if needed)\n"
    "3) Adjust threshold\n"
    "4) Review flagged sites + summary\n"
    "5) Download outputs"
)

threshold = st.sidebar.slider(
    "High methylation threshold",
    min_value=0.0, max_value=1.0, value=0.70, step=0.01
)

st.sidebar.subheader("Expected columns")
st.sidebar.code("Gene, Methylation_Level", language="text")

# --- Optional: sample file (nice for demos) ---
sample_csv = """Gene,Methylation_Level
ABC1,0.12
ABC1,0.42
MTHFR,0.88
COMT,0.73
BRCA1,0.91
TP53,0.15
"""
st.sidebar.download_button(
    label="Download sample CSV",
    data=sample_csv,
    file_name="sample_methylation.csv",
    mime="text/csv"
)

# --- Upload ---
uploaded_file = st.file_uploader("Upload your DNA methylation file (CSV)", type=["csv"])

if not uploaded_file:
    st.info("Upload a CSV to begin, or download the sample CSV from the sidebar.")
    st.stop()

# --- Read CSV safely ---
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

if df.empty:
    st.warning("Your CSV loaded, but it appears to be empty.")
    st.stop()

st.subheader("1) Preview")
st.dataframe(df.head(20), use_container_width=True)

# --- Column mapping for real-world files ---
st.subheader("2) Column mapping")
cols = list(df.columns)

col1, col2 = st.columns(2)
with col1:
    gene_col = st.selectbox(
        "Select the Gene column",
        options=cols,
        index=cols.index("Gene") if "Gene" in cols else 0
    )
with col2:
    meth_col = st.selectbox(
        "Select the Methylation Level column",
        options=cols,
        index=cols.index("Methylation_Level") if "Methylation_Level" in cols else 0
    )

# --- Validate selected columns ---
df_work = df[[gene_col, meth_col]].copy()
df_work.columns = ["Gene", "Methylation_Level"]

# Force numeric methylation values (coerce errors)
df_work["Methylation_Level"] = pd.to_numeric(df_work["Methylation_Level"], errors="coerce")

invalid_count = df_work["Methylation_Level"].isna().sum()
if invalid_count > 0:
    st.warning(f"{invalid_count} rows have non-numeric methylation values and will be ignored.")

df_work = df_work.dropna(subset=["Methylation_Level"])

if df_work.empty:
    st.error("After cleaning non-numeric values, no rows remain. Check your data format.")
    st.stop()

# --- Main analysis ---
st.subheader("3) Results")

left, right = st.columns([1, 1])

with left:
    st.markdown("**Overall summary**")
    st.write(f"Rows analyzed: **{len(df_work):,}**")
    st.write(f"Unique genes: **{df_work['Gene'].nunique():,}**")
    st.write(f"Mean methylation: **{df_work['Methylation_Level'].mean():.3f}**")
    st.write(f"Median methylation: **{df_work['Methylation_Level'].median():.3f}**")

with right:
    st.markdown("**Distribution (quick view)**")
    # Streamlit built-in charting (keeps it simple)
    st.bar_chart(df_work["Methylation_Level"].value_counts(bins=20).sort_index())

# Flag high methylation
high_meth = df_work[df_work["Methylation_Level"] > threshold].sort_values("Methylation_Level", ascending=False)

st.markdown(f"### High methylation sites (> {threshold:.2f})")
st.write(f"Found **{len(high_meth):,}** rows above threshold.")
st.dataframe(high_meth.head(200), use_container_width=True)

# Gene-level rollup
rollup = (
    df_work.groupby("Gene", as_index=False)["Methylation_Level"]
    .agg(["count", "mean", "max"])
    .reset_index()
    .sort_values("mean", ascending=False)
)
rollup.columns = ["Gene", "Count", "Mean_Methylation", "Max_Methylation"]

st.markdown("### Top genes by mean methylation")
st.dataframe(rollup.head(50), use_container_width=True)

# --- Download outputs ---
st.subheader("4) Export")

# High methylation CSV
high_csv = high_meth.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download high-methylation rows (CSV)",
    data=high_csv,
    file_name="high_methylation_rows.csv",
    mime="text/csv"
)

# Simple report (Markdown)
report_md = f"""# DNA Methylation Interpreter (MVP) — Report

**Disclaimer:** Educational demo only. Not medical advice.

## Summary
- Rows analyzed: {len(df_work):,}
- Unique genes: {df_work['Gene'].nunique():,}
- Threshold: {threshold:.2f}
- Rows above threshold: {len(high_meth):,}
- Mean methylation: {df_work['Methylation_Level'].mean():.3f}
- Median methylation: {df_work['Methylation_Level'].median():.3f}

## Top genes by mean methylation (top 10)
{rollup.head(10).to_markdown(index=False)}

## Notes / Next steps (educational)
- Validate input file schema and units.
- Treat this output as a screening view; confirm interpretation with a qualified professional.
- Re-run on future samples to track changes over time with consistent thresholds.
"""
st.download_button(
    "Download report (Markdown)",
    data=report_md.encode("utf-8"),
    file_name="methylation_report.md",
    mime="text/markdown"
)

st.info("Tip: For your FAC-P/PM demo, the downloads make this feel like a real deliverable.")