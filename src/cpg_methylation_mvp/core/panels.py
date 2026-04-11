"""Panel loading and evaluation helpers for curated CpG marker sets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PANEL_REQUIRED_COLUMNS: tuple[str, ...] = (
    "panel_id",
    "cpg_id",
    "marker_label",
    "expected_direction",
    "notes",
)

PANEL_LIMITATIONS: tuple[str, ...] = (
    "This report is based only on panel coverage and observed beta values.",
    "No clinical interpretation is made.",
    "Missing CpGs reduce interpretability.",
)


def _validate_columns(df: pd.DataFrame, required: tuple[str, ...], *, dataset_name: str) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        missing_columns = ", ".join(missing)
        raise ValueError(f"{dataset_name} missing required columns: {missing_columns}")


def load_panel(panel_path: str | Path) -> pd.DataFrame:
    """Load a curated panel CSV and enforce expected panel columns."""
    path = Path(panel_path)
    panel_df = pd.read_csv(path)
    _validate_columns(panel_df, PANEL_REQUIRED_COLUMNS, dataset_name="panel file")

    for column in PANEL_REQUIRED_COLUMNS:
        panel_df[column] = panel_df[column].astype(str).str.strip()

    return panel_df


def evaluate_panel(normalized_df: pd.DataFrame, panel_df: pd.DataFrame) -> dict:
    """Evaluate normalized methylation data against a curated marker panel."""
    _validate_columns(normalized_df, ("cpg_id", "beta"), dataset_name="normalized dataframe")
    _validate_columns(panel_df, PANEL_REQUIRED_COLUMNS, dataset_name="panel dataframe")

    panel_core = (
        panel_df.loc[:, ["panel_id", "cpg_id", "marker_label"]]
        .drop_duplicates(subset=["cpg_id"], keep="first")
        .reset_index(drop=True)
    )

    observed = panel_core.merge(
        normalized_df.loc[:, ["cpg_id", "beta"]],
        on="cpg_id",
        how="inner",
    )

    missing = panel_core[~panel_core["cpg_id"].isin(observed["cpg_id"])].copy()

    marker_count = int(len(panel_core))
    markers_found = int(len(observed))
    markers_missing = int(len(missing))
    coverage_pct = 0.0 if marker_count == 0 else round((markers_found / marker_count) * 100, 2)

    if coverage_pct == 100.0:
        coverage_status = "complete"
    elif coverage_pct > 0.0:
        coverage_status = "partial"
    else:
        coverage_status = "none"

    panel_id = panel_core["panel_id"].iloc[0] if marker_count else "unknown_panel"

    return {
        "panel_id": panel_id,
        "panel_marker_count": marker_count,
        "markers_found": markers_found,
        "markers_missing": markers_missing,
        "coverage_pct": coverage_pct,
        "coverage_status": coverage_status,
        "observed_markers": observed.loc[:, ["cpg_id", "marker_label", "beta"]].to_dict(orient="records"),
        "missing_markers": missing.loc[:, ["cpg_id", "marker_label"]].to_dict(orient="records"),
        "limitations": list(PANEL_LIMITATIONS),
    }


def panel_report_table(result: dict) -> pd.DataFrame:
    """Flatten an evaluation result into a tabular marker-level report."""
    observed_rows = [
        {
            "panel_id": result["panel_id"],
            "cpg_id": marker["cpg_id"],
            "marker_label": marker["marker_label"],
            "beta": marker["beta"],
            "is_observed": True,
        }
        for marker in result["observed_markers"]
    ]

    missing_rows = [
        {
            "panel_id": result["panel_id"],
            "cpg_id": marker["cpg_id"],
            "marker_label": marker["marker_label"],
            "beta": pd.NA,
            "is_observed": False,
        }
        for marker in result["missing_markers"]
    ]

    return pd.DataFrame(observed_rows + missing_rows)
