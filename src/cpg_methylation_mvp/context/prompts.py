"""Prompt construction for future evidence-grounded interpretation helpers."""

from __future__ import annotations

from .types import Chunk, DatasetSummary

SYSTEM_PROMPT = """You support an educational CpG methylation demo.
Use only the provided aggregated summary and retrieved snippets.
Do not make diagnostic, treatment, or clinical-readiness claims.
If retrieved evidence is missing or weak, state that limitation clearly.
Cite source chunk IDs when discussing retrieved evidence."""


def build_user_message(
    markers: list[str],
    summary: DatasetSummary,
    chunks: list[Chunk],
) -> str:
    """Build a compact user message from aggregated summary and retrieved chunks."""
    marker_text = ", ".join(markers) if markers else "none provided"
    beta_range = (
        f"{summary.beta_range[0]:.3f} to {summary.beta_range[1]:.3f}"
        if summary.beta_range is not None
        else "not provided"
    )
    notes = summary.notes or "none"
    retrieved_text = "\n".join(_format_chunk(chunk) for chunk in chunks) or "No retrieved snippets."

    return "\n".join(
        [
            "Task: Provide a cautious educational context summary for the methylation upload.",
            "",
            "Aggregated dataset summary:",
            f"- Row count: {summary.row_count}",
            f"- Missing beta percent: {summary.missing_pct:.2f}",
            f"- Platform: {summary.platform or 'unknown'}",
            f"- Beta range: {beta_range}",
            f"- Notes: {notes}",
            "",
            f"Markers of interest: {marker_text}",
            "",
            "Retrieved snippets:",
            retrieved_text,
            "",
            "Response requirements:",
            "- Separate observations, limitations, and suggested next analytical checks.",
            "- Keep the response non-diagnostic.",
            "- Mark unsupported claims as unknown rather than guessing.",
        ]
    )


def _format_chunk(chunk: Chunk) -> str:
    section_text = f", section={chunk.section}" if chunk.section else ""
    score_text = f", score={chunk.score:.3f}" if chunk.score is not None else ""
    return f"- [{chunk.id}] source={chunk.source}{section_text}{score_text}: {chunk.text}"
