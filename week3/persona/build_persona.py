#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HINGLISH_WORDS = {
    "hai",
    "kya",
    "nahi",
    "yaar",
    "matlab",
    "acha",
    "theek",
    "bhai",
    "haan",
    "toh",
}

LINE_RE = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2})\s*-\s*(?P<sender>[^:]+):\s*(?P<message>.*)$"
)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\U0001F1E6-\U0001F1FF]")
OUTPUT_PATH = Path(__file__).resolve().parent / "style_signals.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize a WhatsApp export for a specific sender and save persona style signals."
    )
    parser.add_argument("--file", required=True, help="Path to the WhatsApp text export")
    parser.add_argument("--name", required=True, help="Exact sender name as it appears in the export")
    return parser.parse_args()


def read_export_lines(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read().splitlines()


def extract_sender_messages(lines, target_name: str):
    matches = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        match = LINE_RE.match(line)
        if not match:
            continue

        sender = match.group("sender").strip()
        message = match.group("message").strip()

        if sender == target_name:
            matches.append(message)

    return matches


def message_contains_hinglish(message: str) -> bool:
    normalized = re.sub(r"[^a-zA-Z]", " ", message.lower())
    tokens = set(normalized.split())
    return bool(tokens & HINGLISH_WORDS)


def compute_average_words(messages):
    if not messages:
        return 0.0
    total_words = sum(len(re.findall(r"\S+", message)) for message in messages)
    return total_words / len(messages)


def compute_top_emojis(messages, limit: int = 15):
    emoji_counter = Counter()
    for message in messages:
        emoji_counter.update(EMOJI_RE.findall(message))

    top_items = emoji_counter.most_common(limit)
    return [{"emoji": emoji, "count": count} for emoji, count in top_items]


def build_summary(file_path: str, target_name: str, messages):
    total_messages = len(messages)
    hinglish_messages = sum(1 for message in messages if message_contains_hinglish(message))
    avg_words = compute_average_words(messages)
    top_emojis = compute_top_emojis(messages)

    if total_messages == 0:
        hinglish_ratio = 0.0
    else:
        hinglish_ratio = (hinglish_messages / total_messages) * 100.0

    return {
        "file": file_path,
        "sender_name": target_name,
        "sample_size": total_messages,
        "hinglish_ratio_pct": round(hinglish_ratio, 2),
        "average_message_length_words": round(avg_words, 2),
        "top_emojis": top_emojis,
    }


def print_summary(summary):
    print("\n=== Persona Style Summary ===")
    print(f"File: {summary['file']}")
    print(f"Sender: {summary['sender_name']}")
    print(f"Sample size: {summary['sample_size']}")
    print(f"Hinglish ratio: {summary['hinglish_ratio_pct']:.2f}%")
    print(f"Average message length: {summary['average_message_length_words']:.2f} words")
    print("Top 15 emojis:")

    if not summary["top_emojis"]:
        print("  - No emojis found in the selected messages.")
    else:
        for idx, item in enumerate(summary["top_emojis"], start=1):
            print(f"  {idx}. {item['emoji']} -> {item['count']}")


def write_json(summary, warning=None):
    payload = {
        "file": summary["file"],
        "sender_name": summary["sender_name"],
        "sample_size": summary["sample_size"],
        "hinglish_ratio_pct": summary["hinglish_ratio_pct"],
        "average_message_length_words": summary["average_message_length_words"],
        "top_emojis": summary["top_emojis"],
    }
    if warning:
        payload["warning"] = warning

    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    args = parse_args()
    file_path = os.path.abspath(args.file)
    target_name = args.name

    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    lines = read_export_lines(file_path)
    matching_messages = extract_sender_messages(lines, target_name)
    summary = build_summary(file_path, target_name, matching_messages)

    if not matching_messages:
        warning = (
            f"WARNING: No messages were found for sender '{target_name}' in '{file_path}'. "
            "Double-check the exact sender name in the raw export and try again."
        )
        print(warning, file=sys.stderr)
        summary["top_emojis"] = []
        write_json(summary, warning=warning)
        return

    print_summary(summary)
    write_json(summary)


if __name__ == "__main__":
    main()
