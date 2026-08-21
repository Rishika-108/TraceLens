import os
from typing import Any
from sqlalchemy.orm import Session

from app.ai.prompts.report_prompt import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.entity_repository import EntityRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.timeline_repository import TimelineRepository


def generate_case_report(
    db: Session,
    case_id: str,
    title: str | None = None,
) -> dict[str, Any]:
    """
    Generates a formal, evidence-backed Case Intelligence Report (AGENT.md Sec. 50-51).
    Synthesizes timeline events, extracted entities, relationship graphs, and source evidence.
    """
    case = CaseRepository.get_by_id(db, case_id)
    case_title = case.title if case else f"Case {case_id}"
    report_title = title or f"Forensic Case Intelligence Report: {case_title}"

    # Fetch structured case components
    evidence_list = EvidenceRepository.get_by_case(db, case_id)
    timeline_events = TimelineRepository.get_by_case(db, case_id)
    entities = EntityRepository.get_by_case(db, case_id)
    relationships = RelationshipRepository.get_by_case(db, case_id)
    artifacts = ArtifactRepository.get_by_case(db, case_id)

    # Format summaries for AI / Report synthesis
    timeline_lines = [
        f"- [{e.event_timestamp.isoformat() if e.event_timestamp else 'N/A'}] ({e.event_type}) {e.description}"
        for e in timeline_events[:30]
    ]
    timeline_summary = "\n".join(timeline_lines) if timeline_lines else "No chronological events recorded."

    entity_lines = [f"- [{e.entity_type}] {e.value}" for e in entities[:40]]
    entity_summary = "\n".join(entity_lines) if entity_lines else "No entities extracted."

    relationship_lines = [
        f"- {r.relationship_type} (Confidence: {r.confidence})"
        for r in relationships[:30]
    ]
    relationship_summary = "\n".join(relationship_lines) if relationship_lines else "No relationships mapped."

    context_preview = "\n".join([
        f"- [Artifact #{a.id} | {a.artifact_type}] {str(a.content)[:120]}"
        for a in artifacts[:20]
    ])

    # Check for external LLM client
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    narrative_report = None

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = (
                f"{REPORT_SYSTEM_PROMPT}\n\n"
                f"{REPORT_USER_PROMPT.format(case_title=case_title, case_id=case_id, timeline_summary=timeline_summary, entity_summary=entity_summary, relationship_summary=relationship_summary, context=context_preview)}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            narrative_report = response.text
        except Exception:
            narrative_report = None

    # Fallback to structured forensic report generator
    if not narrative_report:
        narrative_report = f"""# {report_title}

## 1. Executive Summary
This report presents intelligence derived from {len(evidence_list)} source evidence files across {len(artifacts)} parsed artifacts for case "{case_title}". A total of {len(timeline_events)} chronological events, {len(entities)} unique forensic entities, and {len(relationships)} inter-entity relationships were mapped.

## 2. Chronological Timeline Analysis
{timeline_summary}

## 3. Extracted Forensic Entities
{entity_summary}

## 4. Discovered Relationship & Communication Matrix
{relationship_summary}

## 5. Evidence Provenance & Audit Trail
All findings are grounded in verified source evidence records. Chain of custody and SHA-256 hashes are recorded for every ingested artifact.
"""

    summary_text = (
        f"Case Intelligence Report for '{case_title}': "
        f"{len(evidence_list)} Evidence files, {len(timeline_events)} Timeline events, "
        f"{len(entities)} Entities, and {len(relationships)} Relationships discovered."
    )

    structured_evidence_payload = {
        "case_id": case_id,
        "case_title": case_title,
        "narrative_report": narrative_report,
        "metrics": {
            "evidence_count": len(evidence_list),
            "artifacts_count": len(artifacts),
            "timeline_events_count": len(timeline_events),
            "entities_count": len(entities),
            "relationships_count": len(relationships),
        },
        "timeline": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "description": e.description,
                "timestamp": e.event_timestamp.isoformat() if e.event_timestamp else None,
            }
            for e in timeline_events
        ],
        "entities": [
            {
                "id": ent.id,
                "type": ent.entity_type,
                "value": ent.value,
            }
            for ent in entities
        ],
        "relationships": [
            {
                "id": r.id,
                "type": r.relationship_type,
                "confidence": r.confidence,
                "source_entity_id": r.source_entity_id,
                "target_entity_id": r.target_entity_id,
            }
            for r in relationships
        ],
    }

    return {
        "case_id": case_id,
        "title": report_title,
        "summary": summary_text,
        "evidence": structured_evidence_payload,
    }
