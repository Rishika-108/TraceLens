import re
from typing import Any


def evaluate(answer: str, retrieved_artifacts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Evaluates an AI investigation response for evidentiary rigor and grounding (AGENT.md Sec. 53).
    """
    text = str(answer)

    # Check for citation references ([Artifact #...] or [EVIDENCE_REF #...])
    citations = re.findall(r"\[(?:Artifact|EVIDENCE_REF)[^\]]+\]", text, re.IGNORECASE)
    citation_count = len(citations)
    has_citations = citation_count > 0

    # Check for fact vs inference separation
    has_fact_tags = "[FACT]" in text or "FACT:" in text
    has_inference_tags = "[INFERENCE]" in text or "INFERENCE:" in text

    # Check for insufficient evidence acknowledgment
    has_insufficient_notice = "INSUFFICIENT EVIDENCE" in text.upper() or "NOT ENOUGH EVIDENCE" in text.upper()

    # Check for timeline mentions
    has_timeline = "TIMELINE" in text.upper() or bool(re.search(r"\d{1,2}:\d{2}", text))

    # Scoring metric
    score = 0.0
    if has_citations or has_insufficient_notice:
        score += 0.4
    if has_fact_tags:
        score += 0.3
    if has_inference_tags:
        score += 0.15
    if has_timeline:
        score += 0.15

    return {
        "evaluation_score": round(score, 2),
        "is_grounded": has_citations or has_insufficient_notice,
        "citation_count": citation_count,
        "has_fact_tags": has_fact_tags,
        "has_inference_tags": has_inference_tags,
        "has_insufficient_notice": has_insufficient_notice,
        "has_timeline_references": has_timeline,
    }