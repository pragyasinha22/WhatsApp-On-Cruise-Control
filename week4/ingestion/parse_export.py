
import re
import json
import argparse
from pathlib import Path

from config.constants import ONE_WORD_ACKS

LINE_PATTERN = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s"
    r"(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s"
    r"([^:]+):\s(.*)$"
)

# Extend this list if your WhatsApp export contains other system messages.
NOISE_MARKERS = [
    "messages and calls are end-to-end encrypted",
    "<media omitted>",
    "image omitted",
    "video omitted",
    "audio omitted",
    "sticker omitted",
    "gif omitted",
    "document omitted",
    "this message was deleted",
    "you deleted this message",
    "missed voice call",
    "missed video call",
    "created group",
    "changed the subject",
    "added you",
    "changed this group's icon",
    "contact card omitted",
]




def is_noise(text):
    lower = text.lower().strip()

    if any(marker in lower for marker in NOISE_MARKERS):
        return True

    cleaned = lower.rstrip(".!,?")

    if cleaned in ONE_WORD_ACKS:
        return True

    return False


def slugify(filename):
    name = Path(filename).stem

    if name.lower().startswith("whatsapp chat with "):
        name = name[len("whatsapp chat with "):]

    name = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    return name.strip("-").lower()


def parse_file(path):
    """
    Read one WhatsApp export and merge continuation lines
    into the previous message.
    """
    entries = []

    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n\r")

            match = LINE_PATTERN.match(line)

            if match:
                date, time, sender, message = match.groups()

                entries.append(
                    {
                        "sender": sender.strip(),
                        "message": message.strip(),
                        "timestamp": f"{date} {time}",
                    }
                )

            elif entries:
                # Continuation line.
                entries[-1]["message"] += "\n" + line

    return entries


def group_into_turns(entries):
    """
    Remove noise and combine consecutive messages
    from the same sender into one turn.
    """
    turns = []

    for entry in entries:
        if is_noise(entry["message"]):
            continue

        if not entry["message"].strip():
            continue

        if turns and turns[-1]["sender"] == entry["sender"]:
            turns[-1]["message"] += "\n" + entry["message"]
        else:
            turns.append(dict(entry))

    return turns


def build_pairs(turns, my_name, conversation_id, cap=500):
    """
    Whenever an other-person turn is immediately followed
    by one of my turns, create a pair.
    """
    pairs = []

    for i in range(1, len(turns)):
        previous_turn = turns[i - 1]
        current_turn = turns[i]

        if (
            current_turn["sender"] == my_name
            and previous_turn["sender"] != my_name
        ):
            pairs.append(
                {
                    "conversation_id": conversation_id,
                    "their_message": previous_turn["message"],
                    "my_reply": current_turn["message"],
                    "timestamp": current_turn["timestamp"],
                }
            )

    return pairs[-cap:]


def main():
    parser = argparse.ArgumentParser(
        description="Parse WhatsApp exports into clean message-reply pairs."
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Your exact sender name as it appears in the export.",
    )

    args = parser.parse_args()

    raw_dir = Path("data/raw_export")
    output_file = Path("data/processed_pairs.jsonl")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    all_pairs = []

    txt_files = sorted(raw_dir.glob("*.txt"))

    if not txt_files:
        print("No .txt files found in data/raw_export/")
        return

    for path in txt_files:
        # Your working_group.txt is a group chat,
        # while this parser is intended for 1:1 conversations.
        if path.name.lower() == "working_group.txt":
            print(f"SKIPPED group chat: {path.name}")
            continue

        conversation_id = slugify(path.name)

        entries = parse_file(path)
        turns = group_into_turns(entries)

        pairs = build_pairs(
            turns,
            args.name,
            conversation_id,
            cap=500,
        )

        all_pairs.extend(pairs)

        print(
            f"{path.name}: {len(pairs)} pairs kept"
        )

        if len(pairs) == 0:
            print(
                f"WARNING: {conversation_id} produced zero pairs. "
                f"Check --name."
            )

    with open(output_file, "w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print()
    print(f"Total pairs written: {len(all_pairs)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

