import re
from typing import Any
from uuid import uuid4


# Strict Telephony Phone Patterns
# 1. International format starting with +: e.g. +1 415 555 2671, +91-9876543210, +44 20 7946 0958
PHONE_INTL_PATTERN = re.compile(r"\+\d{1,4}[-.\s]?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b")
# 2. Formatted regional phone: e.g. (415) 555-2671, 415-555-2671, 020-7946-0958
PHONE_REGIONAL_PATTERN = re.compile(r"(?:\(\d{2,4}\)|\b\d{2,4})[-.\s]\d{3,4}[-.\s]\d{3,4}\b")
# 3. 10-digit contiguous mobile number
PHONE_10DIGIT_PATTERN = re.compile(r"\b[6-9]\d{9}\b")

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
IPV4_PATTERN = re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
CRYPTO_BTC_PATTERN = re.compile(r"\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b")
CRYPTO_ETH_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
DOMAIN_PATTERN = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+(?:com|org|net|edu|gov|io|ch|de|uk|in|co|biz|info)\b", re.IGNORECASE)

ORG_KEYWORDS = ["bank", "corp", "corporation", "ltd", "llc", "group", "fbi", "police", "interpol", "department", "ministry", "agency", "hospital", "customs"]
LOCATION_KEYWORDS = ["road", "street", "avenue", "lane", "boulevard", "hotel", "airport", "station", "building", "warehouse", "dock", "terminal", "zurich", "london", "paris", "tokyo", "delhi", "mumbai", "berlin", "dubai", "singapore", "new york"]


def is_valid_phone_number(candidate: str) -> bool:
    """
    Validates that a candidate string is genuinely a phone number and not a false positive
    such as an ISO date (2023-08-15), timestamp (14:30:00), IPv4 address, currency, or ID.
    """
    s = candidate.strip().rstrip(".,;:!?\"'")
    if not s:
        return False

    # 1. Must not contain letters (prevents suspect names or hex hashes like 0x123)
    if re.search(r"[a-zA-Z]", s):
        return False

    # 2. Must not contain colons (times like 14:30:00) or slashes (dates like 15/08/2023)
    if ":" in s or "/" in s:
        return False

    # 3. Must not contain currency symbols or percent signs
    if re.search(r"[$€£¥₹%]", s):
        return False

    # 4. Reject ISO Date formats: YYYY-MM-DD, YYYY.MM.DD, DD-MM-YYYY
    if re.match(r"^\d{4}[-.]\d{1,2}[-.]\d{1,2}$", s) or re.match(r"^\d{1,2}[-.]\d{1,2}[-.]\d{4}$", s):
        return False

    # 5. Reject IPv4 addresses: 192.168.1.1
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", s):
        return False

    digits = re.sub(r"\D", "", s)
    num_digits = len(digits)

    # Standard telephony digit length (E.164 max is 15 digits)
    if not (7 <= num_digits <= 15):
        return False

    # Reject repetitive single digits like 0000000000 or 11111111
    if len(set(digits)) <= 2:
        return False

    # 6. Reject pure integer numbers that are not standard 10 or 11 digit numbers
    # (e.g. 250000, 99881, 1000000 - amounts/account numbers without phone formatting)
    if s.isdigit():
        if num_digits not in (10, 11):
            return False
        # National mobile check: 10-digit mobile usually starts with 6-9 in many jurisdictions
        return True

    # 7. International number with + prefix
    if s.startswith("+"):
        return True

    # 8. Standard formatted numbers with parens or hyphens
    if re.match(r"^\(?\d{2,4}\)?[-.\s]\d{3,4}[-.\s]\d{3,4}$", s):
        return True

    return False


