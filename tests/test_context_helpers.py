from __future__ import annotations

import json

from cpg_methylation_mvp.context import (
    Chunk,
    DatasetSummary,
    KeywordRetriever,
    MockRetriever,
    build_context,
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
