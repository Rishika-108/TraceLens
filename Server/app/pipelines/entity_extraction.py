import re
from typing import Any
from uuid import uuid4


PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
IPV4_PATTERN = re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
CRYPTO_BTC_PATTERN = re.compile(r"\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b")
CRYPTO_ETH_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
DOMAIN_PATTERN = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+(?:com|org|net|edu|gov|io|ch|de|uk|in|co|biz|info)\b", re.IGNORECASE)

ORG_KEYWORDS = ["bank", "corp", "corporation", "ltd", "llc", "group", "fbi", "police", "interpol", "department", "ministry", "agency", "hospital", "customs"]
LOCATION_KEYWORDS = ["road", "street", "avenue", "lane", "boulevard", "hotel", "airport", "station", "building", "warehouse", "dock", "terminal", "zurich", "london", "paris", "tokyo", "delhi", "mumbai", "berlin", "dubai", "singapore", "new york"]


def extract_entities_from_artifact(artifact: dict[str, Any], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Extracts multi-type forensic entities from a single artifact (phones, emails, people, orgs, crypto, IPs, locations).
    """
    entities: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    artifact_id = artifact.get("id")
    content = artifact.get("content", {})
    raw_type = artifact.get("artifact_type", "")

    def add_entity(entity_type: str, value: str):
        val = value.strip().rstrip(".,;:")
        if not val or len(val) < 2 or (entity_type, val.lower()) in seen:
            return
        # Ignore common non-entity false positives
        if val.lower() in ["unknown", "none", "null", "system", "user", "author"]:
            return

        seen.add((entity_type, val.lower()))
        entities.append({
            "id": str(uuid4()),
            "case_id": case_id or artifact.get("case_id"),
            "artifact_id": artifact_id,
            "entity_type": entity_type,
            "value": val,
        })

    # 1. Extract from structured fields
    if "caller" in content and content["caller"]:
        add_entity("PHONE" if re.search(r"\d", content["caller"]) else "PERSON", content["caller"])
    if "receiver" in content and content["receiver"]:
        add_entity("PHONE" if re.search(r"\d", content["receiver"]) else "PERSON", content["receiver"])
    if "sender" in content and content["sender"]:
        sender_val = content["sender"]
        if "@" in sender_val:
            add_entity("EMAIL", sender_val)
        elif re.search(r"^\+?\d[\d\s\-]{7,}", sender_val):
            add_entity("PHONE", sender_val)
        else:
            add_entity("PERSON", sender_val)
    if "recipient" in content and content["recipient"]:
        recip_val = content["recipient"]
        if "@" in recip_val:
            add_entity("EMAIL", recip_val)
        elif re.search(r"^\+?\d[\d\s\-]{7,}", recip_val):
            add_entity("PHONE", recip_val)
        else:
            add_entity("PERSON", recip_val)

    # 2. Extract from unstructured text contents
    full_text = " ".join([
        str(v) for k, v in content.items() if isinstance(v, (str, int, float))
    ])
    if artifact.get("raw_data"):
        full_text += " " + str(artifact["raw_data"])

    # Phone Numbers
    for match in PHONE_PATTERN.finditer(full_text):
        phone = match.group(0).strip()
        digits = re.sub(r"\D", "", phone)
        if 7 <= len(digits) <= 15:
            add_entity("PHONE", phone)

    # Email Addresses
    for match in EMAIL_PATTERN.finditer(full_text):
        add_entity("EMAIL", match.group(0))

    # IP Addresses
    for match in IPV4_PATTERN.finditer(full_text):
        ip = match.group(0)
        if not ip.startswith("127.") and not ip.startswith("0."):
            add_entity("IP_ADDRESS", ip)

    # Crypto Addresses (Bitcoin & Ethereum)
    for match in CRYPTO_ETH_PATTERN.finditer(full_text):
        add_entity("CRYPTO_ADDRESS", match.group(0))
    for match in CRYPTO_BTC_PATTERN.finditer(full_text):
        add_entity("CRYPTO_ADDRESS", match.group(0))

    # Domains
    for match in DOMAIN_PATTERN.finditer(full_text):
        domain = match.group(0).lower()
        if not domain.startswith("http") and "@" not in domain:
            add_entity("DOMAIN", domain)

    # Organizations
    for sentence in re.split(r"[.\n;]", full_text):
        sentence_clean = sentence.strip()
        for kw in ORG_KEYWORDS:
            if re.search(rf"\b{kw}\b", sentence_clean, re.IGNORECASE):
                # Extract proper noun phrase or surrounding words
                words = sentence_clean.split()
                for i, w in enumerate(words):
                    if kw in w.lower():
                        org_phrase = " ".join(words[max(0, i - 2):min(len(words), i + 3)])
                        if len(org_phrase) > 3 and not any(c in org_phrase for c in ["@", "http", "/"]):
                            add_entity("ORG", org_phrase)
                            break

    # Locations
    for sentence in re.split(r"[.\n;]", full_text):
        sentence_clean = sentence.strip()
        for kw in LOCATION_KEYWORDS:
            if re.search(rf"\b{kw}\b", sentence_clean, re.IGNORECASE):
                words = sentence_clean.split()
                for i, w in enumerate(words):
                    if kw in w.lower():
                        loc_phrase = " ".join(words[max(0, i - 2):min(len(words), i + 3)])
                        if len(loc_phrase) > 3 and not any(c in loc_phrase for c in ["@", "http", "/"]):
                            add_entity("LOCATION", loc_phrase)
                            break

    return entities


def extract_entities(artifacts: list[dict[str, Any]], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Extracts all entities across a collection of artifacts.
    """
    all_entities: list[dict[str, Any]] = []
    for artifact in artifacts:
        all_entities.extend(extract_entities_from_artifact(artifact, case_id))
    return all_entities