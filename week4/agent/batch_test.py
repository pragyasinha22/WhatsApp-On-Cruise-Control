from agent.router import resolve_relationship
from agent.decision_engine import should_reply
from agent.generator import generate_reply


TEST_MESSAGES = [
    (
        "Own message",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": True,
            "text": "Hello",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Group chat",
        {
            "jid": "1234567890@g.us",
            "from_me": False,
            "text": "Hello everyone",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Unknown number",
        {
            "jid": "5555555555@s.whatsapp.net",
            "from_me": False,
            "text": "Hello",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Media only",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "",
            "message_type": "image",
            "is_forwarded": False,
        },
    ),
    (
        "Forwarded message",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "Check this out",
            "message_type": "text",
            "is_forwarded": True,
        },
    ),
    (
        "One-word ack",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "thanks",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Money message",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "Can you send me 5000 rupees?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Casual friend",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "Movie ka plan hai kya?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Casual family",
        {
            "jid": "2233445566@s.whatsapp.net",
            "from_me": False,
            "text": "Sunday ko ghar aaogi?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Casual professional",
        {
            "jid": "9999988888@s.whatsapp.net",
            "from_me": False,
            "text": "Can we connect tomorrow at 10 AM?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
]


def main():
    results = []

    print("=" * 100)
    print("WEEK 3 BATCH TEST — ROUTER → DECISION ENGINE → GENERATOR")
    print("=" * 100)

    for name, message in TEST_MESSAGES:
        relationship, collection_name = resolve_relationship(
            message["jid"]
        )

        should_send, reason = should_reply(
            message,
            relationship,
        )

        reply = None

        if should_send:
            reply = generate_reply(
                incoming_text=message["text"],
                relationship=relationship,
            )

        results.append(
            {
                "name": name,
                "message": message["text"],
                "relationship": relationship,
                "decision": "reply" if should_send else "ignore",
                "reason": reason,
                "reply": reply or "",
            }
        )

    print("\n")
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)

    print(
        f"{'Message':<20} "
        f"{'Relationship':<14} "
        f"{'Decision':<10} "
        f"{'Reason':<38} "
        f"Reply"
    )

    print("-" * 100)

    for result in results:
        message = result["message"][:18]
        relationship = result["relationship"][:12]
        decision = result["decision"]
        reason = result["reason"][:36]
        reply = result["reply"][:35]

        print(
            f"{message:<20} "
            f"{relationship:<14} "
            f"{decision:<10} "
            f"{reason:<38} "
            f"{reply}"
        )

    print("\n")
    print("=" * 100)
    print("BATCH TEST COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()