import hashlib
import json
from collections import Counter
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


PAIRS_FILE = Path("data/processed_pairs.jsonl")
MAP_FILE = Path("config/contact_relationship_map.json")

RELATIONSHIPS = ["family", "friend", "professional", "unknown"]


print("Loading multilingual embedding model...")
print("First run may download the model. Please wait.")

embedder = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
client = chromadb.HttpClient(host="localhost", port=8000)


def stable_id(conversation_id, timestamp, index):
    raw = f"{conversation_id}|{timestamp}|{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def main():
    with open(MAP_FILE, encoding="utf-8") as f:
        relationship_map = json.load(f)

    collections = {
        relationship: client.get_or_create_collection(
            name=f"history_{relationship}"
        )
        for relationship in RELATIONSHIPS
    }

    with open(PAIRS_FILE, encoding="utf-8") as f:
        pairs = [json.loads(line) for line in f if line.strip()]

    counts = Counter()

    for index, pair in enumerate(pairs):
        conversation_id = pair["conversation_id"]

        relationship = relationship_map.get(
            conversation_id,
            relationship_map.get("_default", "unknown"),
        )

        if relationship not in RELATIONSHIPS:
            relationship = "unknown"

        pair_id = stable_id(
            conversation_id,
            pair["timestamp"],
            index,
        )

        their_message = pair["their_message"]
        my_reply = pair["my_reply"]
        timestamp = pair["timestamp"]

        embedding = embedder.encode(their_message).tolist()

        collections[relationship].upsert(
            ids=[pair_id],
            embeddings=[embedding],
            documents=[their_message],
            metadatas=[
                {
                    "my_reply": my_reply,
                    "timestamp": timestamp,
                    "conversation_id": conversation_id,
                }
            ],
        )

        counts[relationship] += 1

        if (index + 1) % 50 == 0:
            print(f"Processed {index + 1} pairs...")

    print("\nEmbedding complete.")
    print("\nPairs processed by relationship:")

    for relationship in RELATIONSHIPS:
        count = collections[relationship].count()
        print(f"  history_{relationship}: {count}")

        if count == 0:
            print(f"  ⚠️ No data in history_{relationship}")

    print(f"\nTotal input pairs: {len(pairs)}")
    print(f"Total processed: {sum(counts.values())}")


if __name__ == "__main__":
    main()