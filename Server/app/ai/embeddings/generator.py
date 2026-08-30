import hashlib
import math
from typing import Any
from app.core.config import settings

_model = None
_model_initialized = False


import os

def get_embedding_model():
    """
    Lazy load SentenceTransformer embedding model from local cache if available.
    In automated tests or when disabled, uses deterministic 384-dim fallback embeddings.
    """
    global _model, _model_initialized
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("DISABLE_TRANSFORMERS") == "1":
        return None

    if not _model_initialized:
        _model_initialized = True
        try:
            from sentence_transformers import SentenceTransformer
            try:
                _model = SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
            except Exception:
                _model = None
        except Exception:
            _model = None
    return _model


def _fallback_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Deterministic pseudo-embedding for testing or fallback when model weights are not local.
    Produces a unit-normalized vector of the specified dimension (384-dim).
    """
    vec = []
    for i in range(dim):
        h = hashlib.sha256(f"{text}_{i}".encode("utf-8")).hexdigest()
        val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
        vec.append(val)

    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def create_embedding(text: str) -> list[float]:
    """
    Generates a 384-dimensional vector embedding for the input text.
    """
    clean_text = str(text).strip()
    if not clean_text:
        return [0.0] * settings.VECTOR_DIMENSION

    model = get_embedding_model()
    if model:
        try:
            vector = model.encode(clean_text)
            return vector.tolist()
        except Exception:
            pass

    return _fallback_embedding(clean_text, settings.VECTOR_DIMENSION)


def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a batch of strings.
    """
    if not texts:
        return []

    model = get_embedding_model()
    if model:
        try:
            vectors = model.encode(texts)
            return [v.tolist() for v in vectors]
        except Exception:
            pass

    return [create_embedding(t) for t in texts]
