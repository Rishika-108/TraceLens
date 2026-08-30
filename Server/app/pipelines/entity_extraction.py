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

# Person Name Stopwords (prevent non-persons from becoming PERSON entities)
NAME_STOPWORDS = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
    "whatsapp", "google", "chrome", "firefox", "safari", "android", "iphone", "apple", "microsoft", "windows",
    "tracelens", "system", "event", "user", "unknown", "author", "sender", "recipient", "subject", "message",
    "phone", "call", "sms", "email", "document", "record", "case", "file", "evidence", "artifact", "report",
    "united states", "new york", "new delhi", "san francisco", "great britain", "swiss bank", "coffee day", "cafe coffee",
    "meeting notes", "status update", "cash transfer", "wire transfer", "bank account",
}

TITLE_NAME_PATTERN = re.compile(
    r"\b(?:Mr\.|Mrs\.|Ms\.|Miss|Dr\.|Prof\.|Agent|Officer|Inspector|Detective|Capt\.|Captain|Advocate)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
)
CONTEXT_NAME_PATTERN = re.compile(
    r"\b(?:meet|with|contact|ask|speak with|talk to|paid|transfer to|saw|seen with|informed by|received from|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
)
FULL_NAME_PATTERN = re.compile(
    r"\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20})?)\b"
)


def is_valid_phone_number(candidate: str) -> bool:
    """
    Validates that a candidate string is genuinely a phone number and not a false positive
    such as an ISO date (2023-08-15), timestamp (14:30:00), IPv4 address, currency, or ID.
    """
    s = candidate.strip().rstrip(".,;:!?\"'")
    if not s:
        return False

    if re.search(r"[a-zA-Z]", s):
        return False

    if ":" in s or "/" in s:
        return False

    if re.search(r"[$€£¥₹%]", s):
        return False

    if re.match(r"^\d{4}[-.]\d{1,2}[-.]\d{1,2}$", s) or re.match(r"^\d{1,2}[-.]\d{1,2}[-.]\d{4}$", s):
        return False

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", s):
        return False

    digits = re.sub(r"\D", "", s)
    num_digits = len(digits)

    if not (7 <= num_digits <= 15):
        return False

    if len(set(digits)) <= 2:
        return False

    if s.isdigit():
        if num_digits not in (10, 11):
            return False
        return True

    if s.startswith("+"):
        return True

    if re.match(r"^\(?\d{2,4}\)?[-.\s]\d{3,4}[-.\s]\d{3,4}$", s):
        return True

    return False


def is_valid_person_name(name: str) -> bool:
    """
    Validates that a proper noun phrase is plausibly a human name and not a stopword,
    location, date, or technology title.
    """
    clean = name.strip()
    if not clean or len(clean) < 3 or len(clean) > 40:
        return False

    lower = clean.lower()
    if lower in NAME_STOPWORDS:
        return False

    words = lower.split()
    if len(words) < 2 or len(words) > 3:
        return False

    # Each word must look like a capitalized name word
    if any(w in NAME_STOPWORDS for w in words):
        return False

    # Check for common tech, file, or domain extensions
    if any(lower.endswith(ext) for ext in [".com", ".org", ".pdf", ".txt", ".csv", ".jpg", ".png"]):
        return False

    # Must be pure alphabetic letters with spaces
    if not re.match(r"^[A-Za-z\s.'-]+$", clean):
        return False

    return True


def classify_structured_party(value: str) -> tuple[str, str] | None:
    """
    Classifies a structured party field (caller, receiver, sender, recipient)
    as PERSON, EMAIL, or PHONE with strict validation.
    """
    clean_val = str(value).strip().rstrip(".,;:")
    if not clean_val or len(clean_val) < 2:
        return None

    if clean_val.lower() in ["unknown", "none", "null", "system", "user", "author", "whatsapp", "chrome"]:
        return None

    if "@" in clean_val and EMAIL_PATTERN.search(clean_val):
        return ("EMAIL", clean_val)

    if is_valid_phone_number(clean_val):
        return ("PHONE", clean_val)

    if re.search(r"[a-zA-Z]", clean_val):
        # Strip trailing parenthesized numbers e.g. "Rahul Sharma (+1...)"
        name_candidate = re.sub(r"\(.*?\)", "", clean_val).strip()
        if is_valid_person_name(name_candidate):
            return ("PERSON", name_candidate)
        return ("PERSON", clean_val)

    return None


