
import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

# Load once when this module is imported.
print("Loading multilingual embedding model...")
_embedding_model = SentenceTransformer(MODEL_NAME)
_chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
)


def retrieve_similar(
    relationship: str,
    incoming_message: str,
    k: int = 3,
) -> list[dict]:
    """Retrieve similar message-reply pairs for one relationship."""

    if not incoming_message or not incoming_message.strip():
        return []

    collection_name = f"history_{relationship}"

    try:
        collection = _chroma_client.get_collection(name=collection_name)
    except Exception as exc:
        # A missing collection should behave like empty history.
        # Re-raise genuine Chroma connection failures.
        error_text = str(exc).lower()
        connection_errors = (
            "connection",
            "connect",
            "localhost",
            "max retries",
            "refused",
            "timeout",
        )

        if any(term in error_text for term in connection_errors):
            raise

        return []

    if collection.count() == 0:
        return []

    query_embedding = _embedding_model.encode(
        [incoming_message],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=max(1, k),
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    distances = results.get("distances") or [[]]

    if not documents[0]:
        return []

    retrieved = []

    for document, metadata, distance in zip(
        documents[0],
        metadatas[0],
        distances[0],
    ):
        metadata = metadata or {}

        retrieved.append(
            {
                "their_message": document,
                "my_reply": metadata.get("my_reply", ""),
                "distance": float(distance),
            }
        )

    return retrieved
