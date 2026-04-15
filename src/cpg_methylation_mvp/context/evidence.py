"""Local evidence contract helpers for deterministic context retrieval."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .builder import build_context
from .retriever import KeywordRetriever
from .types import Chunk, ContextPackage, DatasetSummary

DEFAULT_EVIDENCE_INDEX_PATH = Path("data/evidence/workflow_01_context_chunks.json")
DEFAULT_EXTERNAL_SOURCE_POLICY_PATH = Path("data/evidence/external_source_policy.json")
REQUIRED_METADATA_FIELDS = ("evidence_type", "claim_scope", "allowed_use")
REQUIRED_EXTERNAL_POLICY_FIELDS = (
    "policy_version",
    "status",
    "runtime_enabled",
    "allowed_source_types",
    "disallowed_source_types",
    "citation_requirements",
    "claim_boundaries",
    "review_gate",
)
REQUIRED_EXTERNAL_SOURCE_TYPE_FIELDS = (
    "id",
    "label",
    "allowed_uses",
    "required_metadata",
    "freshness",
)
REQUIRED_FRESHNESS_FIELDS = (
    "metadata_verified_within_days",
    "content_review_expires_after_days",
)


class EvidenceContractError(ValueError):
    """Raised when local evidence chunks do not satisfy the repo contract."""


def load_evidence_chunks(
    index_path: Path = DEFAULT_EVIDENCE_INDEX_PATH,
    repo_root: Path | None = None,
) -> list[Chunk]:
    """Load and validate local evidence chunks from a JSON index."""
    resolved_index_path = Path(index_path)
    root = repo_root or Path.cwd()
    raw_items = json.loads(resolved_index_path.read_text(encoding="utf-8"))
    if not isinstance(raw_items, list) or not raw_items:
        raise EvidenceContractError("Evidence index must contain at least one chunk.")

    chunks: list[Chunk] = []
    seen_ids: set[str] = set()
    for position, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise EvidenceContractError(f"Evidence chunk at position {position} must be an object.")
        chunk = _chunk_from_mapping(raw_item)
        _validate_chunk(chunk=chunk, seen_ids=seen_ids, repo_root=root)
        chunks.append(chunk)

    return chunks


def load_external_source_policy(
    policy_path: Path = DEFAULT_EXTERNAL_SOURCE_POLICY_PATH,
) -> dict[str, Any]:
    """Load and validate the external scientific source policy."""
    raw_policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    if not isinstance(raw_policy, dict):
        raise EvidenceContractError("External source policy must be a JSON object.")
    _validate_external_source_policy(raw_policy)
    return raw_policy


def build_default_workflow_context(
    markers: Sequence[str],
    qc_metrics: Mapping[str, float],
    coverage_status: str,
    evidence_index_path: Path = DEFAULT_EVIDENCE_INDEX_PATH,
    top_k: int = 4,
) -> ContextPackage:
    """Build deterministic cited context for Workflow 01 from local evidence only."""
    load_evidence_chunks(evidence_index_path)
    dataset_summary = dataset_summary_from_qc_metrics(
        qc_metrics=qc_metrics,
        notes=f"Workflow 01 panel coverage status: {coverage_status}",
    )
    return build_context(
        markers=list(markers),
        dataset_summary=dataset_summary,
        retriever=KeywordRetriever(chunk_index_path=evidence_index_path),
        top_k=top_k,
    )


def dataset_summary_from_qc_metrics(
    qc_metrics: Mapping[str, float],
    notes: str | None = None,
) -> DatasetSummary:
    """Convert aggregate QC metrics into a context-safe dataset summary."""
    row_count = int(qc_metrics.get("row_count", 0.0))
    missing_pct = float(qc_metrics.get("missing_beta_pct", 0.0))
    beta_min = _finite_metric(qc_metrics, "beta_min")
    beta_max = _finite_metric(qc_metrics, "beta_max")
    beta_range = (beta_min, beta_max) if beta_min is not None and beta_max is not None else None
    return DatasetSummary(
        row_count=row_count,
        missing_pct=missing_pct,
        platform="Workflow 01",
        beta_range=beta_range,
        notes=notes,
    )


def _chunk_from_mapping(raw_item: Mapping[str, Any]) -> Chunk:
    metadata = raw_item.get("metadata")
    return Chunk(
        id=str(raw_item.get("id", "")).strip(),
        text=str(raw_item.get("text", "")).strip(),
        source=str(raw_item.get("source", "")).strip(),
        section=str(raw_item.get("section", "")).strip() or None,
        metadata=metadata if isinstance(metadata, dict) else None,
    )


def _validate_chunk(chunk: Chunk, seen_ids: set[str], repo_root: Path) -> None:
    if not chunk.id:
        raise EvidenceContractError("Evidence chunk id is required.")
    if chunk.id in seen_ids:
        raise EvidenceContractError(f"Duplicate evidence chunk id: {chunk.id}")
    seen_ids.add(chunk.id)

    if not chunk.text:
        raise EvidenceContractError(f"Evidence chunk {chunk.id} text is required.")
    if not chunk.source:
        raise EvidenceContractError(f"Evidence chunk {chunk.id} source is required.")
    if chunk.section is None:
        raise EvidenceContractError(f"Evidence chunk {chunk.id} section is required.")
    if not _source_exists(source=chunk.source, repo_root=repo_root):
        raise EvidenceContractError(f"Evidence chunk {chunk.id} source does not exist: {chunk.source}")

    metadata = chunk.metadata or {}
    missing_metadata = [field for field in REQUIRED_METADATA_FIELDS if not str(metadata.get(field, "")).strip()]
    if missing_metadata:
        missing_text = ", ".join(missing_metadata)
        raise EvidenceContractError(f"Evidence chunk {chunk.id} missing metadata field(s): {missing_text}")


def _validate_external_source_policy(policy: Mapping[str, Any]) -> None:
    missing_fields = [field for field in REQUIRED_EXTERNAL_POLICY_FIELDS if field not in policy]
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        raise EvidenceContractError(f"External source policy missing field(s): {missing_text}")

    if policy["runtime_enabled"] is not False:
        raise EvidenceContractError("External scientific RAG policy must keep runtime_enabled false until approved.")

    allowed_source_types = policy["allowed_source_types"]
    if not isinstance(allowed_source_types, list) or not allowed_source_types:
        raise EvidenceContractError("External source policy must define at least one allowed source type.")

    seen_source_type_ids: set[str] = set()
    for source_type in allowed_source_types:
        if not isinstance(source_type, dict):
            raise EvidenceContractError("Each allowed source type must be an object.")
        _validate_external_source_type(source_type=source_type, seen_source_type_ids=seen_source_type_ids)

    for list_field in ("disallowed_source_types", "citation_requirements", "claim_boundaries"):
        values = policy[list_field]
        if not isinstance(values, list) or not values:
            raise EvidenceContractError(f"External source policy field {list_field} must be a non-empty list.")

    review_gate = policy["review_gate"]
    if not isinstance(review_gate, dict):
        raise EvidenceContractError("External source policy review_gate must be an object.")
    if review_gate.get("review_required_before_runtime_use") is not True:
        raise EvidenceContractError("External source policy must require review before runtime use.")
    if review_gate.get("source_registry_required") is not True:
        raise EvidenceContractError("External source policy must require a source registry before runtime use.")


def _validate_external_source_type(
    source_type: Mapping[str, Any],
    seen_source_type_ids: set[str],
) -> None:
    missing_fields = [field for field in REQUIRED_EXTERNAL_SOURCE_TYPE_FIELDS if field not in source_type]
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        raise EvidenceContractError(f"Allowed source type missing field(s): {missing_text}")

    source_type_id = str(source_type["id"]).strip()
    if not source_type_id:
        raise EvidenceContractError("Allowed source type id is required.")
    if source_type_id in seen_source_type_ids:
        raise EvidenceContractError(f"Duplicate allowed source type id: {source_type_id}")
    seen_source_type_ids.add(source_type_id)

    for list_field in ("allowed_uses", "required_metadata"):
        values = source_type[list_field]
        if not isinstance(values, list) or not values:
            raise EvidenceContractError(f"Allowed source type {source_type_id} field {list_field} must be non-empty.")

    freshness = source_type["freshness"]
    if not isinstance(freshness, dict):
        raise EvidenceContractError(f"Allowed source type {source_type_id} freshness must be an object.")
    for field in REQUIRED_FRESHNESS_FIELDS:
        value = freshness.get(field)
        if not isinstance(value, int) or value <= 0:
            raise EvidenceContractError(
                f"Allowed source type {source_type_id} freshness field {field} must be a positive integer."
            )


def _source_exists(source: str, repo_root: Path) -> bool:
    if "://" in source:
        return True
    return (repo_root / source).exists()


def _finite_metric(metrics: Mapping[str, float], key: str) -> float | None:
    value = metrics.get(key)
    if value is None:
        return None
    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        return None
    return numeric_value
