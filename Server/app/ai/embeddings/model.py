from sentence_transformers import (
    SentenceTransformer,
)

from app.core.config import settings


embedding_model = SentenceTransformer(
    settings.EMBEDDING_MODEL
)