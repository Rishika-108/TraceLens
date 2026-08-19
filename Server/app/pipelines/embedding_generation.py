from sentence_transformers import (
    SentenceTransformer,
)


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings(
    artifacts: list[dict],
):

    embeddings = []

    for artifact in artifacts:

        vector = model.encode(
            str(
                artifact["content"]
            )
        )

        embeddings.append(
            {
                "artifact":
                    artifact,
                "embedding":
                    vector.tolist(),
            }
        )

    return embeddings