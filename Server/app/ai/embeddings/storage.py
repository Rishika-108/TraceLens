from pgvector.sqlalchemy import Vector

from app.core.config import (
    settings,
)


embedding_column = Vector(
    settings.VECTOR_DIMENSION
)