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


def _normalized_column_key(column: object) -> str:
    """Normalize header text for resilient alias matching."""
    return str(column).lstrip("\ufeff").strip().lower()


def _alias_match_priority(column: object, canonical: str) -> tuple[int, str]:
    """Rank matching columns so canonical headers win over BOM-prefixed variants."""
    as_text = str(column)
    stripped = as_text.strip()
    normalized = _normalized_column_key(column)

    if stripped == canonical:
        return (0, normalized)
    if normalized == canonical and not as_text.startswith("\ufeff"):
        return (1, normalized)
    if normalized == canonical:
        return (2, normalized)
    return (3, normalized)


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map known aliases to canonical schema columns."""
    rename_map: dict[str, str] = {}

    for canonical, aliases in ALIASES.items():
        candidates: list[object] = []
        alias_keys = {_normalized_column_key(alias) for alias in aliases}

        for column in df.columns:
            if _normalized_column_key(column) in alias_keys:
                candidates.append(column)

        if not candidates:
            continue

        chosen = min(candidates, key=lambda column: _alias_match_priority(column, canonical))
        rename_map[chosen] = canonical

    return df.rename(columns=rename_map)


def select_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep canonical columns that are present, in canonical order."""
    keep_columns = [column for column in CANONICAL_COLUMNS if column in df.columns]
    return df[keep_columns].copy()



def normalize_upload(df: pd.DataFrame) -> pd.DataFrame:
    """Canonicalize columns and keep canonical subset."""
    normalized = canonicalize_columns(df)
    return select_canonical_columns(normalized)
