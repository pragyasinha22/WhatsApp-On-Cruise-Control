from agent.pipeline import process_message


def test_unknown_sender():
    message = {
        "jid": "5555555555@s.whatsapp.net",
        "from_me": False,
        "text": "Hello",
        "message_type": "text",
        "is_forwarded": False,
    }

    result = process_message(message)

    assert result is None


def test_group_chat():
    message = {
        "jid": "1234567890@g.us",
        "from_me": False,
        "text": "Hello everyone",
        "message_type": "text",
        "is_forwarded": False,
    }

    result = process_message(message)

    assert result is None


def test_one_word_ack():
    message = {
        "jid": "1112223334@s.whatsapp.net",
        "from_me": False,
        "text": "Okay",
        "message_type": "text",
        "is_forwarded": False,
    }

    result = process_message(message)

    assert result is None


def test_money_message():
    message = {
        "jid": "1112223334@s.whatsapp.net",
        "from_me": False,
        "text": "Can you send me money?",
        "message_type": "text",
        "is_forwarded": False,
    }

    result = process_message(message)

    assert result is None