def classify_structured_party(value: str) -> tuple[str, str] | None:
    """
    Classifies a structured party field (caller, receiver, sender, recipient)
    as PERSON, EMAIL, or PHONE with strict validation.
    """
    clean_val = str(value).strip().rstrip(".,;:")
    if not clean_val or len(clean_val) < 2:
        return None

    # Ignore system notices and generic placeholders
    if clean_val.lower() in ["unknown", "none", "null", "system", "user", "author", "whatsapp", "chrome"]:
        return None

    # Email check
    if "@" in clean_val and EMAIL_PATTERN.search(clean_val):
        return ("EMAIL", clean_val)

    # Phone check
    if is_valid_phone_number(clean_val):
        return ("PHONE", clean_val)

    # Person name check: contains alphabetic characters
    if re.search(r"[a-zA-Z]", clean_val):
        return ("PERSON", clean_val)

    return None


def extract_entities_from_artifact(artifact: dict[str, Any], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Extracts multi-type forensic entities from a single artifact (phones, emails, people, orgs, crypto, IPs, locations).
    Filters false positives and deduplicates within the artifact.
    """
    entities: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    artifact_id = artifact.get("id")
    content = artifact.get("content", {})

    def add_entity(entity_type: str, value: str):
        val = value.strip().rstrip(".,;:!?\"'")
        norm_key = (entity_type, val.lower())
        if not val or len(val) < 2 or norm_key in seen:
            return

        # Filter out generic words
        if val.lower() in ["unknown", "none", "null", "system", "user", "author"]:
            return

        # Negative checks for PHONE
        if entity_type == "PHONE" and not is_valid_phone_number(val):
            return

        seen.add(norm_key)
        entities.append({
            "id": str(uuid4()),
            "case_id": case_id or artifact.get("case_id"),
            "artifact_id": artifact_id,
            "entity_type": entity_type,
            "value": val,
        })

    # 1. Extract from structured fields
    for field_name in ["caller", "receiver", "sender", "recipient"]:
        if field_name in content and content[field_name]:
            classified = classify_structured_party(content[field_name])
            if classified:
                add_entity(classified[0], classified[1])

    # 2. Extract from unstructured text contents
    full_text = " ".join([
        str(v) for k, v in content.items() if isinstance(v, (str, int, float))
    ])
    if artifact.get("raw_data"):
        full_text += " " + str(artifact["raw_data"])

    # Phone Numbers (International, Formatted Regional, 10-digit)
    phone_spans: list[tuple[int, int]] = []
    for pattern in [PHONE_INTL_PATTERN, PHONE_REGIONAL_PATTERN, PHONE_10DIGIT_PATTERN]:
        for match in pattern.finditer(full_text):
            start, end = match.span()
            # Prevent sub-matching within already matched spans (e.g. regional matching within international +...)
            if any(not (end <= s or start >= e) for s, e in phone_spans):
                continue
            candidate = match.group(0).strip()
            if is_valid_phone_number(candidate):
                phone_spans.append((start, end))
                add_entity("PHONE", candidate)

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
    Extracts all forensic entities across a collection of artifacts.
    Strictly deduplicates across the entire collection by (entity_type, normalized_value)
    while recording observation frequencies and artifact provenance references.
    """
    dedup_map: dict[tuple[str, str], dict[str, Any]] = {}

    for artifact in artifacts:
        art_entities = extract_entities_from_artifact(artifact, case_id)
        for ent in art_entities:
            norm_val = ent["value"].strip()
            if ent["entity_type"] == "PHONE":
                norm_key = re.sub(r"[^\d+]", "", norm_val)
            else:
                norm_key = norm_val.lower()
            key = (ent["entity_type"], norm_key)

            if key not in dedup_map:
                dedup_map[key] = {
                    "id": ent["id"],
                    "case_id": ent["case_id"],
                    "artifact_id": ent["artifact_id"],
                    "entity_type": ent["entity_type"],
                    "value": norm_val,
                    "mentions_count": 1,
                    "artifact_ids": [ent["artifact_id"]] if ent.get("artifact_id") else [],
                }
            else:
                existing = dedup_map[key]
                existing["mentions_count"] += 1
                if ent.get("artifact_id") and ent["artifact_id"] not in existing["artifact_ids"]:
                    existing["artifact_ids"].append(ent["artifact_id"])

    return list(dedup_map.values())