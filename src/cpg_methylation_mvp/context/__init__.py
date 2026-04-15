"""Experimental context-pack helpers for future evidence-grounded workflows.

This module is intentionally outside ``cpg_methylation_mvp.core`` so Streamlit
and current analytical behavior remain unchanged.
"""

from .builder import build_context
from .citations import format_citations
from .retriever import KeywordRetriever, MockRetriever, Retriever
from .types import Chunk, Citation, ContextPackage, DatasetSummary

__all__ = [
    "Chunk",
    "Citation",
    "ContextPackage",
    "DatasetSummary",
    "KeywordRetriever",
    "MockRetriever",
    "Retriever",
    "build_context",
    "format_citations",
]
