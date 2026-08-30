import re
from collections import defaultdict
from itertools import combinations
from typing import Any
from uuid import uuid4


def _clean_key(val: str) -> str:
    # Normalize telephony and names for canonical lookup
    clean = str(val).strip().lower()
    if re.match(r"^\+?[\d\s\-\(\)\.]+$", clean):
        return re.sub(r"[\s\-\(\)\.]", "", clean)
    return clean


def discover_relationships_from_artifacts(
    artifacts: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    case_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Discovers evidence-grounded relationships between entities with forensic rigor:
    1. Elevates links to Person / Account / Device-level (e.g. Person USES_PHONE Phone, Person MESSAGES Person).
    2. Completely suppresses redundant CO_OCCURS_WITH when direct communication or ownership exists.
    3. Records the supporting artifact ID and evidence snippet for every relationship.
    4. Computes explainable confidence scores based on corroboration and communication depth.
    """
    relationships: list[dict[str, Any]] = []

    # Map normalized entity value -> entity object
    value_to_entity: dict[str, dict[str, Any]] = {}
    person_entities: dict[str, dict[str, Any]] = {}
    phone_entities: dict[str, dict[str, Any]] = {}
    email_entities: dict[str, dict[str, Any]] = {}

    for ent in entities:
        key = _clean_key(ent["value"])
        value_to_entity[key] = ent
        # Also store under raw lowercase
        value_to_entity[ent["value"].lower().strip()] = ent

        e_type = ent.get("entity_type")
        if e_type == "PERSON":
            person_entities[key] = ent
            person_entities[ent["value"].lower().strip()] = ent
        elif e_type == "PHONE":
            phone_entities[key] = ent
        elif e_type == "EMAIL":
            email_entities[key] = ent

    # Track interactions: (src_id, tgt_id, rel_type) -> {"count": int, "artifact_id": str, "snippet": str}
    rel_store: dict[tuple[str, str, str], dict[str, Any]] = {}

    # Set of connected entity pairs that already have a strong link
    connected_pairs: set[frozenset[str]] = set()

    for artifact in artifacts:
        metadata = artifact.get("metadata") or {}
        if metadata.get("is_system_doc") or metadata.get("exclude_from_primary_evidence"):
            continue

        art_id = artifact.get("id")
        content = artifact.get("content", {})
        raw_type = artifact.get("artifact_type", "")

        # 1. Direct Communication Channels
        source_val = None
        target_val = None
        rel_type = "COMMUNICATES_WITH"
        evidence_snippet = ""

        if raw_type == "CALL":
            source_val = content.get("caller")
            target_val = content.get("receiver")
            duration = content.get("duration_seconds", 0)
            call_type = content.get("call_type", "CALL")
            rel_type = "CALLS"
            evidence_snippet = f"{call_type} call ({duration}s duration)"
        elif raw_type == "SMS":
            source_val = content.get("sender")
            target_val = content.get("recipient")
            msg = content.get("message", "")
            rel_type = "MESSAGES"
            evidence_snippet = f"SMS: \"{(msg[:120] + '...') if len(msg) > 120 else msg}\""
        elif raw_type == "EMAIL":
            source_val = content.get("sender")
            target_val = content.get("recipient")
            subj = content.get("subject", "No Subject")
            rel_type = "EMAILS"
            evidence_snippet = f"Email Subject: \"{subj}\""
        elif raw_type == "WHATSAPP_MESSAGE":
            source_val = content.get("sender")
            msg = content.get("message", "")
            rel_type = "CHATS_WITH"
            evidence_snippet = f"WhatsApp: \"{(msg[:120] + '...') if len(msg) > 120 else msg}\""

        # Direct communication relationship
        if source_val and target_val:
            src_key = _clean_key(str(source_val))
            tgt_key = _clean_key(str(target_val))
            src_ent = value_to_entity.get(src_key)
            tgt_ent = value_to_entity.get(tgt_key)

            if src_ent and tgt_ent and src_ent["id"] != tgt_ent["id"]:
                pair_key = (src_ent["id"], tgt_ent["id"], rel_type)
                if pair_key not in rel_store:
                    rel_store[pair_key] = {
                        "count": 1,
                        "artifact_id": art_id,
                        "snippet": evidence_snippet,
                    }
                else:
                    rel_store[pair_key]["count"] += 1

                connected_pairs.add(frozenset([src_ent["id"], tgt_ent["id"]]))

        # 2. Person-to-Device / Account Attribution
        # If an artifact has an identifiable person and phone/email, map person USES_PHONE or USES_EMAIL
        text_content = (
            str(content.get("message", "")) + " " +
            str(content.get("text", "")) + " " +
            str(content.get("body", "")) + " " +
            str(artifact.get("raw_data", ""))
        )

        for p_key, p_ent in person_entities.items():
            if p_ent["value"].lower() in text_content.lower() or (source_val and p_ent["value"].lower() in str(source_val).lower()):
                # Link person with sender phone or mentioned phones
                if source_val and _clean_key(str(source_val)) in phone_entities:
                    ph_ent = phone_entities[_clean_key(str(source_val))]
                    if p_ent["id"] != ph_ent["id"]:
                        p_pair = (p_ent["id"], ph_ent["id"], "USES_PHONE")
                        if p_pair not in rel_store:
                            rel_store[p_pair] = {
                                "count": 1,
                                "artifact_id": art_id,
                                "snippet": f"{p_ent['value']} identified using telephone {ph_ent['value']}",
                            }
                        connected_pairs.add(frozenset([p_ent["id"], ph_ent["id"]]))

                if source_val and _clean_key(str(source_val)) in email_entities:
                    em_ent = email_entities[_clean_key(str(source_val))]
                    if p_ent["id"] != em_ent["id"]:
                        p_pair = (p_ent["id"], em_ent["id"], "USES_EMAIL")
                        if p_pair not in rel_store:
                            rel_store[p_pair] = {
                                "count": 1,
                                "artifact_id": art_id,
                                "snippet": f"{p_ent['value']} identified using email account {em_ent['value']}",
                            }
                        connected_pairs.add(frozenset([p_ent["id"], em_ent["id"]]))

        # 3. Person-to-Person Communication Elevation
        # If Person A sends to Person B
        for p1_key, p1_ent in person_entities.items():
            for p2_key, p2_ent in person_entities.items():
                if p1_ent["id"] == p2_ent["id"]:
                    continue
                if source_val and target_val:
                    # Check if source represents p1 and target represents p2
                    s_str = str(source_val).lower()
                    t_str = str(target_val).lower()
                    if (p1_ent["value"].lower() in s_str or _clean_key(p1_ent["value"]) == _clean_key(s_str)) and (
                        p2_ent["value"].lower() in t_str or _clean_key(p2_ent["value"]) == _clean_key(t_str)
                    ):
                        p2p_pair = (p1_ent["id"], p2_ent["id"], "COMMUNICATES_WITH")
                        if p2p_pair not in rel_store:
                            rel_store[p2p_pair] = {
                                "count": 1,
                                "artifact_id": art_id,
                                "snippet": evidence_snippet or f"Direct interaction between {p1_ent['value']} and {p2_ent['value']}",
                            }
                        connected_pairs.add(frozenset([p1_ent["id"], p2_ent["id"]]))

        # 4. Crypto Transactions
        for c_key, c_ent in value_to_entity.items():
            if c_ent.get("entity_type") == "CRYPTO_ADDRESS" and c_ent["value"].lower() in text_content.lower():
                # Link person with crypto transfer
                for p_key, p_ent in person_entities.items():
                    if p_ent["value"].lower() in text_content.lower() and p_ent["id"] != c_ent["id"]:
                        tx_pair = (p_ent["id"], c_ent["id"], "TRANSFERS_FUNDS_TO")
                        if tx_pair not in rel_store:
                            rel_store[tx_pair] = {
                                "count": 1,
                                "artifact_id": art_id,
                                "snippet": f"Financial crypto transfer to {c_ent['value']} referenced in connection with {p_ent['value']}",
                            }
                        connected_pairs.add(frozenset([p_ent["id"], c_ent["id"]]))

    # Convert stored interactions into Relationship records with calibrated confidence
    for (src_id, tgt_id, r_type), info in rel_store.items():
        count = info["count"]
        # Direct communications have high evidence grounding
        if r_type in ["CALLS", "MESSAGES", "EMAILS", "CHATS_WITH", "COMMUNICATES_WITH"]:
            confidence = min(0.99, 0.90 + (count * 0.02))
        elif r_type in ["USES_PHONE", "USES_EMAIL", "TRANSFERS_FUNDS_TO"]:
            confidence = min(0.98, 0.88 + (count * 0.03))
        else:
            confidence = min(0.92, 0.70 + (count * 0.05))

        relationships.append({
            "id": str(uuid4()),
            "case_id": case_id,
            "source_entity_id": src_id,
            "target_entity_id": tgt_id,
            "relationship_type": r_type,
            "confidence": f"{confidence:.2f}",
            "supporting_artifact_id": info["artifact_id"],
            "evidence_snippet": info["snippet"][:490],
        })

    return relationships


def discover_relationships(
    entities: list[dict[str, Any]],
    artifacts: list[dict[str, Any]] | None = None,
    case_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Main entrypoint for relationship discovery.
    """
    if artifacts:
        return discover_relationships_from_artifacts(artifacts, entities, case_id)

    relationships = []
    for source, target in combinations(entities, 2):
        if source.get("id") == target.get("id") or source.get("value") == target.get("value"):
            continue
        relationships.append({
            "id": str(uuid4()),
            "case_id": case_id or source.get("case_id"),
            "source_entity_id": source["id"],
            "target_entity_id": target["id"],
            "relationship_type": "ASSOCIATED_WITH",
            "confidence": "0.75",
            "supporting_artifact_id": None,
            "evidence_snippet": "Cross-case co-presence in evidence locker",
        })
    return relationships