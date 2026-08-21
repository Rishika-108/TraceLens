from collections import defaultdict
from itertools import combinations
from typing import Any
from uuid import uuid4


def discover_relationships_from_artifacts(
    artifacts: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    case_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Discovers evidence-grounded relationships between entities based on direct communications
    and artifact co-occurrences.
    """
    relationships: list[dict[str, Any]] = []
    
    # Map entity value -> entity object
    value_to_entity: dict[str, dict[str, Any]] = {}
    for ent in entities:
        value_to_entity[ent["value"].lower().strip()] = ent

    # Group entities by originating artifact_id
    artifact_entities: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ent in entities:
        art_id = ent.get("artifact_id")
        if art_id:
            artifact_entities[art_id].append(ent)

    # Track interactions and co-occurrence counts: (source_id, target_id, rel_type) -> count
    interaction_counts: dict[tuple[str, str, str], int] = defaultdict(int)

    for artifact in artifacts:
        art_id = artifact.get("id")
        content = artifact.get("content", {})
        raw_type = artifact.get("artifact_type", "")

        # 1. Direct Communication Channels
        source_val = None
        target_val = None
        rel_type = "COMMUNICATES_WITH"

        if raw_type == "CALL":
            source_val = content.get("caller")
            target_val = content.get("receiver")
            rel_type = "CALLS"
        elif raw_type == "SMS":
            source_val = content.get("sender")
            target_val = content.get("recipient")
            rel_type = "MESSAGES"
        elif raw_type == "EMAIL":
            source_val = content.get("sender")
            target_val = content.get("recipient")
            rel_type = "EMAILS"
        elif raw_type == "WHATSAPP_MESSAGE":
            source_val = content.get("sender")
            # If in 1-on-1 or group chat
            rel_type = "CHATS_WITH"

        if source_val and target_val:
            src_ent = value_to_entity.get(str(source_val).lower().strip())
            tgt_ent = value_to_entity.get(str(target_val).lower().strip())

            if src_ent and tgt_ent and src_ent["id"] != tgt_ent["id"]:
                interaction_counts[(src_ent["id"], tgt_ent["id"], rel_type)] += 1

        # 2. Co-occurrence of entities in the same artifact
        ents_in_art = artifact_entities.get(art_id, [])
        if len(ents_in_art) >= 2:
            # Pairwise within the same artifact
            for e1, e2 in combinations(ents_in_art, 2):
                if e1["id"] == e2["id"]:
                    continue
                # Order pair canonically to avoid duplicate bidirectional pairs
                pair = tuple(sorted([e1["id"], e2["id"]]))
                interaction_counts[(pair[0], pair[1], "CO_OCCURS_WITH")] += 1

    # Convert counts to Relationship records with calculated confidence
    seen_pairs: set[tuple[str, str, str]] = set()

    for (src_id, tgt_id, r_type), count in interaction_counts.items():
        if (src_id, tgt_id, r_type) in seen_pairs:
            continue
        seen_pairs.add((src_id, tgt_id, r_type))

        # Confidence heuristic: Direct communication has high baseline (0.9 + min(0.09, count*0.02))
        # Co-occurrence starts at 0.7 + min(0.25, count * 0.05)
        if r_type in ["CALLS", "MESSAGES", "EMAILS", "CHATS_WITH"]:
            confidence = min(0.99, 0.90 + (count * 0.02))
        else:
            confidence = min(0.95, 0.70 + (count * 0.05))

        relationships.append({
            "id": str(uuid4()),
            "case_id": case_id,
            "source_entity_id": src_id,
            "target_entity_id": tgt_id,
            "relationship_type": r_type,
            "confidence": f"{confidence:.2f}",
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

    # Fallback: if only entities list is passed without artifacts
    relationships = []
    for source, target in combinations(entities, 2):
        if source.get("id") == target.get("id") or source.get("value") == target.get("value"):
            continue
        relationships.append({
            "id": str(uuid4()),
            "case_id": case_id or source.get("case_id"),
            "source_entity_id": source["id"],
            "target_entity_id": target["id"],
            "relationship_type": "CO_OCCURRENCE",
            "confidence": "0.75",
        })
    return relationships