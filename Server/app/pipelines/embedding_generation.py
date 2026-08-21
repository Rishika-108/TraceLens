from typing import Any
from app.ai.embeddings.generator import create_embedding


def prepare_artifact_text(artifact: dict[str, Any]) -> str:
    """
    Assembles a rich semantic text representation of an artifact for embedding generation.
    """
    art_type = artifact.get("artifact_type", "ARTIFACT")
    content = artifact.get("content", {})
    ts = artifact.get("timestamp", "")

    parts = [f"Type: {art_type}"]
    if ts:
        parts.append(f"Timestamp: {ts}")

    for k, v in content.items():
        if v and isinstance(v, (str, int, float, list)):
            parts.append(f"{k}: {v}")

    if artifact.get("raw_data"):
        raw_snippet = str(artifact["raw_data"])[:300]
        parts.append(f"Raw: {raw_snippet}")

    return "\n".join(parts)


def generate_embeddings(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Generates semantic vector embeddings for a list of artifact dictionaries.
    """
    for artifact in artifacts:
        text = prepare_artifact_text(artifact)
        artifact["embedding"] = create_embedding(text)
    return artifacts