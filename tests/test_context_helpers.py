from __future__ import annotations

import json

from cpg_methylation_mvp.context import (
    Chunk,
    DatasetSummary,
    EvidenceContractError,
    KeywordRetriever,
    MockRetriever,
    build_context,
    build_default_workflow_context,
    load_evidence_chunks,
    load_external_source_policy,
)


def test_build_context_returns_cited_prompt_package() -> None:
    chunks = [
        Chunk(
            id="chunk-1",
            text="CpG methylation beta values are often summarized between 0 and 1.",
            source="methylation_basics.md",
            section="beta values",
            score=2.0,
        ),
        Chunk(
            id="chunk-1",
            text="Duplicate source chunk should be cited once.",
            source="methylation_basics.md",
            score=1.0,
        ),
    ]
    summary = DatasetSummary(row_count=10, missing_pct=0.0, platform="demo", beta_range=(0.1, 0.9))

    context_package = build_context(
        markers=["cg000001"],
        dataset_summary=summary,
        retriever=MockRetriever(canned=chunks),
        top_k=2,
    )

    assert "Do not make diagnostic" in context_package.system_prompt
    assert "Row count: 10" in context_package.user_message
    assert "cg000001" in context_package.user_message
    assert len(context_package.retrieved_chunks) == 2
    assert len(context_package.citations) == 1
    assert context_package.citations[0].chunk_id == "chunk-1"
    assert context_package.token_estimate > 0


def test_build_context_rejects_invalid_aggregate_summary() -> None:
    summary = DatasetSummary(row_count=-1, missing_pct=0.0)

    try:
        build_context(markers=[], dataset_summary=summary, retriever=MockRetriever(canned=[]))
    except ValueError as error:
        assert "row_count" in str(error)
    else:
        raise AssertionError("Expected invalid row_count to raise ValueError")


def test_keyword_retriever_ranks_matching_chunks(tmp_path) -> None:
    index_path = tmp_path / "chunks.json"
    index_path.write_text(
        json.dumps(
            [
                {
                    "id": "a",
                    "text": "methylation beta quality control",
                    "source": "a.md",
                },
                {
                    "id": "b",
                    "text": "unrelated topic",
                    "source": "b.md",
                },
            ]
        ),
        encoding="utf-8",
    )

    retriever = KeywordRetriever(chunk_index_path=index_path)
    chunks = retriever.retrieve("beta methylation", top_k=5)

    assert [chunk.id for chunk in chunks] == ["a"]
    assert chunks[0].score == 2.0


def test_default_evidence_index_satisfies_contract() -> None:
    chunks = load_evidence_chunks()

    assert {chunk.id for chunk in chunks}.issuperset(
        {
            "workflow-01-scope",
            "schema-beta-contract",
            "interpretation-limits",
        }
    )
    assert all(chunk.source for chunk in chunks)
    assert all(chunk.section for chunk in chunks)


def test_build_default_workflow_context_uses_local_evidence() -> None:
    context_package = build_default_workflow_context(
        markers=["cg000001"],
        qc_metrics={
            "row_count": 5.0,
            "missing_beta_pct": 0.0,
            "beta_min": 0.1,
            "beta_max": 0.9,
        },
        coverage_status="partial",
    )

    assert context_package.retrieved_chunks
    assert context_package.citations
    assert "Workflow 01 panel coverage status: partial" in context_package.user_message
    assert all(chunk.source.startswith(("docs/", "data/")) for chunk in context_package.retrieved_chunks)


def test_evidence_contract_rejects_missing_source(tmp_path) -> None:
    index_path = tmp_path / "bad_chunks.json"
    index_path.write_text(
        json.dumps(
            [
                {
                    "id": "bad",
                    "text": "Unsupported local source.",
                    "source": "docs/does_not_exist.md",
                    "section": "Missing",
                    "metadata": {
                        "evidence_type": "workflow_contract",
                        "claim_scope": "repo_behavior",
                        "allowed_use": "test",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_evidence_chunks(index_path=index_path, repo_root=tmp_path)
    except EvidenceContractError as error:
        assert "source does not exist" in str(error)
    else:
        raise AssertionError("Expected missing local source to fail the evidence contract")


def test_external_source_policy_defines_rag_gate() -> None:
    policy = load_external_source_policy()
    source_type_ids = {source_type["id"] for source_type in policy["allowed_source_types"]}

    assert policy["runtime_enabled"] is False
    assert source_type_ids == {
        "peer_reviewed_primary_study",
        "systematic_review_or_meta_analysis",
        "official_database_record",
        "official_guidance_or_reference",
    }
    assert "unreviewed_llm_output" in policy["disallowed_source_types"]
    assert {"chunk_id", "source_type", "retrieved_at", "reviewed_at", "limitations"}.issubset(
        set(policy["citation_requirements"])
    )
    assert policy["review_gate"]["review_required_before_runtime_use"] is True
    assert policy["review_gate"]["source_registry_required"] is True


def test_external_source_policy_rejects_runtime_enabled_without_approval(tmp_path) -> None:
    policy_path = tmp_path / "external_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "policy_version": "0.1",
                "status": "planning_contract_only",
                "runtime_enabled": True,
                "allowed_source_types": [
                    {
                        "id": "peer_reviewed_primary_study",
                        "label": "Peer-reviewed primary study",
                        "allowed_uses": ["background_context"],
                        "required_metadata": ["title"],
                        "freshness": {
                            "metadata_verified_within_days": 180,
                            "content_review_expires_after_days": 365,
                        },
                    }
                ],
                "disallowed_source_types": ["unreviewed_llm_output"],
                "citation_requirements": ["chunk_id"],
                "claim_boundaries": ["No diagnosis."],
                "review_gate": {
                    "review_required_before_runtime_use": True,
                    "source_registry_required": True,
                },
            }
        ),
        encoding="utf-8",
    )

    try:
        load_external_source_policy(policy_path=policy_path)
    except EvidenceContractError as error:
        assert "runtime_enabled false" in str(error)
    else:
        raise AssertionError("Expected runtime-enabled external RAG policy to fail without approval")
