from agent.pipeline import process_message


tests = [
    (
        "Unknown sender",
        {
            "jid": "5555555555@s.whatsapp.net",
            "from_me": False,
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
        "One-word ack",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "Okay",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
    (
        "Money message",
        {
            "jid": "1112223334@s.whatsapp.net",
            "from_me": False,
            "text": "Can you send me money?",
            "message_type": "text",
            "is_forwarded": False,
        },
    ),
]


for name, message in tests:
    print()
    print("=" * 60)
    print(name)

    result = process_message(message)

    print(f"Result: {result}")