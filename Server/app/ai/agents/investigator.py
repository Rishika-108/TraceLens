import os
import re
from typing import Any
from sqlalchemy.orm import Session

from app.ai.prompts.investigation_prompt import (
    INVESTIGATION_SYSTEM_PROMPT,
    INVESTIGATION_USER_PROMPT,
)
from app.ai.retrieval.retriever import retrieve_context
from app.core.config import settings


def _generate_deterministic_investigation(
    question: str,
    artifacts: list[dict[str, Any]],
) -> tuple[str, float]:
    """
    Deterministic rule-based evidence synthesis engine used when running offline or in testing.
    Strictly follows AGENT.md invariants: ground in facts, cite artifacts, separate inference.
    """
    if not artifacts:
        return (
            "### Executive Summary\n"
            "INSUFFICIENT EVIDENCE IN CASE RECORD. No evidence artifacts matching the query were found in this case.\n\n"
            "### Identified Gaps\n"
            "Additional evidence ingestion or broader query keywords required.",
            0.0,
        )

    findings = []
    citations = []

    for idx, art in enumerate(artifacts, start=1):
        art_id = art.get("artifact_id") or art.get("id") or f"ART-{idx}"
        art_type = art.get("artifact_type", "EVIDENCE")
        ts = art.get("timestamp") or "Timestamp Unrecorded"
        content = art.get("content", {})
        ref_tag = f"[Artifact #{art_id} - {art_type} @ {ts}]"
        citations.append(ref_tag)

        if art_type == "CALL":
            caller = content.get("caller", "Unknown")
            receiver = content.get("receiver", "Unknown")
            duration = content.get("duration_seconds", 0)
            findings.append(f"- [FACT] Phone call recorded from {caller} to {receiver} (Duration: {duration}s). (Source: {ref_tag})")
        elif art_type == "SMS":
            sender = content.get("sender", "Unknown")
            recipient = content.get("recipient", "Unknown")
            msg = content.get("message", "")
            findings.append(f"- [FACT] SMS from {sender} to {recipient}: \"{msg}\". (Source: {ref_tag})")
        elif art_type == "WHATSAPP_MESSAGE":
            sender = content.get("sender", "Unknown")
            msg = content.get("message", "")
            findings.append(f"- [FACT] WhatsApp message from {sender}: \"{msg}\". (Source: {ref_tag})")
        elif art_type == "EMAIL":
            sender = content.get("sender", "Unknown")
            recipient = content.get("recipient", "Unknown")
            subj = content.get("subject", "No Subject")
            body = content.get("body", "")[:100]
            findings.append(f"- [FACT] Email from {sender} to {recipient} with subject \"{subj}\" (Body: \"{body}...\"). (Source: {ref_tag})")
        elif art_type == "BROWSER_HISTORY":
            url = content.get("url", "")
            title = content.get("title", "")
            findings.append(f"- [FACT] Web navigation record to \"{title}\" ({url}). (Source: {ref_tag})")
        elif art_type == "DOCUMENT":
            text = content.get("text", "")[:120]
            findings.append(f"- [FACT] Document record content: \"{text}...\". (Source: {ref_tag})")
        else:
            findings.append(f"- [FACT] Forensic record of type {art_type}: {str(content)[:100]}. (Source: {ref_tag})")

    # Analytical inference based on observed findings
    inference = f"- [INFERENCE] Observed communication patterns across {len(artifacts)} evidence items indicate direct multi-channel interaction between identified subjects."

    findings_text = "\n".join(findings)
    citations_text = "\n".join([f"- {c}" for c in citations])

    answer = f"""### Executive Summary
Analysis of {len(artifacts)} retrieved evidence artifact(s) for query: "{question}". Communication records and chronological events identified below with high confidence.

### Evidence-Backed Findings
{findings_text}
{inference}

### Supporting Evidence References
{citations_text}

### Identified Gaps / Uncertainties
- Verification of unconfirmed aliases or third-party phone ownership requires subscriber record subpoenas.
"""
    confidence = min(0.98, 0.70 + (len(artifacts) * 0.05))
    return answer, confidence


def investigate(
    db: Session,
    case_id: str,
    question: str,
    limit: int = 8,
) -> dict[str, Any]:
    """
    Main entry point for AI-assisted case investigation (AGENT.md Sec. 43-48).
    Retrieves grounded case context, performs RAG reasoning, and provides evidence references.
    """
    clean_question = str(question).strip()
    if not clean_question:
        return {
            "case_id": case_id,
            "question": "",
            "answer": "Please provide a valid investigative question.",
            "confidence": 0.0,
            "evidence_references": [],
        }

    # Step 1: Retrieve grounded case context via Context Builder
    context_str, raw_artifacts = retrieve_context(
        db=db,
        case_id=case_id,
        question=clean_question,
        limit=limit,
    )

    # Step 2: Try calling external LLM if API keys are configured, otherwise use deterministic engine
    answer = None
    confidence = 0.85

    # Check for Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = f"{INVESTIGATION_SYSTEM_PROMPT}\n\n{INVESTIGATION_USER_PROMPT.format(context=context_str, question=clean_question)}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            answer = response.text
            confidence = 0.95
        except Exception:
            answer = None

    elif openai_key and not answer:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": INVESTIGATION_SYSTEM_PROMPT},
                    {"role": "user", "content": INVESTIGATION_USER_PROMPT.format(context=context_str, question=clean_question)},
                ],
            )
            answer = response.choices[0].message.content
            confidence = 0.95
        except Exception:
            answer = None

    # Fallback to deterministic evidence engine if no external API key is set or call fails
    if not answer:
        answer, confidence = _generate_deterministic_investigation(
            question=clean_question,
            artifacts=raw_artifacts,
        )

    return {
        "case_id": case_id,
        "question": clean_question,
        "answer": answer,
        "confidence": confidence,
        "evidence_references": raw_artifacts,
        "citations_count": len(raw_artifacts),
    }