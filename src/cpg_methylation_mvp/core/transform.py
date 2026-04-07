"""Transformation helpers for canonical methylation schema."""

from __future__ import annotations

import pandas as pd

CANONICAL_COLUMNS: tuple[str, ...] = (
    "cpg_id",
    "beta",
    "chrom",
    "pos",
    "gene",
    "pval",
)

ALIASES: dict[str, tuple[str, ...]] = {
    "cpg_id": ("cpg_id", "cpg", "probe", "probe_id", "CpG", "cgid"),
    "beta": ("beta", "beta_value", "methylation_level", "methylation", "Beta"),
    "chrom": ("chrom", "chr", "chromosome"),
    "pos": ("pos", "position", "bp", "start"),
    "gene": ("gene", "symbol", "gene_symbol"),
    "pval": ("pval", "p_value", "p.value"),
}


def _find_preferred_source_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    """Return the preferred input column for an alias group.

    Preference order:
    1) First exact alias match in declared alias order.
    2) First case-insensitive alias match in declared alias order.
    """
    columns = list(df.columns)

    for alias in aliases:
        if alias in columns:
            return alias

    lowered_to_columns: dict[str, list[str]] = {}
    for column in columns:
        lowered_to_columns.setdefault(column.lower().strip(), []).append(column)

    for alias in aliases:
        matches = lowered_to_columns.get(alias.lower().strip(), [])
        if matches:
            return matches[0]

    return None


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map known aliases to canonical schema columns."""
    rename_map: dict[str, str] = {}

    for canonical, aliases in ALIASES.items():
        source_column = _find_preferred_source_column(df, aliases)
        if source_column is not None:
            rename_map[source_column] = canonical

    return df.rename(columns=rename_map)


def select_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep canonical columns that are present, in canonical order."""
    keep_columns = [column for column in CANONICAL_COLUMNS if column in df.columns]
    return df[keep_columns].copy()



def normalize_upload(df: pd.DataFrame) -> pd.DataFrame:
    """Canonicalize columns and keep canonical subset."""
    normalized = canonicalize_columns(df)
    return select_canonical_columns(normalized)
