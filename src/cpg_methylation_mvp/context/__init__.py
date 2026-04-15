"""Experimental context-pack helpers for future evidence-grounded workflows.

This module is intentionally outside ``cpg_methylation_mvp.core`` so Streamlit
and current analytical behavior remain unchanged.
"""

from .builder import build_context
from .citations import format_citations
from .evidence import (
    DEFAULT_EVIDENCE_INDEX_PATH,
    DEFAULT_EXTERNAL_SOURCE_POLICY_PATH,
    EvidenceContractError,
    build_default_workflow_context,
    dataset_summary_from_qc_metrics,
    load_evidence_chunks,
    load_external_source_policy,
)
from .retriever import KeywordRetriever, MockRetriever, Retriever
from .types import Chunk, Citation, ContextPackage, DatasetSummary

__all__ = [
    "Chunk",
    "Citation",
    "ContextPackage",
    "DEFAULT_EVIDENCE_INDEX_PATH",
    "DEFAULT_EXTERNAL_SOURCE_POLICY_PATH",
    "DatasetSummary",
    "EvidenceContractError",
    "KeywordRetriever",
    "MockRetriever",
    "Retriever",
    "build_context",
    "build_default_workflow_context",
    "dataset_summary_from_qc_metrics",
    "format_citations",
    "load_evidence_chunks",
    "load_external_source_policy",
]
