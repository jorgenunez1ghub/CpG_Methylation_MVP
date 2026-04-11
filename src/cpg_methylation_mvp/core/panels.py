"""Panel loading, evaluation, and structured interpretation helpers."""

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
WORKFLOW_ID = "mvp_workflow_01"
_LOW_BETA_THRESHOLD = 0.30
_HIGH_BETA_THRESHOLD = 0.70


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


def _beta_state(beta_value: float) -> str:
    """Return a bounded state label for observed beta values."""
    if beta_value >= _HIGH_BETA_THRESHOLD:
        return "higher"
    if beta_value <= _LOW_BETA_THRESHOLD:
        return "lower"
    return "intermediate"


def _agreement_label(observed_state: str, expected_direction: str) -> str:
    """Return agreement status between observed and expected signal direction."""
    if observed_state == "intermediate":
        return "uncertain"
    if observed_state == expected_direction:
        return "aligned"
    return "not_aligned"


def structured_interpretation(normalized_df: pd.DataFrame, panel_df: pd.DataFrame) -> dict[str, object]:
    """Build a cautious, structured interpretation for one bounded workflow."""
    _validate_columns(normalized_df, ("cpg_id", "beta"), dataset_name="normalized dataframe")
    _validate_columns(panel_df, PANEL_REQUIRED_COLUMNS, dataset_name="panel dataframe")

    panel_result = evaluate_panel(normalized_df=normalized_df, panel_df=panel_df)

    panel_with_expected = panel_df.loc[:, ["cpg_id", "expected_direction"]].drop_duplicates("cpg_id")
    observed_markers_df = pd.DataFrame(panel_result["observed_markers"])
    if observed_markers_df.empty:
        observed_markers_df = pd.DataFrame(columns=["cpg_id", "marker_label", "beta", "expected_direction"])
    else:
        observed_markers_df = observed_markers_df.merge(
            panel_with_expected,
            on="cpg_id",
            how="left",
        )

    marker_interpretations: list[dict[str, object]] = []
    for _, row in observed_markers_df.iterrows():
        observed_beta = float(row["beta"])
        observed_state = _beta_state(observed_beta)
        expected_direction = str(row["expected_direction"]).strip()
        marker_interpretations.append(
            {
                "cpg_id": row["cpg_id"],
                "marker_label": row["marker_label"],
                "observed_beta": observed_beta,
                "observed_state": observed_state,
                "expected_direction": expected_direction,
                "agreement": _agreement_label(observed_state, expected_direction),
            }
        )

    aligned_count = sum(item["agreement"] == "aligned" for item in marker_interpretations)
    uncertain_count = sum(item["agreement"] == "uncertain" for item in marker_interpretations)

    interpretation_summary = (
        "Coverage too low for directional interpretation."
        if panel_result["coverage_status"] == "none"
        else "Directional signal is preliminary and should be treated as exploratory."
    )

    return {
        "workflow_id": WORKFLOW_ID,
        "panel_id": panel_result["panel_id"],
        "status": "complete" if panel_result["coverage_status"] != "none" else "insufficient_coverage",
        "observed_data": {
            "panel_marker_count": panel_result["panel_marker_count"],
            "markers_found": panel_result["markers_found"],
            "markers_missing": panel_result["markers_missing"],
            "coverage_pct": panel_result["coverage_pct"],
            "coverage_status": panel_result["coverage_status"],
        },
        "interpretation": {
            "summary": interpretation_summary,
            "markers_aligned": aligned_count,
            "markers_uncertain": uncertain_count,
            "marker_interpretations": marker_interpretations,
        },
        "limitations": [
            *panel_result["limitations"],
            "Beta state thresholds are fixed at <=0.30 (lower), >=0.70 (higher), otherwise intermediate.",
            "Marker direction agreement is heuristic and intended for workflow demonstration only.",
        ],
        "next_steps": [
            "Inspect missing panel markers before drawing directional conclusions.",
            "Review marker-level agreement alongside source metadata and duplicate handling choices.",
            "Use independent datasets before expanding beyond this bounded panel workflow.",
        ],
    }
