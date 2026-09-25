import argparse

import chromadb
from sentence_transformers import SentenceTransformer


RELATIONSHIPS = [
    "family",
    "friend",
    "professional",
    "unknown",
]


client = chromadb.HttpClient(host="localhost", port=8000)

print("Loading multilingual embedding model...")
embedder = SentenceTransformer(
    "paraphrase-multilingual-mpnet-base-v2"
)


def retrieve(relationship, incoming_message, k=3):
    collection_name = f"history_{relationship}"

    collection = client.get_collection(name=collection_name)

    if collection.count() == 0:
        print(f"\n⚠️ {collection_name} is empty. Skipping.")
        return

    query_embedding = embedder.encode(incoming_message).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
    )

    print("\n" + "=" * 70)
    print(f"Relationship: {relationship}")
    print(f"Query: {incoming_message}")
    print("=" * 70)

    distances = results["distances"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for i, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        print(f"\nResult {i}")
        print(f"Distance: {distance:.3f}")
        print(f"Their message: {document}")
        print(f"My reply: {metadata['my_reply']}")
        print(f"Timestamp: {metadata['timestamp']}")

    if all(
        distances[i] <= distances[i + 1]
        for i in range(len(distances) - 1)
    ):
        print("\n✅ Distance sanity check: results are ordered correctly.")
    else:
        print("\n⚠️ Distance sanity check failed.")


def main():
    parser = argparse.ArgumentParser(
        description="Test retrieval from relationship-specific ChromaDB collections."
    )

    parser.add_argument(
        "--relationship",
        choices=RELATIONSHIPS,
        default=None,
        help="Relationship collection to search.",
    )

    parser.add_argument(
        "--query",
        default=None,
        help="Message to search for.",
    )

    args = parser.parse_args()

    if args.relationship and args.query:
        retrieve(args.relationship, args.query)
        return

    sample_queries = {
        "family": [
            "Babu khana kha liya?",
            "Sunday ko ghar aaogi?",
        ],
        "friend": [
            "Movie ka plan hai kya?",
            "Yaar ye photo dekh 😂",
        ],
        "professional": [
            "Can we connect tomorrow?",
        ],
        "unknown": [
            "Hello, how are you?",
        ],
    }

    for relationship in RELATIONSHIPS:
        for query in sample_queries[relationship]:
            retrieve(relationship, query)


if __name__ == "__main__":
    main()