
import datetime
import json
import os
import re

from dotenv import load_dotenv
from google import genai

from config.constants import ONE_WORD_ACKS


load_dotenv()

VALID_INTENT_LABELS = {
    "safe_to_auto_reply",
    "needs_human_money_or_serious",
}

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def intent_check(text: str) -> str:
    prompt = f"""Classify this incoming WhatsApp message into exactly one label:
"safe_to_auto_reply" or "needs_human_money_or_serious".

Use "needs_human_money_or_serious" for anything involving money, payments,
loans, medical/legal/serious personal matters, or genuine ambiguity that a
generic reply could get wrong.

Message: "{text}"

Reply with only the label, nothing else."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        label = (response.text or "").strip()
    except Exception as exc:
        print(f"[intent_check] API error, failing closed: {exc}")
        return "needs_human_money_or_serious"

    if label not in VALID_INTENT_LABELS:
        print(
            f"[intent_check] Unexpected response {label!r}, "
            "failing closed"
        )
        return "needs_human_money_or_serious"

    return label


def log_decision(
    text: str,
    relationship: str,
    decision: bool,
    reason: str,
) -> None:
    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "message": text,
        "relationship": relationship,
        "decision": "reply" if decision else "ignore",
        "reason": reason,
    }

    with open(
        "logs/decision_log.jsonl",
        "a",
        encoding="utf-8",
    ) as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _finish(
    text: str,
    relationship: str,
    decision: bool,
    reason: str,
) -> tuple[bool, str]:
    log_decision(
        text=text,
        relationship=relationship,
        decision=decision,
        reason=reason,
    )
    return decision, reason


def should_reply(
    message: dict,
    relationship: str,
) -> tuple[bool, str]:
    """Decide whether an incoming WhatsApp message should be auto-replied to."""

    # ---------------------------------------------------------
    # Layer 1: Hard safety rules
    # ---------------------------------------------------------

    if not isinstance(message, dict):
        return _finish(
            "",
            relationship,
            False,
            "unexpected message shape",
        )

    text = message.get("text", "")

    if not isinstance(text, str):
        return _finish(
            "",
            relationship,
            False,
            "unexpected message shape",
        )

    if message.get("from_me") is True:
        return _finish(
            text,
            relationship,
            False,
            "own message",
        )

    if relationship == "group":
        return _finish(
            text,
            relationship,
            False,
            "group chat, not allowlisted",
        )

    if relationship == "unknown":
        return _finish(
            text,
            relationship,
            False,
            "sender not in allowlist",
        )

    # ---------------------------------------------------------
    # Layer 2: Signal rules
    # ---------------------------------------------------------

    message_type = message.get("message_type", "text")

    if (
        message_type in {"image", "audio", "video"}
        and not text.strip()
    ):
        return _finish(
            text,
            relationship,
            True,
            "media_ack",
        )

    if message.get("is_forwarded") is True:
        return _finish(
            text,
            relationship,
            False,
            "forwarded content, not a real question",
        )

    cleaned_text = re.sub(
        r"[^\w\s]",
        "",
        text.lower(),
        flags=re.UNICODE,
    ).strip()

    if cleaned_text in ONE_WORD_ACKS:
        return _finish(
            text,
            relationship,
            False,
            "low-signal ack, no reply needed",
        )

    if not text.strip():
        return _finish(
            text,
            relationship,
            False,
            "empty message",
        )

    # ---------------------------------------------------------
    # Layer 3: Intent check
    # ---------------------------------------------------------

    intent = intent_check(text)

    if intent == "needs_human_money_or_serious":
        return _finish(
            text,
            relationship,
            False,
            "intent check requires human",
        )

    # ---------------------------------------------------------
    # Layer 4: Passed all gates
    # ---------------------------------------------------------

    return _finish(
        text,
        relationship,
        True,
        "passed all gates",
    )


if __name__ == "__main__":
    examples = [
        {
            "from_me": True,
            "text": "Hello",
            "message_type": "text",
            "is_forwarded": False,
        },
        {
            "from_me": False,
            "text": "Okay",
            "message_type": "text",
            "is_forwarded": False,
        },
        {
            "from_me": False,
            "text": "Kal coffee pe milte hain?",
            "message_type": "text",
            "is_forwarded": False,
        },
        {
            "from_me": False,
            "text": "Can you send me money?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ]

    for example in examples:
        result = should_reply(example, "friend")
        print(f"\nMessage: {example['text']}")
        print(f"Should reply: {result}")
