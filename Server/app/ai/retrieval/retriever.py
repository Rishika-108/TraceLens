from typing import Any
from sqlalchemy.orm import Session

from app.ai.retrieval.semantic_search import search


def build_evidence_context(artifacts: list[dict[str, Any]]) -> str:
    """
    Context Builder (AGENT.md Sec. 42).
    Assembles retrieved evidence artifacts into an unambiguous, grounded context block
    with explicit artifact references for LLM citation.
    """
    if not artifacts:
        return "NO_RELEVANT_EVIDENCE_FOUND"

    blocks = []
    for idx, art in enumerate(artifacts, start=1):
        art_id = art.get("artifact_id") or art.get("id") or f"ART-{idx}"
        art_type = art.get("artifact_type", "UNKNOWN")
        ts = art.get("timestamp") or "NO_TIMESTAMP"
        content = art.get("content", {})

        content_lines = []
        for k, v in content.items():
            content_lines.append(f"  {k}: {v}")
        formatted_content = "\n".join(content_lines)

        raw_snippet = f"\n  Raw Snippet: {art.get('raw_data')[:200]}" if art.get("raw_data") else ""

        block = (
            f"[EVIDENCE_REF #{idx} | ID: {art_id} | TYPE: {art_type} | TIMESTAMP: {ts}]\n"
            f"{formatted_content}"
            f"{raw_snippet}"
        )
        blocks.append(block)

    return "\n\n---\n\n".join(blocks)


def retrieve_context(
    db: Session,
    case_id: str,
    question: str,
    limit: int = 8,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Retrieves case evidence relevant to the question and builds grounded LLM context.
    Returns (formatted_context_string, raw_retrieved_artifacts).
    """
    retrieved_artifacts = search(
        db=db,
        case_id=case_id,
        query=question,
        limit=limit,
    )

    context_str = build_evidence_context(retrieved_artifacts)
    return context_str, retrieved_artifacts