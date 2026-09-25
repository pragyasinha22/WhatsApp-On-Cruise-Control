from agent.decision_engine import should_reply
from agent.generator import generate_reply
from agent.router import resolve_relationship


def process_message(message: dict) -> str | None:
    """
    Run one incoming WhatsApp message through the full Week 3 pipeline.

    Returns:
        Generated reply string if the agent should reply.
        None if the agent should ignore the message.
    """

    jid = message.get("jid", "")

    relationship, collection_name = resolve_relationship(jid)

    print(f"Relationship: {relationship}")
    print(f"History collection: {collection_name}")

    should_send, reason = should_reply(message, relationship)

    print(f"Decision: {'reply' if should_send else 'ignore'}")
    print(f"Reason: {reason}")

    if not should_send:
        return None

    reply = generate_reply(
        incoming_text=message.get("text", ""),
        relationship=relationship,
    )

    return reply


if __name__ == "__main__":
    test_message = {
        # "jid": "919876543210@s.whatsapp.net",
        "jid": "1112223334@s.whatsapp.net",
        "from_me": False,
        "text": "Movie ka plan hai kya?",
        "message_type": "text",
        "is_forwarded": False,
    }

    print("=" * 70)
    print("WEEK 3 END-TO-END PIPELINE")
    print("=" * 70)

    reply = process_message(test_message)

    if reply:
        print(f"\nFinal reply: {reply}")
    else:
        print("\nNo reply sent.")