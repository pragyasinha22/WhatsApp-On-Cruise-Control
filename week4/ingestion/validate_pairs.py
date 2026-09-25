import json
import random
from collections import Counter


INPUT_FILE = "data/processed_pairs.jsonl"


def load_pairs():
    pairs = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                pairs.append(json.loads(line))

    return pairs


def word_count(text):
    return len(text.split())


def main():
    pairs = load_pairs()

    print(f"Total pairs: {len(pairs)}")
    print()

    # 1. Per-conversation counts
    counts = Counter(pair["conversation_id"] for pair in pairs)

    print("Pairs per conversation:")
    for conversation_id, count in sorted(counts.items()):
        print(f"  {conversation_id}: {count}")

    print()

    # 2. Show conversations that produced zero pairs
    expected_conversations = {"family", "friend"}

    for conversation_id in sorted(expected_conversations):
        if counts.get(conversation_id, 0) == 0:
            print(f"WARNING: {conversation_id} has 0 pairs")

    print()

    # 3. Print 5 random pairs
    print("Sample pairs:")

    sample_size = min(5, len(pairs))

    for i, pair in enumerate(random.sample(pairs, sample_size), start=1):
        print(f"\n--- Pair {i} ---")
        print(f"Conversation: {pair['conversation_id']}")
        print(f"Their message: {pair['their_message']}")
        print(f"My reply: {pair['my_reply']}")
        print(f"Timestamp: {pair['timestamp']}")

    print()

    # 4. Scan for problems
    issues = []

    for index, pair in enumerate(pairs, start=1):
        their_message = pair.get("their_message", "")
        my_reply = pair.get("my_reply", "")

        # Noise leakage
        combined = f"{their_message}\n{my_reply}".lower()

        noise_markers = [
            "omitted",
            "<media",
            "deleted",
        ]

        for marker in noise_markers:
            if marker in combined:
                issues.append(
                    f"Pair {index}: possible noise leakage -> {marker}"
                )

        # Empty messages
        if not their_message.strip():
            issues.append(f"Pair {index}: empty their_message")

        if not my_reply.strip():
            issues.append(f"Pair {index}: empty my_reply")

        # Very long reply
        if word_count(my_reply) > 100:
            issues.append(
                f"Pair {index}: my_reply is over 100 words"
            )

        # Identical messages
        if their_message.strip().lower() == my_reply.strip().lower():
            issues.append(
                f"Pair {index}: their_message and my_reply are identical"
            )

    print("Validation:")

    if issues:
        for issue in issues:
            print(f"⚠️ {issue}")

        print()
        print(f"⚠️ {len(issues)} issues found — review above")

    else:
        print("✅ Looks good")


if __name__ == "__main__":
    main()