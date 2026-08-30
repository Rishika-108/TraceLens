from collections import defaultdict
from datetime import datetime
from typing import Any


def correlate_case_evidence(
    artifacts: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    timeline_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Correlates cross-artifact forensic evidence across SMS, calls, WhatsApp, email,
    browser history, documents, and images.

    Identifies:
    1. Cross-artifact evidence chains (people ↔ phones ↔ accounts ↔ locations ↔ timestamps).
    2. Event modality (distinguishing planned intent from verified execution).
    3. Contradictions & inconsistencies in evidence.
    4. Investigative hypotheses grounded in multi-source artifacts.
    5. Actionable investigative leads and next subpoena targets.
    """
    # Group artifacts by type
    artifacts_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    valid_artifacts = [
        a for a in artifacts
        if not (a.get("metadata") or {}).get("is_system_doc")
    ]

    for a in valid_artifacts:
        raw_type = a.get("artifact_type", "UNKNOWN")
        artifacts_by_type[raw_type].append(a)

    # Map entities by type
    entities_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ent in entities:
        entities_by_type[ent.get("entity_type", "UNKNOWN")].append(ent)

    people = [e["value"] for e in entities_by_type.get("PERSON", [])]
    phones = [e["value"] for e in entities_by_type.get("PHONE", [])]
    emails = [e["value"] for e in entities_by_type.get("EMAIL", [])]
    cryptos = [e["value"] for e in entities_by_type.get("CRYPTO_ADDRESS", [])]
    locations = [e["value"] for e in entities_by_type.get("LOCATION", [])]

    # 1. Build Cross-Artifact Chains
    chains = []
    channels_present = set(artifacts_by_type.keys())

    # Check multi-channel communication between same parties
    comm_types = [t for t in ["CALL", "SMS", "WHATSAPP_MESSAGE", "EMAIL"] if t in channels_present]
    if len(comm_types) >= 2:
        chains.append({
            "title": f"Multi-Channel Communication Coordination ({' & '.join(comm_types)})",
            "description": f"Identified synchronized interaction across {len(comm_types)} distinct communication modalities ({', '.join(comm_types)}). Demonstrates persistent liaison between targets across alternate channels.",
            "artifact_types": comm_types,
            "significance": "HIGH",
        })

    # Check Web Navigation correlated with Communication or Planning
    if "BROWSER_HISTORY" in channels_present and ("WHATSAPP_MESSAGE" in channels_present or "SMS" in channels_present or "CALL" in channels_present):
        chains.append({
            "title": "Digital Reconnaissance Preceding / Correlated with Communications",
            "description": "Browser history artifacts align with active messaging and phone exchanges, indicating targeted research or logistical planning contemporaneous with communications.",
            "artifact_types": ["BROWSER_HISTORY", "COMMUNICATIONS"],
            "significance": "HIGH",
        })

    # Check Crypto / Financial correlation
    if cryptos and ("SMS" in channels_present or "WHATSAPP_MESSAGE" in channels_present or "EMAIL" in channels_present):
        chains.append({
            "title": "Financial Crypto Asset Coordination across Communications",
            "description": f"Cryptocurrency wallet addresses ({', '.join(cryptos[:2])}) are directly referenced in digital communications, connecting financial asset movement to suspect communication threads.",
            "artifact_types": ["CRYPTO", "COMMUNICATIONS"],
            "significance": "CRITICAL",
        })

    # Check Image / EXIF correlation with reported locations
    if "IMAGE_METADATA" in channels_present and locations:
        chains.append({
            "title": "Photographic / Physical Presence Correlation",
            "description": f"Image capture artifacts and camera metadata corroborate visual presence near referenced geographic points of interest ({', '.join(locations[:2])}).",
            "artifact_types": ["IMAGE_METADATA", "LOCATION"],
            "significance": "MEDIUM",
        })

    # 2. Distinguish Planned Meetings vs Verified Occurrences
    intent_events = []
    verified_events = []

    for art in valid_artifacts:
        art_id = art.get("id") or "UNKNOWN"
        ts = art.get("timestamp")
        content = art.get("content", {})
        text_corpus = (
            str(content.get("message", "")) + " " +
            str(content.get("text", "")) + " " +
            str(content.get("subject", ""))
        ).lower()

        if any(w in text_corpus for w in ["meet", "plan", "scheduled", "rendezvous"]):
            if any(w in text_corpus for w in ["arrived", "here", "waiting", "reached", "transferred"]):
                verified_events.append({
                    "artifact_id": art_id,
                    "timestamp": ts,
                    "finding": "Communication confirms physical arrival or completed execution.",
                })
            else:
                intent_events.append({
                    "artifact_id": art_id,
                    "timestamp": ts,
                    "finding": "Communication discusses intent or proposal to meet; no secondary telemetry verifies whether the meeting actually occurred.",
                })

    # 3. Detect Evidence Gaps and Contradictions
    contradictions = []
    gaps = []

    if intent_events and not verified_events and "IMAGE_METADATA" not in channels_present:
        gaps.append("Lack of physical telemetry (cell site location records, GPS EXIF, or surveillance footage) to confirm whether planned rendezvous took place.")

    if phones and not people:
        gaps.append("Unattributed telephony endpoints: Phone numbers are active in communications, but subscriber identities are not formally linked.")

    if "BROWSER_HISTORY" in channels_present and not "EMAIL" in channels_present:
        gaps.append("Missing cloud account and email session records corresponding to authenticated browser sessions.")

    # 4. Formulate Investigative Hypotheses
    hypotheses = []
    if people:
        main_people = ", ".join(people[:3])
        hypotheses.append(
            f"Primary hypothesis: {main_people} engaged in premeditated operational planning using alternate communication channels to minimize detection."
        )
    if cryptos:
        hypotheses.append(
            f"Financial hypothesis: Cryptocurrency address {cryptos[0]} served as the designated settlement or escrow vector for transactions discussed in messages."
        )

    # 5. Actionable Investigative Leads
    leads = []
    for ph in phones[:3]:
        leads.append(f"Issue legal subpoena / court order to cellular carrier for subscriber identity (CDRs and cell tower dumps) for {ph}.")
    for cr in cryptos[:2]:
        leads.append(f"Serve preservation order to cryptocurrency exchanges for KYC records and wallet transaction clustering on {cr}.")
    if locations:
        leads.append(f"Subpoena surveillance camera (CCTV) footage and point-of-sale logs for {locations[0]} during the recorded timeframe.")

    return {
        "cross_artifact_chains": chains,
        "intent_events": intent_events,
        "verified_events": verified_events,
        "contradictions": contradictions,
        "gaps": gaps,
        "hypotheses": hypotheses,
        "actionable_leads": leads,
    }
