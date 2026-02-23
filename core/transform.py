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


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map known aliases to canonical schema columns."""
    lowered = {column.lower().strip(): column for column in df.columns}
    rename_map: dict[str, str] = {}

    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in lowered:
                rename_map[lowered[alias_lower]] = canonical
                break

    return df.rename(columns=rename_map)


def select_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep canonical columns that are present, in canonical order."""
    keep_columns = [column for column in CANONICAL_COLUMNS if column in df.columns]
    return df[keep_columns].copy()