def extract_entities_from_artifact(artifact: dict[str, Any], case_id: str | None = None) -> list[dict[str, Any]]:
    """
    Extracts multi-type forensic entities from a single artifact (people, phones, emails, orgs, crypto, IPs, locations).
    Filters false positives, captures named identities, and deduplicates within the artifact.
    """
    metadata = artifact.get("metadata") or {}
    # Exclude system documentation from contaminating case entity directory
    if metadata.get("is_system_doc") or metadata.get("exclude_from_primary_evidence"):
        return []

    entities: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    artifact_id = artifact.get("id")
    content = artifact.get("content", {})

    def add_entity(entity_type: str, value: str):
        val = value.strip().rstrip(".,;:!?\"'")
        norm_key = (entity_type, val.lower())
        if not val or len(val) < 2 or norm_key in seen:
            return

        if val.lower() in ["unknown", "none", "null", "system", "user", "author"]:
            return

        if entity_type == "PHONE" and not is_valid_phone_number(val):
            return

        if entity_type == "PERSON" and not is_valid_person_name(val):
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
    for field_name in ["caller", "receiver", "sender", "recipient", "author", "name", "contact", "agent", "user", "participant"]:
        if field_name in content and content[field_name]:
            classified = classify_structured_party(content[field_name])
            if classified:
                add_entity(classified[0], classified[1])

    # 2. Extract from unstructured text contents (including nested structures)
    def _extract_text_fragments(val: Any) -> list[str]:
        fragments = []
        if isinstance(val, (str, int, float)):
            fragments.append(str(val))
        elif isinstance(val, dict):
            for v in val.values():
                fragments.extend(_extract_text_fragments(v))
        elif isinstance(val, (list, tuple, set)):
            for v in val:
                fragments.extend(_extract_text_fragments(v))
        return fragments

    text_parts = _extract_text_fragments(content)
    full_text = " ".join(text_parts)
    if artifact.get("raw_data"):
        full_text += " " + str(artifact["raw_data"])

    # Phone Numbers (International, Formatted Regional, 10-digit)
    phone_spans: list[tuple[int, int]] = []
    for pattern in [PHONE_INTL_PATTERN, PHONE_REGIONAL_PATTERN, PHONE_10DIGIT_PATTERN]:
        for match in pattern.finditer(full_text):
            start, end = match.span()
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

    # Person Names (Titles + Names, Contextual Mentions, Proper Nouns)
    for match in TITLE_NAME_PATTERN.finditer(full_text):
        name_cand = match.group(1).strip()
        if is_valid_person_name(name_cand):
            add_entity("PERSON", name_cand)

    for match in CONTEXT_NAME_PATTERN.finditer(full_text):
        name_cand = match.group(1).strip()
        if is_valid_person_name(name_cand):
            add_entity("PERSON", name_cand)

    for match in FULL_NAME_PATTERN.finditer(full_text):
        name_cand = match.group(1).strip()
        if is_valid_person_name(name_cand):
            add_entity("PERSON", name_cand)

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
    Extracts, deduplicates, and normalizes entities across all artifacts in a case.
    Preserves mention counts and source provenance.
    """
    all_extracted: list[dict[str, Any]] = []
    for art in artifacts:
        all_extracted.extend(extract_entities_from_artifact(art, case_id))

    grouped: dict[tuple[str, str], dict[str, Any]] = {}

    for ent in all_extracted:
        raw_val = ent["value"].strip()
        ent_type = ent["entity_type"]

        if ent_type == "PHONE":
            norm_val = re.sub(r"[\s\-\(\)\.]", "", raw_val)
        else:
            norm_val = raw_val.lower()

        group_key = (ent_type, norm_val)

        if group_key not in grouped:
            grouped[group_key] = {
                "id": ent["id"],
                "case_id": ent["case_id"],
                "artifact_id": ent["artifact_id"],
                "entity_type": ent_type,
                "value": raw_val,
                "mentions_count": 1,
                "artifact_ids": [ent["artifact_id"]] if ent.get("artifact_id") else [],
            }
        else:
            grouped[group_key]["mentions_count"] += 1
            if ent.get("artifact_id") and ent["artifact_id"] not in grouped[group_key]["artifact_ids"]:
                grouped[group_key]["artifact_ids"].append(ent["artifact_id"])
            if len(raw_val) > len(grouped[group_key]["value"]):
                grouped[group_key]["value"] = raw_val

    return list(grouped.values())