import json
from pathlib import Path

PAIRS_FILE = Path("data/processed_pairs.jsonl")
MAP_FILE = Path("config/contact_relationship_map.json")

VALID_RELATIONSHIPS = {"family", "friend", "professional", "unknown"}


def main():
    with open(MAP_FILE, encoding="utf-8") as f:
        relationship_map = json.load(f)

    conversation_ids = set()

    with open(PAIRS_FILE, encoding="utf-8") as f:
        for line in f:
            pair = json.loads(line)
            conversation_ids.add(pair["conversation_id"])

    missing = []
    invalid = []

    for conversation_id in sorted(conversation_ids):
        if conversation_id not in relationship_map:
            missing.append(conversation_id)
        elif relationship_map[conversation_id] == "REPLACE_ME":
            missing.append(conversation_id)
        elif relationship_map[conversation_id] not in VALID_RELATIONSHIPS:
            invalid.append(
                f"{conversation_id}: {relationship_map[conversation_id]}"
            )

    print(f"Conversation IDs found: {len(conversation_ids)}")
    print(f"Mapped IDs: {len(conversation_ids) - len(missing)}")

    if missing:
        print("\nMissing/unclassified IDs:")
        for conversation_id in missing:
            print(f"  - {conversation_id}")

    if invalid:
        print("\nInvalid relationship values:")
        for item in invalid:
            print(f"  - {item}")

    if not missing and not invalid:
        print("\n✅ Relationship map looks good")
    else:
        print("\n⚠️ Relationship map needs fixing")
        raise SystemExit(1)


if __name__ == "__main__":
    main()